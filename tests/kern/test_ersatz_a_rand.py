"""Der Ersatz zu Spur A an seinen Rändern: was er zusätzlich zu ``test_ersatz_a`` festlegt.

Das Spiel muss sich auch mit lauter offenen Missionen auf den Ersatz verlassen können. Darum
steht hier, was der Ersatz am Kartenrand, auf falschem Gelände und bei unbekannten Zeichen
antwortet, und wo er dabei mit Absicht anders ist als die Mission.
"""

import unittest

from rudersdorf.ersatz import ersatz_fuer
from tests.missionen.helfer import raster_aus

# Gelände für die Bauregel. Das Orktor "S" ist die Zelle (0, 0), das Dorftor "Z" die (4, 2).
GELAENDE = """
    S.#~D
    ..%.^
    ....Z
"""


class ErsatzKartenRand(unittest.TestCase):
    def test_der_ersatz_schaut_beim_suchen_nicht_in_das_raster(self):
        # Mission 1 fände hier das Orktor auf (2, 0) und das Dorftor auf (0, 1).
        finde = ersatz_fuer("karten", "finde")
        raster = raster_aus("..S\nZ..\n")
        self.assertEqual(finde(raster, "S"), [(0, 7)], "das Orktor des Flusstals")
        self.assertEqual(finde(raster, "Z"), [(17, 8)], "das Dorftor des Flusstals")

    def test_ein_anderes_zeichen_als_die_tore_findet_der_ersatz_nicht(self):
        finde = ersatz_fuer("karten", "finde")
        raster = ersatz_fuer("karten", "lies_karte")("")
        for zeichen in ["#", "~", "D", ".", "?"]:
            self.assertEqual(finde(raster, zeichen), [], f"gesucht war {zeichen!r}")

    def test_jede_suche_liefert_eine_eigene_liste(self):
        finde = ersatz_fuer("karten", "finde")
        erste = finde([], "S")
        erste.append("verdorben")
        self.assertEqual(finde([], "S"), [(0, 7)])

    def test_die_tore_stehen_im_flusstal_des_ersatzes_wirklich_dort(self):
        raster = ersatz_fuer("karten", "lies_karte")("")
        self.assertEqual(raster[7][0], "S")
        self.assertEqual(raster[8][17], "Z")
        gezaehlt = {"S": 0, "Z": 0}
        for zeile in raster:
            for zeichen in zeile:
                if zeichen in gezaehlt:
                    gezaehlt[zeichen] += 1
        self.assertEqual(gezaehlt, {"S": 1, "Z": 1}, "Der Ersatz kennt genau zwei Tore.")


class ErsatzWegfindungRand(unittest.TestCase):
    def test_der_geist_schaut_erst_zur_seite_dann_nach_unten_und_oben(self):
        # Mission 2 verlangt die Reihenfolge oben, rechts, unten, links.
        nachbarn = ersatz_fuer("wegfindung", "nachbarn")
        self.assertEqual(nachbarn((1, 1), 3, 3), [(2, 1), (0, 1), (1, 2), (1, 0)])

    def test_auch_der_geist_hat_keine_nachbarn_ausserhalb_der_karte(self):
        nachbarn = ersatz_fuer("wegfindung", "nachbarn")
        self.assertEqual(nachbarn((0, 0), 3, 2), [(1, 0), (0, 1)])
        self.assertEqual(nachbarn((2, 1), 3, 2), [(1, 1), (2, 0)])
        self.assertEqual(nachbarn((0, 0), 1, 1), [])

    def test_fuer_den_geist_sind_fels_wasser_und_bauwerke_begehbar(self):
        # Nach Mission 2 wäre keine dieser drei Zellen begehbar.
        ist_begehbar = ersatz_fuer("wegfindung", "ist_begehbar")
        raster = raster_aus(GELAENDE)
        for zelle in [(2, 0), (3, 0), (1, 1)]:
            self.assertIs(ist_begehbar(raster, zelle, {(1, 1)}), True, f"Zelle {zelle}")

    def test_ausserhalb_der_karte_ist_auch_fuer_den_geist_nichts_begehbar(self):
        ist_begehbar = ersatz_fuer("wegfindung", "ist_begehbar")
        raster = raster_aus(GELAENDE)
        for zelle in [(-1, 0), (0, -1), (5, 0), (0, 3)]:
            self.assertIs(ist_begehbar(raster, zelle, set()), False, f"Zelle {zelle}")

    def test_der_geist_nimmt_den_ersten_naeheren_nachbarn_nicht_den_naechsten(self):
        # Mission 4 ginge nach oben zur 1. Der Ersatz nimmt die 4 rechts, weil er sie zuerst sieht.
        naechster_schritt = ersatz_fuer("wegfindung", "naechster_schritt")
        abstaende = {(1, 0): 1, (0, 1): 9, (1, 1): 5, (2, 1): 4, (1, 2): 9}
        self.assertEqual(naechster_schritt(abstaende, (1, 1), 3, 3), (2, 1))

    def test_am_ziel_und_ohne_abstand_bleibt_der_geist_stehen(self):
        naechster_schritt = ersatz_fuer("wegfindung", "naechster_schritt")
        abstaende = ersatz_fuer("wegfindung", "abstandskarte")(raster_aus(GELAENDE), (4, 2), set())
        self.assertIsNone(naechster_schritt(abstaende, (4, 2), 5, 3), "am Ziel")
        # Die Zelle (5, 2) liegt rechts neben der Karte, ihr linker Nachbar ist das Ziel.
        self.assertIsNone(naechster_schritt(abstaende, (5, 2), 5, 3), "Zelle ohne Abstand")

    def test_der_geist_geht_nie_auf_eine_zelle_mit_gleichem_abstand(self):
        naechster_schritt = ersatz_fuer("wegfindung", "naechster_schritt")
        abstaende = {(0, 0): 2, (1, 0): 2, (0, 1): 2}
        self.assertIsNone(naechster_schritt(abstaende, (0, 0), 2, 2))


