"""Mission 10 · Die Turmschmiede: Aus den Werten eines Turms werden die verbesserten berechnet."""

from rudersdorf.fehler import NochOffen
from tests.missionen import helfer

TIPP_ZEICHEN = (
    'Jeder Eintrag im Ausbau ist ein Paar aus Zeichen und Zahl: "+" zählt die Zahl dazu, '
    '"*" nimmt den Wert mit der Zahl mal, "=" setzt den Wert auf die Zahl.'
)
TIPP_KOPIE = (
    "Die Werte gehören dem Turm und sind nur geliehen. Mach als Erstes eine Kopie "
    "(dict(werte) oder werte.copy()), ändere nur die Kopie und gib sie zurück."
)
TIPP_UNBEKANNT = (
    'Es gibt nur die drei Zeichen "+", "*" und "=". Bei jedem anderen Zeichen stimmt etwas '
    "nicht mit dem Ausbau: Melde das mit raise ValueError(...)."
)
TIPP_FEHLT = (
    "Zu einem Wert, den es nicht gibt, kann man nichts dazuzählen und ihn nicht malnehmen. "
    'Prüfe bei "+" und "*" zuerst, ob der Schlüssel in den Werten steht, und melde sonst '
    'einen ValueError. Nur "=" darf einen neuen Wert anlegen.'
)


def turmwerte():
    """Die Werte eines Turms, wie das Spiel sie an die Schmiede gibt."""
    return {"schaden": 10, "reichweite": 120.0, "pause": 0.8}


class Mission10(helfer.Missionstest):
    modul = "tuerme"

    def pruefe_ausbau(self, ausbau, erwartet, tipp):
        werte = turmwerte()
        self.pruefe_gleich(
            self.werkstatt.wende_ausbau_an(werte, ausbau),
            erwartet,
            f"wende_ausbau_an({werte}, {ausbau})",
            tipp,
        )

    def pruefe_wertfehler(self, ausbau, tipp):
        werte = turmwerte()
        self.pruefe_fehler(
            ValueError,
            f"wende_ausbau_an({werte}, {ausbau})",
            tipp,
            self.werkstatt.wende_ausbau_an,
            werte,
            ausbau,
        )

    # --- die drei Zeichen ---------------------------------------------------------------------

    def test_plus_zaehlt_die_zahl_zum_wert_dazu(self):
        self.pruefe_ausbau(
            {"schaden": ("+", 5)},
            {"schaden": 15, "reichweite": 120.0, "pause": 0.8},
            TIPP_ZEICHEN,
        )

    def test_mal_nimmt_den_wert_mit_der_zahl_mal(self):
        self.pruefe_ausbau(
            {"reichweite": ("*", 1.25)},
            {"schaden": 10, "reichweite": 150.0, "pause": 0.8},
            TIPP_ZEICHEN,
        )

    def test_gleich_setzt_den_wert_auf_die_zahl(self):
        self.pruefe_ausbau(
            {"pause": ("=", 0.5)},
            {"schaden": 10, "reichweite": 120.0, "pause": 0.5},
            TIPP_ZEICHEN,
        )

    def test_ein_ausbau_mit_allen_drei_zeichen_aendert_jeden_wert_auf_seine_art(self):
        self.pruefe_ausbau(
            {"schaden": ("+", 5), "reichweite": ("*", 1.25), "pause": ("=", 0.5)},
            {"schaden": 15, "reichweite": 150.0, "pause": 0.5},
            TIPP_ZEICHEN,
        )

    def test_plus_mit_einer_negativen_zahl_macht_den_wert_kleiner(self):
        self.pruefe_ausbau(
            {"schaden": ("+", -4)},
            {"schaden": 6, "reichweite": 120.0, "pause": 0.8},
            TIPP_ZEICHEN,
        )

    def test_gleich_auf_einem_neuen_schluessel_legt_den_wert_an(self):
        self.pruefe_ausbau(
            {"splitter": ("=", 3)},
            {"schaden": 10, "reichweite": 120.0, "pause": 0.8, "splitter": 3},
            'Mit "=" darf ein Ausbau dem Turm etwas ganz Neues geben. '
            "Dafür muss der Schlüssel vorher nicht in den Werten stehen.",
        )

    def test_ein_leerer_ausbau_aendert_keinen_wert(self):
        self.pruefe_ausbau({}, {"schaden": 10, "reichweite": 120.0, "pause": 0.8}, TIPP_KOPIE)

    # --- Fehler im Ausbau ---------------------------------------------------------------------

    def test_ein_unbekanntes_zeichen_ist_ein_fehler(self):
        self.pruefe_wertfehler({"schaden": ("-", 5)}, TIPP_UNBEKANNT)
        self.pruefe_wertfehler({"schaden": ("/", 2)}, TIPP_UNBEKANNT)

    def test_ein_unbekanntes_zeichen_ist_auch_auf_einem_neuen_schluessel_ein_fehler(self):
        self.pruefe_wertfehler({"splitter": ("?", 3)}, TIPP_UNBEKANNT)

    def test_plus_auf_einem_wert_den_es_nicht_gibt_ist_ein_fehler(self):
        self.pruefe_wertfehler({"splitter": ("+", 1)}, TIPP_FEHLT)

    def test_mal_auf_einem_wert_den_es_nicht_gibt_ist_ein_fehler(self):
        self.pruefe_wertfehler({"splitter": ("*", 2)}, TIPP_FEHLT)

    # --- nichts verändern ---------------------------------------------------------------------

    def test_das_ergebnis_ist_ein_neues_woerterbuch(self):
        for ausbau in [{"schaden": ("+", 5)}, {}]:
            werte = turmwerte()
            bekommen = self.werkstatt.wende_ausbau_an(werte, ausbau)
            if bekommen is werte:
                self.fail(
                    helfer.meldung(
                        f"wende_ausbau_an(werte, {ausbau}) ergibt ein neues Wörterbuch",
                        "genau das Wörterbuch werte, das hineingegeben wurde",
                        TIPP_KOPIE,
                    )
                )

    def test_die_werte_des_turms_bleiben_wie_sie_waren(self):
        werte = turmwerte()
        ausbau = {
            "schaden": ("+", 5),
            "reichweite": ("*", 1.25),
            "pause": ("=", 0.5),
            "splitter": ("=", 3),
        }
        self.werkstatt.wende_ausbau_an(werte, ausbau)
        self.pruefe_unveraendert(
            turmwerte(), werte, "werte", f"wende_ausbau_an(werte, {ausbau})", TIPP_KOPIE
        )

    def test_auch_nach_einem_fehler_sind_die_werte_des_turms_wie_vorher(self):
        werte = turmwerte()
        ausbau = {"schaden": ("+", 5), "reichweite": ("-", 1)}
        try:
            self.werkstatt.wende_ausbau_an(werte, ausbau)
        except NochOffen:
            raise
        except Exception:
            pass  # welcher Fehler es ist, prüfen die Tests weiter oben
        self.pruefe_unveraendert(
            turmwerte(), werte, "werte", f"wende_ausbau_an(werte, {ausbau})", TIPP_KOPIE
        )

    def test_der_ausbau_selbst_bleibt_wie_er_war(self):
        ausbau = {"schaden": ("+", 5), "splitter": ("=", 3)}
        self.werkstatt.wende_ausbau_an(turmwerte(), ausbau)
        self.pruefe_unveraendert(
            {"schaden": ("+", 5), "splitter": ("=", 3)},
            ausbau,
            "ausbau",
            "wende_ausbau_an(werte, ausbau)",
            "Auch der Ausbau ist nur geliehen. Lies ihn, aber ändere ihn nicht.",
        )
