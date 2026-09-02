from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

def load_jsonl(path: Path) -> list[dict]:
    rows = []

    if not path.exists():
        return rows

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                rows.append(json.loads(line))

    return rows


def safe_number(value, default=0):
    if value is None:
        return default

    return value


def summarize_llm(events: list[dict]) -> list[dict]:
    groups = defaultdict(
        lambda: {
            "calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "total_latency_ms": 0.0,
            "total_cost_usd": 0.0,
        }
    )

    for event in events:
        if event.get("step_type") != "llm":
            continue

        key = (
            event.get("experiment_id"),
            event.get("provider"),
            event.get("model"),
            event.get("prompt_version"),
        )

        group = groups[key]

        group["calls"] += 1

        if event.get("success"):
            group["successful_calls"] += 1
        else:
            group["failed_calls"] += 1

        group["input_tokens"] += safe_number(
            event.get("input_tokens")
        )

        group["output_tokens"] += safe_number(
            event.get("output_tokens")
        )

        group["total_tokens"] += safe_number(
            event.get("total_tokens")
        )

        group["total_latency_ms"] += safe_number(
            event.get("latency_ms"),
            0.0,
        )

        group["total_cost_usd"] += safe_number(
            event.get("estimated_cost_usd"),
            0.0,
        )

    summaries = []

    for key, values in groups.items():
        (
            experiment_id,
            provider,
            model,
            prompt_version,
        ) = key

        calls = values["calls"]

        summaries.append(
            {
                "experiment_id": experiment_id,
                "provider": provider,
                "model": model,
                "prompt_version": prompt_version,
                "calls": calls,
                "successful_calls": values["successful_calls"],
                "failed_calls": values["failed_calls"],
                "input_tokens": values["input_tokens"],
                "output_tokens": values["output_tokens"],
                "total_tokens": values["total_tokens"],
                "total_cost_usd": round(
                    values["total_cost_usd"],
                    8,
                ),
                "average_cost_per_call_usd": round(
                    values["total_cost_usd"] / calls,
                    8,
                )
                if calls
                else 0.0,
                "average_latency_ms": round(
                    values["total_latency_ms"] / calls,
                    2,
                )
                if calls
                else 0.0,
            }
        )

    return sorted(
        summaries,
        key=lambda row: (
            str(row["provider"]),
            str(row["model"]),
        ),
    )


def summarize_steps(events: list[dict]) -> list[dict]:
    groups = defaultdict(
        lambda: {
            "calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_latency_ms": 0.0,
            "total_cost_usd": 0.0,
        }
    )

    for event in events:
        key = event.get("step_name", "unknown")
        group = groups[key]

        group["calls"] += 1

        if event.get("success"):
            group["successful_calls"] += 1
        else:
            group["failed_calls"] += 1

        group["total_latency_ms"] += safe_number(
            event.get("latency_ms"),
            0.0,
        )

        group["total_cost_usd"] += safe_number(
            event.get("estimated_cost_usd"),
            0.0,
        )

    summaries = []

    for step_name, values in groups.items():
        calls = values["calls"]

        summaries.append(
            {
                "step_name": step_name,
                "calls": calls,
                "successful_calls": values["successful_calls"],
                "failed_calls": values["failed_calls"],
                "average_latency_ms": round(
                    values["total_latency_ms"] / calls,
                    2,
                )
                if calls
                else 0.0,
                "total_cost_usd": round(
                    values["total_cost_usd"],
                    8,
                ),
            }
        )

    return sorted(
        summaries,
        key=lambda row: row["step_name"],
    )


def summarize_conversations(events: list[dict]) -> dict:
    conversation_ids = {
        event.get("conversation_id")
        for event in events
        if event.get("conversation_id")
    }

    turn_keys = {
        (
            event.get("conversation_id"),
            event.get("turn_id"),
        )
        for event in events
        if event.get("conversation_id")
        and event.get("turn_id") is not None
    }

    llm_events = [
        event
        for event in events
        if event.get("step_type") == "llm"
    ]

    total_input_tokens = sum(
        safe_number(event.get("input_tokens"))
        for event in llm_events
    )

    total_output_tokens = sum(
        safe_number(event.get("output_tokens"))
        for event in llm_events
    )

    total_tokens = sum(
        safe_number(event.get("total_tokens"))
        for event in llm_events
    )

    total_cost = sum(
        safe_number(event.get("estimated_cost_usd"), 0.0)
        for event in llm_events
    )

    return {
        "conversations": len(conversation_ids),
        "turns": len(turn_keys),
        "llm_calls": len(llm_events),
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": total_tokens,
        "estimated_ai_cost_usd": round(
            total_cost,
            8,
        ),
        "average_ai_cost_per_turn_usd": round(
            total_cost / len(turn_keys),
            8,
        )
        if turn_keys
        else 0.0,
        "average_llm_calls_per_turn": round(
            len(llm_events) / len(turn_keys),
            3,
        )
        if turn_keys
        else 0.0,
    }


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]

    trace_path = (
        project_root
        / "outputs"
        / "conversation_traces.jsonl"
    )

    output_path = (
        project_root
        / "outputs"
        / "observability_summary.json"
    )

    events = load_jsonl(trace_path)

    if not events:
        print(
            "No trace events found in "
            "outputs/conversation_traces.jsonl"
        )
        return

    summary = {
        "runtime_summary": summarize_conversations(events),
        "llm_by_vendor_model": summarize_llm(events),
        "steps": summarize_steps(events),
    }

    output_path.write_text(
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