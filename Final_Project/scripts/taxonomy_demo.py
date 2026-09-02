from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import List

import sys
from pathlib import Path

import time
import uuid
from datetime import datetime, timezone

from functools import lru_cache

REPO_ROOT = Path(__file__).resolve().parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.retrieval_improved import (
    CHUNKS_PATH,
    INDEX_PATH,
    MODEL_NAME,
    add_metadata,
    load_jsonl,
    semantic_search,
)

@dataclass
class TaxonomyResult:
    query: str
    primary_intent: str
    secondary_intent: List[str]
    risk_class: str
    requested_action: str
    domain: List[str]
    preferred_capability: str
    required_policy: List[str]
    allowed_capabilities: List[str]
    forbidden_capabilities: List[str]
    needs_clarification: bool
    label_rationale: str


# ---------------------------------------------------------
# Observability helpers
# ---------------------------------------------------------

TRACE_PATH = (
    Path(__file__).resolve().parents[1]
    / "outputs"
    / "conversation_traces.jsonl"
)

CLAUDE_INPUT_COST_PER_MILLION = 1.00
CLAUDE_OUTPUT_COST_PER_MILLION = 5.00

EXPERIMENT_ID = "taxonomy_v2_rag_demo_cached_v2"

LLM_PROVIDER = "anthropic"
LLM_MODEL = "claude-haiku-4-5-20251001"

TAXONOMY_VERSION = "v2"
PROMPT_VERSION = "grounded_synthesis_v1"

RETRIEVAL_TOP_K = 3


def estimate_claude_cost(
    input_tokens: int,
    output_tokens: int,
) -> float:
    return (
        input_tokens / 1_000_000 * CLAUDE_INPUT_COST_PER_MILLION
        + output_tokens / 1_000_000 * CLAUDE_OUTPUT_COST_PER_MILLION
    )


def log_trace(event: dict) -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with TRACE_PATH.open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(
                event,
                ensure_ascii=False,
            )
            + "\n"
        )

