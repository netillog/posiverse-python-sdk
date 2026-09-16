"""Shared base class for resource namespaces."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from posiverse.client import PosiverseClient


class BaseResource:
    """Bind a resource namespace to a :class:`PosiverseClient` instance.

    Args:
        client: Parent HTTP client used for all requests.
    """

    def __init__(self, client: "PosiverseClient") -> None:
        self._client = client
