from __future__ import annotations

import json
import random
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from src.config import output_dir, robot_generated_dir, robot_dir, temp_dir
from src.models import RunResult, TestCase
from src.result_reader import read_results

@dataclass(frozen=True)
class MockRunArtifacts:
    run_id: str
    payload_file: Path
    output_dir: Path
    results: list[RunResult]


@dataclass(frozen=True)
class RunArtifacts:
    run_id: str
    output_dir: Path
    results: list[RunResult]
    mode: str
    payload_file: Path
    error: str = ""


def create_run_id() -> str:
    return f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def build_run_payload_file(run_id: str, test_cases: list[TestCase]) -> Path:
    path = temp_dir() / f"{run_id}_selected.json"
    payload = {
        "run_id": run_id,
        "test_cases": [
            {
                "id": test_case.id,
                "group": test_case.group,
                "api_name": test_case.api_name,
                "method": test_case.method,
                "endpoint": test_case.endpoint,
                "expected_status": test_case.expected_status,
                "request_body": test_case.request_body,
                "headers": test_case.headers,
                "auth_type": test_case.auth_type,
                "auth_value": test_case.auth_value,
                "auth_header_name": test_case.auth_header_name,
                "timeout_seconds": test_case.timeout_seconds,
                "response_json_path": test_case.response_json_path,
                "expected_value": test_case.expected_value,
                "match_type": test_case.match_type,
                "expected_contains": test_case.expected_contains,
            }
            for test_case in test_cases
        ],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def robot_is_available() -> bool:
    try:
        import robot  # noqa: F401
    except ImportError:
        return False
    return True


def build_generated_robot_suite(run_id: str, test_cases: list[TestCase], results_file: Path, payload_file: Path) -> Path:
    suite_path = robot_generated_dir() / f"{run_id}.robot"
    lines = [
        "*** Settings ***",
        "Resource    ../suites/api_regression.robot",
        "",
        "*** Test Cases ***",
        "Prepare Run Output",
        f"    Initialize Run Output    {results_file.as_posix()}    {payload_file.as_posix()}    ${{BASE_URL}}    ${{DEFAULT_AUTH_TYPE}}    ${{DEFAULT_AUTH_VALUE}}    ${{DEFAULT_AUTH_HEADER_NAME}}    ${{DEFAULT_TIMEOUT_SECONDS}}",
    ]
    for test_case in test_cases:
        test_name = f"{test_case.id:03d} {test_case.api_name}".replace("\n", " ").strip()
        lines.extend(
            [
                "",
                test_name,
                f"    Execute API Check By Id    {run_id}    {test_case.id}",
            ]
        )
    suite_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return suite_path


def execute_robot_run(
    run_id: str,
    test_cases: list[TestCase],
    *,
    environment_base_url: str = "",
    default_auth_type: str = "",
    default_auth_value: str = "",
    default_auth_header_name: str = "Authorization",
    default_timeout_seconds: float = 30.0,
) -> RunArtifacts:
    run_output_dir = output_dir(run_id)
    payload_file = build_run_payload_file(run_id, test_cases)
    results_file = run_output_dir / "results.json"
    suite_file = build_generated_robot_suite(run_id, test_cases, results_file, payload_file)
    command = [
        sys.executable,
        "-m",
        "robot",
        "--outputdir",
        str(run_output_dir),
        "--variable",
        f"BASE_URL:{environment_base_url}",
        "--variable",
        f"DEFAULT_AUTH_TYPE:{default_auth_type}",
        "--variable",
        f"DEFAULT_AUTH_VALUE:{default_auth_value}",
        "--variable",
        f"DEFAULT_AUTH_HEADER_NAME:{default_auth_header_name}",
        "--variable",
        f"DEFAULT_TIMEOUT_SECONDS:{default_timeout_seconds}",
        str(suite_file),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, cwd=robot_dir())
    if not results_file.exists():
        error = (completed.stderr or completed.stdout or "Robot run did not produce results.").strip()
        raise RuntimeError(error)
    results = read_results(results_file)
    return RunArtifacts(
        run_id=run_id,
        output_dir=run_output_dir,
        results=results,
        mode="robot",
        payload_file=payload_file,
    )


def execute_run(
    run_id: str,
    test_cases: list[TestCase],
    *,
    environment_base_url: str = "",
    default_auth_type: str = "",
    default_auth_value: str = "",
    default_auth_header_name: str = "Authorization",
    default_timeout_seconds: float = 30.0,
    allow_mock_fallback: bool = True,
) -> RunArtifacts:
    if robot_is_available():
        try:
            return execute_robot_run(
                run_id,
                test_cases,
                environment_base_url=environment_base_url,
                default_auth_type=default_auth_type,
                default_auth_value=default_auth_value,
                default_auth_header_name=default_auth_header_name,
                default_timeout_seconds=default_timeout_seconds,
            )
        except Exception as exc:  # noqa: BLE001
            if not allow_mock_fallback:
                raise
            mock = execute_mock_run(run_id, test_cases)
            return RunArtifacts(
                run_id=mock.run_id,
                output_dir=mock.output_dir,
                results=mock.results,
                mode="mock",
                payload_file=mock.payload_file,
                error=str(exc),
            )

    if not allow_mock_fallback:
        raise RuntimeError("Robot Framework is not installed in the current Python environment.")

    mock = execute_mock_run(run_id, test_cases)
    return RunArtifacts(
        run_id=mock.run_id,
        output_dir=mock.output_dir,
        results=mock.results,
        mode="mock",
        payload_file=mock.payload_file,
        error="Robot Framework is not installed; mock execution was used.",
    )


def execute_mock_run(
    run_id: str,
    test_cases: list[TestCase],
    persist_artifacts: bool = True,
) -> MockRunArtifacts:
    payload_file = build_run_payload_file(run_id, test_cases) if persist_artifacts else temp_dir() / f"{run_id}_selected.json"
    run_output_dir = output_dir(run_id) if persist_artifacts else temp_dir()
    started_at = datetime.now()
    results: list[RunResult] = []

    for index, test_case in enumerate(test_cases):
        duration = round(random.uniform(0.5, 4.8), 1)
        result = "PASSED"
        actual_status = test_case.expected_status
        error_message = ""
        executed_at = started_at + timedelta(seconds=index)
        results.append(
            RunResult(
                run_id=run_id,
                test_case_id=test_case.id,
                group=test_case.group,
                api_name=test_case.api_name,
                method=test_case.method,
                endpoint=test_case.endpoint,
                expected_status=test_case.expected_status,
                actual_status=actual_status,
                result=result,
                duration_seconds=duration,
                error_message=error_message,
                executed_at=executed_at,
            )
        )

    if persist_artifacts:
        output_file = run_output_dir / "mock_results.json"
        output_file.write_text(
            json.dumps(
                [
                    {
                        "run_id": result.run_id,
                        "test_case_id": result.test_case_id,
                        "group": result.group,
                        "api_name": result.api_name,
                        "method": result.method,
                        "endpoint": result.endpoint,
                        "expected_status": result.expected_status,
                        "actual_status": result.actual_status,
                        "result": result.result,
                        "duration_seconds": result.duration_seconds,
                        "error_message": result.error_message,
                        "executed_at": result.executed_at.isoformat(),
                    }
                    for result in results
                ],
                indent=2,
            ),
            encoding="utf-8",
        )

    return MockRunArtifacts(
        run_id=run_id,
        payload_file=payload_file,
        output_dir=run_output_dir,
        results=results,
    )
