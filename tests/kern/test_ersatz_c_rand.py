"""Der Ersatz zu Spur C an seinen Rändern: was er zusätzlich zu ``test_ersatz_c`` festlegt.

Das Spiel muss sich auch mit lauter offenen Missionen auf den Ersatz verlassen können. Darum
steht hier, was der Ersatz mit kaputten oder unerwarteten Eingaben tut, was er sich merkt und
dass er nichts würfelt. Sonst liefe dieselbe Partie nicht jedes Mal gleich ab.
"""

import inspect
import random
import unittest

from loesung import horde
from rudersdorf.ersatz import ersatz_fuer
from rudersdorf.werkbank import FAEHIGKEITEN
from tests.missionen.helfer import TestGegner

# Mit Absicht ausgeschrieben: die vier Fähigkeiten der Spur C.
FAEHIGKEITEN_DER_SPUR_C = ("schadensarten", "effekte", "faehigkeiten", "wellen")


class ErsatzGleicheArgumente(unittest.TestCase):
    """Das Spiel ruft Original und Ersatz gleich auf, auch mit benannten Argumenten (so
    stehen sie in den Tabellen des Spiels). Darum müssen die Parameter gleich heißen."""

    def test_jeder_ersatz_hat_dieselben_parameter_wie_die_referenz(self):
        for faehigkeit in FAEHIGKEITEN_DER_SPUR_C:
            for name in FAEHIGKEITEN[faehigkeit]["namen"]:
                with self.subTest(faehigkeit=faehigkeit, name=name):
                    self.assertEqual(
                        str(inspect.signature(ersatz_fuer(faehigkeit, name))),
                        str(inspect.signature(getattr(horde, name))),
                    )

    def test_jede_methode_eines_ersatzes_hat_dieselben_parameter_wie_die_referenz(self):
        for faehigkeit in ("effekte", "faehigkeiten"):
            for name in FAEHIGKEITEN[faehigkeit]["namen"]:
                original = getattr(horde, name)
                if not isinstance(original, type):
                    continue
                for methode in ("tick", "ist_vorbei", "tempo_faktor", "aktualisiere"):
                    if not hasattr(original, methode):
                        continue
                    with self.subTest(name=name, methode=methode):
                        self.assertEqual(
                            str(inspect.signature(getattr(ersatz_fuer(faehigkeit, name), methode))),
                            str(inspect.signature(getattr(original, methode))),
                        )

    def test_der_ersatzbeschwoerer_entsteht_auch_aus_einer_zeile_der_gegnertabelle(self):
        beschwoerer = ersatz_fuer("faehigkeiten", "Beschwoerer")(intervall=6.0, art="ork", anzahl=3)
        self.assertEqual(
            (beschwoerer.intervall, beschwoerer.art, beschwoerer.anzahl), (6.0, "ork", 3)
        )


class ErsatzSchadensartenRand(unittest.TestCase):
    def setUp(self):
        self.berechne_schaden = ersatz_fuer("schadensarten", "berechne_schaden")

    def test_auch_kommazahlen_kommen_unveraendert_an(self):
        self.assertEqual(self.berechne_schaden(12.5, "feuer", {"feuer": 0.4}), 12.5)
        self.assertEqual(self.berechne_schaden(0.25, "gift", {}), 0.25)

    def test_in_die_resistenzen_schaut_der_ersatz_gar_nicht(self):
        # Mit einem kaputten Eintrag oder ganz ohne Wörterbuch scheitert Mission 11 hier.
        self.assertEqual(self.berechne_schaden(20, "feuer", {"feuer": "kaputt"}), 20)
        self.assertEqual(self.berechne_schaden(20, "feuer", None), 20)


