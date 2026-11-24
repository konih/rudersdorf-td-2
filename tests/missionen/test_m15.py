"""Mission 15 · Die Wellenschmiede: Mit einem Budget werden die Gegner der nächsten Welle gekauft.

Wer genau in einer Welle steht, entscheidet der Zufall. Darum prüfen diese Tests nie eine
bestimmte Welle, sondern das, was für jede richtige Welle gilt, und das gleich für viele
verschiedene Zufallszahlen (jede "Saat" ergibt eine andere Folge von Zufallszahlen).

Hinweis: Hört deine Funktion nie auf zu kaufen, bleibt auch der Test stehen. Dann hilft nur
Strg+C. Schau in dem Fall nach, ob der Preis wirklich vom Rest abgezogen wird.
"""

import copy
import random

from rudersdorf import daten
from tests.missionen import helfer


def neuer_katalog():
    """Ein kleiner Katalog, bei jedem Aufruf frisch, damit kein Test den nächsten stört.

    Der Kobold ist der Billigste, kommt aber erst ab Welle 9. Der König ist billig und von
    Anfang an da, aber ein Boss.
    """
    return {
        "wolf": {"preis": 6, "ab_welle": 2, "boss": False},
        "troll": {"preis": 14, "ab_welle": 4, "boss": False},
        "ork": {"preis": 5, "ab_welle": 1, "boss": False},
        "koenig": {"preis": 3, "ab_welle": 1, "boss": True},
        "kobold": {"preis": 2, "ab_welle": 9, "boss": False},
    }


SAATEN = range(1, 21)

TIPP_ZUFALL = (
    "Wer gekauft wird, entscheidet allein zufall.choice(kandidaten). Benutze nur dieses "
    "zufall, das die Funktion bekommt, und kein eigenes random."
)
TIPP_SORTIERT = (
    "Sortiere die Kandidaten nach ihrem Namen, bevor der Zufall wählt. Dann kommt mit "
    "derselben Saat immer dieselbe Welle heraus, egal wie der Katalog geordnet ist."
)
TIPP_KEINER = (
    "Gibt es keinen Kandidaten, den man bezahlen kann, ist die Welle fertig. Ganz am Anfang "
    "heißt das: eine leere Liste."
)


