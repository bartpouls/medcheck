# ADR-003 — Patiëntidentiteitscontrole vóór de medicatie-diff

Datum: 2026-08-26 · Status: geaccepteerd

## Context

MedCheck vergelijkt twee medicatieoverzichten van "dezelfde patiënt uit verschillende
bronnen" (INTENDED_USE.md §1). Tot nu toe werd die aanname nergens gecontroleerd: de
diff-engine matcht en vergelijkt medicatieregels, maar niets verifieert dat bron A en
bron B daadwerkelijk over één patiënt gaan. Bij zorgoverdracht is een verwisseling
tussen twee patiëntendossiers een reëel en klinisch relevant risico — de diff-engine
zou dan plausibel ogende, maar volledig onzinnige discrepanties presenteren.

## Overwogen opties

1. Geen patiëntidentiteitscontrole — buiten scope, de gebruiker is toch al verplicht
   te verifiëren welke twee bronnen ze koppelt.
2. BSN-only matching, hard falen als BSN ontbreekt of niet overeenkomt.
3. BSN primair (met 11-proef-validatie), naam + geboortedatum als fallback zodra BSN
   ontbreekt of ongeldig is; bij mismatch of ontbrekende identificatie nooit blokkeren,
   altijd een prominente, expliciet onderscheiden waarschuwing tonen.

## Besluit

Optie 3. BSN is voor de NL-situatie de sterkste beschikbare identificator en krijgt
voorkeur; de 11-proef (zelfde principe als de bankrekening-11-proef) vangt typo's/
OCR-fouten in een los BSN, maar bewijst niets over gelijkheid tussen twee BSN's — die
vergelijking is gewone stringgelijkheid, uitgevoerd in `identity.py`. Naam +
geboortedatum is een bewust zwakkere fallback: die twee identiceren geen tweeling, en
dat wordt niet met een zelfbedachte tiebreaker "opgelost" — in plaats daarvan blijft de
onzekerheid zichtbaar (consistent met CLAUDE.md regel 3/4: onzekerheid tonen, geen
stille aannames).

Bij twijfel wordt nooit geblokkeerd: Bart's expliciete keuze (2026-08-26) is doorlaten
met een prominente waarschuwing, omdat MedCheck geen autonome beslissingen neemt
(INTENDED_USE.md §5) — de apothekersassistent/apotheker beoordeelt of bron A en bron B
werkelijk dezelfde patiënt betreffen. "BSN niet gevonden" en "BSN ongeldig (11-proef
gefaald)" zijn bewust twee aparte waarschuwingscodes, geen samengevoegde "kon niet
valideren" — dat maakt zichtbaar of het om ontbrekende brondata gaat of om een
waarschijnlijke overtype-/OCR-fout.

Architecturaal: BSN-validatie (`locales/nl/patient_id.py`) is een NL-landmodule, net als
merknaamresolutie in `locales/nl/brands.py` — BSN heeft geen equivalent in andere
Europese landen. De generieke identiteitsvergelijking (`identity.py`, top-level) kent
geen BSN-specifieke logica; ze vergelijkt alleen al-gevalideerde strings, zodat een
toekomstige tweede landmodule zijn eigen primaire identificator kan leveren zonder
`identity.py` te hoeven aanpassen (zelfde scheiding als `matching.py` t.o.v.
`locales/nl/brands.py`).

## Gevolgen

+ Een verwisseling tussen twee patiëntendossiers wordt zichtbaar vóórdat de gebruiker
  naar de medicatie-diff kijkt, in plaats van pas (of nooit) op te vallen tussen de
  discrepanties door.
+ "Niet gevonden" vs. "ongeldig" als aparte codes maakt de vervolgstap voor de
  gebruiker concreet (brondata aanvullen vs. een vermoedelijke typefout controleren).
- Nog geen dekking voor het vocab-gedreven PDF-pad en het briefsjabloon-PDF-pad
  (`locales/nl/pdf_parser.py`, `locales/nl/prose_parser.py`) — die leveren nu altijd
  "geen identificatie mogelijk" op. Niet blokkerend (de controle waarschuwt toch al
  niet-blokkerend), wel een open BACKLOG-punt.
- BSN is een bijzonder identificerend nummer onder AVG/UAVG. Zodra een gebruiker per
  ongeluk een echt BSN invoert (bijv. in een test met kopieer-geplakte praktijkdata),
  ligt dat nu in het parse-pad. Dit raakt CLAUDE.md regel 1 ("geen echte patiëntdata")
  onverkort — de synthetische casusset gebruikt uitsluitend publiek bekende
  test-BSN's (bv. "111222333"), nooit uit een geldigheidscontrole afgeleide willekeurige
  nummers die toevallig een bestaand BSN zouden kunnen zijn.
- Naam + geboortedatum als fallback lost het tweelingrisico niet op — bewust
  geaccepteerd restrisico, zichtbaar gemaakt via de waarschuwingstekst in de UI, niet
  weggenomen door extra velden te verzinnen.

## Relatie tot intended use en risicoanalyse

Draagt bij aan het beoogd doel uit INTENDED_USE.md §1 ("dezelfde patiënt uit
verschillende bronnen") — dat was tot nu toe een ongecontroleerde aanname. Vereist een
§4-aanvulling in INTENDED_USE.md (zie changelog-entry v1.1, nog geen akkoord Bart
Pouls) en een BACKLOG-punt voor de resterende PDF-paden.
