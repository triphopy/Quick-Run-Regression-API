# Import Adapter Design

## Purpose

This document describes how the project should handle CSV files from external teams when their format does not match the tool's internal CSV schema.

The main design goal is:

- keep the app's internal schema stable
- accept multiple external CSV formats
- isolate format-specific logic in a small adapter layer
- avoid rewriting parser, runner, dashboard, or export logic every time an upstream file changes

## Core Principle

The tool should treat incoming files and execution files as two different things:

1. External format
- the CSV structure provided by another team
- may change over time
- may use different column names or conventions

2. Internal format
- the normalized schema used by this tool
- should remain stable
- should be the only format understood by parser, runner, dashboard, and export logic

The adapter layer exists to translate external format into internal format.

## Recommended Architecture

```text
Uploaded CSV
-> Import Adapter Detection
-> Format-Specific Adapter
-> Normalized Internal Rows
-> Existing Parser / Validator
-> TestCase Objects
-> Runner / Dashboard / Log / Export
```

## Internal Schema

The internal schema should remain the source of truth for the rest of the system.

Current required internal columns:

- `group`
- `api_name`
- `method`
- `endpoint`
- `expected_status`

Current optional internal columns:

- `request_body`
- `headers`
- `auth_type`
- `auth_value`
- `auth_header_name`
- `timeout_seconds`
- `response_json_path`
- `expected_value`
- `match_type`
- `expected_contains`

Any external file should be mapped into this schema before the existing parser and validation flow continues.

## Adapter Responsibilities

Each import adapter should be responsible for:

- recognizing whether it can handle a given file
- mapping external column names to internal names
- filling default values when the external file does not provide them
- transforming values into internal conventions
- producing normalized rows ready for internal parsing

Adapters should not be responsible for:

- rendering UI
- executing API tests
- computing dashboard summaries
- exporting results

## Typical Problems an Adapter Should Solve

### Different column names

Example:

- external: `api`, `url`, `http_method`
- internal: `api_name`, `endpoint`, `method`

### Missing columns

Example:

- no `expected_status` in the external file
- adapter provides a default such as `200`

### Different value conventions

Example:

- external method value: `get`
- internal method value: `GET`

### Combined or split fields

Example:

- external file has `base_url` and `path`
- internal tool wants a single `endpoint`

### Validation rules expressed differently

Example:

- external file stores `expected` as `status=200`
- adapter extracts `expected_status=200`

## Proposed Module Layout

```text
src/
└─ importers/
   ├─ __init__.py
   ├─ base.py
   ├─ factory.py
   ├─ internal_csv.py
   ├─ team_external_csv.py
   └─ helpers.py
```

### `src/importers/base.py`

Defines a common interface for all import adapters.

Suggested shape:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ImportPreview:
    adapter_name: str
    matched: bool
    confidence: float


class BaseImporter:
    name = "base"

    def can_handle(self, headers: list[str]) -> ImportPreview:
        ...

    def normalize(self, rows: list[dict[str, str]]) -> list[dict[str, str]]:
        ...
```

### `src/importers/internal_csv.py`

Handles the current tool-native schema.

Purpose:

- preserve current behavior
- act as the default importer when uploaded files already match the internal format

### `src/importers/team_external_csv.py`

Handles a specific external team's format.

Purpose:

- map upstream column names to internal names
- apply team-specific defaults and transformations

### `src/importers/factory.py`

Chooses the best importer for an uploaded file.

Purpose:

- inspect headers
- ask each importer if it can handle the file
- choose the importer with highest confidence
- fail clearly if no adapter matches

## Detection Strategy

The simplest strategy is header-based detection.

Examples:

- if headers contain `group`, `api_name`, `method`, `endpoint`, `expected_status`
  - use `internal_csv`
- if headers contain `service`, `api`, `http_method`, `url`
  - use `team_external_csv`

Recommended behavior:

- exact schema match gets high confidence
- partial signature match gets medium confidence
- no recognizable signature gets rejected with a helpful message

## Normalization Strategy

An adapter should output normalized rows using the internal column names.

Example:

External row:

```python
{
  "service": "Orders",
  "api": "List Orders",
  "http_method": "get",
  "url": "/orders",
  "expected_code": "200"
}
```

Normalized row:

```python
{
  "group": "Orders",
  "api_name": "List Orders",
  "method": "GET",
  "endpoint": "/orders",
  "expected_status": "200",
  "request_body": "",
  "headers": "",
  "auth_type": "",
  "auth_value": "",
  "auth_header_name": "",
  "timeout_seconds": "",
  "response_json_path": "",
  "expected_value": "",
  "match_type": "",
  "expected_contains": ""
}
```

After normalization, the existing parser can continue unchanged.

## Recommended Flow in Code

```python
uploaded_rows = read_csv_rows(file_bytes)
headers = list(uploaded_rows[0].keys())
importer = importer_factory.choose(headers)
normalized_rows = importer.normalize(uploaded_rows)
csv_text = write_internal_csv_text(normalized_rows)
test_cases = parse_csv_text(csv_text)
```

## Error Handling

The adapter layer should fail early and clearly.

Examples:

- `Unsupported CSV format. No importer matched the uploaded headers.`
- `Orders Team importer matched, but required external column "http_method" is missing.`
- `Could not map expected response code from column "expected".`

Recommended principle:

- adapter errors should explain the external-format problem
- parser errors should explain internal-schema validation problems

This separation makes debugging much easier.

## Why This Design Is Flexible

This design is flexible because:

- internal schema remains stable
- multiple upstream formats can coexist
- new external formats can be added by creating new adapters
- upstream changes are isolated to one module
- the rest of the tool remains untouched

## Phase 1 Recommendation

When the real external CSV format arrives, implement in this order:

1. preserve the current internal parser and schema
2. add `internal_csv` importer as baseline
3. add one external-team importer for the first real format
4. use a small factory to choose importer by headers
5. only add mapping UI later if code-based mapping becomes insufficient

## Future Enhancements

Possible upgrades later:

- YAML or JSON mapping config instead of hard-coded adapters
- import preview screen showing mapped columns before confirmation
- manual column mapping UI when auto-detection fails
- support for Excel input as well as CSV
- versioned adapters if upstream formats change often

## Practical Recommendation

Do not make the core parser accept every possible external format directly.

Instead:

- keep one clean internal contract
- adapt incoming files into that contract
- let the rest of the system stay simple

That approach gives the best balance of flexibility, maintainability, and low risk.
