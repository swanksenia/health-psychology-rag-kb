"""
Health Psychology & Chronic Back Pain Assistant
Homework 6 — Agentic Workflow

Controlled workflow:
user goal → route/plan → action → observation
→ state update → next step → final answer
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict

import faiss
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types
from google.genai.errors import ClientError


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.retrieval_improved import (
    CHUNKS_PATH,
    INDEX_PATH,
    MODEL_NAME,
    TOP_K,
    load_jsonl,
    add_metadata,
    semantic_search,
)


# -------------------------
# Retrieval setup
# -------------------------

retrieval_chunks = load_jsonl(CHUNKS_PATH)
add_metadata(retrieval_chunks)

retrieval_index = faiss.read_index(str(INDEX_PATH))

if retrieval_index.ntotal != len(retrieval_chunks):
    raise ValueError(
        "FAISS index size does not match the number of retrieval chunks."
    )

retrieval_model = SentenceTransformer(MODEL_NAME)


# -------------------------
# Gemini setup
# -------------------------

gemini_api_key = os.getenv("GEMINI_API_KEY")

gemini_client = (
    genai.Client(api_key=gemini_api_key)
    if gemini_api_key
    else None
)


# -------------------------
# IVR care configuration
# -------------------------

IVR_CARE = {'provider': 'Institute of Vertebrology and Rehabilitation', 'website': 'https://ivr.ua/', 'country': 'Ukraine', 'cities': ['Kyiv', 'Lviv', 'Ivano-Frankivsk'], 'care_categories': ['doctor consultations', 'therapeutic massage', 'physical therapy and physiotherapy', 'rehabilitation', 'manual and other medical procedures', 'injection therapy', 'diagnostics', 'orthopedic corrective devices'], 'online_consultation': True}



def search_knowledge_base(
    query: str,
    top_k: int = TOP_K,
) -> Dict[str, Any]:
    results = semantic_search(
        query=query,
        model=retrieval_model,
        index=retrieval_index,
        chunks=retrieval_chunks,
        top_k=top_k,
    )

    return {
        "success": bool(results),
        "query": query,
        "results": results,
    }



def get_ivr_care_options() -> Dict[str, Any]:
    return {
        "success": True,
        "provider": IVR_CARE["provider"],
        "website": IVR_CARE["website"],
        "country": IVR_CARE["country"],
        "cities": IVR_CARE["cities"],
        "care_categories": IVR_CARE["care_categories"],
        "online_consultation": IVR_CARE["online_consultation"],
    }



def create_initial_state(user_message: str) -> Dict[str, Any]:
    return {
        "user_message": user_message,
        "user_goal": None,

        "selected_route": None,

        "plan": [],
        "current_step": None,
        "completed_steps": [],

        "health_psychology_topics": [],
        "physical_back_pain_request": False,
        "spine_condition_detected": False,
        "medical_advice_requested": False,

        "care_pathway_needed": False,
        "care_mode": None,

        "tool_calls": [],
        "observations": [],
        "intermediate_results": {},

        "fallback_used": False,
        "final_answer": None,
    }



def classify_request(state: Dict[str, Any]) -> Dict[str, Any]:
    message = state["user_message"].lower()

    back_pain_keywords = [
        "lower back pain",
        "back pain",
        "sciatica pain",
        "upper back ache",
        "sharp pain in spine",
        "stiff lower back",
        "neck pain",
        "herniated disc",
        "bulging disc",
        "pinched nerve",
        "muscle strain",
        "spinal stenosis",
        "degenerative disc disease",
        "disc hernia",
        "spinal hernia",
        "lumbar pain",
        "lumbar spine",
        "pain down the leg",
        "shooting pain",
        "radiating pain",
        "back stiffness",
        "neck stiffness",
        "back hurts",
        "pain gets worse",
    ]

    medical_advice_keywords = [
        "back pain relief",
        "back pain treatment",
        "physical therapy for back",
        "chiropractor near me",
        "back stretches for pain",
        "pain relief medicine",
        "painkiller",
        "what should i do",
        "what can i do",
        "how should i treat",
        "how to treat",
        "what treatment",
        "what exercises",
        "which exercises",
        "what medication",
        "what medicine",
    ]

    psychology_keywords = [
        "health psychology",
        "biopsychosocial",
        "stress",
        "anxiety",
        "depression",
        "mood",
        "mental health",
        "coping",
        "fear",
        "pain",
        "can't work",
        "cannot work",
        "can't concentrate",
        "cannot concentrate",
        "angry",
        "can't sleep",
        "cannot sleep",
        "sleep problems",
        "isolated",
        "avoid people",
        "don't want to see anyone",
        "behavior",
        "harmful behavior",
        "harmful behaviour",
        "behavior change",
        "behaviour change",
    ]

    spine_condition_keywords = [
        "spine",
        "herniated disc",
        "bulging disc",
        "disc hernia",
        "spinal hernia",
        "sciatica",
        "pinched nerve",
        "spinal stenosis",
        "degenerative disc disease",
        "lumbar spine",
    ]

    state["current_step"] = "classify_request"

    state["physical_back_pain_request"] = any(
        keyword in message
        for keyword in back_pain_keywords
    )

    state["spine_condition_detected"] = any(
        keyword in message
        for keyword in spine_condition_keywords
    )

    state["medical_advice_requested"] = any(
        keyword in message
        for keyword in medical_advice_keywords
    )

    detected_topics = [
        keyword
        for keyword in psychology_keywords
        if keyword in message
    ]

    state["health_psychology_topics"] = detected_topics

    if state["physical_back_pain_request"]:
        state["selected_route"] = "back_pain_medical_request"
        state["user_goal"] = (
            "understand a physical back-pain problem and what to do next"
        )

    elif detected_topics:
        state["selected_route"] = "psychoeducation"
        state["user_goal"] = (
            "understand a health psychology topic using scientific evidence"
        )

    else:
        state["selected_route"] = "clarification"
        state["user_goal"] = "clarify the user's request"

    state["completed_steps"].append("classify_request")

    return state



def build_plan(state: Dict[str, Any]) -> Dict[str, Any]:
    state["current_step"] = "build_plan"

    if state["selected_route"] == "back_pain_medical_request":
        state["plan"] = [
            "search_knowledge_base",
            "apply_medical_boundary",
            "get_ivr_care_options",
            "add_biopsychosocial_context",
            "build_final_answer",
        ]

        state["care_pathway_needed"] = True

    elif state["selected_route"] == "psychoeducation":
        state["plan"] = [
            "search_knowledge_base",
            "build_final_answer",
        ]

    else:
        state["plan"] = [
            "build_clarification_answer",
        ]

    state["completed_steps"].append("build_plan")

    return state



def build_retrieval_query(state: Dict[str, Any]) -> str:
    user_message = state["user_message"]

    if state["selected_route"] == "back_pain_medical_request":
        return (
            f"{user_message} "
            "psychological behavioral aspects of pain "
            "pain perception health psychology"
        )

    return user_message



def run_knowledge_search(state: Dict[str, Any]) -> Dict[str, Any]:
    state["current_step"] = "search_knowledge_base"

    retrieval_query = build_retrieval_query(state)

    state["tool_calls"].append({
        "tool": "search_knowledge_base",
        "input": {
            "query": retrieval_query,
        },
    })

    result = search_knowledge_base(retrieval_query)

    observation = {
        "tool": "search_knowledge_base",
        "success": result["success"],
        "result_count": len(result.get("results", [])),
        "results": result.get("results", []),
    }

    state["observations"].append(observation)
    state["intermediate_results"]["knowledge_search"] = result

    if not result["success"]:
        state["fallback_used"] = True

    state["completed_steps"].append("search_knowledge_base")

    return state



def apply_medical_boundary(state: Dict[str, Any]) -> Dict[str, Any]:
    state["current_step"] = "apply_medical_boundary"

    boundary = {
        "diagnosis_allowed": False,
        "treatment_recommendations_allowed": False,
        "medical_referral_required": (
            state["physical_back_pain_request"]
            or state["spine_condition_detected"]
        ),
        "psychoeducation_allowed": True,
    }

    state["intermediate_results"]["medical_boundary"] = boundary

    state["observations"].append({
        "step": "apply_medical_boundary",
        "result": boundary,
    })

    state["completed_steps"].append("apply_medical_boundary")

    return state



def run_ivr_care_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    state["current_step"] = "get_ivr_care_options"

    state["tool_calls"].append({
        "tool": "get_ivr_care_options",
        "input": {},
    })

    result = get_ivr_care_options()

    observation = {
        "tool": "get_ivr_care_options",
        "success": result["success"],
        "provider": result["provider"],
        "cities": result["cities"],
        "online_consultation": result["online_consultation"],
    }

    state["observations"].append(observation)
    state["intermediate_results"]["ivr_care"] = result

    state["completed_steps"].append("get_ivr_care_options")

    return state



def add_biopsychosocial_context(
    state: Dict[str, Any],
) -> Dict[str, Any]:
    state["current_step"] = "add_biopsychosocial_context"

    knowledge_result = state["intermediate_results"].get(
        "knowledge_search",
        {},
    )

    results = knowledge_result.get("results", [])

    if not results:
        state["intermediate_results"]["biopsychosocial_context"] = None
        state["fallback_used"] = True

    else:
        top_result = results[0]

        context = {
            "text": top_result["text"],
            "score": top_result["score"],
            "chunk_id": top_result["chunk_id"],
            "source": top_result["metadata"],
        }

        state["intermediate_results"][
            "biopsychosocial_context"
        ] = context

    state["completed_steps"].append(
        "add_biopsychosocial_context"
    )

    return state



def synthesize_with_gemini(
    state: Dict[str, Any],
) -> str:

    knowledge_result = state[
        "intermediate_results"
    ].get("knowledge_search", {})

    results = knowledge_result.get("results", [])

    evidence_text = "\n\n".join(
        [
            (
                f"Source {i + 1}\n"
                f"Chunk ID: {item['chunk_id']}\n"
                f"Document: {item['metadata']['document_id']}\n"
                f"Evidence: {item['text']}"
            )
            for i, item in enumerate(results)
        ]
    )

    state["intermediate_results"]["llm_evidence"] = evidence_text

    if state["selected_route"] == "back_pain_medical_request":
        task = """
    Rewrite only the parts of the retrieved evidence that explain
    psychological, emotional, cognitive, learning, or behavioral aspects
    of pain and pain perception.

    Do not include any information about treatment, therapy, medication,
    exercise, pain-management techniques, interventions, biofeedback,
    relaxation, hypnosis, or other methods of reducing pain.

    The medical/treatment part of the user's request is handled separately
    by the workflow through professional referral.

    Use 2-3 short sentences.
    Paraphrase only what is explicitly present in the retrieved evidence.
    Do not add interpretations, recommendations, or new information.
    """
    else:
        task = """
    Use the retrieved evidence to answer the user's question as directly
    as the evidence allows.

    Summarize and combine relevant statements from the evidence into
    a concise, readable answer.
    """

    prompt = f"""
