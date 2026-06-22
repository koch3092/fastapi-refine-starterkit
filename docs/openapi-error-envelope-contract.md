# OpenAPI Error Envelope Contract

Runtime API errors are normalized by `fastapi-refine` through
`configure_refine(app)` in `backend/app/main.py`.

Typical response shape:

```json
{
  "message": "User not found",
  "statusCode": 404,
  "code": "user.not_found",
  "errors": null,
  "detail": null
}
```

| Field | Required | Meaning |
| --- | --- | --- |
| `message` | yes | Human-readable message for the UI |
| `statusCode` | yes | HTTP status code |
| `code` | no | Stable machine code for business errors |
| `errors` | no | Field-level validation errors, mainly for 422 responses |
| `detail` | no | Extra context, emitted only when it differs from `message` |

## Backend

- `backend/app/main.py` calls `configure_refine(app)` so FastAPI errors are formatted consistently at runtime.
- `backend/app/api/main.py` attaches `refine_error_responses(status_codes=(400, 401, 403, 404, 409, 422, 500, 503))` to the top-level router.
- This makes the same error envelope visible in OpenAPI instead of only changing runtime responses.

## Frontend

The Refine data provider uses `@refinedev/simple-rest`, whose axios instance receives the
runtime envelope as `error.response.data`.

When handling an unknown error body, narrow before reading fields:

```ts
type RefineErrorResponse = {
  message: string;
  statusCode: number;
  errors?: Record<string, string[]> | null;
  detail?: unknown;
  code?: string | null;
};

function isRefineErrorResponse(body: unknown): body is RefineErrorResponse {
  return (
    !!body &&
    typeof body === "object" &&
    "message" in body &&
    "statusCode" in body
  );
}
```

## Adding Business Error Codes

If the project grows a central error-code enum, keep values stable and named as
`<resource>.<event>`, then raise them through `fastapi_refine.RefineHTTPException`.
