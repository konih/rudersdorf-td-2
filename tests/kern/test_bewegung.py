"""Gegner im Spielkern: laufen, abbiegen, Schaden nehmen und am Dorftor durchbrechen.

Die Tests stellen Gegner mit ``Spiel.erzeuge_gegner`` auf das Feld und lassen die Zeit nur mit
``schritt`` vergehen. Eine Welle starten sie nicht: Gegner laufen auch in der Bauphase.
Alle Zahlen kommen aus ``rudersdorf.daten``.
"""

import unittest

from rudersdorf import daten
from rudersdorf.kern.gegner import Gegner
from rudersdorf.werkbank import Werkbank
from tests.kern.helfer import (
    GENAU,
    ereignisse,
    fehler_im_weg,
    ist_dabei,
    laufe,
    mitte,
    partie,
    punkt_auf_weg,
    reich,
    schritte_fuer,
    verfolge,
)

ZELLE = daten.ZELLE
DT = daten.DT

# Ein gerader Gang: Orktor (0, 0), Dorftor (13, 0).
GANG = """
    S............Z
"""
GANG_ZELLEN = [(spalte, 0) for spalte in range(14)]

# Ein Gang mit zwei Ecken. Es gibt nur diesen einen Weg.
ECKE = """
    S...#
    ###.#
    ###.#
    ###...Z
"""
ECKE_ZELLEN = [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (3, 2), (3, 3), (4, 3), (5, 3), (6, 3)]

# Ein Gang mit vier Zellen Sumpf: (3, 0) bis (6, 0).
SUMPF = """
    S..%%%%...Z
"""
SUMPF_ZELLEN = [(spalte, 0) for spalte in range(11)]
SUMPF_PIXEL = 4 * ZELLE

# Eine Felswand mit einer Lücke unten bei (5, 3).
WAND = """
    S....#....
    .....#....
    .....#....
    .........Z
"""

# Oben der kurze Weg, unten ein Umweg. Steht auf (4, 0) ein Bauwerk, bleibt nur der Umweg.
UMWEG = """
    S.......Z
    ##.###.##
    ##.....##
"""
KURZ = [(spalte, 0) for spalte in range(9)]
LANG = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (6, 1), (6, 0)]
LANG = LANG + [(7, 0), (8, 0)]
SPERRE = (4, 0)

# Zwei Zellen vor dem Dorftor (4, 0) beginnt der Test des Durchbruchs.
KURZER_GANG = """
    S...Z
"""

# Der Weg führt unten um den Fels auf (2, 0) herum: 8 Schritte. Die Luftlinie hat 6.
FELS_IM_WEG = """
    S.#...Z
    .......
"""

LAUFENDE = ("ork", "wolf", "oger")


def tempo_von(art):
    return daten.GEGNER[art]["tempo"]


class Kerntest(unittest.TestCase):
    def pruefe_punkt(self, gegner, erwartet, genau=GENAU):
        self.assertAlmostEqual(erwartet[0], gegner.x, delta=genau, msg="x des Gegners")
        self.assertAlmostEqual(erwartet[1], gegner.y, delta=genau, msg="y des Gegners")


class NeuerGegner(Kerntest):
    def test_ein_neuer_gegner_steht_in_der_mitte_seiner_zelle_und_gehoert_zur_partie(self):
        spiel = partie(GANG)
        gegner = spiel.erzeuge_gegner("ork", zelle=(2, 0))
        self.assertIsInstance(gegner, Gegner)
        self.assertTrue(ist_dabei(spiel, gegner), "Der neue Gegner fehlt in spiel.gegner.")
        self.assertEqual(1, len(spiel.gegner))
        self.assertEqual("ork", gegner.art)
        self.assertEqual((2, 0), tuple(gegner.zelle))
        self.pruefe_punkt(gegner, mitte((2, 0)))

    def test_ohne_zelle_erscheint_der_gegner_am_orktor(self):
        spiel = partie(GANG)
        gegner = spiel.erzeuge_gegner("ork")
        self.assertEqual((0, 0), tuple(gegner.zelle))
        self.pruefe_punkt(gegner, mitte((0, 0)))

    def test_der_rest_weg_eines_neuen_gegners_ist_sein_abstand_in_pixeln(self):
        spiel = partie(GANG)
        gegner = spiel.erzeuge_gegner("ork", zelle=(2, 0))
        self.assertEqual(11, spiel.abstaende()[(2, 0)])
        self.assertAlmostEqual(11 * ZELLE, gegner.rest_weg, delta=GENAU)

    def test_ohne_schritt_bewegt_sich_niemand(self):
        spiel = partie(GANG)
        gegner = spiel.erzeuge_gegner("ork", zelle=(2, 0))
        spiel.erzeuge_gegner("wolf", zelle=(5, 0))
        self.pruefe_punkt(gegner, mitte((2, 0)))


