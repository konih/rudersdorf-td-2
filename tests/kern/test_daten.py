"""Die Tabellen in ``rudersdorf/daten.py`` und die Karten im Ordner ``karten/`` passen zusammen.

Jede Prüfung ist eine Funktion, die eine Tabelle oder einen Kartentext bekommt und eine Liste
von Fehlertexten zurückgibt. So lässt sich jede Prüfung zweimal benutzen: einmal für die
echten Daten (die Liste muss leer sein) und einmal im Selbsttest für eine absichtlich
kaputte Kopie (die Liste muss genau den erwarteten Fehler nennen).
"""

import collections
import copy
import pathlib
import unittest

from rudersdorf import daten

WURZEL = pathlib.Path(__file__).resolve().parent.parent.parent
KARTEN_ORDNER = WURZEL / "karten"

# --- Was der Vertrag festlegt (specs/001-rudersdorf-2: data-model.md und contracts/) ---------

KARTEN = ("flusstal", "zwei_tore", "felsenmeer", "weites_feld", "labor")
ZEICHEN = ".#~%^SZD"
BEGEHBAR = ".%^SZ"
SPALTEN = 24
ZEILEN = 16
DORF_AB_SPALTE = 18
SCHADENSARTEN = {"stich", "wucht", "magie", "gift", "feuer"}

BAUWERK_SCHLUESSEL = {"name", "kurz", "kosten", "werte", "ausbau", "meister", "farbe"}
MEISTER_SCHLUESSEL = {"name", "kurz", "kosten", "braucht_schmiede", "ausbau"}
GEGNER_SCHLUESSEL = {
    "name",
    "leben",
    "tempo",
    "belohnung",
    "dorfschaden",
    "preis",
    "ab_welle",
    "boss",
    "fliegt",
    "resistenzen",
    "faehigkeiten",
    "teilt_in",
    "bricht",
    "groesse",
    "farbe",
}
SCHWIERIGKEIT_SCHLUESSEL = {"name", "leben_faktor", "budget_faktor", "start", "dorf_leben"}
DORF_SCHLUESSEL = {"name", "stufen"}
DORFSTUFE_SCHLUESSEL = {"name", "kosten", "braucht", "boni"}
ZAUBER_SCHLUESSEL = {"name", "klasse", "frei_ab_kirche", "braucht_ziel", "ausbau_kosten", "stufen"}

DORFLINIEN = {
    "kirche": 5,
    "schmiede": 3,
    "markt": 4,
    "steinbruch": 3,
    "haeuser": 5,
    "mauer": 4,
    "bauhuette": 3,
    "bibliothek": 3,
}
BONI = {
    "turm_schaden_prozent",
    "gold_pro_welle",
    "zinsen_prozent",
    "zinsen_max",
    "verkauf_prozent",
    "stein_pro_welle",
    "bewohner",
    "dorf_leben",
    "dorf_ruestung",
    "bau_rabatt_prozent",
    "zauber_stufe_max",
    "zauber_tempo_prozent",
    "mana_pro_sekunde",
    "mana_max",
    "heilung_pro_welle",
    "glocken_intervall",
    "glocken_dauer",
    "schmiede_stufe",
}
# Klassen der Mission 14 und die Namen ihrer Werte.
FAEHIGKEITEN = {
    "Regeneration": {"pro_sekunde"},
    "Heiler": {"radius", "pro_sekunde"},
    "Beschwoerer": {"intervall", "art", "anzahl"},
}
FAEHIGKEIT_FREIWILLIG = {"Beschwoerer": {"anzahl"}}
# Klassen der Mission 20 und die Namen ihrer Werte.
ZAUBERKLASSEN = {
    "Feuerball": {"kosten", "abklingzeit", "radius", "schaden", "brand_dauer", "brand_schaden"},
    "Eissturm": {"kosten", "abklingzeit", "radius", "dauer", "faktor"},
    "Blitzschlag": {"kosten", "abklingzeit", "schaden", "spruenge", "sprungweite"},
    "Segen": {"kosten", "abklingzeit", "heilung"},
    "Glockenschlag": {"kosten", "abklingzeit", "dauer"},
}
AUSBAU_ZEICHEN = ("+", "*", "=")
# Die Werte jedes Turms auf Stufe 1 (data-model.md, Tabelle der Bauwerke).
TURM_WERTE = {"schaden", "art", "reichweite", "nachladezeit", "trifft_luft"}
BESONDERE_WERTE = {
    "pfeil": set(),
    "kanone": {"radius"},
    "frost": {"frost_dauer", "frost_faktor"},
    "gift": {"gift_dauer", "gift_schaden"},
    "blitz": {"spruenge", "sprungweite"},
}
# Diese Gegner kauft die Wellenschmiede nie: Sie entstehen nur aus anderen.
NIE_GEKAUFT = {"schleimling"}


# --- Kleine Helfer -------------------------------------------------------------------------


def ist_zahl(wert):
    """``True`` und ``False`` sind in Python auch Zahlen; hier zählen sie nicht."""
    return isinstance(wert, (int, float)) and not isinstance(wert, bool)


def pruefe_schluessel(ort, eintrag, erwartet):
    """Ein Eintrag muss genau die erwarteten Schlüssel haben."""
    if not isinstance(eintrag, dict):
        return [f"{ort}: ist kein Wörterbuch"]
    fehler = [f"{ort}: Schlüssel {name!r} fehlt" for name in sorted(erwartet - set(eintrag))]
    fehler += [
        f"{ort}: Schlüssel {name!r} ist unbekannt" for name in sorted(set(eintrag) - erwartet)
    ]
    return fehler


def pruefe_kosten(ort, kosten):
    """Kosten nennen Gold und Stein, nie negativ, und irgendetwas muss es kosten."""
    fehler = pruefe_schluessel(ort, kosten, {"gold", "stein"})
    if fehler:
        return fehler
    for name in ("gold", "stein"):
        if not isinstance(kosten[name], int) or isinstance(kosten[name], bool) or kosten[name] < 0:
            fehler.append(f"{ort}: {name} muss eine ganze Zahl ab 0 sein")
    if not fehler and kosten["gold"] + kosten["stein"] <= 0:
        fehler.append(f"{ort}: kostet nichts")
    return fehler


