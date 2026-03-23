# Phase 1 Design

## Purpose

Phase 1 focuses on a practical internal tool for on-demand API regression runs.

The goal is not to build a full test platform yet. The goal is to make it easy to:

- load a list of API test cases
- choose which APIs to run
- execute tests locally
- inspect results in a web UI
- export results for downstream Excel and Jira Cloud workflows

## Scope

Included in phase 1:

- Streamlit UI
- CSV input
- local run execution
- Robot Framework integration
- summary dashboard
- per-API execution log
- CSV/XLSX export

Not included in phase 1:

- database
- direct Jira Cloud write-back
- shared Excel template automation
- scheduling
- multi-user support
- environment management beyond simple local configuration

## System Flow

1. User uploads a CSV file containing API test cases.
2. The parser validates required columns and row format.
3. The app builds an in-memory test case list.
4. The user filters by group and selects APIs to run.
5. The runner prepares an execution payload for Robot Framework.
6. Robot Framework executes the selected API tests.
7. Python reads Robot output files and normalizes the results.
8. The UI renders summary metrics and detailed logs.
9. The user exports results to CSV or XLSX.

## Data Flow

```text
CSV Upload
-> Parse and Validate
-> TestCase List
-> User Selection
-> Run Payload
-> Robot Execution
-> Robot Output Files
-> Result Parsing
-> Summary and Log Models
-> CSV/XLSX Export
```

## File Flow

### Input

- uploaded CSV file from the user
- optional saved copy in `data/input/`

### Temporary execution files

- generated selection payload in `data/temp/`
- example:

```text
data/temp/run_20260323_103000_selected.csv
```

### Robot output

- one output directory per run
- example:

```text
data/output/run_20260323_103000/output.xml
data/output/run_20260323_103000/log.html
data/output/run_20260323_103000/report.html
```

### Export output

- neutral result files for manual team workflows
- example:

```text
data/output/run_20260323_103000/result.csv
data/output/run_20260323_103000/result.xlsx
```

## Input Contract

Required CSV columns:

- `group`
- `api_name`
- `method`
- `endpoint`
- `expected_status`

Optional CSV columns:

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

Validation rules:

- all required headers must exist
- `method` must be an allowed HTTP method
- `endpoint` must not be empty
- `expected_status` must be an integer
- `timeout_seconds` must be numeric when provided
- if `response_json_path` is provided, the response must be valid JSON and the value at that path must match `expected_value`
- `match_type` may be `equals`, `not_equals`, `contains`, `not_contains`, `exists`, `greater_than`, `less_than`, `greater_or_equal`, or `less_or_equal` when provided
- invalid files should be rejected early in phase 1

Example:

```csv
group,api_name,method,endpoint,expected_status
Authentication,Login,POST,/auth/login,200
Order,Get Order List,GET,/order/list,200
Payment,Refund,POST,/payment/refund,200
```

Suggested onboarding assets:

- [basic_template.csv](../assets/basic_template.csv) for simple test-case authoring
- [advanced_template.csv](../assets/advanced_template.csv) for APIs that need auth, headers, body, or response assertions
- [team_api_realistic.csv](../assets/team_api_realistic.csv) as a working reference
- [team_api_failure_examples.csv](../assets/team_api_failure_examples.csv) as a debugging reference with intentional failures
- [team_api_demo_mix.csv](../assets/team_api_demo_mix.csv) as a mixed pass/fail demo reference
- [csv-cheatsheet.md](csv-cheatsheet.md) as a quick reference for the team

## Internal Models

### TestCase

```python
{
  "id": 1,
  "group": "Authentication",
  "api_name": "Login",
  "method": "POST",
  "endpoint": "/auth/login",
  "expected_status": 200
}
```

### RunPayload

```python
{
  "run_id": "run_20260323_103000",
  "environment": "UAT",
  "test_cases": [
    {
      "id": 1,
      "group": "Authentication",
      "api_name": "Login",
      "method": "POST",
      "endpoint": "/auth/login",
      "expected_status": 200
    }
  ]
}
```

### RunResult

```python
{
  "run_id": "run_20260323_103000",
  "test_case_id": 1,
  "group": "Authentication",
  "api_name": "Login",
  "method": "POST",
  "endpoint": "/auth/login",
  "expected_status": 200,
  "actual_status": 200,
  "result": "PASSED",
  "duration_seconds": 0.82,
  "error_message": "",
  "executed_at": "2026-03-23T10:30:12"
}
```

