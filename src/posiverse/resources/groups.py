"""Groups resource — OpenAPI tag Groups.

Paths: GET ``/groups``, GET/PUT ``/groups/{groupId}``.
"""

from __future__ import annotations

from typing import Optional, Union

from posiverse.models import Group, GroupPut
from posiverse.pagination import PaginatedResponse
from posiverse.resources._base import BaseResource


class GroupsResource(BaseResource):
    """List, fetch, and update device groups."""

    def list(self, *, tenant_id: Optional[str] = None) -> PaginatedResponse[Group]:
        """List groups (operation ``getGroups``).

        Args:
            tenant_id: Alternate tenant UUID.

        Returns:
            Paginated list of :class:`~posiverse.models.group.Group` objects.

        Raises:
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        return self._client.request_paginated(
            "GET",
            "/groups",
            item_model=Group,
            params={"tenantId": tenant_id},
        )

    def get(self, group_id: str) -> Group:
        """Get a group by ID (operation ``getGroup``).

        Args:
            group_id: Group UUID.

        Returns:
            A :class:`~posiverse.models.group.Group` object.

        Raises:
            NotFoundError: Group not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json("GET", f"/groups/{group_id}")
        return Group.model_validate(data)

    def update(self, group_id: str, body: Union[GroupPut, dict]) -> None:
        """Modify a group (operation ``modifyGroup``).

        Args:
            group_id: Group UUID.
            body: :class:`~posiverse.models.group.GroupPut` or dict of
                mutable fields (name, description).

        Raises:
            NotFoundError: Group not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        self._client.request("PUT", f"/groups/{group_id}", json=self._client.dump_body(body))
