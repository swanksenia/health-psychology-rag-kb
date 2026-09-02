from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

RiskLevel = Literal["low", "moderate", "high"]
LocationPermission = Literal["unknown", "requested", "granted", "denied"]
CareIntent = Literal["none", "latent", "explicit"]


@dataclass
class ConversationState:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    turn_count: int = 0
    domain_turn_count: int = 0
    unique_topics: list[str] = field(default_factory=list)

    current_route: str | None = None
    risk_level: RiskLevel = "low"
    medical_safety_triggered: bool = False

    care_intent: CareIntent = "none"
    professional_care_required: bool = False

    location_permission: LocationPermission = "unknown"
    detected_city: str | None = None
    confirmed_city: str | None = None

    soft_cta_eligible: bool = False
    ivr_cta_shown: bool = False
    ivr_cta_shown_at_turn: int | None = None
    ivr_cta_accepted: bool = False

    clinic_discussion_started: bool = False
    clinic_discussion_started_at_turn: int | None = None
    ivr_link_clicked: bool = False
    booking_started: bool = False
    booking_completed: bool = False

    llm_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_ai_cost_usd: float = 0.0

    started_at_unix: float = field(default_factory=time.time)
    events: list[dict] = field(default_factory=list)


def _emit(state: ConversationState, event_name: str, **properties) -> None:
    state.events.append({
        "event_name": event_name,
        "session_id": state.session_id,
        "turn_count": state.turn_count,
        "timestamp_unix": time.time(),
        **properties,
    })


def start_conversation(state: ConversationState) -> None:
    if not any(e["event_name"] == "conversation_started" for e in state.events):
        _emit(state, "conversation_started")


def add_turn(
    state: ConversationState,
    *,
    route: str,
    topic: str | None = None,
    risk_level: RiskLevel = "low",
    domain_relevant: bool = True,
) -> None:
    start_conversation(state)

    state.turn_count += 1
    state.current_route = route

    if domain_relevant:
        state.domain_turn_count += 1
        _emit(state, "domain_engaged", route=route, topic=topic)

    if topic and topic not in state.unique_topics:
        state.unique_topics.append(topic)

    state.risk_level = risk_level

    if route == "back_pain_medical_request":
        state.medical_safety_triggered = True

    # High risk means the professional-care pathway must not wait for turn 6.
    if risk_level == "high":
        state.professional_care_required = True
        state.care_intent = "explicit"
        _emit(
            state,
            "professional_care_required",
            reason="high_risk_safety_policy",
        )

    update_soft_cta_eligibility(state)


def update_soft_cta_eligibility(
    state: ConversationState,
    soft_cta_after_turn: int = 6,
    minimum_domain_turns: int = 3,
) -> bool:
    eligible = (
        state.risk_level != "high"
        and state.turn_count >= soft_cta_after_turn
        and state.domain_turn_count >= minimum_domain_turns
        and not state.ivr_cta_shown
    )

    if eligible and not state.soft_cta_eligible:
        state.soft_cta_eligible = True
        _emit(
            state,
            "soft_cta_eligible",
            threshold_turn=soft_cta_after_turn,
            domain_turn_count=state.domain_turn_count,
        )

    return state.soft_cta_eligible


def request_location_permission(state: ConversationState) -> None:
    state.location_permission = "requested"
    _emit(state, "location_permission_requested")


def set_location_permission(
    state: ConversationState,
    granted: bool,
) -> None:
    state.location_permission = "granted" if granted else "denied"
    _emit(
        state,
        "location_permission_result",
        granted=granted,
    )


def set_detected_city(state: ConversationState, city: str) -> None:
    """
    Store only an approximate detected city in conversational state.
    Precise coordinates should not be persisted by this demo.
    """
    state.detected_city = city
    _emit(state, "city_detected", city=city)


def confirm_city(
    state: ConversationState,
    *,
    confirmed: bool,
    corrected_city: str | None = None,
) -> None:
    if confirmed:
        state.confirmed_city = corrected_city or state.detected_city
    elif corrected_city:
        state.confirmed_city = corrected_city
    else:
        state.confirmed_city = None

    _emit(
        state,
        "city_confirmation",
        confirmed=confirmed,
        confirmed_city=state.confirmed_city,
    )


def show_ivr_cta(
    state: ConversationState,
    *,
    reason: str,
) -> None:
    """
    Soft CTA is allowed only when eligible.
    Safety-required professional-care messaging is a separate pathway and can occur immediately.
    """
    if reason == "soft_conversion":
        if not state.soft_cta_eligible:
            raise ValueError("Soft IVR CTA is not eligible yet.")
    elif reason == "safety":
        if not state.professional_care_required:
            raise ValueError("Safety referral requires professional_care_required=True.")
    else:
        raise ValueError("reason must be 'soft_conversion' or 'safety'.")

    if not state.ivr_cta_shown:
        state.ivr_cta_shown = True
        state.ivr_cta_shown_at_turn = state.turn_count
        _emit(state, "ivr_cta_shown", reason=reason)


