# posiverse-python-sdk

Production Python SDK for the [Posiverse](https://www.positioninguniversal.com) OpenAPI (v1.1.1).

Built with **httpx** and **pydantic v2**. Covers all OpenAPI tags: Commands, Devices, Firmwares, Groups, Logs, Products, Settings, TagMaps, Tags, Tenants, Users, VirtualConsole.

The OpenAPI document checked into this repository (`openapi/posiverse.openapi.json`) is the source of truth. The SDK does not invent endpoints beyond that spec.

## Install

```bash
pip install -e ".[dev]"   # from a checkout
```

## Authentication

Posiverse uses an API key in the **`posiverse-auth-key`** header (OpenAPI `bearerAuth` is an `apiKey` scheme, **not** HTTP Bearer).

Set the key via environment variable (recommended):

```bash
export POSIVERSE_API_KEY="your-api-key"
```

Use a separate key for test vs production backends. Keys are available in the Posiverse UI under User Profile.

## Servers

| Environment | Base URL |
|-------------|----------|
| **Test (default)** | `https://openapi-test.posiverse.com` |
| Production | `https://openapi-prod.posiverse.com` |

The client defaults to the **test** server to avoid accidental production traffic.

```python
from posiverse import PosiverseClient, TEST_BASE_URL, PROD_BASE_URL

with PosiverseClient() as client:          # TEST_BASE_URL
    ...

# Explicit production URL (do not use in automated tests)
# client = PosiverseClient(base_url=PROD_BASE_URL)
```

## Quickstart

```python
from posiverse import PosiverseClient

# Uses POSIVERSE_API_KEY and defaults to the test server
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

Walk pages with `client.follow_next_page(page, item_model)` or `client.iter_pages(...)`.

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
| `client.devices` | Devices | list / get / update, plus properties, scratchpad, settings synched |
| `client.firmwares` | Firmwares | list / get |
| `client.groups` | Groups | list / get / update |
| `client.logs` | Logs | `list_device` / `list_telemetry` / `list_user` |
| `client.products` | Products | list / get |
| `client.settings` | Settings | get / update |
| `client.tagmaps` | TagMaps | list / get / create / update / delete |
| `client.tags` | Tags | list / get / create / update / delete |
| `client.tenants` | Tenants | list / get / update |
| `client.users` | Users | list / get / update |
| `client.virtual_console` | VirtualConsole | `get_output` / `send` |

## Development

```bash
pip install -e ".[dev]"
ruff check src tests
pytest          # mocked unit tests; live marker is excluded by default
```

Unit tests use **respx** mocks against the test base URL only — no secrets and no production calls.

An optional live smoke test exists (`tests/test_live_smoke.py`) and is skipped unless you set `POSIVERSE_LIVE_SMOKE=1` **and** `POSIVERSE_API_KEY`. It always uses `https://openapi-test.posiverse.com`. Never point it at production.

```bash
POSIVERSE_LIVE_SMOKE=1 POSIVERSE_API_KEY=... pytest -m live
```

OpenAPI source of truth: `openapi/posiverse.openapi.json`.

## License

MIT
