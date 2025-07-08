# Changes

## Changes from the original SMO

1. **RESTful Best Practices**: We changed the methods for `start`, `stop`, and `placement` from `GET` to `POST`, bc. these are state-changing actions, not simple data retrievals.

2. **Clarity and Organization**:
    *   Added `tags` (`[Clusters]`, `[Graph]`, `[Internal]`) for organizing the API in the Swagger UI.
    *   Detailed the `summary` and `description` fields for developers who will use the API.
    *   The use of reusable `responses` and `schemas` in the `components` section (e.g., `Problem`, `NotFound`) keeps the specification DRY (Don't Repeat Yourself) and easy to maintain.

3. **Error Handling**: We defined a standard `Problem` schema (based on RFC 7807) and reusing it for `4xx` and `5xx` responses.
