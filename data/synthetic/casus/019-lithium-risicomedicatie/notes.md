# Casus 019 — lithium dosiswijziging

**Edge case:** lithiumcarbonaat (smalle therapeutische breedte) met een dosiswijziging tussen
lijst A en lijst B. In tegenstelling tot casus 009 (lithium zonder discrepantie) triggert dit
hier onvoorwaardelijk escalatie: risicomedicatie + echte discrepantie.

**Verwacht:** 1 discrepantie, DOSE_CHANGE, hoog, verplichte escalatie.

**Test wat:** samenspel van risicoklasse-escalatie en discrepantie-detectie.
