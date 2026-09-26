"""Release hygiene: no test host or secrets in published library sources."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src" / "posiverse"
TEST_HOST = "openapi-test.posiverse.com"

SECRET_PATTERNS = (
    (re.compile(r"pypi-AgE[\w-]+"), "PyPI API token"),
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "GitHub token"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "GitHub PAT"),
    (re.compile(r"(?i)AKIA[0-9A-Z]{16}"), "AWS access key"),
)


def _iter_text_files():
    skip_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        "dist",
        "build",
    }
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pyc", ".whl", ".zip"}:
            continue
        yield path


def test_published_library_omits_test_host():
    """Installed package sources must not embed the test OpenAPI hostname."""
    hits = []
    for path in SRC_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".pyi", ".md", ".txt"} and path.name != "py.typed":
            continue
        text = path.read_text(encoding="utf-8")
        if TEST_HOST in text:
            hits.append(path.relative_to(REPO_ROOT).as_posix())
    assert hits == []


def test_readme_and_pyproject_omit_test_host():
    """Public README and package metadata must not paste the test hostname."""
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert TEST_HOST not in readme
    assert TEST_HOST not in pyproject
    assert "TEST_BASE_URL" not in readme
    assert 'environment="test"' not in readme


def test_no_committed_dotenv():
    """Real env files must not be committed."""
    assert not (REPO_ROOT / ".env").exists()
    example = REPO_ROOT / ".env.example"
    assert example.exists()
    text = example.read_text(encoding="utf-8")
    assert "POSIVERSE_API_KEY=" in text
    assert "POSIVERSE_BASE_URL=" in text
    assert TEST_HOST not in text


def test_no_verify_false_in_library():
    """Library source must not disable TLS verification."""
    for path in SRC_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.keyword) or node.arg != "verify":
                continue
            value = node.value
            if isinstance(value, ast.Constant) and value.value is False:
                pytest.fail(f"verify=False in {path}")


def test_no_accidental_key_material():
    """Scan the repo for common leaked token prefixes."""
    hits = []
    for path in _iter_text_files():
        relative = path.relative_to(REPO_ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern, label in SECRET_PATTERNS:
            if pattern.search(text):
                hits.append(f"{relative}: {label}")
    assert hits == []


def test_publish_workflow_uses_oidc_not_tokens():
    """The publish workflow must use Trusted Publishing, not a stored token."""
    workflow = (REPO_ROOT / ".github" / "workflows" / "publish.yml").read_text(encoding="utf-8")
    assert "id-token: write" in workflow
    assert "pypa/gh-action-pypi-publish" in workflow
    assert "environment:" in workflow
    assert "name: pypi" in workflow
    assert "password:" not in workflow.lower()
    assert "PYPI_API_TOKEN" not in workflow


def test_publish_workflow_is_off_until_explicitly_enabled():
    """Upload stays off until the owner flips ENABLE_PYPI_PUBLISH in a dedicated PR."""
    workflow = (REPO_ROOT / ".github" / "workflows" / "publish.yml").read_text(encoding="utf-8")
    assert 'ENABLE_PYPI_PUBLISH: "false"' in workflow
    assert 'ENABLE_PYPI_PUBLISH: "true"' not in workflow
    assert "\n  release:" not in workflow
    assert "types: [published]" not in workflow
    assert "needs.guard.outputs.enabled == 'true'" in workflow


def test_release_docs_exist():
    """Trusted Publishing and SemVer notes must be present for the first release."""
    contributing = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    release = (REPO_ROOT / "RELEASE.md").read_text(encoding="utf-8")
    assert "Trusted Publishing" in release
    assert "OIDC" in release
    assert "do not" in release.lower()
    assert "token" in release.lower()
    assert "Semantic Versioning" in release or "SemVer" in release
    assert "ENABLE_PYPI_PUBLISH" in release
    assert "develop" in release and "main" in release
    assert "does not run pytest" in release
    assert "POSIVERSE_BASE_URL" in contributing
    assert "pip-audit" in contributing
