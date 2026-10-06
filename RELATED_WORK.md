# Verwant werk

Deze scan is achteraf gedaan, na de eerste werkende versie van MedCheck — niet als
onderbouwing vooraf. Dat is zelf een leermoment, niet alleen een formaliteit: een
onaf prototype is niet automatisch vrijgesteld van een positioneringscheck.

## jherskovic/MedRec

Reconciliatie-algoritme dat twee medicatielijsten met elkaar matcht. Vereist RxNorm/UMLS
als terminologie, dus VS-georiënteerd. Rond 2013 gepubliceerd, geen actief onderhoud meer
bekend.

**Verschil met MedCheck:** MedRec is gebonden aan RxNorm/UMLS en daarmee niet zonder
herbouw bruikbaar buiten de VS. MedCheck gebruikt ATC-5 als internationale backbone en
zet landspecifieke terminologie (in Nederland: de G-standaard) in een pluggable
locale-module (`locales/nl/`), zodat een ander land een eigen module toevoegt
zonder de matching-kern aan te raken.

## Twinlist (SHARP/HCIL, University of Maryland)

Open source, vooral een UI-innovatie: side-by-side matching van medicatielijsten met
visuele nadruk op wat een verpleegkundige/arts moet controleren tijdens reconciliatie.

**Verschil met MedCheck:** Twinlist's bijdrage zit in de interactie-ontwerp, niet in de
matching-logica zelf of in AI-extractie uit ongestructureerde bronnen (PDF, foto). MedCheck
voegt een deterministische diff-engine met expliciete confidence-scores per veld toe, en een
escalatieregelset die niet wegklikbaar is voor risicomedicatie.

## astraedus/medrecon

Recent project, gebruikt AI-agents die zelf over FHIR-resources redeneren om
discrepanties te vinden. Hackathon-niveau, geen gepubliceerde validatie.

**Verschil met MedCheck:** in medrecon vergelijkt het model zelf — dat is precies wat
ADR-001 voor MedCheck uitsluit. Een LLM dat "verschillen ziet" is voor patiëntveiligheid
onaanvaardbaar zonder deterministische, testbare garantie. MedCheck laat AI alleen
extraheren en normaliseren; de diff zelf is code met unit tests.

## MedXN

Extractie- en normalisatietool voor medicatie-vermeldingen in vrije klinische tekst
(NLP-pipeline, geen LLM-gebaseerde extractie).

**Verschil met MedCheck:** MedXN doet alleen extractie/normalisatie, geen vergelijking
tussen twee bronnen en geen escalatielogica. MedCheck combineert AI-extractie (met
per-veld confidence) met een aparte, deterministische diff- en triagelaag, en documenteert
de MDR-by-design-overwegingen die daarbij horen (`docs/decisions/`) — MedXN is een
onderzoekscomponent, geen op zorgovergang gericht eindproduct.

## Wat dit niet dekt

Deze vier zijn niet uitputtend — het is een scan om MedCheck's positionering te
onderbouwen (ATC-5 als backbone, pluggable locale-module, deterministische diff,
MDR-by-design zonder certificering na te streven), niet een systematische review.
