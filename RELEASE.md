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

Publish from `main`. That branch is the release surface: library sources, this checklist, and the consumer README. Its CI builds the wheel and sdist, runs `twine check`, an import smoke test, ruff on `src`, and a runtime `pip-audit`. It does not run pytest.

`develop` is the engineering branch (tests, OpenAPI document, contributor docs, optional test/dev dependencies). Mocked unit tests run on `develop`. Do not tag a release or publish from `develop`.

The sdist built from `main` includes `/src`, `README.md`, `LICENSE`, and `pyproject.toml`. It does not include `tests/`, `openapi/`, `CONTRIBUTING.md`, `RELEASE.md`, `.env.example`, or `requirements-dev.txt`. This checklist stays in git and stays out of the sdist.

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

## Publish steps

1. Ensure CI is green on `main` for the commit you intend to ship (ruff on `src`, runtime `pip-audit`, wheel/sdist build, `twine check`, import smoke). Confirm mocked unit tests are green on `develop`.
2. Confirm the version in `pyproject.toml` and `src/posiverse/_version.py`.
3. Tag `v0.1.0` (or the current version) and push the tag, **or** create a GitHub Release, **or** run the `Publish` workflow via `workflow_dispatch`.
4. Approve the `pypi` environment if protection rules require it.
5. Verify the files on [PyPI](https://pypi.org/project/posiverse/) and that the project description matches README (production default, no test hostname).

Local dry-run (does not upload):

```bash
pip install build twine
python -m build
twine check dist/*
```

Never pass `--username` / `--password` or a token file into the GitHub publish job.
