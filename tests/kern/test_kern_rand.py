"""Der Spielkern am Rand: eine Suche für alle Gegner, das Spiel ohne gelöste Missionen
und was sonst noch gilt, wenn etwas fehlt oder falsch ist.

Die Tests in ``test_karte``, ``test_bewegung`` und ``test_bauen`` legen fest, was der Kern
tut. Hier steht, was er darüber hinaus verspricht.
"""

import unittest
from unittest import mock

from rudersdorf import daten
from rudersdorf.fehler import Lernfehler
from rudersdorf.kern.dorf import Dorf
from rudersdorf.kern.gegner import Gegner
from rudersdorf.kern.karte import Karte, lade_karte
from rudersdorf.kern.spiel import Spiel
from rudersdorf.werkbank import Werkbank
from tests.kern.helfer import (
    ereignisse,
    karte_aus,
    laufe,
    mitte,
    paket_wie_loesung,
    partie,
    raster_von,
    reich,
    zeilen_von,
)

# Oben der kurze Weg, unten ein Umweg.
UMWEG = """
    S.......Z
    ##.###.##
    ##.....##
"""
ZWEI_TORE = """
    S.......Z
    .########
    S########
"""
FELD = """
    S..#......
    ..........
    .........Z
"""

IMMER_JA = '''
def darf_bauen(raster, zelle, gesperrt, starts, ziel, besetzt):
    """Eine fehlerhafte Bauregel: Sie erlaubt einfach alles."""
    return True
'''
IMMER_NEIN = '''
def darf_bauen(raster, zelle, gesperrt, starts, ziel, besetzt):
    """Eine fehlerhafte Bauregel: Sie verbietet einfach alles."""
    return False
'''
AUF_DER_STELLE = """
def naechster_schritt(abstaende, zelle, breite, hoehe):
    \"\"\"Ein Fehler: Der nächste Schritt führt auf die Zelle, auf der man schon steht.\"\"\"
    return zelle
"""
SCHADEN_HEILT = """
def berechne_schaden(schaden, art, resistenzen):
    \"\"\"Ein Fehler: Aus Schaden wird Heilung.\"\"\"
    return -schaden
"""
LIES_KARTE_KAPUTT = '''
def lies_karte(text):
    """Ein Fehler im Code, nicht im Kartentext."""
    return text + 1
'''

OFFEN = ("karten", "wegfindung", "bauregel", "schadensarten")


class Zaehler:
    """Zählt mit, wie oft die Partie welche Funktion der Werkstatt aufruft."""

    def __init__(self, test, werkbank):
        self.echt = werkbank.rufe
        self.aufrufe = []
        flicken = mock.patch.object(werkbank, "rufe", side_effect=self.rufe)
        flicken.start()
        test.addCleanup(flicken.stop)

    def rufe(self, faehigkeit, name, *args, **kwargs):
        self.aufrufe.append(name)
        return self.echt(faehigkeit, name, *args, **kwargs)

    def anzahl(self, name):
        return self.aufrufe.count(name)


