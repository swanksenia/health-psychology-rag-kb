
from typing import Any, Literal, TypedDict

from langgraph.graph import StateGraph, START, END


UserRole = Literal[
    "admin",
    "user",
]

Route = Literal[
    "health_psychology",
    "analytics",
    "clarification",
]


class WorkflowState(TypedDict, total=False):
    user_request: str
    user_role: UserRole

    route: Route | None
    analytics_access: bool | None

    tool_result: dict[str, Any] | None
    final_answer: str | None

    executed_nodes: list[str]


def append_node(
    state: WorkflowState,
    node_name: str,
) -> list[str]:

    return [
        *state.get("executed_nodes", []),
        node_name,
    ]


def search_health_psychology(
    query: str,
) -> dict[str, Any]:

    return {
        "tool_name": "search_health_psychology",
        "success": True,
        "query": query,
        "result": (
            "Relevant Health Psychology context was retrieved "
            "about chronic pain, pain perception, psychological "
            "factors, and daily functioning."
        ),
    }


def get_usage_analytics(
    period_days: int = 7,
) -> dict[str, Any]:

    return {
        "tool_name": "get_usage_analytics",
        "success": True,
        "period_days": period_days,
        "total_users": 6,
        "new_users": 4,
        "returning_users": 2,
        "total_sessions": 9,
        "total_queries": 15,
    }


def classify_request_node(
    state: WorkflowState,
) -> dict[str, Any]:

    request = state["user_request"].lower()

    analytics_keywords = [
        "analytics",
        "users",
        "sessions",
        "queries",
        "usage",
    ]

    health_psychology_keywords = [
        "pain",
        "chronic",
        "stress",
        "psychology",
        "health",
        "behavior",
        "behaviour",
        "com-b",
    ]

    if any(
        keyword in request
        for keyword in analytics_keywords
    ):
        route = "analytics"

    elif any(
        keyword in request
        for keyword in health_psychology_keywords
    ):
        route = "health_psychology"

    else:
        route = "clarification"

    return {
        "route": route,
        "executed_nodes": append_node(
            state,
            "classify_request",
        ),
    }


def retrieve_health_psychology_node(
    state: WorkflowState,
) -> dict[str, Any]:

    result = search_health_psychology(
        state["user_request"]
    )

    return {
        "tool_result": result,
        "executed_nodes": append_node(
            state,
            "retrieve_health_psychology",
        ),
    }


def check_analytics_access_node(
    state: WorkflowState,
) -> dict[str, Any]:

    access_granted = (
        state.get("user_role") == "admin"
    )

    return {
        "analytics_access": access_granted,
        "executed_nodes": append_node(
            state,
            "check_analytics_access",
        ),
    }


def get_usage_analytics_node(
    state: WorkflowState,
) -> dict[str, Any]:

    result = get_usage_analytics(
        period_days=7
    )

    return {
        "tool_result": result,
        "executed_nodes": append_node(
            state,
            "get_usage_analytics",
        ),
    }


def deny_access_node(
    state: WorkflowState,
) -> dict[str, Any]:

    return {
        "tool_result": {
            "tool_name": "get_usage_analytics",
            "success": False,
            "error": "analytics_access_denied",
        },
        "executed_nodes": append_node(
            state,
            "deny_access",
        ),
    }


def ask_clarification_node(
    state: WorkflowState,
) -> dict[str, Any]:

    return {
        "tool_result": {
            "success": True,
            "message": (
                "Please clarify whether your question is about "
                "Health Psychology content or product analytics."
            ),
        },
        "executed_nodes": append_node(
            state,
            "ask_clarification",
        ),
    }


