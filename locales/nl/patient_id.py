"""NL-landmodule: BSN-validatie (elfproef).

BSN is een Nederlands, wettelijk beschermd persoonsidentificerend nummer (AVG/UAVG,
zwaarder beschermd dan gewone persoonsgegevens) -- geen equivalent in andere landen,
dus hier en nergens in de taal-agnostische kern (CLAUDE.md architectuursectie: nooit
NL-specifieke logica buiten de locale-module).

Deze module valideert alleen de 11-proef (hetzelfde principe als de oude
bankrekening-11-proef): dat bewijst dat een BSN correct is ingevoerd/overgenomen, niet
dat het een bestaand of bij deze patiënt behorend nummer is. De daadwerkelijke
identiteitsvergelijking (BSN A == BSN B) gebeurt in identity.py, buiten deze module --
dat is taal-agnostische stringgelijkheid, geen BSN-specifieke logica.
"""

import re

_WEIGHTS = (9, 8, 7, 6, 5, 4, 3, 2, -1)


def normalize_bsn(raw: str) -> str:
    """Strip niet-cijfers (spaties, punten, koppeltekens uit brondocumenten)."""
    return re.sub(r"\D", "", raw or "")


def is_valid_bsn(bsn: str) -> bool:
    """11-proef: som van cijfer * gewicht (9..2, laatste cijfer * -1) moet deelbaar
    zijn door 11. Een BSN telt 8 of 9 cijfers; bij 8 cijfers wordt links met een 0
    aangevuld (officiële BSN-notatie). "000000000" is geen uitgegeven BSN en telt
    bewust als ongeldig, ook al voldoet de som toevallig aan de 11-proef."""
    digits = normalize_bsn(bsn)
    if len(digits) == 8:
        digits = "0" + digits
    if len(digits) != 9 or digits == "0" * 9:
        return False
    total = sum(int(digit) * weight for digit, weight in zip(digits, _WEIGHTS))
    return total % 11 == 0
