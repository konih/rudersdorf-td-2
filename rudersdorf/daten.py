"""Alle Zahlen und Tabellen des Spiels an einem Ort.

Hier steht, was es im Spiel gibt: Gelände, Türme, Gegner, Wellen, Schwierigkeitsgrade,
Dorfgebäude und Zauber. Der Spielkern liest diese Tabellen nur. Wer das Spiel verändern will
(ein stärkerer Turm, ein neuer Gegner, ein billigeres Gebäude), ändert hier eine Zahl und
keinen Programmcode.

Eine Zelle ist immer ``(spalte, zeile)``. Längen sind Pixel, Zeiten sind Sekunden.
"""

# --------------------------------------------------------------------------------------
# Spielfeld und Bildschirm
# --------------------------------------------------------------------------------------

SPALTEN = 24
ZEILEN = 16
DORF_SPALTEN = 6  # so viele Spalten ganz rechts gehören dem Dorf
ZELLE = 40  # Pixel pro Zelle
DT = 1 / 60  # fester Rechenschritt des Spiels
LABOR_DT = 1 / 20  # gröberer Schritt für das Labor und die langen Tests

BILD_BREITE = 1280
BILD_HOEHE = 720
LEISTE_HOEHE = 80  # obere Leiste
SEITE_BREITE = 320  # Seitenleiste rechts
KARTE_BREITE = SPALTEN * ZELLE  # 960
KARTE_HOEHE = ZEILEN * ZELLE  # 640
KARTE_ECKE = (0, LEISTE_HOEHE)  # linke obere Ecke der Karte auf dem Bildschirm

# Die Zeichen der Kartendateien im Ordner karten/.
GELAENDE = {
    ".": "Wiese",
    "#": "Fels",
    "~": "Wasser",
    "%": "Sumpf",
    "^": "Hügel",
    "S": "Orktor",
    "Z": "Dorftor",
    "D": "Dorfgrund",
}
BEGEHBAR = ".%^SZ"  # darüber können Gegner laufen
BEBAUBAR = ".^"  # darauf darf man bauen
SUMPF_TEMPO_FAKTOR = 0.5  # im Sumpf sind Gegner halb so schnell
HUEGEL_REICHWEITE_FAKTOR = 1.25  # ein Turm auf einem Hügel schießt weiter

KARTEN = ("flusstal", "zwei_tore", "felsenmeer", "weites_feld", "labor")
STANDARD_KARTE = "flusstal"

# --------------------------------------------------------------------------------------
# Schadensarten
# --------------------------------------------------------------------------------------

SCHADENSARTEN = ("stich", "wucht", "magie", "gift", "feuer")

# --------------------------------------------------------------------------------------
# Bauwerke auf dem Spielfeld
#
# "werte" sind die Werte der Stufe 1. Ein Eintrag in "ausbau" oder im "ausbau" eines Meisters
# sagt, wie sich ein Wert ändert: ("+", zahl) zählt dazu, ("*", zahl) nimmt mal,
# ("=", zahl) setzt den Wert neu.
# --------------------------------------------------------------------------------------

AUSBAU_KOSTEN_ANTEIL = 0.8  # Stufe 2 kostet 80 % des Kaufpreises in Gold
VERKAUF_ANTEIL = 0.6  # so viel vom ausgegebenen Gold gibt es beim Verkauf zurück
ABRISS_SEKUNDEN = {"palisade": 2.0, "turm": 5.0}  # so lange braucht ein Brecher

_STUFE_2 = {"schaden": ("*", 1.6), "reichweite": ("+", 15)}

