"""Der Ersatz zu Spur C: was das Spiel benutzt, solange die Missionen 11 bis 15 offen sind.

Ein Ersatz ist mit Absicht schwächer als die echte Regel, und man soll das im Spiel sehen.
Jede Klasse hier zeigt darum an einem kleinen Beispiel, wo der Ersatz anders antwortet, als es
die Mission verlangt. Geholt wird jeder Ersatz so, wie ihn auch die Werkbank holt: aus dem
Verzeichnis in ``rudersdorf/ersatz.py``.
"""

import copy
import random
import unittest

from rudersdorf import daten
from rudersdorf.ersatz import ERSATZ, ersatz_fuer
from rudersdorf.werkbank import FAEHIGKEITEN
from tests.missionen.helfer import TestEffekt, TestGegner

# So werden die fünf Effekte erzeugt, im Original wie im Ersatz.
EFFEKTE = {
    "Effekt": (3.0,),
    "Frost": (3.0, 0.5),
    "Gift": (3.0, 4.0),
    "Brand": (3.0, 4.0),
    "Betaeubung": (3.0,),
}
NAMEN = {
    "Effekt": "effekt",
    "Frost": "frost",
    "Gift": "gift",
    "Brand": "brand",
    "Betaeubung": "betaeubung",
}
# So werden die drei Fähigkeiten erzeugt. Der Beschwörer kommt einmal ohne und einmal mit Anzahl.
FAEHIGKEITEN_DER_HORDE = [
    ("Regeneration", (5.0,)),
    ("Heiler", (100.0, 5.0)),
    ("Beschwoerer", (1.0, "ork")),
    ("Beschwoerer", (1.0, "ork", 3)),
]


def hole_ersatz(test, faehigkeit, name):
    """Holt einen Ersatz so, wie ihn die Werkbank holt. Fehlt er, scheitert der Test mit Ansage."""
    test.assertIn(
        name,
        ERSATZ.get(faehigkeit, {}),
        f"Im Verzeichnis ERSATZ fehlt unter {faehigkeit!r} der Eintrag {name!r}.",
    )
    return ersatz_fuer(faehigkeit, name)


class ErsatzVollstaendig(unittest.TestCase):
    """Für jeden Namen einer Fähigkeit gibt es einen Ersatz, sonst bliebe das Spiel stehen."""

    def pruefe_alle_namen(self, faehigkeit):
        for name in FAEHIGKEITEN[faehigkeit]["namen"]:
            ersatz = hole_ersatz(self, faehigkeit, name)
            self.assertTrue(
                callable(ersatz), f"Der Ersatz für {faehigkeit}.{name} lässt sich nicht aufrufen."
            )

    def test_schadensarten_hat_einen_ersatz_fuer_jeden_namen(self):
        self.pruefe_alle_namen("schadensarten")

    def test_effekte_hat_einen_ersatz_fuer_jeden_namen(self):
        self.pruefe_alle_namen("effekte")

    def test_faehigkeiten_hat_einen_ersatz_fuer_jeden_namen(self):
        self.pruefe_alle_namen("faehigkeiten")

    def test_wellen_hat_einen_ersatz_fuer_jeden_namen(self):
        self.pruefe_alle_namen("wellen")

    def test_der_ersatz_fuer_eine_klasse_ist_selbst_eine_klasse(self):
        for faehigkeit, namen in (
            ("effekte", list(EFFEKTE)),
            ("faehigkeiten", ["Regeneration", "Heiler", "Beschwoerer"]),
        ):
            for name in namen:
                self.assertIsInstance(
                    hole_ersatz(self, faehigkeit, name),
                    type,
                    f"Der Ersatz für {faehigkeit}.{name} ist keine Klasse.",
                )