class EineSucheFuerAlle(unittest.TestCase):
    """Die Abstandskarte wird nur neu berechnet, wenn sich die gesperrten Zellen ändern."""

    def setUp(self):
        self.werkbank = Werkbank("loesung")
        self.zaehler = Zaehler(self, self.werkbank)
        self.spiel = reich(partie(UMWEG, werkbank=self.werkbank))

    def test_viele_gegner_und_viele_schritte_brauchen_eine_einzige_suche(self):
        for spalte in (0, 1, 2):
            self.spiel.erzeuge_gegner("ork", zelle=(spalte, 0))
        laufe(self.spiel, 200)
        self.spiel.abstaende()
        self.assertEqual(1, self.zaehler.anzahl("abstandskarte"))

    def test_nach_dem_naechsten_schritt_wird_nur_beim_ankommen_auf_einer_mitte_gefragt(self):
        self.spiel.erzeuge_gegner("ork", zelle=(0, 0))
        schritte = 200
        laufe(self.spiel, schritte)
        zellen = daten.GEGNER["ork"]["tempo"] * schritte * daten.DT / daten.ZELLE
        self.assertLessEqual(self.zaehler.anzahl("naechster_schritt"), int(zellen) + 1)

    def test_die_abstandskarte_bleibt_dasselbe_woerterbuch_solange_nichts_gebaut_wird(self):
        vorher = self.spiel.abstaende()
        self.spiel.erzeuge_gegner("ork", zelle=(0, 0))
        laufe(self.spiel, 30)
        self.assertIs(vorher, self.spiel.abstaende())

    def test_ein_bauwerk_kostet_genau_eine_neue_suche(self):
        self.spiel.erzeuge_gegner("ork", zelle=(0, 0))
        self.spiel.abstaende()
        vorher = self.zaehler.anzahl("abstandskarte")
        self.assertTrue(self.spiel.baue("palisade", (4, 0)))
        laufe(self.spiel, 100)
        self.assertEqual(12, self.spiel.abstaende()[(0, 0)])
        # Die Bauregel der Lösung sucht selbst einmal (in der Lösung, nicht über die
        # Werkbank). Der Kern sucht für sein Sicherheitsnetz einmal und behält das Ergebnis.
        self.assertEqual(vorher + 1, self.zaehler.anzahl("abstandskarte"))

    def test_eine_ablehnung_laesst_die_abstandskarte_wie_sie_ist(self):
        vorher = self.spiel.abstaende()
        suchen = self.zaehler.anzahl("abstandskarte")
        self.assertFalse(self.spiel.baue("palisade", (0, 1)))  # Fels
        self.assertEqual(suchen, self.zaehler.anzahl("abstandskarte"), "Für Fels sucht niemand.")
        self.spiel.dorf.vorraete["gold"] = 0
        self.assertFalse(self.spiel.baue("palisade", (4, 0)))  # kein Gold
        # Für eine freie Zelle hat das Sicherheitsnetz einmal zur Probe gesucht. Das Ergebnis
        # der Probe wird nach einer Ablehnung weggeworfen: Es gilt weiter die alte Karte.
        self.assertEqual(suchen + 1, self.zaehler.anzahl("abstandskarte"))
        self.assertIs(vorher, self.spiel.abstaende())
        self.assertEqual(suchen + 1, self.zaehler.anzahl("abstandskarte"))
        self.assertEqual(set(), self.spiel.karte.gesperrt)

    def test_ein_verkauf_kostet_genau_eine_neue_suche(self):
        self.assertTrue(self.spiel.baue("palisade", (4, 0)))
        self.spiel.erzeuge_gegner("ork", zelle=(0, 0))
        vorher = self.zaehler.anzahl("abstandskarte")
        self.assertTrue(self.spiel.verkaufe((4, 0)))
        laufe(self.spiel, 100)
        self.assertEqual(8, self.spiel.abstaende()[(0, 0)])
        self.assertEqual(vorher + 1, self.zaehler.anzahl("abstandskarte"))

    def test_die_gesperrten_zellen_sind_genau_die_zellen_der_bauwerke(self):
        spiel = reich(partie(FELD))
        self.assertTrue(spiel.baue("palisade", (4, 0)))
        self.assertTrue(spiel.baue("pfeil", (4, 2)))
        self.assertEqual({(4, 0), (4, 2)}, spiel.karte.gesperrt)
        self.assertTrue(spiel.verkaufe((4, 0)))
        self.assertEqual({(4, 2)}, spiel.karte.gesperrt)
        self.assertEqual(set(spiel.bauwerke), spiel.karte.gesperrt)

    def test_nach_neuem_code_der_werkstatt_laesst_sich_die_abstandskarte_vergessen(self):
        self.spiel.abstaende()
        vorher = self.zaehler.anzahl("abstandskarte")
        self.spiel.karte.vergiss_abstaende()
        self.spiel.abstaende()
        self.assertEqual(vorher + 1, self.zaehler.anzahl("abstandskarte"))