BAUWERKE = {
    "pfeil": {
        "name": "Pfeilturm",
        "kurz": "Schießt schnell auf einen einzelnen Gegner.",
        "kosten": {"gold": 50, "stein": 0},
        "werte": {
            "schaden": 12,
            "art": "stich",
            "reichweite": 130,
            "nachladezeit": 0.7,
            "trifft_luft": True,
        },
        "ausbau": [dict(_STUFE_2)],
        "meister": {
            "scharfschuetze": {
                "name": "Scharfschütze",
                "kurz": "Schießt viel weiter und trifft viel härter.",
                "kosten": {"gold": 110, "stein": 15},
                "braucht_schmiede": 1,
                "ausbau": {"reichweite": ("*", 1.5), "schaden": ("*", 2.2)},
            },
            "schnellfeuer": {
                "name": "Schnellfeuer",
                "kurz": "Lädt mehr als doppelt so schnell nach.",
                "kosten": {"gold": 110, "stein": 15},
                "braucht_schmiede": 1,
                "ausbau": {"nachladezeit": ("*", 0.45)},
            },
        },
        "farbe": (156, 108, 62),
    },
    "kanone": {
        "name": "Kanonenturm",
        "kurz": "Trifft alle Gegner am Boden rund um den Einschlag.",
        "kosten": {"gold": 90, "stein": 0},
        "werte": {
            "schaden": 26,
            "art": "wucht",
            "reichweite": 150,
            "nachladezeit": 1.9,
            "radius": 55,
            "trifft_luft": False,
        },
        "ausbau": [dict(_STUFE_2)],
        "meister": {
            "moerser": {
                "name": "Mörser",
                "kurz": "Größerer Einschlag und mehr Reichweite.",
                "kosten": {"gold": 160, "stein": 25},
                "braucht_schmiede": 1,
                "ausbau": {"radius": ("*", 1.6), "reichweite": ("+", 40)},
            },
            "brandbombe": {
                "name": "Brandbombe",
                "kurz": "Getroffene Gegner brennen danach weiter.",
                "kosten": {"gold": 160, "stein": 25},
                "braucht_schmiede": 1,
                "ausbau": {"brand_dauer": ("=", 3.0), "brand_schaden": ("=", 10)},
            },
        },
        "farbe": (92, 92, 104),
    },
    "frost": {
        "name": "Frostturm",
        "kurz": "Macht Gegner für kurze Zeit langsam.",
        "kosten": {"gold": 70, "stein": 0},
        "werte": {
            "schaden": 4,
            "art": "magie",
            "reichweite": 115,
            "nachladezeit": 1.1,
            "frost_dauer": 2.0,
            "frost_faktor": 0.5,
            "trifft_luft": True,
        },
        "ausbau": [dict(_STUFE_2)],
        "meister": {
            "eiswind": {
                "name": "Eiswind",
                "kurz": "Bremst alle Gegner in der Nähe des Ziels.",
                "kosten": {"gold": 130, "stein": 20},
                "braucht_schmiede": 2,
                "ausbau": {"frost_radius": ("=", 60)},
            },
            "tiefkuehler": {
                "name": "Tiefkühler",
                "kurz": "Bremst stärker und länger.",
                "kosten": {"gold": 130, "stein": 20},
                "braucht_schmiede": 2,
                "ausbau": {"frost_faktor": ("=", 0.25), "frost_dauer": ("+", 1.5)},
            },
        },
        "farbe": (120, 190, 230),
    },
    "gift": {
        "name": "Giftturm",
        "kurz": "Vergiftet Gegner, die dann nach und nach Leben verlieren.",
        "kosten": {"gold": 80, "stein": 0},
        "werte": {
            "schaden": 2,
            "art": "gift",
            "reichweite": 120,
            "nachladezeit": 1.4,
            "gift_dauer": 4.0,
            "gift_schaden": 7,
            "trifft_luft": True,
        },
        "ausbau": [dict(_STUFE_2)],
        "meister": {
            "seuche": {
                "name": "Seuche",
                "kurz": "Das Gift wirkt mehr als doppelt so stark.",
                "kosten": {"gold": 140, "stein": 20},
                "braucht_schmiede": 2,
                "ausbau": {"gift_schaden": ("*", 2.2)},
            },
            "giftwolke": {
                "name": "Giftwolke",
                "kurz": "Vergiftet alle Gegner in der Nähe des Ziels.",
                "kosten": {"gold": 140, "stein": 20},
                "braucht_schmiede": 2,
                "ausbau": {"gift_radius": ("=", 50)},
            },
        },
        "farbe": (110, 170, 70),
    },
    "blitz": {
        "name": "Blitzturm",
        "kurz": "Der Blitz springt von Gegner zu Gegner.",
        "kosten": {"gold": 120, "stein": 10},
        "werte": {
            "schaden": 16,
            "art": "magie",
            "reichweite": 125,
            "nachladezeit": 1.6,
            "spruenge": 3,
            "sprungweite": 85,
            "trifft_luft": True,
        },
        "ausbau": [dict(_STUFE_2)],
        "meister": {
            "gewitter": {
                "name": "Gewitter",
                "kurz": "Der Blitz springt viel öfter weiter.",
                "kosten": {"gold": 190, "stein": 35},
                "braucht_schmiede": 3,
                "ausbau": {"spruenge": ("+", 4)},
            },
            "donnerschlag": {
                "name": "Donnerschlag",
                "kurz": "Doppelter Schaden, und jeder Treffer betäubt kurz.",
                "kosten": {"gold": 190, "stein": 35},
                "braucht_schmiede": 3,
                "ausbau": {"schaden": ("*", 2), "betaeubung_dauer": ("=", 0.4)},
            },
        },
        "farbe": (230, 210, 80),
    },
    "palisade": {
        "name": "Palisade",
        "kurz": "Schießt nicht, versperrt aber den Weg.",
        "kosten": {"gold": 5, "stein": 3},
        "werte": {},
        "ausbau": [],
        "meister": {},
        "farbe": (120, 84, 50),
    },
}

