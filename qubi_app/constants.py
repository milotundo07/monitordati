from __future__ import annotations

PERIODS = [
    {"key": "p1", "label": "01/07/2025 - 31/12/2025", "end": "31/12/2025"},
    {"key": "p2", "label": "01/01/2026 - 30/06/2026", "end": "30/06/2026"},
    {"key": "p3", "label": "01/07/2026 - 31/12/2026", "end": "31/12/2026"},
    {"key": "p4", "label": "01/01/2027 - 31/05/2027", "end": "31/05/2027"},
]

STATUS_OPTIONS = ["", "In corso", "Conclusa"]
BENEFICIARY_RELATION_OPTIONS = [
    "",
    "Conosciuti da QuBì",
    "Nuovi beneficiari",
    "Misti",
    "Non rilevabile",
]

CATEGORY_CAPACITY = {
    "Alimentare": 5,
    "Scuola": 8,
    "Sport": 3,
    "Offerta generale": 8,
    "Azioni trasversali di coordinamento": 2,
    "Ulteriori azioni progettuali": 3,
}

ACTIVITY_CATALOG = {
    "Alimentare": [
        "Integrazione spesa",
        "Supporto alla comunità",
        "Rifornimento scaffali Hub/market e acquisto beni alimentari",
    ],
    "Scuola": [
        "Kit scuola (base, con cartella, con libri)",
        "Doposcuola",
        "Oltre la scuola (campi estivi/invernali)",
        "Sostegno educativo (es. valutazione DSA)",
        "Sostegno per logopedia, psicomotricità",
        "Sostegno per attività ricreative/tempo libero",
    ],
    "Sport": [
        "Erogazione voucher per attività sportiva",
    ],
    "Offerta generale": [
        "Visite mediche specialistiche",
        "Certificato medico per sport",
        "Mediazione linguistico-culturale",
        "Interventi educativi individuali per bambini con bisogni speciali",
        "Sostegno psicologico",
        "Budget sostegno diretto alle famiglie",
    ],
    "Azioni trasversali di coordinamento": [
        "Coordinamento, comunicazione",
        "Gestione amministrativa",
    ],
    "Ulteriori azioni progettuali": [],
}

COST_PARAMETERS = {
    "Integrazione spesa": "Max 120 €/nucleo/mese; + max 30 €/componente aggiuntivo/mese",
    "Supporto alla comunità": "Max 170 €/famiglia/mese",
    "Rifornimento scaffali Hub/market e acquisto beni alimentari": "Max 10.000 €/mese",
    "Kit scuola (base)": "Max 50 €/bambino",
    "Kit scuola con cartella": "Max 100 €/bambino",
    "Kit scuola con libri": "Max 300 €/bambino",
    "Doposcuola": "Max 27 €/ora",
    "Oltre la scuola - campus estivo/invernale": "Max 150 €/bambino/settimana",
    "Sostegno educativo (es. valutazione DSA)": "Max 600 €/bambino/anno",
    "Logopedia e psicomotricità": "Max 1.000 €/bambino",
    "Attività ricreative/tempo libero": "Max 400 €/bambino/anno",
    "Voucher per attività sportiva": "Max 500 €/bambino/anno",
    "Visite mediche specialistiche": "Max 150 €",
    "Certificato medico per sport": "Max 70 €",
    "Mediazione linguistico-culturale": "Max 35 €/ora",
    "Interventi educativi individuali per bambini con bisogni speciali": "Max 27 €/ora",
    "Sostegno psicologico": "Max 200 €/bambino/mese",
    "Budget sostegno diretto alle famiglie": "Max 400 €/mese",
}

EXPENSE_ACTIVITY_OPTIONS = [""] + list(COST_PARAMETERS.keys()) + ["Altro"]
