# Instructieprompts: alternatieve brondocument-formaten per casusgroep

**Doel:** Fase 2 (extractie-evaluatie) heeft brondocumenten nodig in meerdere formaten/lay-outs
— niet alleen CSV — om te testen of extractie robuust is tegen presentatievariatie. Dit levert
géén nieuwe klinische inhoud op: de medicatiegegevens komen 1-op-1 uit de al bestaande,
geverifieerde `truth_a.json`/`truth_b.json` per casus. De prompts hieronder vragen een AI alleen
om diezelfde gegevens in een ander document-formaat te *gieten*.

**Waarom dit geen nieuwe ground-truth-generatie is:** de klinische waarheid (welk middel, welke
sterkte, welke frequentie) staat al vast en is niet opnieuw AI-gegenereerd. Wat je nog wél
handmatig moet checken per output: **visuele/tekstuele getrouwheid** — komt het gerenderde
document exact overeen met de brongegevens hieronder, zonder toegevoegde, weggelaten of
gewijzigde waarden? Dat is een lichtere check dan medisch-inhoudelijke verificatie, maar wel
verplicht vóór gebruik in evaluatie.

**Bestandslocatie-suggestie:** zet de output per casus in een submap `formats/`, bv.
`data/synthetic/casus/001-merknaam-vs-stofnaam/formats/source_a.csv` — zo blijven de bestaande
`source_a.csv`/`source_b.csv` (fase 1, diff-engine-fixtures) onaangeroerd.

**Vaste regels voor elke prompt (herhaald per blok zodat ze los te plakken zijn):**
- Geen echte patiëntdata. Patiëntnaam altijd `Testpatiënt 0XX` (XX = casusnummer), geboortedatum
  fictief bv. `01-01-1955`, geen BSN of duidelijk fictief (`000000000`).
- Geen nieuwe of gewijzigde klinische waarden — alleen herformatteren van de gegeven regels.
- Bij twijfel over lay-out: kies iets dat op een echt Nederlands apotheeksysteem/EPD-export lijkt,
  geen abstract sjabloon.

---

## Groep 1 — casus 001–005 · formaat: CSV, alternatieve kolomvolgorde + Engelse headers

**Instructieprompt:**

> Genereer voor onderstaande 5 casus een alternatieve CSV-weergave van source_a en source_b.
> Gebruik Engelstalige kolomkoppen in een andere volgorde dan gebruikelijk:
> `drug_name, route, dose_form, frequency, strength, prn_flag, start_date, stop_date, stop_reason`
> (dus sterkte en vorm verderop, niet vooraan — test of de parser kolomvolgorde-onafhankelijk is).
> Vul per regel exact de onderstaande gegevens in, geen andere waarden. Output: `source_a.csv` en
> `source_b.csv` per casus, UTF-8, met header.
>
> **001-merknaam-vs-stofnaam**
> A: Emcor 5mg tablet 1dd1 oraal | Selokeen 50mg tablet 2dd1 oraal | Coversyl 4mg tablet 1dd1 oraal
> | Ascal 80mg tablet 1dd1 oraal | Zocor 20mg tablet 1dd1 's avonds oraal
> B: bisoprolol 5mg tablet 1dd1 oraal | metoprolol 100mg tablet 2dd1 oraal | perindopril 4mg
> tablet 1dd1 oraal | acetylsalicylzuur 80mg tablet 1dd1 oraal | simvastatine 20mg tablet 1dd1
> 's avonds oraal
>
> **002-combinatiepreparaat**
> A: Exforge 5/80mg tablet 1dd1 oraal
> B: amlodipine 5mg tablet 1dd1 oraal | valsartan 80mg tablet 1dd1 oraal
>
> **003-titratie-prednisolon**
> A: prednisolon — afbouwschema 30mg week1, 20mg week2, 10mg week3 (nu week 3), tablet, 1dd1, oraal
> B: prednisolon 10mg tablet 1dd1 oraal
>
> **004-zo-nodig-vs-vast**
> A: oxycodon 5mg tablet, zo nodig max 4dd1, oraal, prn=ja
> B: oxycodon 5mg tablet 2dd1 oraal, prn=nee
>
> **005-andere-toedieningsvorm**
> A: paracetamol 500mg tablet, 2 tabletten, 4dd1, oraal
> B: paracetamol 24mg/ml drank, 40ml, 4dd1, oraal

