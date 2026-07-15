from __future__ import annotations

import math
import streamlit as st

from qubi_app.constants import (
    BENEFICIARY_RELATION_OPTIONS,
    CATEGORY_CAPACITY,
    COST_PARAMETERS,
    EXPENSE_ACTIVITY_OPTIONS,
    PERIODS,
    STATUS_OPTIONS,
)
from qubi_app.exporter import build_excel, safe_filename
from qubi_app.persistence import load_payload, project_json_bytes, project_payload
from qubi_app.state import init_state, reset_state
from qubi_app.validation import cleaned_rows, validate_project

st.set_page_config(
    page_title="Monitoraggio Fondo QuBì",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_state()

st.title("Monitoraggio dei progetti finanziati dal Fondo QuBì")
st.caption("Compila i dati in modo guidato, verifica gli errori e genera la scheda Excel ufficiale.")

with st.sidebar:
    st.header("Progetto")
    uploaded = st.file_uploader("Carica un progetto salvato", type=["json"], key="project_loader")
    if st.button("Apri il progetto", use_container_width=True, disabled=uploaded is None):
        try:
            load_payload(uploaded.getvalue())
            st.success("Progetto caricato.")
            st.rerun()
        except Exception as exc:
            st.error(f"Il file non è valido: {exc}")

    st.download_button(
        "Salva una copia modificabile",
        data=project_json_bytes(),
        file_name="progetto_qubi.json",
        mime="application/json",
        use_container_width=True,
    )

    if st.button("Azzera tutti i dati", type="secondary", use_container_width=True):
        reset_state()
        st.rerun()

    st.info(
        "I dati restano nella sessione corrente. Scarica il file JSON per conservarli e riaprirli in seguito."
    )

TAB_GENERAL, TAB_ACTIVITIES, TAB_EXPENSES, TAB_BENEFICIARIES, TAB_EXPORT = st.tabs([
    "1. Informazioni generali",
    "2. Attività",
    "3. Avanzamento economico",
    "4. Beneficiari",
    "5. Verifica ed esporta",
])

with TAB_GENERAL:
    st.subheader("Informazioni generali")
    left, right = st.columns(2)
    with left:
        st.text_input("Titolo del progetto", key="project_title")
        st.text_input("Codice progetto", key="project_code", help="ID associato al progetto nel portale FDC")
        st.text_input("Ente capofila", key="lead_org")
        st.date_input("Data di inizio", key="project_start", format="DD/MM/YYYY")
    with right:
        st.date_input("Data di fine", key="project_end", format="DD/MM/YYYY")
        st.text_input("Telefono del referente", key="contact_phone")
        st.text_input("Email del referente", key="contact_email")

    st.subheader("Stima cumulativa del contributo utilizzato")
    columns = st.columns(4)
    for column, period in zip(columns, PERIODS):
        with column:
            st.number_input(
                f"Al {period['end']} (%)",
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                key=f"contribution_{period['key']}",
            )

with TAB_ACTIVITIES:
    st.subheader("Stato di avanzamento delle attività")
    st.write(
        "Inserisci una riga per ogni attività. Le date e gli stati verranno riportati nella sezione corrispondente della scheda ufficiale."
    )
    capacity_text = "; ".join(f"{category}: {capacity}" for category, capacity in CATEGORY_CAPACITY.items())
    st.caption(f"Capienza massima del modello: {capacity_text}.")

    category_options = list(CATEGORY_CAPACITY.keys())
    edited_activities = st.data_editor(
        st.session_state.activities_df,
        key="activities_editor",
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "category": st.column_config.SelectboxColumn("Categoria", options=category_options, required=True, width="medium"),
            "activity": st.column_config.TextColumn("Attività", required=True, width="large"),
            "start_date": st.column_config.DateColumn("Data di avvio", format="DD/MM/YYYY"),
            "p1_status": st.column_config.SelectboxColumn("31/12/2025", options=STATUS_OPTIONS),
            "p2_status": st.column_config.SelectboxColumn("30/06/2026", options=STATUS_OPTIONS),
            "p3_status": st.column_config.SelectboxColumn("31/12/2026", options=STATUS_OPTIONS),
            "p4_status": st.column_config.SelectboxColumn("31/05/2027", options=STATUS_OPTIONS),
            "end_date": st.column_config.DateColumn("Data di conclusione", format="DD/MM/YYYY"),
        },
    )
    st.session_state.activities_df = edited_activities

with TAB_EXPENSES:
    st.subheader("Stato di avanzamento economico")
    st.write(
        "Gli importi e le quantità richiesti dalla scheda sono cumulativi: il valore di un periodo non può essere inferiore a quello precedente."
    )
    with st.expander("Consulta i parametri di costo del vademecum"):
        for activity, parameter in COST_PARAMETERS.items():
            st.markdown(f"- **{activity}:** {parameter}")

    expense_frame = st.session_state.expenses_df.copy()
    for index, row in expense_frame.iterrows():
        activity = str(row.get("activity") or "").strip()
        if activity in COST_PARAMETERS and not str(row.get("cost_parameter") or "").strip():
            expense_frame.at[index, "cost_parameter"] = COST_PARAMETERS[activity]

    edited_expenses = st.data_editor(
        expense_frame,
        key="expenses_editor",
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "activity": st.column_config.SelectboxColumn("Tipologia attività", options=EXPENSE_ACTIVITY_OPTIONS, width="large"),
            "cost_parameter": st.column_config.TextColumn("Parametro di costo", width="large"),
            "p1_quantity": st.column_config.NumberColumn("N. al 31/12/2025", min_value=0.0),
            "p1_amount": st.column_config.NumberColumn("€ al 31/12/2025", min_value=0.0, format="%.2f"),
            "p2_quantity": st.column_config.NumberColumn("N. al 30/06/2026", min_value=0.0),
            "p2_amount": st.column_config.NumberColumn("€ al 30/06/2026", min_value=0.0, format="%.2f"),
            "p3_quantity": st.column_config.NumberColumn("N. al 31/12/2026", min_value=0.0),
            "p3_amount": st.column_config.NumberColumn("€ al 31/12/2026", min_value=0.0, format="%.2f"),
            "p4_quantity": st.column_config.NumberColumn("N. al 31/05/2027", min_value=0.0),
            "p4_amount": st.column_config.NumberColumn("€ al 31/05/2027", min_value=0.0, format="%.2f"),
        },
    )
    st.session_state.expenses_df = edited_expenses
    st.caption("La scheda ufficiale contiene 4 righe di spesa.")

