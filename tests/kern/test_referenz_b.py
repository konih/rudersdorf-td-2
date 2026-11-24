"""Die sechste Strategie der Referenz: ``gefaehrlichster`` (Mission 8).

Mission 8 lässt offen, welche eigene Regel jemand erfindet. Die Referenz hat sich für diese
entschieden: aus der Vorhut (dem vordersten Viertel zwischen kleinstem und größtem Restweg)
der Gegner mit dem meisten Leben. Hier steht, dass sie genau das tut.
"""

import unittest

from loesung import strategien
from tests.missionen.helfer import TestGegner, TestTurm

TURM = TestTurm(x=200.0, y=200.0)


class Gefaehrlichster(unittest.TestCase):
    def test_aus_der_vorhut_gewinnt_der_gegner_mit_dem_meisten_leben(self):
        # Restweg von 100 bis 500: Die Vorhut reicht bis 200.
        vorn_schwach = TestGegner(leben=20, rest_weg=100.0)
        vorn_stark = TestGegner(leben=80, rest_weg=150.0)
        hinten_riese = TestGegner(leben=900, rest_weg=500.0)
        kandidaten = [vorn_schwach, vorn_stark, hinten_riese]
        self.assertIs(strategien.gefaehrlichster(kandidaten, TURM), vorn_stark)

    def test_wer_genau_auf_der_grenze_der_vorhut_steht_gehoert_dazu(self):
        vorn = TestGegner(leben=20, rest_weg=100.0)
        auf_der_grenze = TestGegner(leben=80, rest_weg=200.0)
        hinten = TestGegner(leben=900, rest_weg=500.0)
        self.assertIs(
            strategien.gefaehrlichster([vorn, auf_der_grenze, hinten], TURM), auf_der_grenze
        )

    def test_wer_knapp_hinter_der_grenze_steht_gehoert_nicht_dazu(self):
        vorn = TestGegner(leben=20, rest_weg=100.0)
        knapp_dahinter = TestGegner(leben=80, rest_weg=201.0)
        hinten = TestGegner(leben=900, rest_weg=500.0)
        self.assertIs(strategien.gefaehrlichster([vorn, knapp_dahinter, hinten], TURM), vorn)

    def test_die_grenze_ist_ein_viertel_der_spanne_und_nicht_des_restwegs(self):
        # Restweg von 1000 bis 1400: Die Vorhut reicht bis 1100, nicht bis 1250 oder 350.
        vorn = TestGegner(leben=20, rest_weg=1000.0)
        dahinter = TestGegner(leben=80, rest_weg=1200.0)
        hinten = TestGegner(leben=900, rest_weg=1400.0)
        self.assertIs(strategien.gefaehrlichster([vorn, dahinter, hinten], TURM), vorn)

    def test_es_zaehlt_das_leben_von_jetzt_nicht_das_volle_leben(self):
        angeschlagen = TestGegner(leben=10, max_leben=500, rest_weg=100.0)
        frisch = TestGegner(leben=40, max_leben=40, rest_weg=110.0)
        hinten = TestGegner(leben=5, rest_weg=900.0)
        self.assertIs(strategien.gefaehrlichster([angeschlagen, frisch, hinten], TURM), frisch)

    def test_bei_gleichem_leben_in_der_vorhut_gewinnt_der_fruehere_in_der_liste(self):
        hinten = TestGegner(leben=900, rest_weg=500.0)
        zuerst = TestGegner(leben=50, rest_weg=120.0)
        danach = TestGegner(leben=50, rest_weg=100.0)
        self.assertIs(strategien.gefaehrlichster([hinten, zuerst, danach], TURM), zuerst)

    def test_haben_alle_denselben_restweg_sind_alle_die_vorhut(self):
        klein = TestGegner(leben=10, rest_weg=300.0)
        gross = TestGegner(leben=70, rest_weg=300.0)
        self.assertIs(strategien.gefaehrlichster([klein, gross], TURM), gross)

    def test_aus_einer_leeren_liste_waehlt_die_regel_none(self):
        self.assertIsNone(strategien.gefaehrlichster([], TURM))

    def test_die_regel_laesst_die_liste_der_kandidaten_wie_sie_war(self):
        kandidaten = [
            TestGegner(leben=20, rest_weg=400.0),
            TestGegner(leben=80, rest_weg=100.0),
            TestGegner(leben=30, rest_weg=250.0),
        ]
        vorher = list(kandidaten)
        strategien.gefaehrlichster(kandidaten, TURM)
        self.assertEqual(kandidaten, vorher)

    def test_die_regel_steht_unter_ihrem_namen_in_der_tabelle(self):
        self.assertIs(strategien.STRATEGIEN.get("gefaehrlichster"), strategien.gefaehrlichster)
        self.assertEqual(len(strategien.STRATEGIEN), 6, "die fünf Regeln der Mission 7 und diese")


if __name__ == "__main__":
    unittest.main()
