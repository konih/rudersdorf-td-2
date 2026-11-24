"""Mission 9 · Der Kettenblitz: Der Blitz springt von Gegner zu Gegner, immer zum nächsten."""

from tests.missionen import helfer
from tests.missionen.helfer import TestGegner

TIPP_KETTE = (
    "Der Blitz springt immer von dem Gegner weiter, den er zuletzt getroffen hat. "
    "Miss den Abstand also vom letzten in deiner Liste, nicht vom Start."
)
TIPP_NAECHSTER = (
    "Von allen, die noch nicht getroffen sind und nah genug stehen, trifft der Blitz den "
    "mit dem kleinsten Abstand zum zuletzt Getroffenen."
)
TIPP_NICHT_ZWEIMAL = (
    "Wer schon in der Trefferliste steht, wird übersprungen. So springt der Blitz nie zurück."
)
TIPP_WEITE = (
    'Ein Sprung reicht höchstens so weit wie sprungweite. "Höchstens" heißt: Genau so weit '
    "ist noch erlaubt, weiter nicht. Findet der Blitz niemanden, ist die Kette zu Ende."
)
TIPP_SPRUENGE = (
    "spruenge sagt, wie oft der Blitz höchstens weiterspringt. Der Start zählt nicht als "
    "Sprung: Bei 3 Sprüngen stehen am Ende höchstens 4 Gegner in der Liste."
)


def reihe(anzahl, abstand=50.0):
    """Gegner in einer Reihe nebeneinander, der erste auf (100, 100), jeder ``abstand`` weiter rechts."""
    return [TestGegner(x=100.0 + abstand * nummer, y=100.0) for nummer in range(anzahl)]