with TAB_BENEFICIARIES:
    st.subheader("Beneficiari previsti e raggiunti")
    st.write(
        "Inserisci una riga distinta quando la stessa attività riguarda tipologie di beneficiari o fasce di età differenti."
    )
    edited_beneficiaries = st.data_editor(
        st.session_state.beneficiaries_df,
        key="beneficiaries_editor",
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "activity": st.column_config.TextColumn("Attività", required=True, width="large"),
            "beneficiary_type": st.column_config.TextColumn("Tipologia beneficiari", required=True, width="medium"),
            "age_range": st.column_config.TextColumn("Fascia di età", required=True),
            "target": st.column_config.NumberColumn("Target di progetto", min_value=0.0),
            "p1_reached": st.column_config.NumberColumn("Raggiunti 31/12/2025", min_value=0.0),
            "p1_minors": st.column_config.NumberColumn("Minori 31/12/2025", min_value=0.0),
            "p1_relation": st.column_config.SelectboxColumn("Rapporto con QuBì 31/12/2025", options=BENEFICIARY_RELATION_OPTIONS),
            "p2_reached": st.column_config.NumberColumn("Raggiunti 30/06/2026", min_value=0.0),
            "p2_minors": st.column_config.NumberColumn("Minori 30/06/2026", min_value=0.0),
            "p2_relation": st.column_config.SelectboxColumn("Rapporto con QuBì 30/06/2026", options=BENEFICIARY_RELATION_OPTIONS),
            "p3_reached": st.column_config.NumberColumn("Raggiunti 31/12/2026", min_value=0.0),
            "p3_minors": st.column_config.NumberColumn("Minori 31/12/2026", min_value=0.0),
            "p3_relation": st.column_config.SelectboxColumn("Rapporto con QuBì 31/12/2026", options=BENEFICIARY_RELATION_OPTIONS),
            "p4_reached": st.column_config.NumberColumn("Raggiunti 31/05/2027", min_value=0.0),
            "p4_minors": st.column_config.NumberColumn("Minori 31/05/2027", min_value=0.0),
            "p4_relation": st.column_config.SelectboxColumn("Rapporto con QuBì 31/05/2027", options=BENEFICIARY_RELATION_OPTIONS),
        },
    )
    st.session_state.beneficiaries_df = edited_beneficiaries
    st.caption("La scheda ufficiale contiene 6 righe per i beneficiari.")

with TAB_EXPORT:
    st.subheader("Controllo finale")
    payload = project_payload()
    validation_data = {
        "general": {
            **payload["general"],
            "project_start": st.session_state.project_start,
            "project_end": st.session_state.project_end,
        },
        "contribution": payload["contribution"],
        "activities_df": st.session_state.activities_df,
        "expenses_df": st.session_state.expenses_df,
        "beneficiaries_df": st.session_state.beneficiaries_df,
    }
    errors = validate_project(validation_data)

    activities_count = len(cleaned_rows(st.session_state.activities_df, "activity"))
    expenses = cleaned_rows(st.session_state.expenses_df, "activity")
    beneficiaries = cleaned_rows(st.session_state.beneficiaries_df, "activity")
    def safe_total(rows, key):
        total = 0.0
        for row in rows:
            value = row.get(key)
            try:
                number = float(value)
            except (TypeError, ValueError):
                continue
            if not math.isnan(number):
                total += number
        return total

    final_expense = safe_total(expenses, "p4_amount")
    final_beneficiaries = safe_total(beneficiaries, "p4_reached")

    metric_columns = st.columns(3)
    metric_columns[0].metric("Attività inserite", activities_count)
    metric_columns[1].metric("Spesa cumulativa finale", f"€ {final_expense:,.2f}")
    metric_columns[2].metric("Beneficiari raggiunti finali", f"{final_beneficiaries:,.0f}")

    if errors:
        st.error(f"La scheda contiene {len(errors)} problemi da correggere.")
        for error in errors:
            st.markdown(f"- {error}")
    else:
        st.success("La scheda è coerente e può essere generata.")
        excel_data = {
            "general": validation_data["general"],
            "contribution": validation_data["contribution"],
            "activities_df": st.session_state.activities_df,
            "expenses_df": st.session_state.expenses_df,
            "beneficiaries_df": st.session_state.beneficiaries_df,
        }
        try:
            excel_bytes = build_excel(excel_data)
            st.download_button(
                "Genera e scarica la scheda tecnica Excel",
                data=excel_bytes,
                file_name=safe_filename(st.session_state.project_title, st.session_state.project_code),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"Non è stato possibile generare l'Excel: {exc}")