def pruefe_ausbau(ort, ausbau):
    """Ein Ausbau ordnet jedem Wert ein Paar (Zeichen, Zahl) zu, wie Mission 10 es liest."""
    if not isinstance(ausbau, dict) or not ausbau:
        return [f"{ort}: muss ein Wörterbuch mit mindestens einem Wert sein"]
    fehler = []
    for wert, paar in ausbau.items():
        if not (isinstance(paar, tuple) and len(paar) == 2):
            fehler.append(f"{ort}: {wert} braucht ein Paar (Zeichen, Zahl)")
        elif paar[0] not in AUSBAU_ZEICHEN:
            fehler.append(f"{ort}: {wert} hat das unbekannte Zeichen {paar[0]!r}")
        elif not ist_zahl(paar[1]):
            fehler.append(f"{ort}: {wert} braucht eine Zahl")
    return fehler


# --- Die Prüfungen -------------------------------------------------------------------------


def pruefe_bauwerke(bauwerke):
    fehler = []
    for art, eintrag in bauwerke.items():
        ort = f"BAUWERKE[{art!r}]"
        falsch = pruefe_schluessel(ort, eintrag, BAUWERK_SCHLUESSEL)
        if falsch:
            fehler += falsch
            continue
        fehler += pruefe_kosten(f"{ort} kosten", eintrag["kosten"])
        werte = eintrag["werte"]
        fehler += pruefe_turmwerte(ort, art, werte)
        for nummer, ausbau in enumerate(eintrag["ausbau"], start=2):
            stufe = f"{ort} Stufe {nummer}"
            fehler += pruefe_ausbau(stufe, ausbau)
            fehler += pruefe_werte_vorhanden(stufe, ausbau, werte)
        for schluessel, meister in eintrag["meister"].items():
            wo = f"{ort} Meister {schluessel!r}"
            falsch = pruefe_schluessel(wo, meister, MEISTER_SCHLUESSEL)
            if falsch:
                fehler += falsch
                continue
            fehler += pruefe_kosten(f"{wo} kosten", meister["kosten"])
            fehler += pruefe_ausbau(wo, meister["ausbau"])
            fehler += pruefe_werte_vorhanden(wo, meister["ausbau"], werte)
            if meister["braucht_schmiede"] not in (1, 2, 3):
                fehler.append(f"{wo}: braucht_schmiede muss 1, 2 oder 3 sein")
    return fehler


def pruefe_turmwerte(ort, art, werte):
    """Ein Turm braucht alle Werte zum Schießen; nur die Palisade hat keine."""
    if art == "palisade":
        return [] if werte == {} else [f"{ort}: eine Palisade hat keine Werte"]
    erwartet = TURM_WERTE | BESONDERE_WERTE.get(art, set())
    fehler = [f"{ort}: Wert {name!r} fehlt" for name in sorted(erwartet - set(werte))]
    fehler += [f"{ort}: Wert {name!r} ist unbekannt" for name in sorted(set(werte) - erwartet)]
    if fehler:
        return fehler
    if werte["art"] not in SCHADENSARTEN:
        fehler.append(f"{ort}: unbekannte Schadensart {werte['art']!r}")
    if not isinstance(werte["trifft_luft"], bool):
        fehler.append(f"{ort}: trifft_luft muss True oder False sein")
    for name in sorted(erwartet - {"art", "trifft_luft"}):
        if not ist_zahl(werte[name]) or werte[name] <= 0:
            fehler.append(f"{ort}: {name} muss größer als 0 sein")
    return fehler


def pruefe_werte_vorhanden(ort, ausbau, werte):
    """``+`` und ``*`` gehen nur bei einem Wert, den der Turm schon hat (Mission 10)."""
    if not isinstance(ausbau, dict):
        return []
    return [
        f"{ort}: {wert} gibt es bei diesem Turm nicht"
        for wert, paar in ausbau.items()
        if isinstance(paar, tuple) and paar and paar[0] in ("+", "*") and wert not in werte
    ]


def pruefe_gegner(gegner):
    fehler = []
    for art, eintrag in gegner.items():
        ort = f"GEGNER[{art!r}]"
        falsch = pruefe_schluessel(ort, eintrag, GEGNER_SCHLUESSEL)
        if falsch:
            fehler += falsch
            continue
        for name in ("leben", "tempo", "belohnung", "dorfschaden", "groesse"):
            if not ist_zahl(eintrag[name]) or eintrag[name] <= 0:
                fehler.append(f"{ort}: {name} muss größer als 0 sein")
        for name in ("boss", "fliegt", "bricht"):
            if not isinstance(eintrag[name], bool):
                fehler.append(f"{ort}: {name} muss True oder False sein")
        for schadensart, faktor in eintrag["resistenzen"].items():
            if schadensart not in SCHADENSARTEN:
                fehler.append(f"{ort}: unbekannte Schadensart {schadensart!r}")
            elif not ist_zahl(faktor) or faktor < 0:
                fehler.append(f"{ort}: Resistenz gegen {schadensart} muss eine Zahl ab 0 sein")
        for klasse, werte in eintrag["faehigkeiten"]:
            if klasse not in FAEHIGKEITEN:
                fehler.append(f"{ort}: unbekannte Fähigkeit {klasse!r}")
                continue
            pflicht = FAEHIGKEITEN[klasse] - FAEHIGKEIT_FREIWILLIG.get(klasse, set())
            if not pflicht <= set(werte) <= FAEHIGKEITEN[klasse]:
                fehler.append(f"{ort}: {klasse} hat falsche Werte {sorted(werte)}")
            if klasse == "Beschwoerer" and werte.get("art") not in gegner:
                fehler.append(f"{ort}: beschwört unbekannte Art {werte.get('art')!r}")
        for kind in eintrag["teilt_in"]:
            if kind not in gegner:
                fehler.append(f"{ort}: teilt_in nennt unbekannte Art {kind!r}")
            elif kind == art:
                fehler.append(f"{ort}: teilt sich in sich selbst")
        fehler += pruefe_erzeugung(art, eintrag)
    return fehler


def pruefe_erzeugung(art, eintrag):
    """Preis und erste Welle sind ganze Zahlen über 0, so wie Mission 15 den Katalog erwartet."""
    ort = f"GEGNER[{art!r}]"
    fehler = []
    for name in ("preis", "ab_welle"):
        wert = eintrag[name]
        if not isinstance(wert, int) or isinstance(wert, bool):
            fehler.append(f"{ort}: {name} muss eine ganze Zahl sein")
        elif wert <= 0:
            fehler.append(f"{ort}: {name} muss größer als 0 sein")
    return fehler


def kaufbar(katalog, nummer, rest):
    """Die Kandidaten der Wellenschmiede, genau nach der Regel der Mission 15."""
    return sorted(
        art
        for art, eintrag in katalog.items()
        if not eintrag["boss"] and eintrag["ab_welle"] <= nummer and eintrag["preis"] <= rest
    )


