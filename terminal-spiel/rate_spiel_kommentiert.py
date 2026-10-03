import random
import sqlite3
import time
import getpass
import os

# ─── Motivationstexte bei verlorenem Spiel ───────────────────────────────────
MOTIVATIONEN = [
    "Bleib dran!", "Du schaffst das!", "Weiter so!", "Nicht aufgeben!",
    "Versuch es noch einmal!", "Jetzt erst recht!", "Du warst so nahe dran!",
    "Beim nächsten mal funktioniert es!!"
]

# ═══════════════════════════════════════════════════════════════════════════════
# DATENBANK
# Alle Spielergebnisse werden in rate.db gespeichert.
# Tabelle: ratedb  →  ein Datensatz pro Spielrunde
# ═══════════════════════════════════════════════════════════════════════════════

def init_db():
    """Erstellt die Datenbank und Tabelle, falls noch nicht vorhanden."""
    con = sqlite3.connect("rate.db")
    con.execute("""CREATE TABLE IF NOT EXISTS ratedb (
        id INTEGER, playername TEXT, geheimzahl INTEGER,
        versuche_gesamt INTEGER, getippt TEXT, benoetigt INTEGER,
        abgebrochen INTEGER, erraten INTEGER, datum TEXT
    )""")
    con.commit()
    con.close()

def db_eintrag(werte):
    """Speichert einen abgeschlossenen Spieldatensatz in der DB."""
    con = sqlite3.connect("rate.db")
    try:
        with con:
            con.execute("INSERT INTO ratedb VALUES (?,?,?,?,?,?,?,?,?)", werte)
    except Exception:
        print("Probleme mit der DB - Rollback")
        con.rollback()
        raise

def db_abfrage(name):
    """Zeigt die Spielhistorie eines Spielers an (nur ab 2 gespeicherten Spielen)."""
    con = sqlite3.connect("rate.db")
    rows = con.execute("SELECT * FROM ratedb WHERE playername = ?", (name,)).fetchall()
    con.close()
    if len(rows) <= 1:
        return  # Noch nicht genug Daten für eine Statistik
    gewonnen  = sum(1 for r in rows if r[7] == 1)
    abbrueche = sum(1 for r in rows if r[6] == 1)
    verloren  = len(rows) - gewonnen - abbrueche
    print("." * 60)
    print(f"{name} Du hast schon {len(rows)} mal gespielt.")
    print(f"Gewonnen: {gewonnen}  |  Verloren: {verloren}  |  Abgebrochen: {abbrueche}")
    print("\nMöchtest Du alle Deine Spiele angezeigt bekommen?\nTippe - 'j' für Ja oder 'n' für Nein")
    if validiere_eingabe(f"-> Deine Wahl {name}: ", ["j", "n"]) == "j":
        for r in rows:
            print(f"\nGespielt am: {r[8]}")
            print(f"Abgebrochen: {'Ja' if r[6] else 'Nein'}  /  Erraten: {'Ja' if r[7] else 'Nein'}")
            print(f"Geheimzahl war: {r[2]}  /  Benötigte Versuche: {r[5]} von {r[3]}")
            print(f"Getippte Zahlen: {r[4]}")

# ═══════════════════════════════════════════════════════════════════════════════
# HILFSFUNKTIONEN
# ═══════════════════════════════════════════════════════════════════════════════

def validiere_eingabe(prompt, erlaubte):
    """Wiederholt die Eingabe solange, bis ein erlaubter Wert eingegeben wurde."""
    eingabe = input(prompt).strip()
    while eingabe not in erlaubte:
        print(f"\nEs ist NUR die Eingabe -> {' / '.join(erlaubte)} <- erlaubt!!")
        eingabe = input(prompt).strip()
    return eingabe

def geheimzahl_eingabe():
    """Liest die Geheimzahl verborgen ein (getpass). Fallback bei PyCharm-Erkennung."""
    while True:
        if "PYCHARM_HOSTED" in os.environ:
            print("\nWarnung: PyCharm erkannt – Eingabe ist SICHTBAR!")
            zahl = input("-> Geheimzahl eingeben: ").strip()
        else:
            zahl = getpass.getpass("\n-> Geheimzahl eingeben (versteckt): ").strip()
        if zahl.isdigit():
            return zahl
        print("\nBitte NUR Zahlen eingeben GameMaster!")

def schwierigkei(wahl):
    """Gibt die Zahlen-Obergrenze für den gewählten Schwierigkeitsgrad zurück."""
    grenzen = {"l": 99, "m": 9999, "s": 999999, "h": 99999999}
    return grenzen[wahl]

