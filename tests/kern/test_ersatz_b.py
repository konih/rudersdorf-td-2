"""Der Ersatz zu Spur B: was das Spiel benutzt, solange die Missionen 6 bis 10 offen sind.

Ein Ersatz ist mit Absicht schwächer als die echte Regel, und man soll das im Spiel sehen.
Jede Klasse hier zeigt darum an einem kleinen Beispiel, wo der Ersatz anders antwortet, als es
die Mission verlangt. Geholt wird jeder Ersatz so, wie ihn auch die Werkbank holt: aus dem
Verzeichnis in ``rudersdorf/ersatz.py``.
"""

import unittest

from rudersdorf.ersatz import ERSATZ, ersatz_fuer
from rudersdorf.werkbank import FAEHIGKEITEN
from tests.missionen.helfer import TestGegner, TestTurm

# Der Turm steht mitten in der Zelle (2, 2). Eine Zelle ist 40 Pixel breit und hoch: Seine
# Zeile reicht also von y = 80 bis y = 120, seine Spalte von x = 80 bis x = 120.
TURM = (100.0, 100.0)
WEITE = 100.0


def kandidaten_fuer_den_zufall():
    """Vier Gegner. Jede Regel aus Mission 7 würde immer denselben von ihnen aussuchen."""
    return [
        TestGegner(leben=50, x=400.0, y=200.0, rest_weg=100.0),
        TestGegner(leben=30, x=300.0, y=200.0, rest_weg=500.0),
        TestGegner(leben=90, x=200.0, y=500.0, rest_weg=300.0),
        TestGegner(leben=10, x=220.0, y=200.0, rest_weg=200.0),
    ]


def hole_ersatz(test, faehigkeit, name):
    """Holt einen Ersatz so, wie ihn die Werkbank holt. Fehlt er, scheitert der Test mit Ansage."""
    test.assertIn(
        name,
        ERSATZ.get(faehigkeit, {}),
        f"Im Verzeichnis ERSATZ fehlt unter {faehigkeit!r} der Eintrag {name!r}.",
    )
    return ersatz_fuer(faehigkeit, name)


class ErsatzVollstaendig(unittest.TestCase):
    """Für jeden Namen einer Fähigkeit gibt es einen Ersatz, sonst bliebe das Spiel stehen."""

    def pruefe_alle_namen(self, faehigkeit):
        for name in FAEHIGKEITEN[faehigkeit]["namen"]:
            ersatz = hole_ersatz(self, faehigkeit, name)
            self.assertTrue(
                callable(ersatz), f"Der Ersatz für {faehigkeit}.{name} lässt sich nicht aufrufen."
            )

    def test_reichweite_hat_einen_ersatz_fuer_jeden_namen(self):
        self.pruefe_alle_namen("reichweite")

    def test_kettenblitz_hat_einen_ersatz_fuer_jeden_namen(self):
        self.pruefe_alle_namen("kettenblitz")

    def test_ausbau_hat_einen_ersatz_fuer_jeden_namen(self):
        self.pruefe_alle_namen("ausbau")

    def test_die_strategien_haben_als_ersatz_nur_den_zufall(self):
        # Die Werkbank fragt bei offenen Strategien nur nach "zufall". Mehr bietet das Menü
        # eines Turms dann nicht an.
        self.assertEqual(
            list(ERSATZ.get("strategien", {})),
            ["zufall"],
            'Unter "strategien" steht im Verzeichnis ERSATZ genau ein Eintrag: "zufall".',
        )
        self.assertTrue(callable(hole_ersatz(self, "strategien", "zufall")))