class ErsatzEffektklassenRand(unittest.TestCase):
    def erzeuge(self, name, *argumente):
        return ersatz_fuer("effekte", name)(*argumente)

    def alle(self):
        return [
            self.erzeuge("Effekt", 3.0),
            self.erzeuge("Frost", 3.0, 0.5),
            self.erzeuge("Gift", 3.0, 4.0),
            self.erzeuge("Brand", 3.0, 4.0),
            self.erzeuge("Betaeubung", 3.0),
        ]

    def test_jeder_ersatzeffekt_merkt_sich_die_dauer_aber_uebrig_ist_nichts(self):
        # Mission 12 verlangt hier rest == 3.0.
        for effekt in self.alle():
            self.assertEqual((effekt.dauer, effekt.rest), (3.0, 0.0), effekt.name)

    def test_der_rest_bleibt_bei_null_was_auch_vergeht(self):
        for effekt in self.alle():
            for sekunden in (1.0, -5.0, 0):
                effekt.tick(TestGegner(), sekunden)
            self.assertEqual((effekt.dauer, effekt.rest), (3.0, 0.0), effekt.name)

    def test_tick_fasst_den_gegner_nicht_an(self):
        # Ein Gegner, den es gar nicht gibt: Wer ihn anfasst, scheitert.
        for effekt in self.alle():
            self.assertIsNone(effekt.tick(None, 1.0), effekt.name)

    def test_der_ersatz_merkt_sich_womit_er_erzeugt_wurde(self):
        self.assertEqual(self.erzeuge("Frost", 3.0, 0.5).faktor, 0.5)
        self.assertEqual(self.erzeuge("Gift", 3.0, 4.0).schaden_pro_sekunde, 4.0)
        self.assertEqual(self.erzeuge("Brand", 3.0, 6.0).schaden_pro_sekunde, 6.0)

    def test_gift_und_brand_nennen_ihre_schadensart_wie_das_original(self):
        self.assertEqual(self.erzeuge("Gift", 3.0, 4.0).schadensart, "gift")
        self.assertEqual(self.erzeuge("Brand", 3.0, 4.0).schadensart, "feuer")

    def test_die_namen_stehen_wie_im_original_in_der_klasse(self):
        for name in ("Effekt", "Frost", "Gift", "Brand", "Betaeubung"):
            self.assertEqual(ersatz_fuer("effekte", name).name, getattr(horde, name).name, name)

    def test_ein_ersatzbrand_haelt_die_heilung_eines_trolls_nicht_auf(self):
        # Mission 14 gelöst, Mission 12 offen: Der Brand ist sofort vorbei, der Troll heilt.
        troll = TestGegner(leben=50.0, max_leben=100.0)
        troll.effekte = [self.erzeuge("Brand", 3.0, 4.0)]
        horde.Regeneration(2.0).aktualisiere(troll, [troll], 1.0)
        self.assertEqual(troll.heilungen, [2.0])

    def test_die_echte_effektliste_wirft_ersatzeffekte_gleich_wieder_hinaus(self):
        # Mission 13 gelöst, Mission 12 offen: Aufräumen und Bremsen kommen damit zurecht.
        effekte = self.alle()
        self.assertEqual(horde.gesamt_tempo_faktor(effekte), 1.0)
        self.assertEqual(horde.raeume_effekte_auf(effekte), [])


class ErsatzEffektlisteRand(unittest.TestCase):
    def test_die_drei_funktionen_schauen_die_effekte_gar_nicht_an(self):
        # Dinge, die keine Effekte sind: Mission 13 scheitert daran, der Ersatz nicht.
        kaputt = [None, "frost", 7]
        self.assertIsNone(ersatz_fuer("effekte", "fuege_effekt_hinzu")(kaputt, None))
        self.assertEqual(ersatz_fuer("effekte", "gesamt_tempo_faktor")(kaputt), 1.0)
        self.assertEqual(ersatz_fuer("effekte", "raeume_effekte_auf")(kaputt), [])
        self.assertEqual(kaputt, [None, "frost", 7])


