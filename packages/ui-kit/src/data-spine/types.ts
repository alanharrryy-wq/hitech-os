export type ProviderId = "mock" | "jsonVault" | "localStorage" | "http" | (string & Record<never, never>);

export type DataSetId = string;

export type KnownDataShapeId = "timeSeries" | "breakdown" | "matrix" | "gauge" | "tableMini";

export type DataShapeId = KnownDataShapeId | (string & Record<never, never>);

export type QueryPrimitive = string | number | boolean | null;

export type QueryValue = QueryPrimitive | readonly QueryPrimitive[];

export type QueryParams = Readonly<Record<string, QueryValue>>;

export type PerfProfile = "default" | "perf";

export interface DeterminismContract {
  readonly deterministic: true;
  readonly seed: string;
  readonly algorithm: "mulberry32";
  readonly version: 1;
}

export interface Query {
  readonly providerId?: ProviderId | undefined;
  readonly datasetId?: DataSetId | undefined;
  readonly dataShapeId?: DataShapeId | undefined;
  readonly params?: QueryParams | undefined;
  readonly seed?: string | undefined;
  readonly timeoutMs?: number | undefined;
  readonly retryCount?: number | undefined;
  readonly cacheTtlMs?: number | undefined;
  readonly forceRefresh?: boolean | undefined;
  readonly perfProfile?: PerfProfile | undefined;
  readonly signal?: AbortSignal | undefined;
}

export interface ProviderResponse {
  readonly providerId?: ProviderId | undefined;
  readonly datasetId?: DataSetId | undefined;
  readonly dataShapeId?: DataShapeId | undefined;
  readonly data: unknown;
  readonly cacheTtlMs?: number | undefined;
  readonly metadata?: Readonly<Record<string, QueryPrimitive>> | undefined;
  readonly determinism?: DeterminismContract | undefined;
}

export interface Result<TData = unknown> {
  readonly providerId: ProviderId;
  readonly datasetId?: DataSetId | undefined;
  readonly dataShapeId: DataShapeId;
  readonly data: TData;
  readonly stableQueryKey: string;
  readonly receivedAt: string;
  readonly cacheTtlMs: number;
  readonly determinism: DeterminismContract | null;
  readonly metadata: Readonly<Record<string, QueryPrimitive>>;
}

export interface DataShapeValidationIssue {
  readonly path: string;
  readonly message: string;
}

export type DataShapeValidationResult<TData> =
  | {
      readonly ok: true;
      readonly value: TData;
      readonly errors: readonly [];
    }
  | {
      readonly ok: false;
      readonly errors: readonly DataShapeValidationIssue[];
    };

export type DataShapeValidator<TData> = (input: unknown) => DataShapeValidationResult<TData>;

export interface DataProviderContext {
  readonly providerId: ProviderId;
  readonly stableQueryKey: string;
  readonly now: () => number;
}

export interface DataProvider {
  readonly id: ProviderId;
  query(input: Query, context: DataProviderContext): ProviderResponse | Promise<ProviderResponse>;
}

export interface DataSpine {
  registerProvider(provider: DataProvider): void;
  unregisterProvider(providerId: ProviderId): void;
  hasProvider(providerId: ProviderId): boolean;
  query<TData = unknown>(input: Query): Promise<Result<TData>>;
}

