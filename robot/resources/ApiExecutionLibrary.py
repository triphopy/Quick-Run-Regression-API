from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import requests
from robot.api.deco import keyword, library


@library(scope="GLOBAL")
class ApiExecutionLibrary:
    def __init__(self) -> None:
        self.results_file: Path | None = None
        self.base_url = ""
        self.payload_by_id: dict[int, dict] = {}
        self.default_auth_type = ""
        self.default_auth_value = ""
        self.default_auth_header_name = "Authorization"
        self.default_timeout_seconds = 30.0
        self.placeholders: dict[str, str] = {}

    def _build_placeholders(self) -> dict[str, str]:
        auth_type = self.default_auth_type.strip().upper()
        return {
            "TOKEN": self.default_auth_value if auth_type == "BEARER" else "",
            "API_KEY": self.default_auth_value if auth_type in {"API KEY", "API_KEY", "HEADER"} else "",
            "AUTH_VALUE": self.default_auth_value,
            "AUTH_HEADER_NAME": self.default_auth_header_name,
            "BASE_URL": self.base_url,
        }

    def _substitute_placeholders(self, raw_text: str) -> str:
        value = raw_text
        for key, replacement in self.placeholders.items():
            value = value.replace(f"{{{{{key}}}}}", replacement)
        return value

    def _parse_expected_value(self, raw_value: str):
        if raw_value == "":
            return ""
        try:
            return json.loads(raw_value)
        except json.JSONDecodeError:
            return raw_value

    def _extract_json_path(self, payload, path: str):
        current = payload
        for segment in path.split("."):
            if isinstance(current, list):
                try:
                    current = current[int(segment)]
                except (ValueError, IndexError) as exc:
                    raise KeyError(f"List index '{segment}' was not found") from exc
            elif isinstance(current, dict):
                if segment not in current:
                    raise KeyError(f"Key '{segment}' was not found")
                current = current[segment]
            else:
                raise KeyError(f"Cannot navigate through '{segment}' on a non-container value")
        return current

    def _validate_response_value(
        self,
        actual_value,
        path: str,
        match_type_raw: str,
        expected_value_raw: str,
        expected_contains_raw: str,
    ) -> tuple[bool, str]:
        match_type = (match_type_raw or "equals").strip().lower()

        if match_type in {"greater_than", "less_than", "greater_or_equal", "less_or_equal"}:
            expected_value = self._parse_expected_value(expected_value_raw)
            try:
                actual_number = float(actual_value)
                expected_number = float(expected_value)
            except (TypeError, ValueError):
                return (
                    False,
                    f"Match type '{match_type}' requires numeric values but got actual={actual_value!r} expected={expected_value!r}",
                )
            if match_type == "greater_than":
                if actual_number > expected_number:
                    return True, ""
                return False, f"Expected {path} > {expected_number!r} but got {actual_number!r}"
            if match_type == "less_than":
                if actual_number < expected_number:
                    return True, ""
                return False, f"Expected {path} < {expected_number!r} but got {actual_number!r}"
            if match_type == "greater_or_equal":
                if actual_number >= expected_number:
                    return True, ""
                return False, f"Expected {path} >= {expected_number!r} but got {actual_number!r}"
            if actual_number <= expected_number:
                return True, ""
            return False, f"Expected {path} <= {expected_number!r} but got {actual_number!r}"

        if match_type == "equals":
            expected_value = self._parse_expected_value(expected_value_raw)
            if actual_value == expected_value:
                return True, ""
            return False, f"Expected {path}={expected_value!r} but got {actual_value!r}"

        if match_type == "not_equals":
            expected_value = self._parse_expected_value(expected_value_raw)
            if actual_value != expected_value:
                return True, ""
            return False, f"Expected {path} to not equal {expected_value!r} but got {actual_value!r}"

        if match_type == "contains":
            contains_value = self._parse_expected_value(
                expected_contains_raw if expected_contains_raw != "" else expected_value_raw
            )
            if isinstance(actual_value, list):
                if contains_value in actual_value:
                    return True, ""
                return False, f"Expected {path} to contain {contains_value!r} but got {actual_value!r}"
            actual_text = str(actual_value)
            contains_text = str(contains_value)
            if contains_text in actual_text:
                return True, ""
            return False, f"Expected {path} to contain {contains_text!r} but got {actual_text!r}"

        if match_type == "not_contains":
            contains_value = self._parse_expected_value(
                expected_contains_raw if expected_contains_raw != "" else expected_value_raw
            )
            if isinstance(actual_value, list):
                if contains_value not in actual_value:
                    return True, ""
                return False, f"Expected {path} to not contain {contains_value!r} but got {actual_value!r}"
            actual_text = str(actual_value)
            contains_text = str(contains_value)
            if contains_text not in actual_text:
                return True, ""
            return False, f"Expected {path} to not contain {contains_text!r} but got {actual_text!r}"

        if match_type == "exists":
            if actual_value is None:
                return False, f"Expected {path} to exist but got None"
            if isinstance(actual_value, str) and actual_value == "":
                return False, f"Expected {path} to exist but got an empty string"
            return True, ""

        return False, (
            f"Unsupported match_type '{match_type_raw}'. "
            "Use equals, not_equals, contains, not_contains, exists, greater_than, less_than, greater_or_equal, or less_or_equal."
        )

    @keyword("Initialize Run Output")
    def initialize_run_output(
        self,
        results_file: str,
        payload_file: str,
        base_url: str = "",
        default_auth_type: str = "",
        default_auth_value: str = "",
        default_auth_header_name: str = "Authorization",
        default_timeout_seconds: str = "30",
    ) -> None:
        self.results_file = Path(results_file)
        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        self.results_file.write_text("[]", encoding="utf-8")
        self.base_url = base_url.rstrip("/")
        self.default_auth_type = default_auth_type.strip()
        self.default_auth_value = default_auth_value
        self.default_auth_header_name = default_auth_header_name or "Authorization"
        self.default_timeout_seconds = float(default_timeout_seconds or "30")
        self.placeholders = self._build_placeholders()
        payload = json.loads(Path(payload_file).read_text(encoding="utf-8"))
        self.payload_by_id = {
            int(item["id"]): item
            for item in payload.get("test_cases", [])
        }

    @keyword("Execute API Check By Id")
    def execute_api_check_by_id(
        self,
        run_id: str,
        test_case_id: str,
    ) -> None:
        if self.results_file is None:
            raise RuntimeError("Run output is not initialized.")
        payload = self.payload_by_id.get(int(test_case_id))
        if payload is None:
            raise RuntimeError(f"Test case id {test_case_id} was not found in payload.")

        group = payload["group"]
        api_name = payload["api_name"]
        method = payload["method"]
        endpoint = payload["endpoint"]
        expected_status = str(payload["expected_status"])
        request_body = self._substitute_placeholders(payload.get("request_body") or "")
        headers = self._substitute_placeholders(payload.get("headers") or "")
        auth_type = (payload.get("auth_type") or self.default_auth_type or "").strip().upper()
        auth_value = self._substitute_placeholders(payload.get("auth_value") or self.default_auth_value or "")
        auth_header_name = self._substitute_placeholders(payload.get("auth_header_name") or self.default_auth_header_name)
        timeout_seconds = float(payload.get("timeout_seconds") or self.default_timeout_seconds or 30)
        response_json_path = (payload.get("response_json_path") or "").strip()
        expected_value_raw = payload.get("expected_value") or ""
        match_type = payload.get("match_type") or ""
        expected_contains_raw = payload.get("expected_contains") or ""

        endpoint = self._substitute_placeholders(endpoint)
        url = endpoint if endpoint.startswith("http://") or endpoint.startswith("https://") else f"{self.base_url}{endpoint}"
        started = time.perf_counter()
        result = "FAILED"
        actual_status = None
        error_message = ""
        json_body = None
        request_headers = {}

        if headers:
            request_headers = json.loads(headers)
        if request_body:
            json_body = json.loads(request_body)
            request_headers.setdefault("Content-Type", "application/json")
        if auth_type == "BEARER" and auth_value:
            request_headers.setdefault("Authorization", f"Bearer {auth_value}")
        elif auth_type in {"API_KEY", "HEADER"} and auth_value:
            request_headers.setdefault(auth_header_name, auth_value)

        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                timeout=timeout_seconds,
                json=json_body,
                headers=request_headers,
            )
            actual_status = response.status_code
            if actual_status == int(expected_status):
                if response_json_path:
                    try:
                        response_payload = response.json()
                    except ValueError:
                        error_message = (
                            f"Response was not valid JSON for path validation '{response_json_path}'"
                        )
                    else:
                        try:
                            actual_value = self._extract_json_path(response_payload, response_json_path)
                        except KeyError as exc:
                            error_message = str(exc)
                        else:
                            is_valid, validation_error = self._validate_response_value(
                                actual_value,
                                response_json_path,
                                match_type,
                                expected_value_raw,
                                expected_contains_raw,
                            )
                            if is_valid:
                                result = "PASSED"
                            else:
                                error_message = validation_error
                else:
                    result = "PASSED"
            else:
                error_message = f"Expected {expected_status} but got {actual_status}"
        except Exception as exc:  # noqa: BLE001
            result = "ERROR"
            error_message = str(exc)

        duration_seconds = round(time.perf_counter() - started, 3)
        self._append_result(
            {
                "run_id": run_id,
                "test_case_id": int(test_case_id),
                "group": group,
                "api_name": api_name,
                "method": method.upper(),
                "endpoint": endpoint,
                "expected_status": int(expected_status),
                "actual_status": actual_status,
                "result": result,
                "duration_seconds": duration_seconds,
                "error_message": error_message,
                "executed_at": datetime.now().isoformat(),
            }
        )

        if result != "PASSED":
            raise AssertionError(error_message or "API check failed")

    def _append_result(self, record: dict) -> None:
        assert self.results_file is not None
        current = json.loads(self.results_file.read_text(encoding="utf-8"))
        current.append(record)
        self.results_file.write_text(json.dumps(current, indent=2), encoding="utf-8")