You are the synthesis layer of a Health Psychology RAG system.

User question:
{state["user_message"]}

Retrieved evidence:
{evidence_text}

Task:
{task}

Rules:
- Use only information contained in the retrieved evidence.
- Do not use general knowledge.
- Do not add new facts, explanations, examples, recommendations,
  causal claims, or interpretations.
- Preserve the meaning of the evidence.
- You may paraphrase, shorten, and combine evidence from multiple chunks.
- Remove broken links, citation artifacts, incomplete sentence fragments,
  and irrelevant text.
- Keep the answer concise and easy to read.
- Do not mention "the provided evidence" or "the knowledge base"
  unless there is genuinely no relevant information in any retrieved chunk.
"""

    try:
      response = gemini_client.models.generate_content(
          model="gemini-3.6-flash",
          contents=prompt,
          config=types.GenerateContentConfig(
              automatic_function_calling=
                  types.AutomaticFunctionCallingConfig(
                      disable=True
                  )
          ),
      )

      return response.text

    except ClientError as error:
          if error.code == 429:
              state["fallback_used"] = True

              return (
                  "LLM synthesis is temporarily unavailable because the API "
                  "quota was exceeded. Relevant evidence was successfully "
                  "retrieved from the knowledge base."
              )

          raise



def build_final_answer(state: Dict[str, Any]) -> Dict[str, Any]:
    state["current_step"] = "build_final_answer"

    route = state["selected_route"]

    if route == "back_pain_medical_request":
        ivr_care = state["intermediate_results"].get(
            "ivr_care",
            {},
        )

        llm_answer = synthesize_with_gemini(state)

        answer_parts = [
            (
                "I cannot diagnose the cause of your back pain or recommend "
                "medication or treatment based on this message. "
                "It would be appropriate to discuss your symptoms with "
                "a healthcare professional."
            )
        ]

        if ivr_care:
            cities = ", ".join(ivr_care["cities"])

            answer_parts.append(
                (
                    f"You can consult specialists at the "
                    f"{ivr_care['provider']}. "
                    f"IVR provides care in {cities}, "
                    f"and online consultations are also available. "
                    f"{ivr_care['website']}"
                )
            )

        if llm_answer:
            answer_parts.append(llm_answer)

        state["final_answer"] = "\n\n".join(answer_parts)

    elif route == "psychoeducation":
        state["final_answer"] = synthesize_with_gemini(state)

    state["completed_steps"].append(
        "build_final_answer"
    )

    return state



def build_clarification_answer(
    state: Dict[str, Any],
) -> Dict[str, Any]:
    state["current_step"] = "build_clarification_answer"

    state["final_answer"] = (
        "Could you clarify what you would like to understand? "
        "You can ask about health psychology, chronic pain, "
        "emotional responses to illness, or a back-pain concern."
    )

    state["completed_steps"].append(
        "build_clarification_answer"
    )

    return state



def run_agent(user_message: str) -> Dict[str, Any]:
    state = create_initial_state(user_message)

    state = classify_request(state)
    state = build_plan(state)

    for step in state["plan"]:
        if step == "search_knowledge_base":
            state = run_knowledge_search(state)

        elif step == "apply_medical_boundary":
            state = apply_medical_boundary(state)

        elif step == "get_ivr_care_options":
            state = run_ivr_care_tool(state)

        elif step == "add_biopsychosocial_context":
            state = add_biopsychosocial_context(state)

        elif step == "build_final_answer":
            state = build_final_answer(state)

        elif step == "build_clarification_answer":
            state = build_clarification_answer(state)

        else:
            state["fallback_used"] = True
            state["observations"].append({
                "step": step,
                "success": False,
                "error": f"Unknown workflow step: {step}",
            })

    return state


if __name__ == "__main__":
    example = run_agent(
        "How to change harmful behavior?"
    )

    print("Route:", example["selected_route"])
    print("Final answer:")
    print(example["final_answer"])
