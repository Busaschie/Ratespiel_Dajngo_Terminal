import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Spieleintrag
from .spiellogik import (
    neue_geheimzahl, pruefe_tipp, motivation,
    SCHWIERIGKEITEN
)


# ─── Hilfsfunktion: Session-Spielstand ───────────────────────────────────────

def _get_spiel(request):
    return request.session.get("spiel", {})

def _set_spiel(request, data):
    request.session["spiel"] = data
    request.session.modified = True


# ─── Views ───────────────────────────────────────────────────────────────────
def index(request):
    """Startseite: GameMaster wählt Modus."""
    request.session.flush()

    # Erste Schwierigkeit als eigene Variable mitgeben
    erste_schwierigkeit = list(SCHWIERIGKEITEN.keys())[0] if SCHWIERIGKEITEN else ""

    return render(request, "game/index.html", {
        "schwierigkeiten": SCHWIERIGKEITEN,
        "erste_schwierigkeit": erste_schwierigkeit,
    })


@require_POST
def setup(request):
    """GameMaster konfiguriert das Spiel (Ajax)."""
    data = json.loads(request.body)
    modus          = data.get("modus")          # "z" oder "e"
    schwierigkeit  = data.get("schwierigkeit")  # "l","m","s","h"
    eigene_zahl    = data.get("eigene_zahl")
    versuchanzahl  = int(data.get("versuchanzahl", 5))

    if modus == "z":
        geheimzahl = neue_geheimzahl(schwierigkeit)
    else:
        try:
            geheimzahl = int(eigene_zahl)
        except (TypeError, ValueError):
            return JsonResponse({"ok": False, "fehler": "Ungültige Geheimzahl."})

    g_str = str(geheimzahl)
    vorschau = {str(i): "x" for i in range(len(g_str))}

    _set_spiel(request, {
        "geheimzahl":    geheimzahl,
        "g_str":         g_str,
        "g_len":         len(g_str),
        "versuchanzahl": versuchanzahl,
        "wieviel":       1,
        "getippt":       [],
        "vorschau":      vorschau,
        "status":        "laeuft",
    })
    return JsonResponse({"ok": True})


def spielername(request):
    """PlayerOne gibt seinen Namen ein."""
    spiel = _get_spiel(request)
    if not spiel:
        return redirect("index")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            return render(request, "game/spielername.html", {"fehler": "Bitte einen Namen eingeben."})

        # Prüfen ob Name schon existiert
        existiert = Spieleintrag.objects.filter(playername=name).exists()
        spiel["name"] = name
        spiel["name_existiert"] = existiert
        _set_spiel(request, spiel)
        return redirect("spielen")

    return render(request, "game/spielername.html")


def spielen(request):
    """Hauptspiel-Seite."""
    spiel = _get_spiel(request)
    if not spiel or "name" not in spiel:
        return redirect("index")

    # Statistik des Spielers laden
    name = spiel["name"]
    alle_spiele = list(Spieleintrag.objects.filter(playername=name).values(
        "erraten", "abgebrochen", "benoetigt", "versuche_gesamt",
        "geheimzahl", "getippt", "datum"
    ))
    gewonnen  = sum(1 for s in alle_spiele if s["erraten"])
    verloren  = sum(1 for s in alle_spiele if not s["erraten"] and not s["abgebrochen"])
    abbrueche = sum(1 for s in alle_spiele if s["abgebrochen"])

    return render(request, "game/spielen.html", {
        "spiel":        spiel,
        "alle_spiele":  alle_spiele,
        "gewonnen":     gewonnen,
        "verloren":     verloren,
        "abbrueche":    abbrueche,
        "gesamt":       len(alle_spiele),
    })


@require_POST
def tipp_ajax(request):
    """Verarbeitet einen Tipp (Ajax-Call)."""
    spiel = _get_spiel(request)
    if not spiel or spiel.get("status") != "laeuft":
        return JsonResponse({"fehler": "Kein aktives Spiel."}, status=400)

    data       = json.loads(request.body)
    tipp_raw   = data.get("tipp", "").strip()

    # Abbruch
    if tipp_raw == "xxx":
        spiel["status"] = "abgebrochen"
        _set_spiel(request, spiel)
        _speichere_spiel(spiel, abgebrochen=True)
        return JsonResponse({
            "status":    "abgebrochen",
            "geheimzahl": spiel["geheimzahl"],
            "getippt":   spiel["getippt"],
        })

    if not tipp_raw.isdigit():
        return JsonResponse({"fehler": "Bitte nur Zahlen eingeben!"})

    versuch = int(tipp_raw)
    spiel["getippt"].append(versuch)

    # Gewonnen?
    if versuch == spiel["geheimzahl"]:
        spiel["status"] = "gewonnen"
        _set_spiel(request, spiel)
        _speichere_spiel(spiel, erraten=True)
        return JsonResponse({
            "status":   "gewonnen",
            "versuche": spiel["wieviel"],
            "geheimzahl": spiel["geheimzahl"],
            "getippt":  spiel["getippt"],
        })

    # Hinweis berechnen
    vorschau_dict = {int(k): v for k, v in spiel["vorschau"].items()}
    hinweis = pruefe_tipp(versuch, spiel["geheimzahl"], vorschau_dict)
    spiel["vorschau"] = {str(k): v for k, v in hinweis["vorschau"].items()}

    spiel["wieviel"] += 1
    verbleibend = spiel["versuchanzahl"] - spiel["wieviel"] + 1

    # Verloren?
    if spiel["wieviel"] > spiel["versuchanzahl"]:
        spiel["status"] = "verloren"
        _set_spiel(request, spiel)
        _speichere_spiel(spiel, erraten=False)
        return JsonResponse({
            "status":      "verloren",
            "geheimzahl":  spiel["geheimzahl"],
            "getippt":     spiel["getippt"],
            "motivation":  motivation(),
        })

    _set_spiel(request, spiel)
    return JsonResponse({
        "status":          "weiter",
        "richtung":        hinweis["richtung"],
        "stellen_hinweis": hinweis["stellen_hinweis"],
        "treffer":         hinweis["treffer"],
        "vorschau_str":    hinweis["vorschau_str"],
        "verbleibend":     verbleibend,
        "wieviel":         spiel["wieviel"],
    })


def _speichere_spiel(spiel, erraten=False, abgebrochen=False):
    Spieleintrag.objects.create(
        playername      = spiel.get("name", "Unbekannt"),
        geheimzahl      = spiel["geheimzahl"],
        versuche_gesamt = spiel["versuchanzahl"],
        getippt         = str(spiel["getippt"]),
        benoetigt       = spiel["wieviel"],
        abgebrochen     = abgebrochen,
        erraten         = erraten,
    )


def highscore(request):
    """Highscore-Übersicht."""
    eintraege = Spieleintrag.objects.filter(erraten=True).order_by("benoetigt", "datum")[:20]
    return render(request, "game/highscore.html", {"eintraege": eintraege})
