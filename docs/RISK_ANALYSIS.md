# Risicoanalyse — MedCheck

Structuur volgens ISO 14971. Versie 0.1 · concept.

Schaal ernst: 1 verwaarloosbaar · 2 gering · 3 matig · 4 ernstig · 5 katastrofaal
Schaal kans: 1 onwaarschijnlijk · 2 zelden · 3 soms · 4 waarschijnlijk · 5 frequent
Risico = ernst × kans. ≥12 = onacceptabel zonder maatregel. 6–11 = maatregel vereist.

## Startlijst (aanvullen tijdens bouw — elk incident wordt een regel)

| ID | Gevaar | Oorzaak | Gevolg voor patiënt | E | K | R | Maatregel | Rest-R |
|---|---|---|---|---|---|---|---|---|
| R01 | Middel gemist bij extractie | onleesbare PDF, meerkoloms layout | discrepantie blijft onopgemerkt | 4 | 3 | 12 | regelteller + "n regels herkend, controleer tegen bron"; brondocument naast output tonen | 8 |
| R02 | Dosering verkeerd geëxtraheerd | OCR-fout (5 vs 0,5) | verkeerde verificatiebeslissing | 5 | 3 | 15 | confidence per veld; <0,85 → verplichte escalatie; decimaal-sanity-check | 5 |
| R03 | Merknaam niet herkend als stofnaam | middel buiten landmodule | vals-positieve discrepantie of gemiste dubbelmedicatie | 4 | 3 | 12 | onbekende term → altijd flag, nooit stilzwijgend als "nieuw middel" | 6 |
| R04 | Gebruiker vertrouwt output blind | automation bias | fout wordt overgenomen | 5 | 4 | 20 | tool toont nooit "goedgekeurd"; verplichte afvinkactie per regel; bron altijd zichtbaar; training | 10 |
| R05 | Dubbelmedicatie gemist | combinatiepreparaat niet ontleed | dubbele dosering | 5 | 2 | 10 | combipreparaten ontleden naar stofnaamset; ATC-4 duplicaatcheck | 5 |
| R06 | Verkeerde patiënt/lijstkoppeling | gebruiker uploadt verkeerd bestand | volstrekt onjuiste vergelijking | 5 | 2 | 10 | bestandsnaam + geëxtraheerde patiëntidentificatie tonen, bevestiging vereist | 5 |
| R07 | "Zo nodig"-medicatie als vaste dosering geïnterpreteerd | prn niet herkend | onterechte discrepantie | 3 | 3 | 9 | prn als apart veld; prn-mismatch is eigen discrepantietype | 4 |
| R08 | Foto van doosje gebruikt als volwaardige bron | scope-misverstand | onvolledige vergelijking | 4 | 3 | 12 | fotobron krijgt eigen labeling "identificatie, geen doseerinformatie"; niet toelaatbaar als hoofdbron | 6 |
| R09 | Stille modelwijziging bij provider | ander gedrag zonder waarschuwing | onverwachte kwaliteitsval | 4 | 3 | 12 | modelversie pinnen; regressietest op casusset bij elke wijziging | 6 |
| R10 | Echte patiëntdata ingevoerd | gebruiker negeert instructie | AVG-inbreuk | 5 | 3 | 15 | waarschuwing bij upload; geen persistente opslag; disclaimer in UI | 8 |
| R11 | Onvoldoende anonimisering EU-medicatiedata | geanonimiseerde data toch herleidbaar (zeldzame combinatie middel/dosis/land) | AVG-inbreuk, patiënt herleidbaar | 5 | 2 | 10 | DPIA per bronland vóór ontvangst; rechtsgrondslag vastgelegd; anonimisering geverifieerd, ook indirecte herleidbaarheid (ADR-002) | 5 |
| R12 | Vermenging synthetische en echte data | geen technische scheiding tussen `data/synthetic/casus/` en echte data — **gematerialiseerd**: casus 026/027 (echte HIX/CGM-testpatiëntexports) stonden tot 2026-08-26 gewoon in `data/casus/`, buiten ADR-002-pijplijn | ground truth onbetrouwbaar; echte data verspreid in devomgeving/tests; risico op publicatie van instellings-/vendornaam bij open-sourcen | 4 | 2 | 8 | *gemitigeerd 2026-08-26*: casus 026/027 verplaatst naar `data/local/` (gitignored, nooit gecommit); code-review op elke plek die data inleest; nooit gecombineerd in dezelfde evaluatierun (ADR-002) | 4 |
| R13 | Klinisch relevante gebruiksinstructiewijziging genegeerd | §4/§5 v1.0: verschil in gebruiksinstructie alleen telt niet als discrepantie — regel houdt geen rekening met uitzonderingen (bv. "nuchter innemen" ↔ "met voedsel", niet fijnmalen/kauwen bij MR-tablet) | klinisch relevante wijziging blijft onopgemerkt, geen escalatie | 4 | 3 | 12 | *E/K bevestigd door Bart Pouls, 2026-08-25* — vaste lijst "altijd-relevante" gebruiksinstructietermen die wél als discrepantie tellen; overige gebruiksinstructiewijzigingen blijven zichtbaar in UI als informatief, ook zonder discrepantiestatus | 6 |
| R14 | Getoonde context niet beoordeeld | labwaarde/allergie/contra-indicatie wordt getoond maar door systeem niet geïnterpreteerd (§1/§5); gebruiker leest eroverheen | contra-indicatie of relevante labwaarde over het hoofd gezien, MedCheck wekt vals gevoel van volledigheid | 5 | 3 | 15 | *E/K bevestigd door Bart Pouls, 2026-08-25* — context altijd zichtbaar, nooit wegklikbaar zonder bevestiging; expliciete disclaimer "niet beoordeeld door MedCheck" direct bij de contextweergave | 8 |

## Restrisico-verantwoording

In te vullen na fase 2, op basis van gemeten extractie-accuratesse. Zonder meetdata geen
uitspraak over restrisico.
