# Quick Start

## Purpose

This quick start is for teammates who want to try the tool without reading the full design documents.

Use this guide to:

- start the app
- choose the right sample file
- run API checks
- export results
- clean old run files

## Start The App

Open PowerShell in the project folder:

```powershell
cd <your-project-folder>
```

Run Streamlit:

```powershell
python -m streamlit run app.py --server.port 8501
```

Then open the local URL shown by Streamlit in the browser.

If `python` is not available on PATH, use the full Python path installed on your machine instead.

## Which Sample To Use

### `Public API Smoke`

Use when:

- you want a quick sanity check
- you want mostly simple GET cases
- you want a lightweight first run

### `Public API Extended`

Use when:

- you want broader public API coverage
- you want more methods such as `POST`, `PUT`, `PATCH`, `DELETE`
- you want to exercise the runner more heavily

### `Team Realistic`

Use when:

- you want examples closer to real team usage
- you want auth, headers, request body, timeout, and response validation examples
- you want a working reference for advanced CSV authoring

### `Failure Examples`

Use when:

- you want to test failed results on purpose
- you want to verify Log and Dashboard error handling
- you want examples of validation failures

### `Demo Mix`

Use when:

- you want a balanced dashboard demo
- you want both passed and failed results in the same run
- you want a better presentation sample than fail-only data

## Templates

### `basic_template.csv`

Use when:

- you only need status-code checks
- you want the easiest starting point

### `advanced_template.csv`

Use when:

- you need auth
- you need headers or request body
- you need response validation with `match_type`

## Run A Test

1. Open the `Run Test` tab.
2. Upload your CSV, or open `Samples And Templates` and load a sample.
3. Set:
   - `Environment`
   - `Base URL` if your endpoints are relative paths
   - optional auth defaults such as token or API key
4. Filter by group or search by API name / endpoint if needed.
5. Select APIs using the checkboxes.
6. Click `Run APIs`.
7. After completion, open:
   - `Dashboard` for summary
   - `Log` for per-API details

## Export Results

Go to the `Dashboard` tab.

Open `Download Results`.

Available exports:

- `All Results CSV`
- `All Results XLSX`
- `Download Failed CSV`
- `Download Failed XLSX`

Use `Failed` exports when you only want issues for Excel or Jira follow-up.

## Robot Artifacts

Go to the `Dashboard` tab.

Open `Robot Artifacts`.

Available files:

- `log.html`
- `report.html`
- `output.xml`

Use these when you want Robot Framework's native test report files.

## Cleanup

Go to the `Dashboard` tab.

### Clean old run folders

Open `Cleanup Old Runs`.

Use when:

- `data/output` is getting too large
- you only want to keep the latest N runs

Steps:

1. Choose `Keep latest runs`
2. Click `Clean Old Runs`
3. Review the confirmation dialog
4. Confirm cleanup

The dialog shows:

- base folder path
- the exact run folders that will be removed

### Clean temp files

Open `Cleanup Temp Files`.

Use when:

- `data/temp` has too many leftover payload files
- you want to remove generated temp JSON files

Steps:

1. Click `Clean Temp Files`
2. Review the confirmation dialog
3. Confirm cleanup

The dialog shows:

- temp folder path
- the exact files that will be removed

## Helpful Notes

- Internal sample files and templates are available inside the app.
- The tool keeps one output folder per run under `data/output`.
- Temporary payload files are stored under `data/temp`.
- If a run uses real Robot execution, the run folder will contain `log.html`, `report.html`, `output.xml`, and `results.json`.
- If another team later provides a different file format, the current plan is to add an import adapter instead of changing the internal schema directly.

## Suggested First Try

If you want the easiest first demo:

1. Start the app
2. Load `Demo Mix`
3. Run all APIs
4. Review `Dashboard`
5. Click a group result count to open the filtered `Log`
6. Try `Download Failed CSV`
