"""Der Ersatz zu Spur A: was das Spiel benutzt, solange die Missionen 1 bis 5 offen sind.

Ein Ersatz ist mit Absicht schwächer als die echte Regel, und man soll das im Spiel sehen.
Jede Klasse hier zeigt darum an einer kleinen Karte, wo der Ersatz anders antwortet, als es
die Mission verlangt. Geholt wird jeder Ersatz so, wie ihn auch die Werkbank holt: aus dem
Verzeichnis in ``rudersdorf/ersatz.py``.
"""

import pathlib
import unittest

from rudersdorf.ersatz import ersatz_fuer
from rudersdorf.werkbank import FAEHIGKEITEN
from tests.missionen.helfer import raster_aus

KARTEN_ORDNER = pathlib.Path(__file__).resolve().parents[2] / "karten"

# Eine Felswand mit einer einzigen Lücke unten. Das Ziel "Z" ist die Zelle (4, 2).
MAUER = """
    ..#..
    ..#..
    ..#.Z
    ..#..
    .....
"""

# Eine freie Wiese. Das Orktor "S" ist die Zelle (0, 0), das Dorftor "Z" die Zelle (4, 4).
FELD = """
    S....
    .....
    .....
    .....
    ....Z
"""


def karte_aus_datei(name):
    """Liest eine Kartendatei so einfach wie möglich, ohne Code aus Werkstatt oder Ersatz."""
    text = (KARTEN_ORDNER / f"{name}.txt").read_text(encoding="utf-8")
    return [list(zeile) for zeile in text.splitlines() if zeile]


class ErsatzVollstaendig(unittest.TestCase):
    """Für jeden Namen einer Fähigkeit gibt es einen Ersatz, sonst bliebe das Spiel stehen."""

    def pruefe_alle_namen(self, faehigkeit):
        for name in FAEHIGKEITEN[faehigkeit]["namen"]:
            ersatz = ersatz_fuer(faehigkeit, name)
            self.assertTrue(
                callable(ersatz), f"Der Ersatz für {faehigkeit}.{name} lässt sich nicht aufrufen."
            )

    def test_karten_hat_einen_ersatz_fuer_jeden_namen(self):
        self.pruefe_alle_namen("karten")

    def test_wegfindung_hat_einen_ersatz_fuer_jeden_namen(self):
        self.pruefe_alle_namen("wegfindung")

    def test_bauregel_hat_einen_ersatz_fuer_jeden_namen(self):
        self.pruefe_alle_namen("bauregel")


class ErsatzKarten(unittest.TestCase):
    """Ohne Mission 1 kann das Spiel keine Karte lesen: Es gibt immer nur das Flusstal."""

    def test_aus_einem_anderen_kartentext_wird_trotzdem_das_flusstal(self):
        lies_karte = ersatz_fuer("karten", "lies_karte")
        self.assertEqual(
            lies_karte("S.Z\n...\n"),
            karte_aus_datei("flusstal"),
            "Der Ersatz liest den Text nicht. Er liefert immer die eingebaute Karte flusstal.",
        )

    def test_aus_der_datei_einer_anderen_karte_wird_trotzdem_das_flusstal(self):
        lies_karte = ersatz_fuer("karten", "lies_karte")
        text = (KARTEN_ORDNER / "zwei_tore.txt").read_text(encoding="utf-8")
        bekommen = lies_karte(text)
        self.assertNotEqual(
            bekommen,
            karte_aus_datei("zwei_tore"),
            "Der Ersatz darf die Karte zwei_tore nicht lesen können, das wäre schon Mission 1.",
        )
        self.assertEqual(bekommen, karte_aus_datei("flusstal"))

    def test_das_flusstal_des_ersatzes_hat_24_spalten_und_16_zeilen(self):
        raster = ersatz_fuer("karten", "lies_karte")("S.Z\n")
        self.assertEqual([len(zeile) for zeile in raster], [24] * 16)

    def test_jeder_aufruf_liefert_ein_eigenes_raster(self):
        lies_karte = ersatz_fuer("karten", "lies_karte")
        erstes = lies_karte("S.Z\n")
        erstes[0][0] = "?"
        self.assertEqual(
            lies_karte("S.Z\n"),
            karte_aus_datei("flusstal"),
            "Wer das erste Raster verändert, darf damit das nächste nicht verderben.",
        )

    def test_der_ersatz_findet_orktor_und_dorftor_im_flusstal(self):
        finde = ersatz_fuer("karten", "finde")
        raster = karte_aus_datei("flusstal")
        self.assertEqual(finde(raster, "S"), [(0, 7)])
        self.assertEqual(finde(raster, "Z"), [(17, 8)])


