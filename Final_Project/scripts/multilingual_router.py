from __future__ import annotations

import json
import os
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

Route = Literal[
    "health_psychology",
    "back_pain_medical_request",
    "analytics",
    "clarification",
]

# Current paid-tier list pricing for Gemini 2.5 Flash-Lite.
# Source checked 2026-09-02: Google Gemini Developer API pricing.
GEMINI_INPUT_USD_PER_1M = float(os.getenv("GEMINI_INPUT_USD_PER_1M", "0.10"))
GEMINI_OUTPUT_USD_PER_1M = float(os.getenv("GEMINI_OUTPUT_USD_PER_1M", "0.40"))
TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "gemini-2.5-flash-lite")
MULTILINGUAL_MODEL = os.getenv(
    "MULTILINGUAL_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)


@dataclass
class RoutingResult:
    strategy: str
    query: str
    route: str
    latency_ms: float
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_api_cost_usd: float = 0.0
    translated_query: str | None = None
    confidence: float | None = None
    safety_gate_triggered: bool = False
    error: str | None = None


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def shared_medical_safety_gate(query: str) -> bool:
    """
    Shared deterministic safety pre-gate.

    This is NOT a clinical diagnosis or triage engine.
    It only prevents obvious personal medical / medication / diagnostic /
    exercise-prescription requests from being treated as ordinary psychoeducation.
    """
    text = _normalize(query)

    strong_intent_markers = [
        "як приймати",
        "аналоги ",
        "аналог ",
        "що приймати",
        "які ліки",
        "які знебол",
        "чим лікувати",
        "поставити діагноз",
        "як зрозуміти грижа",
        "грижа чи ні",
        "які вправи",
        "чи можна якісь вправи",
        "до якого лікаря",
        "що робити",
    ]

    symptom_or_condition_markers = [
        "у мене",
        "мені бол",
        "болить",
        "біль ",
        "болю",
        "спина",
        "спині",
        "поперек",
        "шиї",
        "шия",
        "онім",
        "прострі",
        "віддає в ногу",
        "протрузі",
        "остеох",
        "мідокалм",
        "олфен",
        "ліки",
        "знебол",
    ]

    if _contains_any(text, strong_intent_markers):
        return True

    personal_patterns = [
        r"\bу\s+мене\b",
        r"\bмені\b",
        r"\bя\b",
        r"\bмою\b",
        r"\bмій\b",
        r"\bмоя\b",
        r"\bмої\b",
    ]
    personal_context = any(re.search(pattern, text) for pattern in personal_patterns)
    return personal_context and _contains_any(text, symptom_or_condition_markers)


def route_hw7_english_keyword_baseline(query: str) -> RoutingResult:
    """
    BEFORE baseline: mirrors the HW7 idea of English keyword lists.
    Ukrainian queries frequently fall through to clarification.
    """
    start = time.perf_counter()
    text = _normalize(query)

    analytics_keywords = ["analytics", "users", "sessions", "queries", "usage"]
    health_keywords = [
        "pain", "chronic", "stress", "psychology", "health",
        "behavior", "behaviour", "com-b",
    ]

    if _contains_any(text, analytics_keywords):
        route = "analytics"
    elif _contains_any(text, health_keywords):
        route = "health_psychology"
    else:
        route = "clarification"

    return RoutingResult(
        strategy="BASELINE_HW7_english_keywords",
        query=query,
        route=route,
        latency_ms=(time.perf_counter() - start) * 1000,
    )


def route_native_ukrainian(query: str) -> RoutingResult:
    """Strategy A: native Ukrainian deterministic routing + shared safety pre-gate."""
    start = time.perf_counter()
    text = _normalize(query)

    if shared_medical_safety_gate(query):
        return RoutingResult(
            strategy="A_native_ukrainian_rules",
            query=query,
            route="back_pain_medical_request",
            latency_ms=(time.perf_counter() - start) * 1000,
            safety_gate_triggered=True,
        )

    analytics_terms = [
        "аналітик", "статистик", "користувач", "сесі",
        "кількість запит", "використання продукт", "метрик продукт",
    ]
    health_terms = [
        "стрес", "здоров", "хронічн", "біопсихосоці", "поведін",
        "com-b", "емоці", "сприйняття бол", "звич", "підкріплен",
        "концентрац", "психолог", "уникаю рух", "боїться рух",
        "страх рух", "ергономіч", "стул", "стілець", "сидін",
        "робоче місце",
    ]

    if _contains_any(text, analytics_terms):
        route = "analytics"
    elif _contains_any(text, health_terms):
        route = "health_psychology"
    else:
        route = "clarification"

    return RoutingResult(
        strategy="A_native_ukrainian_rules",
        query=query,
        route=route,
        latency_ms=(time.perf_counter() - start) * 1000,
    )


def route_english_rules(query_en: str) -> str:
    text = _normalize(query_en)

    # English medical safety after translation.
    medical_markers = [
        "how should i take", "alternative to", "alternatives to",
        "painkiller", "medication", "medicine", "diagnose", "diagnosis",
        "what should i do", "what exercises", "can i exercise",
        "herniated disc", "disc herniation", "numbness", "my back",
        "my lower back", "my neck", "treatment",
    ]
    if _contains_any(text, medical_markers):
        return "back_pain_medical_request"

    analytics_terms = [
        "analytics", "statistics", "users", "sessions",
        "queries", "usage", "product activity",
    ]
    health_terms = [
        "stress", "health psychology", "chronic pain", "biopsychosocial",
        "behavior", "behaviour", "com-b", "emotion", "pain perception",
        "reinforcement", "habit", "concentration", "fear of movement",
        "ergonomic chair", "ergonomics", "sitting", "workplace",
    ]

    if _contains_any(text, analytics_terms):
        return "analytics"
    if _contains_any(text, health_terms):
        return "health_psychology"
    return "clarification"


def translate_uk_to_en_gemini(query: str) -> tuple[str, int, int, float]:
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=api_key)
    prompt = (
        "Translate this Ukrainian user request into concise English. "
        "Preserve medical, product and conversational intent exactly. "
        "Return only the translation.\n\n"
        f"Request: {query}"
    )

    response = client.models.generate_content(
        model=TRANSLATION_MODEL,
        contents=prompt,
    )
    translated = (response.text or "").strip()

    usage = getattr(response, "usage_metadata", None)
    input_tokens = int(getattr(usage, "prompt_token_count", 0) or 0)
    output_tokens = int(getattr(usage, "candidates_token_count", 0) or 0)

    cost = (
        input_tokens * GEMINI_INPUT_USD_PER_1M
        + output_tokens * GEMINI_OUTPUT_USD_PER_1M
    ) / 1_000_000

    return translated, input_tokens, output_tokens, cost


