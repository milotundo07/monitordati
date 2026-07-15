from __future__ import annotations

import math
from typing import Any

import pandas as pd

from .constants import CATEGORY_CAPACITY


def _blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip() == ""


def _number(value: Any) -> float:
    if _blank(value):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def cleaned_rows(df: pd.DataFrame, required_column: str) -> list[dict[str, Any]]:
    return [row for row in df.to_dict("records") if not _blank(row.get(required_column))]


def validate_project(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    general = data["general"]
    for field, label in [
        ("project_title", "Titolo del progetto"),
        ("project_code", "Codice progetto"),
        ("lead_org", "Ente capofila"),
        ("contact_phone", "Telefono del referente"),
        ("contact_email", "Email del referente"),
    ]:
        if _blank(general.get(field)):
            errors.append(f"Informazioni generali: manca «{label}».")
    if general.get("project_start") and general.get("project_end") and general["project_start"] > general["project_end"]:
        errors.append("Informazioni generali: la data di inizio è successiva alla data di fine.")

    activities = cleaned_rows(data["activities_df"], "activity")
    counts: dict[str, int] = {}
    for index, row in enumerate(activities, start=1):
        category = str(row.get("category") or "").strip()
        if not category:
            errors.append(f"Attività {index}: manca la categoria.")
        counts[category] = counts.get(category, 0) + 1
        start = row.get("start_date")
        end = row.get("end_date")
        if start and end and start > end:
            errors.append(f"Attività «{row.get('activity')}»: la conclusione precede l'avvio.")
    for category, count in counts.items():
        capacity = CATEGORY_CAPACITY.get(category)
        if capacity is None:
            errors.append(f"Attività: categoria non riconosciuta «{category}».")
        elif count > capacity:
            errors.append(f"Attività: la categoria «{category}» contiene {count} righe, ma la scheda ufficiale ne ammette {capacity}.")

    expenses = cleaned_rows(data["expenses_df"], "activity")
    if len(expenses) > 4:
        errors.append("Avanzamento economico: la scheda ufficiale contiene al massimo 4 righe di spesa.")
    for row_number, row in enumerate(expenses, start=1):
        previous_amount = -1.0
        previous_quantity = -1.0
        for period in ("p1", "p2", "p3", "p4"):
            amount = _number(row.get(f"{period}_amount"))
            quantity = _number(row.get(f"{period}_quantity"))
            if math.isnan(amount) or math.isnan(quantity):
                errors.append(f"Spesa {row_number}: quantità e importi devono essere numeri.")
                break
            if amount < 0 or quantity < 0:
                errors.append(f"Spesa {row_number}: quantità e importi non possono essere negativi.")
                break
            if amount < previous_amount:
                errors.append(f"Spesa {row_number}: gli importi complessivi devono essere cumulativi e non decrescenti.")
                break
            if quantity < previous_quantity:
                errors.append(f"Spesa {row_number}: le quantità complessive devono essere cumulative e non decrescenti.")
                break
            previous_amount, previous_quantity = amount, quantity

    contribution = data["contribution"]
    previous = -1.0
    for period in ("p1", "p2", "p3", "p4"):
        value = float(contribution.get(period, 0) or 0)
        if not 0 <= value <= 100:
            errors.append("Utilizzo contributo: ogni percentuale deve essere compresa tra 0 e 100.")
            break
        if value < previous:
            errors.append("Utilizzo contributo: le percentuali cumulative non possono diminuire nei periodi successivi.")
            break
        previous = value

    beneficiaries = cleaned_rows(data["beneficiaries_df"], "activity")
    if len(beneficiaries) > 6:
        errors.append("Beneficiari: la scheda ufficiale contiene al massimo 6 righe.")
    for row_number, row in enumerate(beneficiaries, start=1):
        if _blank(row.get("beneficiary_type")):
            errors.append(f"Beneficiari {row_number}: manca la tipologia di beneficiari.")
        if _blank(row.get("age_range")):
            errors.append(f"Beneficiari {row_number}: manca la fascia di età.")
        target = _number(row.get("target"))
        if math.isnan(target) or target < 0:
            errors.append(f"Beneficiari {row_number}: il target deve essere un numero non negativo.")
        previous_reached = -1.0
        for period in ("p1", "p2", "p3", "p4"):
            reached = _number(row.get(f"{period}_reached"))
            minors = _number(row.get(f"{period}_minors"))
            if math.isnan(reached) or math.isnan(minors) or reached < 0 or minors < 0:
                errors.append(f"Beneficiari {row_number}: i conteggi devono essere numeri non negativi.")
                break
            if reached < previous_reached:
                errors.append(f"Beneficiari {row_number}: i raggiunti devono essere cumulativi e non decrescenti.")
                break
            if reached > 0 and _blank(row.get(f"{period}_relation")):
                errors.append(f"Beneficiari {row_number}: indica se i beneficiari del periodo {period[-1]} sono conosciuti, nuovi, misti o non rilevabili.")
                break
            previous_reached = reached

    return errors
