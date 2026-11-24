"""Die Helfer der Kerntests rechnen selbst richtig, sonst prüfen die Tests das Falsche."""

import unittest

from rudersdorf import daten
from rudersdorf.werkbank import Werkbank
from tests.kern import helfer


class KartenZeichnen(unittest.TestCase):
    def test_aus_einer_zeile_wird_eine_ganze_karte_mit_dorf(self):
        zeilen = helfer.karte_aus("S..Z").splitlines()
        self.assertEqual(daten.ZEILEN, len(zeilen))
        self.assertEqual("S..Z" + "#" * 14 + "DDDDDD", zeilen[0])
        for zeile in zeilen[1:]:
            self.assertEqual("#" * 18 + "DDDDDD", zeile)

    def test_die_zellen_der_zeichnung_sind_die_zellen_der_karte(self):
        raster = helfer.raster_von("""
            S.#
            .^Z
        """)
        self.assertEqual("S", raster[0][0])
        self.assertEqual("#", raster[0][2])
        self.assertEqual("^", raster[1][1])
        self.assertEqual("Z", raster[1][2])
        self.assertEqual(daten.SPALTEN, len(raster[1]))

    def test_der_rand_kann_auch_wiese_sein(self):
        zeilen = helfer.karte_aus("S.Z", rand=".").splitlines()
        self.assertEqual("S.Z" + "." * 15 + "DDDDDD", zeilen[0])
        self.assertEqual("." * 18 + "DDDDDD", zeilen[15])

    def test_eine_zu_grosse_zeichnung_faellt_auf(self):
        with self.assertRaises(AssertionError):
            helfer.karte_aus("." * 19)
        with self.assertRaises(AssertionError):
            helfer.karte_aus("\n".join(["."] * 17))

    def test_zeilen_von_nimmt_listen_und_texte(self):
        self.assertEqual(["ab", "cd"], helfer.zeilen_von([["a", "b"], "cd"]))


class WegeNachrechnen(unittest.TestCase):
    def test_die_mitte_nennt_erst_x_fuer_die_spalte_und_dann_y_fuer_die_zeile(self):
        self.assertEqual((20.0, 20.0), helfer.mitte((0, 0)))
        self.assertEqual((140.0, 60.0), helfer.mitte((3, 1)))

    def test_die_zelle_unter_einem_punkt(self):
        self.assertEqual((0, 0), helfer.zelle_unter(39.9, 0.0))
        self.assertEqual((1, 2), helfer.zelle_unter(40.0, 119.9))

    def test_der_punkt_auf_einem_geraden_weg(self):
        weg = [(0, 0), (1, 0), (2, 0)]
        self.assertEqual((20.0, 20.0), helfer.punkt_auf_weg(weg, 0))
        self.assertEqual((50.0, 20.0), helfer.punkt_auf_weg(weg, 30))
        self.assertEqual((100.0, 20.0), helfer.punkt_auf_weg(weg, 80))

    def test_der_punkt_hinter_einer_ecke(self):
        weg = [(0, 0), (1, 0), (1, 1), (0, 1)]
        self.assertEqual((60.0, 30.0), helfer.punkt_auf_weg(weg, 50))
        self.assertEqual((50.0, 60.0), helfer.punkt_auf_weg(weg, 90))

    def test_ein_zu_kurzer_weg_faellt_auf(self):
        with self.assertRaises(AssertionError):
            helfer.punkt_auf_weg([(0, 0), (1, 0)], 41)

    def test_auf_der_linie_steht_wer_gerade_von_mitte_zu_mitte_laeuft(self):
        self.assertTrue(helfer.auf_linie(33.3, 20.0))
        self.assertTrue(helfer.auf_linie(60.0, 71.5))
        self.assertTrue(helfer.auf_linie(60.0 - 1e-9, 71.5))

    def test_neben_der_linie_steht_wer_schraeg_laeuft(self):
        self.assertFalse(helfer.auf_linie(33.3, 21.0))
        self.assertFalse(helfer.auf_linie(40.0, 80.0))

    def test_ein_kuerzester_weg_hat_keinen_fehler(self):
        abstaende = {(0, 0): 2, (1, 0): 1, (2, 0): 0, (0, 1): 3}
        self.assertIsNone(helfer.fehler_im_weg([(0, 1), (0, 0), (1, 0), (2, 0)], abstaende))
        self.assertIsNone(helfer.fehler_im_weg([(1, 0)], abstaende))

    def test_ein_schraeger_schritt_ist_ein_fehler(self):
        abstaende = {(0, 0): 2, (1, 1): 1}
        self.assertIn("Nachbarzelle", helfer.fehler_im_weg([(0, 0), (1, 1)], abstaende))

    def test_ein_schritt_ohne_abstand_ist_ein_fehler(self):
        self.assertIn("ohne Abstand", helfer.fehler_im_weg([(0, 0), (1, 0)], {(0, 0): 1}))

    def test_ein_schritt_bergauf_oder_auf_gleicher_hoehe_ist_ein_fehler(self):
        abstaende = {(0, 0): 1, (1, 0): 2, (0, 1): 1}
        self.assertIn("näher", helfer.fehler_im_weg([(0, 0), (1, 0)], abstaende))
        self.assertIn("näher", helfer.fehler_im_weg([(0, 0), (0, 1)], abstaende))