class OhneGeloesteMissionen(unittest.TestCase):
    """Mit der Werkstatt, wie sie ausgeliefert wird, läuft der Kern auf dem Ersatz."""

    def setUp(self):
        self.werkbank = Werkbank("werkstatt")
        for faehigkeit in OFFEN:
            self.assertTrue(self.werkbank.ist_offen(faehigkeit), faehigkeit)

    def test_die_partie_beginnt_auf_dem_flusstal_egal_welche_karte_gewaehlt_ist(self):
        spiel = Spiel(self.werkbank, karte="zwei_tore")
        self.assertEqual("flusstal", spiel.karte.name)
        self.assertEqual(1, len(spiel.karte.starts))
        self.assertIn(spiel.karte.starts[0], spiel.abstaende())

    def test_die_tore_findet_der_kern_selbst_im_raster(self):
        # Der Ersatz von finde kennt nur das Flusstal. Der Kern fragt ihn darum gar nicht.
        werkbank = Werkbank("loesung", gesperrt=("wegfindung",))
        spiel = partie(ZWEI_TORE, werkbank=werkbank)
        self.assertEqual([(0, 0), (0, 2)], spiel.karte.starts)
        self.assertEqual((8, 0), spiel.karte.ziel)

    def test_ein_ork_laeuft_als_geist_bis_zum_dorftor_und_bricht_durch(self):
        spiel = Spiel(self.werkbank)
        leben = spiel.dorf.leben
        ork = spiel.erzeuge_gegner("ork")
        sekunden = ork.rest_weg / ork.tempo / daten.SUMPF_TEMPO_FAKTOR
        laufe(spiel, round(sekunden / daten.LABOR_DT) + 2, daten.LABOR_DT)
        self.assertEqual([], spiel.gegner)
        self.assertEqual(leben - daten.GEGNER["ork"]["dorfschaden"], spiel.dorf.leben)
        self.assertEqual(1, len(ereignisse(spiel, "durchbruch")))

    def test_gebaut_wird_frei_stehend_und_nicht_neben_ein_anderes_bauwerk(self):
        spiel = reich(Spiel(self.werkbank))
        self.assertIs(spiel.baue("pfeil", (5, 4)), True)
        self.assertIs(spiel.baue("pfeil", (6, 5)), False)
        self.assertIn("Mission 5", spiel.meldung)
        self.assertNotIn("Weg", spiel.meldung, "Der Ersatz lehnt nicht wegen der Wege ab.")
        self.assertNotIn("Deine", spiel.meldung, "Die Bauregel ist noch gar nicht geschrieben.")
        self.assertIs(spiel.baue("pfeil", (7, 4)), True)
        self.assertEqual({(5, 4), (7, 4)}, set(spiel.bauwerke))

    def test_auch_mit_dem_ersatz_wird_nicht_auf_wasser_oder_auf_gegner_gebaut(self):
        spiel = reich(Spiel(self.werkbank))
        ork = spiel.erzeuge_gegner("ork")
        self.assertIs(spiel.baue("pfeil", (8, 0)), False)
        self.assertIn("Wasser", spiel.meldung)
        self.assertIs(spiel.baue("pfeil", ork.zelle), False)
        self.assertEqual({}, spiel.bauwerke)

    def test_schaden_kommt_mit_dem_ersatz_ganz_an(self):
        gegner = Gegner("schildork", self.werkbank)
        self.assertEqual(20, gegner.erleide_schaden(20, "stich"))


class FalscheBauregel(unittest.TestCase):
    def mit(self, quelltext, bild=FELD):
        werkbank = Werkbank(paket_wie_loesung(self, {"raster": quelltext}))
        self.assertFalse(werkbank.ist_offen("bauregel"))
        return reich(partie(bild, werkbank=werkbank))

    def test_sagt_die_bauregel_immer_ja_wird_trotzdem_nicht_auf_fels_gebaut(self):
        spiel = self.mit(IMMER_JA)
        self.assertIs(spiel.baue("pfeil", (3, 0)), False)
        self.assertIn("Fels", spiel.meldung)
        self.assertIn("Mission 5", spiel.meldung)
        self.assertEqual({}, spiel.bauwerke)

    def test_sagt_die_bauregel_immer_ja_wird_trotzdem_nicht_ausserhalb_der_karte_gebaut(self):
        for zelle in [(-1, 1), (1, -1), (daten.SPALTEN, 1), (1, daten.ZEILEN)]:
            with self.subTest(zelle=zelle):
                spiel = self.mit(IMMER_JA)
                self.assertIs(spiel.baue("pfeil", zelle), False)
                self.assertIn("Mission 5", spiel.meldung)
                self.assertEqual({}, spiel.bauwerke)

    def test_sagt_die_bauregel_immer_ja_wird_trotzdem_nicht_doppelt_oder_auf_gegner_gebaut(self):
        spiel = self.mit(IMMER_JA)
        self.assertIs(spiel.baue("pfeil", (5, 1)), True)
        self.assertIs(spiel.baue("kanone", (5, 1)), False)
        self.assertIn("Mission 5", spiel.meldung)
        self.assertEqual("pfeil", spiel.bauwerke[(5, 1)].art)
        ork = spiel.erzeuge_gegner("ork", zelle=(1, 1))
        laufe(spiel, 5)
        for zelle in (ork.zelle, ork.ziel_zelle):
            self.assertIs(spiel.baue("pfeil", zelle), False)
            self.assertIn("Mission 5", spiel.meldung)

    def test_sagt_die_bauregel_immer_nein_nennt_die_meldung_die_mission(self):
        spiel = self.mit(IMMER_NEIN)
        gold = spiel.dorf.vorraete["gold"]
        self.assertIs(spiel.baue("pfeil", (5, 1)), False)
        self.assertIn("Mission 5", spiel.meldung)
        self.assertNotIn("Weg", spiel.meldung)
        self.assertEqual({}, spiel.bauwerke)
        self.assertEqual(gold, spiel.dorf.vorraete["gold"])


