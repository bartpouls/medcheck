# Casus 017 — insulineschema met meerdere insulines

**Edge case:** basaal-bolusschema (glargine 1dd + aspart 3dd) waarbij de bolusinsuline-dosis
in lijst B is gewijzigd. Twee verschillende insulines mogen niet met elkaar matchen (andere
ATC-5 ondanks zelfde ATC-4 A10A).

**Verwacht:** 1 discrepantie (DOSE_CHANGE op aspart), 0 op glargine.
Beide insulines zijn risicomedicatie -> escalatie verplicht op de gewijzigde regel.

**Test wat:** matching op ATC-5 (niet ATC-4) binnen dezelfde stofklasse insuline.