class ErsatzReichweite(unittest.TestCase):
    """Ohne Mission 6 hat ein Turm einen Tunnelblick: Er sieht nur Gegner in seiner eigenen
    Zeile oder Spalte der Karte, und auch dort nur bis zu seiner Reichweite."""

    def sieht(self, gegner):
        return hole_ersatz(self, "reichweite", "in_reichweite")(TURM, WEITE, gegner)

    def test_einen_gegner_in_der_zeile_des_turms_sieht_der_ersatz(self):
        rechts = TestGegner(x=180.0, y=100.0)
        links = TestGegner(x=20.0, y=100.0)
        self.assertEqual(self.sieht([rechts, links]), [rechts, links])

    def test_einen_gegner_in_der_spalte_des_turms_sieht_der_ersatz(self):
        oben = TestGegner(x=100.0, y=20.0)
        unten = TestGegner(x=100.0, y=180.0)
        self.assertEqual(self.sieht([oben, unten]), [oben, unten])

    def test_einen_schraeg_stehenden_gegner_im_kreis_sieht_der_ersatz_nicht(self):
        # Mission 6 sieht diesen Gegner: Er ist nur etwa 70,7 Pixel entfernt.
        schraeg = TestGegner(x=150.0, y=150.0)
        self.assertEqual(
            self.sieht([schraeg]),
            [],
            "Der Gegner steht weder in der Zeile noch in der Spalte des Turms.",
        )

    def test_die_zeile_ist_so_breit_wie_eine_zelle(self):
        noch_in_der_zeile = TestGegner(x=180.0, y=115.0)  # Zeile 2 reicht bis y = 120
        schon_darunter = TestGegner(x=180.0, y=125.0)  # das ist Zeile 3
        self.assertEqual(self.sieht([noch_in_der_zeile, schon_darunter]), [noch_in_der_zeile])

    def test_die_spalte_ist_so_breit_wie_eine_zelle(self):
        noch_in_der_spalte = TestGegner(x=85.0, y=180.0)  # Spalte 2 beginnt bei x = 80
        schon_daneben = TestGegner(x=75.0, y=180.0)  # das ist Spalte 1
        self.assertEqual(self.sieht([noch_in_der_spalte, schon_daneben]), [noch_in_der_spalte])

    def test_auch_in_der_zeile_sieht_der_ersatz_nicht_weiter_als_die_reichweite(self):
        zu_weit = TestGegner(x=260.0, y=100.0)  # 160 Pixel entfernt
        self.assertEqual(self.sieht([zu_weit]), [])

    def test_gesehene_gegner_bleiben_in_der_reihenfolge_der_liste(self):
        unten = TestGegner(x=100.0, y=180.0)
        schraeg = TestGegner(x=150.0, y=150.0)
        rechts = TestGegner(x=140.0, y=100.0)
        self.assertEqual(self.sieht([unten, schraeg, rechts]), [unten, rechts])

    def test_der_ersatz_laesst_die_liste_der_gegner_wie_sie_war(self):
        rechts = TestGegner(x=180.0, y=100.0)
        schraeg = TestGegner(x=150.0, y=150.0)
        gegner = [rechts, schraeg]
        self.sieht(gegner)
        self.assertEqual(gegner, [rechts, schraeg])

    def test_der_ersatz_liefert_eine_neue_liste_auch_wenn_er_alle_sieht(self):
        gegner = [TestGegner(x=180.0, y=100.0), TestGegner(x=100.0, y=20.0)]
        bekommen = self.sieht(gegner)
        self.assertEqual(bekommen, gegner)
        self.assertIsNot(bekommen, gegner)


class ErsatzStrategien(unittest.TestCase):
    """Ohne Mission 7 zielt ein Turm auf irgendwen: Der Ersatz würfelt."""

    def setUp(self):
        self.zufall = hole_ersatz(self, "strategien", "zufall")
        self.turm = TestTurm(x=200.0, y=200.0)

    def test_der_zufall_waehlt_immer_einen_der_kandidaten(self):
        kandidaten = kandidaten_fuer_den_zufall()
        for _ in range(50):
            gewaehlt = self.zufall(kandidaten, self.turm)
            self.assertTrue(
                any(gewaehlt is kandidat for kandidat in kandidaten),
                f"{gewaehlt!r} ist keiner der Kandidaten.",
            )

    def test_der_zufall_bleibt_nicht_bei_einem_gegner_wie_es_eine_regel_taete(self):
        # Die Gegner rücken wie im Spiel bei jedem Versuch ein Stück vor. Ihre Rangfolge bleibt
        # dabei gleich: Jede Regel aus Mission 7 sucht alle 200 Male denselben Gegner aus.
        kandidaten = kandidaten_fuer_den_zufall()
        gewaehlt = []
        for _ in range(200):
            gegner = self.zufall(kandidaten, self.turm)
            if not any(gegner is schon for schon in gewaehlt):
                gewaehlt.append(gegner)
            for kandidat in kandidaten:
                kandidat.rest_weg -= 0.25
                kandidat.x += 0.25
        self.assertGreater(
            len(gewaehlt),
            1,
            "In 200 Versuchen hat der Ersatz immer denselben Gegner gewählt. "
            "Das ist eine feste Regel und kein Zufall.",
        )

    def test_aus_einer_leeren_liste_waehlt_der_zufall_none(self):
        self.assertIsNone(self.zufall([], self.turm))

    def test_der_zufall_laesst_die_liste_der_kandidaten_wie_sie_war(self):
        kandidaten = kandidaten_fuer_den_zufall()
        vorher = list(kandidaten)
        for _ in range(20):
            self.zufall(kandidaten, self.turm)
        self.assertEqual(kandidaten, vorher)