class Geradeaus(Kerntest):
    def test_nach_t_sekunden_ist_der_gegner_tempo_mal_t_pixel_weiter(self):
        for art in LAUFENDE:
            with self.subTest(art):
                spiel = partie(GANG)
                gegner = spiel.erzeuge_gegner(art, zelle=(1, 0))
                vorher = gegner.rest_weg
                schritte = schritte_fuer(4.3 * ZELLE, tempo_von(art))
                laufe(spiel, schritte)
                strecke = tempo_von(art) * schritte * DT
                self.pruefe_punkt(gegner, punkt_auf_weg(GANG_ZELLEN[1:], strecke))
                self.assertAlmostEqual(vorher - strecke, gegner.rest_weg, delta=GENAU)

    def test_der_rest_weg_faellt_schritt_fuer_schritt_um_die_gelaufene_strecke(self):
        spiel = partie(GANG)
        gegner = spiel.erzeuge_gegner("ork", zelle=(1, 0))
        vorher = gegner.rest_weg
        for nummer in range(1, 131):
            spiel.schritt(DT)
            self.assertAlmostEqual(
                vorher - tempo_von("ork") * nummer * DT,
                gegner.rest_weg,
                delta=GENAU,
                msg=f"nach {nummer} Schritten",
            )

    def test_die_groesse_der_schritte_aendert_die_strecke_nicht(self):
        # Dreimal dieselbe Zeit, in verschieden großen Schritten gerechnet.
        dauer = 3.0
        for name, dt in [("DT", DT), ("2 DT", 2 * DT), ("LABOR_DT", daten.LABOR_DT)]:
            with self.subTest(name):
                spiel = partie(GANG)
                gegner = spiel.erzeuge_gegner("ork", zelle=(1, 0))
                laufe(spiel, round(dauer / dt), dt)
                strecke = tempo_von("ork") * dauer
                self.pruefe_punkt(gegner, punkt_auf_weg(GANG_ZELLEN[1:], strecke))

    def test_ein_schneller_gegner_kommt_in_derselben_zeit_weiter(self):
        spiel = partie(GANG)
        ork = spiel.erzeuge_gegner("ork", zelle=(1, 0))
        wolf = spiel.erzeuge_gegner("wolf", zelle=(1, 0))
        laufe(spiel, 60)
        self.assertAlmostEqual(
            (tempo_von("wolf") - tempo_von("ork")) * 60 * DT, wolf.x - ork.x, delta=GENAU
        )

    def test_die_zelle_des_gegners_wandert_mit(self):
        spiel = partie(GANG)
        gegner = spiel.erzeuge_gegner("ork", zelle=(1, 0))
        # Nach 3,4 Zellen steht er zwischen den Mitten von (4, 0) und (5, 0).
        laufe(spiel, schritte_fuer(3.4 * ZELLE, tempo_von("ork")))
        self.assertIn(tuple(gegner.zelle), [(4, 0), (5, 0)])
        self.assertEqual((5, 0), tuple(gegner.ziel_zelle))


