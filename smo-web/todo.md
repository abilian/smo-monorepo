# TODO

## Minor improvements

### More Specific Request Body Schemas

*   In `POST /project/{project}/graphs`, the `requestBody` schema is defined simply as `type: object`. While valid, the API could be made more self-descriptive and enable better validation by defining a schema for the HDAG descriptor itself.
*   Similarly, the `POST /alerts` endpoint could have a schema that defines the expected fields from an Alertmanager payload (e.g., `alerts`, `labels`, `annotations`).

**Example:**

```yaml
# In components/schemas:
HdagDescriptor:
  type: object
  required: [hdaGraph]
  properties:
    hdaGraph:
      type: object
      properties:
        id: { type: string }
        # ... other required fields of a graph descriptor
```

And then reference it in the `requestBody`:

```yaml
# In POST /project/{project}/graphs:
requestBody:
  content:
    application/json:
      schema:
        # $ref: '#/components/schemas/HdagDescriptor'
        # Or define an inline schema that points to an artifact
        oneOf:
          - $ref: '#/components/schemas/HdagDescriptor'
          - type: object
            properties:
              artifact: { type: string, format: uri }
```

### Add `examples`

For complex request bodies like the graph deployment, adding an `example` or `examples` field can be incredibly helpful for users of your API. It shows them exactly what a valid request looks like.

**Example:**

```yaml
# In POST /project/{project}/graphs's requestBody content:
application/json:
  schema:
    type: object
  example:
    artifact: "oci://my-registry/my-app:1.0"
```

### Refine Parameter Descriptions

The descriptions are good, but some could be slightly more specific.

*   For `GET /graphs/{name}`, the description for the `name` parameter could be "The unique name of the graph to fetch."

### A Note on Implementation (Regarding the `NonConformingResponseHeaders` Error)

Operations like `GET /clusters` define responses for both `200 OK` (with `application/json`) and `500` (with `application/problem+json`), so the handler code **must be explicit about the `Content-Type` it is returning**.

*   **For a successful `get_clusters` response**, the handler must return:

    ```python
    return clusters_list, 200, {"Content-Type": "application/json"}
    ```

* **For an error**, the error handler must return a problem detail response, which will automatically have the `application/problem+json` content type.