def classify_request(query: str) -> TaxonomyResult:
    """
    Deterministic taxonomy classifier for the demo.

    The classifier separates:
    - user intent and domain context;
    - preferred capability;
    - safety / policy requirements.

    Medical safety is treated as a policy overlay rather than
    as a competing topic category.
    """

    text = query.lower().strip()

    # ---------------------------------------------------------
    # 1. Lightweight Ukrainian lexical signals
    # ---------------------------------------------------------

    high_risk_terms = [
        "оніміння",
        "дзвін у вухах",
        "сильна втома",
    ]

    medication_terms = [
        "мідокалм",
        "олфен",
        "ліки",
        "таблетки",
        "дозування",
        "як приймати",
    ]

    exercise_terms = [
        "вправи",
        "пілатес",
        "розтяг",
        "закачувати",
        "спорт",
    ]

    ergonomics_terms = [
        "ергономіч",
        "стул",
        "стілець",
        "крісло",
    ]

    diagnosis_terms = [
        "грижа",
        "протрузі",
        "остеохондроз",
        "як зрозуміти",
    ]

    work_terms = [
        "робот",
        "прац",
        "сидін",
        "сиджу",
    ]

    pain_terms = [
        "біль",
        "болить",
        "спина",
    ]

    health_psychology_terms = [
    "health psychology",
    "психологія здоров'я",
    "психологія здоров’я",
    "стрес",
    "біопсихосоціаль",
    "емоці",
    ]

    analytics_terms = [
        "аналітик",
        "використання продукту",
    ]

    local_terms = [
        "місцев",
        "аналог",
    ]

    has_high_risk = any(term in text for term in high_risk_terms)
    has_medication = any(term in text for term in medication_terms)
    has_exercise = any(term in text for term in exercise_terms)
    has_ergonomics = any(term in text for term in ergonomics_terms)
    has_diagnosis = any(term in text for term in diagnosis_terms)
    has_work = any(term in text for term in work_terms)
    has_pain = any(term in text for term in pain_terms)
    has_health_psychology = any(term in text for term in health_psychology_terms)
    has_analytics = any(term in text for term in analytics_terms)
    has_local = any(term in text for term in local_terms)
    

    # ---------------------------------------------------------
    # 2. High-risk symptom context
    # ---------------------------------------------------------

    if has_high_risk:
        return TaxonomyResult(
            query=query,
            primary_intent="symptom_understanding_and_next_steps",
            secondary_intent=[
                "pain_management",
                "work_functioning" if has_work else "daily_functioning",
                "care_navigation",
            ],
            risk_class="high_risk",
            requested_action="understand_symptoms_and_what_to_do_next",
            domain=[
                "health_psychology",
                "chronic_pain",
                "work_context" if has_work else "daily_functioning",
            ],
            preferred_capability="health_psychology",
            required_policy=[
                "medical_safety",
            ],
            allowed_capabilities=[
                "health_psychology",
                "medical_safety_workflow",
            ],
            forbidden_capabilities=[
                "diagnosis",
                "medication_advice",
                "exercise_prescription",
                "generic_reassurance_only",
            ],
            needs_clarification=False,
            label_rationale=(
                "The request combines physical symptoms, functioning context "
                "and a medical-safety concern. The assistant should preserve "
                "the biopsychosocial context while activating the medical-safety policy."
            ),
        )
    # ---------------------------------------------------------
    # 3. Analytics
    # ---------------------------------------------------------

    if has_analytics:
        return TaxonomyResult(
            query=query,
            primary_intent="product_analytics",
            secondary_intent=[],
            risk_class="low",
            requested_action="view_product_analytics",
            domain=["analytics"],
            preferred_capability="analytics",
            required_policy=["authorization"],
            allowed_capabilities=["analytics"],
            forbidden_capabilities=[],
            needs_clarification=False,
            label_rationale=(
                "The user requests product analytics. "
                "Analytics access requires authorization."
            ),
        )
    
    # ---------------------------------------------------------
    # 4. Medication
    # ---------------------------------------------------------

    if has_medication:
        secondary = ["pain_management"]

        if has_exercise:
            secondary.append("exercise_question")
           
        if has_local:
            secondary.append("local_equivalent")

        return TaxonomyResult(
            query=query,
            primary_intent="medication_guidance",
            secondary_intent=secondary,
            risk_class="medical_safety",
            requested_action="individualized_treatment_guidance",
            domain=[
                "chronic_pain",
                "health_psychology",
            ],
            preferred_capability="medical_safety_workflow",
            required_policy=[
                "medical_safety",
                *(["location_consent"] if has_local else []),
            ],
            allowed_capabilities=[
                "medical_safety_workflow",
            ],
            forbidden_capabilities=[
                "medication_dosing_advice",
                "individualized_exercise_prescription",
                "diagnosis",
            ],
            needs_clarification=has_local,
            label_rationale=(
                "The user asks for individualized medication or treatment guidance. "
                "This crosses the assistant's medical-safety boundary."
            ),
        )

    # ---------------------------------------------------------
    # 5. Diagnostic intent
    # ---------------------------------------------------------

    if has_diagnosis:
        return TaxonomyResult(
            query=query,
            primary_intent="diagnostic_intent",
            secondary_intent=[
                "symptom_understanding",
                "care_navigation",
            ],
            risk_class="medical_safety",
            requested_action="understand_possible_diagnosis",
            domain=[
                "chronic_pain",
                "health_psychology",
            ],
            preferred_capability="health_psychology",
            required_policy=[
                "medical_safety",
            ],
            allowed_capabilities=[
                "health_psychology",
                "medical_safety_workflow",
                "clarification",
            ],
            forbidden_capabilities=[
                "diagnosis",
                "false_reassurance",
            ],
            needs_clarification=False,
            label_rationale=(
                "The user is trying to understand whether a diagnosis may explain "
                "their symptoms. The assistant can preserve the Health Psychology "
                "context, but the medical-safety policy prevents diagnostic conclusions."
            ),
        )

    # ---------------------------------------------------------
    # 6. Ergonomics
    # ---------------------------------------------------------

    if has_ergonomics:
        return TaxonomyResult(
            query=query,
            primary_intent="ergonomics_information",
            secondary_intent=[
                "work_context",
                "pain_prevention_or_management",
            ],
            risk_class="low",
            requested_action="ergonomics_information",
            domain=[
                "health_psychology",
                "work_context",
            ],
            preferred_capability="health_psychology",
            required_policy=[],
            allowed_capabilities=[
                "health_psychology",
                "clarification",
            ],
            forbidden_capabilities=[
                "unsupported_medical_claim",
            ],
            needs_clarification=True,
            label_rationale=(
                "The query is underspecified. The assistant can clarify the user's "
                "goal and answer from an evidence-based Health Psychology and "
                "work-behaviour perspective."
            ),
        )

    # ---------------------------------------------------------
    # 7. Exercise / rehabilitation
    # ---------------------------------------------------------

    if has_exercise and has_pain:
        return TaxonomyResult(
            query=query,
            primary_intent="exercise_and_rehabilitation_guidance",
            secondary_intent=[
                "pain_management",
                "self_management",
            ],
            risk_class="medical_safety",
            requested_action="exercise_or_rehabilitation_plan",
            domain=[
                "health_psychology",
                "chronic_pain",
            ],
            preferred_capability="health_psychology",
            required_policy=[
                "medical_safety",
            ],
            allowed_capabilities=[
                "health_psychology",
                "medical_safety_workflow",
            ],
            forbidden_capabilities=[
                "individualized_exercise_prescription",
                "treatment_prescription",
            ],
            needs_clarification=False,
            label_rationale=(
                "The request combines pain context with exercise or rehabilitation "
                "planning. The assistant should preserve the self-management and "
                "Health Psychology context while avoiding individualized treatment "
                "prescription."
            ),
        )

    # ---------------------------------------------------------
    # 8. General pain / Health Psychology context
    # ---------------------------------------------------------

    if has_pain:
        return TaxonomyResult(
            query=query,
            primary_intent="pain_and_functioning_support",
            secondary_intent=[
                "self_management",
                "work_functioning" if has_work else "daily_functioning",
            ],
            risk_class="moderate",
            requested_action="understand_and_manage_pain_context",
            domain=[
                "health_psychology",
                "chronic_pain",
            ],
            preferred_capability="health_psychology",
            required_policy=[],
            allowed_capabilities=[
                "health_psychology",
                "medical_safety_workflow",
            ],
            forbidden_capabilities=[
                "diagnosis",
                "treatment_prescription",
            ],
            needs_clarification=False,
            label_rationale=(
                "The request is primarily about pain and functioning. "
                "A Health Psychology response is appropriate while preserving "
                "the assistant's medical boundaries."
            ),
        )
    # ---------------------------------------------------------
    # 9. General Health Psychology knowledge
    # ---------------------------------------------------------

    if has_health_psychology:
        return TaxonomyResult(
            query=query,
            primary_intent="health_psychology_information",
            secondary_intent=[
                "psychoeducation",
            ],
            risk_class="low",
            requested_action="understand_health_psychology",
            domain=[
                "health_psychology",
            ],
            preferred_capability="health_psychology",
            required_policy=[],
            allowed_capabilities=[
                "health_psychology",
            ],
            forbidden_capabilities=[],
            needs_clarification=False,
            label_rationale=(
                "The user asks for general information about Health Psychology. "
                "The existing Health Psychology knowledge base is the appropriate "
                "source for this request."
            ),
        )
    # ---------------------------------------------------------
    # 10. Fallback
    # ---------------------------------------------------------

    return TaxonomyResult(
        query=query,
        primary_intent="unclear",
        secondary_intent=[],
        risk_class="low",
        requested_action="unknown",
        domain=[],
        preferred_capability="clarification",
        required_policy=[],
        allowed_capabilities=[
            "clarification",
        ],
        forbidden_capabilities=[],
        needs_clarification=True,
        label_rationale=(
            "The request does not contain enough information for a confident "
            "capability decision."
        ),
    )

