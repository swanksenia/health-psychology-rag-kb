from __future__ import annotations

import json
from pathlib import Path

from taxonomy_demo import classify_request

EVALUATION_ID = "taxonomy_v2_eval_v1"
TAXONOMY_VERSION = "v2"
EVAL_SET_VERSION = "routing_eval_v2_13_cases"

def load_jsonl(path: Path) -> list[dict]:
    rows = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                rows.append(json.loads(line))

    return rows


def evaluate_case(item: dict) -> dict:
    result = classify_request(item["query_uk"])

    actual_capability = result.preferred_capability

    preferred_route_correct = (
        actual_capability == item["preferred_capability"]
    )

    allowed_route_correct = (
        actual_capability in item["allowed_capabilities"]
    )

    risk_class_correct = (
        result.risk_class == item["risk_class"]
    )

    required_policy_correct = (
        set(result.required_policy)
        == set(item["required_policy"])
    )

    clarification_correct = (
        result.needs_clarification
        == item["needs_clarification"]
    )

    unsafe_route = (
        actual_capability not in item["allowed_capabilities"]
    )

    medical_safety_expected = (
        "medical_safety" in item["required_policy"]
    )

    medical_safety_triggered = (
        "medical_safety" in result.required_policy
    )

    return {
        "case_id": item["case_id"],
        "source_type": item["source_type"],
        "query_uk": item["query_uk"],

        "expected_preferred_capability": item["preferred_capability"],
        "actual_preferred_capability": actual_capability,

        "preferred_route_correct": preferred_route_correct,
        "allowed_route_correct": allowed_route_correct,
        "risk_class_correct": risk_class_correct,
        "required_policy_correct": required_policy_correct,
        "clarification_correct": clarification_correct,
        "unsafe_route": unsafe_route,

        "medical_safety_expected": medical_safety_expected,
        "medical_safety_triggered": medical_safety_triggered,

        "expected_risk_class": item["risk_class"],
        "actual_risk_class": result.risk_class,

        "expected_required_policy": item["required_policy"],
        "actual_required_policy": result.required_policy,

        "expected_needs_clarification": item["needs_clarification"],
        "actual_needs_clarification": result.needs_clarification,

        "knowledge_coverage": item["knowledge_coverage"],
    }


def percentage(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0

    return round((numerator / denominator) * 100, 1)


def summarize(records: list[dict]) -> dict:
    total = len(records)

    preferred_correct = sum(
        row["preferred_route_correct"]
        for row in records
    )

    allowed_correct = sum(
        row["allowed_route_correct"]
        for row in records
    )

    risk_correct = sum(
        row["risk_class_correct"]
        for row in records
    )

    policy_correct = sum(
        row["required_policy_correct"]
        for row in records
    )

    clarification_correct = sum(
        row["clarification_correct"]
        for row in records
    )

    unsafe_count = sum(
        row["unsafe_route"]
        for row in records
    )

    medical_cases = [
        row
        for row in records
        if row["medical_safety_expected"]
    ]

    medical_triggered = sum(
        row["medical_safety_triggered"]
        for row in medical_cases
    )

    real_user_cases = [
        row
        for row in records
        if row["source_type"] == "real_user_derived"
    ]

    real_user_allowed_correct = sum(
        row["allowed_route_correct"]
        for row in real_user_cases
    )

    failures = [
        row["case_id"]
        for row in records
        if not (
            row["allowed_route_correct"]
            and row["required_policy_correct"]
            and row["clarification_correct"]
        )
    ]

    return {
        "cases": total,

        "preferred_route_accuracy_pct": percentage(
            preferred_correct,
            total,
        ),

        "allowed_route_accuracy_pct": percentage(
            allowed_correct,
            total,
        ),

        "risk_class_accuracy_pct": percentage(
            risk_correct,
            total,
        ),

        "required_policy_accuracy_pct": percentage(
            policy_correct,
            total,
        ),

        "medical_safety_recall_pct": percentage(
            medical_triggered,
            len(medical_cases),
        ),

        "unsafe_route_rate_pct": percentage(
            unsafe_count,
            total,
        ),

        "clarification_appropriateness_pct": percentage(
            clarification_correct,
            total,
        ),

        "real_user_allowed_route_accuracy_pct": percentage(
            real_user_allowed_correct,
            len(real_user_cases),
        ),

        "failed_case_ids": failures,
    }


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]

    eval_path = (
        project_root
        / "data"
        / "routing_eval_v2.jsonl"
    )

    output_dir = project_root / "outputs"
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    eval_rows = load_jsonl(eval_path)

    records = [
        evaluate_case(item)
        for item in eval_rows
    ]

    summary = summarize(records)

    summary = {
        "evaluation_id": EVALUATION_ID,
        "taxonomy_version": TAXONOMY_VERSION,
        "eval_set_version": EVAL_SET_VERSION,
        **summary,
    }

    (
        output_dir
        / "taxonomy_v2_results.json"
    ).write_text(
        json.dumps(
            records,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    (
        output_dir
        / "taxonomy_v2_summary.json"
    ).write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
        main()