class ErsatzKettenblitz(unittest.TestCase):
    """Ohne Mission 9 springt der Blitz nicht: Er trifft nur den ersten Gegner."""

    def setUp(self):
        self.kettenblitz = hole_ersatz(self, "kettenblitz", "kettenblitz")
        self.reihe = [TestGegner(x=100.0 + 50.0 * nummer, y=100.0) for nummer in range(4)]

    def test_auch_wenn_andere_nah_genug_stehen_trifft_der_ersatz_nur_den_start(self):
        # Mission 9 verlangt hier die ganze Reihe: vier Gegner, jeder 50 vom nächsten entfernt.
        start = self.reihe[0]
        self.assertEqual(self.kettenblitz(start, self.reihe, 3, 60.0), [start])

    def test_ohne_spruenge_trifft_der_ersatz_ebenfalls_nur_den_start(self):
        start = self.reihe[1]
        self.assertEqual(self.kettenblitz(start, self.reihe, 0, 60.0), [start])

    def test_jeder_aufruf_liefert_eine_eigene_liste(self):
        start = self.reihe[0]
        erste = self.kettenblitz(start, self.reihe, 3, 60.0)
        erste.append("verdorben")
        self.assertEqual(self.kettenblitz(start, self.reihe, 3, 60.0), [start])

    def test_der_ersatz_laesst_die_liste_der_gegner_wie_sie_war(self):
        vorher = list(self.reihe)
        self.kettenblitz(self.reihe[0], self.reihe, 3, 60.0)
        self.assertEqual(self.reihe, vorher)


class ErsatzAusbau(unittest.TestCase):
    """Ohne Mission 10 gibt es keine Turmschmiede: Der Ersatz antwortet auf jeden Ausbau mit
    None. Das heißt für das Spiel: Dieser Turm kann nicht ausgebaut werden."""

    def setUp(self):
        self.wende_ausbau_an = hole_ersatz(self, "ausbau", "wende_ausbau_an")

    def test_auf_einen_ausbau_antwortet_der_ersatz_mit_none(self):
        # Mission 10 verlangt hier {"schaden": 15, "reichweite": 120.0}.
        werte = {"schaden": 10, "reichweite": 120.0}
        self.assertIsNone(
            self.wende_ausbau_an(werte, {"schaden": ("+", 5)}),
            "None heißt: Ausbauen gibt es noch nicht. Verbesserte Werte liefert der Ersatz nie.",
        )

    def test_auch_auf_einen_leeren_oder_falschen_ausbau_antwortet_der_ersatz_mit_none(self):
        # Mission 10 verlangt beim zweiten Ausbau einen ValueError. Der Ersatz meldet keinen
        # Fehler: Er sieht sich den Ausbau gar nicht an.
        werte = {"schaden": 10}
        self.assertIsNone(self.wende_ausbau_an(werte, {}))
        self.assertIsNone(self.wende_ausbau_an(werte, {"schaden": ("?", 5)}))

    def test_der_ersatz_laesst_die_werte_des_turms_wie_sie_waren(self):
        werte = {"schaden": 10, "reichweite": 120.0}
        self.wende_ausbau_an(werte, {"schaden": ("+", 5), "splitter": ("=", 3)})
        self.assertEqual(werte, {"schaden": 10, "reichweite": 120.0})


if __name__ == "__main__":
    unittest.main()