class ErsatzWegfindung(unittest.TestCase):
    """Ohne die Missionen 2 bis 4 laufen Gegner als Geister: geradewegs durch alles hindurch."""

    def setUp(self):
        self.raster = raster_aus(MAUER)
        self.ziel = (4, 2)
        self.gesperrt = {(3, 1)}  # hier steht ein Bauwerk
        self.abstaende = ersatz_fuer("wegfindung", "abstandskarte")(
            self.raster, self.ziel, self.gesperrt
        )

    def test_hinter_der_mauer_zaehlt_der_ersatz_die_luftlinie_statt_des_umwegs(self):
        # Mission 3 verlangt für (1, 2) den Umweg durch die Lücke: 7 Schritte.
        self.assertEqual(
            self.abstaende[(1, 2)],
            3,
            "Der Ersatz zählt Spalten und Zeilen bis zum Ziel und kümmert sich um keine Wand.",
        )

    def test_auch_fels_und_bauwerke_haben_beim_ersatz_einen_abstand(self):
        # Nach Mission 3 fehlen beide Zellen in der Abstandskarte.
        self.assertEqual(self.abstaende.get((2, 2)), 2, "Fels direkt neben dem Weg zum Ziel")
        self.assertEqual(self.abstaende.get((3, 1)), 2, "die Zelle mit dem Bauwerk")

    def test_jede_zelle_der_karte_hat_ihre_luftlinie_als_abstand(self):
        erwartet = {}
        for zeile in range(5):
            for spalte in range(5):
                erwartet[(spalte, zeile)] = abs(spalte - 4) + abs(zeile - 2)
        self.assertEqual(self.abstaende, erwartet)

    def test_das_ziel_hat_auch_beim_ersatz_den_abstand_null(self):
        self.assertEqual(self.abstaende[self.ziel], 0)

    def test_ein_geist_laeuft_gerade_durch_die_mauer_zum_ziel(self):
        naechster_schritt = ersatz_fuer("wegfindung", "naechster_schritt")
        zelle = (0, 2)
        weg = []
        while zelle is not None and len(weg) < 10:
            zelle = naechster_schritt(self.abstaende, zelle, 5, 5)
            if zelle is not None:
                weg.append(zelle)
        self.assertEqual(
            weg,
            [(1, 2), (2, 2), (3, 2), (4, 2)],
            "Der Weg des Ersatzes führt über den Fels (2, 2); nach Mission 4 wären es 8 Schritte.",
        )

    def test_der_ersatz_laesst_gesperrt_und_das_raster_wie_sie_waren(self):
        self.assertEqual(self.gesperrt, {(3, 1)})
        self.assertEqual(self.raster, raster_aus(MAUER))


class ErsatzBauregel(unittest.TestCase):
    """Ohne Mission 5 gilt eine grobe Regel: nie direkt neben ein anderes Bauwerk, auch nicht
    schräg. So kann keine Mauer entstehen, die den Weg versperrt."""

    def darf_bauen(self, zelle, gesperrt):
        raster = raster_aus(FELD)
        return ersatz_fuer("bauregel", "darf_bauen")(
            raster, zelle, set(gesperrt), [(0, 0)], (4, 4), set()
        )

    def test_schraeg_neben_einem_bauwerk_verbietet_der_ersatz_das_bauen(self):
        # Mission 5 erlaubt diese Zelle: Auf der freien Wiese bleibt der Weg offen.
        for zelle in [(1, 1), (3, 1), (1, 3), (3, 3)]:
            self.assertIs(
                self.darf_bauen(zelle, [(2, 2)]),
                False,
                f"{zelle} liegt schräg neben dem Bauwerk auf (2, 2).",
            )

    def test_direkt_neben_einem_bauwerk_verbietet_der_ersatz_das_bauen(self):
        for zelle in [(2, 1), (3, 2), (2, 3), (1, 2)]:
            self.assertIs(
                self.darf_bauen(zelle, [(2, 2)]),
                False,
                f"{zelle} liegt direkt neben dem Bauwerk auf (2, 2).",
            )

    def test_mit_einer_zelle_abstand_erlaubt_der_ersatz_das_bauen(self):
        for zelle in [(2, 0), (4, 2), (0, 3), (4, 0)]:
            self.assertIs(
                self.darf_bauen(zelle, [(2, 2)]),
                True,
                f"Zwischen {zelle} und dem Bauwerk auf (2, 2) liegt mindestens eine Zelle.",
            )

    def test_ohne_andere_bauwerke_erlaubt_der_ersatz_das_bauen(self):
        self.assertIs(self.darf_bauen((2, 2), []), True)

    def test_der_ersatz_laesst_gesperrt_wie_es_war(self):
        gesperrt = {(2, 2)}
        ersatz_fuer("bauregel", "darf_bauen")(
            raster_aus(FELD), (2, 0), gesperrt, [(0, 0)], (4, 4), set()
        )
        self.assertEqual(gesperrt, {(2, 2)})


if __name__ == "__main__":
    unittest.main()
