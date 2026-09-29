# posiverse-python-sdk

Python SDK for the [Posiverse](https://www.positioninguniversal.com) OpenAPI (v1.1.1).

Built with **httpx** and **pydantic v2**. Requires Python 3.10 or newer. Covers the OpenAPI tags: Commands, Devices, Firmwares, Groups, Logs, Products, Settings, TagMaps, Tags, Tenants, Users, VirtualConsole, plus `GET /pages/{pageId}` (operation tag Pagination).

The OpenAPI document checked into this repository (`openapi/posiverse.openapi.json`) is the source of truth. The SDK does not invent endpoints beyond that spec.

This package is **not on PyPI yet**. From a checkout of `develop`:

```bash
pip install -e ".[dev]"
```

`requirements.txt` and `requirements-dev.txt` list the same ranges as `pyproject.toml` (the source of truth). `requirements-dev.txt` starts with `-r requirements.txt`, then pytest, respx, ruff, and pip-audit.

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

After the first PyPI release:

```bash
pip install posiverse
```

## Authentication

Posiverse uses an API key in the **`posiverse-auth-key`** header (OpenAPI `bearerAuth` is an `apiKey` scheme, **not** HTTP Bearer).

**Option A — project `.env` (recommended for local work)**

Copy the example file and set `POSIVERSE_API_KEY` in it. `PosiverseClient()` and the live pytest suite load a project-root `.env` (searched from the working directory upward). Values already set in your shell or CI are left unchanged. `.env` is gitignored — never commit it.

Linux / macOS:

```bash
cp .env.example .env
# edit .env and set:
# POSIVERSE_API_KEY=your-api-key
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
# edit .env and set:
# POSIVERSE_API_KEY=your-api-key
```

Windows Command Prompt:

```cmd
copy .env.example .env
REM edit .env and set:
REM POSIVERSE_API_KEY=your-api-key
```

**Option B — shell environment variable**

Linux / macOS (current session):

```bash
export POSIVERSE_API_KEY="your-api-key"
```

Windows PowerShell (current session):

```powershell
$env:POSIVERSE_API_KEY = "your-api-key"
```

Windows Command Prompt (current session):

```cmd
set POSIVERSE_API_KEY=your-api-key
```

Windows PowerShell (persist for your user; new terminals pick it up):

```powershell
[System.Environment]::SetEnvironmentVariable(
    "POSIVERSE_API_KEY",
    "your-api-key",
    "User"
)
```

Use a separate key for test vs production backends. Keys are available in the Posiverse UI under User Profile. Never commit API keys or paste them into logs.

## Servers

The client defaults to **production**: `https://openapi-prod.posiverse.com`.

```python
from posiverse import PosiverseClient

with PosiverseClient() as client:  # production; key from the environment or a project .env
    ...
```

Staff and bots that need a non-production OpenAPI host should set `POSIVERSE_BASE_URL` to their internal test OpenAPI base URL (https only), or pass `base_url=` to the client. The published package does not embed a test hostname. You can set `POSIVERSE_BASE_URL` in the project `.env` from Option A; leave it unset to keep the production default.

Linux / macOS (current session):

```bash
export POSIVERSE_BASE_URL="https://your-internal-test-openapi.example"
```

Windows PowerShell (current session):

```powershell
$env:POSIVERSE_BASE_URL = "https://your-internal-test-openapi.example"
```

Windows Command Prompt (current session):

```cmd
set POSIVERSE_BASE_URL=https://your-internal-test-openapi.example
```

HTTP URLs are rejected. TLS verification and request timeouts are on by default and cannot be turned off through the client constructor.

## Quickstart

```python
from posiverse import PosiverseClient

# Uses POSIVERSE_API_KEY (environment or project .env) and defaults to production
with PosiverseClient() as client:
    page = client.devices.list()
    print(page.total_count, page.page_count, page.page_start, page.next_page_url)
    for device in page.items:
        print(device.id, device.name, device.imei)

    device = client.devices.get(page.items[0].id, full=True)
    print(device.settings)
```

### Pagination

List endpoints return a `PaginatedResponse` with items plus headers:

- `x-total-count` → `total_count`
- `x-page-count` → `page_count`
- `x-page-start` → `page_start`
- `x-next-page-url` → `next_page_url` (partial URL; prepend the server base URL)

Walk pages with `client.follow_next_page(page, item_model)` or `client.iter_pages(...)`. When `x-next-page-url` is a `/pages/{pageId}` cursor, you can also call `client.pages.get(page_id, item_model=...)` (`GET /pages/{pageId}`, operation `getNextPage`). The response is an array of objects plus the same pagination headers; pass the model from the original list.

### Logs

`client.logs.list_device` calls `GET /devicelogs` (operation `getDeviceLogs`). Pass `service_ids` and `actions` to filter (`serviceIds` and `actions` on the query string). Optional filters include `database_ids`, `min_log_level` (`debug`, `info`, `warn`, `error`), and `min_duration` (milliseconds). Provide at most one of `imeis` or `device_ids` (the OpenAPI marks both optional and says only one may be sent). `start_millis` is optional UTC milliseconds (server default: 10 minutes ago), limited to the past 365 days, and the window may not span more than 30 days. `limit` defaults to 1000 on the server. Each call returns one page. Walk further pages with `client.follow_next_page(page, DeviceLog)`, `client.pages.get`, or `client.iter_pages(...)`.

`client.logs.list_telemetry` calls `GET /telemetrylogs`. `start_millis` is optional UTC milliseconds (server default: 4 hours ago). `limit` defaults to 1000 and cannot exceed 5000. Telemetry search can filter by `imeis`.

`client.logs.list_user` calls `GET /userlogs`. `start_millis` is optional UTC milliseconds (server default: 10 minutes ago), with the same 365-day lookback and 30-day window as device logs. User search can filter by `user_ids`, `database_ids`, `service_ids`, `actions`, `min_log_level`, and `min_duration`.

```python
page = client.logs.list_device(
    start_millis=1_700_000_000_000,
    imeis="123456789012345",
    service_ids=["config"],
    actions=["logs"],
    min_log_level="info",
    limit=100,
)
```

### Errors

| HTTP | Exception |
|------|-----------|
| 400 | `BadRequestError` |
| 401 | `AuthenticationError` |
| 403 | `ForbiddenError` |
| 404 | `NotFoundError` |
| 429 | `RateLimitError` |
| other | `APIError` |

### Resource map

| Attribute | Tag | Operations |
|-----------|-----|------------|
| `client.commands` | Commands | list / add / delete |
| `client.devices` | Devices | list (`tag_id` optional) / get / update, plus properties, scratchpad, `delete_scratchpad_keys`, settings synched |
| `client.firmwares` | Firmwares | list / get |
| `client.groups` | Groups | list / get / update |
| `client.logs` | Logs | `list_device` / `list_telemetry` / `list_user` |
| `client.pages` | Pagination | `get` (`GET /pages/{pageId}`) |
| `client.products` | Products | list / get |
| `client.settings` | Settings | get / update (owner is a device or group UUID) |
| `client.tagmaps` | TagMaps | list / get / create / update / delete |
| `client.tags` | Tags | list / get / create / update / delete |
| `client.tenants` | Tenants | list / get / update |
| `client.users` | Users | list / get / update |
| `client.virtual_console` | VirtualConsole | `get_output(device_id, last_date=, last_idx=)` / `send` (text/plain body) |

## Versioning

This package follows [Semantic Versioning](https://semver.org/). `0.1.0` is the first public PyPI release. While the major version is `0`, minor bumps may include breaking changes; patch bumps are bug fixes. `1.0.0` will mark a stable public API. See [RELEASE.md](RELEASE.md) for the publish checklist.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for the venv-scoped runtime `pip-audit` command. Local unit tests:

```bash
pip install -e ".[test]"
# same test tools, plus pip-audit: pip install -r requirements-dev.txt
ruff check src tests
pytest          # mocked unit tests; live marker is excluded by default
```

Unit tests use **respx** mocks — no secrets and no production calls. The default pytest config excludes the `live` marker (`addopts = -m "not live"`), so CI stays mocked.

### Live smoke / integration

Live tests are env-gated and **never default to production**. They require `POSIVERSE_BASE_URL` (your internal test OpenAPI base URL) and refuse the production host.

| Flag | Purpose |
|------|---------|
| `POSIVERSE_LIVE_SMOKE=1` | Enable the minimal smoke test in `tests/test_live_smoke.py` |
| `POSIVERSE_LIVE_INTEGRATION=1` | Enable the full per-tag suite under `tests/integration/` (also enables smoke) |
| `POSIVERSE_API_KEY` | Required for any live run (sent as `posiverse-auth-key`) |
| `POSIVERSE_BASE_URL` | Required for any live run; https only; production is refused |

Linux / macOS:

```bash
# Mocked unit tests (default CI)
pytest

# Full live integration against an internal test OpenAPI
# (or set the same keys in a project-root .env — see Authentication)
POSIVERSE_LIVE_INTEGRATION=1 POSIVERSE_API_KEY=... POSIVERSE_BASE_URL=... pytest -m live -v --tb=short

# Smoke only
POSIVERSE_LIVE_SMOKE=1 POSIVERSE_API_KEY=... POSIVERSE_BASE_URL=... pytest -m live tests/test_live_smoke.py

# With .env already containing POSIVERSE_API_KEY, POSIVERSE_BASE_URL, and a live gate:
pytest -m live -v --tb=short
```

Windows PowerShell:

```powershell
# Mocked unit tests (default CI)
pytest

# Full live integration against an internal test OpenAPI
# (or set the same keys in a project-root .env — see Authentication)
$env:POSIVERSE_LIVE_INTEGRATION = "1"
$env:POSIVERSE_API_KEY = "..."
$env:POSIVERSE_BASE_URL = "https://your-internal-test-openapi.example"
pytest -m live -v --tb=short

# Smoke only
$env:POSIVERSE_LIVE_SMOKE = "1"
$env:POSIVERSE_API_KEY = "..."
$env:POSIVERSE_BASE_URL = "https://your-internal-test-openapi.example"
pytest -m live tests/test_live_smoke.py

# With .env already containing POSIVERSE_API_KEY, POSIVERSE_BASE_URL, and a live gate:
pytest -m live -v --tb=short
```

Windows Command Prompt:

```cmd
REM Mocked unit tests (default CI)
pytest

REM Full live integration against an internal test OpenAPI
set POSIVERSE_LIVE_INTEGRATION=1
set POSIVERSE_API_KEY=...
set POSIVERSE_BASE_URL=https://your-internal-test-openapi.example
pytest -m live -v --tb=short

REM Smoke only
set POSIVERSE_LIVE_SMOKE=1
set POSIVERSE_API_KEY=...
set POSIVERSE_BASE_URL=https://your-internal-test-openapi.example
pytest -m live tests/test_live_smoke.py

REM With .env already containing POSIVERSE_API_KEY, POSIVERSE_BASE_URL, and a live gate:
pytest -m live -v --tb=short
```

Settings write coverage uses the known test device and constraints from `tests/integration/fixtures/Release.json` (mask keys: ver, config, analytics, telemetry, ota, motion, vehicle, driverBehavior, driverId, bluetooth). Prior values are restored when practical. Irreversible deletes (tenants/users/devices) and destructive device commands (for example `reset`) are skipped.

OpenAPI source of truth: `openapi/posiverse.openapi.json`.

## License

MIT