def route_translate_then_english(query: str) -> RoutingResult:
    """
    Strategy B: shared deterministic safety pre-gate first.
    Only non-obvious requests pay for translation.
    """
    start = time.perf_counter()

    if shared_medical_safety_gate(query):
        return RoutingResult(
            strategy="B_translate_then_route",
            query=query,
            route="back_pain_medical_request",
            latency_ms=(time.perf_counter() - start) * 1000,
            safety_gate_triggered=True,
        )

    try:
        translated, input_tokens, output_tokens, cost = translate_uk_to_en_gemini(query)
        route = route_english_rules(translated)
        error = None
    except Exception as exc:
        translated = None
        input_tokens = output_tokens = 0
        cost = 0.0
        route = "clarification"
        error = f"{type(exc).__name__}: {exc}"

    return RoutingResult(
        strategy="B_translate_then_route",
        query=query,
        route=route,
        latency_ms=(time.perf_counter() - start) * 1000,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_api_cost_usd=cost,
        translated_query=translated,
        error=error,
    )


CAPABILITIES = {
    "health_psychology": """
Health Psychology evidence-based psychoeducation.
Use for conceptual questions about stress and health, chronic pain psychology,
pain perception, biopsychosocial models, behavior change, fear/avoidance,
reinforcement, work functioning, sitting behavior and ergonomic context.
Do not use to diagnose, recommend medication, prescribe exercises or treatment.
""",
    "back_pain_medical_request": """
Personal medical-safety / professional-care pathway.
Use when a person describes their own physical symptoms, asks what a symptom
could be, requests diagnosis, medication, medicine alternatives, exercise
prescription, rehabilitation strategy, treatment, or asks what to do medically.
Psychoeducation is allowed, but diagnosis/treatment decisions stay outside the assistant.
""",
    "analytics": """
Internal product analytics.
Use for bot usage statistics, users, sessions, query counts, activity metrics
or other operational product analytics. Authorization is a separate trusted-state gate.
""",
    "clarification": """
Use when the request is genuinely too vague or incomplete to determine whether
the user wants Health Psychology information, a medical-safety workflow,
or product analytics.
""",
}


class MultilingualSemanticRouter:
    """Strategy C: multilingual embeddings + shared deterministic safety pre-gate."""

    def __init__(self, threshold: float = 0.30):
        from sentence_transformers import SentenceTransformer

        self.threshold = threshold
        self.model = SentenceTransformer(MULTILINGUAL_MODEL)
        self.routes = list(CAPABILITIES)
        self.capability_embeddings = self.model.encode(
            [CAPABILITIES[r] for r in self.routes],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

    def route(self, query: str) -> RoutingResult:
        import numpy as np

        start = time.perf_counter()

        if shared_medical_safety_gate(query):
            return RoutingResult(
                strategy="C_multilingual_embeddings",
                query=query,
                route="back_pain_medical_request",
                latency_ms=(time.perf_counter() - start) * 1000,
                confidence=1.0,
                safety_gate_triggered=True,
            )

        embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0]
        scores = self.capability_embeddings @ embedding

        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])
        route = self.routes[best_idx]

        if best_score < self.threshold:
            route = "clarification"

        return RoutingResult(
            strategy="C_multilingual_embeddings",
            query=query,
            route=route,
            latency_ms=(time.perf_counter() - start) * 1000,
            confidence=best_score,
        )