class Mission15(helfer.Missionstest):
    modul = "horde"

    def welle(self, nummer, budget, saat, katalog=None):
        """Lässt eine Welle erzeugen und prüft sie gleich an allen Regeln."""
        katalog = neuer_katalog() if katalog is None else katalog
        # Geprüft wird mit einer Kopie von vorher: So zählt der Katalog, wie er übergeben wurde.
        vorher = copy.deepcopy(katalog)
        aufruf = f"erzeuge_welle({nummer}, {budget}, katalog, random.Random({saat}))"
        bekommen = self.rufe_sicher(
            aufruf,
            "Lies in der Meldung, in welcher Zeile deiner Funktion der Fehler entsteht.",
            self.werkstatt.erzeuge_welle,
            nummer,
            budget,
            katalog,
            random.Random(saat),
        )
        fehler = helfer.wellenfehler(bekommen, nummer, budget, vorher)
        if fehler is not None:
            erwartet, bekommen_text, tipp = fehler
            self.fail(helfer.meldung(f"{aufruf}: {erwartet}", bekommen_text, tipp))
        return bekommen

    def pruefe_welle(self, nummer, budget, saat, erwartet, tipp, katalog=None):
        bekommen = self.welle(nummer, budget, saat, katalog)
        self.pruefe_gleich(
            bekommen,
            erwartet,
            f"erzeuge_welle({nummer}, {budget}, katalog, random.Random({saat}))",
            tipp,
        )

    # --- die Regeln, für viele Saaten ---------------------------------------------------------

    def test_jede_welle_haelt_alle_regeln_ein(self):
        # Geprüft wird in welle(): eine Liste aus Namen, kein Boss, niemand zu früh, nicht zu
        # teuer und kein Geld übrig, für das es noch einen erlaubten Gegner gäbe.
        for nummer in (1, 2, 3, 4, 5, 9, 12):
            for budget in (5, 11, 23, 40, 97):
                for saat in SAATEN:
                    self.welle(nummer, budget, saat)

    def test_in_keiner_welle_laeuft_ein_boss_mit(self):
        # Der König kostet nur 3 Münzen und ist von Anfang an da. Gekauft wird er trotzdem nie:
        # welle() meldet jeden Boss.
        for nummer in (1, 6):
            for saat in SAATEN:
                self.welle(nummer, 60, saat)

    def test_in_welle_eins_gibt_es_nur_orks(self):
        for saat in SAATEN:
            self.pruefe_welle(
                1,
                23,
                saat,
                ["ork"] * 4,
                "In Welle 1 ist nur der Ork freigeschaltet (und der König, aber der ist ein "
                "Boss). Für 23 Münzen gibt es genau vier Orks zu je 5.",
            )

    def test_wer_genau_in_dieser_welle_frei_wird_laeuft_schon_mit(self):
        arten = set()
        for saat in SAATEN:
            arten.update(self.welle(2, 60, saat))
        self.pruefe_gleich(
            sorted(arten),
            ["ork", "wolf"],
            "die Arten, die in 20 Wellen mit der Nummer 2 vorkommen,",
            'Der Wolf hat "ab_welle" 2. In Welle 2 ist er also dabei: Die Nummer muss '
            "mindestens so groß sein wie ab_welle, gleich groß genügt.",
        )

    def test_das_geld_wird_bis_auf_den_letzten_bezahlbaren_gegner_ausgegeben(self):
        # Hier gibt es nur Orks zu 5 und Trolle zu 14. Ist der Troll zu teuer geworden, passt
        # oft noch ein Ork. welle() meldet, wenn am Ende mehr als 4 Münzen übrig sind.
        katalog = {
            "ork": {"preis": 5, "ab_welle": 1, "boss": False},
            "troll": {"preis": 14, "ab_welle": 1, "boss": False},
        }
        for budget in (19, 33, 47):
            for saat in SAATEN:
                self.welle(3, budget, saat, katalog)

    def test_ein_preis_der_genau_dem_rest_entspricht_wird_noch_bezahlt(self):
        for saat in SAATEN:
            self.pruefe_welle(
                1,
                10,
                saat,
                ["ork", "ork"],
                "Ein Gegner ist bezahlbar, wenn sein Preis höchstens so groß ist wie der "
                "Rest. Genau gleich viel reicht.",
            )

    # --- leere Wellen -------------------------------------------------------------------------

    def test_reicht_das_budget_fuer_niemanden_ist_die_welle_leer(self):
        # 4 Münzen: Der Ork kostet 5. Der Kobold (2) ist noch gesperrt, der König (3) ein Boss.
        for saat in SAATEN:
            self.pruefe_welle(5, 4, saat, [], TIPP_KEINER)

    def test_ohne_budget_ist_die_welle_leer(self):
        self.pruefe_welle(5, 0, 1, [], TIPP_KEINER)

    def test_ist_noch_keine_art_freigeschaltet_ist_die_welle_leer(self):
        self.pruefe_welle(0, 50, 1, [], TIPP_KEINER)

    def test_ein_katalog_nur_aus_bossen_ergibt_eine_leere_welle(self):
        katalog = {"koenig": {"preis": 3, "ab_welle": 1, "boss": True}}
        self.pruefe_welle(5, 50, 1, [], TIPP_KEINER, katalog)

    # --- der Zufall ---------------------------------------------------------------------------

    def test_dieselbe_saat_ergibt_dieselbe_welle(self):
        for saat in SAATEN:
            erste = self.welle(5, 97, saat)
            zweite = self.welle(5, 97, saat)
            if erste != zweite:
                self.fail(
                    helfer.meldung(
                        f"erzeuge_welle(5, 97, katalog, random.Random({saat})) ergibt bei "
                        "jedem Aufruf dieselbe Welle",
                        f"erst {helfer.kurz(erste)}, dann {helfer.kurz(zweite)}",
                        TIPP_ZUFALL,
                    )
                )

    def test_verschiedene_saaten_ergeben_verschiedene_wellen(self):
        wellen = []
        for saat in SAATEN:
            welle = self.welle(5, 97, saat)
            if welle not in wellen:
                wellen.append(welle)
        if len(wellen) < 2:
            self.fail(
                helfer.meldung(
                    "erzeuge_welle(5, 97, katalog, zufall) ergibt mit 20 verschiedenen Saaten "
                    "nicht immer dieselbe Welle",
                    f"zwanzigmal die Welle {helfer.kurz(wellen[0])}",
                    TIPP_ZUFALL,
                )
            )

    def test_jede_erlaubte_art_kommt_irgendwann_an_die_reihe(self):
        arten = set()
        for saat in SAATEN:
            arten.update(self.welle(5, 97, saat))
        self.pruefe_gleich(
            sorted(arten),
            ["ork", "troll", "wolf"],
            "die Arten, die in 20 Wellen mit der Nummer 5 und dem Budget 97 vorkommen,",
            "Jeder Kandidat hat dieselbe Chance. Kaufe nicht immer den billigsten oder den "
            "teuersten. " + TIPP_ZUFALL,
        )

    def test_die_reihenfolge_im_katalog_aendert_die_welle_nicht(self):
        umgekehrt = dict(reversed(list(neuer_katalog().items())))
        for saat in SAATEN:
            normal = self.welle(5, 97, saat)
            anders = self.welle(5, 97, saat, umgekehrt)
            if normal != anders:
                self.fail(
                    helfer.meldung(
                        f"erzeuge_welle(5, 97, katalog, random.Random({saat})) ergibt dieselbe "
                        "Welle, wenn derselbe Katalog nur in anderer Reihenfolge geschrieben ist",
                        f"einmal {helfer.kurz(normal)}, einmal {helfer.kurz(anders)}",
                        TIPP_SORTIERT,
                    )
                )

    # --- der echte Katalog des Spiels ---------------------------------------------------------

    def test_auch_mit_dem_katalog_des_spiels_haelt_jede_welle_die_regeln_ein(self):
        # daten.GEGNER hat zu jeder Art noch viel mehr Einträge. Die stören nicht.
        for nummer in (1, 3, 6, 10, 15, 30):
            for budget in (30, 120, 400):
                for saat in (1, 2, 3):
                    self.welle(nummer, budget, saat, copy.deepcopy(daten.GEGNER))

    # --- nichts verändern ---------------------------------------------------------------------

    def test_erzeuge_welle_laesst_den_katalog_wie_er_war(self):
        katalog = neuer_katalog()
        self.welle(5, 97, 1, katalog)
        self.pruefe_unveraendert(
            neuer_katalog(),
            katalog,
            "der Katalog",
            "erzeuge_welle(5, 97, katalog, zufall)",
            "Lies nur aus dem Katalog. Das Budget, das übrig ist, merkst du dir in einer "
            "eigenen Variablen.",
        )