class ErsatzSchadensarten(unittest.TestCase):
    """Ohne Mission 11 zählt jeder Faktor als 1: Jeder Schaden kommt ganz an."""

    def setUp(self):
        self.berechne_schaden = hole_ersatz(self, "schadensarten", "berechne_schaden")

    def test_trotz_resistenz_kommt_der_schaden_ganz_an(self):
        # Mission 11 verlangt hier 8.
        self.assertEqual(self.berechne_schaden(20, "feuer", {"feuer": 0.4}), 20)

    def test_auch_eine_schwaeche_und_eine_volle_abwehr_zaehlen_nicht(self):
        # Mission 11 verlangt hier 30 und 0.
        self.assertEqual(self.berechne_schaden(15, "frost", {"frost": 2.0}), 15)
        self.assertEqual(self.berechne_schaden(50, "gift", {"gift": 0.0}), 50)

    def test_eine_schadensart_ohne_eintrag_kommt_ebenfalls_ganz_an(self):
        self.assertEqual(self.berechne_schaden(12, "pfeil", {}), 12)

    def test_auch_der_ersatz_heilt_nicht_durch_negativen_schaden(self):
        # Schwächer heißt nicht gefährlich: Unter 0 fällt auch der Ersatz nie.
        self.assertEqual(self.berechne_schaden(-10, "feuer", {"feuer": 0.4}), 0)
        self.assertEqual(self.berechne_schaden(-10, "pfeil", {}), 0)
        self.assertEqual(self.berechne_schaden(0, "feuer", {"feuer": 2.0}), 0)

    def test_der_ersatz_laesst_die_resistenzen_wie_sie_waren(self):
        resistenzen = {"feuer": 0.4}
        self.berechne_schaden(20, "pfeil", resistenzen)
        self.assertEqual(resistenzen, {"feuer": 0.4})


class ErsatzEffektklassen(unittest.TestCase):
    """Ohne Mission 12 tun Effekte nichts: Sie bremsen nicht, sie schaden nicht, und sie sind
    von Anfang an vorbei."""

    def erzeuge(self, name):
        return hole_ersatz(self, "effekte", name)(*EFFEKTE[name])

    def test_jeder_ersatzeffekt_laesst_sich_wie_das_original_erzeugen(self):
        for name in EFFEKTE:
            self.assertIsNotNone(self.erzeuge(name), name)

    def test_jeder_ersatzeffekt_traegt_den_namen_des_originals(self):
        for name, erwartet in NAMEN.items():
            self.assertEqual(self.erzeuge(name).name, erwartet, name)

    def test_kein_ersatzeffekt_bremst(self):
        # Mission 12 verlangt bei Frost(3.0, 0.5) den Faktor 0.5 und bei Betaeubung(3.0) den Faktor 0.0.
        for name in EFFEKTE:
            self.assertEqual(self.erzeuge(name).tempo_faktor(), 1.0, name)

    def test_kein_ersatzeffekt_bremst_nachdem_zeit_vergangen_ist(self):
        for name in EFFEKTE:
            effekt = self.erzeuge(name)
            effekt.tick(TestGegner(), 1.0)
            self.assertEqual(effekt.tempo_faktor(), 1.0, name)

    def test_kein_ersatzeffekt_schadet_oder_heilt(self):
        # Mission 12 verlangt bei Gift(3.0, 4.0) nach einer Sekunde 4 Schaden der Art "gift".
        for name in EFFEKTE:
            gegner = TestGegner(leben=50.0, max_leben=100.0)
            effekt = self.erzeuge(name)
            for sekunden in (1.0, 0.5, 5.0, -1.0, 0):
                effekt.tick(gegner, sekunden)
            self.assertEqual(
                (gegner.schaeden, gegner.heilungen, gegner.leben), ([], [], 50.0), name
            )

    def test_jeder_ersatzeffekt_ist_von_anfang_an_vorbei(self):
        # Mission 12 verlangt hier False: Dort wirkt ein Effekt 3 Sekunden lang.
        for name in EFFEKTE:
            effekt = self.erzeuge(name)
            self.assertIs(effekt.ist_vorbei(), True, name)
            effekt.tick(TestGegner(), 1.0)
            self.assertIs(effekt.ist_vorbei(), True, name)


