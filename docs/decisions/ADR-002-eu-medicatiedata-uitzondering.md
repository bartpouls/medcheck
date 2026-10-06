# ADR-002 — Uitzondering op "geen echte patiëntdata" voor EU-medicatiedata

Datum: 2026-07-23 · Status: geaccepteerd (Bart Pouls, 2026-08-25)

## Context
De trainings- en testbasis van MedCheck is uitsluitend synthetisch (`data/synthetic/casus/`). Dat begrenst
hoe goed extractie en normalisatie generaliseren naar echte, rommelige brondocumenten, en hoe
overtuigend de Europese inzetbaarheid (meerdere landmodules) onderbouwd kan worden — synthetische
casus zijn per definitie gekleurd door de aannames van wie ze genereert.

Er is behoefte aan een uitvraag naar geanonimiseerde medicatieoverzichten uit meerdere Europese
landen om die basis te verbreden. Dit staat op gespannen voet met de harde regel in `CLAUDE.md`
("geen echte patiëntdata. Ooit."), die zonder uitzondering was geformuleerd.

## Overwogen opties
1. Vasthouden aan de regel zonder uitzondering — validatie blijft beperkt tot synthetische data.
2. Ongeclausuleerd toestaan van echte data zodra "geanonimiseerd" is geclaimd.
3. Bounded uitzondering: alleen geanonimiseerde data, alleen via een gescheiden pijplijn, alleen
   na DPIA en vastgelegde rechtsgrondslag per bronland, nooit vermengd met de synthetische set.

## Besluit
Optie 3. Zie de bijgewerkte regel 1 in `CLAUDE.md` voor de vier voorwaarden.

## Gevolgen
- Positief: bredere, realistischere test-/trainingsbasis; Europese inzetbaarheid onderbouwd met
  echte diversiteit in plaats van uitsluitend synthetische aannames.
- Negatief: aanzienlijke overhead per bronland (DPIA, rechtsgrondslag varieert per lidstaat),
  trager dan direct beginnen. Nieuw foutrisico: onvoldoende anonimisering blijkt achteraf toch
  herleidbaar. Terugdraaien nadat data is binnengehaald is moeilijk — daarom blijft de default
  "nee" en is elke databron een aparte, expliciete beslissing, niet een blanco vrijbrief.
- De vier voorwaarden zijn stuk voor stuk noodzakelijk, niet optioneel: zonder DPIA is er geen
  zicht op restrisico; zonder rechtsgrondslag per land is verwerking niet rechtmatig (AVG-grondslag
  verschilt per lidstaat); zonder gescheiden pijplijn vervuilt echte data de synthetische ground
  truth (zie R12); zonder geverifieerde anonimisering is "geanonimiseerd" een aanname, geen feit.

## Relatie tot intended use en risicoanalyse
Wijzigt `docs/INTENDED_USE.md` §6 (beperkingen: synthetische data) en §7 (verwerking
persoonsgegevens). Voegt R11 (onvoldoende anonimisering) en R12 (vermenging synthetische/echte
data) toe aan `docs/RISK_ANALYSIS.md`. Elke feitelijke databron moet vóór gebruik een eigen,
concrete toets aan de vier voorwaarden documenteren — deze ADR keurt het principe goed, niet een
specifieke databron.