def pruefe_schwierigkeit(tabelle):
    fehler = []
    for name, eintrag in tabelle.items():
        ort = f"SCHWIERIGKEIT[{name!r}]"
        falsch = pruefe_schluessel(ort, eintrag, SCHWIERIGKEIT_SCHLUESSEL)
        falsch = falsch or pruefe_schluessel(f"{ort} start", eintrag["start"], {"gold", "stein"})
        if falsch:
            fehler += falsch
            continue
        for wert in ("leben_faktor", "budget_faktor", "dorf_leben"):
            if not ist_zahl(eintrag[wert]) or eintrag[wert] <= 0:
                fehler.append(f"{ort}: {wert} muss größer als 0 sein")
    return fehler


def pruefe_dorf(katalog):
    fehler = []
    for gebaeude, eintrag in katalog.items():
        ort = f"DORFGEBAEUDE[{gebaeude!r}]"
        falsch = pruefe_schluessel(ort, eintrag, DORF_SCHLUESSEL)
        if falsch:
            fehler += falsch
            continue
        if not 3 <= len(eintrag["stufen"]) <= 5:
            fehler.append(f"{ort}: braucht drei bis fünf Stufen")
        for nummer, stufe in enumerate(eintrag["stufen"], start=1):
            wo = f"{ort} Stufe {nummer}"
            falsch = pruefe_schluessel(wo, stufe, DORFSTUFE_SCHLUESSEL)
            if falsch:
                fehler += falsch
                continue
            fehler += pruefe_kosten(f"{wo} kosten", stufe["kosten"])
            if not stufe["boni"]:
                fehler.append(f"{wo}: bringt keinen Bonus")
            for bonus, wert in stufe["boni"].items():
                if bonus not in BONI:
                    fehler.append(f"{wo}: unbekannter Bonus {bonus!r}")
                elif not ist_zahl(wert):
                    fehler.append(f"{wo}: Bonus {bonus} braucht eine Zahl")
            fehler += pruefe_braucht(wo, gebaeude, stufe["braucht"], katalog)
    return fehler


def pruefe_braucht(ort, gebaeude, braucht, katalog):
    """Jede Voraussetzung nennt ein anderes Dorfgebäude und eine Stufe, die es dort gibt."""
    fehler = []
    for anderes, stufe in braucht.items():
        if anderes not in katalog:
            fehler.append(f"{ort}: braucht das unbekannte Gebäude {anderes!r}")
        elif anderes == gebaeude:
            fehler.append(f"{ort}: braucht sich selbst")
        elif not isinstance(stufe, int) or isinstance(stufe, bool):
            fehler.append(f"{ort}: braucht {anderes} mit einer Stufe, die keine ganze Zahl ist")
        elif not 1 <= stufe <= len(katalog[anderes].get("stufen", [])):
            fehler.append(f"{ort}: braucht {anderes} Stufe {stufe}, die es nicht gibt")
    return fehler


def finde_kreis(katalog):
    """Sucht einen Kreis in den Voraussetzungen und gibt ihn als Liste von Käufen zurück.

    Ein Kauf ist ``(gebaeude, stufe)``. Jeder Kauf braucht die Stufe davor und alles, was in
    ``braucht`` steht. Ein Kreis hieße: Man könnte keinen dieser Käufe als ersten machen.
    Ohne Kreis ist das Ergebnis eine leere Liste.
    """

    def davor(kauf):
        gebaeude, stufe = kauf
        stufen = katalog.get(gebaeude, {}).get("stufen", [])
        if not 1 <= stufe <= len(stufen):
            return []
        vorher = [(gebaeude, stufe - 1)] if stufe > 1 else []
        return vorher + sorted(stufen[stufe - 1].get("braucht", {}).items())

    fertig = set()

    def suche(kauf, weg):
        if kauf in weg:
            return weg[weg.index(kauf) :] + [kauf]
        if kauf in fertig:
            return []
        for naechster in davor(kauf):
            kreis = suche(naechster, weg + [kauf])
            if kreis:
                return kreis
        fertig.add(kauf)
        return []

    for gebaeude in sorted(katalog):
        for stufe in range(1, len(katalog[gebaeude].get("stufen", [])) + 1):
            kreis = suche((gebaeude, stufe), [])
            if kreis:
                return kreis
    return []


def pruefe_zauber(zauber, kirchenstufen):
    fehler = []
    for name, eintrag in zauber.items():
        ort = f"ZAUBER[{name!r}]"
        falsch = pruefe_schluessel(ort, eintrag, ZAUBER_SCHLUESSEL)
        if falsch:
            fehler += falsch
            continue
        klasse = eintrag["klasse"]
        if klasse not in ZAUBERKLASSEN:
            fehler.append(f"{ort}: unbekannte Klasse {klasse!r}")
            continue
        frei = eintrag["frei_ab_kirche"]
        if not isinstance(frei, int) or isinstance(frei, bool) or not 1 <= frei <= kirchenstufen:
            fehler.append(f"{ort}: frei_ab_kirche muss eine Stufe der Kirche sein")
        if not isinstance(eintrag["braucht_ziel"], bool):
            fehler.append(f"{ort}: braucht_ziel muss True oder False sein")
        if len(eintrag["stufen"]) != 3:
            fehler.append(f"{ort}: braucht genau drei Stufen")
        if len(eintrag["ausbau_kosten"]) != 2:
            fehler.append(f"{ort}: braucht genau zwei Ausbaupreise")
        for nummer, kosten in enumerate(eintrag["ausbau_kosten"], start=2):
            fehler += pruefe_kosten(f"{ort} Ausbau auf Stufe {nummer}", kosten)
        for nummer, werte in enumerate(eintrag["stufen"], start=1):
            wo = f"{ort} Stufe {nummer}"
            if set(werte) != ZAUBERKLASSEN[klasse]:
                fehler.append(f"{wo}: die Werte passen nicht zur Klasse {klasse}")
                continue
            if not all(ist_zahl(wert) for wert in werte.values()):
                fehler.append(f"{wo}: alle Werte müssen Zahlen sein")
            elif werte["kosten"] <= 0 or werte["abklingzeit"] <= 0:
                fehler.append(f"{wo}: Kosten und Abklingzeit müssen größer als 0 sein")
    return fehler


def lies_zeilen(text):
    """Die Zeilen einer Kartendatei; leere Zeilen und Leerzeichen am Ende zählen nicht."""
    return [zeile.rstrip() for zeile in text.splitlines() if zeile.rstrip()]


