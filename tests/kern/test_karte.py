"""Die Karte im Spielkern: prüfen, laden, Zellen in Pixel umrechnen, eine Partie beginnen.

Kaputte Karten dürfen das Spiel nie abstürzen lassen: Der Kern meldet sie mit einem
``ValueError`` und einem deutschen Satz, der das Problem nennt.
"""

import copy
import pathlib
import unittest

from rudersdorf import daten
from rudersdorf.kern.karte import Karte, lade_karte, pruefe_karte, zentrum
from rudersdorf.kern.spiel import Spiel
from rudersdorf.werkbank import Werkbank
from tests.kern.helfer import karte_aus, paket_wie_loesung, raster_von, zeilen_von

KARTENORDNER = pathlib.Path(daten.__file__).parent.parent / "karten"

# Das Orktor "S" ist die Zelle (0, 0), das Dorftor "Z" die Zelle (8, 0).
GANG = """
    S.......Z
"""
ZWEI_TORE = """
    S.......Z
    .########
    S########
"""
OHNE_DORFTOR = """
    S........
"""
ZWEI_DORFTORE = """
    S...Z...Z
"""
OHNE_ORKTOR = """
    ........Z
"""
FREMDES_ZEICHEN = """
    S...X...Z
"""
KEIN_WEG = """
    S...#...Z
"""
ZWEITES_TOR_OHNE_WEG = """
    S.......Z
    #########
    S........
"""
ERSTES_TOR_OHNE_WEG = """
    S........
    #########
    S.......Z
"""
WASSER_IM_WEG = """
    S...~...Z
"""


# Für die Karte mit zwei Orktoren liefert dieses lies_karte ein Raster mit zwei Dorftoren.
# Für den Kern ist das dasselbe wie eine kaputte Datei im Ordner karten/.
ZWEI_TORE_KAPUTT = '''
from loesung import raster as _echt


def lies_karte(text):
    """Liest wie die Lösung, verdirbt aber die Karte mit zwei Orktoren."""
    raster = _echt.lies_karte(text)
    if sum(zeile.count("S") for zeile in raster) == 2:
        raster[0][0] = "Z"
    return raster
'''


def zeilen_der_datei(name):
    """Liest eine Kartendatei so, wie sie im Ordner karten/ liegt."""
    text = (KARTENORDNER / f"{name}.txt").read_text(encoding="utf-8")
    return [zeile.rstrip() for zeile in text.splitlines() if zeile.strip() != ""]


def zellen_mit(zeilen, zeichen):
    """Sucht in den Zeilen einer Karte alle Zellen mit diesem Zeichen."""
    gefunden = []
    for zeile, text in enumerate(zeilen):
        for spalte, inhalt in enumerate(text):
            if inhalt == zeichen:
                gefunden.append((spalte, zeile))
    return gefunden


def ungleich_lang():
    raster = raster_von(GANG)
    del raster[3][-1]
    return raster


def zu_wenige_zeilen():
    return raster_von(GANG)[:-1]


def zu_viele_zeilen():
    raster = raster_von(GANG)
    raster.append(list(raster[-1]))
    return raster


def zu_schmal():
    return [zeile[1:] for zeile in raster_von(".S.......Z")]


def zu_breit():
    return [["#"] + zeile for zeile in raster_von(GANG)]


def wiese_im_dorf():
    raster = raster_von(GANG)
    raster[4][20] = "."
    return raster


def dorfgrund_im_feld():
    raster = raster_von(GANG)
    raster[5][5] = "D"
    return raster


