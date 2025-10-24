# Pointages

Time-logging toolkit combining a FastAPI microservice backed by CSV storage and a Streamlit agent UI powered by Azure AI Agents.

## Overview

- `api-bookings` — FastAPI service exposing time logs from a semicolon CSV file with API key auth and CORS enabled. See `api-bookings/main.py:1`.
- `api-create-py` — Lightweight variant of the API for local/dev without API key middleware. See `api-create-py/main.py:1`.
- `agent` — Streamlit app integrating Azure AI Agents to parse “missions” from chat output and export CSV/XLSX. See `agent/agent.py:1`.
- `Dockerfile` — Container for the Streamlit agent (exposes `8501`). See `Dockerfile:1`.
- Tests — Local API tests and remote smoke tests. See `api-bookings/test_main.py:1`, `api-bookings/test_api.py:1`.

## Key Features

- FastAPI endpoints to list and create time logs (`/pointages`).
- CSV persistence using `pointages-cb.csv` with `;` delimiter.
- Flexible schema with defaults: missing text fields become `"none"`; `start` auto-filled with current timestamp; `confirmed` parsed from truthy strings.
- API key protection via `x-api-key` header in `api-bookings`. Open CORS for easy client use.
- Streamlit “Bookings Agent” UI to converse with an Azure Agent, extract missions with regex, and download as CSV/XLSX.

## Data Model (Pointage)

Columns saved to `pointages-cb.csv` and served by the API:

- `start` (string, auto-filled `MM/DD/YY HH:MM:SS`)
- `name` (string, required)
- `type_sollicitation` (string, required)
- `practice` (string | null)
- `director` (string | null)
- `client` (string | null)
- `department` (string | null)
- `kam` (string | null)
- `business_manager` (string | null)
- `description` (string | null)
- `confirmed` (bool | null)

See validation and defaults in `api-bookings/main.py:33`.

## API Reference (api-bookings)

Base URL (local): `http://localhost:8000`

- GET `/pointages`
  - Returns: `200 OK` with list of `Pointage` objects.
  - Ensures all columns exist; `NaN` → `null` in JSON. See `api-bookings/main.py:64`.

- POST `/pointages`
  - Body: `Pointage` JSON. `start` auto-set when omitted. Missing text fields default to `"none"`; `confirmed` defaults to `false`.
  - Returns: `200 OK` with the created record. See `api-bookings/main.py:73`.

Auth header (required if `API_KEY` is set):

```
x-api-key: <your_api_key>
```

Example:

```
curl -H "x-api-key: $API_KEY" http://localhost:8000/pointages

curl -X POST -H "Content-Type: application/json" \
     -H "x-api-key: $API_KEY" \
     -d '{
           "name": "Jane Doe",
           "type_sollicitation": "EXPERTISE",
           "practice": "Weekly",
           "director": "John Smith",
           "client": "Acme Corp",
           "department": "IT",
           "kam": "Bob Wilson",
           "business_manager": "Alice Johnson",
           "description": "Test entry",
           "confirmed": true
         }' \
     http://localhost:8000/pointages
```

Note: A hosted instance is referenced in tests as `https://pointages.onrender.com`. See `api-bookings/test_api.py:1`.

## Streamlit Agent (agent)

- Chat UI backed by Azure AI Agents; displays assistant responses and parses “missions” using a regex into a table.
- Provides CSV and Excel downloads for parsed missions. See `agent/agent.py:64`.
- Requires Azure credentials (see Environment).

Run locally:

```
streamlit run agent/agent.py --server.port=8501 --server.address=0.0.0.0
```

Docker (for the agent UI):

```
docker build -t pointages-agent .
docker run --rm -p 8501:8501 --env-file .env pointages-agent
```

## Environment

Create a `.env` file at the repo root (example keys referenced by the code):

- For API auth: `API_KEY`
- For Azure agent auth: `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`
- Optional scope metadata: `AZURE_RESOURCE_GROUP`, `AZURE_SUBSCRIPTION_ID`

See loads and usage in `api-bookings/main.py:20` and `agent/agent.py:15`.

## Local Development

Prereqs: Python 3.11+

```
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run the API (bookings):

```
cd api-bookings
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Alternatively, use the helper script: `api-bookings/run.bash:1`.

Run the dev API (no API key):

```
cd api-create-py
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## Tests

- Local app tests via FastAPI `TestClient`: `api-bookings/test_main.py:1`.
- Remote smoke tests against deployed Render app: `api-bookings/test_api.py:1`.

Run pytest from the repo root after installing requirements:

```
pytest -q
```

## Notes and Design Choices

- CORS is open by design for integration simplicity. See `api-bookings/main.py:17`.
- CSV delimiter is `;` to match existing `pointages-cb.csv`. Persist occurs on every POST.
- `confirmed` accepts booleans and truthy strings (e.g., "true", "1", "yes"). See `api-bookings/main.py:54`.

## Deployment

- Streamlit agent can be containerized using the provided `Dockerfile:1`. The `webapp-create.md:1` includes Azure App Service CLI snippets.
- The FastAPI app can be deployed to any ASGI-compatible environment (e.g., Uvicorn + reverse proxy) or PaaS (Render, Azure App Service).

## Troubleshooting

- 401 from API: ensure `x-api-key` matches `API_KEY` in environment.
- CSV not updating: check write permissions and path `api-bookings/pointages-cb.csv` and that the service has working directory set appropriately.
- Streamlit agent auth failures: verify Azure env vars and Entra ID app registration.