# --------------------------------------------------------------------------------------
# Gegner
#
# "tempo" ist Pixel pro Sekunde, "preis" kostet der Gegner die Wellenschmiede,
# "ab_welle" ist die erste Welle, in der er vorkommen darf.
# "resistenzen" nimmt den Schaden einer Art mal diese Zahl: unter 1 hält er mehr aus,
# über 1 ist es seine Schwäche. "faehigkeiten" nennt Klassen aus der Mission 14 und
# die Werte, mit denen sie erzeugt werden.
# --------------------------------------------------------------------------------------

# Als "ab_welle" für einen Gegner, den die Wellenschmiede nie kaufen soll: So weit kommt keine
# Partie. Die ganze Tabelle GEGNER darf deshalb als Katalog an die Mission 15 gehen.
NIE_VON_SELBST = 1_000_000_000

GEGNER = {
    "ork": {
        "name": "Ork",
        "leben": 45,
        "tempo": 48,
        "belohnung": 5,
        "dorfschaden": 1,
        "preis": 5,
        "ab_welle": 1,
        "boss": False,
        "fliegt": False,
        "resistenzen": {},
        "faehigkeiten": [],
        "teilt_in": [],
        "bricht": False,
        "groesse": 11,
        "farbe": (96, 150, 70),
    },
    "wolf": {
        "name": "Wolfsreiter",
        "leben": 30,
        "tempo": 90,
        "belohnung": 6,
        "dorfschaden": 1,
        "preis": 6,
        "ab_welle": 2,
        "boss": False,
        "fliegt": False,
        "resistenzen": {},
        "faehigkeiten": [],
        "teilt_in": [],
        "bricht": False,
        "groesse": 10,
        "farbe": (140, 140, 150),
    },
    "oger": {
        "name": "Oger",
        "leben": 160,
        "tempo": 30,
        "belohnung": 14,
        "dorfschaden": 3,
        "preis": 16,
        "ab_welle": 4,
        "boss": False,
        "fliegt": False,
        "resistenzen": {"wucht": 0.7},
        "faehigkeiten": [],
        "teilt_in": [],
        "bricht": False,
        "groesse": 16,
        "farbe": (150, 120, 80),
    },
    "schildork": {
        "name": "Schildork",
        "leben": 80,
        "tempo": 40,
        "belohnung": 11,
        "dorfschaden": 2,
        "preis": 12,
        "ab_welle": 5,
        "boss": False,
        "fliegt": False,
        "resistenzen": {"stich": 0.4},
        "faehigkeiten": [],
        "teilt_in": [],
        "bricht": False,
        "groesse": 12,
        "farbe": (70, 120, 110),
    },
    "harpyie": {
        "name": "Harpyie",
        "leben": 55,
        "tempo": 70,
        "belohnung": 12,
        "dorfschaden": 2,
        "preis": 14,
        "ab_welle": 6,
        "boss": False,
        "fliegt": True,
        "resistenzen": {},
        "faehigkeiten": [],
        "teilt_in": [],
        "bricht": False,
        "groesse": 11,
        "farbe": (200, 130, 170),
    },
    "troll": {
        "name": "Troll",
        "leben": 220,
        "tempo": 26,
        "belohnung": 20,
        "dorfschaden": 4,
        "preis": 24,
        "ab_welle": 7,
        "boss": False,
        "fliegt": False,
        "resistenzen": {},
        "faehigkeiten": [("Regeneration", {"pro_sekunde": 12})],
        "teilt_in": [],
        "bricht": False,
        "groesse": 17,
        "farbe": (80, 130, 120),
    },
    "schamane": {
        "name": "Schamane",
        "leben": 90,
        "tempo": 38,
        "belohnung": 18,
        "dorfschaden": 2,
        "preis": 22,
        "ab_welle": 8,
        "boss": False,
        "fliegt": False,
        "resistenzen": {},
        "faehigkeiten": [("Heiler", {"radius": 90, "pro_sekunde": 14})],
        "teilt_in": [],
        "bricht": False,
        "groesse": 12,
        "farbe": (170, 90, 190),
    },
    "schleim": {
        "name": "Schleim",
        "leben": 120,
        "tempo": 34,
        "belohnung": 12,
        "dorfschaden": 2,
        "preis": 18,
        "ab_welle": 9,
        "boss": False,
        "fliegt": False,
        "resistenzen": {"gift": 0.5},
        "faehigkeiten": [],
        "teilt_in": ["schleimling", "schleimling"],
        "bricht": False,
        "groesse": 14,
        "farbe": (120, 210, 120),
    },
    "schleimling": {
        "name": "Schleimling",
        "leben": 35,
        "tempo": 60,
        "belohnung": 3,
        "dorfschaden": 1,
        "preis": 4,
        "ab_welle": NIE_VON_SELBST,  # entsteht nur, wenn ein Schleim zerplatzt
        "boss": False,
        "fliegt": False,
        "resistenzen": {"gift": 0.5},
        "faehigkeiten": [],
        "teilt_in": [],
        "bricht": False,
        "groesse": 8,
        "farbe": (150, 230, 150),
    },
    "geist": {
        "name": "Geist",
        "leben": 70,
        "tempo": 55,
        "belohnung": 16,
        "dorfschaden": 2,
        "preis": 20,
        "ab_welle": 11,
        "boss": False,
        "fliegt": False,
        "resistenzen": {"stich": 0.25, "wucht": 0.25, "magie": 1.5},
        "faehigkeiten": [],
        "teilt_in": [],
        "bricht": False,
        "groesse": 12,
        "farbe": (210, 220, 240),
    },
    "brecher": {
        "name": "Brecher",
        "leben": 260,
        "tempo": 28,
        "belohnung": 24,
        "dorfschaden": 3,
        "preis": 30,
        "ab_welle": 12,
        "boss": False,
        "fliegt": False,
        "resistenzen": {},
        "faehigkeiten": [],
        "teilt_in": [],
        "bricht": True,  # läuft geradeaus und reißt ab, was im Weg steht
        "groesse": 17,
        "farbe": (130, 70, 60),
    },
    "orkkoenig": {
        "name": "Orkkönig",
        "leben": 2600,
        "tempo": 20,
        "belohnung": 200,
        "dorfschaden": 20,
        "preis": 400,  # nie gekauft (er kommt in den Bosswellen dazu), aber immer über 0
        "ab_welle": 10,
        "boss": True,
        "fliegt": False,
        "resistenzen": {},
        "faehigkeiten": [("Beschwoerer", {"intervall": 6.0, "art": "ork", "anzahl": 3})],
        "teilt_in": [],
        "bricht": False,
        "groesse": 24,
        "farbe": (190, 60, 50),
    },
}

