"""Tenants resource — OpenAPI tag Tenants.

Paths: GET ``/tenants``, GET/PUT ``/tenants/{tenantId}``.
"""

from __future__ import annotations

from typing import Union

from posiverse.models import Tenant, TenantPut
from posiverse.pagination import PaginatedResponse
from posiverse.resources._base import BaseResource


class TenantsResource(BaseResource):
    """List, fetch, and update tenants."""

    def list(self) -> PaginatedResponse[Tenant]:
        """List tenants (operation ``getTenants``).

        Listing multiple tenants is only meaningful for accounts with
        access to more than one tenant.

        Returns:
            Paginated list of :class:`~posiverse.models.tenant.Tenant` objects.

        Raises:
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        return self._client.request_paginated("GET", "/tenants", item_model=Tenant)

    def get(self, tenant_id: str) -> Tenant:
        """Get a tenant by ID (operation ``getTenant``).

        Args:
            tenant_id: Tenant UUID.

        Returns:
            A :class:`~posiverse.models.tenant.Tenant` object.

        Raises:
            NotFoundError: Tenant not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json("GET", f"/tenants/{tenant_id}")
        return Tenant.model_validate(data)

    def update(self, tenant_id: str, body: Union[TenantPut, dict]) -> None:
        """Modify a tenant (operation ``modifyTenant``).

        Args:
            tenant_id: Tenant UUID.
            body: :class:`~posiverse.models.tenant.TenantPut` or dict of
                mutable fields (name, description).

        Raises:
            NotFoundError: Tenant not found.
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        self._client.request(
            "PUT",
            f"/tenants/{tenant_id}",
            json=self._client.dump_body(body),
        )