class Mission09(helfer.Missionstest):
    modul = "tuerme"

    def pruefe_kette(self, start, gegner, spruenge, sprungweite, erwartet, tipp):
        self.pruefe_gleich(
            self.werkstatt.kettenblitz(start, gegner, spruenge, sprungweite),
            erwartet,
            f"kettenblitz({start}, {gegner}, {spruenge}, {sprungweite})",
            tipp,
        )

    # --- die Kette folgt der Reihe ----------------------------------------------------------

    def test_der_blitz_folgt_der_reihe_von_gegner_zu_gegner(self):
        g = reihe(8)
        self.pruefe_kette(g[0], g, 5, 60.0, [g[0], g[1], g[2], g[3], g[4], g[5]], TIPP_KETTE)

    def test_mit_einem_sprung_trifft_der_blitz_den_start_und_einen_weiteren(self):
        g = reihe(6)
        self.pruefe_kette(g[0], g, 1, 60.0, [g[0], g[1]], TIPP_SPRUENGE)

    def test_ohne_spruenge_trifft_der_blitz_nur_den_start(self):
        g = reihe(6)
        self.pruefe_kette(g[0], g, 0, 60.0, [g[0]], TIPP_SPRUENGE)

    def test_sind_mehr_spruenge_erlaubt_als_gegner_da_sind_endet_die_kette_frueher(self):
        g = reihe(4)
        self.pruefe_kette(g[0], g, 10, 60.0, [g[0], g[1], g[2], g[3]], TIPP_NICHT_ZWEIMAL)

    def test_eine_zu_grosse_luecke_beendet_die_kette(self):
        g = reihe(3)
        hinter_der_luecke = TestGegner(x=300.0, y=100.0)  # 100 vom letzten der Reihe entfernt
        self.pruefe_kette(g[0], [*g, hinter_der_luecke], 5, 60.0, [g[0], g[1], g[2]], TIPP_WEITE)

    def test_ein_sprung_genau_so_weit_wie_die_sprungweite_gelingt_noch(self):
        g = reihe(3)
        self.pruefe_kette(g[0], g, 2, 50.0, [g[0], g[1], g[2]], TIPP_WEITE)

    def test_ein_sprung_knapp_ueber_der_sprungweite_gelingt_nicht(self):
        g = reihe(3)
        self.pruefe_kette(g[0], g, 2, 49.0, [g[0]], TIPP_WEITE)

    def test_ohne_andere_gegner_trifft_der_blitz_nur_den_start(self):
        start = TestGegner(x=100.0, y=100.0)
        self.pruefe_kette(start, [start], 3, 60.0, [start], TIPP_NICHT_ZWEIMAL)

    # --- niemand wird zweimal getroffen -----------------------------------------------------

    def test_zwischen_zwei_gegnern_springt_der_blitz_nicht_hin_und_her(self):
        g = reihe(2)
        self.pruefe_kette(g[0], g, 3, 60.0, [g[0], g[1]], TIPP_NICHT_ZWEIMAL)

    def test_der_start_wird_auch_dann_nur_einmal_getroffen_wenn_er_weiter_hinten_steht(self):
        g = reihe(3)
        # Der Start ist der letzte der Liste. Von ihm aus geht es nach links zurück.
        self.pruefe_kette(g[2], g, 5, 60.0, [g[2], g[1], g[0]], TIPP_NICHT_ZWEIMAL)

    def test_der_start_steht_vorn_auch_wenn_er_in_der_liste_der_gegner_fehlt(self):
        start = TestGegner(x=100.0, y=100.0)
        andere = [TestGegner(x=150.0, y=100.0), TestGegner(x=200.0, y=100.0)]
        self.pruefe_kette(
            start,
            andere,
            2,
            60.0,
            [start, andere[0], andere[1]],
            "Die Trefferliste beginnt immer mit dem Start: treffer = [start].",
        )

    # --- der nächste gewinnt -----------------------------------------------------------------

    def test_der_blitz_springt_zum_naechsten_und_nicht_zum_ersten_der_liste(self):
        start = TestGegner(x=100.0, y=100.0)
        weiter = TestGegner(x=150.0, y=100.0)
        naeher = TestGegner(x=130.0, y=100.0)
        self.pruefe_kette(start, [start, weiter, naeher], 1, 60.0, [start, naeher], TIPP_NAECHSTER)

    def test_nach_dem_naeheren_trifft_der_naechste_sprung_den_anderen(self):
        start = TestGegner(x=100.0, y=100.0)
        weiter = TestGegner(x=150.0, y=100.0)
        naeher = TestGegner(x=130.0, y=100.0)
        self.pruefe_kette(
            start, [start, weiter, naeher], 2, 60.0, [start, naeher, weiter], TIPP_NAECHSTER
        )

    def test_bei_zwei_gleich_nahen_gegnern_gewinnt_der_fruehere_in_der_liste(self):
        g = reihe(5)
        # Vom mittleren Gegner sind der linke und der rechte Nachbar gleich weit weg.
        # Der linke steht früher in der Liste. Danach geht es links weiter bis zum Ende;
        # von dort ist der rechte Nachbar des Starts schon zu weit weg.
        self.pruefe_kette(
            g[2],
            g,
            4,
            60.0,
            [g[2], g[1], g[0]],
            "Bei Gleichstand gewinnt, wer weiter vorn in der Liste gegner steht. Ein neuer "
            "Gegner verdrängt den bisher nächsten nur, wenn er wirklich näher ist. " + TIPP_KETTE,
        )

    def test_die_sprungweite_ist_ein_kreis_um_den_zuletzt_getroffenen(self):
        start = TestGegner(x=100.0, y=100.0)
        schraeg = TestGegner(x=140.0, y=140.0)  # 40 nach rechts, 40 nach unten: etwa 56,6
        zu_weit = TestGegner(x=190.0, y=190.0)  # von schraeg aus 50 und 50: etwa 70,7
        self.pruefe_kette(
            start,
            [start, zu_weit, schraeg],
            3,
            60.0,
            [start, schraeg],
            "Der Abstand ist die gerade Linie zwischen zwei Gegnern, wie in Mission 6: "
            "Satz des Pythagoras oder math.hypot.",
        )

    # --- Besiegte ----------------------------------------------------------------------------

    def test_ein_besiegter_gegner_wird_uebersprungen(self):
        start = TestGegner(x=100.0, y=100.0)
        besiegt = TestGegner(leben=0, x=120.0, y=100.0)
        lebendig = TestGegner(x=150.0, y=100.0)
        self.pruefe_kette(
            start,
            [start, besiegt, lebendig],
            2,
            60.0,
            [start, lebendig],
            "Der Blitz trifft nur lebende Gegner: solche, deren leben größer als 0 ist.",
        )

    def test_ueber_einen_besiegten_hinweg_reicht_die_kette_nicht_weiter(self):
        g = reihe(4)
        g[1].leben = 0
        # Der zweite der Reihe ist besiegt. Der dritte ist vom Start 100 entfernt: zu weit.
        self.pruefe_kette(
            g[0],
            g,
            3,
            60.0,
            [g[0]],
            "Ein Besiegter leitet den Blitz nicht weiter. Er kommt gar nicht erst in die "
            "Trefferliste.",
        )

    # --- nichts verändern --------------------------------------------------------------------

    def test_kettenblitz_laesst_die_liste_der_gegner_wie_sie_war(self):
        g = reihe(5)
        vorher = list(g)
        self.werkstatt.kettenblitz(g[0], g, 3, 60.0)
        self.pruefe_unveraendert(
            vorher,
            g,
            "die Liste gegner",
            "kettenblitz(start, gegner, 3, 60.0)",
            "Nimm getroffene Gegner nicht aus gegner heraus. Merke dir in deiner eigenen "
            "Trefferliste, wer schon getroffen ist.",
        )

    def test_kettenblitz_teilt_selbst_keinen_schaden_aus(self):
        g = reihe(4)
        self.werkstatt.kettenblitz(g[0], g, 3, 60.0)
        schaeden = [gegner.schaeden for gegner in g]
        if schaeden != [[], [], [], []]:
            self.fail(
                helfer.meldung(
                    "kettenblitz(start, gegner, 3, 60.0) verletzt selbst niemanden",
                    f"die vier Gegner haben diese Schäden erlitten: {schaeden}",
                    "Die Funktion sagt nur, wen der Blitz der Reihe nach trifft. Den Schaden "
                    "teilt das Spiel danach selbst aus.",
                )
            )