# Ein Boss lässt sich nicht betäuben und nie stärker bremsen als auf diesen Faktor.
BOSS_FROST_MINDESTFAKTOR = 0.8

# --------------------------------------------------------------------------------------
# Wellen
# --------------------------------------------------------------------------------------

KAMPAGNE_WELLEN = 20
BOSS_ART = "orkkoenig"
BOSS_WELLEN_ABSTAND = 10  # jede zehnte Welle ist eine Bosswelle
BOSS_BUDGET_ANTEIL = 0.6  # eine Bosswelle hat nur 60 % des Budgets, dafür den Boss
BOSS_ANZAHL_ENDKAMPF = 2  # in Welle 20 kommen zwei Orkkönige, sonst einer

WELLEN_GOLD = 40  # Einkommen nach jeder Welle
WELLEN_STEIN = 5


def wellen_budget(n, faktor):
    """Wie viel die Welle ``n`` kosten darf; ``faktor`` kommt vom Schwierigkeitsgrad."""
    return round((18 + 9 * n + 0.9 * n * n) * faktor)


def wellen_leben_faktor(n):
    """Um wie viel die Gegner der Welle ``n`` mehr Leben haben als in Welle 1."""
    return 1 + 0.06 * (n - 1)


def spawn_abstand(n):
    """Sekunden zwischen zwei Gegnern der Welle ``n``."""
    return max(0.25, 1.1 - 0.03 * n)


