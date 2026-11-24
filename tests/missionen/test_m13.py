"""Mission 13 · Die Effektliste: Jeder Gegner trägt eine Liste von Effekten, aber keinen doppelt.

Die Tests benutzen eigene kleine Testeffekte. So lässt sich diese Mission prüfen, auch wenn
Mission 12 noch offen ist. Ein Testeffekt hat wie jeder Effekt name, rest, ist_vorbei() und
tempo_faktor().
"""

from tests.missionen import helfer
from tests.missionen.helfer import TestEffekt

TIPP_NIE_DOPPELT = (
    "Such in der Liste nach einem Effekt mit demselben name wie der neue. Gibt es einen, "
    "bleibt es bei einem einzigen Effekt dieser Art: Die Liste wird dabei nicht länger."
)
TIPP_LAENGER_GEWINNT = (
    "Von zwei Effekten mit demselben Namen bleibt der, der noch länger wirkt: Vergleiche "
    "rest (nicht dauer). Ist der neue mindestens so lang, kommt er an den Platz des alten."
)
TIPP_NAME = (
    "Ob zwei Effekte von derselben Art sind, sagt allein ihr name. Verschiedene Namen "
    "stören sich nicht: Dann kommt der neue Effekt hinten an die Liste."
)
TIPP_KLEINSTER = (
    "Der Gegner ist so langsam, wie es der stärkste Bremser will: Gesucht ist der kleinste "
    "tempo_faktor() aller Effekte, die noch nicht vorbei sind."
)
TIPP_OHNE = "Ohne einen Effekt, der noch wirkt, läuft der Gegner normal: Das Ergebnis ist 1.0."
TIPP_NEUE_LISTE = (
    "Bau eine neue Liste und nimm nur die Effekte hinein, die noch nicht vorbei sind. Wer "
    "aus einer Liste löscht, während er sie durchläuft, überspringt Einträge."
)