---

## Groep 2 — casus 006–010 · formaat: PDF, vrije-tekst ontslagbrief-stijl

**Instructieprompt:**

> Genereer voor onderstaande 5 casus een PDF per source (A en B) in de stijl van een Nederlandse
> ontslagbrief: lopende tekst onder het kopje "Medicatie bij ontslag" / "Actuele medicatie",
> per middel één zin, geen tabel. Briefhoofd met fictieve praktijknaam, `Testpatiënt 0XX`,
> geboortedatum, datum brief. Gebruik exact onderstaande gegevens, verzin geen extra medicatie.
>
> **006-dubbelmedicatie-atc4**
> A: ibuprofen 400mg, 3dd1
> B: ibuprofen 400mg, 3dd1; diclofenac 50mg, 3dd1
>
> **007-gestopt-zonder-reden**
> A: methotrexaat 10mg, 1x per week
> B: (geen methotrexaat vermeld — leeg medicatieoverzicht op dit punt)
>
> **008-geen-discrepantie-cardiovasculair**
> A: Bisoprolol 5mg 1dd1; Atorvastatine 40mg 1dd1 's avonds; Metformine 850mg 2dd1
> B: bisoprolol 5 mg 1dd1; atorvastatine 40 mg 1dd1 's avonds; metformine 850 mg 2dd1
>
> **009-geen-discrepantie-psychiatrie**
> A: lithiumcarbonaat 400mg 2dd1; sertraline 100mg 1dd1
> B: lithiumcarbonaat 400mg 2dd1; sertraline 100mg 1dd1 (identiek aan A)
>
> **010-geen-discrepantie-inhalatie**
> A: Symbicort 160/4,5 microgram, 2 inhalaties, 2dd1
> B: Symbicort 160/4,5 mcg, 2 inhalaties, 2dd1 (identiek aan A, andere eenheidsnotatie)

---

## Groep 3 — casus 011–015 · formaat: afbeelding (PNG), EPD-schermafbeelding-stijl

**Instructieprompt:**

> Genereer voor onderstaande 5 casus een PNG-schermafbeelding per source (A en B): een fictief
> EPD/apotheeksysteem-scherm met venstertitel ("Medicatieoverzicht"), een tabel met kolommen
> Middel / Sterkte / Vorm / Dosering / Frequentie, en `Testpatiënt 0XX` in de kop. Normale
> schermresolutie, leesbaar lettertype, geen ruis — dit test het "schone" vision-pad.
> Gebruik exact onderstaande gegevens.
>
> **011-nieuw-middel-toegevoegd**
> A: amoxicilline 500mg, 3dd1
> B: amoxicilline 500mg, 3dd1; flucloxacilline 500mg, 4dd1 (nieuw gestart)
>
> **012-gestopt-met-reden**
> A: lisinopril 10mg, 1dd1 — gestopt 01-02-2026, reden: bijwerking prikkelhoest
> B: (lisinopril niet meer vermeld)
>
> **013-frequentiewijziging**
> A: metoprolol 50mg, 1dd1
> B: metoprolol 50mg, 2dd1
>
> **014-sterktewijziging**
> A: furosemide 40mg, 1dd1
> B: furosemide 80mg, 1dd1
>
> **015-frequentienotatie-varianten**
> A: levothyroxine 100 microgram, "1x per dag, 's ochtends nuchter"; atorvastatine 20mg,
> "'s avonds 1 tablet"
> B: levothyroxine 100mcg, 1dd1; atorvastatine 20mg, 1dd1 's avonds

---

## Groep 4 — casus 016–020 · formaat: afbeelding (PNG/JPG), "foto van uitdraai" met ruis

**Instructieprompt:**

