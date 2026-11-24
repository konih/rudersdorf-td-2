"""Mission 5 · Nicht einmauern! Ein Bauwerk ist nur erlaubt, wenn alle Wege zum Dorf offen bleiben."""

from tests.missionen import helfer

# Eine freie Wiese mit einem Hügel "^". Orktor "S" ist die Zelle (0, 0), Dorftor "Z" die (4, 2).
FELD = """
    S....
    ..^..
    ....Z
"""

# Verschiedenes Gelände. Der Weg vom Orktor zum Dorftor führt über die Wiese unten.
GELAENDE = """
    S.#~D
    ..%..
    ....Z
"""

# Ein Fluss "~" mit einer Furt: Der Gang in Zeile 2 ist nur eine Zelle breit.
FURT = """
    S.~~~..
    ..~~~..
    .......
    ..~~~.Z
"""

# Eine Nische bei (2, 2): Rundherum ist Fels, hinein und hinaus geht es nur über (2, 3).
NISCHE = """
    S...Z
    .##..
    .#.#.
    .....
"""

# Zwei Orktore. Das untere Tor (0, 3) kommt nur über die Zelle (0, 2) hinaus.
ZWEI_TORE = """
    S....
    .....
    .#...
    S#..Z
"""

TIPP_GELAENDE = (
    "Gebaut wird nur auf Wiese und Hügel. Welche Zeichen das sind, steht in BEBAUBAR "
    "aus rudersdorf.daten. Prüfe das, bevor du nach dem Weg suchst."
)
TIPP_AUSSERHALB = (
    "Prüfe zuerst, ob die Zelle überhaupt auf der Karte liegt. Vorsicht: Eine negative Zahl "
    "ist für Python kein Fehler, raster[-1] ist die letzte Zeile."
)
TIPP_PROBE = (
    "Tu so, als stünde das Bauwerk schon da: Bilde eine neue Menge aus gesperrt und der "
    "Zelle, rechne damit die Abstandskarte aus und schau nach, wer darin noch vorkommt."
)
TIPP_ERLAUBT = (
    "Hier bleibt ein Weg offen. Verboten ist ein Bauwerk nur, wenn danach ein Orktor oder "
    "eine Zelle aus besetzt nicht mehr in der Abstandskarte steht."
)


def finde_dorftor(raster):
    """Sucht das "Z" auf der gezeichneten Karte (der Test hängt so nicht von Mission 1 ab)."""
    for zeile, inhalt in enumerate(raster):
        if "Z" in inhalt:
            return (inhalt.index("Z"), zeile)
    raise AssertionError("Auf der Karte des Tests fehlt das Dorftor Z.")


