import { describe, expect, it } from 'vitest'
import { paths } from '@/shared/api/paths'

describe('paths', () => {
  it('builds CI detail and relations paths', () => {
    expect(paths.ci.detail(42)).toBe('/api/v1/ci/42')
    expect(paths.ci.relations(42)).toBe('/api/v1/ci/42/relations')
    expect(paths.resources.detail(42)).toBe('/api/v1/resources/42')
    expect(paths.resources.relations(42)).toBe('/api/v1/resources/42/relations')
  })

  it('uses v1 for CI list and relations CRUD', () => {
    expect(paths.ci.list).toBe('/api/v1/ci')
    expect(paths.ci.recycleBin).toBe('/api/v1/ci/recycle-bin')
    expect(paths.ci.bulkStatus).toBe('/api/v1/ci/bulk/status')
    expect(paths.ci.restore(1)).toBe('/api/v1/ci/1/restore')
    expect(paths.ci.import).toBe('/api/v1/ci/import')
    expect(paths.ci.exportFull).toBe('/api/v1/ci/export/full')
    expect(paths.ci.types).toBe('/api/v1/ci/types')
    expect(paths.ci.type(5)).toBe('/api/v1/ci/types/5')
    expect(paths.relations.list).toBe('/api/v1/relations')
    expect(paths.relations.validate).toBe('/api/v1/relations/validate')
    expect(paths.relations.importJson).toBe('/api/v1/relations/import/json')
    expect(paths.relations.detail(3)).toBe('/api/v1/relations/3')
  })

  it('exposes correlation ingest on v1', () => {
    expect(paths.correlation.ingest).toBe('/api/v1/correlation/ingest')
  })

  it('exposes export endpoints', () => {
    expect(paths.ci.exportCsv).toBe('/api/v1/ci/export/csv')
    expect(paths.ci.exportXlsx).toBe('/api/v1/ci/export/xlsx')
  })

  it('builds auth user paths by email', () => {
    expect(paths.auth.userEmail('admin@example.com')).toBe('/api/v1/auth/users/admin%40example.com')
    expect(paths.auth.userRole('a@b.c')).toBe('/api/v1/auth/users/a%40b.c/role')
  })

  it('exposes relations and autodiscover paths', () => {
    expect(paths.autodiscover.scan).toBe('/api/v1/autodiscover/scan')
    expect(paths.autodiscover.run(7)).toBe('/api/v1/autodiscover/runs/7')
  })

  it('exposes resources topology paths', () => {
    expect(paths.resources.graph(3)).toBe('/api/v1/resources/3/graph')
    expect(paths.resources.impact(3)).toBe('/api/v1/resources/3/impact')
    expect(paths.resources.graphLayout(3)).toBe('/api/v1/resources/3/graph-layout')
    expect(paths.resources.resolve).toBe('/api/v1/resources/resolve')
    expect(paths.resources.search).toBe('/api/v1/resources/search')
    expect(paths.misc.constants).toBe('/api/v1/meta/constants')
    expect(paths.misc.dashboard).toBe('/api/v1/dashboard/overview')
    expect(paths.misc.audit).toBe('/api/v1/audit')
    expect(paths.misc.entityAudit('ci', 9)).toBe('/api/v1/audit/ci/9')
  })
})