class UmDieEcke(Kerntest):
    def test_der_gegner_laeuft_von_mitte_zu_mitte_und_nie_schraeg(self):
        spiel = partie(ECKE)
        gegner = spiel.erzeuge_gegner("ork", zelle=(0, 0))
        schritte = schritte_fuer(7.4 * ZELLE, tempo_von("ork"))
        (spur,) = verfolge(spiel, [gegner], schritte)
        self.assertEqual([], spur.neben_der_linie()[:3], "Hier lief der Gegner schräg.")
        self.assertEqual(ECKE_ZELLEN[:8], spur.zellen())

    def test_auch_um_ecken_ist_die_strecke_tempo_mal_zeit(self):
        spiel = partie(ECKE)
        gegner = spiel.erzeuge_gegner("ork", zelle=(0, 0))
        vorher = gegner.rest_weg
        schritte = schritte_fuer(7.4 * ZELLE, tempo_von("ork"))
        laufe(spiel, schritte)
        strecke = tempo_von("ork") * schritte * DT
        self.pruefe_punkt(gegner, punkt_auf_weg(ECKE_ZELLEN, strecke))
        self.assertAlmostEqual(vorher - strecke, gegner.rest_weg, delta=GENAU)

    def test_auch_mit_groben_schritten_schneidet_der_gegner_keine_ecke_ab(self):
        spiel = partie(ECKE)
        gegner = spiel.erzeuge_gegner("wolf", zelle=(0, 0))
        dt = daten.LABOR_DT
        schritte = schritte_fuer(7.4 * ZELLE, tempo_von("wolf"), dt)
        (spur,) = verfolge(spiel, [gegner], schritte, dt)
        self.assertEqual([], spur.neben_der_linie()[:3], "Hier lief der Gegner schräg.")
        self.pruefe_punkt(gegner, punkt_auf_weg(ECKE_ZELLEN, tempo_von("wolf") * schritte * dt))

    def test_der_gegner_nimmt_einen_kuerzesten_weg_durch_die_luecke(self):
        spiel = partie(WAND)
        abstaende = dict(spiel.abstaende())
        gegner = spiel.erzeuge_gegner("wolf", zelle=(0, 0))
        (spur,) = verfolge(spiel, [gegner], schritte_fuer(14 * ZELLE, tempo_von("wolf")))
        zellen = spur.zellen()
        self.assertEqual([], spur.neben_der_linie()[:3], "Hier lief der Gegner schräg.")
        self.assertIsNone(fehler_im_weg(zellen, abstaende))
        self.assertIn((5, 3), zellen, "Der Weg führt durch die Lücke der Felswand.")
        self.assertEqual((0, 0), zellen[0])
        self.assertEqual((9, 3), zellen[-1], "Der Lauf endet erst am Dorftor.")
        self.assertFalse(ist_dabei(spiel, gegner), "Der Gegner kam nie am Dorftor an.")


