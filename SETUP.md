# Setup — VS Code + Claude Code

Doel: een werkende lokale omgeving om MedCheck te draaien en verder te bouwen, met VS Code en
Claude Code. Doorloop dit één keer volledig en test het voordat je aan het werk gaat.

## 1. Basis

| Onderdeel | Waarom |
|---|---|
| Node.js 18+ | vereist voor Claude Code |
| Python 3.11+ | de stack |
| Git + GitHub-account | versiebeheer en traceerbaarheid van wat er gebouwd is |
| VS Code | editor |

Controleer: `node -v`, `python3 --version`, `git --version`.

## 2. Claude Code

Installeren via npm, daarna in de projectmap starten met `claude`. Zie de actuele instructies
op de Anthropic-documentatie — installatiecommando's veranderen, dus controleer de actuele versie.
Er is ook een VS Code-extensie waarmee Claude Code in een zijpaneel draait; dat werkt prettiger
dan een losse terminal, omdat je diffs direct in de editor ziet.

Verifieer dat het werkt: open de projectmap, start Claude Code, en vraag "vat CLAUDE.md samen".
Krijg je een correcte samenvatting, dan leest hij je projectinstructie. Dat is de test.

## 3. VS Code-extensies

- Python (Microsoft)
- Ruff (linting + formatting)
- Even Better TOML
- Markdown All in One
- GitLens (handig bij het terugkijken op wie wat wanneer heeft gewijzigd)

## 4. Projectmap opzetten

```bash
git init
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # alleen nodig voor de geplande AI-extractie (fase 2); mag leeg
pytest                              # moet slagen (nog geen tests = groen)
```

`.env` staat in `.gitignore`. Zet je API-key nooit in een bestand dat je commit — controleer dit
vóór je eerste push.

## 5. Streamlit-UI starten en testen

Na installatie van de dependencies start je de Streamlit-webinterface:

```bash
# Activeer de virtuele omgeving (Windows)
.venv\Scripts\activate

# Of op macOS/Linux
source .venv/bin/activate

# Start Streamlit
streamlit run ui/app.py
```

Streamlit opent automatisch een browservenster met MedCheck. Als dat niet lukt, kopieer dan
de URL die in de terminal verschijnt (meestal `http://localhost:8501`) en plak die in je browser.

### Verificatiestappen

Controleer of alles werkt door deze checks uit te voeren:

1. **Streamlit start op**
   - Zie je de MedCheck-titel en versie in de browser?
   - Zie je de twee upload-velden "Was" en "Wordt"?

2. **Bestanden uploaden en vergelijken**
   - Upload twee CSV- of PDF-bestanden met medicatiegegevens
   - Klik op "Vergelijk"
   - Zie je een resultaat met eventuele discrepanties?

3. **Identiteitscheck**
   - Als de bestanden BSN-gegevens bevatten: zie je de melding "Patiëntidentiteit bevestigd via BSN"?
   - Als er geen BSN is: zie je een waarschuwing over handmatige controle?

4. **Geen verschillen**
   - Upload twee identieke medicatielijsten
   - Zie je een succsmelding met het aantal gematchte regels?

5. **Foutafhandeling**
   - Probeer een onleesbaar PDF-bestand te uploaden
   - Zie je een duidelijke foutmelding?

### Veelvoorkomende problemen

- **ModuleNotFoundError: streamlit**: Voer `pip install -r requirements.txt` uit in de geactiveerde venv
- **Port 8501 in use**: Sluit andere Streamlit-instanties of gebruik `streamlit run ui/app.py --server.port 8502`
- **FileNotFoundError**: Zorg dat je in de projectroot staat (`cd /pad/naar/medcheck`)

## 6. API-key (optioneel)

**Niet nodig voor de huidige versie.** MedCheck draait nu volledig lokaal: de vergelijking en de
parsers bevatten geen AI-aanroepen of netwerkverkeer. Een API-key is alleen nodig voor de geplande
AI-extractie (fase 2) en voor evaluatieruns daarvan. Aanmaken kan in de Anthropic Console. Zet dan
een uitgavenlimiet; evaluatieruns over 30 casus × meerdere iteraties lopen anders ongemerkt op.

## 7. Vaste sessieroutine (voor werken met Claude Code)

Begin:
```
Lees CLAUDE.md en docs/BACKLOG.md.
Vat samen waar we staan en stel de eerstvolgende stap voor. Bouw nog niets.
```

Eind:
```
Vat deze sessie samen: wat is gebouwd, wat misging en welk gedrag van jou onbetrouwbaar was.
Zet het in de commitmessage of PR-beschrijving.
```

## 8. Repo-structuur

```
medcheck/
├── CLAUDE.md              projectinstructie — leest Claude automatisch
├── SETUP.md               dit bestand
├── README.md  SAFETY.md  CONTRIBUTING.md  VALIDATION.md  RELATED_WORK.md  CHANGELOG.md
├── requirements.txt
├── .env.example
├── compare.py             orchestratie: bestand A + bestand B → discrepanties
├── engine/                diff en duplicaatdetectie — geen AI
├── matching.py  identity.py  models.py  reference.py
├── normalize/             eenheden, frequentie
├── parsing/               CSV- en PDF-tekstparsers
├── locales/               landmodules (nl/, template/)
├── triage/                escalatieregels
├── ui/                    Streamlit-interface
├── scripts/               casusgeneratie, validatie
├── tests/
├── data/
│   ├── synthetic/casus/   synthetische casus + ground truth
│   └── reference/         ATC-subset, risicomedicatielijst
└── docs/
    ├── INTENDED_USE.md    leidend bij elke scopevraag
    ├── RISK_ANALYSIS.md   risicoregister (ISO 14971-stijl)
    ├── BACKLOG.md
    ├── MVP_OPZET.md  DEMO.md  CASUS_FORMAAT_PROMPTS.md
    └── decisions/         ADR's
```

Gepland maar nog niet aanwezig: `extraction/` (AI-extractie) en `eval/` (evaluatieharnas), fase 2.