# --------------------------------------------------------------------------------------
# Schwierigkeitsgrade
# --------------------------------------------------------------------------------------

SCHWIERIGKEIT = {
    "leicht": {
        "name": "Leicht",
        "leben_faktor": 0.75,
        "budget_faktor": 0.8,
        "start": {"gold": 320, "stein": 40},
        "dorf_leben": 30,
    },
    "normal": {
        "name": "Normal",
        "leben_faktor": 1.0,
        "budget_faktor": 1.0,
        "start": {"gold": 260, "stein": 30},
        "dorf_leben": 20,
    },
    "schwer": {
        "name": "Schwer",
        "leben_faktor": 1.3,
        "budget_faktor": 1.25,
        "start": {"gold": 220, "stein": 20},
        "dorf_leben": 15,
    },
    "albtraum": {
        "name": "Albtraum",
        "leben_faktor": 1.7,
        "budget_faktor": 1.5,
        "start": {"gold": 200, "stein": 10},
        "dorf_leben": 10,
    },
}

# --------------------------------------------------------------------------------------
# Das Dorf
#
# Jedes Gebäude hat Stufen, die man der Reihe nach kauft. "braucht" nennt andere Gebäude und
# die Stufe, die sie mindestens haben müssen. "boni" zählen sich über alle gekauften Stufen
# zusammen. Wo es auf die Einwohner ankommt, steht eine Stufe der Wohnhäuser in "braucht".
# --------------------------------------------------------------------------------------

START_BEWOHNER = 12
ZAUBER_STUFE_GRUND = 1  # so weit lassen sich Zauber ohne Bibliothek ausbauen