def accept_ivr_cta(state: ConversationState) -> None:
    state.ivr_cta_accepted = True
    _emit(state, "ivr_cta_accepted")


def start_clinic_discussion(state: ConversationState) -> None:
    state.clinic_discussion_started = True
    if state.clinic_discussion_started_at_turn is None:
        state.clinic_discussion_started_at_turn = state.turn_count
    _emit(state, "clinic_discussion_started")


def click_ivr_link(state: ConversationState) -> None:
    state.ivr_link_clicked = True
    _emit(state, "ivr_link_clicked")


def start_booking(state: ConversationState) -> None:
    state.booking_started = True
    _emit(state, "booking_started")


def complete_booking(state: ConversationState) -> None:
    state.booking_completed = True
    _emit(state, "booking_completed")


def record_model_usage(
    state: ConversationState,
    *,
    input_tokens: int,
    output_tokens: int,
    estimated_cost_usd: float,
) -> None:
    state.llm_calls += 1
    state.input_tokens += input_tokens
    state.output_tokens += output_tokens
    state.estimated_ai_cost_usd += estimated_cost_usd
    _emit(
        state,
        "model_usage",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=estimated_cost_usd,
    )


def conversation_metrics(state: ConversationState) -> dict:
    duration_seconds = max(0.0, time.time() - state.started_at_unix)

    return {
        "session_id": state.session_id,
        "turn_count": state.turn_count,
        "domain_turn_count": state.domain_turn_count,
        "unique_topic_count": len(state.unique_topics),
        "conversation_duration_seconds": duration_seconds,
        "risk_level": state.risk_level,
        "medical_safety_triggered": state.medical_safety_triggered,
        "professional_care_required": state.professional_care_required,
        "soft_cta_eligible": state.soft_cta_eligible,
        "ivr_cta_shown": state.ivr_cta_shown,
        "ivr_cta_shown_at_turn": state.ivr_cta_shown_at_turn,
        "clinic_discussion_started": state.clinic_discussion_started,
        "ivr_link_clicked": state.ivr_link_clicked,
        "booking_started": state.booking_started,
        "booking_completed": state.booking_completed,
        "llm_calls": state.llm_calls,
        "input_tokens": state.input_tokens,
        "output_tokens": state.output_tokens,
        "estimated_ai_cost_usd": state.estimated_ai_cost_usd,
        "cost_per_turn_usd": (
            state.estimated_ai_cost_usd / state.turn_count
            if state.turn_count
            else None
        ),
    }


def funnel_metrics(states: list[ConversationState]) -> dict:
    total = len(states)

    def count(attr: str) -> int:
        return sum(int(bool(getattr(s, attr))) for s in states)

    cta_shown = count("ivr_cta_shown")
    cta_accepted = count("ivr_cta_accepted")
    clinic = count("clinic_discussion_started")
    clicks = count("ivr_link_clicked")
    bookings_started = count("booking_started")
    bookings_completed = count("booking_completed")
    total_cost = sum(s.estimated_ai_cost_usd for s in states)

    return {
        "conversations": total,
        "ivr_cta_shown": cta_shown,
        "ivr_cta_accepted": cta_accepted,
        "clinic_discussion_started": clinic,
        "ivr_link_clicked": clicks,
        "booking_started": bookings_started,
        "booking_completed": bookings_completed,
        "cta_acceptance_rate": cta_accepted / cta_shown if cta_shown else None,
        "clinic_to_click_rate": clicks / clinic if clinic else None,
        "click_to_booking_start_rate": bookings_started / clicks if clicks else None,
        "booking_completion_rate": (
            bookings_completed / bookings_started if bookings_started else None
        ),
        "total_ai_cost_usd": total_cost,
        "ai_cost_per_conversation_usd": total_cost / total if total else None,
        "ai_cost_per_booking_usd": (
            total_cost / bookings_completed if bookings_completed else None
        ),
    }


def save_state(state: ConversationState, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(asdict(state), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    # Small deterministic demo.
    state = ConversationState()

    for i in range(6):
        add_turn(
            state,
            route="health_psychology",
            topic="ergonomics" if i < 2 else "work_and_pain",
            risk_level="low",
        )

    assert state.soft_cta_eligible is True
    show_ivr_cta(state, reason="soft_conversion")
    accept_ivr_cta(state)
    start_clinic_discussion(state)

    print(json.dumps(conversation_metrics(state), ensure_ascii=False, indent=2))