class WegeDerWerkbank(Kerntest):
    """Den Weg rechnet nicht der Kern aus: Er fragt die Fähigkeit ``wegfindung``."""

    def test_mit_der_loesung_fuehrt_der_weg_um_den_fels_herum(self):
        spiel = partie(FELS_IM_WEG)
        self.assertEqual(8, spiel.abstaende()[(0, 0)])
        self.assertNotIn((2, 0), spiel.abstaende())
        gegner = spiel.erzeuge_gegner("wolf", zelle=(0, 0))
        (spur,) = verfolge(spiel, [gegner], schritte_fuer(10 * ZELLE, tempo_von("wolf")))
        self.assertNotIn((2, 0), spur.zellen(), "Der Gegner lief durch den Fels.")
        self.assertIsNone(fehler_im_weg(spur.zellen(), spiel.abstaende()))
        self.assertFalse(ist_dabei(spiel, gegner), "Der Gegner kam nie am Dorftor an.")

    def test_ist_die_wegfindung_offen_laufen_die_gegner_als_geister_durch_den_fels(self):
        # Der Ersatz der Missionen 2 bis 4 zählt die Luftlinie und läuft durch alles hindurch.
        # Rechnet der Kern die Wege an der Werkbank vorbei selbst aus, fällt das hier auf.
        werkbank = Werkbank("loesung", gesperrt=("wegfindung",))
        spiel = partie(FELS_IM_WEG, werkbank=werkbank)
        self.assertEqual(6, spiel.abstaende()[(0, 0)])
        gegner = spiel.erzeuge_gegner("wolf", zelle=(0, 0))
        (spur,) = verfolge(spiel, [gegner], schritte_fuer(8 * ZELLE, tempo_von("wolf")))
        self.assertEqual([(spalte, 0) for spalte in range(7)], spur.zellen())
        self.assertFalse(ist_dabei(spiel, gegner), "Der Geist kam nie am Dorftor an.")

    def test_auch_den_naechsten_schritt_waehlt_bei_offener_wegfindung_der_ersatz(self):
        # Von (0, 1) aus liegen oben und rechts gleich nah am Ziel. Die Mission 4 ginge nach
        # oben, ihr Ersatz nimmt den erstbesten Nachbarn und geht nach rechts.
        werkbank = Werkbank("loesung", gesperrt=("wegfindung",))
        spiel = partie(FELS_IM_WEG, werkbank=werkbank)
        gegner = spiel.erzeuge_gegner("wolf", zelle=(0, 1))
        (spur,) = verfolge(spiel, [gegner], schritte_fuer(9 * ZELLE, tempo_von("wolf")))
        self.assertEqual([(spalte, 1) for spalte in range(7)] + [(6, 0)], spur.zellen())


class ImSumpf(Kerntest):
    faktor = daten.SUMPF_TEMPO_FAKTOR

    def test_mitten_im_sumpf_ist_der_gegner_nur_halb_so_schnell(self):
        for art in LAUFENDE:
            with self.subTest(art):
                spiel = partie(SUMPF)
                gegner = spiel.erzeuge_gegner(art, zelle=(3, 0))
                vorher = gegner.rest_weg
                tempo = tempo_von(art) * self.faktor
                schritte = schritte_fuer(2.5 * ZELLE, tempo)
                laufe(spiel, schritte)
                strecke = tempo * schritte * DT
                self.pruefe_punkt(gegner, punkt_auf_weg(SUMPF_ZELLEN[3:], strecke))
                self.assertAlmostEqual(vorher - strecke, gegner.rest_weg, delta=GENAU)

    def test_vor_dem_sumpf_laeuft_der_gegner_mit_vollem_tempo(self):
        spiel = partie(SUMPF)
        gegner = spiel.erzeuge_gegner("ork", zelle=(0, 0))
        schritte = schritte_fuer(1.5 * ZELLE, tempo_von("ork"))
        laufe(spiel, schritte)
        self.pruefe_punkt(gegner, punkt_auf_weg(SUMPF_ZELLEN, tempo_von("ork") * schritte * DT))

    def test_hinter_dem_sumpf_laeuft_der_gegner_wieder_mit_vollem_tempo(self):
        # Vier Zellen Sumpf kosten bei halbem Tempo so viel Zeit wie acht Zellen Wiese.
        spiel = partie(SUMPF)
        gegner = spiel.erzeuge_gegner("ork", zelle=(1, 0))
        vorher = gegner.rest_weg
        tempo = tempo_von("ork")
        verlust = SUMPF_PIXEL * (1 / self.faktor - 1)
        schritte = schritte_fuer(7.5 * ZELLE + verlust, tempo)
        laufe(spiel, schritte)
        strecke = tempo * schritte * DT - verlust
        # Wo genau das halbe Tempo beginnt und endet, legt der Plan nicht fest: Darum darf
        # der Gegner hier um die Strecke von zwei Schritten neben der Rechnung stehen.
        spiel_raum = 2 * tempo * DT
        self.pruefe_punkt(gegner, punkt_auf_weg(SUMPF_ZELLEN[1:], strecke), genau=spiel_raum)
        self.assertAlmostEqual(vorher - strecke, gegner.rest_weg, delta=spiel_raum)


