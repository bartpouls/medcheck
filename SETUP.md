# Setup — VS Code + Claude Code

Doel: op 25 augustus om 9:00 open je je laptop, typ je `claude`, en begin je te bouwen.
Geen installatiegedoe op de dag zelf. Doorloop dit ruim vooraf en test het één keer volledig.

## 1. Basis

| Onderdeel | Waarom |
|---|---|
| Node.js 18+ | vereist voor Claude Code |
| Python 3.11+ | de stack |
| Git + GitHub-account | versiebeheer én je bewijsmateriaal voor het congres |
| VS Code | editor |

Controleer: `node -v`, `python3 --version`, `git --version`.

## 2. Claude Code

Installeren via npm, daarna in de projectmap starten met `claude`. Zie de actuele instructies
op de Anthropic-documentatie — installatiecommando's veranderen; controleer die vóór 25 augustus.
Er is ook een VS Code-extensie waarmee Claude Code in een zijpaneel draait; dat werkt prettiger
dan een losse terminal, omdat je diffs direct in de editor ziet.

Verifieer dat het werkt: open de projectmap, start Claude Code, en vraag "vat CLAUDE.md samen".
Krijg je een correcte samenvatting, dan leest hij je projectinstructie. Dat is de test.

## 3. VS Code-extensies

- Python (Microsoft)
- Ruff (linting + formatting)
- Even Better TOML
- Markdown All in One
- GitLens (handig bij het terugkijken op je eigen bouwproces voor het congres)

## 4. Projectmap opzetten

```bash
git init
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # vul je API-key in
pytest                              # moet slagen (nog geen tests = groen)
```

`.env` staat in `.gitignore`. Zet je API-key nooit in een bestand dat je commit — controleer dit
vóór je eerste push.

## 5. API-key

Aanmaken in de Anthropic Console. Je gebruikt de API alleen in fase 2 (extractie) en voor de
evaluatieruns. Zet een uitgavenlimiet; evaluatieruns over 30 casus × meerdere iteraties lopen
anders ongemerkt op.

## 6. Vaste sessieroutine

Begin:
```
Lees CLAUDE.md, de laatste entries in docs/JOURNEY.md en docs/BACKLOG.md.
Vat samen waar we staan en stel de eerstvolgende stap voor. Bouw nog niets.
```

Eind:
```
Schrijf een JOURNEY-entry voor deze sessie volgens het sjabloon. Wees eerlijk over wat
misging en welk gedrag van jou onbetrouwbaar was.
```

## 7. Repo-structuur

```
medcheck/
├── CLAUDE.md              projectinstructie — leest Claude automatisch
├── SETUP.md               dit bestand
├── requirements.txt
├── .env.example
├── docs/
│   ├── INTENDED_USE.md    leidend bij elke scopevraag
│   ├── RISK_ANALYSIS.md   ISO 14971
│   ├── JOURNEY.md         bouwlog = congresmateriaal
│   ├── BACKLOG.md
│   ├── WORKSHOP_25AUG.md
│   ├── WORKSHOP_12OKT.md
│   └── decisions/         ADR's
├── data/
│   ├── casus/             synthetische casus + ground truth
│   └── reference/         ATC-subset, risicomedicatielijst
├── engine/                diff — geen AI
├── extraction/            AI-extractie
├── eval/                  evaluatieharnas
├── ui/                    Streamlit (fase 3)
└── tests/
```