class Randfaelle(unittest.TestCase):
    def test_der_rest_weg_wartender_gegner_folgt_sofort_dem_bauen_und_verkaufen(self):
        spiel = reich(partie(UMWEG))
        ork = spiel.erzeuge_gegner("ork", zelle=(0, 0))
        self.assertEqual(8 * daten.ZELLE, ork.rest_weg)
        self.assertTrue(spiel.baue("palisade", (4, 0)))
        self.assertEqual(12 * daten.ZELLE, ork.rest_weg)
        self.assertTrue(spiel.verkaufe((4, 0)))
        self.assertEqual(8 * daten.ZELLE, ork.rest_weg)

    def test_fuehrt_der_naechste_schritt_auf_die_eigene_zelle_wartet_der_gegner(self):
        # Ohne diese Vorsicht käme der Rechenschritt nie zu einem Ende.
        werkbank = Werkbank(paket_wie_loesung(self, {"raster": AUF_DER_STELLE}))
        spiel = partie(FELD, werkbank=werkbank)
        ork = spiel.erzeuge_gegner("ork", zelle=(1, 1))
        laufe(spiel, 5)
        self.assertEqual(mitte((1, 1)), (ork.x, ork.y))
        self.assertIsNone(ork.ziel_zelle)

    def test_haelt_nur_das_netz_den_gang_offen_ist_von_deiner_bauregel_keine_rede(self):
        werkbank = Werkbank("loesung", gesperrt=("bauregel",))
        spiel = reich(partie("S.......Z", werkbank=werkbank))
        self.assertIs(spiel.baue("palisade", (4, 0)), False)
        self.assertIn("Weg", spiel.meldung)
        self.assertNotIn("Deine", spiel.meldung)
        self.assertNotIn("Mission 5", spiel.meldung)

    def test_start_waehlt_das_orktor_mit_dieser_nummer(self):
        spiel = partie(ZWEI_TORE)
        erster = spiel.erzeuge_gegner("ork", start=0)
        zweiter = spiel.erzeuge_gegner("ork", start=1)
        self.assertEqual(spiel.karte.starts[0], erster.zelle)
        self.assertEqual(spiel.karte.starts[1], zweiter.zelle)
        self.assertEqual(mitte(spiel.karte.starts[1]), (zweiter.x, zweiter.y))
        self.assertEqual(10 * daten.ZELLE, zweiter.rest_weg)

    def test_ist_die_partie_vorbei_laeuft_und_baut_niemand_mehr(self):
        for phase in ("sieg", "verloren"):
            with self.subTest(phase):
                spiel = reich(partie(FELD))
                self.assertTrue(spiel.baue("pfeil", (6, 1)))
                ork = spiel.erzeuge_gegner("ork", zelle=(1, 1))
                spiel.phase = phase
                laufe(spiel, 30)
                self.assertEqual(mitte((1, 1)), (ork.x, ork.y))
                self.assertEqual(0.0, spiel.zeit)
                self.assertIs(spiel.baue("pfeil", (5, 1)), False)
                self.assertNotEqual("", spiel.meldung)
                self.assertIs(spiel.verkaufe((6, 1)), False)
                self.assertEqual([(6, 1)], list(spiel.bauwerke))

    def test_die_zeit_der_partie_zaehlt_die_schritte(self):
        spiel = partie(FELD)
        laufe(spiel, 60)
        self.assertAlmostEqual(1.0, spiel.zeit)

    def test_nach_dem_bauen_und_verkaufen_ist_die_alte_ablehnung_vergessen(self):
        spiel = reich(partie(FELD))
        self.assertFalse(spiel.baue("pfeil", (3, 0)))
        self.assertNotEqual("", spiel.meldung)
        self.assertTrue(spiel.baue("pfeil", (5, 1)))
        self.assertEqual("", spiel.meldung)
        self.assertFalse(spiel.verkaufe((6, 1)))
        self.assertNotEqual("", spiel.meldung)
        self.assertTrue(spiel.verkaufe((5, 1)))
        self.assertEqual("", spiel.meldung)

    def test_gebaut_und_verkauft_nennen_zelle_und_art(self):
        spiel = reich(partie(FELD))
        spiel.baue("kanone", (5, 1))
        (gebaut,) = ereignisse(spiel, "gebaut")
        self.assertEqual(((5, 1), "kanone"), (gebaut["zelle"], gebaut["bauwerk_art"]))
        spiel.verkaufe((5, 1))
        (verkauft,) = ereignisse(spiel, "verkauft")
        self.assertEqual(((5, 1), "kanone"), (verkauft["zelle"], verkauft["bauwerk_art"]))
        erwartet = int(daten.VERKAUF_ANTEIL * daten.BAUWERKE["kanone"]["kosten"]["gold"])
        self.assertEqual(erwartet, verkauft["gold"])

    def test_fehlt_gold_und_stein_nennt_die_meldung_beides(self):
        spiel = reich(partie(FELD), gold=0, stein=0)
        self.assertFalse(spiel.baue("blitz", (5, 1)))
        self.assertIn("Gold", spiel.meldung)
        self.assertIn("Stein", spiel.meldung)

    def test_ein_fehler_im_code_von_lies_karte_bleibt_ein_lernfehler(self):
        werkbank = Werkbank(paket_wie_loesung(self, {"raster": LIES_KARTE_KAPUTT}))
        with self.assertRaises(Lernfehler) as gefangen:
            Spiel(werkbank, kartentext=karte_aus(FELD))
        self.assertEqual("TypeError", gefangen.exception.art)
        with self.assertRaises(Lernfehler):
            Spiel(werkbank, karte="zwei_tore")

    def test_eine_fehlende_kartendatei_ist_ein_fehler_der_die_datei_nennt(self):
        with self.assertRaises(ValueError) as gefangen:
            lade_karte("gibtsnicht", Werkbank("loesung"))
        self.assertIn("gibtsnicht.txt", str(gefangen.exception))

    def test_die_meldung_zur_ersatzkarte_nennt_auch_die_gewuenschte_karte(self):
        spiel = Spiel(Werkbank("loesung"), karte="gibtsnicht")
        self.assertIn("'gibtsnicht'", spiel.meldung)

    def test_die_karte_behaelt_ihr_eigenes_raster(self):
        raster = raster_von(FELD)
        karte = Karte(raster)
        raster[0][1] = "#"
        self.assertEqual(karte_aus(FELD).splitlines(), zeilen_von(karte.raster))
        self.assertEqual(".", karte.gelaende((1, 0)))
        self.assertTrue(karte.enthaelt((daten.SPALTEN - 1, daten.ZEILEN - 1)))
        for zelle in [(-1, 0), (0, -1), (daten.SPALTEN, 0), (0, daten.ZEILEN)]:
            self.assertFalse(karte.enthaelt(zelle), zelle)

    def test_was_keine_liste_von_zeilen_ist_ist_keine_karte(self):
        for name, raster in [("None", None), ("Zahl", 7), ("Zahlen", [1] * daten.ZEILEN)]:
            with self.subTest(name), self.assertRaises(ValueError):
                Karte(raster)

    def test_heilen_meldet_was_wirklich_geheilt_wurde_und_schadet_nie(self):
        gegner = Gegner("ork", Werkbank("loesung"))
        gegner.erleide_schaden(10, "wucht")
        self.assertEqual(0, gegner.heile(-5))
        self.assertEqual(4, gegner.heile(4))
        self.assertEqual(6, gegner.heile(100))
        dorf = Dorf("normal")
        dorf.erleide_schaden(5)
        self.assertEqual(0, dorf.heile(-3))
        self.assertEqual(5, dorf.heile(100))
        dorf.erleide_schaden(-4)
        self.assertEqual(dorf.max_leben, dorf.leben)

    def test_auch_eine_falsche_schadensrechnung_heilt_keinen_gegner(self):
        werkbank = Werkbank(paket_wie_loesung(self, {"horde": SCHADEN_HEILT}))
        gegner = Gegner("ork", werkbank)
        gegner.leben = 10
        self.assertEqual(0, gegner.erleide_schaden(5, "wucht"))
        self.assertEqual(10, gegner.leben)

    def test_was_ein_spaeterer_teil_des_spiels_ist_meldet_das_deutlich(self):
        spiel = partie(FELD)
        with self.assertRaises(NotImplementedError):
            spiel.starte_welle()


if __name__ == "__main__":
    unittest.main()
