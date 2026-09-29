"""Pagination resource — OpenAPI operation ``getNextPage``.

Path: GET ``/pages/{pageId}``.
"""

from __future__ import annotations

from typing import Type, TypeVar

from pydantic import BaseModel

from posiverse.pagination import PaginatedResponse
from posiverse.resources._base import BaseResource

T = TypeVar("T", bound=BaseModel)


class PagesResource(BaseResource):
    """Fetch a cursor page from ``GET /pages/{pageId}``."""

    def get(self, page_id: str, *, item_model: Type[T]) -> PaginatedResponse[T]:
        """Retrieve the next page of results (operation ``getNextPage``).

        ``page_id`` is the cursor token from ``x-next-page-url``. The header
        is still a partial URL; this method calls ``/pages/{pageId}`` directly.
        ``follow_next_page`` remains available when the header is already a
        request path.

        Args:
            page_id: Unique token identifier for the next page of results.
            item_model: Pydantic model used to validate each array element.
                The OpenAPI types the body as an array of objects; callers
                pass the model for the original list.

        Returns:
            A :class:`~posiverse.pagination.PaginatedResponse` of ``item_model``
            instances, with pagination taken from the ``x-*`` headers.

        Raises:
            NotFoundError: Page token not found.
            AuthenticationError: Invalid or missing API key.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
            TypeError: If the JSON body is not a list.
        """
        return self._client.request_paginated(
            "GET",
            f"/pages/{page_id}",
            item_model=item_model,
        )
