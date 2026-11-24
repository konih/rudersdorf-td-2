"""Mission 2 · Nachbarn: Welche Zellen liegen neben einer Zelle, und wo kann ein Ork laufen?"""

from tests.missionen import helfer

# Die Karte für nachbarn ist 4 Zellen breit und 3 Zellen hoch:
#
#     spalte   0 1 2 3
#     zeile 0  . . . .
#     zeile 1  . . . .
#     zeile 2  . . . .
BREITE = 4
HOEHE = 3

# Die Karte für ist_begehbar. "." Wiese, "%" Sumpf, "^" Hügel, "S" Orktor, "Z" Dorftor,
# "#" Fels, "~" Wasser, "D" Dorfgrund.
GELAENDE = """
    S.#~
    .%^Z
    ...D
"""

TIPP_REIHENFOLGE = "Die Reihenfolge ist immer: oben, rechts, unten, links."
TIPP_RAND = (
    "Am Rand fehlen Nachbarn. Erlaubt sind nur die Spalten 0 bis breite - 1 "
    "und die Zeilen 0 bis hoehe - 1."
)
TIPP_BEGEHBAR = "Welche Zeichen begehbar sind, steht in BEGEHBAR aus rudersdorf.daten."
TIPP_AUSSERHALB = (
    "Prüfe zuerst, ob die Zelle überhaupt auf der Karte liegt. Vorsicht: Eine negative Zahl "
    "ist für Python kein Fehler, raster[-1] ist die letzte Zeile."
)


class Mission02(helfer.Missionstest):
    def pruefe_nachbarn(self, zelle, erwartet):
        aufruf = f"nachbarn({zelle}, {BREITE}, {HOEHE})"
        bekommen = self.rufe_sicher(
            aufruf, TIPP_RAND, self.werkstatt.nachbarn, zelle, BREITE, HOEHE
        )
        tipp = TIPP_RAND
        if helfer.nur_die_reihenfolge_ist_anders(bekommen, erwartet):
            tipp = TIPP_REIHENFOLGE
        self.pruefe_gleich(bekommen, erwartet, aufruf, tipp)

    # ----- nachbarn -----

    def test_eine_zelle_in_der_mitte_hat_vier_nachbarn_oben_rechts_unten_links(self):
        self.pruefe_nachbarn((1, 1), [(1, 0), (2, 1), (1, 2), (0, 1)])

    def test_die_ecke_oben_links_hat_nur_zwei_nachbarn(self):
        self.pruefe_nachbarn((0, 0), [(1, 0), (0, 1)])

    def test_die_ecke_unten_rechts_hat_nur_zwei_nachbarn(self):
        self.pruefe_nachbarn((3, 2), [(3, 1), (2, 2)])

    def test_eine_zelle_am_oberen_rand_hat_drei_nachbarn(self):
        self.pruefe_nachbarn((1, 0), [(2, 0), (1, 1), (0, 0)])

    def test_eine_zelle_am_rechten_rand_hat_drei_nachbarn(self):
        self.pruefe_nachbarn((3, 1), [(3, 0), (3, 2), (2, 1)])

    def test_eine_zelle_am_unteren_rand_hat_drei_nachbarn(self):
        self.pruefe_nachbarn((2, 2), [(2, 1), (3, 2), (1, 2)])

    def test_auf_einer_karte_aus_einer_einzigen_zelle_gibt_es_keine_nachbarn(self):
        self.pruefe_gleich(
            self.werkstatt.nachbarn((0, 0), 1, 1), [], "nachbarn((0, 0), 1, 1)", TIPP_RAND
        )

    # ----- ist_begehbar -----

    def pruefe_begehbar(self, zelle, gesperrt, erwartet, tipp):
        raster = helfer.raster_aus(GELAENDE)
        aufruf = f"ist_begehbar(raster, {zelle}, {gesperrt})"
        bekommen = self.rufe_sicher(
            aufruf, tipp, self.werkstatt.ist_begehbar, raster, zelle, gesperrt
        )
        self.pruefe_gleich(bekommen, erwartet, aufruf, tipp)

    def test_wiese_sumpf_huegel_und_die_beiden_tore_sind_begehbar(self):
        for zelle in [(1, 0), (1, 1), (2, 1), (0, 0), (3, 1)]:
            self.pruefe_begehbar(zelle, set(), True, TIPP_BEGEHBAR)

    def test_fels_wasser_und_dorfgrund_sind_nicht_begehbar(self):
        for zelle in [(2, 0), (3, 0), (3, 2)]:
            self.pruefe_begehbar(zelle, set(), False, TIPP_BEGEHBAR)

    def test_eine_gesperrte_wiese_ist_nicht_begehbar(self):
        self.pruefe_begehbar(
            (1, 0),
            {(1, 0)},
            False,
            "In gesperrt stehen die Zellen, auf denen ein Bauwerk steht. "
            "Dort kommt kein Ork durch, auch wenn darunter Wiese ist.",
        )

    def test_neben_einer_gesperrten_zelle_bleibt_die_wiese_begehbar(self):
        self.pruefe_begehbar(
            (0, 1), {(1, 0)}, True, "Gesperrt ist nur genau die Zelle, die in gesperrt steht."
        )

    def test_links_und_oberhalb_der_karte_ist_nichts_begehbar(self):
        for zelle in [(-1, 1), (0, -1)]:
            self.pruefe_begehbar(zelle, set(), False, TIPP_AUSSERHALB)

    def test_rechts_und_unterhalb_der_karte_ist_nichts_begehbar(self):
        for zelle in [(4, 1), (0, 3), (4, 3)]:
            self.pruefe_begehbar(zelle, set(), False, TIPP_AUSSERHALB)

    def test_ist_begehbar_laesst_raster_und_gesperrt_wie_sie_waren(self):
        raster = helfer.raster_aus(GELAENDE)
        gesperrt = {(1, 0)}
        self.werkstatt.ist_begehbar(raster, (1, 0), gesperrt)
        self.werkstatt.ist_begehbar(raster, (0, 1), gesperrt)
        tipp = "ist_begehbar schaut nur nach. Es ändert weder das Raster noch gesperrt."
        self.pruefe_unveraendert(
            helfer.raster_aus(GELAENDE), raster, "das Raster", "ist_begehbar(...)", tipp
        )
        self.pruefe_unveraendert({(1, 0)}, gesperrt, "gesperrt", "ist_begehbar(...)", tipp)
