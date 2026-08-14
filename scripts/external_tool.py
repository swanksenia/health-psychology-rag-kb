from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANALYTICS_FILE = PROJECT_ROOT / "data" / "analytics" / "usage_events.csv"


@dataclass
class ToolRequest:
    tool_name: str
    tool_type: str
    payload: dict[str, Any]


@dataclass
class ToolObservation:
    tool_name: str
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


def validate_period_days(period_days: Any) -> str | None:
    if period_days is None:
        return "period_days is required."

    if not isinstance(period_days, int):
        return "period_days must be an integer."

    if period_days < 1 or period_days > 1095:
        return "period_days must be between 1 and 1095."

    return None


def validate_analytics_access(requester_role: str) -> str | None:
    if requester_role != "admin":
        return "Access denied: analytics data is restricted to administrators."

    return None


def get_usage_analytics(period_days: int) -> dict:
    validation_error = validate_period_days(period_days)

    if validation_error:
        return {
            "status": "error",
            "error": validation_error,
        }

    df = pd.read_csv(
        ANALYTICS_FILE,
        parse_dates=["timestamp"],
    )

    if df.empty:
        return {
            "status": "error",
            "error": "Analytics data source is empty.",
        }

    reference_date = df["timestamp"].max()

    start_date = reference_date - pd.Timedelta(
        days=period_days - 1
    )

    period_df = df[
        df["timestamp"] >= start_date.normalize()
    ].copy()

    total_users = period_df["user_id"].nunique()
    total_sessions = period_df["session_id"].nunique()
    total_queries = len(period_df)

    first_seen = (
        df.groupby("user_id")["timestamp"]
        .min()
    )

    users_in_period = period_df["user_id"].unique()

    new_users = sum(
        first_seen[user_id] >= start_date.normalize()
        for user_id in users_in_period
    )

    returning_users = total_users - new_users

    session_times = (
        period_df.groupby("session_id")["timestamp"]
        .agg(["min", "max"])
    )

    session_times["duration_minutes"] = (
        session_times["max"] - session_times["min"]
    ).dt.total_seconds() / 60

    average_session_minutes = float(
        round(
            session_times["duration_minutes"].mean(),
            2,
        )
    )

    average_queries_per_session = round(
        total_queries / total_sessions,
        2,
    )

    top_queries = (
        period_df["query"]
        .value_counts()
        .head(5)
        .reset_index()
    )

    top_queries.columns = ["query", "count"]

    top_queries = top_queries.to_dict(
        orient="records"
    )

    return {
        "status": "success",
        "period_days": period_days,
        "period_start": start_date.date().isoformat(),
        "period_end": reference_date.date().isoformat(),
        "total_users": total_users,
        "new_users": new_users,
        "returning_users": returning_users,
        "total_sessions": total_sessions,
        "total_queries": total_queries,
        "average_session_minutes": average_session_minutes,
        "average_queries_per_session": average_queries_per_session,
        "top_queries": top_queries,
    }


def execute_tool_request(request: ToolRequest) -> ToolObservation:
    if request.tool_name != "get_usage_analytics":
        return ToolObservation(
            tool_name=request.tool_name,
            success=False,
            error=f"Unknown tool: {request.tool_name}",
        )

    if request.tool_type != "read":
        return ToolObservation(
            tool_name=request.tool_name,
            success=False,
            error="get_usage_analytics must be called as a read tool.",
        )

    period_days = request.payload.get("period_days")
    requester_role = request.payload.get("requester_role")

    access_error = validate_analytics_access(requester_role)

    if access_error:
        return ToolObservation(
            tool_name=request.tool_name,
            success=False,
            error=access_error,
        )

    result = get_usage_analytics(
        period_days=period_days,
    )

    if result["status"] == "error":
        return ToolObservation(
            tool_name=request.tool_name,
            success=False,
            error=result["error"],
        )

    return ToolObservation(
        tool_name=request.tool_name,
        success=True,
        data=result,
    )