def spielername_abfragen():
    """Fragt nach dem Spielernamen und prüft, ob er bereits in der DB existiert.
    Rückgabe: [eingegebener_name, db_name_oder_None]"""
    name = input("\n\nPlayerOne 🐯\n-> Wähle Deinen Spielernamen: ").strip()
    con  = sqlite3.connect("rate.db")
    row  = con.execute("SELECT playername FROM ratedb WHERE playername = ?", (name,)).fetchone()
    con.close()
    return [name, row[0] if row else None]

def zeige_vorschau(versuch, geheimniss, geheim_lang, gheimlist, vorschau):
    """Gibt zu groß/zu klein Hinweis und zeigt welche Ziffern bereits stimmen.
    Vergleich erfolgt stellenweise von rechts nach links."""
    versuch_str  = str(versuch)
    versuch_lang = len(versuch_str)
    diff         = abs(versuch_lang - geheim_lang)

    # Richtungshinweis + Stellenanzahl-Hinweis
    if versuch > geheimniss:
        print("--- Die Zahl ist zu groß!!!")
        if versuch_lang > geheim_lang:
            print(f"--- Deine Zahl hat {versuch_lang} Stellen, die Geheimzahl hat {diff} Stellen weniger!!")
    else:
        print("--- Die Zahl ist zu klein!!!")
        if versuch_lang < geheim_lang:
            print(f"--- Deine Zahl hat {versuch_lang} Stellen, die Geheimzahl hat {diff} Stellen mehr!!")

    # Ziffernvergleich von rechts → richtige Stellen in Vorschau übernehmen
    versuch_list = list(versuch_str)
    g = geheim_lang - 1
    for i in range(versuch_lang - 1, -1, -1):
        if g < 0:
            break
        if int(versuch_list[i]) == int(gheimlist[g]):
            print(f"--- Position {i+1} stimmt – Ziffer: {gheimlist[g]}")
            vorschau[g] = gheimlist[g]
        g -= 1

    print("--- Bisher richtig:", "".join(vorschau.values()))
    return vorschau

def nach_spiel(werte, list_getippt, geheimniss, name):
    """Speichert Ergebnis, zeigt Statistik und fragt ob nochmal gespielt wird."""
    print(f"\nDu hast getippt: {list_getippt}")
    print(f"Die Geheimzahl war: {geheimniss}")
    db_eintrag(werte)
    db_abfrage(name)
    print("=" * 60)
    print(f"\nNocheinmal spielen {name}?\nTippe - 'j' für Ja oder 'n' für Nein")
    return validiere_eingabe("Deine wahl: ", ["j", "n"])


# ═══════════════════════════════════════════════════════════════════════════════
# HAUPTPROGRAMM
# Ablauf pro Runde:
#   1. GameMaster legt Geheimzahl + Versuchsanzahl fest
#   2. PlayerOne gibt seinen Namen ein
#   3. Spielschleife: raten bis richtig, abgebrochen oder Versuche aufgebraucht
#   4. Ergebnis speichern, Statistik zeigen, ggf. neu starten
# ═══════════════════════════════════════════════════════════════════════════════
init_db()

