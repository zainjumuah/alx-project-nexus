# Products App

`products` owns the product catalog domain: product and category data, API serializers, viewsets, filtering/discovery behavior, and test coverage.

## Responsibilities

- Product and category models
- DRF serializers for product/category payloads
- API viewsets for CRUD + discovery query support
- API/performance/model tests for this domain

## Key Files

- `products/models.py`: `Product`, `Category`, constraints, indexes
- `products/serializers.py`: API serialization for product/category resources
- `products/views.py`: tagged Swagger docs + viewset behavior
- `products/urls.py`: router wiring for products/categories endpoints
- `products/tests/`: API, discovery, perf, and model tests

## API Notes

- Endpoints are mounted under `/api/` from project urls.
- Writes require JWT (`Authorization: Bearer <access_token>`).
- Discovery supports:
  - `?category=<id>`
  - `?ordering=price|-price|created_at|-created_at`
  - `?page=<n>&page_size=<n>`

## Development Notes

- Keep query behavior and Swagger docs aligned.
- Keep tests updated when changing filters, ordering, or permissions.
- Preserve `select_related("category")` and perf tests when touching list behavior.
