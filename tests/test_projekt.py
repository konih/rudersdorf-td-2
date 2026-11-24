"""Grundgerüst: Das Projekt nennt seine einzige Laufzeit-Abhängigkeit und hat alle Pakete."""

import pathlib
import unittest

WURZEL = pathlib.Path(__file__).resolve().parent.parent

PAKETE = (
    "rudersdorf",
    "rudersdorf/kern",
    "rudersdorf/labor",
    "rudersdorf/ansicht",
    "rudersdorf/uebung",
    "werkstatt",
    "loesung",
    "tests",
    "tests/architektur",
    "tests/missionen",
    "tests/kern",
    "tests/ansicht",
    "tests/lernen",
)


class Projekt(unittest.TestCase):
    def test_pygame_ce_ist_die_einzige_abhaengigkeit(self):
        text = (WURZEL / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('dependencies = ["pygame-ce', text)

    def test_grundgeruest_ist_vollstaendig(self):
        fehlend = [paket for paket in PAKETE if not (WURZEL / paket / "__init__.py").is_file()]
        self.assertEqual([], fehlend, "Diesen Paketen fehlt die Datei __init__.py")


if __name__ == "__main__":
    unittest.main()