class Mission05(helfer.Missionstest):
    def pruefe_bauen(self, bild, zelle, erwartet, tipp, gesperrt=(), besetzt=(), starts=None):
        raster = helfer.raster_aus(bild)
        gesperrt = set(gesperrt)
        besetzt = set(besetzt)
        if starts is None:
            starts = [(0, 0)]
        ziel = finde_dorftor(raster)
        aufruf = (
            f"darf_bauen(raster, {zelle}, gesperrt={sorted(gesperrt)}, starts={starts}, "
            f"ziel={ziel}, besetzt={sorted(besetzt)})"
        )
        bekommen = self.rufe_sicher(
            aufruf, tipp, self.werkstatt.darf_bauen, raster, zelle, gesperrt, starts, ziel, besetzt
        )
        self.pruefe_gleich(bekommen, erwartet, aufruf, tipp)

    # ----- erlaubt -----

    def test_auf_einer_freien_wiese_abseits_des_weges_darf_gebaut_werden(self):
        self.pruefe_bauen(FELD, (0, 2), True, TIPP_ERLAUBT)

    def test_auf_einem_freien_huegel_darf_gebaut_werden(self):
        self.pruefe_bauen(FELD, (2, 1), True, TIPP_GELAENDE)

    def test_mitten_im_weg_darf_gebaut_werden_wenn_ein_anderer_weg_bleibt(self):
        self.pruefe_bauen(FELD, (1, 0), True, TIPP_ERLAUBT)
        self.pruefe_bauen(FELD, (4, 1), True, TIPP_ERLAUBT)

    # ----- verboten, weil die Zelle selbst nicht passt -----

    def test_auf_fels_wasser_sumpf_und_dorfgrund_darf_nicht_gebaut_werden(self):
        for zelle in [(2, 0), (3, 0), (2, 1), (4, 0)]:
            self.pruefe_bauen(GELAENDE, zelle, False, TIPP_GELAENDE)

    def test_auf_den_toren_darf_nicht_gebaut_werden(self):
        for zelle in [(0, 0), (4, 2)]:
            self.pruefe_bauen(GELAENDE, zelle, False, TIPP_GELAENDE)

    def test_wo_schon_ein_bauwerk_steht_darf_nicht_gebaut_werden(self):
        self.pruefe_bauen(
            FELD,
            (0, 2),
            False,
            "Steht die Zelle schon in gesperrt, ist dort bereits ein Bauwerk.",
            gesperrt=[(0, 2)],
        )

    def test_wo_gerade_ein_ork_steht_darf_nicht_gebaut_werden(self):
        self.pruefe_bauen(
            FELD,
            (0, 2),
            False,
            "In besetzt stehen die Zellen, auf denen gerade Orks sind. "
            "Niemand baut einem Ork einen Turm auf den Kopf.",
            besetzt=[(0, 2)],
        )

    def test_links_und_oberhalb_der_karte_darf_nicht_gebaut_werden(self):
        for zelle in [(-1, 1), (1, -1)]:
            self.pruefe_bauen(FELD, zelle, False, TIPP_AUSSERHALB)

    def test_rechts_und_unterhalb_der_karte_darf_nicht_gebaut_werden(self):
        for zelle in [(5, 1), (1, 3)]:
            self.pruefe_bauen(FELD, zelle, False, TIPP_AUSSERHALB)

    # ----- verboten, weil ein Weg verloren ginge -----

    def test_die_letzte_luecke_einer_mauer_darf_nicht_geschlossen_werden(self):
        # In Spalte 2 stehen schon zwei Bauwerke. Nur (2, 2) ist noch offen.
        self.pruefe_bauen(FELD, (2, 2), False, TIPP_PROBE, gesperrt=[(2, 0), (2, 1)])

    def test_neben_der_letzten_luecke_darf_weiter_gebaut_werden(self):
        self.pruefe_bauen(FELD, (3, 1), True, TIPP_ERLAUBT, gesperrt=[(2, 0), (2, 1)])

    def test_in_einer_furt_die_nur_eine_zelle_breit_ist_darf_nicht_gebaut_werden(self):
        for zelle in [(2, 2), (3, 2), (4, 2)]:
            self.pruefe_bauen(FURT, zelle, False, TIPP_PROBE)

    def test_vor_und_hinter_der_furt_darf_gebaut_werden(self):
        for zelle in [(1, 1), (5, 1)]:
            self.pruefe_bauen(FURT, zelle, True, TIPP_ERLAUBT)

    def test_ein_ork_in_der_nische_darf_nicht_eingesperrt_werden(self):
        self.pruefe_bauen(
            NISCHE,
            (2, 3),
            False,
            "Nicht nur die Orktore brauchen einen Weg. Auch jede Zelle in besetzt muss "
            "nach dem Bau noch in der Abstandskarte stehen, sonst steckt dort ein Ork fest.",
            besetzt=[(2, 2)],
        )

    def test_neben_dem_eingang_der_nische_darf_gebaut_werden(self):
        self.pruefe_bauen(NISCHE, (1, 3), True, TIPP_ERLAUBT, besetzt=[(2, 2)])

    def test_ist_die_nische_leer_darf_ihr_eingang_zugebaut_werden(self):
        self.pruefe_bauen(NISCHE, (2, 3), True, TIPP_ERLAUBT)

    def test_bei_zwei_toren_darf_das_zweite_tor_nicht_abgeschnitten_werden(self):
        self.pruefe_bauen(
            ZWEI_TORE,
            (0, 2),
            False,
            "Es gibt mehr als ein Orktor. Geh alle Zellen in starts durch, nicht nur die erste.",
            starts=[(0, 0), (0, 3)],
        )

    def test_bei_zwei_toren_darf_das_erste_tor_nicht_abgeschnitten_werden(self):
        self.pruefe_bauen(
            ZWEI_TORE,
            (0, 2),
            False,
            "Es gibt mehr als ein Orktor. Geh alle Zellen in starts durch, nicht nur die letzte.",
            starts=[(0, 3), (0, 0)],
        )

    def test_bei_zwei_toren_darf_gebaut_werden_wenn_beide_ihren_weg_behalten(self):
        self.pruefe_bauen(ZWEI_TORE, (2, 2), True, TIPP_ERLAUBT, starts=[(0, 0), (0, 3)])

    # ----- nichts verändern -----

    def test_darf_bauen_laesst_alles_wie_es_war(self):
        tipp = (
            "gesperrt, besetzt, starts und das Raster sind nur geliehen. Für die Probe "
            "brauchst du eine neue Menge. Wer die Zelle in gesperrt selbst einträgt, "
            "hat das Bauwerk schon gebaut, obwohl nur gefragt wurde."
        )
        # Einmal mit der Antwort "ja" und einmal mit der Antwort "nein".
        for zelle in [(3, 1), (2, 2)]:
            raster = helfer.raster_aus(FELD)
            gesperrt = {(2, 0), (2, 1)}
            besetzt = {(1, 1)}
            starts = [(0, 0)]
            self.werkstatt.darf_bauen(raster, zelle, gesperrt, starts, (4, 2), besetzt)
            aufruf = f"darf_bauen(raster, {zelle}, gesperrt, starts, (4, 2), besetzt)"
            self.pruefe_unveraendert({(2, 0), (2, 1)}, gesperrt, "gesperrt", aufruf, tipp)
            self.pruefe_unveraendert({(1, 1)}, besetzt, "besetzt", aufruf, tipp)
            self.pruefe_unveraendert([(0, 0)], starts, "starts", aufruf, tipp)
            self.pruefe_unveraendert(helfer.raster_aus(FELD), raster, "das Raster", aufruf, tipp)