class NeuerWeg(Kerntest):
    def setUp(self):
        self.spiel = reich(partie(UMWEG))

    def test_ohne_bauwerk_nimmt_der_gegner_den_kurzen_weg(self):
        gegner = self.spiel.erzeuge_gegner("wolf", zelle=(0, 0))
        (spur,) = verfolge(self.spiel, [gegner], schritte_fuer(10 * ZELLE, tempo_von("wolf")))
        self.assertEqual(KURZ, spur.zellen())

    def test_nach_dem_bauen_auf_dem_weg_nimmt_der_gegner_den_umweg(self):
        gegner = self.spiel.erzeuge_gegner("wolf", zelle=(0, 0))
        laufe(self.spiel, 10)
        self.assertTrue(self.spiel.baue("palisade", SPERRE))
        (spur,) = verfolge(self.spiel, [gegner], schritte_fuer(14 * ZELLE, tempo_von("wolf")))
        self.assertEqual(LANG, spur.zellen())
        self.assertEqual([], spur.neben_der_linie()[:3], "Hier lief der Gegner schräg.")
        self.assertFalse(ist_dabei(self.spiel, gegner), "Der Gegner kam nie am Dorftor an.")

    def test_auch_in_der_phase_welle_darf_gebaut_werden_und_die_gegner_weichen_aus(self):
        # Eine Welle starten kann der Kern erst später. Darum setzt der Test die Phase selbst
        # und hört auf, solange der Gegner noch unterwegs ist: Die Welle endet hier nie.
        gegner = self.spiel.erzeuge_gegner("ork", zelle=(0, 0))
        self.spiel.phase = "welle"
        laufe(self.spiel, 10)
        self.assertIs(
            self.spiel.baue("palisade", SPERRE), True, "Bauen ist auch in der Welle erlaubt."
        )
        (spur,) = verfolge(self.spiel, [gegner], schritte_fuer(6.4 * ZELLE, tempo_von("ork")))
        self.assertEqual(LANG[:8], spur.zellen())
        self.assertEqual([], spur.neben_der_linie()[:3], "Hier lief der Gegner schräg.")
        self.assertTrue(ist_dabei(self.spiel, gegner))
        self.assertEqual("welle", self.spiel.phase)

    def test_der_gegner_beendet_erst_seinen_schritt_und_dreht_dann_um(self):
        # Der Ork ist von (2, 0) nach (3, 0) unterwegs, als (4, 0) zugebaut wird. Der neue Weg
        # führt zurück über (2, 0) und dann nach unten.
        gegner = self.spiel.erzeuge_gegner("ork", zelle=(2, 0))
        laufe(self.spiel, 10)
        self.assertEqual((3, 0), tuple(gegner.ziel_zelle))
        self.assertTrue(self.spiel.baue("palisade", SPERRE))
        (spur,) = verfolge(self.spiel, [gegner], schritte_fuer(16 * ZELLE, tempo_von("ork")))
        self.assertEqual([(2, 0), (3, 0)] + LANG[2:], spur.zellen())
        self.assertEqual([], spur.neben_der_linie()[:3], "Hier lief der Gegner schräg.")
        oben = mitte((3, 0))[1]
        weitester = max(x for x, y in spur.punkte if abs(y - oben) <= GENAU and x < 4 * ZELLE)
        wende = mitte((3, 0))[0]
        self.assertLessEqual(weitester, wende + GENAU, "Er lief über die Mitte von (3, 0) hinaus.")
        self.assertGreaterEqual(
            weitester, wende - tempo_von("ork") * DT, "Er kehrte vor der Mitte von (3, 0) um."
        )

    def test_kein_gegner_betritt_je_die_zugebaute_zelle(self):
        tempo = tempo_von("ork")
        am_tor = self.spiel.erzeuge_gegner("ork", zelle=(0, 0))
        davor = self.spiel.erzeuge_gegner("ork", zelle=(2, 0))
        dahinter = self.spiel.erzeuge_gegner("ork", zelle=(5, 0))
        laufe(self.spiel, 10)
        leben = self.spiel.dorf.leben
        self.assertTrue(self.spiel.baue("palisade", SPERRE))
        spuren = verfolge(self.spiel, [am_tor, davor, dahinter], schritte_fuer(16 * ZELLE, tempo))
        for name, spur in zip(["am Tor", "davor", "dahinter"], spuren, strict=True):
            self.assertNotIn(SPERRE, spur.zellen(), f"Der Ork {name} lief durch das Bauwerk.")
            self.assertEqual([], spur.neben_der_linie()[:3], f"Der Ork {name} lief schräg.")
        self.assertEqual([(5, 0), (6, 0), (7, 0), (8, 0)], spuren[2].zellen())
        self.assertEqual([], list(self.spiel.gegner), "Nicht alle Orks kamen am Dorftor an.")
        self.assertEqual(leben - 3 * daten.GEGNER["ork"]["dorfschaden"], self.spiel.dorf.leben)

    def test_nach_dem_verkauf_nehmen_die_gegner_wieder_den_kurzen_weg(self):
        self.assertTrue(self.spiel.baue("palisade", SPERRE))
        langsam = self.spiel.erzeuge_gegner("ork", zelle=(0, 0))
        laufe(self.spiel, 10)
        self.assertTrue(self.spiel.verkaufe(SPERRE))
        (spur,) = verfolge(self.spiel, [langsam], schritte_fuer(10 * ZELLE, tempo_von("ork")))
        self.assertEqual(KURZ, spur.zellen())

    def test_der_rest_weg_eines_neuen_gegners_zaehlt_den_umweg(self):
        self.assertTrue(self.spiel.baue("palisade", SPERRE))
        gegner = self.spiel.erzeuge_gegner("ork", zelle=(0, 0))
        self.assertAlmostEqual((len(LANG) - 1) * ZELLE, gegner.rest_weg, delta=GENAU)


