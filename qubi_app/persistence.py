from __future__ import annotations

import json
import math
from datetime import date, datetime
from typing import Any

import pandas as pd
import streamlit as st

from .state import ACTIVITY_COLUMNS, BENEFICIARY_COLUMNS, EXPENSE_COLUMNS


def _safe_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (date, datetime, pd.Timestamp)):
        return value.isoformat()
    if isinstance(value, float) and math.isnan(value):
        return None
    if pd.isna(value):
        return None
    return value


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [{key: _safe_value(value) for key, value in row.items()} for row in df.to_dict("records")]


def project_payload() -> dict[str, Any]:
    return {
        "version": 1,
        "general": {
            "project_title": st.session_state.project_title,
            "project_code": st.session_state.project_code,
            "lead_org": st.session_state.lead_org,
            "project_start": _safe_value(st.session_state.project_start),
            "project_end": _safe_value(st.session_state.project_end),
            "contact_phone": st.session_state.contact_phone,
            "contact_email": st.session_state.contact_email,
        },
        "contribution": {
            "p1": float(st.session_state.contribution_p1),
            "p2": float(st.session_state.contribution_p2),
            "p3": float(st.session_state.contribution_p3),
            "p4": float(st.session_state.contribution_p4),
        },
        "activities": _records(st.session_state.activities_df),
        "expenses": _records(st.session_state.expenses_df),
        "beneficiaries": _records(st.session_state.beneficiaries_df),
    }


def project_json_bytes() -> bytes:
    return json.dumps(project_payload(), ensure_ascii=False, indent=2).encode("utf-8")


def _date_or_none(value: Any):
    if not value:
        return None
    try:
        return pd.to_datetime(value).date()
    except (TypeError, ValueError):
        return None


def _frame(records: list[dict[str, Any]], columns: list[str], date_columns: list[str] | None = None) -> pd.DataFrame:
    frame = pd.DataFrame(records or [], columns=columns)
    if frame.empty:
        frame = pd.DataFrame([{column: None for column in columns}], columns=columns)
    for column in date_columns or []:
        frame[column] = frame[column].apply(_date_or_none)
    return frame


def load_payload(raw: bytes) -> None:
    data = json.loads(raw.decode("utf-8"))
    general = data.get("general", {})
    st.session_state.project_title = general.get("project_title", "")
    st.session_state.project_code = general.get("project_code", "")
    st.session_state.lead_org = general.get("lead_org", "")
    st.session_state.project_start = _date_or_none(general.get("project_start")) or date(2025, 7, 1)
    st.session_state.project_end = _date_or_none(general.get("project_end")) or date(2027, 5, 31)
    st.session_state.contact_phone = general.get("contact_phone", "")
    st.session_state.contact_email = general.get("contact_email", "")

    contribution = data.get("contribution", {})
    for period in ("p1", "p2", "p3", "p4"):
        st.session_state[f"contribution_{period}"] = float(contribution.get(period, 0) or 0)

    st.session_state.activities_df = _frame(
        data.get("activities", []), ACTIVITY_COLUMNS, ["start_date", "end_date"]
    )
    st.session_state.expenses_df = _frame(data.get("expenses", []), EXPENSE_COLUMNS)
    st.session_state.beneficiaries_df = _frame(data.get("beneficiaries", []), BENEFICIARY_COLUMNS)

    for widget_key in ("activities_editor", "expenses_editor", "beneficiaries_editor"):
        st.session_state.pop(widget_key, None)