> Genereer voor onderstaande 5 casus een foto-achtige afbeelding per source (A en B): een
> geprinte medicatielijst gefotografeerd op een bureau — lichte scheve hoek (2-6°), zachte
> schaduw langs één rand, licht wazig/lagere resolutie dan groep 3. Dit test het vision-pad
> onder realistische, niet-ideale omstandigheden (vergelijk met het "foto van verpakking"-idee
> uit BACKLOG.md nice-to-have). Inhoud blijft exact leesbaar, alleen de fotokwaliteit is minder.
> Gebruik exact onderstaande gegevens.
>
> **016-om-de-12-uur-equivalentie**
> A: amoxicilline 500mg, om de 8 uur
> B: amoxicilline 500mg, 3dd1
>
> **017-insulineschema-meervoudig**
> A: insuline glargine 100E/ml, 20 eenheden, 1dd1, subcutaan; insuline aspart 100E/ml,
> 8 eenheden, 3dd1, subcutaan
> B: insuline glargine 100E/ml, 20 eenheden, 1dd1, subcutaan; insuline aspart 100E/ml,
> 12 eenheden, 3dd1, subcutaan
>
> **018-anticoagulantia-switch**
> A: acenocoumarol 1mg, volgens doseerschema — gestopt 05-02-2026, reden: switch naar DOAC
> B: rivaroxaban 20mg, 1dd1 — gestart 05-02-2026
>
> **019-lithium-risicomedicatie**
> A: lithiumcarbonaat 400mg, 1 tablet, 2dd1
> B: lithiumcarbonaat 400mg, 2 tabletten, 2dd1
>
> **020-digoxine-dosiswijziging**
> A: digoxine 0,25mg, 1dd1
> B: digoxine 0,125mg, 1dd1

---

## Groep 5 — casus 021–025 · formaat: PDF, verpleegkundige overdracht/telegramstijl

**Instructieprompt:**

> Genereer voor onderstaande 5 casus een PDF per source (A en B) in telegramstijl zoals een
> verpleegkundige overdrachtsnotitie: korte regels, veel afkortingen (mcg, u = uur, tab = tablet,
> sc = subcutaan), geen volledige zinnen, geen tabel. `Testpatiënt 0XX` bovenaan. Gebruik exact
> onderstaande gegevens, verzin geen afkortingen die de waarde zouden kunnen veranderen.
>
> **021-opioid-titratie**
> A: fentanyl 25mcg/u pleister, q72u, transdermaal
> B: fentanyl 50mcg/u pleister, q72u, transdermaal
>
> **022-methotrexaat-weekdosering-fout**
> A: methotrexaat 10mg, 1x/week (elke maandag)
> B: methotrexaat 10mg, 1dd1 — **laat deze fout letterlijk staan, dit is de opzettelijke
> overdrachtsfout die de casus test**
>
> **023-duplicaat-benzodiazepines**
> A: oxazepam 10mg, 1dd1 's avonds
> B: oxazepam 10mg, 1dd1 's avonds; temazepam 10mg, 1dd1 's avonds (nieuw gestart)
>
> **024-meervoudige-discrepanties-gemengd**
> A: amlodipine 5mg 1dd1; simvastatine 40mg 1dd1 's avonds; pantoprazol 40mg 1dd1 — gestopt
> 03-02-2026, geen reden; metformine 500mg 2dd1
> B: amlodipine 10mg 1dd1; simvastatine 40mg 1dd1 's avonds; metformine 500mg 2dd1; candesartan
> 8mg 1dd1 — gestart 10-02-2026
>
> **025-eenheidsnormalisatie-mcg-mg**
> A: levothyroxine 0,1mg, 1dd1
> B: levothyroxine 100 microgram, 1dd1

---

## Na ontvangst van de output

1. Check per bestand: staan alle en alléén de bovenstaande waarden erin (geen toegevoegde/
   weggelaten regel, geen gewijzigd getal)?
2. Zet goedgekeurde bestanden in `data/synthetic/casus/<casus-id>/formats/`.
3. `expected_diff.json`, `truth_a.json`, `truth_b.json` blijven ongewijzigd — die horen bij de
   klinische waarheid, niet bij de presentatievorm.
