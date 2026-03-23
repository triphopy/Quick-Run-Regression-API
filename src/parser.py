from __future__ import annotations

import csv
import io
import json

from src.models import TestCase

REQUIRED_COLUMNS = [
    "group",
    "api_name",
    "method",
    "endpoint",
    "expected_status",
]
OPTIONAL_COLUMNS = [
    "request_body",
    "headers",
    "auth_type",
    "auth_value",
    "auth_header_name",
    "timeout_seconds",
    "response_json_path",
    "expected_value",
    "match_type",
    "expected_contains",
]

ALLOWED_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH"}
ALLOWED_MATCH_TYPES = {
    "",
    "equals",
    "not_equals",
    "contains",
    "not_contains",
    "exists",
    "greater_than",
    "less_than",
    "greater_or_equal",
    "less_or_equal",
}
ALLOWED_AUTH_TYPES = {"", "BEARER", "API KEY", "API_KEY", "HEADER", "NONE"}


def validate_headers(headers: list[str] | None) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in (headers or [])]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def parse_csv_text(csv_text: str) -> list[TestCase]:
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    validate_headers(reader.fieldnames)

    test_cases: list[TestCase] = []
    for index, row in enumerate(reader, start=1):
        method = (row.get("method") or "").strip().upper()
        endpoint = (row.get("endpoint") or "").strip()
        expected_status_raw = (row.get("expected_status") or "").strip()
        timeout_seconds_raw = (row.get("timeout_seconds") or "").strip()
        request_body = (row.get("request_body") or "").strip()
        headers = (row.get("headers") or "").strip()
        auth_type = (row.get("auth_type") or "").strip()
        auth_value = (row.get("auth_value") or "").strip()
        auth_header_name = (row.get("auth_header_name") or "").strip()
        response_json_path = (row.get("response_json_path") or "").strip()
        expected_value = (row.get("expected_value") or "").strip()
        match_type = (row.get("match_type") or "").strip().lower()
        expected_contains = (row.get("expected_contains") or "").strip()

        if method not in ALLOWED_METHODS:
            raise ValueError(f"Invalid method at row {index + 1}: {method or '<empty>'}")
        if not endpoint:
            raise ValueError(f"Missing endpoint at row {index + 1}")

        try:
            expected_status = int(expected_status_raw)
        except ValueError as exc:
            raise ValueError(
                f"Invalid expected_status at row {index + 1}: {expected_status_raw or '<empty>'}"
            ) from exc

        if timeout_seconds_raw:
            try:
                timeout_seconds = float(timeout_seconds_raw)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid timeout_seconds at row {index + 1}: {timeout_seconds_raw}"
                ) from exc
        else:
            timeout_seconds = 30.0

        if timeout_seconds <= 0:
            raise ValueError(f"Invalid timeout_seconds at row {index + 1}: must be greater than 0")

        if headers:
            try:
                parsed_headers = json.loads(headers)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in headers at row {index + 1}: {exc.msg}") from exc
            if not isinstance(parsed_headers, dict):
                raise ValueError(f"Invalid headers at row {index + 1}: must be a JSON object")

        if request_body:
            try:
                json.loads(request_body)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in request_body at row {index + 1}: {exc.msg}") from exc

        if auth_type.upper() not in ALLOWED_AUTH_TYPES:
            raise ValueError(
                f"Invalid auth_type at row {index + 1}: {auth_type}. "
                "Use None, Bearer, API Key, or Header."
            )

        if match_type not in ALLOWED_MATCH_TYPES:
            raise ValueError(
                f"Invalid match_type at row {index + 1}: {match_type or '<empty>'}. "
                "Use equals, not_equals, contains, not_contains, exists, greater_than, less_than, greater_or_equal, or less_or_equal."
            )

        if expected_contains and match_type not in {"contains", "not_contains", ""}:
            raise ValueError(
                f"Invalid expected_contains at row {index + 1}: it is only supported with contains or not_contains."
            )

        if response_json_path and not match_type:
            match_type = "equals"

        numeric_match_types = {"greater_than", "less_than", "greater_or_equal", "less_or_equal"}
        if match_type in numeric_match_types and expected_value == "":
            raise ValueError(
                f"Missing expected_value at row {index + 1}: match_type {match_type} requires a numeric expected_value."
            )

        if auth_type.upper() in {"API KEY", "API_KEY", "HEADER"} and auth_value and not auth_header_name:
            auth_header_name = "Authorization"

        test_cases.append(
            TestCase(
                id=index,
                group=(row.get("group") or "").strip() or "Unknown",
                api_name=(row.get("api_name") or "").strip(),
                method=method,
                endpoint=endpoint,
                expected_status=expected_status,
                request_body=request_body,
                headers=headers,
                auth_type=auth_type,
                auth_value=auth_value,
                auth_header_name=auth_header_name,
                timeout_seconds=timeout_seconds,
                response_json_path=response_json_path,
                expected_value=expected_value,
                match_type=match_type,
                expected_contains=expected_contains,
            )
        )
    return test_cases


def parse_csv_file(file_bytes: bytes, filename: str) -> list[TestCase]:
    try:
        csv_text = file_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Could not decode {filename} as UTF-8.") from exc
    return parse_csv_text(csv_text)