class EinGegnerZumVerfolgen:
    def __init__(self):
        self.x = 20.0
        self.y = 20.0


class EinePartieZumVerfolgen:
    """Bewegt ihren Gegner je Schritt 25 Pixel nach rechts und nimmt ihn bei x > 100 heraus."""

    def __init__(self):
        self.gegner = [EinGegnerZumVerfolgen()]
        self.schritte = 0

    def schritt(self, dt):
        self.schritte += 1
        for gegner in list(self.gegner):
            gegner.x += 25.0
            if gegner.x > 100:
                self.gegner.remove(gegner)


class Verfolgen(unittest.TestCase):
    def test_die_spur_nennt_jede_betretene_zelle_und_hoert_auf_wenn_der_gegner_weg_ist(self):
        spiel = EinePartieZumVerfolgen()
        gegner = spiel.gegner[0]
        (spur,) = helfer.verfolge(spiel, [gegner], 50)
        self.assertEqual([(0, 0), (1, 0), (2, 0)], spur.zellen())
        self.assertEqual([(20.0, 20.0), (45.0, 20.0), (70.0, 20.0), (95.0, 20.0)], spur.punkte)
        self.assertEqual(4, spiel.schritte)
        self.assertEqual([], spur.neben_der_linie())

    def test_die_spur_hoert_nach_der_hoechstzahl_von_schritten_auf(self):
        spiel = EinePartieZumVerfolgen()
        helfer.verfolge(spiel, [spiel.gegner[0]], 2)
        self.assertEqual(2, spiel.schritte)

    def test_eine_zelle_die_zweimal_betreten_wird_steht_zweimal_in_der_spur(self):
        gegner = EinGegnerZumVerfolgen()
        spur = helfer.Spur(gegner)
        for x in (50.0, 30.0):
            gegner.x = x
            spur.merke()
        self.assertEqual([(0, 0), (1, 0), (0, 0)], spur.zellen())

    def test_ein_schraeger_punkt_steht_in_neben_der_linie(self):
        gegner = EinGegnerZumVerfolgen()
        spur = helfer.Spur(gegner)
        gegner.x, gegner.y = 31.0, 27.0
        spur.merke()
        self.assertEqual([(31.0, 27.0)], spur.neben_der_linie())

    def test_ist_dabei_erkennt_genau_diesen_gegner(self):
        spiel = EinePartieZumVerfolgen()
        self.assertTrue(helfer.ist_dabei(spiel, spiel.gegner[0]))
        self.assertFalse(helfer.ist_dabei(spiel, EinGegnerZumVerfolgen()))

    def test_schritte_fuer_rechnet_strecke_durch_tempo_in_schritten(self):
        self.assertEqual(60, helfer.schritte_fuer(48, 48, 1 / 60))
        self.assertEqual(30, helfer.schritte_fuer(48, 48, 1 / 30))


class Probepaket(unittest.TestCase):
    def test_das_paket_verhaelt_sich_wie_die_loesung_bis_auf_das_eigene(self):
        eigenes = "def nachbarn(zelle, breite, hoehe):\n    return ['eigen']\n"
        name = helfer.paket_wie_loesung(self, {"raster": eigenes})
        werkbank = Werkbank(name)
        self.assertEqual(Werkbank("loesung").offene(), werkbank.offene())
        self.assertEqual(["eigen"], werkbank.rufe("wegfindung", "nachbarn", (0, 0), 3, 3))
        self.assertEqual([["a", "b"]], werkbank.rufe("karten", "lies_karte", "ab\n"))


if __name__ == "__main__":
    unittest.main()
