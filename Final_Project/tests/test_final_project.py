from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from conversation_funnel import (
    ConversationState,
    add_turn,
    show_ivr_cta,
    request_location_permission,
    set_location_permission,
    set_detected_city,
    confirm_city,
)
from multilingual_router import route_native_ukrainian


def test_soft_cta_only_after_six_turns():
    state = ConversationState()

    for _ in range(5):
        add_turn(
            state,
            route="health_psychology",
            topic="ergonomics",
            risk_level="low",
        )

    assert state.soft_cta_eligible is False

    add_turn(
        state,
        route="health_psychology",
        topic="work_and_pain",
        risk_level="low",
    )
    assert state.soft_cta_eligible is True


def test_high_risk_does_not_wait_for_turn_six():
    state = ConversationState()

    add_turn(
        state,
        route="back_pain_medical_request",
        topic="symptoms",
        risk_level="high",
    )

    assert state.turn_count == 1
    assert state.professional_care_required is True
    assert state.soft_cta_eligible is False

    show_ivr_cta(state, reason="safety")
    assert state.ivr_cta_shown_at_turn == 1


def test_location_requires_permission_and_confirmation_flow():
    state = ConversationState()

    request_location_permission(state)
    assert state.location_permission == "requested"

    set_location_permission(state, True)
    assert state.location_permission == "granted"

    set_detected_city(state, "Lisbon")
    assert state.confirmed_city is None

    confirm_city(state, confirmed=True)
    assert state.confirmed_city == "Lisbon"


def test_real_user_medication_query_routes_to_medical_safety():
    result = route_native_ukrainian("місцеві аналоги Олфену")
    assert result.route == "back_pain_medical_request"


def test_ergonomic_chair_routes_to_health_psychology():
    result = route_native_ukrainian("Ергономічний стул")
    assert result.route == "health_psychology"
