from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TestCase:
    id: int
    group: str
    api_name: str
    method: str
    endpoint: str
    expected_status: int
    request_body: str = ""
    headers: str = ""
    auth_type: str = ""
    auth_value: str = ""
    auth_header_name: str = ""
    timeout_seconds: float = 30.0
    response_json_path: str = ""
    expected_value: str = ""
    match_type: str = ""
    expected_contains: str = ""


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class RunSummary:
    run_id: str
    environment: str
    total: int
    passed: int
    failed: int
    error: int
    skipped: int
    pass_rate: float
    avg_duration_seconds: float
    started_at: datetime | None
    finished_at: datetime | None


@dataclass(frozen=True)
class GroupSummary:
    group: str
    total: int
    passed: int
    failed: int
    error: int
    skipped: int
    pass_rate: float
