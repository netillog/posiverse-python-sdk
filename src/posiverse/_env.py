"""Load a project ``.env`` file into ``os.environ`` (no extra dependency).

Existing environment variables always win — values already set in the shell
or CI are never overwritten. Safe to call multiple times.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Optional

_LOADED = False


def _candidate_dirs() -> Iterable[Path]:
    """Yield directories to search for a ``.env`` file, nearest first."""
    seen: set[Path] = set()
    cwd = Path.cwd().resolve()
    for base in (cwd, *cwd.parents):
        if base in seen:
            break
        seen.add(base)
        yield base
        if (base / ".git").exists() or (base / "pyproject.toml").exists():
            # Stop climbing past the project root once we have offered it.
            # Still allow cwd-above roots already yielded.
            break

    # Also try the repo root relative to this package (src/posiverse/_env.py).
    here = Path(__file__).resolve()
    package_roots = [here.parents[2]]
    if len(here.parents) > 3:
        package_roots.append(here.parents[3])
    for base in package_roots:
        if base in seen:
            continue
        seen.add(base)
        yield base


def find_dotenv(filename: str = ".env") -> Optional[Path]:
    """Return the first ``.env`` path found walking from cwd / package root.

    Args:
        filename: Env file name to look for (default ``.env``).

    Returns:
        Absolute path to the file, or ``None`` if not found.
    """
    for directory in _candidate_dirs():
        path = directory / filename
        if path.is_file():
            return path
    return None


def load_dotenv(path: Optional[Path] = None, *, override: bool = False) -> Optional[Path]:
    """Parse a ``KEY=VALUE`` env file into ``os.environ``.

    Args:
        path: Explicit file to load. When ``None``, searches via
            :func:`find_dotenv`.
        override: When True, overwrite existing ``os.environ`` keys.
            Default False so shell/CI values win.

    Returns:
        The path that was loaded. A repeat default load returns that same
        path without parsing again. ``None`` if no file was found.
    """
    global _LOADED
    target = path or find_dotenv()
    if target is None:
        return None
    # Allow explicit re-load of a given path; skip duplicate default loads.
    if path is None and _LOADED and not override:
        return target

    # utf-8-sig strips a leading BOM so Notepad-saved Windows files still parse.
    for raw in target.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        # Strip matching single/double quotes.
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        if override or key not in os.environ:
            os.environ[key] = value

    if path is None:
        _LOADED = True
    return target