class KartePruefen(unittest.TestCase):
    def grund(self, raster, *woerter):
        """Erwartet einen ValueError und liefert seinen Text; ``woerter`` müssen darin stehen."""
        vorher = copy.deepcopy(raster)
        with self.assertRaises(ValueError) as gefangen:
            pruefe_karte(raster)
        text = str(gefangen.exception)
        self.assertNotEqual(
            "", text.strip(), "Der Fehler braucht einen Satz, der das Problem nennt."
        )
        for wort in woerter:
            self.assertIn(wort.lower(), text.lower(), f"Der Grund soll {wort!r} nennen.")
        self.assertEqual(vorher, raster, "pruefe_karte darf das Raster nicht verändern.")
        return text

    def test_eine_gute_karte_wird_ohne_fehler_angenommen(self):
        raster = raster_von(GANG)
        vorher = copy.deepcopy(raster)
        self.assertIsNone(pruefe_karte(raster))
        self.assertEqual(vorher, raster, "pruefe_karte darf das Raster nicht verändern.")

    def test_eine_karte_mit_zwei_orktoren_ist_in_ordnung(self):
        self.assertIsNone(pruefe_karte(raster_von(ZWEI_TORE)))

    def test_alle_gelaendearten_sind_bekannte_zeichen(self):
        self.assertIsNone(pruefe_karte(raster_von("S.%^~#..Z\n.........")))

    def test_verschieden_lange_zeilen_sind_ein_fehler(self):
        self.grund(ungleich_lang())

    def test_eine_zeile_zu_wenig_oder_zu_viel_ist_ein_fehler(self):
        self.grund(zu_wenige_zeilen(), str(daten.ZEILEN))
        self.grund(zu_viele_zeilen(), str(daten.ZEILEN))

    def test_eine_spalte_zu_wenig_oder_zu_viel_ist_ein_fehler(self):
        self.grund(zu_schmal(), str(daten.SPALTEN))
        self.grund(zu_breit(), str(daten.SPALTEN))

    def test_ein_leeres_raster_ist_ein_fehler(self):
        self.grund([])

    def test_eine_karte_ohne_dorftor_ist_ein_fehler(self):
        self.grund(raster_von(OHNE_DORFTOR), "Dorftor")

    def test_eine_karte_mit_zwei_dorftoren_ist_ein_fehler(self):
        self.grund(raster_von(ZWEI_DORFTORE), "Dorftor")

    def test_eine_karte_ohne_orktor_ist_ein_fehler(self):
        self.grund(raster_von(OHNE_ORKTOR), "Orktor")

    def test_ein_unbekanntes_zeichen_ist_ein_fehler_und_wird_genannt(self):
        self.grund(raster_von(FREMDES_ZEICHEN), "X")

    def test_wiese_in_den_spalten_des_dorfes_ist_ein_fehler(self):
        self.grund(wiese_im_dorf(), "Dorf")

    def test_dorfgrund_ausserhalb_der_dorfspalten_ist_ein_fehler(self):
        self.grund(dorfgrund_im_feld(), "Dorf")

    def test_ein_orktor_ohne_weg_zum_dorftor_ist_ein_fehler(self):
        self.grund(raster_von(KEIN_WEG), "Weg")

    def test_wasser_versperrt_den_weg_wie_fels(self):
        self.grund(raster_von(WASSER_IM_WEG), "Weg")

    def test_auch_das_zweite_orktor_braucht_einen_weg(self):
        self.grund(raster_von(ZWEITES_TOR_OHNE_WEG), "Weg")

    def test_auch_das_erste_orktor_braucht_einen_weg(self):
        self.grund(raster_von(ERSTES_TOR_OHNE_WEG), "Weg")

    def test_jeder_fehler_hat_seinen_eigenen_grund(self):
        gruende = {
            "ungleich lang": self.grund(ungleich_lang()),
            "kein Dorftor": self.grund(raster_von(OHNE_DORFTOR)),
            "zwei Dorftore": self.grund(raster_von(ZWEI_DORFTORE)),
            "kein Orktor": self.grund(raster_von(OHNE_ORKTOR)),
            "fremdes Zeichen": self.grund(raster_von(FREMDES_ZEICHEN)),
            "kein Weg": self.grund(raster_von(KEIN_WEG)),
        }
        self.assertEqual(
            len(gruende), len(set(gruende.values())), f"Zwei Fehler haben denselben Satz: {gruende}"
        )


