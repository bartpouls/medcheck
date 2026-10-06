"""Landelijke terminologie voor Nederlandse medicatieoverzichten -- gebaseerd op de
NHG/KNMP-begrippenset achter Nictiz' AMO/Medicatieproces (MP9)-informatiestandaard.

Let op wat deze standaard wél en niét regelt (zie JOURNEY.md 2026-08-26 sessie 9): MP9
standaardiseert het datamodel en de elektronische uitwisseling (HL7v3/FHIR) tussen
systemen, NIET de lay-out van een afgedrukt/PDF-medicatieoverzicht. Elke EPD-/
apotheekleverancier rendert zijn eigen pagina. Dit bestand is dus geen "MP9-parser"
maar een brede, EXPLICIETE synoniemenlijst voor labels die feitelijk voorkomen op
Nederlandse medicatieoverzichten, aangevuld met de MP9-begrippenset zodat de lijst niet
beperkt blijft tot de twee bronnen die nu bekend zijn (HIX, CGM Apotheek).

Nog steeds CLAUDE.md regel 4: een label dat hier niet in staat, wordt niet gegokt --
de generieke parser (locales/nl/pdf_parser.py) faalt dan hard. Breder vocabulaire is geen
vrijbrief om te raden, alleen om meer bekende synoniemen te herkennen dan één letterlijk
documentsjabloon toestond."""

SECTION_MARKERS = [
    "actueel medicatieoverzicht",
    "medicatieoverzicht",
    "actuele medicatie",
    "huidige medicatie",
    "voorgeschreven medicatie",
    "geneesmiddelen",
    "artsenverklaring",
    # ASP (Apotheek Woerden B.V.), casus 028: sectietitel "Medicatie (Voorschriften/
    # Afleveringen)" staat als eigen rij BOVEN de kolomkoprij, niet erin samengevoegd --
    # zie _parse_table in locales/nl/pdf_parser.py voor hoe dat nu wordt opgevangen.
    # Nog NIET geverifieerd tegen de echte PDF-bytes (alleen tegen tekst uit een
    # chat-upload), zie data/local/casus/028-praktijkcasus-asp-testpat/notes.md.
    "voorschriften/ afleveringen",
]

# Volgorde binnen elke lijst: langste/specifiekste synoniem eerst, relevant voor
# substring-matching in _find_labels_in_text (locales/nl/pdf_parser.py).
COLUMN_LABELS: dict[str, list[str]] = {
    # Bewust ALLEEN generieke-naam-synoniemen -- "productnaam"/"handelsnaam" duiden op
    # de merknaam-kolom (een ander veld, zie models.py:MedicationLine.brand), niet op
    # de stofnaam-kolom waar matching/ATC-opzoeking op draait. Een bron met uitsluitend
    # een merknaam-kolom (geen aparte stofnaam-kolom) valt hier bewust nog buiten --
    # nieuw geval, geen gok (CLAUDE.md regel 4).
    "substance": ["werkzame stof", "generieke naam", "stofnaam", "middel", "geneesmiddel"],
    "strength": ["sterkte", "concentratie"],
    "form": ["farmaceutische vorm", "toedieningsvorm", "vorm"],
    "dose": ["dosering", "hoeveelheid", "dosis", "aantal"],
    # "tijden" (klokttijden van inname, bv. "07:00") hoort hier bewust NIET bij --
    # dat is een ander concept dan doseerfrequentie en staat in HIX in een eigen,
    # ongebruikte kolom (zie locales/nl/pdf_parser.py's kolomherkenning).
    "frequency": ["doseerschema", "frequentie", "innamemoment"],
    "route": ["toedieningsweg", "toedieningswijze", "route", "tw"],
    "start_date": ["ingangsdatum", "startdatum", "sinds"],
    "stop_date": ["stopdatum", "einddatum", "gestopt"],
    "stop_reason": ["reden staken", "reden stop", "stopreden"],
    "prescriber": ["voorschrijver", "behandelaar", "arts"],
    "prn": ["zo nodig", "z.n.", "indien nodig"],
}

# Toedieningsvorm-woorden zoals ze feitelijk in celtekst voorkomen (regex-alternatief-
# klaar), inclusief bekende meervouds-/toevoegingsvarianten. Nieuw bronsysteem met een
# vorm die hier niet in staat: hard falen, niet gokken (CLAUDE.md regel 4) -- uitbreiden
# is een bewuste, kleine toevoeging aan deze lijst.
VORM_PATTERNS = [
    # "msr" (maagsapresistent) toegevoegd n.a.v. het ASP-patiëntportaaloverzicht,
    # zie locales/nl/patient_portal_parser.py.
    r"tablet(?:ten)?(?:\s+(?:mga|msr))?",
    r"drank",
    r"capsule(?:s)?",
    r"inj\s+pen",
    r"zetpil(?:len)?",
    r"pleister(?:s)?",
]

# Bekende zoutvorm-/toevoegingswoorden tussen stofnaam en vorm (bv. "amitriptyline
# HCL tablet") die NIET bij de stofnaam horen voor ATC-opzoeking. Klein en expliciet,
# net als COMBO_BRANDS in locales/nl/brands.py.
SALT_WOORDEN = ["hcl", "natrium", "kalium", "succinaat", "tartraat", "mesilaat", "sulfaat", "fumaraat", "maleaat", "citraat"]

# Woorden voor "keer" in een doseerfrequentie (bv. "3 x per dag", "3 maal per dag").
# Klein en expliciet, zelfde patroon als VORM_PATTERNS hierboven -- "maal" toegevoegd
# n.a.v. ASP (Apotheek Woerden B.V.), casus 028.
FREQUENCY_TIMES_WOORDEN = ["x", "maal"]

# Letterlijke Dosering-celwaarden die "geen dosering geregistreerd" betekenen, i.p.v.
# een onherkend patroon dat als fout zou moeten gelden (CLAUDE.md regel 4: expliciete,
# gedocumenteerde waarde, geen gok -- en zeker geen stille drop, zie SAFETY.md over
# automation bias). Bron: ASP (Apotheek Woerden B.V.), casus 028 -- daar staat "."
# voor drie van de vier medicijnen in de Dosering-kolom.
EMPTY_DOSE_MARKERS = ["."]

# Vorm -> gebruikelijke toedieningsweg. Structurele afleiding (geen klinisch oordeel,
# zie parsing/cgm_apotheek.py's oorspronkelijke onderbouwing) voor bronnen zonder
# expliciete route-kolom. Onbekende/vertaalde vorm: route blijft "" (geen gok).
ROUTE_BY_VORM = {
    "tablet": "oraal",
    "tabletten": "oraal",
    "tablet mga": "oraal",
    "tablet msr": "oraal",
    "drank": "oraal",
    "capsule": "oraal",
    "capsules": "oraal",
    "zetpil": "rectaal",
    "zetpillen": "rectaal",
    "pleister": "transdermaal",
    "pleisters": "transdermaal",
}