def pruefe_karte(text):
    """Die Kartenregeln, die diese Aufgabe nennt, und dazu: Jedes Orktor erreicht das Dorftor."""
    zeilen = lies_zeilen(text)
    if len(zeilen) != ZEILEN:
        return [f"{len(zeilen)} Zeilen statt {ZEILEN}"]
    fehler = []
    for nummer, zeile in enumerate(zeilen):
        if len(zeile) != SPALTEN:
            fehler.append(f"Zeile {nummer}: {len(zeile)} Zeichen statt {SPALTEN}")
        fehler += [
            f"Zeile {nummer}: unbekanntes Zeichen {zeichen!r}"
            for zeichen in sorted(set(zeile) - set(ZEICHEN))
        ]
    if fehler:
        return fehler
    for nummer, zeile in enumerate(zeilen):
        for spalte, zeichen in enumerate(zeile):
            if spalte >= DORF_AB_SPALTE and zeichen != "D":
                fehler.append(f"Zelle ({spalte}, {nummer}): hier muss Dorfgrund sein")
            if spalte < DORF_AB_SPALTE and zeichen == "D":
                fehler.append(f"Zelle ({spalte}, {nummer}): Dorfgrund außerhalb des Dorfes")
    ziele = finde(zeilen, "Z")
    starts = finde(zeilen, "S")
    if len(ziele) != 1:
        fehler.append(f"{len(ziele)} Dorftore statt genau einem")
    if not starts:
        fehler.append("kein Orktor")
    if len(ziele) == 1:
        erreichbar = erreichbare_zellen(zeilen, ziele[0])
        fehler += [
            f"Orktor {start}: kein Weg zum Dorftor" for start in starts if start not in erreichbar
        ]
    return fehler


def finde(zeilen, zeichen):
    return [
        (spalte, nummer)
        for nummer, zeile in enumerate(zeilen)
        for spalte, inhalt in enumerate(zeile)
        if inhalt == zeichen
    ]


def erreichbare_zellen(zeilen, ziel):
    """Alle Zellen, von denen aus man über begehbares Gelände zum Ziel kommt."""
    gesehen = {ziel}
    offen = collections.deque([ziel])
    while offen:
        spalte, zeile = offen.popleft()
        for nachbar in (
            (spalte, zeile - 1),
            (spalte + 1, zeile),
            (spalte, zeile + 1),
            (spalte - 1, zeile),
        ):
            x, y = nachbar
            if nachbar in gesehen or not (0 <= x < SPALTEN and 0 <= y < ZEILEN):
                continue
            if zeilen[y][x] in BEGEHBAR:
                gesehen.add(nachbar)
                offen.append(nachbar)
    return gesehen


def rand(zelle):
    """An welchem Rand der Karte eine Zelle liegt (oder ``None``)."""
    spalte, zeile = zelle
    if zeile == 0:
        return "oben"
    if zeile == ZEILEN - 1:
        return "unten"
    if spalte == 0:
        return "links"
    return None


def lies_karte(name):
    return (KARTEN_ORDNER / f"{name}.txt").read_text(encoding="utf-8")


# --- Die echten Daten ----------------------------------------------------------------------


class Tabellen(unittest.TestCase):
    def test_spielfeld_und_gelaende(self):
        self.assertEqual(
            (24, 16, 6, 40), (daten.SPALTEN, daten.ZEILEN, daten.DORF_SPALTEN, daten.ZELLE)
        )
        self.assertEqual((1 / 60, 1 / 20), (daten.DT, daten.LABOR_DT))
        self.assertEqual(
            (1280, 720, 80, 320),
            (daten.BILD_BREITE, daten.BILD_HOEHE, daten.LEISTE_HOEHE, daten.SEITE_BREITE),
        )
        self.assertEqual(
            (960, 640, (0, 80)), (daten.KARTE_BREITE, daten.KARTE_HOEHE, daten.KARTE_ECKE)
        )
        self.assertEqual(set(ZEICHEN), set(daten.GELAENDE))
        self.assertEqual((BEGEHBAR, ".^"), (daten.BEGEHBAR, daten.BEBAUBAR))
        self.assertEqual((0.5, 1.25), (daten.SUMPF_TEMPO_FAKTOR, daten.HUEGEL_REICHWEITE_FAKTOR))
        self.assertEqual(SCHADENSARTEN, set(daten.SCHADENSARTEN))
        self.assertEqual(KARTEN, daten.KARTEN)
        self.assertEqual("flusstal", daten.STANDARD_KARTE)

    def test_bauwerke(self):
        self.assertEqual(
            {"pfeil", "kanone", "frost", "gift", "blitz", "palisade"}, set(daten.BAUWERKE)
        )
        self.assertEqual([], pruefe_bauwerke(daten.BAUWERKE))

    def test_jeder_turm_hat_stufe_zwei_und_zwei_meister(self):
        for art, eintrag in daten.BAUWERKE.items():
            with self.subTest(art=art):
                if art == "palisade":
                    self.assertEqual(
                        ({}, [], {}), (eintrag["werte"], eintrag["ausbau"], eintrag["meister"])
                    )
                    continue
                stufe_2 = {"schaden": ("*", 1.6), "reichweite": ("+", 15)}
                self.assertEqual([stufe_2], eintrag["ausbau"])
                self.assertEqual(2, len(eintrag["meister"]))
                self.assertIsInstance(eintrag["werte"]["trifft_luft"], bool)

    def test_ausbau_listen_gehoeren_jedem_turm_allein(self):
        listen = [
            id(eintrag["ausbau"][0]) for eintrag in daten.BAUWERKE.values() if eintrag["ausbau"]
        ]
        self.assertEqual(
            len(listen), len(set(listen)), "Zwei Türme teilen sich dasselbe Wörterbuch"
        )

    def test_gegner(self):
        self.assertEqual(12, len(daten.GEGNER))
        self.assertEqual([], pruefe_gegner(daten.GEGNER))

    def test_wellenschmiede_kauft_nur_was_sie_darf(self):
        # Die ganze Tabelle geht als Katalog an die Mission 15, auch im Endlosmodus.
        reich = 10**9
        self.assertEqual(["ork"], kaufbar(daten.GEGNER, 1, reich))
        self.assertEqual([], kaufbar(daten.GEGNER, 1, 4))
        alle = sorted(set(daten.GEGNER) - NIE_GEKAUFT - {"orkkoenig"})
        for nummer in (12, 20, 21, 1000, 1_000_000):
            with self.subTest(welle=nummer):
                self.assertEqual(alle, kaufbar(daten.GEGNER, nummer, reich))
        for art in NIE_GEKAUFT:
            eltern = [name for name, eintrag in daten.GEGNER.items() if art in eintrag["teilt_in"]]
            self.assertTrue(eltern, f"{art} entsteht aus keinem anderen Gegner")

    def test_wellenformeln(self):
        self.assertEqual(28, daten.wellen_budget(1, 1.0))
        self.assertEqual(198, daten.wellen_budget(10, 1.0))
        self.assertEqual(558, daten.wellen_budget(20, 1.0))
        self.assertEqual(round(198 * 1.5), daten.wellen_budget(10, 1.5))
        self.assertEqual(1.0, daten.wellen_leben_faktor(1))
        self.assertAlmostEqual(1.54, daten.wellen_leben_faktor(10))
        self.assertAlmostEqual(1.07, daten.spawn_abstand(1))
        self.assertAlmostEqual(0.5, daten.spawn_abstand(20))
        self.assertEqual(0.25, daten.spawn_abstand(40))
        self.assertEqual(20, daten.KAMPAGNE_WELLEN)

    def test_schwierigkeit(self):
        self.assertEqual(["leicht", "normal", "schwer", "albtraum"], list(daten.SCHWIERIGKEIT))
        self.assertEqual([], pruefe_schwierigkeit(daten.SCHWIERIGKEIT))

    def test_dorf(self):
        stufen = {name: len(eintrag["stufen"]) for name, eintrag in daten.DORFGEBAEUDE.items()}
        self.assertEqual(DORFLINIEN, stufen)
        self.assertEqual([], pruefe_dorf(daten.DORFGEBAEUDE))

    def test_dorf_hat_keinen_kreis(self):
        self.assertEqual([], finde_kreis(daten.DORFGEBAEUDE))

    def test_kirche_laeutet_ab_stufe_vier(self):
        stufen = daten.DORFGEBAEUDE["kirche"]["stufen"]
        intervalle = [stufe["boni"].get("glocken_intervall", 0) for stufe in stufen]
        self.assertEqual([0, 0, 0, 40, -15], intervalle)

    def test_zauber(self):
        klassen = {eintrag["klasse"] for eintrag in daten.ZAUBER.values()}
        self.assertEqual(set(ZAUBERKLASSEN), klassen)
        kirchenstufen = len(daten.DORFGEBAEUDE["kirche"]["stufen"])
        self.assertEqual([], pruefe_zauber(daten.ZAUBER, kirchenstufen))


