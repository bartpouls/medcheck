# PDF-overzicht (handmatig testen)

Kopieën van de PDF-fixtures uit de casusmappen, herbenoemd met casusnummer + A/B in de
bestandsnaam, zodat ze los van hun mapstructuur herkenbaar zijn (bv. bij het handmatig
uploaden via `ui/app.py`). Geen nieuwe testfixtures — de canonieke bestanden blijven
`source_a.pdf`/`source_b.pdf` in de eigen casusmap; deze map wordt bewust genegeerd door
de testsuite (geen `expected_diff.json`).

Casus 009/010 zijn nog lege placeholder-PDF's (zie BACKLOG.md) — die geven terecht een
foutmelding bij het vergelijken.

Casus 026/027 staan hier bewust niet in: dat zijn echte HIX/CGM-systeemexports, geen
synthetische fixture. Hun PDF-overzicht-kopieën staan in `data/local/casus/_pdf-overzicht/`
(nooit gecommit) — zie `data/local/README.md`.

Bij een nieuwe/gewijzigde PDF-casus: kopieer 'm hier ook opnieuw, deze map wordt niet
automatisch bijgewerkt.
