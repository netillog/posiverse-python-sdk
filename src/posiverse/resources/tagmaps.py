"""TagMaps resource — OpenAPI tag TagMaps.

Paths: GET ``/tagmaps/{tagId}``, GET/PUT/POST/DELETE
``/tagmaps/{tagId}/{objectId}``.
"""

from __future__ import annotations

from typing import Optional, Union

from posiverse.models import TagMap, TagMapPut
from posiverse.pagination import PaginatedResponse
from posiverse.resources._base import BaseResource


class TagMapsResource(BaseResource):
    """Associate tags with devices, groups, or users."""

    def list(self, tag_id: str, *, tenant_id: Optional[str] = None) -> PaginatedResponse[TagMap]:
        """List maps for a tag (operation ``getTagMaps``).

        Args:
            tag_id: Tag UUID.
            tenant_id: Alternate tenant UUID.

        Returns:
            Paginated list of :class:`~posiverse.models.tag.TagMap` objects.

        Raises:
            NotFoundError: Tag not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        return self._client.request_paginated(
            "GET",
            f"/tagmaps/{tag_id}",
            item_model=TagMap,
            params={"tenantId": tenant_id},
        )

    def get(
        self,
        tag_id: str,
        object_id: str,
        *,
        tenant_id: Optional[str] = None,
    ) -> TagMap:
        """Get a single tag map (operation ``getTagMap``).

        Args:
            tag_id: Tag UUID.
            object_id: UUID of the device, group, or user (``ownerId``).
            tenant_id: Alternate tenant UUID.

        Returns:
            A :class:`~posiverse.models.tag.TagMap` object.

        Raises:
            NotFoundError: Map not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json(
            "GET",
            f"/tagmaps/{tag_id}/{object_id}",
            params={"tenantId": tenant_id},
        )
        return TagMap.model_validate(data)

    def create(
        self,
        tag_id: str,
        object_id: str,
        body: Union[TagMapPut, dict],
        *,
        tenant_id: Optional[str] = None,
    ) -> TagMap:
        """Create a tag map (operation ``addTagMap``).

        Args:
            tag_id: Tag UUID.
            object_id: UUID of the device, group, or user.
            body: :class:`~posiverse.models.tag.TagMapPut` or dict with
                required ``value``.
            tenant_id: Alternate tenant UUID.

        Returns:
            The created :class:`~posiverse.models.tag.TagMap`.

        Raises:
            NotFoundError: Tag or object not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json(
            "POST",
            f"/tagmaps/{tag_id}/{object_id}",
            params={"tenantId": tenant_id},
            json=self._client.dump_body(body),
        )
        return TagMap.model_validate(data)

    def update(
        self,
        tag_id: str,
        object_id: str,
        body: Union[TagMapPut, dict],
        *,
        tenant_id: Optional[str] = None,
    ) -> TagMap:
        """Update a tag map value (operation ``modifyTagMap``).

        Args:
            tag_id: Tag UUID.
            object_id: UUID of the device, group, or user.
            body: :class:`~posiverse.models.tag.TagMapPut` or dict with
                required ``value``.
            tenant_id: Alternate tenant UUID.

        Returns:
            The updated :class:`~posiverse.models.tag.TagMap`.

        Raises:
            NotFoundError: Map not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json(
            "PUT",
            f"/tagmaps/{tag_id}/{object_id}",
            params={"tenantId": tenant_id},
            json=self._client.dump_body(body),
        )
        return TagMap.model_validate(data)

    def delete(
        self,
        tag_id: str,
        object_id: str,
        *,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Delete a tag map (operation ``deleteTagMap``).

        Args:
            tag_id: Tag UUID.
            object_id: UUID of the device, group, or user.
            tenant_id: Alternate tenant UUID.

        Raises:
            NotFoundError: Map not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        self._client.request(
            "DELETE",
            f"/tagmaps/{tag_id}/{object_id}",
            params={"tenantId": tenant_id},
        )
