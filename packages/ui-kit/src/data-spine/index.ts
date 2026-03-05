export type {
  DataProvider,
  DataProviderContext,
  DataSetId,
  DataShapeId,
  DataShapeValidationIssue,
  DataShapeValidationResult,
  DataShapeValidator,
  DataSpine,
  DeterminismContract,
  KnownDataShapeId,
  PerfProfile,
  ProviderId,
  ProviderResponse,
  Query,
  QueryParams,
  QueryPrimitive,
  QueryValue,
  Result
} from "./types.js";

export { createSpine, createStableQueryKey, DATA_SPINE_DEFAULT_CACHE_TTL_MS } from "./spine.js";

export {
  listRegisteredDataShapes,
  registerDataShape,
  safeValidateDataShape,
  validateDataShape
} from "./schema/registry.js";

export {
  DataShapeGuardError,
  formatGuardErrors,
  isDataShapeGuardError,
  validateBreakdown,
  validateGauge,
  validateMatrix,
  validateTableMini,
  validateTimeSeries
} from "./schema/guards.js";

export { createMockProvider } from "./providers/mock.js";
export type { MockProviderOptions } from "./providers/mock.js";

export { createJsonVaultProvider } from "./providers/jsonVault.js";
export type { JsonVaultProviderOptions } from "./providers/jsonVault.js";

export { createLocalStorageProvider, writeLocalStorageDataset } from "./providers/localStorage.js";
export type { LocalStorageProviderOptions, WriteLocalStorageDatasetInput } from "./providers/localStorage.js";

export { createHttpProvider } from "./providers/http.js";
export type { HttpProviderOptions, HttpRequestDescriptor } from "./providers/http.js";

export { useDataQuery } from "./hooks/useDataQuery.js";
export type { UseDataQueryOptions, UseDataQueryState } from "./hooks/useDataQuery.js";

export { useLiveData } from "./hooks/useLiveData.js";
export type { UseLiveDataOptions, UseLiveDataState } from "./hooks/useLiveData.js";
