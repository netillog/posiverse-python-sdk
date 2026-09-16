"""Package version for the Posiverse Python SDK.

Kept in a dedicated module so :mod:`posiverse.client` can read it without
importing :mod:`posiverse` (which would create a circular import).
"""

__version__ = "0.1.0"
