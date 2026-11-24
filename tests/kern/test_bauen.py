"""Bauen und Verkaufen im Spielkern, das Sicherheitsnetz und die Kasse des Dorfes.

Wer baut, bezahlt genau einmal und nur, wenn das Bauwerk wirklich steht. Eine Ablehnung
kostet nichts und nennt in ``spiel.meldung`` ihren Grund. Alle Preise kommen aus
``rudersdorf.daten``; Gold und Stein setzen die Tests über ``spiel.dorf.vorraete``.
"""

import copy
import math
import unittest

from rudersdorf import daten
from rudersdorf.kern.bauwerk import Bauwerk
from rudersdorf.kern.dorf import Dorf
from rudersdorf.werkbank import Werkbank
from tests.kern.helfer import ereignisse, laufe, mitte, paket_wie_loesung, partie, reich

# Ein offenes Feld: Orktor (0, 0), Dorftor (9, 2).
FELD = """
    S.........
    ..........
    .........Z
"""
# Mit Palisaden auf (4, 0) und (4, 1) bleibt als einzige Lücke der Wand die Zelle (4, 2).
WAND = [(4, 0), (4, 1)]
LUECKE = (4, 2)

# Jedes Gelände einmal. Der Rest der Karte ist hier Wiese, auch die unterste Zeile.
GELAENDE = """
    S..#~%^..Z
    ..........
"""
NICHT_BEBAUBAR = {
    "Fels": (3, 0),
    "Wasser": (4, 0),
    "Sumpf": (5, 0),
    "Orktor": (0, 0),
    "Dorftor": (9, 0),
    "Dorfgrund am Rand": (18, 1),
    "Dorfgrund in der Ecke": (23, 15),
}
# Python zählt negative Zahlen von hinten: raster[-1][1] ist die Wiese (1, 15). Wer den Rand
# der Karte nicht prüft, baut dort.
AUSSERHALB = {
    "oberhalb": (1, -1),
    "links": (-1, 1),
    "links oben": (-1, -1),
    "rechts": (daten.SPALTEN, 1),
    "unterhalb": (1, daten.ZEILEN),
}

# Eine Nische mit den Zellen (5, 2), (5, 3) und (5, 4); ihr Eingang ist (5, 2).
NISCHE = """
    S........Z
    ..........
    ....#.#...
    ....#.#...
    ....#.#...
    ....###...
"""

# Zwei Orktore, (0, 0) und (0, 3). Jedes erreicht das Feld nur durch eine einzige Zelle:
# das obere durch (1, 0), das untere durch (1, 2).
ZWEI_TORE = """
    S.#......Z
    #.........
    #.########
    S.########
"""
ENGSTELLEN = {"vor dem oberen Orktor": (1, 0), "vor dem unteren Orktor": (1, 2)}

# Ein Gang, der nur eine Zelle breit ist.
GANG = """
    S.......Z
"""

# Oben der kurze Weg (8 Schritte), unten ein Umweg (12 Schritte).
UMWEG = """
    S.......Z
    ##.###.##
    ##.....##
"""

# Ein Hügel auf (3, 0).
HUEGEL = """
    S..^.....Z
    ..........
"""

IMMER_JA = '''
def darf_bauen(raster, zelle, gesperrt, starts, ziel, besetzt):
    """Eine fehlerhafte Bauregel: Sie erlaubt einfach alles."""
    return True
'''

TUERME = [art for art, werte in daten.BAUWERKE.items() if "reichweite" in werte["werte"]]
MIT_STEIN = [art for art, werte in daten.BAUWERKE.items() if werte["kosten"]["stein"] > 0]


def kosten_von(art):
    return daten.BAUWERKE[art]["kosten"]


