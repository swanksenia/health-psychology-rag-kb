from __future__ import annotations

import json
from pathlib import Path

from multilingual_router import (
    load_eval_set,
    route_hw7_english_keyword_baseline,
    route_native_ukrainian,
    summarize,
)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    eval_rows = load_eval_set(project_root / "data" / "routing_eval_ua.jsonl")
    output_dir = project_root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for item in eval_rows:
        for result in [
            route_hw7_english_keyword_baseline(item["query_uk"]),
            route_native_ukrainian(item["query_uk"]),
        ]:
            row = result.__dict__.copy()
            row.update({
                "case_id": item["case_id"],
                "source_type": item["source_type"],
                "intent_label": item["intent_label"],
                "risk_level": item["risk_level"],
                "expected_route": item["expected_route"],
                "correct": result.route == item["expected_route"],
            })
            records.append(row)

    summary = summarize(records)

    (output_dir / "offline_routing_results.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "offline_routing_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
