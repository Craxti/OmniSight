import { expect, type APIRequestContext } from '@playwright/test'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { paths as V1Paths } from '../src/shared/api/paths'
import { unwrapV1Ci, unwrapV1Items } from '../src/shared/api/v1Envelope'
import { API_BASE, apiLogin, authHeaders, deleteCiByNameApi, deleteTypeByNameApi } from './api-helpers'

const E2E_DIR = path.dirname(fileURLToPath(import.meta.url))
export const REPO_ROOT = path.resolve(E2E_DIR, '../../..')
const FIXTURES_ROOT = path.join(REPO_ROOT, 'fixtures')

export const AUTODISCOVER_HOST_SNAPSHOT_PATH = path.join(FIXTURES_ROOT, 'host_snapshot_pay_srv.json')
export const AUTODISCOVER_INVENTORY_PATH = path.join(FIXTURES_ROOT, 'autodiscover_inventory.json')
export const IMPORT_UNKNOWN_TYPES_SAMPLE_PATH = path.join(FIXTURES_ROOT, 'import_unknown_types_sample.json')
export const E2E_IMPORT_FIXTURE_PATH = IMPORT_UNKNOWN_TYPES_SAMPLE_PATH

export { DEMO_CORRELATION_ALERTS } from '../src/shared/constants'
export type { AlertRow } from '../src/shared/constants'

type CiSummary = { id: number; name: string; external_ids?: Record<string, string> }

export async function ensureAutodiscoverDemoFixture(request: APIRequestContext) {
  if (!fs.existsSync(AUTODISCOVER_HOST_SNAPSHOT_PATH)) {
    throw new Error(`Missing host snapshot file: ${AUTODISCOVER_HOST_SNAPSHOT_PATH}`)
  }

  const token = await apiLogin(request)
  const headers = authHeaders(token)

  const typesRes = await request.get(`${API_BASE}${V1Paths.ci.types}`, { headers })
  expect(typesRes.ok()).toBeTruthy()
  const types = Object.fromEntries(
    unwrapV1Items<{ id: number; name: string }>(await typesRes.json()).map((t) => [t.name, t.id]),
  ) as Record<string, number>

  async function ensureCi(name: string, typeName: string, attrs: Record<string, string>) {
    const list = await request.get(
      `${API_BASE}${V1Paths.ci.list}?name=${encodeURIComponent(name)}`,
      { headers },
    )
    expect(list.ok()).toBeTruthy()
    const found = unwrapV1Items<CiSummary>(await list.json()).find((c) => c.name === name)
    if (found) return found.id

    const ext = Object.fromEntries(
      Object.entries(attrs).filter(([k]) =>
        ['hostname', 'ip', 'externalId', 'serviceCode', 'applicationCode'].includes(k),
      ),
    )
    const create = await request.post(`${API_BASE}${V1Paths.ci.list}`, {
      headers,
      data: {
        name,
        type_id: types[typeName],
        status: 'active',
        criticality: 'high',
        environment: 'production',
        owner: 'ops',
        attributes: attrs,
        external_ids: ext,
      },
    })
    expect(create.ok()).toBeTruthy()
    return unwrapV1Ci<{ id: number }>(await create.json()).id
  }

  const srvId = await ensureCi('demo-pay-srv', 'Server', {
    hostname: 'pay-srv-01',
    ip: '10.0.0.21',
    os: 'Ubuntu 24.04',
  })
  const appId = await ensureCi('demo-app', 'Application', {
    hostname: 'app-01',
    serviceCode: 'PAY',
    applicationCode: 'PAY-APP',
  })
  const dbId = await ensureCi('demo-db', 'Database', {
    hostname: 'demo-db',
    ip: '10.0.0.5',
    externalId: 'ext-db-1',
  })

  async function ensureRelation(sourceId: number, targetId: number, relationType: string) {
    const rels = await request.get(`${API_BASE}${V1Paths.relations.list}`, { headers })
    expect(rels.ok()).toBeTruthy()
    const exists = unwrapV1Items<{
      source_ci_id: number
      target_ci_id: number
      relation_type: string
    }>(await rels.json()).some(
      (r) =>
        r.source_ci_id === sourceId && r.target_ci_id === targetId && r.relation_type === relationType,
    )
    if (exists) return
    const create = await request.post(`${API_BASE}${V1Paths.relations.list}`, {
      headers,
      data: { source_ci_id: sourceId, target_ci_id: targetId, relation_type: relationType, status: 'active' },
    })
    expect(create.ok()).toBeTruthy()
  }

  await ensureRelation(appId, dbId, 'depends_on')
  await ensureRelation(appId, srvId, 'hosted_on')

  const connectorsRes = await request.get(
    `${API_BASE}${V1Paths.autodiscover.connectors}?enabled_only=false`,
    { headers },
  )
  expect(connectorsRes.ok()).toBeTruthy()
  const connectors = unwrapV1Items<{
    id: number
    server_ci_id: number | null
    connector_type: string
  }>(await connectorsRes.json())
  const hostConnector = connectors.find(
    (c) => c.server_ci_id === srvId && c.connector_type === 'host',
  )
  if (hostConnector) {
    const patch = await request.patch(`${API_BASE}${V1Paths.autodiscover.connector(hostConnector.id)}`, {
      headers,
      data: { config: { snapshot_path: AUTODISCOVER_HOST_SNAPSHOT_PATH, mode: 'snapshot' } },
    })
    expect(patch.ok()).toBeTruthy()
  } else {
    const createConn = await request.post(`${API_BASE}${V1Paths.autodiscover.connectors}`, {
      headers,
      data: {
        name: `e2e-host-pay-srv-${srvId}`,
        connector_type: 'host',
        server_ci_id: srvId,
        config: { snapshot_path: AUTODISCOVER_HOST_SNAPSHOT_PATH, mode: 'snapshot' },
      },
    })
    expect(createConn.ok()).toBeTruthy()
  }

  const appRes = await request.get(`${API_BASE}${V1Paths.ci.detail(appId)}`, { headers })
  expect(appRes.ok()).toBeTruthy()
  const app = unwrapV1Ci<{
    external_ids?: Record<string, string>
    attributes?: Record<string, string>
  }>(await appRes.json())
  const ext = { ...(app.external_ids ?? {}) }
  delete ext.ip
  const attrs = { ...(app.attributes ?? {}) }
  delete attrs.ip
  const patch = await request.patch(`${API_BASE}${V1Paths.ci.detail(appId)}`, {
    headers,
    data: { external_ids: ext, attributes: attrs },
  })
  expect(patch.ok()).toBeTruthy()

  return { srvId, appId, expectedIp: '10.0.0.10' }
}

