"""Products resource — OpenAPI tag Products.

Paths: GET ``/products``, GET ``/products/{productId}``.
"""

from __future__ import annotations

from typing import Optional

from posiverse.models import Product
from posiverse.pagination import PaginatedResponse
from posiverse.resources._base import BaseResource


class ProductsResource(BaseResource):
    """List and fetch product definitions."""

    def list(self, *, tenant_id: Optional[str] = None) -> PaginatedResponse[Product]:
        """List products (operation ``getProducts``).

        Args:
            tenant_id: Alternate tenant UUID.

        Returns:
            Paginated list of :class:`~posiverse.models.product.Product` objects.

        Raises:
            AuthenticationError: Invalid or missing API key.
            ForbiddenError: Insufficient permissions.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        return self._client.request_paginated(
            "GET",
            "/products",
            item_model=Product,
            params={"tenantId": tenant_id},
        )

    def get(self, product_id: str) -> Product:
        """Get a product by ID (operation ``getProduct``).

        Args:
            product_id: Product UUID.

        Returns:
            A :class:`~posiverse.models.product.Product` object.

        Raises:
            NotFoundError: Product not found.
            AuthenticationError: Invalid or missing API key.
            BadRequestError: Invalid request.
            RateLimitError: Rate limited.
        """
        data = self._client.request_json("GET", f"/products/{product_id}")
        return Product.model_validate(data)
