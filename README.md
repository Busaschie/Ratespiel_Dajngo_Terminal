# Ratespiel - Terminal Version

Verzeichnis -> terminal-spiel -> rate_spiel_kommentiert.py


# Ratespiel – Django Web-App

## Schnellstart

```bash
# 1. Django installieren
pip install django

# 2. In das Projektverzeichnis wechseln
cd ratespiel_django

# 3. Datenbank anlegen (einmalig)
python manage.py migrate

# 4. Sessions-Verzeichnis anlegen (einmalig)
mkdir -p sessions

# 5. Entwicklungsserver starten
python manage.py runserver

# → Browser öffnen: http://127.0.0.1:8000
```

## Projektstruktur

```
ratespiel_django/
├── manage.py
├── ratespiel/          ← Django-Projekt-Konfiguration
│   ├── settings.py
│   └── urls.py
└── game/               ← Spiellogik als Django-App
    ├── models.py       ← Datenbankmodell (Spieleintrag)
    ├── views.py        ← Alle Views inkl. Ajax-Endpunkte
    ├── spiellogik.py   ← Reine Spiellogik (kein Django)
    ├── urls.py
    ├── migrations/
    ├── templates/game/
    │   ├── base.html
    │   ├── index.html      ← GameMaster Setup
    │   ├── spielername.html
    │   ├── spielen.html    ← Hauptspiel (Ajax)
    │   └── highscore.html
    └── static/game/css/
        └── style.css       ← Flat Dark Design
```

## Spielablauf

1. **GameMaster** wählt: Zufallszahl oder eigene Zahl, Schwierigkeitsgrad, Versuche
2. **PlayerOne** gibt seinen Namen ein
3. **Spielschleife** läuft per Ajax (kein Seitenreload)
4. Hinweise: Richtung, Stellenanzahl, Positions-Treffer, Vorschau
5. Ergebnis-Overlay + Statistik aus der Datenbank

## Datenbank

SQLite (`rate.db`) – kompatibel mit dem Original `raten-kurz.py`.
Tabelle: `ratedb` (gleiche Spaltenstruktur wie original).
