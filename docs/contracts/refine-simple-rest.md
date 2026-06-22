# @refinedev/simple-rest conventions

This project uses `@refinedev/simple-rest` as the Refine data provider. Backend endpoints
and frontend queries must follow these conventions to work correctly.

Backend behavior should be implemented with the `fastapi-refine` package. Prefer
`RefineCRUDRouter`, `refine_query(...)`, `refine_response()`, `FilterConfig`, and
`SortConfig` over custom per-route query parsing.

## Base URL and resources
- `apiUrl` is the REST base. Each resource is addressed as `${apiUrl}/{resource}`.
- `resources[].name` values map directly to REST paths (for example `blog_posts`).

## List (getList)
- Method: `GET` by default (override with `meta.method`).
- Pagination (server mode, default): `_start` and `_end` query params (0-based range).
  - `currentPage` defaults to `1`, `pageSize` defaults to `10`.
- Total count: response should include `x-total-count` header.
  - If missing, Refine falls back to `data.length`.
- Sorting: `_sort` and `_order` query params; multiple fields are comma-separated.
- Filtering: see filter mapping below.

Example:
`GET /blog_posts?_start=0&_end=10&_sort=title,createdAt&_order=asc,desc&status=published`

## Get one
`GET /{resource}/{id}`

## Get many
`GET /{resource}?id=1&id=2&id=3`

## Create
`POST /{resource}` with JSON body

## Update
`PATCH /{resource}/{id}` with JSON body (override with `meta.method` if needed)

## Delete
`DELETE /{resource}/{id}`
- If `variables` are provided, they are sent as the request body.

## Filter mapping
Simple REST uses json-server style parameters:
- `eq` (default): `field=value`
- `ne`: `field_ne=value`
- `gte`: `field_gte=value`
- `lte`: `field_lte=value`
- `contains`: `field_like=value`
- Full-text search uses `q=...` (set filter field to `"q"`).

Not supported:
- Compound filters with `operator: "and"` or `"or"` (throws an error).
- Any other operators are treated as `eq` without a suffix.

## Custom requests
`dataProvider.custom` builds a `GET` URL with sorters/filters/query as above.
For `post/put/patch`, the payload is sent as the body. For `delete`, payload is sent
as `data` in the request.

## Implications for code generation
- Avoid `useCreateMany`, `useUpdateMany`, `useDeleteMany`, or compound filters.
- Prefer server pagination and ensure the backend returns `x-total-count` on list endpoints.
- When adding new filters or sorters, match the mapping above so the backend understands them.