class ErsatzEffektliste(unittest.TestCase):
    """Ohne Mission 13 trägt kein Gegner einen Effekt: Die Liste bleibt leer, und niemand wird
    gebremst."""

    def setUp(self):
        self.fuege_effekt_hinzu = hole_ersatz(self, "effekte", "fuege_effekt_hinzu")
        self.gesamt_tempo_faktor = hole_ersatz(self, "effekte", "gesamt_tempo_faktor")
        self.raeume_effekte_auf = hole_ersatz(self, "effekte", "raeume_effekte_auf")

    def test_der_ersatz_legt_keinen_effekt_in_die_liste(self):
        # Mission 13 verlangt hier, dass der Frost danach in der Liste steht.
        effekte = []
        ergebnis = self.fuege_effekt_hinzu(effekte, TestEffekt("frost", rest=2.0, faktor=0.5))
        self.assertEqual(effekte, [])
        self.assertIsNone(ergebnis)

    def test_der_ersatz_legt_auch_seinen_eigenen_ersatzeffekt_nicht_in_die_liste(self):
        effekte = []
        self.fuege_effekt_hinzu(effekte, hole_ersatz(self, "effekte", "Frost")(2.0, 0.5))
        self.assertEqual(effekte, [])

    def test_der_ersatz_tauscht_keinen_effekt_aus_der_schon_in_der_liste_steht(self):
        # Mission 13 verlangt hier, dass der längere Frost den kürzeren ersetzt.
        alt = TestEffekt("frost", rest=1.0, faktor=0.5)
        effekte = [alt]
        self.fuege_effekt_hinzu(effekte, TestEffekt("frost", rest=2.0, faktor=0.5))
        self.fuege_effekt_hinzu(effekte, TestEffekt("gift", rest=2.0))
        self.assertEqual(effekte, [alt])

    def test_der_ersatz_bremst_auch_mit_einem_frost_in_der_liste_nicht(self):
        # Mission 13 verlangt hier 0.5.
        self.assertEqual(self.gesamt_tempo_faktor([TestEffekt("frost", rest=2.0, faktor=0.5)]), 1.0)
        self.assertEqual(
            self.gesamt_tempo_faktor([TestEffekt("betaeubung", rest=1.0, faktor=0.0)]), 1.0
        )
        self.assertEqual(self.gesamt_tempo_faktor([]), 1.0)

    def test_nach_dem_aufraeumen_des_ersatzes_ist_die_liste_leer(self):
        # Mission 13 verlangt hier, dass der Frost bleibt, weil er noch wirkt.
        frost = TestEffekt("frost", rest=2.0, faktor=0.5)
        vorbei = TestEffekt("gift", rest=0.0)
        self.assertEqual(self.raeume_effekte_auf([frost, vorbei]), [])
        self.assertEqual(self.raeume_effekte_auf([]), [])

    def test_der_ersatz_laesst_die_alte_liste_beim_aufraeumen_und_beim_bremsen_wie_sie_war(self):
        frost = TestEffekt("frost", rest=2.0, faktor=0.5)
        vorbei = TestEffekt("gift", rest=0.0)
        effekte = [frost, vorbei]
        self.raeume_effekte_auf(effekte)
        self.gesamt_tempo_faktor(effekte)
        self.assertEqual(effekte, [frost, vorbei])

    def test_jedes_aufraeumen_liefert_eine_eigene_liste(self):
        erste = self.raeume_effekte_auf([])
        erste.append("verdorben")
        self.assertEqual(self.raeume_effekte_auf([]), [])


class ErsatzFaehigkeiten(unittest.TestCase):
    """Ohne Mission 14 hat niemand eine besondere Fähigkeit: Der Troll heilt sich nicht, der
    Schamane heilt niemanden, und der Orkkönig ruft niemanden herbei."""

    def erzeuge(self, name, argumente):
        return hole_ersatz(self, "faehigkeiten", name)(*argumente)

    def gruppe(self):
        """Ein verwundeter Träger und zwei Verwundete direkt neben ihm."""
        traeger = TestGegner(leben=50.0, max_leben=100.0, x=200.0, y=200.0)
        andere = [
            TestGegner(leben=10.0, max_leben=45.0, x=210.0, y=200.0),
            TestGegner(leben=10.0, max_leben=45.0, x=200.0, y=190.0),
        ]
        return traeger, [andere[0], traeger, andere[1]]

    def test_jede_ersatzfaehigkeit_antwortet_mit_einer_leeren_liste(self):
        # Mission 14 verlangt beim Beschwoerer(1.0, "ork", 3) nach einer Sekunde drei Orks.
        for name, argumente in FAEHIGKEITEN_DER_HORDE:
            traeger, alle = self.gruppe()
            faehigkeit = self.erzeuge(name, argumente)
            for _ in range(5):
                self.assertEqual(faehigkeit.aktualisiere(traeger, alle, 1.0), [], name)

    def test_keine_ersatzfaehigkeit_heilt_oder_verletzt_jemanden(self):
        # Mission 14 verlangt bei Regeneration(5.0) 5 Leben für den Träger und bei
        # Heiler(100.0, 5.0) 5 Leben für jeden der beiden anderen.
        for name, argumente in FAEHIGKEITEN_DER_HORDE:
            traeger, alle = self.gruppe()
            faehigkeit = self.erzeuge(name, argumente)
            for sekunden in (1.0, 0.5, 3.0):
                faehigkeit.aktualisiere(traeger, alle, sekunden)
            for gegner in alle:
                self.assertEqual((gegner.heilungen, gegner.schaeden), ([], []), name)
            self.assertEqual([gegner.leben for gegner in alle], [10.0, 50.0, 10.0], name)

    def test_keine_ersatzfaehigkeit_veraendert_die_liste_aller_gegner(self):
        for name, argumente in FAEHIGKEITEN_DER_HORDE:
            traeger, alle = self.gruppe()
            vorher = list(alle)
            self.erzeuge(name, argumente).aktualisiere(traeger, alle, 1.0)
            self.assertEqual(alle, vorher, name)

    def test_jeder_aufruf_liefert_eine_eigene_liste(self):
        for name, argumente in FAEHIGKEITEN_DER_HORDE:
            traeger, alle = self.gruppe()
            faehigkeit = self.erzeuge(name, argumente)
            faehigkeit.aktualisiere(traeger, alle, 1.0).append("verdorben")
            self.assertEqual(faehigkeit.aktualisiere(traeger, alle, 1.0), [], name)