class Durchbruch(Kerntest):
    def bis_zum_tor(self, art, schwierigkeit="normal"):
        """Stellt einen Gegner zwei Zellen vor das Dorftor und liefert Partie und Gegner."""
        spiel = partie(KURZER_GANG, schwierigkeit=schwierigkeit)
        gegner = spiel.erzeuge_gegner(art, zelle=(2, 0))
        spiel.hole_ereignisse()
        return spiel, gegner

    def test_kurz_vor_der_mitte_des_dorftors_ist_noch_nichts_geschehen(self):
        # Erreicht ist das Dorftor in der Mitte seiner Zelle, nicht schon an ihrem Rand.
        spiel, gegner = self.bis_zum_tor("ork")
        laufe(spiel, schritte_fuer(2 * ZELLE, tempo_von("ork")) - 3)
        self.assertTrue(ist_dabei(spiel, gegner))
        self.assertEqual(spiel.dorf.max_leben, spiel.dorf.leben)
        self.assertEqual([], ereignisse(spiel, "durchbruch"))

    def test_am_dorftor_verliert_das_dorf_den_dorfschaden_des_gegners(self):
        for art in LAUFENDE:
            with self.subTest(art):
                spiel, gegner = self.bis_zum_tor(art)
                leben = spiel.dorf.leben
                laufe(spiel, schritte_fuer(2 * ZELLE, tempo_von(art)) + 2)
                self.assertEqual(leben - daten.GEGNER[art]["dorfschaden"], spiel.dorf.leben)

    def test_nach_dem_durchbruch_ist_der_gegner_weg(self):
        spiel, gegner = self.bis_zum_tor("ork")
        laufe(spiel, schritte_fuer(2 * ZELLE, tempo_von("ork")) + 2)
        self.assertFalse(ist_dabei(spiel, gegner))
        self.assertEqual([], list(spiel.gegner))

    def test_der_durchbruch_wird_als_ereignis_mit_dem_schaden_gemeldet(self):
        spiel, gegner = self.bis_zum_tor("oger")
        laufe(spiel, schritte_fuer(2 * ZELLE, tempo_von("oger")) + 2)
        gemeldet = ereignisse(spiel, "durchbruch")
        self.assertEqual(1, len(gemeldet), "Genau ein Durchbruch soll gemeldet werden.")
        self.assertEqual(daten.GEGNER["oger"]["dorfschaden"], gemeldet[0]["schaden"])

    def test_fuer_einen_durchbruch_gibt_es_keine_belohnung(self):
        spiel, gegner = self.bis_zum_tor("oger")
        vorraete = dict(spiel.dorf.vorraete)
        laufe(spiel, schritte_fuer(2 * ZELLE, tempo_von("oger")) + 2)
        self.assertFalse(ist_dabei(spiel, gegner))
        self.assertEqual(vorraete, dict(spiel.dorf.vorraete))
        self.assertEqual([], ereignisse(spiel, "tod"))

    def test_ein_durchbruch_zaehlt_nur_einmal(self):
        spiel, gegner = self.bis_zum_tor("ork")
        leben = spiel.dorf.leben
        laufe(spiel, schritte_fuer(2 * ZELLE, tempo_von("ork")) + 120)
        self.assertEqual(leben - daten.GEGNER["ork"]["dorfschaden"], spiel.dorf.leben)
        self.assertEqual(1, len(ereignisse(spiel, "durchbruch")))

    def test_ein_gegner_der_auf_dem_dorftor_entsteht_bricht_sofort_durch(self):
        spiel = partie(KURZER_GANG)
        leben = spiel.dorf.leben
        gegner = spiel.erzeuge_gegner("ork", zelle=(4, 0))
        laufe(spiel, 3)
        self.assertFalse(ist_dabei(spiel, gegner))
        self.assertEqual(leben - daten.GEGNER["ork"]["dorfschaden"], spiel.dorf.leben)

    def test_das_leben_des_dorfes_faellt_nie_unter_null(self):
        spiel, gegner = self.bis_zum_tor("oger")
        self.assertGreater(daten.GEGNER["oger"]["dorfschaden"], 1)
        spiel.dorf.leben = 1
        laufe(spiel, schritte_fuer(2 * ZELLE, tempo_von("oger")) + 2)
        self.assertEqual(0, spiel.dorf.leben)


