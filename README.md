# posiverse-python-sdk

Python SDK for the [Posiverse](https://www.positioninguniversal.com) OpenAPI (v1.1.1).

Built with **httpx** and **pydantic v2**. Requires Python 3.10 or newer. Covers all OpenAPI tags: Commands, Devices, Firmwares, Groups, Logs, Products, Settings, TagMaps, Tags, Tenants, Users, VirtualConsole.

The SDK follows the Posiverse OpenAPI v1.1.1 and does not invent endpoints beyond that spec.

This package is **not on PyPI yet**. Install from a clone of `main`:

```bash
git clone https://github.com/netillog/posiverse-python-sdk.git
cd posiverse-python-sdk
git checkout main
pip install .
```

After the first PyPI release:

```bash
pip install posiverse
```

## Authentication

Posiverse uses an API key in the **`posiverse-auth-key`** header (OpenAPI `bearerAuth` is an `apiKey` scheme, **not** HTTP Bearer).

Set `POSIVERSE_API_KEY` in your shell. Keys are available in the Posiverse UI under User Profile. Never commit API keys or paste them into logs.

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

## Production client

The client defaults to production. `PRODUCTION_BASE_URL` is `https://openapi-prod.posiverse.com`.

```python
from posiverse import PosiverseClient

with PosiverseClient() as client:  # production; key from POSIVERSE_API_KEY
    ...
```

HTTP URLs are rejected. TLS verification and request timeouts are on by default and cannot be turned off through the client constructor.

## Quickstart

```python
from posiverse import PosiverseClient

# Uses POSIVERSE_API_KEY from the environment and defaults to production
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

### Device logs, reports, and device data

`client.logs.get_logs`, `get_reports`, and `get_device_data` wrap `GET /devicelogs` (`list_device`). They do not add endpoints.

| Method | Query clauses (`serviceIds` / `actions`) |
|--------|------------------------------------------|
| `get_logs` | `config` / `logs` |
| `get_reports` | `tel` / *(omitted)*, then `conn` / `new-sent`, `retry-sent` |
| `get_device_data` | the union of those clauses |

`GET /devicelogs` has no boolean filter parameter. `serviceIds` and `actions` are sent as separate conjunctive requests and merged in the client. Each clause follows `x-next-page-url`. `limit` applies to the first request of each clause.

`get_reports` and `get_device_data` keep one row per `ts` + `rpt` pair. Those names are not `DeviceLog` schema fields. The SDK reads them from the `request` JSON object, then `result`, then extra top-level fields (`ReportIdentity`). Rows without both keys are kept. When two report rows share the pair and differ elsewhere, the earlier merged row is kept: `tel` before `conn`, and config logs before reports.

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
| `client.logs` | Logs | `list_device` / `list_telemetry` / `list_user`, plus `get_logs` / `get_reports` / `get_device_data` |
| `client.products` | Products | list / get |
| `client.settings` | Settings | get / update |
| `client.tagmaps` | TagMaps | list / get / create / update / delete |
| `client.tags` | Tags | list / get / create / update / delete |
| `client.tenants` | Tenants | list / get / update |
| `client.users` | Users | list / get / update |
| `client.virtual_console` | VirtualConsole | `get_output` / `send` |

## Versioning

This package follows [Semantic Versioning](https://semver.org/). `0.1.0` is the first public PyPI release. While the major version is `0`, minor bumps may include breaking changes; patch bumps are bug fixes. `1.0.0` will mark a stable public API. See [RELEASE.md](RELEASE.md) for the publish checklist.

## Contributing

Library development lives on the [`develop`](https://github.com/netillog/posiverse-python-sdk/tree/develop) branch. See `CONTRIBUTING.md` there.

## License

MIT
