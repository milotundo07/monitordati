# Monitoraggio Fondo QuBì

Web app Streamlit per compilare in modo guidato la scheda di monitoraggio dei progetti finanziati dal Fondo QuBì e scaricare l'Excel ufficiale già compilato.

## Funzioni incluse

- informazioni generali del progetto;
- attività e stato nei quattro periodi di monitoraggio;
- avanzamento economico cumulativo;
- percentuale cumulativa del contributo utilizzato;
- beneficiari previsti e raggiunti;
- controlli automatici di completezza e coerenza;
- salvataggio e riapertura del progetto tramite file JSON;
- generazione dell'Excel sulla base del modello ufficiale;
- correzione automatica dei refusi nelle date del modello originale.

## Avvio sul computer

1. Installa Python 3.11 o successivo.
2. Apri il terminale nella cartella del progetto.
3. Crea un ambiente virtuale:

```bash
python -m venv .venv
```

4. Attivalo.

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

5. Installa le dipendenze:

```bash
pip install -r requirements.txt
```

6. Avvia l'app:

```bash
streamlit run app.py
```

## Pubblicazione gratuita con GitHub e Streamlit Community Cloud

1. Crea un nuovo repository GitHub.
2. Carica tutti i file e le cartelle di questo progetto, compresa la cartella `template`.
3. Accedi a Streamlit Community Cloud con GitHub.
4. Seleziona `Create app`.
5. Indica il repository, il branch `main` e il file principale `app.py`.
6. Pubblica l'app.

GitHub conserva il codice; Streamlit esegue Python. GitHub Pages da solo non esegue questa applicazione.

## Salvataggio dei dati

Questa prima versione non usa un database. I dati restano nella sessione dell'app e possono essere conservati scaricando il file `progetto_qubi.json`. Il file può essere ricaricato in seguito dalla barra laterale.

Questa scelta evita di archiviare online dati relativi ai beneficiari. La scheda contiene solo dati aggregati, ma resta comunque prudente non inserire nomi o dati personali.

## Limiti imposti dal modello ufficiale

Il file Excel di partenza dispone di:

- 5 righe per le attività alimentari;
- 8 righe per la scuola;
- 3 righe per lo sport;
- 8 righe per l'offerta generale;
- 2 righe per il coordinamento;
- 3 righe per ulteriori attività;
- 4 righe di avanzamento economico;
- 6 righe per i beneficiari.

L'app controlla questi limiti prima di generare il file, invece di produrre un Excel deformato e sperare che nessuno se ne accorga.

## Struttura

```text
qubi_monitoraggio_app/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
├── template/
│   └── Fondo_QuBi_Scheda_Monitoraggio.xlsx
└── qubi_app/
    ├── constants.py
    ├── exporter.py
    ├── persistence.py
    ├── state.py
    └── validation.py
```
