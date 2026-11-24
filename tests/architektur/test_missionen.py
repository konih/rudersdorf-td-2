"""Das Missionsverzeichnis ist vollständig und passt zum Vertrag der Werkstatt.

Die Tabellen hier sind mit Absicht noch einmal ausgeschrieben (aus
``specs/001-rudersdorf-2/contracts/werkstatt-api.md``): Ein Tippfehler im Verzeichnis soll
auffallen und sich nicht selbst bestätigen.
"""

import unittest

from rudersdorf.missionen import MISSIONEN

SCHLUESSEL = {
    "nummer",
    "spur",
    "titel",
    "modul",
    "namen",
    "faehigkeit",
    "braucht",
    "testklasse",
    "dokument",
    "sterne",
}

TITEL = [
    "Die Karte lesen",
    "Nachbarn",
    "Der kürzeste Weg",
    "Dem Weg folgen",
    "Nicht einmauern!",
    "Wer ist in Reichweite?",
    "Zielstrategien",
    "Deine eigene Strategie",
    "Der Kettenblitz",
    "Die Turmschmiede",
    "Schadensarten",
    "Effekte",
    "Die Effektliste",
    "Besondere Fähigkeiten",
    "Die Wellenschmiede",
    "Was fehlt noch?",
    "Die Kraft des Dorfes",
    "Der Bauplan",
    "Mana und Abklingzeit",
    "Das Zauberbuch",
    "Fehlerjagd",
    "Aufräumen",
    "Eigene Tests",
    "Der Dorfschreiber",
    "Das Labor",
    "Der Bot",
]

SPUREN = {"A": range(1, 6), "B": range(6, 11), "C": range(11, 16), "D": range(16, 21)}
SPUREN["E"] = range(21, 27)

DOKUMENTE = {
    "A": "missionen/spur_a_raster.md",
    "B": "missionen/spur_b_tuerme.md",
    "C": "missionen/spur_c_horde.md",
    "D": "missionen/spur_d_dorf_und_magie.md",
    "E": "missionen/spur_e_werkstatt.md",
}

MODULE = {
    "raster": [1, 2, 3, 4, 5],
    "tuerme": [6, 9, 10],
    "strategien": [7, 8],
    "horde": [11, 12, 13, 14, 15],
    "dorf": [16, 17, 18],
    "magie": [19, 20],
    "fehlerjagd": [21],
    "aufraeumen": [22],
    "meine_tests": [23],
    "schreiber": [24],
    "forschung": [25, 26],
}

FAEHIGKEITEN = {
    "karten": [1],
    "wegfindung": [2, 3, 4],
    "bauregel": [5],
    "reichweite": [6],
    "strategien": [7, 8],
    "kettenblitz": [9],
    "ausbau": [10],
    "schadensarten": [11],
    "effekte": [12, 13],
    "faehigkeiten": [14],
    "wellen": [15],
    "voraussetzungen": [16],
    "boni": [17],
    "bauplan": [18],
    "magie": [19, 20],
    None: [21, 22, 23],
    "speichern": [24],
    "auswertung": [25],
    "bot": [26],
}

BRAUCHT = {5: [2, 3, 4], 20: [9, 12, 13], 26: [2, 3, 4, 5, 6, 7]}