class EineKarte(unittest.TestCase):
    def test_die_karte_kennt_groesse_tore_und_namen(self):
        karte = Karte(raster_von(GANG))
        self.assertEqual("eigene", karte.name)
        self.assertEqual(daten.SPALTEN, karte.breite)
        self.assertEqual(daten.ZEILEN, karte.hoehe)
        self.assertEqual([(0, 0)], list(karte.starts))
        self.assertEqual((8, 0), tuple(karte.ziel))
        self.assertEqual(karte_aus(GANG).splitlines(), zeilen_von(karte.raster))

    def test_die_karte_merkt_sich_ihren_namen(self):
        self.assertEqual("probe", Karte(raster_von(GANG), "probe").name)
        self.assertEqual("probe", Karte(raster_von(GANG), name="probe").name)

    def test_eine_zelle_nennt_erst_die_spalte_und_dann_die_zeile(self):
        karte = Karte(raster_von("....\n....\n.S.Z"))
        self.assertEqual([(1, 2)], list(karte.starts))
        self.assertEqual((3, 2), tuple(karte.ziel))

    def test_die_karte_kennt_alle_orktore(self):
        karte = Karte(raster_von(ZWEI_TORE))
        self.assertEqual([(0, 0), (0, 2)], sorted(tuple(start) for start in karte.starts))

    def test_eine_kaputte_karte_wird_gar_nicht_erst_gebaut(self):
        for name, raster in [
            ("kein Dorftor", raster_von(OHNE_DORFTOR)),
            ("ungleich lang", ungleich_lang()),
            ("kein Weg", raster_von(KEIN_WEG)),
        ]:
            with self.subTest(name), self.assertRaises(ValueError):
                Karte(raster)


class Zellmitte(unittest.TestCase):
    def test_die_mitte_der_ersten_zelle_liegt_eine_halbe_zelle_vom_rand(self):
        self.assertEqual((daten.ZELLE / 2, daten.ZELLE / 2), tuple(zentrum((0, 0))))

    def test_die_spalte_bestimmt_x_und_die_zeile_y(self):
        x, y = zentrum((3, 1))
        self.assertEqual(3 * daten.ZELLE + daten.ZELLE / 2, x)
        self.assertEqual(1 * daten.ZELLE + daten.ZELLE / 2, y)


class KarteLaden(unittest.TestCase):
    def test_jede_karte_des_spiels_laesst_sich_laden(self):
        for name in daten.KARTEN:
            with self.subTest(name):
                zeilen = zeilen_der_datei(name)
                karte = lade_karte(name, Werkbank("loesung"))
                self.assertEqual(name, karte.name)
                self.assertEqual(zeilen, zeilen_von(karte.raster))
                self.assertEqual(
                    sorted(zellen_mit(zeilen, "S")),
                    sorted(tuple(s) for s in karte.starts),
                    "Orktore",
                )
                self.assertEqual(zellen_mit(zeilen, "Z"), [tuple(karte.ziel)], "Dorftor")

    def test_die_karte_mit_zwei_toren_hat_zwei_orktore(self):
        self.assertEqual(2, len(lade_karte("zwei_tore", Werkbank("loesung")).starts))

    def test_gelesen_wird_die_datei_mit_der_faehigkeit_karten(self):
        # Ist die Mission 1 offen, liest ihr Ersatz den Text nicht und liefert das Flusstal.
        # Liest der Kern die Datei an der Werkbank vorbei selbst, fällt das hier auf.
        werkbank = Werkbank("loesung", gesperrt=("karten",))
        karte = lade_karte("zwei_tore", werkbank)
        self.assertEqual(zeilen_der_datei("flusstal"), zeilen_von(karte.raster))


