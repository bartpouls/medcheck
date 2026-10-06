"""Minimale upload-UI (fase 1 MVP): twee bestanden uploaden, vergelijken, resultaat
tonen. Geen afvinken, geen escalatiestatus, geen verificatieverslag -- dat is fase 3
(zie MVP_OPZET.md). Puur invocatie van compare.py; alle logica staat daar, niet hier.

Starten: streamlit run ui/app.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from compare import UnsupportedFileTypeError, compare_files, parse_file
from matching import match_lines
from parsing.csv_parser import UnreadableCsvError
from parsing.pdf_text import UnreadablePdfError
from version import __version__

st.set_page_config(page_title=f"MedCheck v{__version__} (fase 1, onderzoeksprototype)", layout="wide")
st.title(f"MedCheck v{__version__} — medicatievergelijking")
st.caption(
    "Onderzoeks-/demonstratieprototype. Niet in gebruik voor patiëntenzorg, niet "
    "CE-gemarkeerd. Zie docs/INTENDED_USE.md."
)

col_a, col_b = st.columns(2)
with col_a:
    file_a = st.file_uploader("Was", type=["csv", "pdf"], key="file_a")
with col_b:
    file_b = st.file_uploader("Wordt", type=["csv", "pdf"], key="file_b")

if st.button("Vergelijk", disabled=not (file_a and file_b)):
    with tempfile.TemporaryDirectory() as tmp_dir:
        path_a = Path(tmp_dir) / file_a.name
        path_b = Path(tmp_dir) / file_b.name
        path_a.write_bytes(file_a.getvalue())
        path_b.write_bytes(file_b.getvalue())

        try:
            result = compare_files(path_a, path_b)
        except (UnsupportedFileTypeError, UnreadablePdfError, UnreadableCsvError) as exc:
            st.error(exc.headline)
            if exc.detail:
                st.caption(exc.detail)
        else:
            identity_check = result.identity
            discrepancies = result.discrepancies

            # Patiëntidentiteit blokkeert nooit de vergelijking (Bart's expliciete
            # keuze, 2026-08-26) -- alleen prominente waarschuwingen, de assistent/
            # apotheker beoordeelt zelf. "Niet gevonden" en "ongeldig" zijn bewust
            # aparte meldingen, geen samengevoegde "kon niet valideren".
            if identity_check.method == "bsn" and identity_check.matched:
                st.success("Patiëntidentiteit bevestigd via BSN.")
            else:
                for warning in identity_check.warnings:
                    st.warning(warning.message)
                if identity_check.matched:
                    st.warning(
                        "Patiëntidentiteit bevestigd via naam + geboortedatum (BSN niet "
                        "bruikbaar). Let op: dit onderscheidt geen twee patiënten met "
                        "dezelfde naam en geboortedatum (bijv. een tweeling) — "
                        "controleer dit handmatig."
                    )
                else:
                    st.error(
                        "Patiëntidentiteit kon niet bevestigd worden — controleer "
                        "handmatig of Was en Wordt dezelfde patiënt betreffen "
                        "vóórdat je onderstaande vergelijking gebruikt."
                    )

            if not discrepancies:
                # Bewust geen kale "geen verschillen gevonden": dat suggereert dat er
                # niets te controleren valt. Ongematchte regels zijn het gevaarlijke
                # residu, niet nul -- dus toon expliciet hoeveel regels wél/niet
                # gematcht zijn, ook als dat laatste aantal (met de huidige
                # matching-logica, waar elke ongematchte regel al als ADDED/STOPPED-
                # discrepantie verschijnt) hier altijd 0 is.
                lines_a = parse_file(path_a, "a")
                lines_b = parse_file(path_b, "b")
                pairs = match_lines(lines_a, lines_b)
                gematcht = sum(1 for a_idx, b_idx in pairs if a_idx is not None and b_idx is not None)
                ongematcht = sum(1 for a_idx, b_idx in pairs if a_idx is None or b_idx is None)
                st.success(
                    f"{gematcht} regel(s) matchten en hadden geen verschil. "
                    f"{ongematcht} regel(s) konden niet gematcht worden — controleer die handmatig."
                )
            else:
                rows = [
                    {
                        "type": d.type,
                        "regel(s) was": ", ".join(str(i) for i in d.lines_a) or "-",
                        "regel(s) wordt": ", ".join(str(i) for i in d.lines_b) or "-",
                        "severity": d.severity,
                        "escalatie vereist": "ja" if d.requires_escalation else "nee",
                        "reden": d.reason,
                    }
                    for d in discrepancies
                ]
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)
                st.download_button(
                    "Download als JSON",
                    data=df.to_json(orient="records", force_ascii=False, indent=2),
                    file_name="medcheck_diff.json",
                    mime="application/json",
                )
