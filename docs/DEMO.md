# Demo aan een collega — snelstart

## MedCheck starten

```bash
cd "vibe coden\medcheck"
source .venv/bin/activate          # Windows: .venv\Scripts\activate
streamlit run ui/app.py
```

Opent automatisch in de browser (standaard `localhost:8501`). Titelbalk toont de
versie en fase, zie `version.py`.

## PDF's om te laten zien

Synthetische voorbeeld-PDF's (medicatieoverzicht A/B per casus) staan in:

```
data/synthetic/casus/_pdf-overzicht/
```

Bijv. `casus002-A-combinatiepreparaat.pdf` + `casus002-B-combinatiepreparaat.pdf` als
koppel. Niet elke casus heeft een PDF-variant (sommige alleen CSV) — zie
`data/synthetic/casus/_pdf-overzicht/README.md` voor welke casusnummers wel/niet.

**Let op:** alleen synthetische data tonen bij een collega buiten het project. Data in
`data/local/` valt onder de EU-datavrijgave-uitzondering (ADR-002) en is niet voor demo's.