NAMEN = {
    1: ["lies_karte", "finde"],
    2: ["nachbarn", "ist_begehbar"],
    3: ["abstandskarte"],
    4: ["naechster_schritt"],
    5: ["darf_bauen"],
    6: ["in_reichweite"],
    7: ["erster", "letzter", "staerkster", "schwaechster", "naechster", "STRATEGIEN"],
    8: ["STRATEGIEN"],
    9: ["kettenblitz"],
    10: ["wende_ausbau_an"],
    11: ["berechne_schaden"],
    12: ["Effekt", "Frost", "Gift", "Brand", "Betaeubung"],
    13: ["fuege_effekt_hinzu", "gesamt_tempo_faktor", "raeume_effekte_auf"],
    14: ["Regeneration", "Heiler", "Beschwoerer"],
    15: ["erzeuge_welle"],
    16: ["fehlende_voraussetzungen"],
    17: ["sammle_boni"],
    18: ["bauplan"],
    19: ["Zauber"],
    20: ["Feuerball", "Eissturm", "Blitzschlag", "Segen", "Glockenschlag"],
    21: ["leeres_raster", "entferne_besiegte", "zaehle_arten"],
    22: ["turm_trifft", "anzahl_in_reichweite", "naechster_gegner", "ist_ueberlastet"],
    23: ["MeineTests"],
    24: ["zu_daten", "aus_daten"],
    25: ["auswertung"],
    26: ["mein_bot"],
}


def gruppiert(schluessel):
    """Liefert ``{Wert des Schlüssels: [Nummern der Missionen]}`` aus dem Verzeichnis."""
    gruppen = {}
    for mission in MISSIONEN:
        gruppen.setdefault(mission[schluessel], []).append(mission["nummer"])
    return gruppen


class Missionen(unittest.TestCase):
    def test_es_gibt_die_missionen_1_bis_26_in_dieser_reihenfolge(self):
        self.assertEqual(list(range(1, 27)), [mission["nummer"] for mission in MISSIONEN])

    def test_jeder_eintrag_hat_genau_die_vereinbarten_schluessel(self):
        for mission in MISSIONEN:
            with self.subTest(mission=mission["nummer"]):
                self.assertEqual(SCHLUESSEL, set(mission))

    def test_titel(self):
        self.assertEqual(TITEL, [mission["titel"] for mission in MISSIONEN])

    def test_spuren(self):
        erwartet = {spur: list(nummern) for spur, nummern in SPUREN.items()}
        self.assertEqual(erwartet, gruppiert("spur"))

    def test_module(self):
        self.assertEqual(MODULE, gruppiert("modul"))

    def test_namen(self):
        self.assertEqual(NAMEN, {mission["nummer"]: mission["namen"] for mission in MISSIONEN})

    def test_faehigkeiten(self):
        self.assertEqual(FAEHIGKEITEN, gruppiert("faehigkeit"))

    def test_braucht(self):
        for mission in MISSIONEN:
            with self.subTest(mission=mission["nummer"]):
                self.assertEqual(BRAUCHT.get(mission["nummer"], []), mission["braucht"])

    def test_braucht_nennt_nur_fruehere_missionen_anderer_faehigkeiten(self):
        faehigkeit = {mission["nummer"]: mission["faehigkeit"] for mission in MISSIONEN}
        for mission in MISSIONEN:
            for nummer in mission["braucht"]:
                with self.subTest(mission=mission["nummer"], braucht=nummer):
                    self.assertLess(nummer, mission["nummer"])
                    self.assertNotEqual(faehigkeit[nummer], mission["faehigkeit"])

    def test_testklasse_und_dokument(self):
        for mission in MISSIONEN:
            nummer = mission["nummer"]
            with self.subTest(mission=nummer):
                zwei = str(nummer).rjust(2, "0")
                self.assertEqual(
                    "tests.missionen.test_m" + zwei + ".Mission" + zwei, mission["testklasse"]
                )
                erwartet = DOKUMENTE[mission["spur"]] + "#mission-" + str(nummer)
                self.assertEqual(erwartet, mission["dokument"])

    def test_sterne(self):
        for mission in MISSIONEN:
            with self.subTest(mission=mission["nummer"]):
                self.assertIs(int, type(mission["sterne"]))
                self.assertIn(mission["sterne"], (1, 2, 3))

    def test_jede_mission_hat_ihre_eigenen_listen(self):
        listen = [id(mission[name]) for mission in MISSIONEN for name in ("namen", "braucht")]
        self.assertEqual(len(listen), len(set(listen)))


if __name__ == "__main__":
    unittest.main()
