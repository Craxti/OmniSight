/** E2E helpers barrel — re-exports fixtures, API helpers, and UI flows. */

export {
  API_BASE,
  apiLogin,
  authHeaders,
  deleteCiByNameApi,
  deleteTypeByNameApi,
} from './api-helpers'

export {
  AUTODISCOVER_HOST_SNAPSHOT_PATH,
  AUTODISCOVER_INVENTORY_PATH,
  IMPORT_UNKNOWN_TYPES_SAMPLE_PATH,
  E2E_IMPORT_FIXTURE_PATH,
  REPO_ROOT,
  DEMO_CORRELATION_ALERTS,
  ensureAutodiscoverDemoFixture,
  buildRandomImportFixture,
  cleanupImportFixture,
  type RandomImportFixture,
  type AlertRow,
} from './fixtures'

export {
  login,
  createCi,
  deleteCiByName,
  deleteCiByNameIfExists,
  createRelation,
  deleteRelation,
  deleteRelationIfExists,
  openGraphForCi,
  fillCorrelationAlerts,
  runCorrelationIngest,
  runAutodiscoverInventoryUi,
  runAutodiscoverGraphUi,
  inventoryTable,
  relationsTable,
  auditTable,
} from './ui-helpers'
