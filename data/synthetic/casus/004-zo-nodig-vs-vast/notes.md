# Casus 004 — "zo nodig" tegenover vaste dosering

**Edge case:** oxycodon staat in lijst A als "zo nodig", in lijst B als vaste dosering
(2dd1) opgevoerd — een reële en risicovolle overdrachtsfout (pijnstilling die ongemerkt van
prn naar vast is gekanteld).

**Verwacht:** 1 discrepantie, FREQUENCY_CHANGE, hoge severity, verplichte escalatie
(opioïd + risicomedicatie).

**Test wat:** prn-veld correct meenemen in matching en diff, niet alleen frequency_canonical.