class Bautest(unittest.TestCase):
    def pruefe_abgelehnt(self, spiel, art, zelle, *woerter):
        """Erwartet, dass ``baue`` ablehnt, nichts kostet und nichts verändert.

        Zurück kommt die Meldung. Die ``woerter`` müssen in ihr stehen.
        """
        spiel.hole_ereignisse()
        vorraete = dict(spiel.dorf.vorraete)
        bauwerke = dict(spiel.bauwerke)
        abstaende = dict(spiel.abstaende())
        meldung = spiel.meldung
        self.assertIs(spiel.baue(art, zelle), False, f"baue({art!r}, {zelle}) muss False liefern")
        self.assertEqual(vorraete, dict(spiel.dorf.vorraete), "Eine Ablehnung kostet nichts.")
        self.assertEqual(bauwerke, dict(spiel.bauwerke), "Nach einer Ablehnung steht nichts Neues.")
        self.assertEqual(abstaende, dict(spiel.abstaende()), "Die Wege bleiben, wie sie waren.")
        self.assertEqual([], ereignisse(spiel, "gebaut"), "Eine Ablehnung meldet kein 'gebaut'.")
        self.assertIsInstance(spiel.meldung, str)
        self.assertNotEqual("", spiel.meldung.strip(), "Die Meldung soll den Grund nennen.")
        self.assertNotEqual(meldung, spiel.meldung, "Die Meldung ist noch die alte.")
        for wort in woerter:
            self.assertIn(wort.lower(), spiel.meldung.lower(), f"Die Meldung soll {wort!r} nennen.")
        return spiel.meldung

    def baue_wand(self, spiel):
        for zelle in WAND:
            self.assertTrue(spiel.baue("palisade", zelle), f"Die Palisade auf {zelle} fehlt.")


