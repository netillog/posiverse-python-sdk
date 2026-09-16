# posiverse-python-sdk

Production Python SDK for the [Posiverse](https://www.positioninguniversal.com) OpenAPI (v1.1.1).

Built with **httpx** and **pydantic v2**. Covers all OpenAPI tags: Commands, Devices, Firmwares, Groups, Logs, Products, Settings, TagMaps, Tags, Tenants, Users, VirtualConsole.

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

Use a separate key for test vs production backends.

## Servers

| Environment | Base URL |
|-------------|----------|
| **Test (default)** | `https://openapi-test.posiverse.com` |
| Production | `https://openapi-prod.posiverse.com` |

The client defaults to the **test** server to avoid accidental production traffic.

## Quickstart

```python
from posiverse import PosiverseClient, TEST_BASE_URL, PROD_BASE_URL

# Uses POSIVERSE_API_KEY and defaults to the test server
with PosiverseClient() as client:
    page = client.devices.list()
    print(page.total_count, page.page_count, page.page_start, page.next_page_url)
    for device in page.items:
        print(device.id, device.name, device.imei)

    device = client.devices.get(page.items[0].id, full=True)
    print(device.settings)

# Explicit production URL (do not use in automated tests)
# client = PosiverseClient(base_url=PROD_BASE_URL)
```

### Pagination

List endpoints return a `PaginatedResponse` with items plus headers:

- `x-total-count` → `total_count`
- `x-page-count` → `page_count`
- `x-page-start` → `page_start`
- `x-next-page-url` → `next_page_url` (partial URL; prepend the server base URL)

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

| Attribute | Tag |
|-----------|-----|
| `client.commands` | Commands |
| `client.devices` | Devices (+ properties, scratchpad, settings synched) |
| `client.firmwares` | Firmwares |
| `client.groups` | Groups |
| `client.logs` | Logs (device / telemetry / user) |
| `client.products` | Products |
| `client.settings` | Settings |
| `client.tagmaps` | TagMaps |
| `client.tags` | Tags |
| `client.tenants` | Tenants |
| `client.users` | Users |
| `client.virtual_console` | VirtualConsole |

## Development

```bash
pip install -e ".[dev]"
ruff check src tests
pytest
```

Unit tests use **respx** mocks against the test base URL only — no secrets and no production calls.

OpenAPI source of truth: `openapi/posiverse.openapi.json`.

## License

MIT