DORFGEBAEUDE = {
    "kirche": {
        "name": "Kirche",
        "stufen": [
            {
                "name": "Holzkapelle",
                "kosten": {"gold": 60, "stein": 0},
                "braucht": {},
                "boni": {"mana_max": 60, "mana_pro_sekunde": 1.0, "heilung_pro_welle": 1},
            },
            {
                "name": "Dorfkirche",
                "kosten": {"gold": 120, "stein": 15},
                "braucht": {},
                "boni": {"mana_max": 30, "mana_pro_sekunde": 0.5, "heilung_pro_welle": 1},
            },
            {
                "name": "Basilika",
                "kosten": {"gold": 220, "stein": 40},
                "braucht": {"steinbruch": 1, "haeuser": 1},
                "boni": {"mana_max": 40, "mana_pro_sekunde": 0.5, "heilung_pro_welle": 1},
            },
            {
                "name": "Kathedrale",
                "kosten": {"gold": 340, "stein": 90},
                "braucht": {"bauhuette": 2, "steinbruch": 2, "haeuser": 3},
                "boni": {
                    "mana_max": 50,
                    "mana_pro_sekunde": 0.5,
                    "heilung_pro_welle": 1,
                    "glocken_intervall": 40,
                    "glocken_dauer": 1.5,
                },
            },
            {
                "name": "Kathedrale mit Türmen",
                "kosten": {"gold": 500, "stein": 150},
                "braucht": {"bauhuette": 3, "bibliothek": 2, "haeuser": 4},
                "boni": {
                    "mana_max": 70,
                    "mana_pro_sekunde": 2.5,  # verdoppelt, was die Stufen 1 bis 4 geben
                    "heilung_pro_welle": 1,
                    "glocken_intervall": -15,  # 40 - 15: die Glocken läuten alle 25 Sekunden
                    "glocken_dauer": 0.5,
                },
            },
        ],
    },
    "schmiede": {
        "name": "Schmiede",
        "stufen": [
            {
                "name": "Feldschmiede",
                "kosten": {"gold": 80, "stein": 0},
                "braucht": {},
                "boni": {"turm_schaden_prozent": 10, "schmiede_stufe": 1},
            },
            {
                "name": "Dorfschmiede",
                "kosten": {"gold": 160, "stein": 20},
                "braucht": {"steinbruch": 1},
                "boni": {"turm_schaden_prozent": 10, "schmiede_stufe": 1},
            },
            {
                "name": "Waffenschmiede",
                "kosten": {"gold": 280, "stein": 50},
                "braucht": {"haeuser": 2},
                "boni": {"turm_schaden_prozent": 10, "schmiede_stufe": 1},
            },
        ],
    },
    "markt": {
        "name": "Markt",
        "stufen": [
            {
                "name": "Marktstand",
                "kosten": {"gold": 70, "stein": 0},
                "braucht": {},
                "boni": {"gold_pro_welle": 10, "verkauf_prozent": 5},
            },
            {
                "name": "Marktplatz",
                "kosten": {"gold": 150, "stein": 0},
                "braucht": {},
                "boni": {"gold_pro_welle": 10, "zinsen_prozent": 2, "zinsen_max": 20},
            },
            {
                "name": "Kaufhaus",
                "kosten": {"gold": 260, "stein": 20},
                "braucht": {"haeuser": 2},
                "boni": {
                    "gold_pro_welle": 15,
                    "zinsen_prozent": 2,
                    "zinsen_max": 30,
                    "verkauf_prozent": 10,
                },
            },
            {
                "name": "Handelshof",
                "kosten": {"gold": 400, "stein": 40},
                "braucht": {"haeuser": 3},
                "boni": {
                    "gold_pro_welle": 20,
                    "zinsen_prozent": 2,
                    "zinsen_max": 50,
                    "verkauf_prozent": 10,
                },
            },
        ],
    },
    "steinbruch": {
        "name": "Steinbruch",
        "stufen": [
            {
                "name": "Steingrube",
                "kosten": {"gold": 60, "stein": 0},
                "braucht": {},
                "boni": {"stein_pro_welle": 6},
            },
            {
                "name": "Steinbruch",
                "kosten": {"gold": 130, "stein": 0},
                "braucht": {},
                "boni": {"stein_pro_welle": 8},
            },
            {
                "name": "Großer Steinbruch",
                "kosten": {"gold": 240, "stein": 0},
                "braucht": {},
                "boni": {"stein_pro_welle": 10},
            },
        ],
    },
    "haeuser": {
        "name": "Wohnhäuser",
        "stufen": [
            {
                "name": "Hütten",
                "kosten": {"gold": 50, "stein": 0},
                "braucht": {},
                "boni": {"bewohner": 12, "gold_pro_welle": 3},
            },
            {
                "name": "Fachwerkhäuser",
                "kosten": {"gold": 90, "stein": 0},
                "braucht": {},
                "boni": {"bewohner": 12, "gold_pro_welle": 3},
            },
            {
                "name": "Bürgerhäuser",
                "kosten": {"gold": 150, "stein": 10},
                "braucht": {},
                "boni": {"bewohner": 12, "gold_pro_welle": 3},
            },
            {
                "name": "Stadthäuser",
                "kosten": {"gold": 230, "stein": 20},
                "braucht": {"markt": 2},
                "boni": {"bewohner": 12, "gold_pro_welle": 3},
            },
            {
                "name": "Patrizierhäuser",
                "kosten": {"gold": 340, "stein": 40},
                "braucht": {},
                "boni": {"bewohner": 12, "gold_pro_welle": 3},
            },
        ],
    },
    "mauer": {
        "name": "Stadtmauer",
        "stufen": [
            {
                "name": "Erdwall",
                "kosten": {"gold": 70, "stein": 10},
                "braucht": {},
                "boni": {"dorf_leben": 6},
            },
            {
                "name": "Steinmauer",
                "kosten": {"gold": 120, "stein": 30},
                "braucht": {"steinbruch": 1},
                "boni": {"dorf_leben": 6},
            },
            {
                "name": "Wehrmauer",
                "kosten": {"gold": 200, "stein": 60},
                "braucht": {"haeuser": 2},
                "boni": {"dorf_leben": 6, "dorf_ruestung": 1},
            },
            {
                "name": "Stadtmauer mit Türmen",
                "kosten": {"gold": 320, "stein": 100},
                "braucht": {"bauhuette": 1},
                "boni": {"dorf_leben": 6, "dorf_ruestung": 1},
            },
        ],
    },
    "bauhuette": {
        "name": "Bauhütte",
        "stufen": [
            {
                "name": "Werkplatz",
                "kosten": {"gold": 90, "stein": 15},
                "braucht": {"steinbruch": 1},
                "boni": {"bau_rabatt_prozent": 8},
            },
            {
                "name": "Bauhütte",
                "kosten": {"gold": 180, "stein": 35},
                "braucht": {},
                "boni": {"bau_rabatt_prozent": 8},
            },
            {
                "name": "Dombauhütte",
                "kosten": {"gold": 300, "stein": 70},
                "braucht": {"kirche": 3},
                "boni": {"bau_rabatt_prozent": 8},
            },
        ],
    },
    "bibliothek": {
        "name": "Bibliothek",
        "stufen": [
            {
                "name": "Schreibstube",
                "kosten": {"gold": 120, "stein": 0},
                "braucht": {"kirche": 2},
                "boni": {"zauber_stufe_max": 1, "zauber_tempo_prozent": 10},
            },
            {
                "name": "Bibliothek",
                "kosten": {"gold": 220, "stein": 20},
                "braucht": {"haeuser": 2},
                "boni": {"zauber_stufe_max": 1, "zauber_tempo_prozent": 10},
            },
            {
                "name": "Große Bibliothek",
                "kosten": {"gold": 360, "stein": 50},
                "braucht": {"kirche": 4},
                "boni": {"zauber_stufe_max": 1, "zauber_tempo_prozent": 10},
            },
        ],
    },
}

