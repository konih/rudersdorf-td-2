"""Mission 4 · Dem Weg folgen: Von einer Zelle geht es zu dem Nachbarn, der näher am Ziel liegt."""

from tests.missionen import helfer

# Die Abstandskarte einer Karte mit 5 Spalten und 5 Zeilen. In Spalte 2 steht eine Felswand
# ("#", ohne Abstand) mit einer Lücke unten. Das Ziel ist die Zelle (4, 2) mit dem Abstand 0.
ABSTAENDE = """
    10  9  #  3  2
     9  8  #  2  1
     8  7  #  1  0
     7  6  #  2  1
     6  5  4  3  2
"""
BREITE = 5
HOEHE = 5

TIPP_KLEINER = (
    "Schau dir die Abstände aller Nachbarn an und nimm den kleinsten. "
    "Er muss kleiner sein als der Abstand der eigenen Zelle."
)
TIPP_GLEICHSTAND = (
    "Haben zwei Nachbarn denselben kleinsten Abstand, gewinnt der, der in der Reihenfolge "
    "oben, rechts, unten, links zuerst kommt. Ersetze den besten Nachbarn nur, "
    "wenn ein neuer wirklich kleiner ist."
)
TIPP_OHNE_ABSTAND = (
    "Ein Nachbar, der nicht in der Abstandskarte steht, ist Fels oder versperrt. "
    "Er kommt als Schritt nicht in Frage."
)


