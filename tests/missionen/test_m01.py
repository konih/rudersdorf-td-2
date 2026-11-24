"""Mission 1 · Die Karte lesen: Aus einem Text wird ein Raster, und im Raster wird gesucht."""

from tests.missionen import helfer

TIPP_ZEICHEN = "Jede Zeile des Textes wird zu einer Liste aus einzelnen Zeichen."
TIPP_ZEILENENDE = (
    "Leerzeichen am Ende einer Zeile sieht man nicht, sie gehören nicht zur Karte. "
    "Schneide sie ab, bevor du die Zeile in Zeichen zerlegst."
)
TIPP_LEERZEILEN = (
    "Eine Zeile, in der nichts oder nur Leerzeichen stehen, ist keine Zeile der Karte. "
    "Überspringe sie."
)
TIPP_ZEILENANFANG = "Schneide nur am Ende der Zeile ab, nicht am Anfang."
TIPP_LAENGE = (
    "Eine Karte ist ein Rechteck. Vergleiche die Länge jeder Zeile mit der Länge der ersten "
    "und melde einen ValueError, wenn eine nicht passt."
)
TIPP_LEER = "Bleibt keine einzige Zeile übrig, gibt es keine Karte. Das ist ein ValueError."
TIPP_VERTAUSCHT = (
    "Zeile und Spalte vertauscht? Eine Zelle ist (spalte, zeile), "
    "das Raster wird aber mit raster[zeile][spalte] gelesen."
)
TIPP_REIHENFOLGE = (
    "Geh das Raster so durch, wie man liest: die Zeilen von oben nach unten "
    "und in jeder Zeile von links nach rechts."
)


class Mission01(helfer.Missionstest):
    # ----- lies_karte -----

    def test_jede_zeile_wird_eine_liste_aus_einzelnen_zeichen(self):
        text = "S.#\n.~.\n..Z\n"
        erwartet = [
            ["S", ".", "#"],
            [".", "~", "."],
            [".", ".", "Z"],
        ]
        self.pruefe_gleich(
            self.werkstatt.lies_karte(text), erwartet, f"lies_karte({text!r})", TIPP_ZEICHEN
        )

    def test_leerzeichen_am_zeilenende_gehoeren_nicht_zur_karte(self):
        text = "S.#  \n.~.\t\n..Z \n"
        erwartet = [
            ["S", ".", "#"],
            [".", "~", "."],
            [".", ".", "Z"],
        ]
        self.pruefe_gleich(
            self.werkstatt.lies_karte(text), erwartet, f"lies_karte({text!r})", TIPP_ZEILENENDE
        )

    def test_leere_zeilen_davor_dazwischen_und_danach_werden_uebersprungen(self):
        text = "\n\nS.#\n\n.~.\n   \n..Z\n\n\n"
        erwartet = [
            ["S", ".", "#"],
            [".", "~", "."],
            [".", ".", "Z"],
        ]
        self.pruefe_gleich(
            self.werkstatt.lies_karte(text), erwartet, f"lies_karte({text!r})", TIPP_LEERZEILEN
        )

    def test_leerzeilen_ringsum_und_leerzeichen_am_ende_zusammen(self):
        text = "\n  \nS.#   \n.~.\n..Z  \n\n"
        erwartet = [
            ["S", ".", "#"],
            [".", "~", "."],
            [".", ".", "Z"],
        ]
        self.pruefe_gleich(
            self.werkstatt.lies_karte(text), erwartet, f"lies_karte({text!r})", TIPP_ZEILENENDE
        )

    def test_die_letzte_zeile_braucht_keinen_zeilenumbruch(self):
        text = "S.\n.Z"
        erwartet = [["S", "."], [".", "Z"]]
        self.pruefe_gleich(
            self.werkstatt.lies_karte(text), erwartet, f"lies_karte({text!r})", TIPP_ZEICHEN
        )

    def test_leerzeichen_am_zeilenanfang_bleiben_stehen(self):
        text = " .Z\n#..\n"
        erwartet = [[" ", ".", "Z"], ["#", ".", "."]]
        self.pruefe_gleich(
            self.werkstatt.lies_karte(text), erwartet, f"lies_karte({text!r})", TIPP_ZEILENANFANG
        )

    def test_unbekannte_zeichen_sind_hier_noch_kein_fehler(self):
        text = "S?Z\n"
        self.pruefe_gleich(
            self.werkstatt.lies_karte(text),
            [["S", "?", "Z"]],
            f"lies_karte({text!r})",
            "lies_karte liest nur. Ob ein Zeichen erlaubt ist, prüft später das Spiel.",
        )

    def test_eine_zu_kurze_zeile_ist_ein_fehler(self):
        for text in ("S..\n.Z\n", "S.\n..Z\n", "...\n...\n..\n"):
            self.pruefe_fehler(
                ValueError, f"lies_karte({text!r})", TIPP_LAENGE, self.werkstatt.lies_karte, text
            )

    def test_ein_leerer_text_ist_ein_fehler(self):
        self.pruefe_fehler(ValueError, "lies_karte('')", TIPP_LEER, self.werkstatt.lies_karte, "")

    def test_ein_text_nur_aus_leerzeilen_ist_ein_fehler(self):
        text = "\n   \n\n"
        self.pruefe_fehler(
            ValueError, f"lies_karte({text!r})", TIPP_LEER, self.werkstatt.lies_karte, text
        )

    # ----- finde -----

    def test_finde_nennt_erst_die_spalte_und_dann_die_zeile(self):
        raster = helfer.raster_aus(
            """
            ....
            ...Z
            """
        )
        self.pruefe_gleich(
            self.werkstatt.finde(raster, "Z"), [(3, 1)], "finde(raster, 'Z')", TIPP_VERTAUSCHT
        )

    def test_finde_sucht_zeile_fuer_zeile_von_oben_nach_unten(self):
        raster = helfer.raster_aus(
            """
            .S.S
            S...
            ..S.
            """
        )
        self.pruefe_gleich(
            self.werkstatt.finde(raster, "S"),
            [(1, 0), (3, 0), (0, 1), (2, 2)],
            "finde(raster, 'S')",
            TIPP_REIHENFOLGE,
        )

    def test_finde_liefert_eine_leere_liste_wenn_das_zeichen_fehlt(self):
        raster = helfer.raster_aus(
            """
            S..
            ..Z
            """
        )
        self.pruefe_gleich(
            self.werkstatt.finde(raster, "~"),
            [],
            "finde(raster, '~')",
            "Kommt das Zeichen nicht vor, ist die Antwort eine leere Liste und nicht None.",
        )

    def test_finde_laesst_das_raster_wie_es_war(self):
        raster = helfer.raster_aus(
            """
            S.#
            #.Z
            """
        )
        vorher = [list(zeile) for zeile in raster]
        self.werkstatt.finde(raster, "#")
        self.pruefe_unveraendert(
            vorher,
            raster,
            "das Raster",
            "finde(raster, '#')",
            "finde schaut nur nach. Es schreibt nichts in das Raster.",
        )
