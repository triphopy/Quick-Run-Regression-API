from __future__ import annotations

import csv
from pathlib import Path

from src.models import RunResult

EXPORT_COLUMNS = [
    "run_id",
    "run_date",
    "environment",
    "group",
    "api_name",
    "method",
    "endpoint",
    "expected_status",
    "actual_status",
    "result",
    "duration_seconds",
    "error_message",
]


def _result_row(
    result: RunResult,
    *,
    environment: str = "",
) -> dict[str, str | int | float | None]:
    return {
        "run_id": result.run_id,
        "run_date": result.executed_at.strftime("%Y-%m-%d %H:%M:%S"),
        "environment": environment,
        "group": result.group,
        "api_name": result.api_name,
        "method": result.method,
        "endpoint": result.endpoint,
        "expected_status": result.expected_status,
        "actual_status": result.actual_status,
        "result": result.result,
        "duration_seconds": result.duration_seconds,
        "error_message": result.error_message,
    }


def export_results_csv(
    results: list[RunResult],
    output_file: Path,
    *,
    environment: str = "",
) -> Path:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8-sig", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=EXPORT_COLUMNS)
        writer.writeheader()
        for result in results:
            writer.writerow(_result_row(result, environment=environment))
    return output_file


def export_results_xlsx(
    results: list[RunResult],
    output_file: Path,
    *,
    environment: str = "",
) -> Path:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        from openpyxl import Workbook
    except ImportError as exc:
        raise RuntimeError("openpyxl is required for XLSX export.") from exc

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Results"
    worksheet.append(EXPORT_COLUMNS)
    for result in results:
        row = _result_row(result, environment=environment)
        worksheet.append([row[column] for column in EXPORT_COLUMNS])
    workbook.save(output_file)
    return output_file