class PartieBeginnt(unittest.TestCase):
    def test_ohne_angabe_wird_auf_der_standardkarte_gespielt(self):
        spiel = Spiel(Werkbank("loesung"))
        self.assertEqual(daten.STANDARD_KARTE, spiel.karte.name)
        self.assertEqual(zeilen_der_datei(daten.STANDARD_KARTE), zeilen_von(spiel.karte.raster))

    def test_eine_karte_kann_mit_ihrem_namen_gewaehlt_werden(self):
        spiel = Spiel(Werkbank("loesung"), karte="zwei_tore")
        self.assertEqual("zwei_tore", spiel.karte.name)
        self.assertEqual(zeilen_der_datei("zwei_tore"), zeilen_von(spiel.karte.raster))

    def test_bei_einem_unbekannten_namen_wird_das_flusstal_gespielt_und_das_gemeldet(self):
        spiel = Spiel(Werkbank("loesung"), karte="gibtsnicht")
        self.assertEqual("flusstal", spiel.karte.name)
        self.assertEqual(zeilen_der_datei("flusstal"), zeilen_von(spiel.karte.raster))
        self.assertIn("flusstal", spiel.meldung.lower(), "Die Meldung soll die Ersatzkarte nennen.")

    def test_besteht_die_gewaehlte_karte_die_pruefung_nicht_wird_das_flusstal_gespielt(self):
        werkbank = Werkbank(paket_wie_loesung(self, {"raster": ZWEI_TORE_KAPUTT}))
        self.assertFalse(werkbank.ist_offen("karten"))
        with self.assertRaises(ValueError):
            lade_karte("zwei_tore", werkbank)
        spiel = Spiel(werkbank, karte="zwei_tore")
        self.assertEqual("flusstal", spiel.karte.name)
        self.assertEqual(zeilen_der_datei("flusstal"), zeilen_von(spiel.karte.raster))
        self.assertIn("flusstal", spiel.meldung.lower(), "Die Meldung soll die Ersatzkarte nennen.")

    def test_eine_gefundene_karte_meldet_keinen_ersatz(self):
        spiel = Spiel(Werkbank("loesung"), karte="zwei_tore")
        self.assertNotIn("flusstal", spiel.meldung.lower())

    def test_ein_kartentext_wird_zur_karte_der_partie(self):
        spiel = Spiel(Werkbank("loesung"), kartentext=karte_aus(ZWEI_TORE))
        self.assertEqual(karte_aus(ZWEI_TORE).splitlines(), zeilen_von(spiel.karte.raster))
        self.assertEqual([(0, 0), (0, 2)], sorted(tuple(start) for start in spiel.karte.starts))
        self.assertEqual((8, 0), tuple(spiel.karte.ziel))
        self.assertEqual(daten.SPALTEN, spiel.karte.breite)
        self.assertEqual(daten.ZEILEN, spiel.karte.hoehe)

    def test_auch_der_kartentext_wird_mit_der_faehigkeit_karten_gelesen(self):
        werkbank = Werkbank("loesung", gesperrt=("karten",))
        spiel = Spiel(werkbank, kartentext=karte_aus(ZWEI_TORE))
        self.assertEqual(zeilen_der_datei("flusstal"), zeilen_von(spiel.karte.raster))

    def test_ein_kaputter_kartentext_ist_ein_fehler_mit_grund(self):
        kaputt = {
            "kein Dorftor": karte_aus(OHNE_DORFTOR),
            "zwei Dorftore": karte_aus(ZWEI_DORFTORE),
            "kein Orktor": karte_aus(OHNE_ORKTOR),
            "fremdes Zeichen": karte_aus(FREMDES_ZEICHEN),
            "kein Weg": karte_aus(KEIN_WEG),
            "ungleich lang": karte_aus(GANG).replace("D\n", "\n", 1),
            "zu kurz": "S..Z\n",
        }
        for name, text in kaputt.items():
            with self.subTest(name):
                with self.assertRaises(ValueError) as gefangen:
                    Spiel(Werkbank("loesung"), kartentext=text)
                self.assertNotEqual("", str(gefangen.exception).strip())

    def test_eine_neue_partie_beginnt_leer_in_der_bauphase(self):
        spiel = Spiel(Werkbank("loesung"), kartentext=karte_aus(GANG))
        self.assertEqual("bauen", spiel.phase)
        self.assertEqual(0, spiel.welle)
        self.assertEqual([], list(spiel.gegner))
        self.assertEqual({}, dict(spiel.bauwerke))

    def test_die_abstandskarte_der_partie_zaehlt_die_schritte_zum_dorftor(self):
        spiel = Spiel(Werkbank("loesung"), kartentext=karte_aus(GANG))
        abstaende = spiel.abstaende()
        self.assertEqual(0, abstaende[(8, 0)])
        self.assertEqual(8, abstaende[(0, 0)])
        self.assertNotIn((9, 0), abstaende, "Fels hat keinen Abstand.")

    def test_das_dorf_beginnt_mit_den_werten_seines_schwierigkeitsgrads(self):
        for name, werte in daten.SCHWIERIGKEIT.items():
            with self.subTest(name):
                spiel = Spiel(Werkbank("loesung"), schwierigkeit=name, kartentext=karte_aus(GANG))
                self.assertEqual(werte["dorf_leben"], spiel.dorf.leben)
                self.assertEqual(werte["dorf_leben"], spiel.dorf.max_leben)
                self.assertEqual(werte["start"]["gold"], spiel.dorf.vorraete["gold"])
                self.assertEqual(werte["start"]["stein"], spiel.dorf.vorraete["stein"])


if __name__ == "__main__":
    unittest.main()
