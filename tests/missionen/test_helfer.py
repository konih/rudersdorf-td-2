"""Die Hilfen der Missionstests selbst: Paketwahl, Meldungen, Zahlen, Wellenregeln, gezeichnete
Karten, Testgegner, Testeffekt, Testturm.

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

    def test_erzeuge_baut_ein_objekt_der_klasse_aus_der_werkstatt(self):
        self.test.werkstatt = helfer
        turm = self.test.erzeuge("TestTurm", 3.0, 4.0)
        self.assertIsInstance(turm, helfer.TestTurm)
        self.assertEqual((turm.x, turm.y), (3.0, 4.0))

    def test_erzeuge_macht_aus_einem_absturz_eine_meldung_mit_aufruf_und_tipp(self):
        self.test.werkstatt = helfer
        zeilen = self.meldung_von(self.test.erzeuge, "TestTurm", 1.0, "zwei", 3.0)
        self.pruefe_drei_teile(zeilen)
        self.assertEqual(zeilen[0], "Erwartet: TestTurm(1.0, 'zwei', 3.0) läuft ohne Absturz durch")
        self.assertIn("ein TypeError", zeilen[1])
        self.assertIn("im __init__ von TestTurm", zeilen[2])

    def test_erzeuge_meldet_auch_eine_fehlende_klasse_und_nimmt_einen_eigenen_tipp(self):
        self.test.werkstatt = helfer
        zeilen = self.meldung_von(lambda: self.test.erzeuge("Drache", 1.0, tipp="Eigener Tipp."))
        self.pruefe_drei_teile(zeilen)
        self.assertIn("ein AttributeError", zeilen[1])
        self.assertEqual(zeilen[2], "Tipp: Eigener Tipp.")

    def test_erzeuge_laesst_noch_offen_durch(self):
        class Offen:
            def __init__(self):
                raise NochOffen("Mission 0: Probe")

        self.test.werkstatt = type("Werkstatt", (), {"Offen": Offen})
        with self.assertRaises(NochOffen):
            self.test.erzeuge("Offen")

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


class Zahlen(Pruefstand):
    """Zahlen werden bis auf einen winzigen Rundungsrest verglichen."""

    def test_ein_rundungsrest_stoert_nicht(self):
        self.assertTrue(helfer.fast_gleich(0.1 + 0.2, 0.3))
        self.assertTrue(helfer.fast_gleich(8, 8.0))

    def test_ein_echter_unterschied_wird_bemerkt(self):
        self.assertFalse(helfer.fast_gleich(0.3001, 0.3))
        self.assertFalse(helfer.fast_gleich(-8.0, 8.0))

    def test_was_keine_zahl_ist_passt_nie(self):
        for antwort in (None, "8", [8], True, float("nan")):
            self.assertFalse(helfer.fast_gleich(antwort, 1), antwort)

    def test_listen_von_zahlen_passen_nur_bei_gleicher_laenge_und_gleichen_zahlen(self):
        self.assertTrue(helfer.alle_fast_gleich([1.0, 0.1 + 0.2], [1.0, 0.3]))
        self.assertTrue(helfer.alle_fast_gleich([], []))
        self.assertFalse(helfer.alle_fast_gleich([1.0], [1.0, 0.3]))
        self.assertFalse(helfer.alle_fast_gleich([1.0, 0.3, 0.3], [1.0, 0.3]))
        self.assertFalse(helfer.alle_fast_gleich([0.3, 1.0], [1.0, 0.3]))

    def test_eine_liste_mit_none_oder_gar_keine_liste_bringt_den_vergleich_nicht_zum_absturz(self):
        self.assertFalse(helfer.alle_fast_gleich([None], [1.0]))
        self.assertFalse(helfer.alle_fast_gleich(None, []))
        self.assertFalse(helfer.alle_fast_gleich((1.0,), [1.0]))

    def test_schaeden_passen_nur_mit_menge_und_art(self):
        self.assertTrue(helfer.schaeden_fast_gleich([(0.1 + 0.2, "gift")], [(0.3, "gift")]))
        self.assertTrue(helfer.schaeden_fast_gleich([], []))
        self.assertFalse(helfer.schaeden_fast_gleich([(0.3, "feuer")], [(0.3, "gift")]))
        self.assertFalse(helfer.schaeden_fast_gleich([(0.4, "gift")], [(0.3, "gift")]))
        self.assertFalse(helfer.schaeden_fast_gleich([], [(0.3, "gift")]))
        self.assertFalse(
            helfer.schaeden_fast_gleich([(0.3, "gift"), (0.3, "gift")], [(0.3, "gift")])
        )

    def test_unpassende_schaeden_bringen_den_vergleich_nicht_zum_absturz(self):
        for schaeden in ([(None, "gift")], [("viel", "gift")], [None], [(0.3,)], None):
            self.assertFalse(helfer.schaeden_fast_gleich(schaeden, [(0.3, "gift")]), schaeden)

    def test_pruefe_zahl_schweigt_bei_einem_rundungsrest(self):
        self.test.pruefe_zahl(0.1 + 0.2, 0.3, "f()", "egal")

    def test_pruefe_zahl_meldet_aufruf_erwartung_ergebnis_und_tipp(self):
        zeilen = self.meldung_von(self.test.pruefe_zahl, None, 8.0, "f(20)", "Rechne nach.")
        self.assertEqual(
            zeilen, ["Erwartet: f(20) ergibt 8.0", "Bekommen: None", "Tipp: Rechne nach."]
        )

    def test_lies_attribut_liefert_den_wert(self):
        self.assertEqual(self.test.lies_attribut(helfer.TestTurm(x=7.0), "x", "egal"), 7.0)

    def test_lies_attribut_liefert_auch_none_wenn_das_der_wert_ist(self):
        turm = helfer.TestTurm()
        turm.ziel = None
        self.assertIsNone(self.test.lies_attribut(turm, "ziel", "egal"))

    def test_lies_attribut_meldet_ein_fehlendes_attribut_mit_tipp(self):
        zeilen = self.meldung_von(
            self.test.lies_attribut, helfer.TestTurm(), "rest", "Setze es in __init__."
        )
        self.assertEqual(
            zeilen,
            [
                "Erwartet: TestTurm hat das Attribut rest",
                "Bekommen: TestTurm hat kein Attribut rest",
                "Tipp: Setze es in __init__.",
            ],
        )

    def test_pruefe_schaeden_schweigt_wenn_die_schaeden_stimmen(self):
        gegner = helfer.TestGegner()
        gegner.erleide_schaden(0.1 + 0.2, "gift")
        self.test.pruefe_schaeden(gegner, [(0.3, "gift")], "tick()", "egal")

    def test_pruefe_schaeden_meldet_erwartete_und_erlittene_schaeden(self):
        gegner = helfer.TestGegner()
        gegner.erleide_schaden(2.0, "feuer")
        zeilen = self.meldung_von(
            self.test.pruefe_schaeden, gegner, [(2.0, "gift")], "tick()", "Schau auf die Art."
        )
        self.pruefe_drei_teile(zeilen)
        self.assertIn("nach tick()", zeilen[0])
        self.assertIn("[(2.0, 'gift')]", zeilen[0])
        self.assertIn("[(2.0, 'feuer')]", zeilen[1])

    def test_pruefe_heilungen_schweigt_wenn_die_heilungen_stimmen(self):
        gegner = helfer.TestGegner(leben=10, max_leben=30)
        gegner.heile(0.1 + 0.2)
        self.test.pruefe_heilungen(gegner, [0.3], "aktualisiere()", "egal")

    def test_pruefe_heilungen_meldet_erwartete_und_bekommene_heilungen(self):
        gegner = helfer.TestGegner(leben=10, max_leben=30)
        zeilen = self.meldung_von(
            self.test.pruefe_heilungen, gegner, [1.0], "aktualisiere()", "Ruf heile auf."
        )
        self.pruefe_drei_teile(zeilen)
        self.assertIn("[1.0]", zeilen[0])
        self.assertIn("[]", zeilen[1])


class Wellenregeln(unittest.TestCase):
    """``wellenfehler`` findet jeden Verstoß gegen die Regeln aus Mission 15 und stürzt nie ab."""

    KATALOG = {
        "ork": {"preis": 5, "ab_welle": 1, "boss": False},
        "wolf": {"preis": 6, "ab_welle": 2, "boss": False},
        "kobold": {"preis": 2, "ab_welle": 9, "boss": False},
        "koenig": {"preis": 3, "ab_welle": 1, "boss": True},
    }

    def fehler(self, welle, nummer=3, budget=17):
        return helfer.wellenfehler(welle, nummer, budget, self.KATALOG)

    def test_eine_richtige_welle_hat_keinen_fehler(self):
        self.assertIsNone(self.fehler(["ork", "wolf", "ork"]))  # 16 von 17, Rest 1
        self.assertIsNone(self.fehler(["wolf", "ork", "wolf"]))  # 17 von 17, Rest 0

    def test_eine_leere_welle_ist_richtig_wenn_das_geld_fuer_niemanden_reicht(self):
        # Mit 4 Münzen wären nur der Kobold (gesperrt) und der König (Boss) bezahlbar.
        self.assertIsNone(self.fehler([], budget=4))
        self.assertIsNone(self.fehler([], budget=0))
        self.assertIsNone(self.fehler([], budget=-5))

    def test_ein_rest_fuer_den_gesperrten_kobold_oder_den_boss_ist_kein_fehler(self):
        self.assertIsNone(self.fehler(["ork", "ork", "ork"], budget=19))  # Rest 4

    def test_die_art_die_genau_in_dieser_welle_frei_wird_ist_erlaubt(self):
        self.assertIsNone(self.fehler(["wolf", "wolf", "ork"], nummer=2))

    def test_etwas_anderes_als_eine_liste_wird_gemeldet(self):
        for antwort in (None, "ork", ("ork",), 3):
            self.assertIn("eine Liste", self.fehler(antwort)[0], antwort)

    def test_ein_eintrag_der_kein_name_des_katalogs_ist_wird_gemeldet(self):
        for eintrag in ("drache", None, 5, ["ork"], {"preis": 5}):
            fehler = self.fehler(["ork", eintrag])
            self.assertIn("nur Namen aus dem Katalog", fehler[0], eintrag)
            self.assertIn(repr(eintrag), fehler[1])

    def test_ein_boss_wird_gemeldet(self):
        fehler = self.fehler(["ork", "koenig", "ork"])
        self.assertEqual(fehler[0], "eine Welle ohne Boss")
        self.assertIn("'koenig'", fehler[1])

    def test_eine_noch_gesperrte_art_wird_gemeldet(self):
        fehler = self.fehler(["ork", "wolf"], nummer=1, budget=11)
        self.assertIn("in Welle 1 nur Arten, die schon freigeschaltet sind", fehler[0])
        self.assertIn("'wolf'", fehler[1])
        self.assertIn("ab Welle 2", fehler[1])

    def test_eine_zu_teure_welle_wird_gemeldet(self):
        fehler = self.fehler(["wolf", "wolf", "wolf"])  # 18 von 17
        self.assertIn("höchstens 17 Münzen", fehler[0])
        self.assertIn("18 Münzen", fehler[1])

    def test_uebriges_geld_fuer_einen_erlaubten_gegner_wird_gemeldet(self):
        fehler = self.fehler(["wolf", "wolf"])  # 12 von 17: ein Ork ginge noch
        self.assertIn("noch 5 Münzen übrig", fehler[1])
        self.assertIn("['ork']", fehler[1])
        fehler = self.fehler([], budget=6)
        self.assertIn("['ork', 'wolf']", fehler[1])

    def test_eine_absurd_lange_welle_wird_gemeldet_ohne_sie_ganz_auszuschreiben(self):
        # Für 17 Münzen gibt es höchstens 8 Gegner, selbst wenn alle so billig wären wie der Kobold.
        fehler = self.fehler(["ork"] * 100_000)
        self.assertIn("höchstens 8 Gegner", fehler[0])
        self.assertIn("100000 Gegnern", fehler[1])
        self.assertIn("viel zu lang", fehler[2])
        self.assertLess(len(fehler[1]), 300)

    def test_bei_negativem_budget_ist_jeder_gegner_einer_zu_viel(self):
        self.assertIn("höchstens 0 Gegner", self.fehler(["ork"], budget=-5)[0])

    def test_mit_einem_leeren_katalog_ist_nur_die_leere_welle_richtig(self):
        self.assertIsNone(helfer.wellenfehler([], 3, 17, {}))
        self.assertIn("nur Namen aus dem Katalog", helfer.wellenfehler(["ork"], 3, 17, {})[0])

    def test_jeder_fehler_hat_die_drei_teile_einer_meldung(self):
        for welle in (None, ["drache"], ["koenig"], ["kobold"], ["wolf"] * 3, [], ["ork"] * 99):
            fehler = self.fehler(welle)
            self.assertEqual(len(fehler), 3, welle)
            self.assertTrue(all(isinstance(teil, str) and teil for teil in fehler), welle)

    def test_kurz_schreibt_kurze_listen_ganz_und_lange_nur_am_anfang(self):
        self.assertEqual(helfer.kurz(["ork", "wolf"]), "['ork', 'wolf']")
        self.assertEqual(helfer.kurz(list(range(12))), repr(list(range(12))))
        self.assertEqual(helfer.kurz([1, 2, 3, 4], hoechstens=2), "[1, 2, ... und 2 weitere]")
        self.assertEqual(helfer.kurz(None), "None")


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


class DerTesteffekt(unittest.TestCase):
    def test_er_hat_alles_was_ein_effekt_aus_mission_12_hat(self):
        effekt = helfer.TestEffekt("frost", rest=2.0, faktor=0.5)
        self.assertEqual(
            (effekt.name, effekt.dauer, effekt.rest, effekt.ist_vorbei(), effekt.tempo_faktor()),
            ("frost", 2.0, 2.0, False, 0.5),
        )

    def test_ohne_weitere_angaben_wirkt_er_noch_und_bremst_nicht(self):
        effekt = helfer.TestEffekt("gift")
        self.assertEqual(
            (effekt.rest, effekt.ist_vorbei(), effekt.tempo_faktor()), (1.0, False, 1.0)
        )

    def test_tick_laesst_die_zeit_vergehen_aber_nie_unter_null(self):
        effekt = helfer.TestEffekt("frost", rest=2.0)
        effekt.tick(None, 0.5)
        self.assertEqual((effekt.rest, effekt.ist_vorbei()), (1.5, False))
        effekt.tick(None, -1.0)
        self.assertEqual(effekt.rest, 1.5)
        effekt.tick(None, 5.0)
        self.assertEqual((effekt.rest, effekt.ist_vorbei(), effekt.dauer), (0.0, True, 2.0))

    def test_mit_dem_rest_null_ist_er_von_anfang_an_vorbei(self):
        self.assertTrue(helfer.TestEffekt("brand", rest=0.0).ist_vorbei())

    def test_er_nennt_seinen_faktor_mit_absicht_auch_wenn_er_vorbei_ist(self):
        effekt = helfer.TestEffekt("frost", rest=0.0, faktor=0.2)
        self.assertEqual((effekt.ist_vorbei(), effekt.tempo_faktor()), (True, 0.2))

    def test_zwei_gleiche_effekte_sind_trotzdem_zwei_verschiedene(self):
        # Die Tests vergleichen Listen von Effekten. Dabei soll nur derselbe Effekt passen.
        self.assertNotEqual(helfer.TestEffekt("frost"), helfer.TestEffekt("frost"))

    def test_in_einer_meldung_nennt_er_namen_rest_und_faktor(self):
        self.assertEqual(
            repr(helfer.TestEffekt("frost", rest=2.0, faktor=0.5)),
            "TestEffekt('frost', rest=2.0, faktor=0.5)",
        )


class DerTestturm(unittest.TestCase):
    def test_er_steht_dort_wo_man_ihn_hinstellt(self):
        turm = helfer.TestTurm(x=200.0, y=120.0)
        self.assertEqual((turm.x, turm.y), (200.0, 120.0))

    def test_in_einer_meldung_nennt_er_seinen_platz(self):
        self.assertEqual(repr(helfer.TestTurm(x=200.0, y=120.0)), "TestTurm(x=200.0, y=120.0)")


def offen(*argumente):
    raise NochOffen("Mission 0: Probe")
