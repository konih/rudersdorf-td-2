"""Mission 6 · Wer ist in Reichweite? Ein Turm sucht die lebenden Gegner, die nah genug sind."""

from tests.missionen import helfer
from tests.missionen.helfer import TestGegner

# Der Turm steht in allen Tests auf diesem Punkt und sieht 50 Pixel weit.
TURM = (100.0, 100.0)
WEITE = 50.0

TIPP_ABSTAND = (
    "Der Abstand ist die gerade Linie vom Turm zum Gegner. Zieh erst x von x und y von y ab, "
    "dann hilft der Satz des Pythagoras (oder math.hypot)."
)
TIPP_RAND = (
    'In Reichweite heißt "höchstens so weit". Ein Gegner, der genau so weit weg ist wie die '
    "Reichweite, gehört noch dazu. Schau dir dein Vergleichszeichen an."
)
TIPP_LEBEN = "Ein Gegner lebt, solange sein leben größer als 0 ist. Auf Besiegte schießt kein Turm."
TIPP_NEUE_LISTE = (
    "Fang mit einer leeren Liste an und häng jeden passenden Gegner an. "
    "Die Liste gegner selbst ist nur geliehen."
)


class Mission06(helfer.Missionstest):
    modul = "tuerme"

    def pruefe_reichweite(self, gegner, erwartet, tipp):
        self.pruefe_gleich(
            self.werkstatt.in_reichweite(TURM, WEITE, gegner),
            erwartet,
            f"in_reichweite({TURM}, {WEITE}, {gegner})",
            tipp,
        )

    def test_ein_gegner_nah_am_turm_ist_in_reichweite(self):
        nah = TestGegner(x=130.0, y=100.0)
        self.pruefe_reichweite([nah], [nah], TIPP_ABSTAND)

    def test_ein_gegner_genau_am_rand_der_reichweite_gehoert_noch_dazu(self):
        rechts = TestGegner(x=150.0, y=100.0)
        schraeg = TestGegner(x=140.0, y=130.0)  # 40 nach rechts, 30 nach unten: genau 50
        self.pruefe_reichweite([rechts, schraeg], [rechts, schraeg], TIPP_RAND)

    def test_ein_gegner_knapp_hinter_dem_rand_ist_nicht_in_reichweite(self):
        self.pruefe_reichweite([TestGegner(x=151.0, y=100.0)], [], TIPP_RAND)

    def test_weit_entfernte_gegner_sind_in_keiner_richtung_in_reichweite(self):
        fern = [
            TestGegner(x=300.0, y=100.0),  # rechts
            TestGegner(x=0.0, y=100.0),  # links
            TestGegner(x=100.0, y=0.0),  # oben
            TestGegner(x=100.0, y=300.0),  # unten
        ]
        self.pruefe_reichweite(
            fern,
            [],
            "Ein Gegner links oder oberhalb des Turms ergibt beim Abziehen eine negative Zahl. "
            "Auch er kann weit weg sein. " + TIPP_ABSTAND,
        )

    def test_die_reichweite_ist_ein_kreis_und_kein_quadrat(self):
        # 40 nach rechts und 40 nach unten: Das sind etwa 56,6 Pixel, also zu weit.
        ecke = TestGegner(x=140.0, y=140.0)
        self.pruefe_reichweite([ecke], [], TIPP_ABSTAND)

    def test_ein_schraeg_stehender_gegner_im_kreis_ist_in_reichweite(self):
        # 30 nach links und 30 nach oben: Das sind etwa 42,4 Pixel, also nah genug.
        schraeg = TestGegner(x=70.0, y=70.0)
        self.pruefe_reichweite([schraeg], [schraeg], TIPP_ABSTAND)

    def test_der_abstand_wird_vom_turm_aus_gemessen_nicht_von_der_ecke_der_karte(self):
        # Dieser Gegner steht nah an der Kartenecke (0, 0), aber weit weg vom Turm.
        an_der_ecke = TestGegner(x=10.0, y=10.0)
        self.pruefe_reichweite(
            [an_der_ecke],
            [],
            "Der Turm steht auf position. Miss von dort: x des Gegners minus x des Turms, "
            "y des Gegners minus y des Turms.",
        )

    def test_ein_besiegter_gegner_in_reichweite_wird_nicht_mehr_gesehen(self):
        besiegt = TestGegner(leben=0, x=110.0, y=100.0)
        lebendig = TestGegner(leben=1, x=120.0, y=100.0)
        self.pruefe_reichweite([besiegt, lebendig], [lebendig], TIPP_LEBEN)

    def test_drinnen_am_rand_draussen_und_besiegt_zusammen(self):
        drinnen = TestGegner(x=130.0, y=100.0)
        am_rand = TestGegner(x=100.0, y=150.0)
        draussen = TestGegner(x=100.0, y=151.0)
        besiegt = TestGegner(leben=0, x=100.0, y=90.0)
        self.pruefe_reichweite(
            [draussen, am_rand, besiegt, drinnen],
            [am_rand, drinnen],
            "Zwei Fragen für jeden Gegner: Lebt er? Ist er höchstens so weit weg wie die "
            "Reichweite? Nur wer beide Male Ja bekommt, kommt in die Liste.",
        )

    def test_die_gegner_bleiben_in_der_reihenfolge_der_liste(self):
        weit = TestGegner(x=145.0, y=100.0)
        nah = TestGegner(x=105.0, y=100.0)
        mittel = TestGegner(x=100.0, y=75.0)
        self.pruefe_reichweite(
            [weit, nah, mittel],
            [weit, nah, mittel],
            "Sortiere nicht. Geh die Liste von vorn nach hinten durch und behalte die Reihenfolge.",
        )

    def test_ohne_gegner_ist_das_ergebnis_eine_leere_liste(self):
        self.pruefe_reichweite(
            [], [], "Auch wenn niemand da ist, kommt eine Liste zurück, nur eben eine leere."
        )

    def test_ist_niemand_nah_genug_ist_das_ergebnis_eine_leere_liste(self):
        self.pruefe_reichweite(
            [TestGegner(x=400.0, y=400.0)],
            [],
            "Auch wenn niemand nah genug ist, kommt eine Liste zurück, nur eben eine leere.",
        )

    def test_das_ergebnis_ist_eine_neue_liste_auch_wenn_alle_in_reichweite_sind(self):
        gegner = [TestGegner(x=110.0, y=100.0), TestGegner(x=100.0, y=110.0)]
        bekommen = self.werkstatt.in_reichweite(TURM, WEITE, gegner)
        aufruf = f"in_reichweite({TURM}, {WEITE}, gegner)"
        self.pruefe_gleich(bekommen, list(gegner), aufruf, TIPP_ABSTAND)
        if bekommen is gegner:
            self.fail(
                helfer.meldung(
                    f"{aufruf} ergibt eine neue Liste",
                    "genau die Liste gegner, die hineingegeben wurde",
                    TIPP_NEUE_LISTE,
                )
            )

    def test_in_reichweite_laesst_die_liste_der_gegner_wie_sie_war(self):
        drinnen = TestGegner(x=130.0, y=100.0)
        draussen = TestGegner(x=300.0, y=100.0)
        besiegt = TestGegner(leben=0, x=100.0, y=90.0)
        zweiter = TestGegner(x=100.0, y=120.0)
        gegner = [draussen, besiegt, drinnen, zweiter]
        self.werkstatt.in_reichweite(TURM, WEITE, gegner)
        self.pruefe_unveraendert(
            [draussen, besiegt, drinnen, zweiter],
            gegner,
            "die Liste gegner",
            f"in_reichweite({TURM}, {WEITE}, gegner)",
            "Nimm nichts aus gegner heraus. " + TIPP_NEUE_LISTE,
        )
