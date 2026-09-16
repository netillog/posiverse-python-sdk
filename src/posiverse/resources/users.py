"""Users resource — OpenAPI tag Users.

Paths: GET ``/users``, GET/PUT ``/users/{userId}``.
"""

from __future__ import annotations

from typing import Optional, Union

from posiverse.models import User, UserPut
from posiverse.pagination import PaginatedResponse
from posiverse.resources._base import BaseResource


class UsersResource(BaseResource):
    """List, fetch, and update users."""

    def list(self, *, tenant_id: Optional[str] = None) -> PaginatedResponse[User]:
        """List users (operation ``getUsers``).

        Args:
            tenant_id: Alternate tenant UUID.

        Returns:
            Paginated list of :class:`~posiverse.models.user.User` objects.

        Raises:
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        return self._client.request_paginated(
            "GET",
            "/users",
            item_model=User,
            params={"tenantId": tenant_id},
        )

    def get(self, user_id: str) -> User:
        """Get a user by ID (operation ``getUser``).

        Args:
            user_id: User UUID.

        Returns:
            A :class:`~posiverse.models.user.User` object.

        Raises:
            NotFoundError: User not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json("GET", f"/users/{user_id}")
        return User.model_validate(data)

    def update(self, user_id: str, body: Union[UserPut, dict]) -> None:
        """Modify a user (operation ``modifyUser``).

        Args:
            user_id: User UUID.
            body: :class:`~posiverse.models.user.UserPut` or dict of mutable
                fields (name, description).

        Raises:
            NotFoundError: User not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        self._client.request("PUT", f"/users/{user_id}", json=self._client.dump_body(body))
