"""Die Hilfen der Missionstests selbst: Paketwahl, Meldungen, gezeichnete Karten, Testgegner.

Diese Tests brauchen keine gelöste Mission. Sie sind von Anfang an grün.
"""

import os
import unittest
from unittest import mock

from rudersdorf.fehler import NochOffen
from tests.missionen import helfer


def drei_teile(text):
    """Zerlegt eine Meldung in ihre Zeilen und prüft nichts; das tun die Tests."""
    return text.strip("\n").split("\n")


class Paketwahl(unittest.TestCase):
    def test_ohne_die_variable_wird_die_werkstatt_geprueft(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("RUDERSDORF_LOESUNG", None)
            self.assertEqual(helfer.lade_modul("raster").__name__, "werkstatt.raster")

    def test_mit_der_variable_auf_eins_wird_die_loesung_geprueft(self):
        with mock.patch.dict(os.environ, {"RUDERSDORF_LOESUNG": "1"}):
            self.assertEqual(helfer.lade_modul("raster").__name__, "loesung.raster")

    def test_ein_missionstest_laedt_sein_modul_vor_jedem_test(self):
        test = helfer.Missionstest("setUp")
        with mock.patch.dict(os.environ, {"RUDERSDORF_LOESUNG": "1"}):
            test.setUp()
        self.assertEqual(test.werkstatt.__name__, "loesung.raster")


class Pruefstand(unittest.TestCase):
    """Gemeinsames für die Tests der Meldungen; selbst ohne Test."""

    def setUp(self):
        self.test = helfer.Missionstest("setUp")

    def meldung_von(self, pruefung, *argumente):
        """Führt eine Prüfung aus, die scheitern soll, und liefert die Zeilen ihrer Meldung."""
        with self.assertRaises(AssertionError) as gefangen:
            pruefung(*argumente)
        return drei_teile(str(gefangen.exception))

    def pruefe_drei_teile(self, zeilen):
        self.assertEqual(len(zeilen), 3, zeilen)
        self.assertTrue(zeilen[0].startswith("Erwartet: "), zeilen)
        self.assertTrue(zeilen[1].startswith("Bekommen: "), zeilen)
        self.assertTrue(zeilen[2].startswith("Tipp: "), zeilen)


class Meldungen(Pruefstand):
    def test_eine_meldung_hat_die_drei_teile_erwartet_bekommen_tipp(self):
        text = helfer.meldung("eine 3", "eine 4", "Zähl noch einmal nach.")
        self.assertEqual(text, "\nErwartet: eine 3\nBekommen: eine 4\nTipp: Zähl noch einmal nach.")

    def test_pruefe_gleich_schweigt_wenn_alles_stimmt(self):
        self.test.pruefe_gleich([(1, 0)], [(1, 0)], "finde(raster, 'S')", "egal")

    def test_pruefe_gleich_meldet_aufruf_erwartung_ergebnis_und_tipp(self):
        zeilen = self.meldung_von(
            self.test.pruefe_gleich, [(0, 1)], [(1, 0)], "finde(raster, 'S')", "Vertauscht?"
        )
        self.assertEqual(
            zeilen,
            [
                "Erwartet: finde(raster, 'S') ergibt [(1, 0)]",
                "Bekommen: [(0, 1)]",
                "Tipp: Vertauscht?",
            ],
        )

    def test_pruefe_gleich_unterscheidet_tupel_und_listen(self):
        zeilen = self.meldung_von(self.test.pruefe_gleich, [[1, 0]], [(1, 0)], "finde()", "Tipp")
        self.pruefe_drei_teile(zeilen)

    def test_pruefe_fehler_schweigt_beim_richtigen_fehler(self):
        self.test.pruefe_fehler(ValueError, "int('x')", "egal", int, "x")

    def test_pruefe_fehler_meldet_wenn_kein_fehler_kommt(self):
        zeilen = self.meldung_von(
            self.test.pruefe_fehler, ValueError, "int('7')", "Melde den Fehler.", int, "7"
        )
        self.assertEqual(
            zeilen,
            [
                "Erwartet: int('7') meldet einen ValueError",
                "Bekommen: kein Fehler, sondern das Ergebnis 7",
                "Tipp: Melde den Fehler.",
            ],
        )

    def test_pruefe_fehler_meldet_einen_fehler_der_falschen_art(self):
        zeilen = self.meldung_von(
            self.test.pruefe_fehler, ValueError, "liste[5]", "Tipp", [].__getitem__, 5
        )
        self.pruefe_drei_teile(zeilen)
        self.assertIn("ein IndexError", zeilen[1])

    def test_pruefe_fehler_laesst_noch_offen_durch(self):
        with self.assertRaises(NochOffen):
            self.test.pruefe_fehler(ValueError, "offen()", "Tipp", offen)

    def test_rufe_sicher_liefert_das_ergebnis(self):
        self.assertEqual(self.test.rufe_sicher("int('7')", "egal", int, "7"), 7)

    def test_rufe_sicher_macht_aus_einem_absturz_eine_meldung_mit_tipp(self):
        zeilen = self.meldung_von(
            self.test.rufe_sicher, "liste[5]", "Erst prüfen.", [].__getitem__, 5
        )
        self.pruefe_drei_teile(zeilen)
        self.assertEqual(zeilen[0], "Erwartet: liste[5] läuft ohne Absturz durch")
        self.assertIn("ein IndexError", zeilen[1])
        self.assertEqual(zeilen[2], "Tipp: Erst prüfen.")

    def test_rufe_sicher_laesst_noch_offen_durch(self):
        with self.assertRaises(NochOffen):
            self.test.rufe_sicher("offen()", "Tipp", offen)

    def test_pruefe_unveraendert_schweigt_wenn_nichts_veraendert_wurde(self):
        self.test.pruefe_unveraendert({(1, 1)}, {(1, 1)}, "gesperrt", "f()", "egal")

    def test_pruefe_unveraendert_meldet_was_vorher_und_nachher_war(self):
        zeilen = self.meldung_von(
            self.test.pruefe_unveraendert, [1], [1, 2], "die Liste", "f(liste)", "Nur lesen."
        )
        self.assertEqual(
            zeilen,
            [
                "Erwartet: f(liste) lässt die Liste so, wie es war: [1]",
                "Bekommen: danach war die Liste [1, 2]",
                "Tipp: Nur lesen.",
            ],
        )


class Abstandsvergleich(Pruefstand):
    ERWARTET = {(0, 0): 1, (1, 0): 0}

    def test_gleiche_abstandskarten_sind_in_ordnung(self):
        self.test.pruefe_abstaende({(1, 0): 0, (0, 0): 1}, self.ERWARTET, "f()", "egal")

    def test_ein_falscher_abstand_wird_mit_seiner_zelle_gemeldet(self):
        zeilen = self.meldung_von(
            self.test.pruefe_abstaende, {(0, 0): 5, (1, 0): 0}, self.ERWARTET, "f()", "Zähle."
        )
        self.assertEqual(
            zeilen,
            [
                "Erwartet: f(): Zelle (0, 0) hat den Abstand 1",
                "Bekommen: Zelle (0, 0) hat den Abstand 5",
                "Tipp: Zähle.",
            ],
        )

    def test_eine_fehlende_zelle_wird_gemeldet(self):
        zeilen = self.meldung_von(
            self.test.pruefe_abstaende, {(1, 0): 0}, self.ERWARTET, "f()", "Tipp"
        )
        self.pruefe_drei_teile(zeilen)
        self.assertEqual(zeilen[1], "Bekommen: Zelle (0, 0) fehlt in der Abstandskarte")

    def test_eine_zelle_zu_viel_wird_gemeldet(self):
        zeilen = self.meldung_von(
            self.test.pruefe_abstaende, {(0, 0): 1, (1, 0): 0, (2, 0): 9}, self.ERWARTET, "f()", "T"
        )
        self.pruefe_drei_teile(zeilen)
        self.assertIn("Zelle (2, 0) steht nicht in der Abstandskarte", zeilen[0])
        self.assertEqual(zeilen[1], "Bekommen: Zelle (2, 0) hat den Abstand 9")

    def test_die_erste_falsche_zelle_in_leserichtung_wird_genannt(self):
        erwartet = {(0, 0): 2, (1, 0): 1, (0, 1): 1, (1, 1): 0}
        bekommen = {(0, 0): 2, (1, 0): 7, (0, 1): 7, (1, 1): 0}
        zeilen = self.meldung_von(self.test.pruefe_abstaende, bekommen, erwartet, "f()", "T")
        self.assertEqual(zeilen[1], "Bekommen: Zelle (1, 0) hat den Abstand 7")

    def test_etwas_anderes_als_ein_woerterbuch_wird_gemeldet(self):
        zeilen = self.meldung_von(self.test.pruefe_abstaende, None, self.ERWARTET, "f()", "T")
        self.pruefe_drei_teile(zeilen)
        self.assertEqual(zeilen[1], "Bekommen: None")


class Reihenfolge(unittest.TestCase):
    ERWARTET = [(1, 0), (0, 1)]

    def test_dieselben_zellen_in_anderer_reihenfolge_werden_erkannt(self):
        self.assertTrue(helfer.nur_die_reihenfolge_ist_anders([(0, 1), (1, 0)], self.ERWARTET))

    def test_die_richtige_antwort_ist_nicht_nur_anders_gereiht(self):
        self.assertFalse(helfer.nur_die_reihenfolge_ist_anders([(1, 0), (0, 1)], self.ERWARTET))

    def test_andere_oder_fehlende_zellen_sind_mehr_als_eine_andere_reihenfolge(self):
        self.assertFalse(helfer.nur_die_reihenfolge_ist_anders([(1, 0), (5, 5)], self.ERWARTET))
        self.assertFalse(helfer.nur_die_reihenfolge_ist_anders([(1, 0)], self.ERWARTET))

    def test_eine_liste_mit_none_darin_bringt_den_vergleich_nicht_zum_absturz(self):
        self.assertFalse(helfer.nur_die_reihenfolge_ist_anders([(1, 0), None], self.ERWARTET))
        self.assertFalse(helfer.nur_die_reihenfolge_ist_anders([None, "x"], self.ERWARTET))

    def test_eine_antwort_die_keine_liste_ist_bringt_ihn_auch_nicht_zum_absturz(self):
        for antwort in (None, 7, {(1, 0), (0, 1)}, ((0, 1), (1, 0))):
            self.assertFalse(helfer.nur_die_reihenfolge_ist_anders(antwort, self.ERWARTET))


class GezeichneteKarten(unittest.TestCase):
    def test_aus_einer_eingerueckten_zeichnung_wird_ein_raster(self):
        raster = helfer.raster_aus(
            """
            S.#
            .~Z
            """
        )
        self.assertEqual(raster, [["S", ".", "#"], [".", "~", "Z"]])

    def test_aus_einer_zeile_wird_ein_raster_mit_einer_zeile(self):
        self.assertEqual(helfer.raster_aus("S.Z"), [["S", ".", "Z"]])

    def test_aus_gezeichneten_zahlen_wird_eine_abstandskarte(self):
        abstaende = helfer.abstaende_aus(
            """
            10  9  #
             -  8  0
            """
        )
        self.assertEqual(abstaende, {(0, 0): 10, (1, 0): 9, (1, 1): 8, (2, 1): 0})


class DerTestgegner(unittest.TestCase):
    def test_er_hat_alles_was_die_werkstatt_von_gegnern_benutzt(self):
        gegner = helfer.TestGegner(leben=30, x=100.0, y=60.0, rest_weg=250.0)
        self.assertEqual(
            (gegner.leben, gegner.max_leben, gegner.x, gegner.y, gegner.rest_weg),
            (30, 30, 100.0, 60.0, 250.0),
        )
        self.assertEqual((gegner.effekte, gegner.fliegt, gegner.ist_boss), ([], False, False))

    def test_jeder_gegner_hat_seine_eigene_effektliste(self):
        erster = helfer.TestGegner()
        erster.effekte.append("frost")
        self.assertEqual(helfer.TestGegner().effekte, [])

    def test_schaden_zieht_leben_ab_und_wird_mitgeschrieben(self):
        gegner = helfer.TestGegner(leben=30)
        verloren = gegner.erleide_schaden(12, "feuer")
        self.assertEqual((gegner.leben, verloren, gegner.schaeden), (18, 12, [(12, "feuer")]))

    def test_das_leben_faellt_nie_unter_null(self):
        gegner = helfer.TestGegner(leben=30)
        verloren = gegner.erleide_schaden(50, "stich")
        self.assertEqual((gegner.leben, verloren), (0, 30))

    def test_negativer_schaden_heilt_nicht(self):
        gegner = helfer.TestGegner(leben=30)
        gegner.erleide_schaden(-5, "stich")
        self.assertEqual(gegner.leben, 30)

    def test_heilen_geht_nie_ueber_das_volle_leben(self):
        gegner = helfer.TestGegner(leben=10, max_leben=30)
        gegner.heile(15)
        self.assertEqual(gegner.leben, 25)
        gegner.heile(15)
        self.assertEqual((gegner.leben, gegner.heilungen), (30, [15, 15]))


def offen(*argumente):
    raise NochOffen("Mission 0: Probe")
