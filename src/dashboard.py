from __future__ import annotations

from src.models import GroupSummary, RunResult, RunSummary


def build_run_summary(
    results: list[RunResult],
    run_id: str,
    environment: str,
) -> RunSummary:
    total = len(results)
    passed = len([result for result in results if result.result == "PASSED"])
    failed = len([result for result in results if result.result == "FAILED"])
    error = len([result for result in results if result.result == "ERROR"])
    skipped = len([result for result in results if result.result == "SKIPPED"])
    pass_rate = (passed / total * 100) if total else 0.0
    avg_duration_seconds = (
        sum(result.duration_seconds for result in results) / total if total else 0.0
    )
    started_at = min((result.executed_at for result in results), default=None)
    finished_at = max((result.executed_at for result in results), default=None)

    return RunSummary(
        run_id=run_id,
        environment=environment,
        total=total,
        passed=passed,
        failed=failed,
        error=error,
        skipped=skipped,
        pass_rate=pass_rate,
        avg_duration_seconds=avg_duration_seconds,
        started_at=started_at,
        finished_at=finished_at,
    )


def build_group_summary(results: list[RunResult]) -> list[GroupSummary]:
    summaries: list[GroupSummary] = []
    for group in sorted({result.group for result in results}):
        group_results = [result for result in results if result.group == group]
        total = len(group_results)
        passed = len([result for result in group_results if result.result == "PASSED"])
        failed = len([result for result in group_results if result.result == "FAILED"])
        error = len([result for result in group_results if result.result == "ERROR"])
        skipped = len([result for result in group_results if result.result == "SKIPPED"])
        pass_rate = (passed / total * 100) if total else 0.0

        summaries.append(
            GroupSummary(
                group=group,
                total=total,
                passed=passed,
                failed=failed,
                error=error,
                skipped=skipped,
                pass_rate=pass_rate,
            )
        )

    return summaries


def worst_group_summary(group_summaries: list[GroupSummary]) -> GroupSummary | None:
    if not group_summaries:
        return None
    return sorted(
        group_summaries,
        key=lambda item: (item.pass_rate, -item.failed, item.group.lower()),
    )[0]
