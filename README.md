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

## Hoe het bedoeld is

MedCheck is een **offline medicatie-overzichtsvergelijker**: geautomatiseerde hulp vooraf, met
menselijke controle en uitvoering daarna. Het neemt het foutgevoelige vergelijkwerk over
(deterministisch, reproduceerbaar), zodat een zorgprofessional gericht kan controleren, beoordelen
en bepalen wat er moet gebeuren. De tool beslist niets en voert niets uit: de verantwoordelijkheid
voor verificatie en vervolgactie blijft bij de mens.

- **Offline:** de huidige versie draait lokaal en bevat geen AI-aanroepen of netwerkverkeer. Je
  medicatiebestanden worden op je eigen computer verwerkt. (Streamlit kan zelf anonieme
  gebruiksstatistiek versturen; zet dat uit met
  `streamlit run ui/app.py --browser.gatherUsageStats false`.)
- **AI is gepland, niet aanwezig:** AI-extractie uit ongestructureerde bronnen staat voor een latere
  fase op de planning. Dat wordt dan een aparte, bewuste stap met een eigen veiligheidsoordeel. De
  vergelijking zelf blijft altijd deterministische code (zie ADR-001).
- **Europees opgezet:** landspecifieke onderdelen (merknamen, documentformaten, patiëntidentificatie)
  zitten in een landmodule (`locales/`). Nederland is de eerste; een nieuw land toevoegen kan
  zonder de kern te wijzigen.
- **Over verwijzingen naar een bouwlog:** de eigenaar houdt een privé-bouwlog en workshopmateriaal bij
  die niet in deze repository staan. Waar documenten daarnaar verwijzen, is het bedoeld als herkomst
  van een besluit, niet als bestand dat je zou moeten kunnen openen.

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
Victor Huiskes · Sint Maartenskliniek