class Bauen(Bautest):
    def test_jedes_bauwerk_steht_nach_dem_bauen_auf_seiner_zelle_und_ist_bezahlt(self):
        for art in daten.BAUWERKE:
            with self.subTest(art):
                kosten = kosten_von(art)
                spiel = reich(partie(FELD), gold=kosten["gold"] + 7, stein=kosten["stein"] + 3)
                spiel.hole_ereignisse()
                self.assertIs(spiel.baue(art, (2, 1)), True)
                self.assertEqual(7, spiel.dorf.vorraete["gold"], "Gold nach dem Bauen")
                self.assertEqual(3, spiel.dorf.vorraete["stein"], "Stein nach dem Bauen")
                self.assertEqual([(2, 1)], list(spiel.bauwerke))
                bauwerk = spiel.bauwerke[(2, 1)]
                self.assertIsInstance(bauwerk, Bauwerk)
                self.assertEqual(art, bauwerk.art)
                self.assertEqual((2, 1), tuple(bauwerk.zelle))
                self.assertEqual(mitte((2, 1)), (bauwerk.x, bauwerk.y))
                self.assertEqual(1, bauwerk.stufe)
                self.assertIsNone(bauwerk.meister)
                self.assertEqual(daten.BAUWERKE[art]["werte"], bauwerk.werte)
                self.assertEqual(kosten["gold"], bauwerk.ausgegeben, "ausgegeben zählt das Gold")
                self.assertEqual(1, len(ereignisse(spiel, "gebaut")), "genau ein Ereignis 'gebaut'")

    def test_ein_ereignis_wird_nur_einmal_abgeholt(self):
        spiel = reich(partie(FELD))
        self.assertTrue(spiel.baue("pfeil", (2, 1)))
        self.assertEqual(1, len(ereignisse(spiel, "gebaut")))
        self.assertEqual([], spiel.hole_ereignisse(), "Nach dem Abholen ist die Liste leer.")

    def test_mit_genau_genug_gold_und_stein_bleibt_nichts_uebrig(self):
        for art in daten.BAUWERKE:
            with self.subTest(art):
                kosten = kosten_von(art)
                spiel = reich(partie(FELD), gold=kosten["gold"], stein=kosten["stein"])
                self.assertIs(spiel.baue(art, (2, 1)), True)
                self.assertEqual(0, spiel.dorf.vorraete["gold"])
                self.assertEqual(0, spiel.dorf.vorraete["stein"])

    def test_ohne_ausbau_im_dorf_ist_der_preis_der_aus_der_tabelle(self):
        spiel = partie(FELD)
        for art in daten.BAUWERKE:
            with self.subTest(art):
                self.assertEqual(kosten_von(art), dict(spiel.preis(art)))

    def test_die_werte_des_bauwerks_sind_eine_eigene_kopie_der_tabelle(self):
        spiel = reich(partie(FELD))
        vorher = copy.deepcopy(daten.BAUWERKE["pfeil"])
        self.assertTrue(spiel.baue("pfeil", (2, 1)))
        self.assertIsNot(daten.BAUWERKE["pfeil"]["werte"], spiel.bauwerke[(2, 1)].werte)
        self.assertEqual(vorher, daten.BAUWERKE["pfeil"])

    def test_zwei_bauwerke_stehen_auf_zwei_zellen_und_kosten_zweimal(self):
        spiel = reich(partie(FELD), gold=500, stein=0)
        self.assertTrue(spiel.baue("pfeil", (2, 1)))
        self.assertTrue(spiel.baue("kanone", (6, 1)))
        self.assertEqual({(2, 1), (6, 1)}, set(spiel.bauwerke))
        self.assertEqual("kanone", spiel.bauwerke[(6, 1)].art)
        self.assertIsNot(spiel.bauwerke[(2, 1)].werte, spiel.bauwerke[(6, 1)].werte)
        bezahlt = kosten_von("pfeil")["gold"] + kosten_von("kanone")["gold"]
        self.assertEqual(500 - bezahlt, spiel.dorf.vorraete["gold"])

    def test_ein_bauwerk_versperrt_seine_zelle_fuer_die_gegner(self):
        spiel = reich(partie(FELD))
        self.assertIn((2, 1), spiel.abstaende())
        self.assertTrue(spiel.baue("palisade", (2, 1)))
        self.assertNotIn((2, 1), spiel.abstaende(), "Eine bebaute Zelle hat keinen Abstand mehr.")

    def test_nach_dem_bauen_auf_dem_weg_zaehlt_die_abstandskarte_den_umweg(self):
        spiel = reich(partie(UMWEG))
        self.assertEqual(8, spiel.abstaende()[(0, 0)])
        self.assertTrue(spiel.baue("palisade", (4, 0)))
        self.assertEqual(12, spiel.abstaende()[(0, 0)])

    def test_neben_einem_laufenden_gegner_darf_gebaut_werden(self):
        spiel = reich(partie(FELD))
        spiel.erzeuge_gegner("ork", zelle=(3, 1))
        laufe(spiel, 10)
        self.assertIs(spiel.baue("pfeil", (3, 0)), True)
        self.assertIs(spiel.baue("pfeil", (6, 1)), True)


