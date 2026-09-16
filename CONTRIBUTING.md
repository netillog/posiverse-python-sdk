# Contributing

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Copy `.env.example` to `.env` for local secrets. `.env` is gitignored — never commit API keys.

## Checks

CI runs these on every pull request. Run them locally before opening a PR:

```bash
ruff check src tests
pytest                 # mocked; live marker excluded
pip-audit --skip-editable
```

Run `pip-audit` inside the same virtualenv. A system Python may report unrelated packages. Do not weaken or skip these checks to land a change.

## Client defaults

Public users talk to production (`https://openapi-prod.posiverse.com`). There is no packaged `environment="test"` helper and no `TEST_BASE_URL` export.

To point the client at an internal OpenAPI:

```bash
export POSIVERSE_API_KEY="..."
export POSIVERSE_BASE_URL="https://your-internal-test-openapi.example"
```

`POSIVERSE_BASE_URL` and `PosiverseClient(base_url=...)` both require https.

## Live tests

Live tests are contributor-only. They must not run in default CI and must not contact production.

1. Set `POSIVERSE_LIVE_SMOKE=1` and/or `POSIVERSE_LIVE_INTEGRATION=1`.
2. Set `POSIVERSE_API_KEY` to a **test** key (never a production key).
3. Set `POSIVERSE_BASE_URL` to your internal test OpenAPI base URL.
4. Run `pytest -m live`.

If `POSIVERSE_BASE_URL` is unset, live tests skip. If it points at production, they fail closed.

Do not log, print, or commit `POSIVERSE_API_KEY`. `PosiverseClient` redacts the key in `repr`/`str`. Prefer `tests.integration.helpers.scrub_secrets` when interpolating exceptions in live tests.

## Security

- TLS verification is on for clients the SDK creates. Do not add a `verify=` constructor argument.
- HTTP timeouts default to 30 seconds and cannot be set to `None`.
- Do not add logging of headers, request objects, or API keys.
- Do not put secrets in the repo, wheels, or GitHub Actions workflow files. Use Trusted Publishing for PyPI (see [RELEASE.md](RELEASE.md)); do not invent or paste tokens.

## Versioning

Follow SemVer. See [RELEASE.md](RELEASE.md) for the first public release notes and publish checklist.
