from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src.models import RunResult


def read_results(results_file: Path) -> list[RunResult]:
    payload = json.loads(results_file.read_text(encoding="utf-8"))
    results: list[RunResult] = []
    for item in payload:
        results.append(
            RunResult(
                run_id=item["run_id"],
                test_case_id=item["test_case_id"],
                group=item["group"],
                api_name=item["api_name"],
                method=item["method"],
                endpoint=item["endpoint"],
                expected_status=item["expected_status"],
                actual_status=item["actual_status"],
                result=item["result"],
                duration_seconds=item["duration_seconds"],
                error_message=item["error_message"],
                executed_at=datetime.fromisoformat(item["executed_at"]),
            )
        )
    return results