class GegnerWerte(unittest.TestCase):
    def test_jede_art_bekommt_ihre_werte_aus_der_tabelle(self):
        for art, werte in daten.GEGNER.items():
            with self.subTest(art):
                gegner = Gegner(art, Werkbank("loesung"))
                self.assertEqual(art, gegner.art)
                self.assertEqual(werte["name"], gegner.name)
                self.assertEqual(werte["leben"], gegner.leben)
                self.assertEqual(werte["leben"], gegner.max_leben)
                self.assertEqual(werte["tempo"], gegner.tempo)
                self.assertEqual(werte["belohnung"], gegner.belohnung)
                self.assertEqual(werte["dorfschaden"], gegner.dorfschaden)
                self.assertEqual(werte["fliegt"], gegner.fliegt)
                self.assertEqual(werte["boss"], gegner.ist_boss)
                self.assertEqual(werte["bricht"], gegner.bricht)
                self.assertEqual(werte["resistenzen"], gegner.resistenzen)
                self.assertEqual([], list(gegner.effekte))
                self.assertFalse(gegner.ist_besiegt())

    def test_der_lebensfaktor_macht_das_leben_groesser(self):
        gegner = Gegner("ork", Werkbank("loesung"), leben_faktor=1.5)
        self.assertAlmostEqual(daten.GEGNER["ork"]["leben"] * 1.5, gegner.leben)
        self.assertAlmostEqual(daten.GEGNER["ork"]["leben"] * 1.5, gegner.max_leben)

    def test_zwei_gleiche_gegner_sind_trotzdem_zwei_verschiedene(self):
        # Die Missionen suchen einen Gegner mit "in" in einer Liste. Das geht nur gut, wenn
        # zwei Orks mit gleichen Werten nicht als derselbe gelten.
        werkbank = Werkbank("loesung")
        erster = Gegner("ork", werkbank)
        zweiter = Gegner("ork", werkbank)
        self.assertNotEqual(erster, zweiter)
        self.assertEqual(1, [erster, zweiter].count(zweiter))

    def test_die_tabelle_der_resistenzen_bleibt_wie_sie_war(self):
        vorher = dict(daten.GEGNER["schildork"]["resistenzen"])
        gegner = Gegner("schildork", Werkbank("loesung"))
        gegner.erleide_schaden(20, "stich")
        self.assertEqual(vorher, daten.GEGNER["schildork"]["resistenzen"])


