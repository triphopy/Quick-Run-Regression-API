from __future__ import annotations

from src.models import TestCase


def get_groups(test_cases: list[TestCase]) -> list[str]:
    return ["All", *sorted({test_case.group for test_case in test_cases})]


def filter_test_cases(test_cases: list[TestCase], group_name: str) -> list[TestCase]:
    if group_name == "All":
        return test_cases
    return [test_case for test_case in test_cases if test_case.group == group_name]


def select_all_ids(test_cases: list[TestCase]) -> set[int]:
    return {test_case.id for test_case in test_cases}
