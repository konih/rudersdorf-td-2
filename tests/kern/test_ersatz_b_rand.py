"""Der Ersatz zu Spur B an seinen Rändern: was er zusätzlich zu ``test_ersatz_b`` festlegt.

Das Spiel muss sich auch mit lauter offenen Missionen auf den Ersatz verlassen können. Darum
steht hier, was der Ersatz mit besiegten Gegnern, am Rand der Reichweite und mit einer leeren
Liste tut, und dass der "Zufall" bei gleicher Lage immer gleich antwortet. Sonst liefe
dieselbe Partie nicht jedes Mal gleich ab.
"""

import unittest

from rudersdorf.ersatz import ersatz_fuer
from tests.missionen.helfer import TestGegner, TestTurm

# Der Turm steht mitten in der Zelle (2, 2): Zeile und Spalte reichen jeweils von 80 bis 120.
TURM = (100.0, 100.0)
WEITE = 100.0


class ErsatzReichweiteRand(unittest.TestCase):
    def sieht(self, gegner):
        return ersatz_fuer("reichweite", "in_reichweite")(TURM, WEITE, gegner)

    def test_einen_besiegten_gegner_in_der_zeile_sieht_der_ersatz_nicht(self):
        besiegt = TestGegner(leben=0, x=150.0, y=100.0)
        lebendig = TestGegner(leben=1, x=160.0, y=100.0)
        self.assertEqual(self.sieht([besiegt, lebendig]), [lebendig])

    def test_genau_am_rand_der_reichweite_sieht_der_ersatz_den_gegner_noch(self):
        am_rand = TestGegner(x=200.0, y=100.0)  # genau 100 Pixel entfernt
        knapp_dahinter = TestGegner(x=200.5, y=100.0)
        self.assertEqual(self.sieht([am_rand, knapp_dahinter]), [am_rand])

    def test_auch_in_der_zeile_misst_der_ersatz_die_gerade_linie(self):
        # Beide stehen in der Zeile des Turms, aber nicht auf seiner Höhe.
        nah_genug = TestGegner(x=195.0, y=115.0)  # etwa 96,2 Pixel entfernt
        zu_weit = TestGegner(x=199.0, y=118.0)  # etwa 100,6 Pixel entfernt
        self.assertEqual(self.sieht([nah_genug, zu_weit]), [nah_genug])

    def test_einen_gegner_in_der_zelle_des_turms_sieht_der_ersatz(self):
        beim_turm = TestGegner(x=85.0, y=118.0)
        self.assertEqual(self.sieht([beim_turm]), [beim_turm])

    def test_links_und_oberhalb_des_turms_gilt_dasselbe_wie_rechts_und_unterhalb(self):
        links_am_rand = TestGegner(x=0.0, y=100.0)
        oben_am_rand = TestGegner(x=100.0, y=0.0)
        schraeg_links_oben = TestGegner(x=60.0, y=60.0)  # Zelle (1, 1), etwa 56,6 Pixel entfernt
        self.assertEqual(
            self.sieht([links_am_rand, schraeg_links_oben, oben_am_rand]),
            [links_am_rand, oben_am_rand],
        )

    def test_ohne_gegner_sieht_der_ersatz_niemanden(self):
        self.assertEqual(self.sieht([]), [])


def aufstellung():
    """Vier Gegner, bei jedem Aufruf neu und gleich aufgestellt."""
    return [
        TestGegner(leben=50, x=400.0, y=200.0, rest_weg=100.0),
        TestGegner(leben=30, x=300.0, y=200.0, rest_weg=500.0),
        TestGegner(leben=90, x=200.0, y=500.0, rest_weg=300.0),
        TestGegner(leben=10, x=220.0, y=200.0, rest_weg=200.0),
    ]


class ErsatzZufallRand(unittest.TestCase):
    """Der "Zufall" des Ersatzes ist kein Würfel: Bei gleicher Lage antwortet er gleich."""

    def setUp(self):
        self.zufall = ersatz_fuer("strategien", "zufall")
        self.turm = TestTurm(x=200.0, y=200.0)

    def verlauf(self, schritte):
        """Lässt vier Gegner ``schritte`` Male ein Stück laufen und merkt sich, wer gewählt wurde."""
        kandidaten = aufstellung()
        nummern = []
        for _ in range(schritte):
            gewaehlt = self.zufall(kandidaten, self.turm)
            nummern.append([gewaehlt is kandidat for kandidat in kandidaten].index(True))
            for kandidat in kandidaten:
                kandidat.rest_weg -= 0.25
                kandidat.x += 0.25
        return nummern

    def test_dieselbe_partie_laeuft_zweimal_genau_gleich_ab(self):
        erster_lauf = self.verlauf(60)
        zweiter_lauf = self.verlauf(60)
        self.assertEqual(
            erster_lauf,
            zweiter_lauf,
            "Zweimal dieselbe Lage, Schritt für Schritt: Der Ersatz muss gleich wählen.",
        )

    def test_der_ersatz_merkt_sich_nichts_von_frueheren_aufrufen(self):
        kandidaten = aufstellung()
        vorher = self.zufall(kandidaten, self.turm)
        # Dazwischen wird der Ersatz für ganz andere Gegner gefragt, wie von einem zweiten Turm.
        andere = [TestGegner(x=10.0 * nummer, y=7.0) for nummer in range(3)]
        for _ in range(5):
            self.zufall(andere, self.turm)
        self.assertIs(self.zufall(kandidaten, self.turm), vorher)

    def test_wo_der_turm_steht_ist_dem_ersatz_gleich(self):
        kandidaten = aufstellung()
        woanders = TestTurm(x=777.0, y=13.0)
        self.assertIs(self.zufall(kandidaten, woanders), self.zufall(kandidaten, self.turm))

    def test_ueber_laengere_zeit_kommt_jeder_gegner_einmal_dran(self):
        self.assertEqual(sorted(set(self.verlauf(60))), [0, 1, 2, 3])

    def test_ist_nur_ein_gegner_da_waehlt_der_ersatz_ihn(self):
        allein = TestGegner(x=333.3, y=12.7)
        self.assertIs(self.zufall([allein], self.turm), allein)

    def test_auch_links_und_oberhalb_der_karte_waehlt_der_ersatz_einen_kandidaten(self):
        # Ein Gegner kann beim Hereinlaufen kurz außerhalb der Karte stehen. Die Nummer
        # darf auch dann nicht neben die Liste greifen.
        kandidaten = [TestGegner(x=-30.5, y=-2.0), TestGegner(x=-10.0, y=4.0), TestGegner(x=-1.5)]
        gewaehlt = self.zufall(kandidaten, self.turm)
        self.assertTrue(any(gewaehlt is kandidat for kandidat in kandidaten))


class ErsatzKettenblitzRand(unittest.TestCase):
    def test_der_start_wird_auch_getroffen_wenn_er_in_der_liste_fehlt(self):
        kettenblitz = ersatz_fuer("kettenblitz", "kettenblitz")
        start = TestGegner(x=100.0, y=100.0)
        daneben = TestGegner(x=110.0, y=100.0)
        self.assertEqual(kettenblitz(start, [daneben], 2, 50.0), [start])
        self.assertEqual(kettenblitz(start, [], 2, 50.0), [start])


if __name__ == "__main__":
    unittest.main()
