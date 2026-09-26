# Release

This document is the checklist for publishing `posiverse` to PyPI. The first public release is **0.1.0**.

## Semantic versioning

The project follows [Semantic Versioning](https://semver.org/):

| Increment | When |
|-----------|------|
| **MAJOR** | Breaking changes after `1.0.0` |
| **MINOR** | New backwards-compatible features; while major is `0`, this may also include breaking changes |
| **PATCH** | Backwards-compatible bug fixes |

`0.1.0` is the first public PyPI release of a single package (no packaged test host). Intentional pre-1.0 breaking changes for public consumers:

- Default base URL is production, not a test host.
- `TEST_BASE_URL` and any `environment="test"` helper are not part of the public API.
- Base URL overrides use `base_url=` and/or `POSIVERSE_BASE_URL` (https only).

`1.0.0` will mark a stable public API. Until then, treat minor bumps as possibly breaking and call them out in the GitHub release notes.

Keep `src/posiverse/_version.py` and `[project].version` in `pyproject.toml` in sync.

## Branches

Publish from `main`. That branch is the release surface: library sources, this checklist, and the consumer README. Its CI job is `package`. That job builds the wheel and sdist, runs `twine check`, an import smoke test, ruff on `src`, and a runtime `pip-audit`. It does not run pytest.

`develop` is the engineering branch (tests, OpenAPI document, contributor docs, optional test/dev dependencies). Its CI job is `lint-and-test`. Mocked unit tests run on `develop`. Do not tag a release or publish from `develop`.

The sdist built from `main` includes `/src`, `README.md`, `LICENSE`, and `pyproject.toml`. It does not include `tests/`, `openapi/`, `CONTRIBUTING.md`, `RELEASE.md`, `.env.example`, or `requirements*` files (`requirements.txt`, `requirements-dev.txt`). This checklist stays in git and stays out of the sdist.

Nothing is uploaded to PyPI until the owner explicitly asks, by merging the dedicated change that turns the publish gate on. Do not publish from `develop`, from a GitHub Release, or from a casual `workflow_dispatch`.

## Publish gate

`.github/workflows/publish.yml` keeps the Trusted Publishing skeleton: the publish job has `permissions: id-token: write`, `environment: pypi`, and `pypa/gh-action-pypi-publish`, and it does not set a username, stored token, or API key.

Upload is off by default.

- The workflow has no `on: release` trigger. Publishing a GitHub Release does not upload to PyPI.
- `workflow_dispatch` is the only trigger. It builds and checks the distributions. The publish job runs only when `ENABLE_PYPI_PUBLISH` is `true`.
- `ENABLE_PYPI_PUBLISH` is `"false"` in the `guard` job. That env var is the only switch. While it is false, dispatch does not request the `pypi` environment and does not upload.
- The build fails unless the ref is `refs/heads/main`, or a tag whose commit is contained in `main`. Any other ref, including `develop`, is refused.
- The build fails if the sdist contains `tests`, `openapi`, `CONTRIBUTING.md`, `RELEASE.md`, `.env.example`, or a `requirements*` path, or if wheel `METADATA` or sdist `PKG-INFO` contains `Provides-Extra` or `Project-URL`. That refuses a fat `develop` artifact even if a ref check were bypassed.

### How the owner re-enables publish

In a dedicated pull request, change `ENABLE_PYPI_PUBLISH` from `"false"` to `"true"` in the `guard` job of `.github/workflows/publish.yml`. Merge that pull request to `main` before dispatching. Apply the same one-line change on `develop` so the workflow files stay aligned, but dispatch only on `main` or on a tag of a commit that is on `main`.

After the flag is `true`, run the `Publish` workflow via **Actions → Publish → Run workflow** on `main` (or on that tag). Approve the `pypi` environment if protection rules require it. Leave the release trigger unset; `workflow_dispatch` on an allowed ref is the upload path.

## Trusted Publishing (OIDC) — do not invent tokens

Do **not** create long-lived PyPI API tokens, paste tokens into GitHub secrets, or commit credentials. Use [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) so GitHub Actions exchanges a short-lived OIDC token.

### One-time PyPI setup

1. Create the project on PyPI if it does not exist (a pending publisher can be registered before the first upload).
2. Open the project **Publishing** settings (or your account’s pending publishers).
3. Add a GitHub Actions trusted publisher with **exactly**:
   - Owner: `netillog`
   - Repository: `posiverse-python-sdk`
   - Workflow name: `publish.yml` (must match `.github/workflows/publish.yml`)
   - Environment name: `pypi` (recommended)
4. Do not generate a PyPI API token for this automation.

Official docs: [Adding a trusted publisher](https://docs.pypi.org/trusted-publishers/adding-a-publisher/) and [GitHub: Configuring OpenID Connect in PyPI](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-pypi).

### One-time GitHub setup

1. Create a GitHub Actions environment named `pypi`.
2. Add protection rules (required reviewers) so a human approves each publish.
3. Confirm `.github/workflows/publish.yml` has `permissions: id-token: write` on the publish job and does **not** set `user`/`password`/`password-token` on `pypa/gh-action-pypi-publish`.
4. Leave `ENABLE_PYPI_PUBLISH` set to `"false"` until the owner explicitly asks to publish.

## Publish steps

1. Ensure CI is green on `main` for the commit you intend to ship (`package`: ruff on `src`, runtime `pip-audit`, wheel/sdist build, `twine check`, import smoke). Confirm mocked unit tests are green on `develop` (`lint-and-test`). `main` CI does not run pytest.
2. Confirm the version in `pyproject.toml` and `src/posiverse/_version.py`.
3. Do not upload yet. Creating a GitHub Release or running `workflow_dispatch` does not publish while `ENABLE_PYPI_PUBLISH` is `"false"`. A dispatch on `main` only builds and checks; a dispatch on `develop` fails.
4. When the owner has explicitly asked to publish, merge the dedicated PR that sets `ENABLE_PYPI_PUBLISH` to `"true"` on `main`, then run `Publish` via `workflow_dispatch` on `main` or on a tag of that `main` commit. Approve the `pypi` environment if protection rules require it.
5. Verify the files on [PyPI](https://pypi.org/project/posiverse/) and that the project description matches README (production default, no test hostname).

Local dry-run (does not upload):

```bash
pip install build twine
python -m build
twine check dist/*
```

Never pass `--username` / `--password` or a token file into the GitHub publish job.