Allowed `result` values:

- `PASSED`
- `FAILED`
- `ERROR`
- `SKIPPED`

### RunSummary

```python
{
  "run_id": "run_20260323_103000",
  "environment": "UAT",
  "total": 20,
  "passed": 15,
  "failed": 5,
  "error": 0,
  "skipped": 0,
  "pass_rate": 75.0,
  "avg_duration_seconds": 1.82,
  "started_at": "2026-03-23T10:30:00",
  "finished_at": "2026-03-23T10:31:05"
}
```

### GroupSummary

```python
[
  {
    "group": "Authentication",
    "total": 4,
    "passed": 4,
    "failed": 0,
    "pass_rate": 100.0
  },
  {
    "group": "Payment",
    "total": 3,
    "passed": 2,
    "failed": 1,
    "pass_rate": 66.67
  }
]
```

## Export Contract

Phase 1 export should be a neutral format that does not modify the team's shared Excel template.

Recommended columns:

- `run_id`
- `run_date`
- `environment`
- `group`
- `api_name`
- `method`
- `endpoint`
- `expected_status`
- `actual_status`
- `result`
- `duration_seconds`
- `error_message`

Example:

```csv
run_id,run_date,environment,group,api_name,method,endpoint,expected_status,actual_status,result,duration_seconds,error_message
run_20260323_103000,2026-03-23 10:30:12,UAT,Authentication,Login,POST,/auth/login,200,200,PASSED,0.82,
run_20260323_103000,2026-03-23 10:30:14,UAT,Payment,Refund,POST,/payment/refund,200,500,FAILED,1.43,Internal Server Error
```

## Suggested Directory Layout

```text
Quick-Run-Regression-API/
├─ app.py
├─ docs/
│  └─ phase1-design.md
├─ data/
│  ├─ input/
│  ├─ output/
│  └─ temp/
├─ src/
│  ├─ config.py
│  ├─ models.py
│  ├─ parser.py
│  ├─ runner.py
│  ├─ result_reader.py
│  ├─ dashboard.py
│  └─ exporter.py
└─ robot/
   ├─ suites/
   ├─ resources/
   └─ generated/
```

## Implementation Priorities

1. Stabilize the input contract.
2. Split UI logic from execution logic.
3. Add Robot Framework execution path.
4. Add normalized result parsing.
5. Add export to CSV/XLSX.

## Next Step

The next design step is module interface definition, so each component has a clear responsibility before implementation expands beyond the current mock UI.

If external team CSV files arrive with a different schema, the recommended long-term approach is an adapter layer. See [import-adapter-design.md](import-adapter-design.md).

## Module Interfaces

Phase 1 should keep `app.py` focused on UI orchestration only. Business logic and execution logic should move into small modules with clear inputs and outputs.

### `src/models.py`

Purpose:

- define normalized data structures used across the project
- keep UI, parser, runner, and exporter aligned on the same contract

Suggested models:

- `TestCase`
- `RunContext`
- `RunPayload`
- `RunResult`
- `RunSummary`
- `GroupSummary`

Suggested shape:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestCase:
    id: int
    group: str
    api_name: str
    method: str
    endpoint: str
    expected_status: int


@dataclass
class RunContext:
    run_id: str
    environment: str
    started_at: datetime
    input_filename: str


@dataclass
class RunResult:
    run_id: str
    test_case_id: int
    group: str
    api_name: str
    method: str
    endpoint: str
    expected_status: int
    actual_status: int | None
    result: str
    duration_seconds: float
    error_message: str
    executed_at: datetime
```

### `src/parser.py`

Purpose:

- read uploaded CSV content
- validate headers and row values
- convert raw rows into `TestCase` objects

Suggested functions:

```python
from src.models import TestCase


def parse_csv_text(csv_text: str) -> list[TestCase]:
    ...


def parse_csv_file(file_bytes: bytes, filename: str) -> list[TestCase]:
    ...


def validate_headers(headers: list[str]) -> None:
    ...
```

Behavior notes:

- reject files with missing required columns
- reject invalid methods or non-numeric `expected_status`
- raise a descriptive exception that the UI can show directly

### `src/selector.py`

Purpose:

- keep selection and filtering logic separate from Streamlit widgets

Suggested functions:

```python
from src.models import TestCase


def get_groups(test_cases: list[TestCase]) -> list[str]:
    ...


