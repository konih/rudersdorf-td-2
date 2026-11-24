"""Mission 7 · Zielstrategien: Fünf Regeln, nach denen ein Turm sein Ziel aussucht."""

from tests.missionen import helfer
from tests.missionen.helfer import TestGegner, TestTurm

NAMEN = ["erster", "letzter", "staerkster", "schwaechster", "naechster"]

TIPPS = {
    "erster": (
        "rest_weg sagt, wie weit ein Gegner noch bis zum Dorftor laufen muss. "
        "Der Erste ist der mit dem kleinsten rest_weg."
    ),
    "letzter": (
        "rest_weg sagt, wie weit ein Gegner noch bis zum Dorftor laufen muss. "
        "Der Letzte ist der mit dem größten rest_weg."
    ),
    "staerkster": "Der Stärkste ist der Gegner mit dem meisten leben.",
    "schwaechster": "Der Schwächste ist der Gegner mit dem wenigsten leben.",
    "naechster": (
        "Der Nächste ist der Gegner mit dem kleinsten Abstand zum Turm. Der Abstand ist die "
        "gerade Linie von (turm.x, turm.y) zu (gegner.x, gegner.y), wie in Mission 6."
    ),
}
TIPP_GLEICHSTAND = (
    "Bei Gleichstand gewinnt, wer weiter vorn in der Liste steht. Ein neuer Kandidat "
    "verdrängt den bisher besten nur, wenn er wirklich besser ist, nicht wenn er gleich gut ist."
)
TIPP_LEER = (
    "Ist die Liste leer, gibt es niemanden auszusuchen. Prüfe das als Erstes und gib dann "
    "None zurück. (min und max stürzen bei einer leeren Liste ab.)"
)


def gemischte_kandidaten():
    """Sieben Gegner. Jede der fünf Strategien sucht sich einen anderen aus.

    Der erste und der letzte in der Liste sind bei keiner Strategie die richtige Antwort.
    Der Turm dazu steht auf (200, 200).
    """
    return {
        "vorn_in_der_liste": TestGegner(leben=40, x=350.0, y=350.0, rest_weg=250.0),
        "erster": TestGegner(leben=50, x=400.0, y=200.0, rest_weg=100.0),
        "letzter": TestGegner(leben=30, x=300.0, y=200.0, rest_weg=500.0),
        "staerkster": TestGegner(leben=90, x=200.0, y=500.0, rest_weg=300.0),
        "schwaechster": TestGegner(leben=10, x=500.0, y=500.0, rest_weg=200.0),
        "naechster": TestGegner(leben=60, x=220.0, y=200.0, rest_weg=400.0),
        "hinten_in_der_liste": TestGegner(leben=45, x=200.0, y=380.0, rest_weg=350.0),
    }


