"""Die beiden Fehlerklassen, an denen das Spiel Lernenden-Code erkennt."""

import inspect
import unittest

from rudersdorf.fehler import Lernfehler, NochOffen


class Fehlerklassen(unittest.TestCase):
    def test_noch_offen_ist_ein_not_implemented_error(self):
        self.assertTrue(issubclass(NochOffen, NotImplementedError))
        with self.assertRaises(NotImplementedError) as gefangen:
            raise NochOffen("Mission 1: Nachbarn")
        self.assertEqual("Mission 1: Nachbarn", str(gefangen.exception))

    def test_lernfehler_ist_ein_gewoehnlicher_fehler(self):
        self.assertTrue(issubclass(Lernfehler, Exception))
        self.assertFalse(issubclass(Lernfehler, NotImplementedError))

    def test_lernfehler_hat_die_festgelegte_signatur(self):
        parameter = inspect.signature(Lernfehler.__init__).parameters
        self.assertEqual(
            ["self", "faehigkeit", "datei", "zeile", "art", "text", "mission", "spur"],
            list(parameter),
        )
        self.assertEqual("", parameter["spur"].default)

    def test_lernfehler_merkt_sich_alle_angaben(self):
        fehler = Lernfehler(
            "wegfindung", "werkstatt/raster.py", 12, "ZeroDivisionError", "division by zero", 4
        )
        self.assertEqual("wegfindung", fehler.faehigkeit)
        self.assertEqual("werkstatt/raster.py", fehler.datei)
        self.assertEqual(12, fehler.zeile)
        self.assertEqual("ZeroDivisionError", fehler.art)
        self.assertEqual("division by zero", fehler.text)
        self.assertEqual(4, fehler.mission)
        self.assertEqual("", fehler.spur)

    def test_lernfehler_traegt_die_spur(self):
        fehler = Lernfehler("a", "b.py", 1, "c", "d", 2, spur="Traceback ...")
        self.assertEqual("Traceback ...", fehler.spur)

    def test_lernfehler_nennt_datei_zeile_art_und_text(self):
        fehler = Lernfehler("wegfindung", "werkstatt/raster.py", 12, "KeyError", "'x'", 4)
        self.assertEqual("werkstatt/raster.py, Zeile 12: KeyError: 'x'", str(fehler))


if __name__ == "__main__":
    unittest.main()