export type RandomImportFixture = {
  ciNames: string[]
  typeNames: string[]
  jsonBuffer: Buffer
}

export function buildRandomImportFixture(suffix: string): RandomImportFixture {
  const typeA = `E2E Edge Node ${suffix}`
  const typeB = `E2E Stream Processor ${suffix}`
  const ciNames = [`e2e-imp-${suffix}-a`, `e2e-imp-${suffix}-b`, `e2e-imp-${suffix}-c`]
  const payload = {
    elements: [
      {
        name: ciNames[0],
        type_name: typeA,
        status: 'active',
        criticality: 'medium',
        environment: 'test',
        owner: 'e2e',
        attributes: { region: 'eu-1', firmware: '1.0' },
      },
      {
        name: ciNames[1],
        type_name: typeA,
        status: 'active',
        criticality: 'low',
        environment: 'test',
        owner: 'e2e',
        attributes: { region: 'eu-2' },
      },
      {
        name: ciNames[2],
        type_name: typeB,
        status: 'active',
        criticality: 'high',
        environment: 'staging',
        owner: 'e2e',
        attributes: { topic: 'orders', partitions: '8' },
      },
    ],
  }
  return {
    ciNames,
    typeNames: [typeA, typeB],
    jsonBuffer: Buffer.from(JSON.stringify(payload), 'utf-8'),
  }
}

export async function cleanupImportFixture(
  request: APIRequestContext,
  token: string,
  fixture: RandomImportFixture,
) {
  for (const name of fixture.ciNames) {
    await deleteCiByNameApi(request, token, name)
  }
  for (const typeName of fixture.typeNames) {
    await deleteTypeByNameApi(request, token, typeName)
  }
}