class ErsatzFaehigkeitenRand(unittest.TestCase):
    def erzeuge(self, name, *argumente):
        return ersatz_fuer("faehigkeiten", name)(*argumente)

    def test_die_uhr_des_ersatzbeschwoerers_bleibt_stehen(self):
        # Mission 14 verlangt hier nach zwei Sekunden rest == 4.0.
        beschwoerer = self.erzeuge("Beschwoerer", 6.0, "ork", 3)
        traeger = TestGegner()
        for _ in range(10):
            beschwoerer.aktualisiere(traeger, [traeger], 1.0)
        self.assertEqual(beschwoerer.rest, 6.0)

    def test_der_ersatz_merkt_sich_womit_er_erzeugt_wurde(self):
        self.assertEqual(self.erzeuge("Regeneration", 5.0).pro_sekunde, 5.0)
        heiler = self.erzeuge("Heiler", 100.0, 5.0)
        self.assertEqual((heiler.radius, heiler.pro_sekunde), (100.0, 5.0))
        ohne_anzahl = self.erzeuge("Beschwoerer", 6.0, "ork")
        self.assertEqual(
            (ohne_anzahl.intervall, ohne_anzahl.art, ohne_anzahl.anzahl), (6.0, "ork", 1)
        )
        self.assertEqual(self.erzeuge("Beschwoerer", 6.0, "wolf", 3).anzahl, 3)

    def test_keine_ersatzfaehigkeit_schaut_den_traeger_oder_die_anderen_an(self):
        for faehigkeit in (
            self.erzeuge("Regeneration", 5.0),
            self.erzeuge("Heiler", 100.0, 5.0),
            self.erzeuge("Beschwoerer", 1.0, "ork"),
        ):
            self.assertEqual(faehigkeit.aktualisiere(None, None, 1.0), [])


class ErsatzWellenRand(unittest.TestCase):
    def setUp(self):
        self.erzeuge_welle = ersatz_fuer("wellen", "erzeuge_welle")

    def katalog(self, preis=7, ab_welle=1, boss=False):
        return {"ork": {"preis": preis, "ab_welle": ab_welle, "boss": boss}}

    def test_ein_budget_genau_so_gross_wie_der_preis_bezahlt_einen_ork(self):
        self.assertEqual(self.erzeuge_welle(1, 7, self.katalog(), random.Random(1)), ["ork"])
        self.assertEqual(self.erzeuge_welle(1, 14, self.katalog(), random.Random(1)), ["ork"] * 2)

    def test_ohne_ork_im_katalog_ist_die_welle_leer(self):
        katalog = {"wolf": {"preis": 6, "ab_welle": 1, "boss": False}}
        self.assertEqual(self.erzeuge_welle(5, 100, katalog, random.Random(1)), [])
        self.assertEqual(self.erzeuge_welle(5, 100, {}, random.Random(1)), [])

    def test_ein_ork_der_nichts_kostet_haelt_das_spiel_nicht_an(self):
        # Geteilt durch 0 gäbe einen Fehler, und für 0 Münzen gäbe es unendlich viele Orks.
        self.assertEqual(self.erzeuge_welle(5, 100, self.katalog(preis=0), random.Random(1)), [])
        self.assertEqual(self.erzeuge_welle(5, 100, self.katalog(preis=-3), random.Random(1)), [])

    def test_wann_der_ork_frei_wird_und_ob_er_ein_boss_ist_sieht_der_ersatz_nicht(self):
        # Mission 15 liefert in beiden Fällen eine leere Welle.
        spaet = self.katalog(ab_welle=9)
        self.assertEqual(self.erzeuge_welle(1, 21, spaet, random.Random(1)), ["ork"] * 3)
        boss = self.katalog(boss=True)
        self.assertEqual(self.erzeuge_welle(1, 21, boss, random.Random(1)), ["ork"] * 3)

    def test_der_ersatz_wuerfelt_nicht(self):
        zufall = random.Random(1)
        vorher = zufall.getstate()
        self.erzeuge_welle(5, 100, self.katalog(), zufall)
        self.assertEqual(zufall.getstate(), vorher)
        # Er braucht den Zufall nicht einmal.
        self.assertEqual(self.erzeuge_welle(5, 21, self.katalog(), None), ["ork"] * 3)


if __name__ == "__main__":
    unittest.main()