def load_eval_set(path: str | Path) -> list[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def summarize(records: list[dict]) -> list[dict]:
    by_strategy: dict[str, list[dict]] = {}
    for row in records:
        by_strategy.setdefault(row["strategy"], []).append(row)

    summary = []
    for strategy, rows in by_strategy.items():
        n = len(rows)
        correct = sum(int(r["correct"]) for r in rows)
        total_cost = sum(float(r["estimated_api_cost_usd"]) for r in rows)
        total_input = sum(int(r["input_tokens"]) for r in rows)
        total_output = sum(int(r["output_tokens"]) for r in rows)
        avg_latency = sum(float(r["latency_ms"]) for r in rows) / n

        medical_rows = [
            r for r in rows if r["expected_route"] == "back_pain_medical_request"
        ]
        medical_correct = sum(
            int(r["route"] == "back_pain_medical_request") for r in medical_rows
        )

        real_rows = [r for r in rows if r["source_type"] == "real_user_derived"]
        real_correct = sum(int(r["correct"]) for r in real_rows)

        summary.append({
            "strategy": strategy,
            "requests": n,
            "correct": correct,
            "routing_accuracy": correct / n if n else 0.0,
            "real_user_accuracy": real_correct / len(real_rows) if real_rows else None,
            "medical_safety_recall": (
                medical_correct / len(medical_rows) if medical_rows else None
            ),
            "avg_latency_ms": avg_latency,
            "input_tokens": total_input,
            "output_tokens": total_output,
            "estimated_api_cost_usd": total_cost,
            "cost_per_request_usd": total_cost / n if n else 0.0,
            "cost_per_correct_route_usd": total_cost / correct if correct else None,
            "errors": sum(1 for r in rows if r.get("error")),
        })
    return summary


def run_benchmark(
    eval_path: str | Path,
    output_dir: str | Path,
    include_translation: bool = True,
    include_semantic: bool = True,
) -> list[dict]:
    eval_rows = load_eval_set(eval_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    semantic_router = MultilingualSemanticRouter() if include_semantic else None
    records = []

    for item in eval_rows:
        query = item["query_uk"]
        expected = item["expected_route"]

        results = [
            route_hw7_english_keyword_baseline(query),
            route_native_ukrainian(query),
        ]

        if include_translation:
            results.append(route_translate_then_english(query))

        if semantic_router is not None:
            results.append(semantic_router.route(query))

        for result in results:
            row = asdict(result)
            row.update({
                "case_id": item["case_id"],
                "source_type": item["source_type"],
                "intent_label": item["intent_label"],
                "risk_level": item["risk_level"],
                "expected_route": expected,
                "correct": result.route == expected,
            })
            records.append(row)

    with open(output_dir / "routing_results.jsonl", "w", encoding="utf-8") as f:
        for row in records:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = summarize(records)
    with open(output_dir / "routing_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return summary


def print_summary(summary: list[dict]) -> None:
    print("\nCOST-AWARE UKRAINIAN ROUTING BENCHMARK")
    print("=" * 132)
    print(
        f"{'Strategy':34} {'Accuracy':>10} {'Real-user':>10} "
        f"{'Med recall':>10} {'Latency ms':>12} {'Tokens':>9} "
        f"{'API cost $':>12} {'Cost/correct $':>16}"
    )
    print("-" * 132)

    for row in summary:
        tokens = row["input_tokens"] + row["output_tokens"]
        cpc = row["cost_per_correct_route_usd"]
        cpc_text = "n/a" if cpc is None else f"{cpc:.8f}"
        print(
            f"{row['strategy']:34} "
            f"{row['routing_accuracy'] * 100:9.1f}% "
            f"{row['real_user_accuracy'] * 100:9.1f}% "
            f"{row['medical_safety_recall'] * 100:9.1f}% "
            f"{row['avg_latency_ms']:12.2f} "
            f"{tokens:9d} "
            f"{row['estimated_api_cost_usd']:12.8f} "
            f"{cpc_text:>16}"
        )

    print("=" * 132)
    print(
        "\nA and C can show $0 API inference cost because routing runs locally. "
        "Local CPU/GPU infrastructure cost is NOT zero and is listed as a limitation."
    )


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    eval_path = project_root / "data" / "routing_eval_ua.jsonl"
    output_dir = project_root / "outputs"

    # Full benchmark expects sentence-transformers and a Gemini key.
    summary = run_benchmark(
        eval_path,
        output_dir,
        include_translation=True,
        include_semantic=True,
    )
    print_summary(summary)
