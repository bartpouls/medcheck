"""Gedeelde basis voor user-facing foutmeldingen met een korte kop + een optionele
langere technische toelichting, zodat de UI (ui/app.py) ze apart kan tonen
(st.error + st.caption) i.p.v. als één blok lopende tekst. str(exc) blijft beide
delen samengevoegd teruggeven, voor code/tests die alleen de platte foutmelding
nodig hebben (bv. pytest.raises(..., match=...))."""


class DiagnosableError(Exception):
    def __init__(self, headline: str, detail: str = ""):
        self.headline = headline
        self.detail = detail
        super().__init__(f"{headline} {detail}".strip() if detail else headline)
