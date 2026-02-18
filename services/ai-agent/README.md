# @hitech/ai-agent

Python deterministic service implementing local job handlers for the Node bridge.

## Endpoints

- `GET /health`
- `GET /capabilities`
- `POST /jobs/run`

## Local setup (manual)

1. `python -m app.main --host 127.0.0.1 --port 8001`
2. `python -m unittest discover -s tests -p "test_*.py"`

Notes:

- The service runs with Python stdlib HTTP server and does not require FastAPI/Pydantic at runtime.
- Models mirror `packages/contracts` shapes with deterministic field ordering.
