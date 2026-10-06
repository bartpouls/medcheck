# Casus 012 — gestopt middel met reden

**Edge case:** contrast met casus 007 — hier is de stopreden wél geregistreerd
("bijwerking: hoest"). Test dat de escalatieregel "STOPPED zonder reden" niet blind afgaat
op elke STOPPED.

**Verwacht:** 1 discrepantie, STOPPED, geen verplichte escalatie (reden aanwezig, geen
risicomedicatie).

**Test wat:** onderscheid STOPPED-met-reden vs. STOPPED-zonder-reden in de escalatieregel.