class Karten(unittest.TestCase):
    def test_es_gibt_genau_die_fuenf_karten(self):
        dateien = sorted(datei.name for datei in KARTEN_ORDNER.iterdir())
        self.assertEqual(sorted(f"{name}.txt" for name in KARTEN), dateien)

    def test_jede_karte_haelt_die_regeln_ein(self):
        for name in KARTEN:
            with self.subTest(karte=name):
                self.assertEqual([], pruefe_karte(lies_karte(name)))

    def test_dorftor_liegt_am_dorf(self):
        for name in KARTEN:
            with self.subTest(karte=name):
                (spalte, _zeile) = finde(lies_zeilen(lies_karte(name)), "Z")[0]
                self.assertEqual(DORF_AB_SPALTE - 1, spalte)

    def test_zwei_tore_hat_zwei_orktore_an_verschiedenen_raendern(self):
        starts = finde(lies_zeilen(lies_karte("zwei_tore")), "S")
        self.assertEqual(2, len(starts))
        raender = {rand(start) for start in starts}
        self.assertEqual(2, len(raender - {None}), f"Orktore bei {starts}")

    def test_flusstal_hat_einen_fluss_mit_zwei_furten(self):
        zeilen = lies_zeilen(lies_karte("flusstal"))
        self.assertEqual(1, len(finde(zeilen, "S")))
        # Eine Furt ist eine Zeile, in der man von links nach rechts kommt, ohne zu schwimmen.
        furten = [nummer for nummer, zeile in enumerate(zeilen) if "~" not in zeile]
        self.assertEqual(2, len(furten), f"Zeilen ohne Wasser: {furten}")
        self.assertGreaterEqual(sum("~" in zeile for zeile in zeilen), 12)


# --- Selbsttest: Jede Prüfung findet ihren Fehler ------------------------------------------

LEERE_KARTE = ["." * DORF_AB_SPALTE + "D" * (SPALTEN - DORF_AB_SPALTE) for _ in range(ZEILEN)]


def karte_mit(*aenderungen):
    """Eine gültige Karte (Orktor links, Dorftor rechts), in der einzelne Zellen ersetzt sind."""
    zeilen = [list(zeile) for zeile in LEERE_KARTE]
    for (spalte, zeile), zeichen in (((0, 7), "S"), ((17, 8), "Z")) + aenderungen:
        zeilen[zeile][spalte] = zeichen
    return "\n".join("".join(zeile) for zeile in zeilen) + "\n"


class SelbsttestKarten(unittest.TestCase):
    def test_gueltige_karte(self):
        self.assertEqual([], pruefe_karte(karte_mit()))

    def test_falsche_zeilenzahl(self):
        text = karte_mit()
        self.assertEqual(["15 Zeilen statt 16"], pruefe_karte(text[: -(SPALTEN + 1)]))
        self.assertEqual(["17 Zeilen statt 16"], pruefe_karte(text + LEERE_KARTE[0] + "\n"))

    def test_falsche_zeilenlaenge(self):
        zeilen = karte_mit().splitlines()
        zeilen[3] = zeilen[3] + "D"
        self.assertEqual(["Zeile 3: 25 Zeichen statt 24"], pruefe_karte("\n".join(zeilen)))
        zeilen[3] = zeilen[3][:-2]
        self.assertEqual(["Zeile 3: 23 Zeichen statt 24"], pruefe_karte("\n".join(zeilen)))

    def test_unbekanntes_zeichen(self):
        fehler = pruefe_karte(karte_mit(((4, 2), "X")))
        self.assertEqual(["Zeile 2: unbekanntes Zeichen 'X'"], fehler)

    def test_dorftor(self):
        ohne = pruefe_karte(karte_mit(((17, 8), ".")))
        self.assertEqual(["0 Dorftore statt genau einem"], ohne)
        zwei = pruefe_karte(karte_mit(((17, 2), "Z")))
        self.assertEqual(["2 Dorftore statt genau einem"], zwei)

    def test_kein_orktor(self):
        self.assertEqual(["kein Orktor"], pruefe_karte(karte_mit(((0, 7), "."))))

    def test_dorfgrund_nur_in_den_dorfspalten(self):
        for spalte in (18, 23):
            with self.subTest(spalte=spalte):
                fehler = pruefe_karte(karte_mit(((spalte, 5), ".")))
                self.assertEqual([f"Zelle ({spalte}, 5): hier muss Dorfgrund sein"], fehler)
        for spalte in (0, 17):
            with self.subTest(spalte=spalte):
                fehler = pruefe_karte(karte_mit(((spalte, 5), "D")))
                self.assertEqual([f"Zelle ({spalte}, 5): Dorfgrund außerhalb des Dorfes"], fehler)

    def test_orktor_ohne_weg(self):
        mauer = tuple(((5, zeile), "#") for zeile in range(ZEILEN))
        self.assertEqual(["Orktor (0, 7): kein Weg zum Dorftor"], pruefe_karte(karte_mit(*mauer)))
        wasser = tuple(((5, zeile), "~") for zeile in range(ZEILEN))
        self.assertEqual(["Orktor (0, 7): kein Weg zum Dorftor"], pruefe_karte(karte_mit(*wasser)))
        furt = tuple(((5, zeile), "~") for zeile in range(ZEILEN) if zeile != 12)
        self.assertEqual([], pruefe_karte(karte_mit(*furt, ((5, 12), "%"))))

    def test_nur_das_abgeschnittene_orktor_wird_gemeldet(self):
        kaefig = (((9, 0), "S"), ((8, 0), "#"), ((10, 0), "#"), ((9, 1), "#"))
        self.assertEqual(["Orktor (9, 0): kein Weg zum Dorftor"], pruefe_karte(karte_mit(*kaefig)))

    def test_rand(self):
        self.assertEqual(
            ["oben", "unten", "links", None], [rand(z) for z in ((9, 0), (9, 15), (0, 7), (9, 7))]
        )