class Abgelehnt(Bautest):
    def test_auf_gelaende_das_nicht_bebaubar_ist_wird_nicht_gebaut(self):
        for name, zelle in NICHT_BEBAUBAR.items():
            with self.subTest(name):
                self.pruefe_abgelehnt(reich(partie(GELAENDE, rand=".")), "pfeil", zelle)

    def test_ausserhalb_der_karte_wird_nicht_gebaut(self):
        for name, zelle in AUSSERHALB.items():
            with self.subTest(name):
                self.pruefe_abgelehnt(reich(partie(GELAENDE, rand=".")), "pfeil", zelle)

    def test_auf_wiese_und_huegel_derselben_karte_wird_gebaut(self):
        spiel = reich(partie(GELAENDE, rand="."))
        self.assertIs(spiel.baue("pfeil", (6, 0)), True, "auf dem Hügel")
        self.assertIs(spiel.baue("pfeil", (1, 15)), True, "auf der Wiese in der untersten Zeile")

    def test_auf_einer_bebauten_zelle_wird_nicht_noch_einmal_gebaut(self):
        spiel = reich(partie(FELD))
        self.assertTrue(spiel.baue("pfeil", (2, 1)))
        self.pruefe_abgelehnt(spiel, "kanone", (2, 1))
        self.assertEqual("pfeil", spiel.bauwerke[(2, 1)].art)

    def test_mit_zu_wenig_gold_wird_nicht_gebaut(self):
        for art in daten.BAUWERKE:
            with self.subTest(art):
                kosten = kosten_von(art)
                spiel = reich(partie(FELD), gold=kosten["gold"] - 1, stein=kosten["stein"] + 50)
                self.pruefe_abgelehnt(spiel, art, (2, 1), "Gold")

    def test_mit_zu_wenig_stein_wird_nicht_gebaut_und_auch_kein_gold_bezahlt(self):
        self.assertNotEqual([], MIT_STEIN, "Die Tabelle braucht ein Bauwerk, das Stein kostet.")
        for art in MIT_STEIN:
            with self.subTest(art):
                kosten = kosten_von(art)
                spiel = reich(partie(FELD), gold=kosten["gold"] + 500, stein=kosten["stein"] - 1)
                self.pruefe_abgelehnt(spiel, art, (2, 1), "Stein")

    def test_eine_unbekannte_art_wird_nicht_gebaut(self):
        self.pruefe_abgelehnt(reich(partie(FELD)), "drachenturm", (2, 1))

    def test_auf_der_zelle_eines_gegners_wird_nicht_gebaut(self):
        spiel = reich(partie(FELD))
        spiel.erzeuge_gegner("ork", zelle=(3, 1))
        self.pruefe_abgelehnt(spiel, "pfeil", (3, 1))

    def test_auf_der_zelle_in_die_ein_gegner_gerade_laeuft_wird_nicht_gebaut(self):
        # Vom Ork auf (3, 1) aus liegt das Dorftor rechts unten: Er läuft nach rechts oder
        # nach unten. Wohin genau, sagt seine ziel_zelle.
        spiel = reich(partie(FELD))
        gegner = spiel.erzeuge_gegner("ork", zelle=(3, 1))
        laufe(spiel, 10)
        ziel = tuple(gegner.ziel_zelle)
        self.assertIn(ziel, [(4, 1), (3, 2)])
        self.pruefe_abgelehnt(spiel, "pfeil", ziel)

    def test_auch_unterwegs_bleibt_die_zelle_gesperrt_aus_der_der_gegner_kommt(self):
        spiel = reich(partie(FELD))
        spiel.erzeuge_gegner("ork", zelle=(3, 1))
        laufe(spiel, 10)
        self.pruefe_abgelehnt(spiel, "palisade", (3, 1))

    def test_die_letzte_luecke_einer_wand_wird_nicht_geschlossen(self):
        spiel = reich(partie(FELD))
        self.baue_wand(spiel)
        meldung = self.pruefe_abgelehnt(spiel, "palisade", LUECKE, "Weg")
        self.assertNotIn("Mission 5", meldung, "Hier hat die Bauregel selbst abgelehnt.")
        self.assertIn((0, 0), spiel.abstaende(), "Das Orktor braucht weiter einen Weg.")

    def test_neben_der_letzten_luecke_darf_weiter_gebaut_werden(self):
        spiel = reich(partie(FELD))
        self.baue_wand(spiel)
        self.assertIs(spiel.baue("palisade", (5, 1)), True)
        self.assertIs(spiel.baue("pfeil", (3, 1)), True)

    def test_ein_gang_von_einer_zelle_breite_wird_nicht_zugebaut(self):
        self.pruefe_abgelehnt(reich(partie(GANG)), "palisade", (4, 0), "Weg")

    def test_bei_zwei_orktoren_wird_keines_von_beiden_abgeschnitten(self):
        for name, zelle in ENGSTELLEN.items():
            with self.subTest(name):
                spiel = reich(partie(ZWEI_TORE))
                meldung = self.pruefe_abgelehnt(spiel, "palisade", zelle, "Weg")
                self.assertNotIn("Mission 5", meldung, "Hier hat die Bauregel selbst abgelehnt.")

    def test_bei_zwei_orktoren_darf_gebaut_werden_wenn_beide_ihren_weg_behalten(self):
        self.assertIs(reich(partie(ZWEI_TORE)).baue("palisade", (5, 1)), True)

    def test_ein_gegner_in_der_nische_wird_nicht_eingesperrt(self):
        spiel = reich(partie(NISCHE))
        spiel.erzeuge_gegner("ork", zelle=(5, 4))
        meldung = self.pruefe_abgelehnt(spiel, "palisade", (5, 2), "Weg")
        self.assertNotIn("Mission 5", meldung, "Hier hat die Bauregel selbst abgelehnt.")

    def test_ist_die_nische_leer_darf_ihr_eingang_zugebaut_werden(self):
        spiel = reich(partie(NISCHE))
        self.assertIs(spiel.baue("palisade", (5, 2)), True)

    def test_verschiedene_gruende_haben_verschiedene_meldungen(self):
        gruende = {}
        gruende["Fels"] = self.pruefe_abgelehnt(reich(partie(GELAENDE, rand=".")), "pfeil", (3, 0))
        spiel = reich(partie(FELD))
        spiel.erzeuge_gegner("ork", zelle=(3, 1))
        gruende["Gegner"] = self.pruefe_abgelehnt(spiel, "pfeil", (3, 1))
        gruende["kein Weg"] = self.pruefe_abgelehnt(reich(partie(GANG)), "palisade", (4, 0))
        arm = reich(partie(FELD), gold=0)
        gruende["kein Gold"] = self.pruefe_abgelehnt(arm, "pfeil", (2, 1))
        self.assertEqual(
            len(gruende), len(set(gruende.values())), f"Zwei Gründe, ein Satz: {gruende}"
        )


