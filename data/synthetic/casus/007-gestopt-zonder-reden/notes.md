# Casus 007 — gestopt middel zonder reden

**Edge case:** methotrexaat komt voor in lijst A, ontbreekt in lijst B, zonder geregistreerde
stopreden. Risicomedicatie + ongedocumenteerde stop is een klassiek escalatiepunt.

**Verwacht:** 1 discrepantie, STOPPED, verplichte escalatie (risicomedicatie + geen reden).

**Test wat:** STOPPED-detectie en de escalatieregel "STOPPED zonder geregistreerde reden".