def filter_test_cases(test_cases: list[TestCase], group_name: str) -> list[TestCase]:
    ...


def select_all_ids(test_cases: list[TestCase]) -> set[int]:
    ...
```

Behavior notes:

- return deterministic group ordering
- keep this module free of UI-specific code

### `src/config.py`

Purpose:

- centralize project paths and default runtime settings
- avoid scattered string literals in UI and runner code

Suggested functions:

```python
from pathlib import Path


def project_root() -> Path:
    ...


def data_dir() -> Path:
    ...


def output_dir(run_id: str) -> Path:
    ...


def temp_dir() -> Path:
    ...
```

Suggested constants:

- `DEFAULT_ENVIRONMENT = "UAT"`
- `REQUIRED_COLUMNS = [...]`
- `ALLOWED_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH"}`

### `src/runner.py`

Purpose:

- prepare execution input for Robot Framework
- invoke Robot Framework
- return file locations and run metadata

Suggested functions:

```python
from pathlib import Path
from src.models import RunContext, TestCase


def create_run_context(environment: str, input_filename: str) -> RunContext:
    ...


def build_run_payload_file(run_context: RunContext, test_cases: list[TestCase]) -> Path:
    ...


def execute_robot(run_context: RunContext, payload_file: Path) -> Path:
    ...
```

Behavior notes:

- create one output folder per run
- return the run output directory path
- keep shell command construction inside this module only

Phase 1 shortcut:

- before real Robot integration is ready, this module may expose a mock execution path that generates fake results for UI development

### `src/result_reader.py`

Purpose:

- read Robot output artifacts
- normalize raw output into `RunResult` objects

Suggested functions:

```python
from pathlib import Path
from src.models import RunContext, RunResult


def read_results(run_context: RunContext, robot_output_dir: Path) -> list[RunResult]:
    ...
```

Possible implementation paths:

- parse `output.xml`
- or parse a generated JSON/CSV artifact if that is simpler in phase 1

Behavior notes:

- this module should be the only place that understands Robot output format details

### `src/dashboard.py`

Purpose:

- compute dashboard-friendly summary data from normalized results

Suggested functions:

```python
from src.models import GroupSummary, RunResult, RunSummary


def build_run_summary(results: list[RunResult], run_id: str, environment: str) -> RunSummary:
    ...


def build_group_summary(results: list[RunResult]) -> list[GroupSummary]:
    ...
```

Behavior notes:

- avoid embedding summary formulas directly inside Streamlit pages

### `src/exporter.py`

Purpose:

- export normalized results into neutral files for manual Excel and Jira workflows

Suggested functions:

```python
from pathlib import Path
from src.models import RunResult


def export_results_csv(results: list[RunResult], output_file: Path) -> Path:
    ...


def export_results_xlsx(results: list[RunResult], output_file: Path) -> Path:
    ...
```

Behavior notes:

- exported columns must follow the project contract
- do not couple the exporter to the team's shared Excel template in phase 1

### `app.py`

Purpose:

- collect user input
- call parser, selector, runner, result reader, dashboard, and exporter
- render UI state only

Should do:

- upload file handling
- tab and session state management
- trigger run flow
- render summary and logs
- offer export buttons

Should avoid:

- CSV parsing logic
- execution command construction
- result normalization logic
- export formatting logic

## Recommended Execution Sequence

When the codebase is refactored from the current mock state, the main flow should look like this:

```python
test_cases = parser.parse_csv_file(...)
filtered_cases = selector.filter_test_cases(test_cases, group_name)
run_context = runner.create_run_context(environment="UAT", input_filename="apis.csv")
payload_file = runner.build_run_payload_file(run_context, selected_cases)
robot_output_dir = runner.execute_robot(run_context, payload_file)
results = result_reader.read_results(run_context, robot_output_dir)
summary = dashboard.build_run_summary(results, run_context.run_id, run_context.environment)
group_summary = dashboard.build_group_summary(results)
exporter.export_results_csv(results, ...)
```

## Phase 1 Refactor Order

To keep momentum and avoid a risky big-bang rewrite, the implementation should move in this order:

1. Add `src/models.py`
2. Move CSV parsing into `src/parser.py`
3. Move summary calculations into `src/dashboard.py`
4. Add `src/exporter.py`
5. Introduce `src/runner.py` with a mock execution path first
6. Replace the mock execution path with real Robot Framework integration
