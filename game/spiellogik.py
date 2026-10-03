import random

MOTIVATIONEN = [
    "Bleib dran!", "Du schaffst das!", "Weiter so!", "Nicht aufgeben!",
    "Versuch es noch einmal!", "Jetzt erst recht!", "Du warst so nahe dran!",
    "Beim nächsten Mal funktioniert es!!"
]

SCHWIERIGKEITEN = {
    "l": {"label": "Leicht",    "max": 99},
    "m": {"label": "Mittel",    "max": 9999},
    "s": {"label": "Schwer",    "max": 999999},
    "h": {"label": "Höllisch",  "max": 99999999},
}


def neue_geheimzahl(schwierigkeit: str) -> int:
    return random.randint(0, SCHWIERIGKEITEN[schwierigkeit]["max"])


def pruefe_tipp(versuch: int, geheimzahl: int, vorschau: dict) -> dict:
    """
    Vergleicht Tipp mit Geheimzahl und gibt Hinweis-Daten zurück.
    vorschau: dict { stelle_idx: ziffer_str_oder_'x' }
    """
    v_str = str(versuch)
    g_str = str(geheimzahl)
    g_len = len(g_str)
    v_len = len(v_str)

    richtung = "groß" if versuch > geheimzahl else "klein"
    diff_stellen = abs(v_len - g_len)

    # Stellen-Hinweis
    stellen_hinweis = None
    if versuch > geheimzahl and v_len > g_len:
        stellen_hinweis = f"Deine Zahl hat {v_len} Stellen – die Geheimzahl hat {diff_stellen} Stellen weniger."
    elif versuch < geheimzahl and v_len < g_len:
        stellen_hinweis = f"Deine Zahl hat {v_len} Stellen – die Geheimzahl hat {diff_stellen} Stellen mehr."

    # Positions-Treffer (von rechts ausrichten)
    treffer = []
    g_idx = g_len - 1
    for i in range(v_len - 1, -1, -1):
        if g_idx < 0:
            break
        if v_str[i] == g_str[g_idx]:
            vorschau[g_idx] = g_str[g_idx]
            treffer.append({"stelle": g_idx + 1, "ziffer": g_str[g_idx]})
        g_idx -= 1

    vorschau_str = "".join(vorschau.get(i, "x") for i in range(g_len))

    return {
        "richtung": richtung,
        "stellen_hinweis": stellen_hinweis,
        "treffer": treffer,
        "vorschau": vorschau,
        "vorschau_str": vorschau_str,
    }


def motivation() -> str:
    return random.choice(MOTIVATIONEN)
