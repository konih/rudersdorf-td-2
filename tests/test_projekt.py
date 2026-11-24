"""Grundgerüst: Das Projekt nennt seine einzige Laufzeit-Abhängigkeit."""

import pathlib
import unittest

WURZEL = pathlib.Path(__file__).resolve().parent.parent


class Projekt(unittest.TestCase):
    def test_pygame_ce_ist_die_einzige_abhaengigkeit(self):
        text = (WURZEL / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('dependencies = ["pygame-ce', text)


if __name__ == "__main__":
    unittest.main()