class ErsatzWellen(unittest.TestCase):
    """Ohne Mission 15 besteht jede Welle nur aus Orks: so viele, wie das Budget bezahlt."""

    def setUp(self):
        self.erzeuge_welle = hole_ersatz(self, "wellen", "erzeuge_welle")
        self.katalog = self.neuer_katalog()

    def neuer_katalog(self):
        """Bei jedem Aufruf frisch, damit kein Test den nächsten stört."""
        return {
            "ork": {"preis": 7, "ab_welle": 1, "boss": False},
            "wolf": {"preis": 6, "ab_welle": 2, "boss": False},
            "kobold": {"preis": 2, "ab_welle": 1, "boss": False},
        }

    def test_der_ersatz_kauft_nur_orks_auch_wenn_andere_arten_frei_sind(self):
        # Mission 15 mischt hier Orks, Wölfe und Kobolde und gibt mehr vom Budget aus.
        for saat in range(1, 11):
            self.assertEqual(
                self.erzeuge_welle(5, 100, self.katalog, random.Random(saat)), ["ork"] * 14
            )

    def test_der_preis_des_orks_kommt_aus_dem_katalog(self):
        katalog = copy.deepcopy(daten.GEGNER)  # eine Kopie, damit die echte Tabelle heil bleibt
        ork = katalog["ork"]["preis"]
        self.assertEqual(
            self.erzeuge_welle(10, 100, katalog, random.Random(1)), ["ork"] * (100 // ork)
        )

    def test_der_ersatz_kauft_auch_dann_keinen_billigeren_wenn_geld_uebrig_bleibt(self):
        # 20 Münzen: zwei Orks zu 7. Mission 15 kauft für die übrigen 6 noch drei Kobolde zu 2
        # oder einen Wolf zu 6.
        self.assertEqual(self.erzeuge_welle(5, 20, self.katalog, random.Random(1)), ["ork", "ork"])

    def test_die_nummer_der_welle_aendert_beim_ersatz_nichts(self):
        for nummer in (1, 2, 30):
            self.assertEqual(
                self.erzeuge_welle(nummer, 21, self.katalog, random.Random(1)), ["ork"] * 3
            )

    def test_reicht_das_budget_fuer_keinen_ork_ist_die_welle_leer(self):
        for budget in (6, 0, -20):
            self.assertEqual(self.erzeuge_welle(5, budget, self.katalog, random.Random(1)), [])

    def test_jeder_aufruf_liefert_eine_eigene_liste(self):
        erste = self.erzeuge_welle(5, 21, self.katalog, random.Random(1))
        erste.append("verdorben")
        self.assertEqual(self.erzeuge_welle(5, 21, self.katalog, random.Random(1)), ["ork"] * 3)

    def test_der_ersatz_laesst_den_katalog_wie_er_war(self):
        self.erzeuge_welle(5, 100, self.katalog, random.Random(1))
        self.assertEqual(self.katalog, self.neuer_katalog())


if __name__ == "__main__":
    unittest.main()
