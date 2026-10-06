# Casus 005 — identiek middel, andere toedieningsvorm

**Edge case:** paracetamol als tablet (lijst A) tegenover drank (lijst B), qua dosis
nagenoeg gelijkwaardig (1000mg vs 960mg).

**Verwacht:** 1 discrepantie, FORM_CHANGE, lage severity, geen escalatie (geen risicomedicatie,
dosis niet wezenlijk anders).

**Test wat:** form-veld in matching; niet automatisch ook als DOSE_CHANGE classificeren
wanneer het onderliggende verschil door vorm/toedieningswijze komt.