class Mission13(helfer.Missionstest):
    modul = "horde"

    # --- fuege_effekt_hinzu ------------------------------------------------------------------

    def fuege_hinzu(self, effekte, neu, erwartet, tipp):
        aufruf = f"fuege_effekt_hinzu({effekte}, {neu})"
        ergebnis = self.rufe_sicher(aufruf, tipp, self.werkstatt.fuege_effekt_hinzu, effekte, neu)
        self.pruefe_gleich(effekte, erwartet, f"die Liste nach {aufruf}", tipp)
        return ergebnis

    def test_in_eine_leere_liste_kommt_der_neue_effekt_einfach_hinein(self):
        frost = TestEffekt("frost", rest=2.0)
        self.fuege_hinzu([], frost, [frost], TIPP_NAME)

    def test_ein_laengerer_frost_ersetzt_den_kuerzeren(self):
        alt = TestEffekt("frost", rest=1.0, faktor=0.5)
        neu = TestEffekt("frost", rest=2.0, faktor=0.5)
        self.fuege_hinzu([alt], neu, [neu], TIPP_NIE_DOPPELT + " " + TIPP_LAENGER_GEWINNT)

    def test_ein_kuerzerer_frost_aendert_nichts(self):
        alt = TestEffekt("frost", rest=1.0, faktor=0.5)
        neu = TestEffekt("frost", rest=0.5, faktor=0.5)
        self.fuege_hinzu([alt], neu, [alt], TIPP_NIE_DOPPELT + " " + TIPP_LAENGER_GEWINNT)

    def test_bei_gleichem_rest_gewinnt_der_neue_effekt(self):
        alt = TestEffekt("frost", rest=1.0, faktor=0.5)
        neu = TestEffekt("frost", rest=1.0, faktor=0.3)
        self.fuege_hinzu([alt], neu, [neu], TIPP_LAENGER_GEWINNT)

    def test_ein_effekt_einer_anderen_art_kommt_hinten_dazu(self):
        frost = TestEffekt("frost", rest=1.0, faktor=0.5)
        gift = TestEffekt("gift", rest=3.0)
        self.fuege_hinzu([frost], gift, [frost, gift], TIPP_NAME)

    def test_gift_und_brand_sind_zwei_verschiedene_arten(self):
        gift = TestEffekt("gift", rest=3.0)
        brand = TestEffekt("brand", rest=1.0)
        self.fuege_hinzu([gift], brand, [gift, brand], TIPP_NAME)

    def test_ein_kuerzerer_effekt_einer_anderen_art_kommt_trotzdem_dazu(self):
        frost = TestEffekt("frost", rest=5.0, faktor=0.5)
        betaeubung = TestEffekt("betaeubung", rest=0.5, faktor=0.0)
        self.fuege_hinzu([frost], betaeubung, [frost, betaeubung], TIPP_NAME)

    def test_der_neue_effekt_uebernimmt_den_platz_des_alten(self):
        gift = TestEffekt("gift", rest=3.0)
        alt = TestEffekt("frost", rest=1.0, faktor=0.5)
        betaeubung = TestEffekt("betaeubung", rest=0.5, faktor=0.0)
        neu = TestEffekt("frost", rest=2.0, faktor=0.5)
        self.fuege_hinzu(
            [gift, alt, betaeubung],
            neu,
            [gift, neu, betaeubung],
            "Der neue Effekt kommt genau an die Stelle, an der der alte stand. Die anderen "
            "Effekte bleiben, wo sie sind.",
        )

    def test_die_anderen_effekte_bleiben_wenn_der_neue_zu_kurz_ist(self):
        gift = TestEffekt("gift", rest=3.0)
        alt = TestEffekt("frost", rest=1.0, faktor=0.5)
        neu = TestEffekt("frost", rest=0.5, faktor=0.5)
        self.fuege_hinzu([gift, alt], neu, [gift, alt], TIPP_NIE_DOPPELT)

    def test_verglichen_wird_was_noch_uebrig_ist_und_nicht_die_volle_dauer(self):
        alt = TestEffekt("frost", rest=5.0, faktor=0.5)
        alt.tick(None, 4.0)  # von 5 Sekunden ist nur noch 1 übrig
        neu = TestEffekt("frost", rest=2.0, faktor=0.5)
        self.fuege_hinzu([alt], neu, [neu], TIPP_LAENGER_GEWINNT)

    def test_wer_dreimal_frost_bekommt_traegt_trotzdem_nur_einen(self):
        effekte = []
        erster = TestEffekt("frost", rest=1.0, faktor=0.5)
        zweiter = TestEffekt("frost", rest=3.0, faktor=0.5)
        dritter = TestEffekt("frost", rest=2.0, faktor=0.5)
        for frost in (erster, zweiter, dritter):
            self.rufe_sicher(
                f"fuege_effekt_hinzu({effekte}, {frost})",
                TIPP_NIE_DOPPELT,
                self.werkstatt.fuege_effekt_hinzu,
                effekte,
                frost,
            )
        self.pruefe_gleich(
            effekte,
            [zweiter],
            "die Liste nach drei Frost-Effekten mit dem Rest 1.0, 3.0 und 2.0",
            TIPP_NIE_DOPPELT + " " + TIPP_LAENGER_GEWINNT,
        )

    def test_fuege_effekt_hinzu_aendert_die_liste_und_gibt_nichts_zurueck(self):
        frost = TestEffekt("frost", rest=2.0)
        ergebnis = self.fuege_hinzu([], frost, [frost], TIPP_NAME)
        self.pruefe_gleich(
            ergebnis,
            None,
            "fuege_effekt_hinzu(effekte, neu)",
            "Die Funktion ändert die Liste, die sie bekommt. Zurückgeben muss sie nichts.",
        )

    # --- gesamt_tempo_faktor -----------------------------------------------------------------

    def pruefe_tempo(self, effekte, erwartet, tipp):
        aufruf = f"gesamt_tempo_faktor({effekte})"
        bekommen = self.rufe_sicher(aufruf, tipp, self.werkstatt.gesamt_tempo_faktor, effekte)
        self.pruefe_zahl(bekommen, erwartet, aufruf, tipp)

    def test_ohne_effekte_laeuft_der_gegner_normal(self):
        self.pruefe_tempo([], 1.0, TIPP_OHNE)

    def test_ein_frost_bremst_mit_seinem_faktor(self):
        self.pruefe_tempo([TestEffekt("frost", rest=2.0, faktor=0.5)], 0.5, TIPP_KLEINSTER)

    def test_effekte_ohne_bremse_lassen_das_tempo_normal(self):
        self.pruefe_tempo(
            [TestEffekt("gift", rest=2.0), TestEffekt("brand", rest=1.0)], 1.0, TIPP_OHNE
        )

    def test_von_mehreren_bremsen_zaehlt_die_staerkste(self):
        frost = TestEffekt("frost", rest=2.0, faktor=0.5)
        schlamm = TestEffekt("schlamm", rest=2.0, faktor=0.3)
        gift = TestEffekt("gift", rest=2.0)
        tipp = TIPP_KLEINSTER + " Die Faktoren werden nicht malgenommen und nicht addiert."
        self.pruefe_tempo([frost, schlamm, gift], 0.3, tipp)
        self.pruefe_tempo([schlamm, gift, frost], 0.3, tipp)
        self.pruefe_tempo([gift, frost, schlamm], 0.3, tipp)

    def test_eine_betaeubung_haelt_den_gegner_ganz_an(self):
        frost = TestEffekt("frost", rest=2.0, faktor=0.5)
        betaeubung = TestEffekt("betaeubung", rest=1.0, faktor=0.0)
        self.pruefe_tempo([frost, betaeubung], 0.0, TIPP_KLEINSTER)

    def test_ein_abgelaufener_effekt_bremst_nicht_mehr(self):
        # Der abgelaufene Testeffekt nennt weiter seinen Faktor 0.2. Gefragt werden darf er
        # aber nicht mehr, weil er vorbei ist.
        vorbei = TestEffekt("betaeubung", rest=0.0, faktor=0.2)
        frost = TestEffekt("frost", rest=2.0, faktor=0.5)
        tipp = (
            "Frag einen Effekt erst, ob er vorbei ist. Nur wer noch wirkt, darf mitreden. "
            + TIPP_KLEINSTER
        )
        self.pruefe_tempo([vorbei, frost], 0.5, tipp)
        self.pruefe_tempo([frost, vorbei], 0.5, tipp)

    def test_sind_alle_effekte_abgelaufen_laeuft_der_gegner_normal(self):
        effekte = [
            TestEffekt("frost", rest=0.0, faktor=0.5),
            TestEffekt("betaeubung", rest=0.0, faktor=0.0),
        ]
        self.pruefe_tempo(effekte, 1.0, TIPP_OHNE)

    def test_gesamt_tempo_faktor_laesst_die_liste_wie_sie_war(self):
        effekte = [
            TestEffekt("frost", rest=0.0, faktor=0.5),
            TestEffekt("gift", rest=2.0),
            TestEffekt("betaeubung", rest=1.0, faktor=0.0),
        ]
        vorher = list(effekte)
        self.pruefe_tempo(effekte, 0.0, TIPP_KLEINSTER)
        self.pruefe_unveraendert(
            vorher,
            effekte,
            "die Liste effekte",
            "gesamt_tempo_faktor(effekte)",
            "Diese Funktion liest nur. Aufgeräumt wird in raeume_effekte_auf.",
        )

    # --- raeume_effekte_auf ------------------------------------------------------------------

    def raeume_auf(self, effekte, erwartet, tipp):
        aufruf = f"raeume_effekte_auf({effekte})"
        bekommen = self.rufe_sicher(aufruf, tipp, self.werkstatt.raeume_effekte_auf, effekte)
        self.pruefe_gleich(bekommen, erwartet, aufruf, tipp)
        return bekommen

    def test_abgelaufene_effekte_fehlen_in_der_neuen_liste(self):
        frost = TestEffekt("frost", rest=2.0, faktor=0.5)
        vorbei = TestEffekt("gift", rest=0.0)
        betaeubung = TestEffekt("betaeubung", rest=0.5, faktor=0.0)
        self.raeume_auf([frost, vorbei, betaeubung], [frost, betaeubung], TIPP_NEUE_LISTE)

    def test_die_uebrigen_effekte_bleiben_in_ihrer_reihenfolge(self):
        a = TestEffekt("gift", rest=3.0)
        b = TestEffekt("frost", rest=1.0, faktor=0.5)
        c = TestEffekt("brand", rest=2.0)
        vorbei = TestEffekt("betaeubung", rest=0.0, faktor=0.0)
        self.raeume_auf([a, vorbei, b, c], [a, b, c], TIPP_NEUE_LISTE)

    def test_auch_zwei_abgelaufene_hintereinander_verschwinden_beide(self):
        vorbei_1 = TestEffekt("gift", rest=0.0)
        vorbei_2 = TestEffekt("brand", rest=0.0)
        frost = TestEffekt("frost", rest=2.0, faktor=0.5)
        vorbei_3 = TestEffekt("betaeubung", rest=0.0, faktor=0.0)
        self.raeume_auf([vorbei_1, vorbei_2, frost, vorbei_3], [frost], TIPP_NEUE_LISTE)

    def test_sind_alle_abgelaufen_ist_die_neue_liste_leer(self):
        effekte = [TestEffekt("gift", rest=0.0), TestEffekt("frost", rest=0.0, faktor=0.5)]
        self.raeume_auf(effekte, [], TIPP_NEUE_LISTE)

    def test_aus_einer_leeren_liste_wird_eine_leere_liste(self):
        self.raeume_auf([], [], TIPP_NEUE_LISTE)

    def test_das_ergebnis_ist_eine_neue_liste_auch_wenn_kein_effekt_abgelaufen_ist(self):
        effekte = [TestEffekt("gift", rest=3.0), TestEffekt("frost", rest=1.0, faktor=0.5)]
        bekommen = self.raeume_auf(effekte, list(effekte), TIPP_NEUE_LISTE)
        if bekommen is effekte:
            self.fail(
                helfer.meldung(
                    "raeume_effekte_auf(effekte) liefert eine neue Liste",
                    "genau die Liste, die hineingegeben wurde",
                    "Gib auch dann eine eigene, neue Liste zurück, wenn nichts wegfällt.",
                )
            )

    def test_raeume_effekte_auf_laesst_die_alte_liste_wie_sie_war(self):
        vorbei_1 = TestEffekt("gift", rest=0.0)
        vorbei_2 = TestEffekt("brand", rest=0.0)
        frost = TestEffekt("frost", rest=2.0, faktor=0.5)
        effekte = [vorbei_1, vorbei_2, frost]
        self.raeume_auf(effekte, [frost], TIPP_NEUE_LISTE)
        self.pruefe_unveraendert(
            [vorbei_1, vorbei_2, frost],
            effekte,
            "die Liste effekte",
            "raeume_effekte_auf(effekte)",
            TIPP_NEUE_LISTE,
        )
