"""Mission 11 · Schadensarten: Wie viel Schaden ankommt, hängt von der Art des Schadens ab."""

from tests.missionen import helfer

TIPP_FAKTOR = (
    "In resistenzen steht zu einer Schadensart ein Faktor. Mit ihm wird der Schaden "
    "malgenommen: 0.4 lässt weniger als die Hälfte durch, 2.0 das Doppelte."
)
TIPP_FEHLT = (
    "Steht die Schadensart nicht in resistenzen, zählt der Faktor 1.0: Der Schaden kommt "
    "ganz an. Ein Wörterbuch kann man so fragen, dass es bei einem fehlenden Schlüssel "
    "einen Ersatzwert liefert statt eines KeyError."
)
TIPP_NIE_NEGATIV = (
    "Schaden, der 0 oder kleiner ist, ergibt immer 0. Sonst würde ein Treffer mit "
    "negativem Schaden den Gegner heilen. Prüfe das zuerst."
)


class Mission11(helfer.Missionstest):
    modul = "horde"

    def pruefe_schaden(self, schaden, art, resistenzen, erwartet, tipp):
        aufruf = f"berechne_schaden({schaden!r}, {art!r}, {resistenzen!r})"
        bekommen = self.rufe_sicher(
            aufruf, tipp, self.werkstatt.berechne_schaden, schaden, art, resistenzen
        )
        self.pruefe_zahl(bekommen, erwartet, aufruf, tipp)

    # --- der Faktor --------------------------------------------------------------------------

    def test_eine_resistenz_laesst_nur_einen_teil_des_schadens_durch(self):
        self.pruefe_schaden(20, "feuer", {"feuer": 0.4}, 8.0, TIPP_FAKTOR)

    def test_eine_schwaeche_macht_den_schaden_groesser(self):
        self.pruefe_schaden(15, "frost", {"frost": 2.0}, 30.0, TIPP_FAKTOR)

    def test_mit_dem_faktor_null_kommt_gar_nichts_an(self):
        self.pruefe_schaden(50, "gift", {"gift": 0.0}, 0.0, TIPP_FAKTOR)

    def test_es_zaehlt_nur_der_faktor_der_eigenen_schadensart(self):
        resistenzen = {"feuer": 0.4, "frost": 0.5, "blitz": 2.0}
        self.pruefe_schaden(20, "frost", resistenzen, 10.0, TIPP_FAKTOR)
        self.pruefe_schaden(20, "blitz", resistenzen, 40.0, TIPP_FAKTOR)

    def test_auch_kommazahlen_als_schaden_werden_malgenommen(self):
        self.pruefe_schaden(2.5, "feuer", {"feuer": 0.5}, 1.25, TIPP_FAKTOR)

    # --- die Schadensart fehlt ---------------------------------------------------------------

    def test_eine_schadensart_ohne_eintrag_kommt_ganz_an(self):
        self.pruefe_schaden(20, "pfeil", {"feuer": 0.4}, 20.0, TIPP_FEHLT)

    def test_ohne_resistenzen_kommt_jeder_schaden_ganz_an(self):
        self.pruefe_schaden(12, "feuer", {}, 12.0, TIPP_FEHLT)

    # --- nie negativ -------------------------------------------------------------------------

    def test_kein_schaden_bleibt_kein_schaden(self):
        self.pruefe_schaden(0, "feuer", {"feuer": 2.0}, 0.0, TIPP_NIE_NEGATIV)
        self.pruefe_schaden(0, "pfeil", {}, 0.0, TIPP_NIE_NEGATIV)

    def test_negativer_schaden_ergibt_null_und_heilt_nicht(self):
        self.pruefe_schaden(-10, "feuer", {"feuer": 0.4}, 0.0, TIPP_NIE_NEGATIV)

    def test_negativer_schaden_ergibt_auch_ohne_eintrag_null(self):
        self.pruefe_schaden(-10, "pfeil", {}, 0.0, TIPP_NIE_NEGATIV)

    def test_negativer_schaden_ergibt_auch_bei_einer_schwaeche_null(self):
        self.pruefe_schaden(-0.5, "frost", {"frost": 2.0}, 0.0, TIPP_NIE_NEGATIV)

    # --- nichts verändern --------------------------------------------------------------------

    def test_berechne_schaden_laesst_die_resistenzen_wie_sie_waren(self):
        resistenzen = {"feuer": 0.4}
        self.rufe_sicher(
            "berechne_schaden(20, 'pfeil', {'feuer': 0.4})",
            TIPP_FEHLT,
            self.werkstatt.berechne_schaden,
            20,
            "pfeil",
            resistenzen,
        )
        self.pruefe_schaden(20, "feuer", resistenzen, 8.0, TIPP_FAKTOR)
        self.pruefe_unveraendert(
            {"feuer": 0.4},
            resistenzen,
            "das Wörterbuch resistenzen",
            "berechne_schaden(20, 'pfeil', resistenzen)",
            "Lies nur aus resistenzen. Trag dort nichts ein, auch nicht den Faktor 1.0 für "
            "eine Schadensart, die fehlt.",
        )
