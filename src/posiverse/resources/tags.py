"""Tags resource — OpenAPI tag Tags.

Paths: GET/POST ``/tags``, GET/PUT/DELETE ``/tags/{tagId}``.
"""

from __future__ import annotations

from typing import Optional, Union

from posiverse.models import Tag, TagPut
from posiverse.pagination import PaginatedResponse
from posiverse.resources._base import BaseResource


class TagsResource(BaseResource):
    """Create, read, update, and delete tags."""

    def list(self, *, tenant_id: Optional[str] = None) -> PaginatedResponse[Tag]:
        """List tags (operation ``getTags``).

        Args:
            tenant_id: Alternate tenant UUID.

        Returns:
            Paginated list of :class:`~posiverse.models.tag.Tag` objects.

        Raises:
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        return self._client.request_paginated(
            "GET",
            "/tags",
            item_model=Tag,
            params={"tenantId": tenant_id},
        )

    def create(
        self,
        body: Union[TagPut, dict],
        *,
        tenant_id: Optional[str] = None,
    ) -> Tag:
        """Create a tag (operation ``addTag``).

        Args:
            body: :class:`~posiverse.models.tag.TagPut` or dict with required
                ``name``.
            tenant_id: Alternate tenant UUID.

        Returns:
            The created :class:`~posiverse.models.tag.Tag`.

        Raises:
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json(
            "POST",
            "/tags",
            params={"tenantId": tenant_id},
            json=self._client.dump_body(body),
        )
        return Tag.model_validate(data)

    def get(self, tag_id: str, *, tenant_id: Optional[str] = None) -> Tag:
        """Get a tag by ID (operation ``getTag``).

        Args:
            tag_id: Tag UUID.
            tenant_id: Alternate tenant UUID.

        Returns:
            A :class:`~posiverse.models.tag.Tag` object.

        Raises:
            NotFoundError: Tag not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json(
            "GET",
            f"/tags/{tag_id}",
            params={"tenantId": tenant_id},
        )
        return Tag.model_validate(data)

    def update(
        self,
        tag_id: str,
        body: Union[TagPut, dict],
        *,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Rename a tag (operation ``modifyTag``).

        Args:
            tag_id: Tag UUID.
            body: :class:`~posiverse.models.tag.TagPut` or dict with ``name``.
            tenant_id: Alternate tenant UUID.

        Raises:
            NotFoundError: Tag not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        self._client.request(
            "PUT",
            f"/tags/{tag_id}",
            params={"tenantId": tenant_id},
            json=self._client.dump_body(body),
        )

    def delete(self, tag_id: str, *, tenant_id: Optional[str] = None) -> None:
        """Delete a tag (operation ``deleteTag``).

        The API rejects deletion when TagMaps still reference the tag.

        Args:
            tag_id: Tag UUID.
            tenant_id: Alternate tenant UUID.

        Raises:
            NotFoundError: Tag not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request (for example maps still exist).
            RateLimitError: Rate limited.
        """
        self._client.request(
            "DELETE",
            f"/tags/{tag_id}",
            params={"tenantId": tenant_id},
        )
