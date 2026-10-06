# MedCheck

**Dit is een onderzoeks- en onderwijsprototype, geen medisch hulpmiddel. Het is niet
klinisch gevalideerd en werkt in deze repository uitsluitend met synthetische data.**
Zie `docs/INTENDED_USE.md` voor de volledige scope en `SAFETY.md` voor de voorwaarden
waaronder een organisatie dit zou mogen inzetten.

Vergelijkt twee medicatieoverzichten en toont discrepanties, ter ondersteuning van
medicatieverificatie bij zorgoverdracht. Primaire gebruiker: apothekersassistent, met
escalatie naar apotheker. De tool detecteert en presenteert verschillen; hij beslist niet
en adviseert geen behandeling (zie ADR-001: de diff-engine is deterministische code, AI
doet alleen extractie en normalisatie).

## Draaien

Zie `SETUP.md` voor installatie en het starten van de Streamlit-UI (`ui/app.py`).

```
pip install -r requirements.txt
pytest
```

## Projectstatus

**Pre-1.0.** Output en interface kunnen breken tussen versies. Zie `CHANGELOG.md` voor
wat er per versie is veranderd, en `docs/BACKLOG.md` voor wat nog open staat.

## Meer lezen

- Wat het doet en niet doet: `docs/INTENDED_USE.md`
- Onder welke voorwaarden een organisatie dit zou mogen inzetten: `SAFETY.md`
- Gemeten prestaties op de synthetische casusset: `VALIDATION.md`
- Verwante projecten en waarin MedCheck verschilt: `RELATED_WORK.md`
- Werkafspraken voor AI-assistentie: `CLAUDE.md`
- Licentie: Apache-2.0, zie `LICENSE`

Bart Pouls · Radboudumc
