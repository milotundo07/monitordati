from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
import streamlit as st

from .constants import ACTIVITY_CATALOG

ACTIVITY_COLUMNS = [
    "category", "activity", "start_date", "p1_status", "p2_status",
    "p3_status", "p4_status", "end_date",
]
EXPENSE_COLUMNS = [
    "activity", "cost_parameter", "p1_quantity", "p1_amount",
    "p2_quantity", "p2_amount", "p3_quantity", "p3_amount",
    "p4_quantity", "p4_amount",
]
BENEFICIARY_COLUMNS = [
    "activity", "beneficiary_type", "age_range", "target",
    "p1_reached", "p1_minors", "p1_relation",
    "p2_reached", "p2_minors", "p2_relation",
    "p3_reached", "p3_minors", "p3_relation",
    "p4_reached", "p4_minors", "p4_relation",
]


def default_activities() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for category, activities in ACTIVITY_CATALOG.items():
        for activity in activities:
            rows.append({
                "category": category,
                "activity": activity,
                "start_date": None,
                "p1_status": "",
                "p2_status": "",
                "p3_status": "",
                "p4_status": "",
                "end_date": None,
            })
    return pd.DataFrame(rows, columns=ACTIVITY_COLUMNS)


def blank_expenses(rows: int = 2) -> pd.DataFrame:
    return pd.DataFrame([{column: None for column in EXPENSE_COLUMNS} for _ in range(rows)], columns=EXPENSE_COLUMNS)


def blank_beneficiaries(rows: int = 1) -> pd.DataFrame:
    return pd.DataFrame([{column: None for column in BENEFICIARY_COLUMNS} for _ in range(rows)], columns=BENEFICIARY_COLUMNS)


def init_state() -> None:
    defaults = {
        "project_title": "",
        "project_code": "",
        "lead_org": "",
        "project_start": date(2025, 7, 1),
        "project_end": date(2027, 5, 31),
        "contact_phone": "",
        "contact_email": "",
        "contribution_p1": 0.0,
        "contribution_p2": 0.0,
        "contribution_p3": 0.0,
        "contribution_p4": 0.0,
        "activities_df": default_activities(),
        "expenses_df": blank_expenses(),
        "beneficiaries_df": blank_beneficiaries(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_state() -> None:
    keys = [
        "project_title", "project_code", "lead_org", "project_start", "project_end",
        "contact_phone", "contact_email", "contribution_p1", "contribution_p2",
        "contribution_p3", "contribution_p4", "activities_df", "expenses_df",
        "beneficiaries_df", "activities_editor", "expenses_editor", "beneficiaries_editor",
    ]
    for key in keys:
        st.session_state.pop(key, None)
    init_state()