@lru_cache(maxsize=1)
def get_retrieval_runtime():
    import faiss
    from sentence_transformers import SentenceTransformer

    chunks = load_jsonl(CHUNKS_PATH)
    add_metadata(chunks)

    index = faiss.read_index(str(INDEX_PATH))

    if index.ntotal != len(chunks):
        raise ValueError(
            "FAISS index size does not match the number of retrieval chunks."
        )

    model = SentenceTransformer(MODEL_NAME)

    return chunks, index, model


def retrieve_knowledge(
    query: str,
    top_k: int = 3,
) -> list[dict]:
    chunks, index, model = get_retrieval_runtime()

    return semantic_search(
        query=query,
        model=model,
        index=index,
        chunks=chunks,
        top_k=top_k,
    )


def generate_grounded_answer(
    query,
    retrieved,
    required_policy,
    conversation_id,
    turn_id,
):
    import os

    from anthropic import Anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        return (
            "Claude synthesis skipped: ANTHROPIC_API_KEY is not configured.",
            None,
        )

    client = Anthropic(api_key=api_key)

    evidence_text = "\n\n".join(
        [
            (
                f"Source {i + 1}\n"
                f"Chunk ID: {item.get('chunk_id')}\n"
                f"Source: {item.get('metadata', {}).get('source_file')}\n"
                f"Section: {item.get('metadata', {}).get('section')}\n"
                f"Evidence: "
                f"{item.get('text') or item.get('chunk_text') or item.get('content') or ''}"
            )
            for i, item in enumerate(retrieved)
        ]
    )

    if "medical_safety" in required_policy:
        task = """
Answer only with psychological, behavioural, emotional, cognitive,
or Health Psychology information explicitly supported by the retrieved evidence.

If the retrieved evidence is insufficient, say so explicitly.

Do not provide diagnosis.
Do not provide medication or treatment advice.
Do not provide exercise advice.
Do not recommend seeing a doctor or other professional.
Do not add referral or safety guidance.

Medical-safety and care-navigation guidance are handled separately
by the deterministic policy layer.

Keep the answer concise.
"""
    else:
        task = """
Answer the user's question directly using only the retrieved evidence.
Summarize and combine relevant statements into a concise, readable answer.
"""

    prompt = f"""
User question:

{query}

Retrieved evidence:

{evidence_text}

Task:

{task}

Rules:

- Use only information contained in the retrieved evidence.
- Do not use general knowledge.
- Do not add new facts, recommendations, causal claims, or interpretations.
- Preserve the meaning of the evidence.
- You may paraphrase, shorten, and combine evidence.
- Keep the answer concise and easy to read.
- Answer in Ukrainian.
- If the evidence is insufficient, say so explicitly.
"""

    model_name = LLM_MODEL
    started = time.perf_counter()

    try:
        response = client.messages.create(
            model=model_name,
            max_tokens=400,
            system=(
                "You are the synthesis layer of a Health Psychology RAG system. "
                "Your answer must stay grounded in retrieved evidence."
            ),
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        latency_ms = round(
            (time.perf_counter() - started) * 1000,
            2,
        )

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        total_tokens = input_tokens + output_tokens

        estimated_cost_usd = estimate_claude_cost(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        trace = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "conversation_id": conversation_id,
            "turn_id": turn_id,
            "experiment_id": EXPERIMENT_ID,
            "taxonomy_version": TAXONOMY_VERSION,
            "prompt_version": PROMPT_VERSION,
            "step_name": "claude_grounded_synthesis",
            "step_type": "llm",
            "provider": LLM_PROVIDER,
            "model": model_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "latency_ms": latency_ms,
            "estimated_cost_usd": round(
                estimated_cost_usd,
                8,
            ),
            "success": True,
            "error": None,
        }

        log_trace(trace)

        for block in response.content:
            if block.type == "text":
                return block.text, trace

        return "Claude returned no text response.", trace

    except Exception as error:
        latency_ms = round(
            (time.perf_counter() - started) * 1000,
            2,
        )

        trace = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "conversation_id": conversation_id,
        "turn_id": turn_id,
        "experiment_id": EXPERIMENT_ID,
        "taxonomy_version": TAXONOMY_VERSION,
        "prompt_version": PROMPT_VERSION,
        "step_name": "claude_grounded_synthesis",
        "step_type": "llm",
        "provider": LLM_PROVIDER,
        "model": model_name,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "latency_ms": latency_ms,
        "estimated_cost_usd": 0.0,
        "success": False,
        "error": f"{type(error).__name__}: {error}",
        }

        log_trace(trace)

        return (
            f"Claude synthesis is temporarily unavailable: "
            f"{type(error).__name__}. "
            "Relevant evidence was successfully retrieved from the knowledge base.",
            trace,
        )
        