class Schaden(unittest.TestCase):
    def setUp(self):
        self.faktor = daten.GEGNER["schildork"]["resistenzen"]["stich"]
        self.gegner = Gegner("schildork", Werkbank("loesung"))
        self.voll = self.gegner.leben

    def test_die_resistenz_laesst_nur_einen_teil_des_schadens_durch(self):
        # Mit den Zahlen des Plans: 20 Stich gegen die Resistenz 0,4 kosten 8 Leben.
        verloren = self.gegner.erleide_schaden(20, "stich")
        self.assertAlmostEqual(20 * self.faktor, verloren)
        self.assertAlmostEqual(self.voll - 20 * self.faktor, self.gegner.leben)
        self.assertNotAlmostEqual(20, verloren, msg="Die Resistenz wurde gar nicht angewendet.")
        self.assertNotAlmostEqual(
            20 * self.faktor * self.faktor, verloren, msg="Die Resistenz wurde doppelt angewendet."
        )

    def test_eine_andere_schadensart_kommt_ganz_an(self):
        verloren = self.gegner.erleide_schaden(20, "wucht")
        self.assertAlmostEqual(20, verloren)
        self.assertAlmostEqual(self.voll - 20, self.gegner.leben)

    def test_eine_schwaeche_kostet_mehr_leben_als_der_schaden(self):
        geist = Gegner("geist", Werkbank("loesung"))
        faktor = daten.GEGNER["geist"]["resistenzen"]["magie"]
        self.assertGreater(faktor, 1)
        self.assertAlmostEqual(20 * faktor, geist.erleide_schaden(20, "magie"))

    def test_das_leben_faellt_nie_unter_null_und_gemeldet_wird_nur_das_verlorene(self):
        self.gegner.erleide_schaden(self.voll - 5, "wucht")
        self.assertFalse(self.gegner.ist_besiegt())
        verloren = self.gegner.erleide_schaden(1000, "wucht")
        self.assertAlmostEqual(5, verloren)
        self.assertEqual(0, self.gegner.leben)
        self.assertTrue(self.gegner.ist_besiegt())

    def test_ein_besiegter_verliert_nichts_mehr(self):
        self.gegner.erleide_schaden(self.voll * 10, "wucht")
        self.assertEqual(0, self.gegner.erleide_schaden(20, "wucht"))
        self.assertEqual(0, self.gegner.leben)

    def test_kein_und_negativer_schaden_aendern_das_leben_nicht(self):
        self.assertEqual(0, self.gegner.erleide_schaden(0, "wucht"))
        self.assertEqual(0, self.gegner.erleide_schaden(-30, "wucht"))
        self.assertEqual(self.voll, self.gegner.leben)

    def test_der_schaden_wird_mit_der_faehigkeit_schadensarten_berechnet(self):
        # Ist die Mission 11 offen, lässt ihr Ersatz jeden Schaden ganz durch. Rechnet der
        # Gegner die Resistenz selbst aus, fällt das hier auf.
        werkbank = Werkbank("loesung", gesperrt=("schadensarten",))
        gegner = Gegner("schildork", werkbank)
        self.assertAlmostEqual(20, gegner.erleide_schaden(20, "stich"))

    def test_heilen_gibt_leben_zurueck_aber_nie_mehr_als_das_volle_leben(self):
        self.gegner.erleide_schaden(30, "wucht")
        self.gegner.heile(10)
        self.assertAlmostEqual(self.voll - 20, self.gegner.leben)
        self.gegner.heile(1000)
        self.assertEqual(self.voll, self.gegner.leben)
        self.assertEqual(self.voll, self.gegner.max_leben)


if __name__ == "__main__":
    unittest.main()