class Sicherheitsnetz(Bautest):
    """Auch eine falsche oder fehlende Bauregel darf den Orks nie den Weg nehmen."""

    def jasager(self):
        werkbank = Werkbank(paket_wie_loesung(self, {"raster": IMMER_JA}))
        self.assertEqual(Werkbank("loesung").offene(), werkbank.offene())
        return werkbank

    def test_sagt_die_bauregel_immer_ja_bleibt_die_letzte_luecke_trotzdem_offen(self):
        spiel = reich(partie(FELD, werkbank=self.jasager()))
        self.baue_wand(spiel)
        self.pruefe_abgelehnt(spiel, "palisade", LUECKE, "Mission 5")
        self.assertIn((0, 0), spiel.abstaende(), "Das Orktor braucht weiter einen Weg.")

    def test_sagt_die_bauregel_immer_ja_wird_trotzdem_kein_gegner_eingesperrt(self):
        spiel = reich(partie(NISCHE, werkbank=self.jasager()))
        gegner = spiel.erzeuge_gegner("ork", zelle=(5, 4))
        self.pruefe_abgelehnt(spiel, "palisade", (5, 2), "Mission 5")
        self.assertIn(tuple(gegner.zelle), spiel.abstaende())

    def test_sagt_die_bauregel_immer_ja_wird_trotzdem_kein_orktor_abgeschnitten(self):
        for name, zelle in ENGSTELLEN.items():
            with self.subTest(name):
                spiel = reich(partie(ZWEI_TORE, werkbank=self.jasager()))
                self.pruefe_abgelehnt(spiel, "palisade", zelle, "Mission 5")
                for start in spiel.karte.starts:
                    self.assertIn(tuple(start), spiel.abstaende())

    def test_das_netz_lehnt_nichts_ab_was_die_wege_offen_laesst(self):
        spiel = reich(partie(FELD, werkbank=self.jasager()))
        self.baue_wand(spiel)
        self.assertIs(spiel.baue("palisade", (5, 1)), True)
        self.assertNotIn("Mission 5", spiel.meldung)

    def test_auch_der_ersatz_der_bauregel_kann_einen_gang_nicht_zubauen(self):
        # Der Ersatz der Mission 5 schaut nicht auf die Wege: Frei stehende Bauwerke erlaubt
        # er überall. Den Gang hält dann allein das Netz offen.
        werkbank = Werkbank("loesung", gesperrt=("bauregel",))
        spiel = reich(partie(GANG, werkbank=werkbank))
        self.pruefe_abgelehnt(spiel, "palisade", (4, 0))
        self.assertIn((0, 0), spiel.abstaende(), "Das Orktor braucht weiter einen Weg.")