class Mission07(helfer.Missionstest):
    modul = "strategien"

    def setUp(self):
        super().setUp()
        self.turm = TestTurm(x=200.0, y=200.0)

    def waehle(self, name, kandidaten, tipp):
        """Ruft die Strategie ``name`` auf. Ein Absturz wird zu einer Meldung mit Tipp."""
        return self.rufe_sicher(
            f"{name}({kandidaten}, {self.turm})",
            tipp,
            getattr(self.werkstatt, name),
            kandidaten,
            self.turm,
        )

    def pruefe_wahl(self, name, kandidaten, erwartet, tipp):
        self.pruefe_gleich(
            self.waehle(name, kandidaten, tipp),
            erwartet,
            f"{name}({kandidaten}, {self.turm})",
            tipp,
        )

    def pruefe_gemischt(self, name):
        gegner = gemischte_kandidaten()
        self.pruefe_wahl(name, list(gegner.values()), gegner[name], TIPPS[name])

    # --- jede Strategie sucht den Richtigen aus -------------------------------------------

    def test_erster_waehlt_den_gegner_mit_dem_kleinsten_rest_weg(self):
        self.pruefe_gemischt("erster")

    def test_letzter_waehlt_den_gegner_mit_dem_groessten_rest_weg(self):
        self.pruefe_gemischt("letzter")

    def test_staerkster_waehlt_den_gegner_mit_dem_meisten_leben(self):
        self.pruefe_gemischt("staerkster")

    def test_schwaechster_waehlt_den_gegner_mit_dem_wenigsten_leben(self):
        self.pruefe_gemischt("schwaechster")

    def test_naechster_waehlt_den_gegner_mit_dem_kleinsten_abstand_zum_turm(self):
        self.pruefe_gemischt("naechster")

    def test_staerkster_und_schwaechster_zaehlen_das_leben_von_jetzt_nicht_das_volle_leben(self):
        tipp = (
            "leben ist das Leben, das ein Gegner in diesem Augenblick hat. max_leben ist sein "
            "volles Leben vom Anfang. Für die Strategie zählt leben."
        )
        verwundeter_riese = TestGegner(leben=30, max_leben=300)
        gesunder_ork = TestGegner(leben=60, max_leben=60)
        self.pruefe_wahl("staerkster", [verwundeter_riese, gesunder_ork], gesunder_ork, tipp)
        self.pruefe_wahl("schwaechster", [gesunder_ork, verwundeter_riese], verwundeter_riese, tipp)

    # --- der Abstand zum Turm --------------------------------------------------------------

    def test_naechster_misst_vom_turm_aus_und_nicht_von_der_ecke_der_karte(self):
        an_der_ecke = TestGegner(x=50.0, y=50.0)  # nah an (0, 0), aber weit weg vom Turm
        am_turm = TestGegner(x=260.0, y=200.0)
        self.pruefe_wahl(
            "naechster",
            [an_der_ecke, am_turm],
            am_turm,
            "Miss vom Turm aus: gegner.x minus turm.x und gegner.y minus turm.y.",
        )

    def test_naechster_beachtet_auch_den_abstand_nach_oben_und_unten(self):
        weit_unten = TestGegner(x=210.0, y=400.0)  # fast dieselbe Spalte, aber 200 tiefer
        daneben = TestGegner(x=260.0, y=200.0)
        self.pruefe_wahl("naechster", [weit_unten, daneben], daneben, TIPPS["naechster"])

    def test_naechster_misst_die_gerade_linie_und_zaehlt_nicht_x_und_y_zusammen(self):
        gerade = TestGegner(x=290.0, y=200.0)  # 90 nach rechts: Abstand 90
        schraeg = TestGegner(x=260.0, y=260.0)  # 60 nach rechts, 60 nach unten: etwa 84,9
        self.pruefe_wahl(
            "naechster",
            [gerade, schraeg],
            schraeg,
            "Schräg ist kürzer als außen herum. Der Abstand kommt aus dem Satz des Pythagoras "
            "(oder math.hypot), nicht aus dx + dy.",
        )

    # --- Gleichstand -----------------------------------------------------------------------

    def test_bei_gleichem_rest_weg_gewinnt_bei_erster_der_fruehere_in_der_liste(self):
        anderer = TestGegner(rest_weg=300.0)
        frueher = TestGegner(rest_weg=100.0)
        spaeter = TestGegner(rest_weg=100.0)
        self.pruefe_wahl("erster", [anderer, frueher, spaeter], frueher, TIPP_GLEICHSTAND)

    def test_bei_gleichem_rest_weg_gewinnt_bei_letzter_der_fruehere_in_der_liste(self):
        anderer = TestGegner(rest_weg=100.0)
        frueher = TestGegner(rest_weg=300.0)
        spaeter = TestGegner(rest_weg=300.0)
        self.pruefe_wahl("letzter", [anderer, frueher, spaeter], frueher, TIPP_GLEICHSTAND)

    def test_bei_gleichem_leben_gewinnt_bei_staerkster_der_fruehere_in_der_liste(self):
        anderer = TestGegner(leben=20)
        frueher = TestGegner(leben=80)
        spaeter = TestGegner(leben=80)
        self.pruefe_wahl("staerkster", [anderer, frueher, spaeter], frueher, TIPP_GLEICHSTAND)

    def test_bei_gleichem_leben_gewinnt_bei_schwaechster_der_fruehere_in_der_liste(self):
        anderer = TestGegner(leben=80)
        frueher = TestGegner(leben=20)
        spaeter = TestGegner(leben=20)
        self.pruefe_wahl("schwaechster", [anderer, frueher, spaeter], frueher, TIPP_GLEICHSTAND)

    def test_bei_gleichem_abstand_gewinnt_bei_naechster_der_fruehere_in_der_liste(self):
        anderer = TestGegner(x=500.0, y=500.0)
        frueher = TestGegner(x=260.0, y=200.0)  # 60 rechts vom Turm
        spaeter = TestGegner(x=200.0, y=140.0)  # 60 über dem Turm
        self.pruefe_wahl("naechster", [anderer, frueher, spaeter], frueher, TIPP_GLEICHSTAND)

    # --- kleine Listen ---------------------------------------------------------------------

    def test_aus_einer_leeren_liste_waehlt_jede_strategie_none(self):
        for name in NAMEN:
            self.pruefe_wahl(name, [], None, TIPP_LEER)

    def test_ist_nur_ein_gegner_da_waehlt_jede_strategie_ihn(self):
        for name in NAMEN:
            einziger = TestGegner(leben=25, x=300.0, y=300.0, rest_weg=120.0)
            self.pruefe_wahl(
                name,
                [einziger],
                einziger,
                "Das Ergebnis ist immer einer der Kandidaten selbst, nicht seine Nummer in der "
                "Liste und nicht sein Wert.",
            )

    def test_jede_strategie_laesst_die_liste_der_kandidaten_wie_sie_war(self):
        for name in NAMEN:
            kandidaten = list(gemischte_kandidaten().values())
            vorher = list(kandidaten)
            self.waehle(name, kandidaten, TIPPS[name])
            self.pruefe_unveraendert(
                vorher,
                kandidaten,
                "die Liste kandidaten",
                f"{name}(kandidaten, turm)",
                "Die Liste ist nur geliehen. kandidaten.sort() sortiert sie um; "
                "such lieber mit einer Schleife (oder mit min und max) den Richtigen heraus.",
            )

    # --- das Wörterbuch STRATEGIEN ---------------------------------------------------------

    def test_strategien_verbindet_die_fuenf_namen_mit_ihren_funktionen(self):
        tabelle = getattr(self.werkstatt, "STRATEGIEN", None)
        tipp = (
            "STRATEGIEN ist ein Wörterbuch: links der Name als Text, rechts die Funktion "
            'ohne Klammern, zum Beispiel "erster": erster.'
        )
        if not isinstance(tabelle, dict):
            self.fail(helfer.meldung("STRATEGIEN ist ein Wörterbuch (dict)", repr(tabelle), tipp))
        for name in NAMEN:
            if name not in tabelle:
                self.fail(
                    helfer.meldung(
                        f"STRATEGIEN hat den Schlüssel {name!r}",
                        f"die Schlüssel {sorted(tabelle, key=repr)}",
                        tipp,
                    )
                )
            if tabelle[name] is not getattr(self.werkstatt, name):
                self.fail(
                    helfer.meldung(
                        f"STRATEGIEN[{name!r}] ist die Funktion {name}",
                        repr(tabelle[name]),
                        tipp,
                    )
                )
        # Und über das Wörterbuch aufgerufen, sucht jede Regel denselben Gegner aus wie direkt.
        for name in NAMEN:
            gegner = gemischte_kandidaten()
            kandidaten = list(gegner.values())
            self.pruefe_gleich(
                self.rufe_sicher(
                    f"STRATEGIEN[{name!r}](kandidaten, turm)",
                    TIPPS[name],
                    lambda regel=name, liste=kandidaten: tabelle[regel](liste, self.turm),
                ),
                gegner[name],
                f"STRATEGIEN[{name!r}]({kandidaten}, {self.turm})",
                TIPPS[name],
            )