def build_medical_safety_guidance(result):
    if "medical_safety" not in result.required_policy:
        return ""

    if (
        "chronic_pain" in result.domain
        or result.risk_class == "high_risk"
    ):
        return (
            "Через описані симптоми я не можу встановлювати діагноз "
            "або рекомендувати індивідуальне лікування. "
            "Для професійної оцінки можна звернутися до профільного "
            "фахівця IVR щодо хронічного болю або неврологічних симптомів. "
            "Консультація може бути онлайн або офлайн."
        )

    return (
        "Цей запит потребує професійної медичної оцінки. "
        "Я не можу встановлювати діагноз або рекомендувати "
        "індивідуальне лікування. "
        "За потреби можна звернутися до IVR онлайн або офлайн."
    )

def print_result(result: TaxonomyResult) -> None:
    print(
        json.dumps(
            asdict(result),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    conversation_id = str(uuid.uuid4())
    turn_id = 0

    print("\nHealth Psychology Routing Taxonomy Demo")
    print("Type a request in Ukrainian.")
    print("Press Ctrl+C to exit.\n")

    while True:
        try:
            query = input("User request: ").strip()

            if not query:
                continue

            turn_id += 1

            print()

            result = classify_request(query)

            log_trace(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "conversation_id": conversation_id,
                    "turn_id": turn_id,
                    "experiment_id": EXPERIMENT_ID,
                    "taxonomy_version": TAXONOMY_VERSION,
                    "step_name": "taxonomy_classification",
                    "step_type": "deterministic",
                    "provider": None,
                    "model": None,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "latency_ms": None,
                    "estimated_cost_usd": 0.0,
                    "success": True,
                    "error": None,
                }
            )

            print_result(result)

            if result.preferred_capability == "health_psychology":
                print("\nRetrieved Health Psychology evidence:\n")

                retrieval_started = time.perf_counter()

                retrieved = retrieve_knowledge(
                    query,
                    top_k=RETRIEVAL_TOP_K,
                )

                retrieval_latency_ms = round(
                    (time.perf_counter() - retrieval_started) * 1000,
                    2,
                )

                log_trace(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "conversation_id": conversation_id,
                        "turn_id": turn_id,
                        "experiment_id": EXPERIMENT_ID,
                        "taxonomy_version": TAXONOMY_VERSION,
                        "step_name": "faiss_retrieval",
                        "step_type": "retrieval",
                        "provider": "local",
                        "model": MODEL_NAME,
                        "retrieval_top_k": RETRIEVAL_TOP_K,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "latency_ms": retrieval_latency_ms,
                        "estimated_cost_usd": 0.0,
                        "success": True,
                        "error": None,
                    }
                )

                for i, item in enumerate(retrieved, start=1):
                    print(f"[{i}] score={item['score']:.4f}")
                    print("chunk_id:", item.get("chunk_id"))

                    metadata = item.get("metadata", {})
                    print("source:", metadata.get("source_file"))
                    print("section:", metadata.get("section"))

                    text = (
                        item.get("text")
                        or item.get("chunk_text")
                        or item.get("content")
                        or ""
                    )

                    print(text[:800])
                    print()

                answer, llm_trace = generate_grounded_answer(
                    query=query,
                    retrieved=retrieved,
                    required_policy=result.required_policy,
                    conversation_id=conversation_id,
                    turn_id=turn_id,
                )

                print("Assistant answer:\n")
                print(answer)

                if llm_trace:
                    print("\nLLM observability:\n")
                    print(
                        f"provider: {llm_trace['provider']}\n"
                        f"model: {llm_trace['model']}\n"
                        f"experiment_id: {llm_trace['experiment_id']}\n"
                        f"prompt_version: {llm_trace['prompt_version']}\n"
                        f"input_tokens: {llm_trace['input_tokens']}\n"
                        f"output_tokens: {llm_trace['output_tokens']}\n"
                        f"total_tokens: {llm_trace['total_tokens']}\n"
                        f"latency_ms: {llm_trace['latency_ms']}\n"
                        f"estimated_cost_usd: "
                        f"{llm_trace['estimated_cost_usd']:.6f}"
                    )

                safety_guidance = build_medical_safety_guidance(result)

                if safety_guidance:
                    print("\nSafety / care navigation:\n")
                    print(safety_guidance)

            elif result.preferred_capability == "medical_safety_workflow":
                print("\nSafety / care navigation:\n")
                print(build_medical_safety_guidance(result))

            elif result.preferred_capability == "clarification":
                print("\nAssistant answer:\n")
                print(
                    "Потрібно трохи більше контексту, щоб зрозуміти, "
                    "яка саме інформація або підтримка з Health Psychology вам потрібна."
                )

            elif result.preferred_capability == "analytics":
                print("\nAssistant answer:\n")
                print(
                    "Analytics capability selected. "
                    "Authorization is required before analytics data can be accessed."
                )

            print()

        except KeyboardInterrupt:
            print("\nBye.")
            break