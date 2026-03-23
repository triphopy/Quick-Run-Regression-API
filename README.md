# Quick-Run-Regression-API

Local-first tool for running API regression tests on demand with a simple web UI.

## Phase 1 Goal

This project is intended to help the team:

- upload a CSV list of APIs to test
- choose a subset of APIs or groups to run
- execute API checks locally
- review run summary and per-API logs in the UI
- export results to a neutral CSV/XLSX file for manual use in Excel and Jira Cloud workflows

Phase 1 is intentionally lightweight:

- local/offline usage
- Python-based implementation
- Streamlit UI
- Robot Framework for test execution
- no database yet
- no direct Jira Cloud integration yet
- no changes to the team's shared Excel template yet

## Current Status

The repository currently contains a Streamlit application in [app.py](/C:/Users/jonew/Downloads/Pu/Quick-Run-Regression-API/app.py) that supports the intended phase 1 flow:

- upload CSV
- select APIs by group
- run API checks through Robot Framework
- review dashboard and log panels
- export CSV/XLSX results

## Planned User Flow

1. Upload a CSV test list.
2. Validate required columns.
3. Select APIs to run.
4. Execute the selected tests through Robot Framework.
5. Parse results into a normalized result model.
6. Show summary and detailed logs in the UI.
7. Export results to CSV/XLSX.

## CSV Input

Minimum required columns:

- `group`
- `api_name`
- `method`
- `endpoint`
- `expected_status`

Optional columns for real execution:

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

Response validation:

- if `response_json_path` is provided, the runner parses the JSON response and compares the value at that path with `expected_value`
- `expected_value` can be plain text or a JSON literal such as `1`, `true`, `9.99`, or `"Gwenborough"`
- supported path style is dot notation, for example `address.city` or `products.0.title`
- `match_type` supports `equals`, `not_equals`, `contains`, `not_contains`, `exists`, `greater_than`, `less_than`, `greater_or_equal`, and `less_or_equal`
- `expected_contains` is used mainly with `contains`; if omitted, the runner falls back to `expected_value`

Example:

```csv
group,api_name,method,endpoint,expected_status
Authentication,Login,POST,/auth/login,200
Order,Get Order List,GET,/order/list,200
Payment,Refund,POST,/payment/refund,200
```

Templates and examples:

- [basic_template.csv](/C:/Users/jonew/Downloads/Pu/Quick-Run-Regression-API/assets/basic_template.csv) for simple status checks
- [advanced_template.csv](/C:/Users/jonew/Downloads/Pu/Quick-Run-Regression-API/assets/advanced_template.csv) for auth/body/header/validation cases
- [team_api_realistic.csv](/C:/Users/jonew/Downloads/Pu/Quick-Run-Regression-API/assets/team_api_realistic.csv) for working public-API examples
- [team_api_failure_examples.csv](/C:/Users/jonew/Downloads/Pu/Quick-Run-Regression-API/assets/team_api_failure_examples.csv) for intentional failed cases
- [team_api_demo_mix.csv](/C:/Users/jonew/Downloads/Pu/Quick-Run-Regression-API/assets/team_api_demo_mix.csv) for a balanced pass/fail demo
- [csv-cheatsheet.md](/C:/Users/jonew/Downloads/Pu/Quick-Run-Regression-API/docs/csv-cheatsheet.md) for quick guidance on fields and match types

Placeholder support:

- CSV fields such as `headers`, `request_body`, `auth_value`, and `endpoint` can use placeholders
- supported placeholders are `{{TOKEN}}`, `{{API_KEY}}`, `{{AUTH_VALUE}}`, `{{AUTH_HEADER_NAME}}`, and `{{BASE_URL}}`
- placeholders are resolved at runtime from the values entered in the UI

## Suggested Project Structure

```text
Quick-Run-Regression-API/
├─ app.py
├─ README.md
├─ requirements.txt
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

## Run Notes

This machine does not currently expose `python` or `streamlit` on PATH, so local run verification has not been completed in this session.

Once Python and Streamlit are available, the app can be started with:

```powershell
streamlit run app.py
```

If `streamlit` is not on PATH but Python is installed:

```powershell
python -m streamlit run app.py
```

## Design Reference

See [docs/phase1-design.md](/C:/Users/jonew/Downloads/Pu/Quick-Run-Regression-API/docs/phase1-design.md) for the current phase 1 scope, data flow, file flow, and input/output contracts.

For future support of external team CSV formats, see [import-adapter-design.md](/C:/Users/jonew/Downloads/Pu/Quick-Run-Regression-API/docs/import-adapter-design.md).

For day-to-day usage, see [quick-start.md](/C:/Users/jonew/Downloads/Pu/Quick-Run-Regression-API/docs/quick-start.md).
