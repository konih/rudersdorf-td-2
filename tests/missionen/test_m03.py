"""Mission 3 · Der kürzeste Weg: Für jede Zelle wird gezählt, wie viele Schritte es zum Ziel sind."""

from tests.missionen import helfer

# Eine Felswand mit einer einzigen Lücke unten. Das Ziel "Z" ist die Zelle (4, 2).
MAUER = """
    ..#..
    ..#..
    ..#.Z
    ..#..
    .....
"""
# So viele Schritte sind es von jeder Zelle bis zum Ziel. Links der Wand geht es nur
# durch die Lücke, darum sind die Zahlen dort so groß.
MAUER_ABSTAENDE = """
    10  9  #  3  2
     9  8  #  2  1
     8  7  #  1  0
     7  6  #  2  1
     6  5  4  3  2
"""

# Die Zelle oben links ist von Fels eingeschlossen. Das Ziel "Z" ist die Zelle (3, 1).
EINGESCHLOSSEN = """
    .#..~
    #..Z.
    .....
"""
EINGESCHLOSSEN_ABSTAENDE = """
    -  #  2  1  ~
    #  2  1  0  1
    4  3  2  1  2
"""

TIPP_BREITE = (
    "Die Suche geht in die Breite: erst alle Zellen mit Abstand 1, dann alle mit Abstand 2 "
    "und so weiter. Wer eine Zelle zuerst erreicht, legt ihren Abstand fest. "
    "Eine Zelle, die schon einen Abstand hat, wird nicht noch einmal besucht."
)
TIPP_MAUER = (
    "Der Weg führt nur über begehbare Zellen. Um die Wand herum ist er länger "
    "als die Luftlinie. Frag für jeden Nachbarn ist_begehbar."
)
TIPP_FEHLT = (
    "In die Abstandskarte kommen nur Zellen, die die Suche vom Ziel aus wirklich erreicht. "
    "Fels, Wasser, gesperrte Zellen und eingeschlossene Zellen bekommen keinen Eintrag."
)


class Mission03(helfer.Missionstest):
    def test_auf_freier_wiese_zaehlt_der_abstand_die_schritte_bis_zum_ziel(self):
        raster = helfer.raster_aus(
            """
            .....
            ...Z.
            .....
            .....
            .....
            """
        )
        ziel = (3, 1)
        erwartet = {}
        for zeile in range(5):
            for spalte in range(5):
                erwartet[(spalte, zeile)] = abs(spalte - 3) + abs(zeile - 1)
        self.pruefe_abstaende(
            self.werkstatt.abstandskarte(raster, ziel, set()),
            erwartet,
            f"abstandskarte(raster, {ziel}, set())",
            TIPP_BREITE,
        )

    def test_das_ziel_selbst_hat_den_abstand_null(self):
        raster = helfer.raster_aus(MAUER)
        bekommen = self.werkstatt.abstandskarte(raster, (4, 2), set())
        self.pruefe_abstaende(
            {(4, 2): bekommen.get((4, 2))} if isinstance(bekommen, dict) else bekommen,
            {(4, 2): 0},
            "abstandskarte(raster, (4, 2), set())",
            "Die Suche beginnt am Ziel. Trage es als Erstes mit dem Abstand 0 ein.",
        )

    def test_um_eine_felswand_mit_einer_luecke_fuehrt_nur_der_umweg(self):
        raster = helfer.raster_aus(MAUER)
        self.pruefe_abstaende(
            self.werkstatt.abstandskarte(raster, (4, 2), set()),
            helfer.abstaende_aus(MAUER_ABSTAENDE),
            "abstandskarte(raster, (4, 2), set())",
            TIPP_MAUER,
        )

    def test_eine_wand_aus_bauwerken_wirkt_genauso_wie_eine_felswand(self):
        raster = helfer.raster_aus(
            """
            .....
            .....
            ....Z
            .....
            .....
            """
        )
        gesperrt = {(2, 0), (2, 1), (2, 2), (2, 3)}
        self.pruefe_abstaende(
            self.werkstatt.abstandskarte(raster, (4, 2), gesperrt),
            helfer.abstaende_aus(MAUER_ABSTAENDE),
            f"abstandskarte(raster, (4, 2), {sorted(gesperrt)})",
            "Auch die Zellen in gesperrt sind zu. Gib gesperrt an ist_begehbar weiter.",
        )

    def test_eine_eingeschlossene_zelle_fehlt_in_der_abstandskarte(self):
        raster = helfer.raster_aus(EINGESCHLOSSEN)
        self.pruefe_abstaende(
            self.werkstatt.abstandskarte(raster, (3, 1), set()),
            helfer.abstaende_aus(EINGESCHLOSSEN_ABSTAENDE),
            "abstandskarte(raster, (3, 1), set())",
            TIPP_FEHLT,
        )

    def test_sumpf_huegel_und_orktor_zaehlen_wie_wiese_einen_schritt(self):
        raster = helfer.raster_aus("S%^.Z")
        self.pruefe_abstaende(
            self.werkstatt.abstandskarte(raster, (4, 0), set()),
            {(0, 0): 4, (1, 0): 3, (2, 0): 2, (3, 0): 1, (4, 0): 0},
            "abstandskarte(raster, (4, 0), set())",
            "Jeder Schritt auf eine begehbare Zelle zählt genau 1, egal welches Gelände.",
        )

    def test_abstandskarte_laesst_gesperrt_und_das_raster_wie_sie_waren(self):
        raster = helfer.raster_aus(MAUER)
        gesperrt = {(3, 3), (4, 4)}
        self.werkstatt.abstandskarte(raster, (4, 2), gesperrt)
        tipp = (
            "gesperrt und das Raster sind nur geliehen. Merke dir besuchte Zellen "
            "in deiner eigenen Abstandskarte, nicht in gesperrt."
        )
        aufruf = "abstandskarte(raster, (4, 2), gesperrt)"
        self.pruefe_unveraendert({(3, 3), (4, 4)}, gesperrt, "gesperrt", aufruf, tipp)
        self.pruefe_unveraendert(helfer.raster_aus(MAUER), raster, "das Raster", aufruf, tipp)
