# schemas

Schema registry workspace for contract validation.

Use:

- Request/response schemas
- Event envelope schemas
- Error model schemas

Current baseline:

- `contract_schema_index.json` with 1:1 mapping for 17 wave-1 contracts.
- `contracts/*.schema.json` per contract ID.
- `envelopes/request_envelope.v1.schema.json`
- `envelopes/response_envelope.v1.schema.json`
- `envelopes/error_envelope.v1.schema.json`
