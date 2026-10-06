# Veiligheid en inzetvoorwaarden

MedCheck is een onderzoeks- en onderwijsprototype (zie `docs/INTENDED_USE.md`), niet
gecertificeerd, niet klinisch gevalideerd. Dit document beschrijft onder welke voorwaarden
een organisatie het toch zou mogen inzetten — en wat daarvoor eerst moet gebeuren.

## Automation bias — het grootste risico, niet de kleinste bug

Een tool die de meeste discrepanties vindt, wekt vertrouwen. Dat vertrouwen maakt de
gebruiker minder scherp op precies de gevallen die de tool mist. Dit werkt averechts: hoe
beter MedCheck aanvoelt, hoe groter het risico dat een apothekersassistent een ongematchte
of gemiste regel over het hoofd ziet omdat "de tool het toch zou hebben gevonden."

Concreet:
- Een discrepantie die de engine niet detecteert (bijv. omdat twee regels niet matchten,
  zie `VALIDATION.md`) is onzichtbaar in de output — er staat geen waarschuwing "dit kan ik
  gemist hebben" naast elke schone lijst.
- `requires_escalation = False` betekent "geen van de geprogrammeerde triggers is geraakt",
  niet "een apotheker heeft dit beoordeeld en akkoord bevonden." Zie CLAUDE.md's
  escalatieregels voor de volledige, eindige lijst triggers — alles daarbuiten valt terug op
  menselijke waakzaamheid.
- Context (labwaarde, allergie, contra-indicatie) die MedCheck toont maar niet interpreteert
  (RISK_ANALYSIS.md R14) is een tweede vorm van hetzelfde risico: getoond ≠ beoordeeld.

**Mitigatie is procedureel, niet technisch op te lossen door "de tool beter te maken":**
periodieke steekproefcontrole door een apotheker op door MedCheck als "geen discrepantie"
gemarkeerde overzichten, juist om de trainingsscherpte van assistenten te bewaken.

## Wat een overnemende partij zelf moet doen vóór inzet

1. **Eigen validatieset draaien.** De cijfers in `VALIDATION.md` gelden voor de 25
   synthetische casus van dit project, niet voor een andere instelling. Reproduceer met
   `python scripts/validate.py` op eigen (geanonimiseerde) testdata vóór gebruik.
2. **Versie van de G-standaard vastleggen.** `locales/nl/brands.py` bevat NL-specifieke
   merknaam→stofnaam-mapping. Documenteer welke G-standaard-versie hieraan ten grondslag
   ligt en met welke cadans die bijgewerkt wordt — een verouderde mapping geeft stille,
   foutieve normalisatie.
3. **Escalatieroute naar apotheker expliciet inrichten.** De triage-regels in
   `triage/escalation.py` bepalen `requires_escalation`, maar wat er daadwerkelijk gebeurt
   ná die vlag (wie ziet het, binnen welke termijn, wat als niemand reageert) is
   organisatorisch, niet iets wat de code regelt.
4. **Ongematchte regels handmatig controleren — verplicht, niet optioneel.** Een regel die
   de matcher niet aan de andere lijst kan koppelen (andere schrijfwijze, ontbrekende
   ATC-code, onvolledige extractie) verdwijnt niet uit de vergelijking, maar wordt ook niet
   automatisch als risico gemarkeerd tenzij hij als STOPPED/ADDED wordt herkend. Behandel elk
   ongematcht paar als het gevaarlijke residu, niet als ruis — zie de UI-tekst bij nul
   discrepanties.
5. **Eigen DPIA en rechtsgrondslag bij gebruik van echte patiëntdata.** Zie ADR-002 voor de
   voorwaarden. Dit project zelf gebruikt in de publieke repository uitsluitend synthetische
   data; elke afwijking daarvan is de verantwoordelijkheid van de partij die het inzet.

## Wat dit document niet is

Geen vervanging voor een risicoanalyse volgens een erkend kader (bijv. ISO 14971) als een
partij dit richting een MDR-traject wil bewegen. Zie `docs/RISK_ANALYSIS.md` voor het
huidige, projectinterne risicoregister — dat is een werkdocument, geen formele
risicomanagementfile.
