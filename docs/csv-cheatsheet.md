# CSV Cheat Sheet

## Which template to use

- Use [basic_template.csv](/C:/Users/jonew/Downloads/Pu/Quick-Run-Regression-API/assets/basic_template.csv) when you only need status-code checks.
- Use [advanced_template.csv](/C:/Users/jonew/Downloads/Pu/Quick-Run-Regression-API/assets/advanced_template.csv) when you need auth, headers, request bodies, timeouts, or response validation.

## Minimum columns

- `group`
- `api_name`
- `method`
- `endpoint`
- `expected_status`

## Optional columns

- `request_body`: JSON request body as text
- `headers`: JSON headers object as text
- `auth_type`: `Bearer` or `API Key`
- `auth_value`: token or API key value
- `auth_header_name`: header name for API key mode such as `X-API-Key`
- `timeout_seconds`: request timeout per row
- `response_json_path`: dot path into JSON response such as `data.email` or `items.0.id`
- `expected_value`: expected value for equality and numeric comparisons
- `match_type`: comparison mode
- `expected_contains`: text or value for `contains` and `not_contains`

## Placeholder support

- You can use placeholders in `request_body`, `headers`, `auth_value`, and `endpoint`
- Supported placeholders:
  - `{{TOKEN}}`
  - `{{API_KEY}}`
  - `{{AUTH_VALUE}}`
  - `{{AUTH_HEADER_NAME}}`
  - `{{BASE_URL}}`
- Example header JSON:

```csv
headers
"{""Authorization"":""Bearer {{TOKEN}}""}"
```

## Match type quick guide

- `equals`
  - exact match
  - example: `userId = 1`
- `not_equals`
  - value must be different
  - example: username is not `guest`
- `contains`
  - string contains text or array contains item
  - example: message contains `approved`
- `not_contains`
  - string must not contain text or array must not contain item
  - example: message must not contain `error`
- `exists`
  - field must exist and not be empty
  - example: `data.token`
- `greater_than`
  - numeric value must be greater than expected
  - example: `total > 0`
- `less_than`
  - numeric value must be less than expected
  - example: `duration < 5`
- `greater_or_equal`
  - numeric value must be greater than or equal to expected
  - example: `total >= 0`
- `less_or_equal`
  - numeric value must be less than or equal to expected
  - example: `price <= 100`

## Common examples

### Exact value

```csv
response_json_path,expected_value,match_type
data.status,"""SUCCESS""",equals
```

### Field exists

```csv
response_json_path,match_type
data.token,exists
```

### Contains text

```csv
response_json_path,match_type,expected_contains
message,contains,approved
```

### Numeric threshold

```csv
response_json_path,expected_value,match_type
data.total,0,greater_than
```

## Tips

- Leave advanced columns blank when you do not need them.
- Start with the basic template first, then copy rows into the advanced template only for APIs that need deeper validation.
- Use valid JSON in `request_body` and `headers`.
- For string `expected_value`, wrap it as a JSON string such as `"approved"` so it is parsed correctly.