class AufDemHuegel(Bautest):
    def test_ein_turm_auf_dem_huegel_schiesst_weiter(self):
        for art in TUERME:
            with self.subTest(art):
                spiel = reich(partie(HUEGEL))
                self.assertTrue(spiel.baue(art, (3, 0)))
                grund = daten.BAUWERKE[art]["werte"]["reichweite"]
                werte = spiel.bauwerke[(3, 0)].werte
                self.assertAlmostEqual(grund * daten.HUEGEL_REICHWEITE_FAKTOR, werte["reichweite"])
                ohne = {name: wert for name, wert in werte.items() if name != "reichweite"}
                erwartet = dict(daten.BAUWERKE[art]["werte"])
                del erwartet["reichweite"]
                self.assertEqual(erwartet, ohne, "Nur die Reichweite wächst auf dem Hügel.")

    def test_auf_der_wiese_bleibt_die_reichweite_wie_in_der_tabelle(self):
        spiel = reich(partie(HUEGEL))
        self.assertTrue(spiel.baue("pfeil", (4, 0)))
        self.assertEqual(
            daten.BAUWERKE["pfeil"]["werte"]["reichweite"],
            spiel.bauwerke[(4, 0)].werte["reichweite"],
        )

    def test_der_huegel_aendert_die_tabelle_nicht(self):
        vorher = copy.deepcopy(daten.BAUWERKE)
        spiel = reich(partie(HUEGEL))
        self.assertTrue(spiel.baue("pfeil", (3, 0)))
        self.assertEqual(vorher, daten.BAUWERKE)

    def test_eine_palisade_auf_dem_huegel_hat_weiter_keine_werte(self):
        spiel = reich(partie(HUEGEL))
        self.assertTrue(spiel.baue("palisade", (3, 0)))
        self.assertEqual({}, spiel.bauwerke[(3, 0)].werte)

    def test_ein_bauwerk_laesst_sich_auch_allein_fuer_den_huegel_erzeugen(self):
        grund = daten.BAUWERKE["frost"]["werte"]["reichweite"]
        unten = Bauwerk("frost", (2, 3))
        oben = Bauwerk("frost", (2, 3), auf_huegel=True)
        self.assertEqual("frost", oben.art)
        self.assertEqual((2, 3), tuple(oben.zelle))
        self.assertEqual(mitte((2, 3)), (oben.x, oben.y))
        self.assertEqual(grund, unten.werte["reichweite"])
        self.assertAlmostEqual(grund * daten.HUEGEL_REICHWEITE_FAKTOR, oben.werte["reichweite"])