def build_answer_node(
    state: WorkflowState,
) -> dict[str, Any]:

    route = state.get("route")
    tool_result = state.get("tool_result")

    if route == "health_psychology":

        final_answer = (
            tool_result.get("result")
            if tool_result
            else "No Health Psychology context was retrieved."
        )

    elif route == "analytics":

        if state.get("analytics_access") is True:

            final_answer = (
                f"Product analytics for the last "
                f"{tool_result['period_days']} days: "
                f"{tool_result['total_users']} users, "
                f"{tool_result['total_sessions']} sessions, "
                f"and {tool_result['total_queries']} queries."
            )

        else:

            final_answer = (
                "Access denied. Product analytics are available "
                "only to authorized internal users."
            )

    else:

        final_answer = (
            tool_result.get("message")
            if tool_result
            else "Please clarify your request."
        )

    return {
        "final_answer": final_answer,
        "executed_nodes": append_node(
            state,
            "build_answer",
        ),
    }


def route_after_classification(
    state: WorkflowState,
) -> str:

    route = state.get("route")

    if route == "health_psychology":
        return "retrieve_health_psychology"

    if route == "analytics":
        return "check_analytics_access"

    return "ask_clarification"


def route_after_access_check(
    state: WorkflowState,
) -> str:

    if state.get("analytics_access") is True:
        return "get_usage_analytics"

    return "deny_access"


def build_graph():

    workflow = StateGraph(WorkflowState)

    workflow.add_node(
        "classify_request",
        classify_request_node,
    )

    workflow.add_node(
        "retrieve_health_psychology",
        retrieve_health_psychology_node,
    )

    workflow.add_node(
        "check_analytics_access",
        check_analytics_access_node,
    )

    workflow.add_node(
        "get_usage_analytics",
        get_usage_analytics_node,
    )

    workflow.add_node(
        "deny_access",
        deny_access_node,
    )

    workflow.add_node(
        "ask_clarification",
        ask_clarification_node,
    )

    workflow.add_node(
        "build_answer",
        build_answer_node,
    )

    workflow.add_edge(
        START,
        "classify_request",
    )

    workflow.add_conditional_edges(
        "classify_request",
        route_after_classification,
        {
            "retrieve_health_psychology":
                "retrieve_health_psychology",
            "check_analytics_access":
                "check_analytics_access",
            "ask_clarification":
                "ask_clarification",
        },
    )

    workflow.add_edge(
        "retrieve_health_psychology",
        "build_answer",
    )

    workflow.add_conditional_edges(
        "check_analytics_access",
        route_after_access_check,
        {
            "get_usage_analytics":
                "get_usage_analytics",
            "deny_access":
                "deny_access",
        },
    )

    workflow.add_edge(
        "get_usage_analytics",
        "build_answer",
    )

    workflow.add_edge(
        "deny_access",
        "build_answer",
    )

    workflow.add_edge(
        "ask_clarification",
        "build_answer",
    )

    workflow.add_edge(
        "build_answer",
        END,
    )

    return workflow.compile()


TEST_SCENARIOS = [
    {
        "name": "Health Psychology question",
        "user_request":
            "Why can't I work effectively with chronic back pain?",
        "user_role": "user",
    },
    {
        "name": "Analytics request — admin",
        "user_request":
            "Show me product analytics for the last 7 days.",
        "user_role": "admin",
    },
    {
        "name": "Analytics request — external user",
        "user_request":
            "Show me product analytics for the last 7 days.",
        "user_role": "user",
    },
    {
        "name": "Unclear request",
        "user_request":
            "I feel tired and annoyed lately and I don't know why.",
        "user_role": "user",
    },
]


if __name__ == "__main__":

    app = build_graph()

    for scenario in TEST_SCENARIOS:

        initial_state: WorkflowState = {
            "user_request": scenario["user_request"],
            "user_role": scenario["user_role"],
            "route": None,
            "analytics_access": None,
            "tool_result": None,
            "final_answer": None,
            "executed_nodes": [],
        }

        final_state = app.invoke(
            initial_state
        )

        print("=" * 70)
        print(scenario["name"])
        print(
            "Path:",
            " -> ".join(
                final_state["executed_nodes"]
            ),
        )
        print(
            "Answer:",
            final_state["final_answer"],
        )
