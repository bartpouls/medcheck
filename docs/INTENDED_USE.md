# Intended Use Statement — MedCheck

Versie 1.1 · definitief — akkoord Bart Pouls · 2026-08-26 · Bart Pouls

## 1. Beoogd doel

MedCheck vergelijkt twee medicatieoverzichten van dezelfde patiënt uit verschillende bronnen en
presenteert de gevonden verschillen gestructureerd, geprioriteerd en verifieerbaar, ter
ondersteuning van de handmatige medicatieverificatie bij zorgoverdracht.

Naast de medicatieregels zelf mag relevante contextinformatie worden meegenomen voor zover die
van belang is bij de medicatiecontrole — zoals labwaarden, allergieën en contra-indicaties.
MedCheck toont deze gegevens als context naast de medicatievergelijking; het beoordeelt ze niet
en trekt er geen klinische conclusie uit (zie 5).

## 2. Beoogde gebruiker

Apothekersassistent, werkzaam in ziekenhuis- of openbare apotheek, met escalatiemogelijkheid
naar een apotheker. De gebruiker is bevoegd en getraind in medicatieverificatie. MedCheck
vervangt die bevoegdheid niet.

## 3. Klinische context

Opname, ontslag of overdracht tussen zorgverleners, waarbij meerdere medicatiebronnen naast
elkaar bestaan (apotheeksysteem, EPD, ontslagbrief, patiëntopgave, medicatierol).

## 4. Wat MedCheck wél doet