class Verkaufen(Bautest):
    def test_der_verkauf_bringt_den_anteil_des_ausgegebenen_goldes_abgerundet(self):
        spiel = reich(partie(FELD), gold=1000, stein=100)
        self.assertTrue(spiel.baue("pfeil", (2, 1)))
        # So viel Gold steckt nach einem Ausbau im Turm. Der Betrag ist so gewählt, dass der
        # Anteil davon keine glatte Zahl ist und beim Runden nach oben ginge.
        betrag = next(n for n in range(91, 400) if (daten.VERKAUF_ANTEIL * n) % 1 >= 0.5)
        spiel.bauwerke[(2, 1)].ausgegeben = betrag
        gold = spiel.dorf.vorraete["gold"]
        self.assertIs(spiel.verkaufe((2, 1)), True)
        zurueck = math.floor(daten.VERKAUF_ANTEIL * betrag)
        self.assertEqual(gold + zurueck, spiel.dorf.vorraete["gold"])

    def test_jedes_bauwerk_bringt_beim_verkauf_den_anteil_seines_kaufpreises(self):
        for art in daten.BAUWERKE:
            with self.subTest(art):
                spiel = reich(partie(FELD), gold=1000, stein=100)
                self.assertTrue(spiel.baue(art, (2, 1)))
                gold = spiel.dorf.vorraete["gold"]
                self.assertIs(spiel.verkaufe((2, 1)), True)
                zurueck = math.floor(daten.VERKAUF_ANTEIL * kosten_von(art)["gold"])
                self.assertEqual(gold + zurueck, spiel.dorf.vorraete["gold"])

    def test_stein_gibt_es_beim_verkauf_nicht_zurueck(self):
        self.assertNotEqual([], MIT_STEIN, "Die Tabelle braucht ein Bauwerk, das Stein kostet.")
        for art in MIT_STEIN:
            with self.subTest(art):
                spiel = reich(partie(FELD), gold=1000, stein=100)
                self.assertTrue(spiel.baue(art, (2, 1)))
                self.assertTrue(spiel.verkaufe((2, 1)))
                self.assertEqual(100 - kosten_von(art)["stein"], spiel.dorf.vorraete["stein"])

    def test_nach_dem_verkauf_ist_die_zelle_frei_und_wieder_bebaubar(self):
        spiel = reich(partie(FELD))
        self.assertTrue(spiel.baue("pfeil", (2, 1)))
        spiel.hole_ereignisse()
        self.assertTrue(spiel.verkaufe((2, 1)))
        self.assertEqual({}, dict(spiel.bauwerke))
        self.assertEqual(1, len(ereignisse(spiel, "verkauft")), "genau ein Ereignis 'verkauft'")
        self.assertIs(spiel.baue("kanone", (2, 1)), True)

    def test_nach_dem_verkauf_gilt_wieder_der_kurze_weg(self):
        spiel = reich(partie(UMWEG))
        vorher = dict(spiel.abstaende())
        self.assertTrue(spiel.baue("palisade", (4, 0)))
        self.assertNotEqual(vorher, dict(spiel.abstaende()))
        self.assertTrue(spiel.verkaufe((4, 0)))
        self.assertEqual(vorher, dict(spiel.abstaende()), "Die Wege wurden nicht neu berechnet.")

    def test_nach_dem_verkauf_der_wand_darf_die_luecke_bebaut_werden(self):
        spiel = reich(partie(FELD))
        self.baue_wand(spiel)
        self.assertIs(spiel.baue("palisade", LUECKE), False)
        self.assertTrue(spiel.verkaufe(WAND[0]))
        self.assertIs(spiel.baue("palisade", LUECKE), True)

    def test_auf_einer_leeren_zelle_gibt_es_nichts_zu_verkaufen(self):
        for name, zelle in [("Wiese", (2, 1)), ("Fels", (12, 5)), ("außerhalb", (-1, 40))]:
            with self.subTest(name):
                spiel = reich(partie(FELD))
                self.assertTrue(spiel.baue("pfeil", (6, 1)))
                spiel.hole_ereignisse()
                vorraete = dict(spiel.dorf.vorraete)
                self.assertIs(spiel.verkaufe(zelle), False)
                self.assertEqual(vorraete, dict(spiel.dorf.vorraete))
                self.assertEqual([(6, 1)], list(spiel.bauwerke))
                self.assertEqual([], ereignisse(spiel, "verkauft"))

    def test_ein_bauwerk_laesst_sich_nur_einmal_verkaufen(self):
        spiel = reich(partie(FELD))
        self.assertTrue(spiel.baue("pfeil", (2, 1)))
        self.assertTrue(spiel.verkaufe((2, 1)))
        gold = spiel.dorf.vorraete["gold"]
        self.assertIs(spiel.verkaufe((2, 1)), False)
        self.assertEqual(gold, spiel.dorf.vorraete["gold"])