class Mission04(helfer.Missionstest):
    def pruefe_schritt(self, abstaende, zelle, breite, hoehe, erwartet, tipp):
        aufruf = f"naechster_schritt(abstaende, {zelle}, {breite}, {hoehe})"
        bekommen = self.rufe_sicher(
            aufruf, tipp, self.werkstatt.naechster_schritt, abstaende, zelle, breite, hoehe
        )
        self.pruefe_gleich(bekommen, erwartet, aufruf, tipp)

    def test_der_schritt_geht_zum_nachbarn_mit_dem_kleineren_abstand(self):
        abstaende = helfer.abstaende_aus(ABSTAENDE)
        # (1, 4) hat Abstand 5. Oben 6, rechts 4, links 6: Es geht nach rechts in die Lücke.
        self.pruefe_schritt(abstaende, (1, 4), BREITE, HOEHE, (2, 4), TIPP_KLEINER)
        # (4, 4) hat Abstand 2. Oben 1, links 3: Es geht nach oben.
        self.pruefe_schritt(abstaende, (4, 4), BREITE, HOEHE, (4, 3), TIPP_KLEINER)

    def test_von_mehreren_kleineren_nachbarn_gewinnt_der_kleinste(self):
        # Eine ausgedachte Abstandskarte: (1, 1) hat Abstand 5. Oben 4, rechts 2, unten 3, links 6.
        abstaende = helfer.abstaende_aus(
            """
            -  4  -
            6  5  2
            -  3  -
            """
        )
        self.pruefe_schritt(abstaende, (1, 1), 3, 3, (2, 1), TIPP_KLEINER)

    def test_bei_gleichstand_gewinnt_rechts_vor_unten(self):
        abstaende = helfer.abstaende_aus(ABSTAENDE)
        # (0, 0) hat Abstand 10. Rechts 9 und unten 9.
        self.pruefe_schritt(abstaende, (0, 0), BREITE, HOEHE, (1, 0), TIPP_GLEICHSTAND)

    def test_bei_gleichstand_gewinnt_oben_vor_rechts(self):
        abstaende = helfer.abstaende_aus(ABSTAENDE)
        # (3, 3) hat Abstand 2. Oben 1 und rechts 1.
        self.pruefe_schritt(abstaende, (3, 3), BREITE, HOEHE, (3, 2), TIPP_GLEICHSTAND)

    def test_bei_gleichstand_gewinnt_unten_vor_links(self):
        abstaende = helfer.abstaende_aus(
            """
            1  2
            0  1
            """
        )
        # (1, 0) hat Abstand 2. Unten 1 und links 1.
        self.pruefe_schritt(abstaende, (1, 0), 2, 2, (1, 1), TIPP_GLEICHSTAND)

    def test_ein_nachbar_ohne_abstand_wird_nie_betreten(self):
        abstaende = helfer.abstaende_aus(ABSTAENDE)
        # (1, 2) hat Abstand 7 und liegt direkt an der Wand. Oben 8, rechts Fels, unten 6, links 8.
        self.pruefe_schritt(abstaende, (1, 2), BREITE, HOEHE, (1, 3), TIPP_OHNE_ABSTAND)

    def test_ein_nachbar_ausserhalb_der_karte_wird_nie_betreten(self):
        # Die Abstandskarte gehört zu einer breiteren Karte, gefragt wird aber für eine Karte
        # mit nur 2 Spalten. (1, 0) hat Abstand 2. Rechts läge (2, 0) mit Abstand 1, doch das
        # ist schon außerhalb. Auf der Karte bleibt nur der Schritt nach unten.
        abstaende = helfer.abstaende_aus(
            """
            3  2  1
            2  1  0
            """
        )
        self.pruefe_schritt(
            abstaende,
            (1, 0),
            2,
            2,
            (1, 1),
            "Nachbarn gibt es nur auf der Karte. breite und hoehe sagen, wo sie aufhört, "
            "genau wie in Mission 2.",
        )

    def test_am_ziel_gibt_es_keinen_schritt_mehr(self):
        abstaende = helfer.abstaende_aus(ABSTAENDE)
        self.pruefe_schritt(
            abstaende,
            (4, 2),
            BREITE,
            HOEHE,
            None,
            "Wer den Abstand 0 hat, ist schon da. Dann ist die Antwort None.",
        )

    def test_fuer_eine_zelle_ohne_abstand_gibt_es_keinen_schritt(self):
        abstaende = helfer.abstaende_aus(ABSTAENDE)
        self.pruefe_schritt(
            abstaende,
            (2, 1),
            BREITE,
            HOEHE,
            None,
            "Steht die Zelle selbst nicht in der Abstandskarte, führt von dort kein Weg "
            "zum Ziel. Prüfe das zuerst, dann ist die Antwort None.",
        )

    def test_bergauf_geht_es_nie(self):
        # (0, 0) hat Abstand 3. Rechts auch 3, unten 4: Kein Nachbar ist näher am Ziel.
        abstaende = {(0, 0): 3, (1, 0): 3, (0, 1): 4}
        self.pruefe_schritt(
            abstaende,
            (0, 0),
            2,
            2,
            None,
            "Ein Schritt zählt nur, wenn der Nachbar einen kleineren Abstand hat als die "
            "eigene Zelle. Gleich groß oder größer reicht nicht, dann ist die Antwort None.",
        )

    def test_wer_den_schritten_folgt_kommt_auf_dem_kuerzesten_weg_ans_ziel(self):
        abstaende = helfer.abstaende_aus(ABSTAENDE)
        zelle = (0, 0)
        weg = [zelle]
        while len(weg) <= 10:
            zelle = self.werkstatt.naechster_schritt(abstaende, zelle, BREITE, HOEHE)
            if zelle is None:
                break
            weg.append(zelle)
        erwartet = [
            (0, 0),
            (1, 0),
            (1, 1),
            (1, 2),
            (1, 3),
            (1, 4),
            (2, 4),
            (3, 4),
            (3, 3),
            (3, 2),
            (4, 2),
        ]
        self.pruefe_gleich(
            weg,
            erwartet,
            "Der Weg von (0, 0) aus, immer mit naechster_schritt weiter,",
            TIPP_GLEICHSTAND,
        )

    def test_naechster_schritt_laesst_die_abstandskarte_wie_sie_war(self):
        abstaende = helfer.abstaende_aus(ABSTAENDE)
        self.werkstatt.naechster_schritt(abstaende, (0, 0), BREITE, HOEHE)
        self.pruefe_unveraendert(
            helfer.abstaende_aus(ABSTAENDE),
            abstaende,
            "die Abstandskarte",
            "naechster_schritt(abstaende, (0, 0), 5, 5)",
            "naechster_schritt liest die Abstandskarte nur. Es trägt nichts ein.",
        )