# --------------------------------------------------------------------------------------
# Zauber
#
# "klasse" ist eine Klasse aus der Mission 20. "stufen" enthält für jede der drei Stufen
# die Werte, mit denen die Klasse erzeugt wird. "ausbau_kosten" sind die Preise für die
# Stufen 2 und 3. "braucht_ziel" sagt, ob man für den Zauber auf die Karte klicken muss.
# --------------------------------------------------------------------------------------

ZAUBER = {
    "segen": {
        "name": "Segen",
        "klasse": "Segen",
        "frei_ab_kirche": 1,
        "braucht_ziel": False,
        "ausbau_kosten": [{"gold": 100, "stein": 0}, {"gold": 200, "stein": 20}],
        "stufen": [
            {"kosten": 30, "abklingzeit": 25.0, "heilung": 3},
            {"kosten": 30, "abklingzeit": 25.0, "heilung": 5},
            {"kosten": 30, "abklingzeit": 25.0, "heilung": 8},
        ],
    },
    "feuerball": {
        "name": "Feuerball",
        "klasse": "Feuerball",
        "frei_ab_kirche": 2,
        "braucht_ziel": True,
        "ausbau_kosten": [{"gold": 120, "stein": 10}, {"gold": 240, "stein": 30}],
        "stufen": [
            {
                "kosten": 40,
                "abklingzeit": 12.0,
                "radius": 70,
                "schaden": 60,
                "brand_dauer": 0.0,
                "brand_schaden": 0,
            },
            {
                "kosten": 40,
                "abklingzeit": 12.0,
                "radius": 70,
                "schaden": 100,
                "brand_dauer": 3.0,
                "brand_schaden": 12,
            },
            {
                "kosten": 40,
                "abklingzeit": 12.0,
                "radius": 95,
                "schaden": 150,
                "brand_dauer": 4.0,
                "brand_schaden": 20,
            },
        ],
    },
    "eissturm": {
        "name": "Eissturm",
        "klasse": "Eissturm",
        "frei_ab_kirche": 2,
        "braucht_ziel": True,
        "ausbau_kosten": [{"gold": 110, "stein": 10}, {"gold": 220, "stein": 30}],
        "stufen": [
            {"kosten": 35, "abklingzeit": 18.0, "radius": 100, "dauer": 4.0, "faktor": 0.4},
            {"kosten": 35, "abklingzeit": 18.0, "radius": 130, "dauer": 4.0, "faktor": 0.4},
            {"kosten": 35, "abklingzeit": 18.0, "radius": 130, "dauer": 6.0, "faktor": 0.25},
        ],
    },
    "blitzschlag": {
        "name": "Blitzschlag",
        "klasse": "Blitzschlag",
        "frei_ab_kirche": 3,
        "braucht_ziel": True,
        "ausbau_kosten": [{"gold": 140, "stein": 15}, {"gold": 280, "stein": 40}],
        "stufen": [
            {"kosten": 50, "abklingzeit": 15.0, "schaden": 220, "spruenge": 0, "sprungweite": 90},
            {"kosten": 50, "abklingzeit": 15.0, "schaden": 320, "spruenge": 2, "sprungweite": 90},
            {"kosten": 50, "abklingzeit": 15.0, "schaden": 480, "spruenge": 4, "sprungweite": 90},
        ],
    },
    "glockenschlag": {
        "name": "Glockenschlag",
        "klasse": "Glockenschlag",
        "frei_ab_kirche": 4,
        "braucht_ziel": False,
        "ausbau_kosten": [{"gold": 160, "stein": 20}, {"gold": 320, "stein": 50}],
        "stufen": [
            {"kosten": 80, "abklingzeit": 60.0, "dauer": 2.5},
            {"kosten": 80, "abklingzeit": 60.0, "dauer": 3.5},
            {"kosten": 80, "abklingzeit": 60.0, "dauer": 5.0},
        ],
    },
}