class SelbsttestTabellen(unittest.TestCase):
    """Jeder Fall verändert eine Kopie der echten Tabelle an genau einer Stelle."""

    def test_bauwerk_fehler(self):
        def aendere(aenderung):
            kopie = copy.deepcopy(daten.BAUWERKE)
            aenderung(kopie)
            return pruefe_bauwerke(kopie)

        def meister(kopie):
            return kopie["pfeil"]["meister"]["schnellfeuer"]

        faelle = {
            "Schlüssel fehlt": (
                lambda k: k["pfeil"].pop("farbe"),
                ["BAUWERKE['pfeil']: Schlüssel 'farbe' fehlt"],
            ),
            "Schlüssel zu viel": (
                lambda k: k["pfeil"].update(extra=1),
                ["BAUWERKE['pfeil']: Schlüssel 'extra' ist unbekannt"],
            ),
            "kostenlos": (
                lambda k: k["palisade"].update(kosten={"gold": 0, "stein": 0}),
                ["BAUWERKE['palisade'] kosten: kostet nichts"],
            ),
            "negativer Preis": (
                lambda k: k["frost"]["kosten"].update(gold=-1),
                ["BAUWERKE['frost'] kosten: gold muss eine ganze Zahl ab 0 sein"],
            ),
            "Schadensart": (
                lambda k: k["gift"]["werte"].update(art="saeure"),
                ["BAUWERKE['gift']: unbekannte Schadensart 'saeure'"],
            ),
            "Turm ohne Nachladezeit": (
                lambda k: k["kanone"]["werte"].pop("nachladezeit"),
                ["BAUWERKE['kanone']: Wert 'nachladezeit' fehlt"],
            ),
            "Turm ohne Reichweite": (
                lambda k: k["frost"]["werte"].pop("reichweite"),
                [
                    "BAUWERKE['frost']: Wert 'reichweite' fehlt",
                    "BAUWERKE['frost'] Stufe 2: reichweite gibt es bei diesem Turm nicht",
                ],
            ),
            "Turm ohne besonderen Wert": (
                lambda k: k["gift"]["werte"].pop("gift_dauer"),
                ["BAUWERKE['gift']: Wert 'gift_dauer' fehlt"],
            ),
            "Turm mit fremdem Wert": (
                lambda k: k["pfeil"]["werte"].update(radius=10),
                ["BAUWERKE['pfeil']: Wert 'radius' ist unbekannt"],
            ),
            "Nachladezeit 0": (
                lambda k: k["blitz"]["werte"].update(nachladezeit=0),
                ["BAUWERKE['blitz']: nachladezeit muss größer als 0 sein"],
            ),
            "trifft_luft ist keine Wahrheit": (
                lambda k: k["kanone"]["werte"].update(trifft_luft=0),
                ["BAUWERKE['kanone']: trifft_luft muss True oder False sein"],
            ),
            "Palisade mit Werten": (
                lambda k: k["palisade"]["werte"].update(schaden=1),
                ["BAUWERKE['palisade']: eine Palisade hat keine Werte"],
            ),
            "Ausbauzeichen": (
                lambda k: k["blitz"]["ausbau"][0].update(schaden=("-", 2)),
                ["BAUWERKE['blitz'] Stufe 2: schaden hat das unbekannte Zeichen '-'"],
            ),
            "Ausbau ohne Paar": (
                lambda k: k["blitz"]["ausbau"][0].update(schaden=1.6),
                ["BAUWERKE['blitz'] Stufe 2: schaden braucht ein Paar (Zeichen, Zahl)"],
            ),
            "Ausbau eines fehlenden Wertes": (
                lambda k: meister(k).update(ausbau={"radius": ("*", 2)}),
                ["BAUWERKE['pfeil'] Meister 'schnellfeuer': radius gibt es bei diesem Turm nicht"],
            ),
            "Meister ohne Schlüssel": (
                lambda k: meister(k).pop("kurz"),
                ["BAUWERKE['pfeil'] Meister 'schnellfeuer': Schlüssel 'kurz' fehlt"],
            ),
            "Meister mit Schmiede 4": (
                lambda k: meister(k).update(braucht_schmiede=4),
                [
                    "BAUWERKE['pfeil'] Meister 'schnellfeuer': braucht_schmiede muss 1, 2 oder 3 sein"
                ],
            ),
            "Meister ohne Ausbau": (
                lambda k: meister(k).update(ausbau={}),
                [
                    "BAUWERKE['pfeil'] Meister 'schnellfeuer': "
                    "muss ein Wörterbuch mit mindestens einem Wert sein"
                ],
            ),
        }
        for name, (aenderung, erwartet) in faelle.items():
            with self.subTest(fall=name):
                self.assertEqual(erwartet, aendere(aenderung))

    def test_gegner_fehler(self):
        def aendere(aenderung):
            kopie = copy.deepcopy(daten.GEGNER)
            aenderung(kopie)
            return pruefe_gegner(kopie)

        faelle = {
            "Schlüssel fehlt": (
                lambda k: k["ork"].pop("groesse"),
                ["GEGNER['ork']: Schlüssel 'groesse' fehlt"],
            ),
            "kein Leben": (
                lambda k: k["wolf"].update(leben=0),
                ["GEGNER['wolf']: leben muss größer als 0 sein"],
            ),
            "boss ist keine Wahrheit": (
                lambda k: k["wolf"].update(boss=0),
                ["GEGNER['wolf']: boss muss True oder False sein"],
            ),
            "Resistenz gegen Unbekanntes": (
                lambda k: k["oger"].update(resistenzen={"eis": 0.5}),
                ["GEGNER['oger']: unbekannte Schadensart 'eis'"],
            ),
            "unbekannte Fähigkeit": (
                lambda k: k["troll"].update(faehigkeiten=[("Unsichtbar", {})]),
                ["GEGNER['troll']: unbekannte Fähigkeit 'Unsichtbar'"],
            ),
            "Fähigkeit mit falschem Wert": (
                lambda k: k["troll"].update(faehigkeiten=[("Regeneration", {"menge": 12})]),
                ["GEGNER['troll']: Regeneration hat falsche Werte ['menge']"],
            ),
            "Fähigkeit ohne Pflichtwert": (
                lambda k: k["schamane"].update(faehigkeiten=[("Heiler", {"radius": 90})]),
                ["GEGNER['schamane']: Heiler hat falsche Werte ['radius']"],
            ),
            "beschwört Unbekanntes": (
                lambda k: k["orkkoenig"]["faehigkeiten"][0][1].update(art="drache"),
                ["GEGNER['orkkoenig']: beschwört unbekannte Art 'drache'"],
            ),
            "teilt in Unbekanntes": (
                lambda k: k["schleim"].update(teilt_in=["schleimling", "tropfen"]),
                ["GEGNER['schleim']: teilt_in nennt unbekannte Art 'tropfen'"],
            ),
            "teilt in sich selbst": (
                lambda k: k["schleimling"].update(teilt_in=["schleimling"]),
                ["GEGNER['schleimling']: teilt sich in sich selbst"],
            ),
            "Preis 0": (
                lambda k: k["oger"].update(preis=0),
                ["GEGNER['oger']: preis muss größer als 0 sein"],
            ),
            "Preis keine ganze Zahl": (
                lambda k: k["oger"].update(preis=16.5),
                ["GEGNER['oger']: preis muss eine ganze Zahl sein"],
            ),
            "ab_welle 0 ohne Teilen": (
                lambda k: k["geist"].update(ab_welle=0),
                ["GEGNER['geist']: ab_welle muss größer als 0 sein"],
            ),
            "ab_welle 0 beim Teilstück": (
                lambda k: k["schleimling"].update(ab_welle=0),
                ["GEGNER['schleimling']: ab_welle muss größer als 0 sein"],
            ),
            "ab_welle ist True": (
                lambda k: k["wolf"].update(ab_welle=True),
                ["GEGNER['wolf']: ab_welle muss eine ganze Zahl sein"],
            ),
            "Boss ohne Welle": (
                lambda k: k["orkkoenig"].update(ab_welle=0),
                ["GEGNER['orkkoenig']: ab_welle muss größer als 0 sein"],
            ),
            "Boss ohne Preis": (
                lambda k: k["orkkoenig"].update(preis=0),
                ["GEGNER['orkkoenig']: preis muss größer als 0 sein"],
            ),
        }
        for name, (aenderung, erwartet) in faelle.items():
            with self.subTest(fall=name):
                self.assertEqual(erwartet, aendere(aenderung))

    def test_teilstueck_mit_frueher_welle_waere_kaufbar(self):
        # Mit einer 0 statt NIE_VON_SELBST würde die Wellenschmiede Schleimlinge kaufen.
        kopie = copy.deepcopy(daten.GEGNER)
        kopie["schleimling"]["ab_welle"] = 0
        self.assertEqual(["schleimling"], kaufbar(kopie, 1, 4))
        self.assertEqual(["ork", "schleimling"], kaufbar(kopie, 1, 5))
        boss = copy.deepcopy(daten.GEGNER)
        boss["orkkoenig"]["boss"] = False
        self.assertIn("orkkoenig", kaufbar(boss, 10, 10**9))

    def test_schwierigkeit_fehler(self):
        kopie = copy.deepcopy(daten.SCHWIERIGKEIT)
        kopie["leicht"].pop("dorf_leben")
        kopie["normal"]["start"].pop("stein")
        kopie["schwer"]["budget_faktor"] = 0
        erwartet = [
            "SCHWIERIGKEIT['leicht']: Schlüssel 'dorf_leben' fehlt",
            "SCHWIERIGKEIT['normal'] start: Schlüssel 'stein' fehlt",
            "SCHWIERIGKEIT['schwer']: budget_faktor muss größer als 0 sein",
        ]
        self.assertEqual(erwartet, pruefe_schwierigkeit(kopie))

    def test_dorf_fehler(self):
        def aendere(aenderung):
            kopie = copy.deepcopy(daten.DORFGEBAEUDE)
            aenderung(kopie)
            return pruefe_dorf(kopie)

        def stufe(kopie, gebaeude, nummer):
            return kopie[gebaeude]["stufen"][nummer - 1]

        faelle = {
            "Gebäude ohne Stufen": (
                lambda k: k["schmiede"].pop("stufen"),
                ["DORFGEBAEUDE['schmiede']: Schlüssel 'stufen' fehlt"],
            ),
            "nur zwei Stufen": (
                lambda k: k["steinbruch"]["stufen"].pop(),
                ["DORFGEBAEUDE['steinbruch']: braucht drei bis fünf Stufen"],
            ),
            "Stufe ohne Kosten": (
                lambda k: stufe(k, "mauer", 2).pop("kosten"),
                ["DORFGEBAEUDE['mauer'] Stufe 2: Schlüssel 'kosten' fehlt"],
            ),
            "Stufe ohne braucht": (
                lambda k: stufe(k, "haeuser", 1).pop("braucht"),
                ["DORFGEBAEUDE['haeuser'] Stufe 1: Schlüssel 'braucht' fehlt"],
            ),
            "Stufe ohne Boni": (
                lambda k: stufe(k, "haeuser", 5).pop("boni"),
                ["DORFGEBAEUDE['haeuser'] Stufe 5: Schlüssel 'boni' fehlt"],
            ),
            "leere Boni": (
                lambda k: stufe(k, "schmiede", 3).update(boni={}),
                ["DORFGEBAEUDE['schmiede'] Stufe 3: bringt keinen Bonus"],
            ),
            "unbekannter Bonus": (
                lambda k: stufe(k, "schmiede", 1)["boni"].update(glueck=1),
                ["DORFGEBAEUDE['schmiede'] Stufe 1: unbekannter Bonus 'glueck'"],
            ),
            "kostenlos": (
                lambda k: stufe(k, "kirche", 1).update(kosten={"gold": 0, "stein": 0}),
                ["DORFGEBAEUDE['kirche'] Stufe 1 kosten: kostet nichts"],
            ),
            "braucht unbekanntes Gebäude": (
                lambda k: stufe(k, "kirche", 2).update(braucht={"einwohner": 30}),
                ["DORFGEBAEUDE['kirche'] Stufe 2: braucht das unbekannte Gebäude 'einwohner'"],
            ),
            "braucht eine zu hohe Stufe": (
                lambda k: stufe(k, "kirche", 5)["braucht"].update(bauhuette=4),
                ["DORFGEBAEUDE['kirche'] Stufe 5: braucht bauhuette Stufe 4, die es nicht gibt"],
            ),
            "braucht Stufe 0": (
                lambda k: stufe(k, "mauer", 2).update(braucht={"steinbruch": 0}),
                ["DORFGEBAEUDE['mauer'] Stufe 2: braucht steinbruch Stufe 0, die es nicht gibt"],
            ),
            "braucht sich selbst": (
                lambda k: stufe(k, "markt", 3).update(braucht={"markt": 2}),
                ["DORFGEBAEUDE['markt'] Stufe 3: braucht sich selbst"],
            ),
        }
        for name, (aenderung, erwartet) in faelle.items():
            with self.subTest(fall=name):
                self.assertEqual(erwartet, aendere(aenderung))

    def test_kreis_wird_gefunden(self):
        def stufe(**braucht):
            return {"name": "x", "kosten": {"gold": 1, "stein": 0}, "braucht": braucht, "boni": {}}

        direkt = {"a": {"stufen": [stufe(b=1)]}, "b": {"stufen": [stufe(a=1)]}}
        self.assertEqual([("a", 1), ("b", 1), ("a", 1)], finde_kreis(direkt))
        # Der Kreis läuft über die Stufe davor: a1 braucht b1, b1 braucht a2, a2 braucht a1.
        ueber_stufen = {"a": {"stufen": [stufe(b=1), stufe()]}, "b": {"stufen": [stufe(a=2)]}}
        self.assertEqual([("a", 1), ("b", 1), ("a", 2), ("a", 1)], finde_kreis(ueber_stufen))
        # Kein Kreis: a2 braucht b1, und b2 braucht a2. Das geht der Reihe nach.
        verzahnt = {"a": {"stufen": [stufe(), stufe(b=1)]}, "b": {"stufen": [stufe(), stufe(a=2)]}}
        self.assertEqual([], finde_kreis(verzahnt))

    def test_kreis_in_den_echten_daten_wird_gefunden(self):
        # Die Bauhütte 3 braucht die Kirche 3. Bräuchte die Kirche 3 die Bauhütte 3, ginge nichts mehr.
        kopie = copy.deepcopy(daten.DORFGEBAEUDE)
        kopie["kirche"]["stufen"][2]["braucht"]["bauhuette"] = 3
        kreis = finde_kreis(kopie)
        self.assertEqual(kreis[0], kreis[-1])
        self.assertEqual({("kirche", 3), ("bauhuette", 3)}, set(kreis))
        # Und eine Stufe höher: Die Kirche 4 braucht die Bauhütte 2; die darf die Kirche 4 nicht brauchen.
        kopie = copy.deepcopy(daten.DORFGEBAEUDE)
        kopie["bauhuette"]["stufen"][1]["braucht"]["kirche"] = 4
        self.assertEqual({("kirche", 4), ("bauhuette", 2)}, set(finde_kreis(kopie)))
        # Über die Stufe davor: Die Kirche 3 braucht den Steinbruch 1; der darf die Kirche 4 nicht brauchen.
        kopie = copy.deepcopy(daten.DORFGEBAEUDE)
        kopie["steinbruch"]["stufen"][0]["braucht"]["kirche"] = 4
        self.assertEqual({("kirche", 3), ("kirche", 4), ("steinbruch", 1)}, set(finde_kreis(kopie)))

    def test_zauber_fehler(self):
        def aendere(aenderung):
            kopie = copy.deepcopy(daten.ZAUBER)
            aenderung(kopie)
            return pruefe_zauber(kopie, 5)

        faelle = {
            "Schlüssel fehlt": (
                lambda k: k["segen"].pop("braucht_ziel"),
                ["ZAUBER['segen']: Schlüssel 'braucht_ziel' fehlt"],
            ),
            "unbekannte Klasse": (
                lambda k: k["segen"].update(klasse="Wunder"),
                ["ZAUBER['segen']: unbekannte Klasse 'Wunder'"],
            ),
            "Kirche 6": (
                lambda k: k["glockenschlag"].update(frei_ab_kirche=6),
                ["ZAUBER['glockenschlag']: frei_ab_kirche muss eine Stufe der Kirche sein"],
            ),
            "zwei Stufen": (
                lambda k: k["eissturm"]["stufen"].pop(),
                ["ZAUBER['eissturm']: braucht genau drei Stufen"],
            ),
            "ein Ausbaupreis": (
                lambda k: k["eissturm"]["ausbau_kosten"].pop(),
                ["ZAUBER['eissturm']: braucht genau zwei Ausbaupreise"],
            ),
            "Wert fehlt": (
                lambda k: k["feuerball"]["stufen"][0].pop("brand_dauer"),
                ["ZAUBER['feuerball'] Stufe 1: die Werte passen nicht zur Klasse Feuerball"],
            ),
            "Wert zu viel": (
                lambda k: k["blitzschlag"]["stufen"][2].update(radius=10),
                ["ZAUBER['blitzschlag'] Stufe 3: die Werte passen nicht zur Klasse Blitzschlag"],
            ),
            "kostet kein Mana": (
                lambda k: k["segen"]["stufen"][1].update(kosten=0),
                ["ZAUBER['segen'] Stufe 2: Kosten und Abklingzeit müssen größer als 0 sein"],
            ),
        }
        for name, (aenderung, erwartet) in faelle.items():
            with self.subTest(fall=name):
                self.assertEqual(erwartet, aendere(aenderung))


if __name__ == "__main__":
    unittest.main()