class Dorfkasse(unittest.TestCase):
    def test_das_dorf_beginnt_mit_leben_und_vorraeten_seines_schwierigkeitsgrads(self):
        for name, werte in daten.SCHWIERIGKEIT.items():
            with self.subTest(name):
                dorf = Dorf(name)
                self.assertEqual(werte["dorf_leben"], dorf.leben)
                self.assertEqual(werte["dorf_leben"], dorf.max_leben)
                self.assertEqual({"gold", "stein", "mana"}, set(dorf.vorraete))
                self.assertEqual(werte["start"]["gold"], dorf.vorraete["gold"])
                self.assertEqual(werte["start"]["stein"], dorf.vorraete["stein"])

    def test_die_starttabelle_bleibt_wie_sie_war(self):
        vorher = copy.deepcopy(daten.SCHWIERIGKEIT)
        dorf = Dorf("normal")
        dorf.vorraete["gold"] = 0
        self.assertTrue(dorf.bezahle({"gold": 0, "stein": 1}))
        self.assertEqual(vorher, daten.SCHWIERIGKEIT)

    def test_bezahlen_zieht_gold_und_stein_ab(self):
        dorf = Dorf("normal")
        dorf.vorraete["gold"] = 100
        dorf.vorraete["stein"] = 20
        kosten = {"gold": 60, "stein": 5}
        self.assertTrue(dorf.kann_bezahlen(kosten))
        self.assertIs(dorf.bezahle(kosten), True)
        self.assertEqual(40, dorf.vorraete["gold"])
        self.assertEqual(15, dorf.vorraete["stein"])
        self.assertEqual({"gold": 60, "stein": 5}, kosten, "Die Kosten bleiben, wie sie waren.")

    def test_genau_passende_vorraete_reichen(self):
        dorf = Dorf("normal")
        dorf.vorraete["gold"] = 60
        dorf.vorraete["stein"] = 5
        self.assertTrue(dorf.kann_bezahlen({"gold": 60, "stein": 5}))
        self.assertIs(dorf.bezahle({"gold": 60, "stein": 5}), True)
        self.assertEqual(0, dorf.vorraete["gold"])
        self.assertEqual(0, dorf.vorraete["stein"])

    def test_fehlt_gold_oder_stein_wird_gar_nichts_abgezogen(self):
        for name, kosten in [
            ("Gold fehlt", {"gold": 101, "stein": 5}),
            ("Stein fehlt", {"gold": 60, "stein": 21}),
            ("beides fehlt", {"gold": 101, "stein": 21}),
        ]:
            with self.subTest(name):
                dorf = Dorf("normal")
                dorf.vorraete["gold"] = 100
                dorf.vorraete["stein"] = 20
                self.assertFalse(dorf.kann_bezahlen(kosten))
                self.assertIs(dorf.bezahle(kosten), False)
                self.assertEqual(100, dorf.vorraete["gold"])
                self.assertEqual(20, dorf.vorraete["stein"])

    def test_fragen_kostet_nichts(self):
        dorf = Dorf("normal")
        vorher = dict(dorf.vorraete)
        dorf.kann_bezahlen({"gold": 1, "stein": 1})
        self.assertEqual(vorher, dict(dorf.vorraete))

    def test_schaden_zieht_leben_ab_aber_nie_unter_null(self):
        dorf = Dorf("normal")
        voll = dorf.leben
        dorf.erleide_schaden(3)
        self.assertEqual(voll - 3, dorf.leben)
        dorf.erleide_schaden(voll * 2)
        self.assertEqual(0, dorf.leben)
        self.assertEqual(voll, dorf.max_leben)

    def test_heilen_gibt_leben_zurueck_aber_nie_mehr_als_das_volle_leben(self):
        dorf = Dorf("normal")
        voll = dorf.leben
        dorf.erleide_schaden(5)
        dorf.heile(2)
        self.assertEqual(voll - 3, dorf.leben)
        dorf.heile(100)
        self.assertEqual(voll, dorf.leben)


if __name__ == "__main__":
    unittest.main()