- Vóór de medicatievergelijking controleren of bron A en bron B over dezelfde patiënt
  gaan: BSN primair (met 11-proef-validatie, NL-specifiek), naam + geboortedatum als
  fallback zodra BSN in één van beide bronnen ontbreekt of ongeldig is. Bij mismatch of
  ontbrekende identificatie wordt niet geblokkeerd — MedCheck toont een prominente,
  expliciet onderscheiden waarschuwing ("niet gevonden" vs. "ongeldig" vs. "komt niet
  overeen") en laat de beoordeling aan de gebruiker (zie ADR-003). Naam + geboortedatum
  onderscheidt geen tweeling — dat restrisico wordt zichtbaar gemaakt, niet opgelost.
- Ongestructureerde medicatieoverzichten omzetten naar een gestructureerd formaat
- Middelen normaliseren naar stofnaam en ATC-code
- Verschillen detecteren en classificeren (toegevoegd, gestopt, dosis, frequentie, vorm,
  sterkte, dubbelmedicatie)
- Onderscheid maken tussen doseerinstructie (bijv. frequentie en hoeveelheid, zoals "3x daags 1
  tablet") en gebruiksinstructie (bijv. innamewijze, zoals "met water innemen"); alleen een
  verschil in doseerinstructie geldt als discrepantie (zie 5). Een nieuw toegevoegd middel, een
  gestopt middel en een sterktewijziging gelden altijd als discrepantie, los van dit onderscheid
- Elke gevonden discrepantie presenteren volgens een was-wordt principe: de eerdere waarde en de
  nieuwe waarde naast elkaar, niet alleen de nieuwe stand
- Relevante niet-medicatiegegevens tonen als context bij de vergelijking, zoals labwaarden,
  allergieën en contra-indicaties
- Verschillen prioriteren op basis van vooraf gedefinieerde risicoklassen
- Onzekerheid in de eigen extractie expliciet markeren
- Een verificatieverslag genereren met wie welk verschil wanneer heeft beoordeeld

## 5. Wat MedCheck expliciet NIET doet

- Geen oordeel of een verschil bedoeld dan wel onbedoeld is — dat is ter beoordeling aan de
  zorgprofessional/gebruiker
- Geen discrepantie registreren op een verschil in gebruiksinstructie alleen (bijv. ontbreken of
  toevoegen van "met water innemen") zolang de doseerinstructie ongewijzigd is — dat heeft geen
  klinische relevantie; MedCheck neemt in dat geval de meest pragmatische instructie over
- Geen behandeladvies, doseeradvies of interactiebeoordeling
- Geen beoordeling van getoonde labwaarden, allergieën of contra-indicaties — uitsluitend tonen
  als context, nooit interpreteren of wegen
- Geen vervanging van de bronsystemen of van het medicatiedossier
- Geen autonome actie: elke output vereist menselijke beoordeling en aftekening
- Geen garantie op volledigheid van de extractie; de brondocumenten blijven leidend

## 6. Beperkingen en restrisico

- Kwaliteit van de output is begrensd door kwaliteit en leesbaarheid van de brondocumenten
- Foto's van verpakkingen zónder leesbare etikettekst leveren geen doserings- of
  frequentiegegevens en zijn daarmee geen volwaardige bron voor vergelijking; foto's mét een
  leesbaar etiket (bijv. apotheeketiket met doseerinstructie) mogen wel als bron dienen, mits de
  tekst goed leesbaar is — de extractie krijgt dan de gebruikelijke confidence-score per veld
- Merknaamherkenning is landspecifiek; buiten de geconfigureerde landmodule is normalisatie
  onbetrouwbaar
- Het systeem is primair getest op synthetische data; prestaties op praktijkdata zijn niet
  vastgesteld. Er is een uitvraag voorzien naar geanonimiseerde medicatiedata uit meerdere
  Europese landen om de test- en trainingsbasis te verbreden (zie 7 en ADR-002); zolang die data
  niet is ontvangen en verwerkt, blijft deze beperking onverkort van kracht

## 7. Regulatoire positie

In de huidige vorm een onderzoeks- en demonstratieprototype. Niet in gebruik voor
patiëntenzorg. Niet CE-gemarkeerd.

Bij inzet in de zorg valt MedCheck naar verwachting onder Verordening (EU) 2017/745 (MDR) als
medisch hulpmiddel voor besluitondersteuning; classificatie waarschijnlijk klasse IIa
(regel 11). Het project wordt daarom ontwikkeld volgens MDR-principes — intended use,
risicomanagement (ISO 14971), softwarelevenscyclus (IEC 62304) — zonder dat certificering wordt
geclaimd.

Verwerking van persoonsgegevens: standaard geen — uitsluitend synthetische data. Uitzondering:
geanonimiseerde medicatiedata uit meerdere Europese landen, alleen na DPIA, een per bronland
vastgelegde rechtsgrondslag en verwerking via een van de synthetische casusset gescheiden
pijplijn (zie `docs/decisions/ADR-002-eu-medicatiedata-uitzondering.md`). Zonder die
voorwaarden blijft de hoofdregel "geen persoonsgegevens" onverkort van kracht.

## 8. Wijzigingslog

| Versie | Datum | Wijziging |
|---|---|---|
| 0.1 | 2026-07-23 | Eerste concept, datum ingevuld — nog niet definitief, zie WORKSHOP_25AUG.md punt 2 |
| 0.2 | 2026-07-23 | Onderscheid doseer- vs. gebruiksinstructie toegevoegd (verschil in gebruiksinstructie alleen = geen discrepantie); was-wordt principe voor presentatie van verschillen; niet-medicatiecontext (labwaarden, allergieën, contra-indicaties) toegevoegd als toonbare, niet-beoordeelde context; fotobeperking verfijnd (met/zonder leesbaar etiket); uitzondering op "geen echte patiëntdata" opgenomen voor geanonimiseerde EU-medicatiedata onder vier voorwaarden, zie ADR-002 — nog steeds concept, akkoord Bart Pouls vereist |
| 0.3 | 2026-07-27 | Expliciet vastgelegd dat toegevoegd/gestopt/sterktewijziging altijd discrepantie zijn, ongeacht het doseer- vs. gebruiksinstructie-onderscheid; §5 verduidelijkt naar "ter beoordeling aan de zorgprofessional/gebruiker" — nog steeds concept, akkoord Bart Pouls vereist |
| 1.0 | 2026-07-27 | Akkoord Bart Pouls op inhoud v0.3, geen verdere inhoudelijke wijziging — document definitief. Blijft onderhevig aan §7: onderzoeks-/demonstratieprototype, niet in gebruik voor patiëntenzorg, niet CE-gemarkeerd |
| 1.1 | 2026-08-26 | §4 aangevuld met patiëntidentiteitscontrole vóór de medicatie-diff (BSN primair, naam+geboortedatum-fallback, nooit blokkerend) — zie ADR-003. Akkoord Bart Pouls, document weer definitief |