wiederholen = "j"
while wiederholen == "j":

    # Spielvariablen zu Beginn jeder Runde zurücksetzen
    wieviel        = 1
    list_getippt   = []
    anzahlversuche = 0
    name           = ""

    # ── Schritt 1: GameMaster – Geheimzahl festlegen ──────────────────────────
    print("\n" + "=" * 60)
    print("\nReady GameMaster? 🐱\nWie möchtest Du vorgehen?\n\nGeheimzahl eingaben oder eine Zufällige Geheimzahl erstellen lassen.\nTippe - 'e' für Eingabe oder 'z' für Zufall.")
    modus = validiere_eingabe("-> Deine Wahl GameMaster: ", ["e", "z"])

    if modus == "z":
        # Zufallszahl im gewählten Schwierigkeitsbereich erzeugen
        print("\nGameMaster - Wie schwer soll es werden?")
        print("Tippe - 'l' für Leicht / 'm' für Mittel / 's' für Schwer / 'h' für Höllisch")
        wahl           = validiere_eingabe("-> Deine Wahl GameMaster: ", ["l", "m", "s", "h"])
        grenzen        = schwierigkei(wahl)
        geheimniss_str = str(random.randint(0, grenzen))
        print("Geheimzahl wurde erstellt!!")
    else:
        # Manuelle Eingabe, versteckt per getpass
        geheimniss_str = geheimzahl_eingabe()

    # ── Schritt 2: Versuchsanzahl festlegen ───────────────────────────────────
    print("\nGameMaster - Wieviele Versuche soll PlayerOne haben?")
    versuchanzahl_str = input("-> Deine Wahl GameMaster: ").strip()
    while not versuchanzahl_str.isdigit() or versuchanzahl_str == "":
        print("\nBitte NUR eine Zahl eingeben!")
        versuchanzahl_str = input("-> Wieviele Versuche also? ").strip()

    # Geheimzahl in Liste aufsplitten (für Ziffernvergleich in zeige_vorschau)
    geheim_lang   = len(geheimniss_str)
    gheimlist     = list(geheimniss_str)
    geheimniss    = int(geheimniss_str)
    versuchanzahl = int(versuchanzahl_str)
    vorschau      = {i: "x" for i in range(geheim_lang)}  # Platzhalter für richtige Ziffern

    # ── Schritt 3: Spielername ────────────────────────────────────────────────
    backinfo = spielername_abfragen()
    while backinfo[1] is not None and backinfo[0] == backinfo[1]:
        # Name existiert bereits → behalten oder neu wählen
        print(f"\nPlayerOne!! Den Spielername '{backinfo[0]}' gibt es schon.\nMöchtest Du ihn behalten oder einen neuen wählen?")
        print("Tippe - 'b' für behalten oder 'n' für einen neuen Spielernamen.")
        wahl_name = validiere_eingabe("-> Deine Wahl PlayerOne? ", ["b", "n"])
        if wahl_name == "n":
            backinfo = spielername_abfragen()
        else:
            break
    name = backinfo[0]

    print(f"\nReady PlayerOne – {name}!")
    print(f"Du hast {versuchanzahl} Versuche. (Abbruch: xxx)\n")

    # ── Schritt 4: Spielschleife ──────────────────────────────────────────────
    versuch = None
    while wieviel <= versuchanzahl and versuch != geheimniss:

        versuch_raw = input("-> Gib Deinen Tipp ein: ").strip()

        # Abbruch durch Eingabe von "xxx"
        if versuch_raw == "xxx":
            print("=" * 60)
            print(f"Du hast abgebrochen {backinfo[0]}!\nDanke das Du gespielt hast 😊")
            datum = time.strftime("%d.%m.%Y um %H:%M:%S Uhr")
            werte = (2, name, geheimniss, versuchanzahl,
                     str(list_getippt) if list_getippt else "keine",
                     wieviel, 1, 0, datum)
            wiederholen = nach_spiel(werte, list_getippt, geheimniss, name)
            break

        # Nur Ziffern erlaubt
        if not versuch_raw.isdigit():
            print("Bitte NUR Zahlen eingeben!")
            continue

        versuch = int(versuch_raw)
        list_getippt.append(versuch)

        # Treffer → Gewonnen
        if versuch == geheimniss:
            print("=" * 60)
            print(f"🎉 🎈 Richtig! 🥇 👍 Du hast es in {wieviel} Versuch(en) geschafft!")
            datum = time.strftime("%d.%m.%Y um %H:%M:%S Uhr")
            werte = (2, name, geheimniss, versuchanzahl,
                     str(list_getippt), wieviel, 0, 1, datum)
            wiederholen = nach_spiel(werte, list_getippt, geheimniss, name)
            break

        # Kein Treffer → Hinweise anzeigen
        vorschau = zeige_vorschau(versuch, geheimniss, geheim_lang, gheimlist, vorschau)

        wieviel += 1
        verbleibend = versuchanzahl - wieviel + 1
        if wieviel <= versuchanzahl:
            print(f"\nNoch {verbleibend} {'Versuch' if verbleibend == 1 else 'Versuche'}!")

    else:
        # while-Bedingung erschöpft → alle Versuche aufgebraucht, nicht erraten
        if versuch != geheimniss:
            print("=" * 60)
            print(f"Schade {name}! Alle {versuchanzahl} Versuche verbraucht.")
            print(f"Leider hast Du es nicht erraten 🤷 - ABER: {random.choice(MOTIVATIONEN)}")
            print(f"\nDu hast getippt: {list_getippt}")
            print(f"Die Geheimzahl war: {geheimniss}")
            datum = time.strftime("%d.%m.%Y um %H:%M:%S Uhr")
            werte = (2, name, geheimniss, versuchanzahl,
                     str(list_getippt), versuchanzahl, 0, 0, datum)
            db_eintrag(werte)
            db_abfrage(name)
            print("=" * 60)
            print(f"\nNocheinmal spielen {name}?\nTippe - 'j' für Ja oder 'n' für Nein")
            wiederholen = validiere_eingabe("Deine Wahl: ", ["j", "n"])

    # Programm beenden wenn nicht nochmal gespielt wird
    if wiederholen != "j":
        print(f"\nDanke das Du gespielt hast, {name}! 👋")
        time.sleep(3)