class ErsatzBauregelRand(unittest.TestCase):
    def darf_bauen(self, zelle, gesperrt=(), besetzt=()):
        return ersatz_fuer("bauregel", "darf_bauen")(
            raster_aus(GELAENDE), zelle, set(gesperrt), [(0, 0)], (4, 2), set(besetzt)
        )

    def test_auf_wiese_und_huegel_erlaubt_der_ersatz_das_bauen(self):
        self.assertIs(self.darf_bauen((1, 2)), True, "Wiese")
        self.assertIs(self.darf_bauen((4, 1)), True, "Hügel")

    def test_auf_falschem_gelaende_verbietet_auch_der_ersatz_das_bauen(self):
        for zelle in [(0, 0), (2, 0), (3, 0), (4, 0), (2, 1), (4, 2)]:
            self.assertIs(self.darf_bauen(zelle), False, f"Zelle {zelle} ist kein Bauland.")

    def test_ausserhalb_der_karte_verbietet_auch_der_ersatz_das_bauen(self):
        # Die negativen Zellen landen mit Pythons Zählung von hinten auf Bauland: (4, 1) und (1, 2).
        for zelle in [(-1, 1), (1, -1), (5, 1), (1, 3)]:
            self.assertIs(
                self.darf_bauen(zelle), False, f"Zelle {zelle} liegt nicht auf der Karte."
            )

    def test_auf_einem_bauwerk_verbietet_der_ersatz_das_bauen(self):
        self.assertIs(self.darf_bauen((1, 2), gesperrt=[(1, 2)]), False)

    def test_auf_einem_ork_verbietet_der_ersatz_das_bauen(self):
        self.assertIs(self.darf_bauen((1, 2), besetzt=[(1, 2)]), False)

    def test_der_ersatz_sucht_keinen_weg_und_erlaubt_darum_das_einsperren(self):
        # Mission 5 verbietet (1, 1): Das Orktor (0, 0) käme danach nicht mehr hinaus.
        # Darum fängt das Spiel selbst so ein Bauwerk noch ab, was auch immer die Regel sagt.
        raster = raster_aus("S#...\n.....\n....Z\n")
        erlaubt = ersatz_fuer("bauregel", "darf_bauen")(
            raster, (0, 1), set(), [(0, 0)], (4, 2), set()
        )
        self.assertIs(erlaubt, True)

    def test_der_ersatz_laesst_besetzt_und_das_raster_wie_sie_waren(self):
        raster = raster_aus(GELAENDE)
        besetzt = {(0, 1)}
        ersatz_fuer("bauregel", "darf_bauen")(raster, (1, 2), {(3, 2)}, [(0, 0)], (4, 2), besetzt)
        self.assertEqual(besetzt, {(0, 1)})
        self.assertEqual(raster, raster_aus(GELAENDE))


if __name__ == "__main__":
    unittest.main()
