"""Mission 12 · Effekte: Frost, Gift, Brand und Betäubung liegen eine Zeit lang auf einem Gegner.

Die fünf Klassen bilden eine kleine Familie: Frost, Gift und Betäubung sind Effekte, und Brand
ist ein Gift. Was die Kinder nicht selbst anders machen, erben sie.
"""

from tests.missionen import helfer
from tests.missionen.helfer import TestGegner

TIPP_MERKEN = (
    "In __init__ merkt sich ein Effekt zwei Dinge: self.dauer (das bleibt immer gleich) und "
    "self.rest (das zählt herunter). Am Anfang sind beide gleich groß."
)
TIPP_TICK = (
    "tick zieht sekunden von self.rest ab. Unter 0 darf der Rest nie fallen, und bei "
    "negativen sekunden bleibt alles, wie es ist."
)
TIPP_VORBEI = "Ein Effekt ist vorbei, sobald sein Rest 0 ist. Genau 0 zählt schon als vorbei."
TIPP_NAME = (
    "Der Name steht direkt in der Klasse, nicht in __init__: eine Zeile name = ... unter der "
    'Zeile mit class. Jede der fünf Klassen hat ihren eigenen Namen, z. B. Frost den Namen "frost".'
)
TIPP_ERBEN = (
    "Schreib die Klasse in Klammern hinter den Klassennamen, von der geerbt wird. Was das Kind "
    "nicht selbst festlegt, übernimmt es dann von dort. In __init__ kannst du mit super() "
    "das __init__ der Elternklasse aufrufen."
)
TIPP_FROST = (
    "tempo_faktor liefert bei Frost den Faktor, den er in __init__ bekommen hat, aber nur "
    "solange der Frost noch nicht vorbei ist. Danach läuft der Gegner wieder normal: 1.0."
)
TIPP_GIFT = (
    "Gift ruft in tick zuerst gegner.erleide_schaden(menge, art) auf und lässt danach die Zeit "
    "vergehen wie jeder Effekt. Die Menge ist der Schaden pro Sekunde mal die Sekunden."
)
TIPP_GIFT_REST = (
    "Gift wirkt nur, solange noch Zeit übrig ist. Sind mehr Sekunden vergangen, als der Rest "
    "hergibt, zählt nur der Rest: Nimm die kleinere der beiden Zahlen. Rechne den Schaden "
    "aus, bevor du den Rest herunterzählst."
)
TIPP_KEIN_SCHADEN = (
    "Ist die Menge nicht größer als 0, wird erleide_schaden gar nicht aufgerufen: nicht bei "
    "0 Sekunden, nicht bei negativen Sekunden und nicht, wenn der Effekt schon vorbei ist."
)
TIPP_ART = (
    "Welche Art von Schaden ein Gift macht, steht als schadensart direkt in der Klasse. In tick "
    "liest du sie mit self.schadensart. Dann braucht Brand kein eigenes tick: Es genügt, in "
    "Brand eine andere schadensart hinzuschreiben."
)
TIPP_BETAEUBUNG = (
    "Ein betäubter Gegner steht still: tempo_faktor liefert 0.0, solange die Betäubung nicht "
    "vorbei ist, danach wieder 1.0."
)


class Mission12(helfer.Missionstest):
    modul = "horde"

    def setUp(self):
        super().setUp()
        self.gegner = TestGegner(leben=100.0)

    # --- kleine Helfer -----------------------------------------------------------------------

    def ticke(self, effekt, sekunden, gegner=None):
        """Lässt für den Effekt Zeit vergehen. Ein Absturz in tick wird zur Meldung mit Tipp."""
        gegner = self.gegner if gegner is None else gegner
        self.rufe_sicher(
            f"{type(effekt).__name__}.tick(gegner, {sekunden})",
            "Der Fehler entsteht in tick (oder im tick der Klasse, von der geerbt wird). "
            "Weiter oben in der Ausgabe steht die Zeile in deiner Datei.",
            effekt.tick,
            gegner,
            sekunden,
        )

    def pruefe_rest(self, effekt, erwartet, aufruf, tipp):
        self.pruefe_zahl(self.lies_attribut(effekt, "rest", TIPP_MERKEN), erwartet, aufruf, tipp)

    def pruefe_faktor(self, effekt, erwartet, aufruf, tipp):
        bekommen = self.rufe_sicher(aufruf, tipp, effekt.tempo_faktor)
        self.pruefe_zahl(bekommen, erwartet, aufruf, tipp)

    def pruefe_vorbei(self, effekt, erwartet, aufruf, tipp):
        self.pruefe_gleich(
            self.rufe_sicher(aufruf, tipp, effekt.ist_vorbei), erwartet, aufruf, tipp
        )

    def pruefe_unberuehrt(self, aufruf):
        """Der Gegner wurde weder verletzt noch geheilt."""
        self.pruefe_schaeden(self.gegner, [], aufruf, TIPP_KEIN_SCHADEN)
        self.pruefe_heilungen(self.gegner, [], aufruf, "Ein Effekt heilt niemanden.")
        self.pruefe_zahl(
            self.gegner.leben, 100.0, f"das Leben des Gegners nach {aufruf}", TIPP_GIFT
        )

    def pruefe_ist_ein(self, effekt, eltern, kind_name, eltern_name):
        if not (isinstance(effekt, eltern) and issubclass(type(effekt), eltern)):
            self.fail(
                helfer.meldung(
                    f"{kind_name} erbt von {eltern_name}: jeder {kind_name} ist auch ein "
                    f"{eltern_name}",
                    f"die Klasse {kind_name} erbt von "
                    f"{[klasse.__name__ for klasse in type(effekt).__mro__[1:]]}",
                    TIPP_ERBEN,
                )
            )

    # --- Effekt: die Grundlage ---------------------------------------------------------------

    def test_ein_effekt_merkt_sich_seine_dauer_und_seinen_rest(self):
        effekt = self.erzeuge("Effekt", 3.0)
        self.pruefe_zahl(
            self.lies_attribut(effekt, "dauer", TIPP_MERKEN), 3.0, "Effekt(3.0).dauer", TIPP_MERKEN
        )
        self.pruefe_rest(effekt, 3.0, "Effekt(3.0).rest", TIPP_MERKEN)

    def test_ein_frischer_effekt_ist_nicht_vorbei_und_bremst_nicht(self):
        effekt = self.erzeuge("Effekt", 3.0)
        self.pruefe_vorbei(effekt, False, "Effekt(3.0).ist_vorbei()", TIPP_VORBEI)
        self.pruefe_faktor(
            effekt,
            1.0,
            "Effekt(3.0).tempo_faktor()",
            "Ein gewöhnlicher Effekt ändert das Tempo nicht: 1.0 heißt normal schnell.",
        )

    def test_tick_zieht_die_vergangene_zeit_vom_rest_ab(self):
        effekt = self.erzeuge("Effekt", 3.0)
        self.ticke(effekt, 0.5)
        self.pruefe_rest(effekt, 2.5, "Effekt(3.0).rest nach tick(gegner, 0.5)", TIPP_TICK)
        self.ticke(effekt, 1.0)
        self.pruefe_rest(effekt, 1.5, "Effekt(3.0).rest nach 0.5 und 1.0 Sekunden", TIPP_TICK)
        self.pruefe_zahl(
            self.lies_attribut(effekt, "dauer", TIPP_MERKEN),
            3.0,
            "Effekt(3.0).dauer nach zwei Aufrufen von tick",
            "Die Dauer ist die volle Zeit des Effekts. Sie bleibt, wie sie war; nur der Rest "
            "zählt herunter.",
        )
        self.pruefe_vorbei(effekt, False, "ist_vorbei() mit dem Rest 1.5", TIPP_VORBEI)

    def test_der_rest_faellt_nie_unter_null(self):
        effekt = self.erzeuge("Effekt", 1.0)
        self.ticke(effekt, 2.5)
        self.pruefe_rest(effekt, 0.0, "Effekt(1.0).rest nach tick(gegner, 2.5)", TIPP_TICK)
        self.pruefe_vorbei(effekt, True, "Effekt(1.0).ist_vorbei() nach 2.5 Sekunden", TIPP_VORBEI)
        self.ticke(effekt, 1.0)
        self.pruefe_rest(effekt, 0.0, "der Rest eines abgelaufenen Effekts nach tick", TIPP_TICK)

    def test_ist_der_rest_genau_aufgebraucht_ist_der_effekt_vorbei(self):
        effekt = self.erzeuge("Effekt", 2.0)
        self.ticke(effekt, 1.5)
        self.pruefe_vorbei(effekt, False, "Effekt(2.0).ist_vorbei() nach 1.5 Sekunden", TIPP_VORBEI)
        self.ticke(effekt, 0.5)
        self.pruefe_vorbei(effekt, True, "Effekt(2.0).ist_vorbei() nach 2.0 Sekunden", TIPP_VORBEI)

    def test_ein_effekt_mit_der_dauer_null_ist_sofort_vorbei(self):
        effekt = self.erzeuge("Effekt", 0)
        self.pruefe_vorbei(effekt, True, "Effekt(0).ist_vorbei()", TIPP_VORBEI)

    def test_negative_zeit_aendert_den_rest_nicht(self):
        effekt = self.erzeuge("Effekt", 3.0)
        self.ticke(effekt, -1.0)
        self.pruefe_rest(effekt, 3.0, "Effekt(3.0).rest nach tick(gegner, -1.0)", TIPP_TICK)

    def test_ein_gewoehnlicher_effekt_verletzt_und_heilt_niemanden(self):
        effekt = self.erzeuge("Effekt", 3.0)
        self.ticke(effekt, 1.0)
        self.pruefe_unberuehrt("Effekt(3.0).tick(gegner, 1.0)")

    def test_jede_klasse_hat_ihren_eigenen_namen(self):
        effekte = [
            ("effekt", "Effekt(1.0)", self.erzeuge("Effekt", 1.0)),
            ("frost", "Frost(1.0, 0.5)", self.erzeuge("Frost", 1.0, 0.5)),
            ("gift", "Gift(1.0, 2.0)", self.erzeuge("Gift", 1.0, 2.0)),
            ("brand", "Brand(1.0, 2.0)", self.erzeuge("Brand", 1.0, 2.0)),
            ("betaeubung", "Betaeubung(1.0)", self.erzeuge("Betaeubung", 1.0)),
        ]
        for name, aufruf, effekt in effekte:
            self.pruefe_gleich(
                self.lies_attribut(effekt, "name", TIPP_NAME), name, f"{aufruf}.name", TIPP_NAME
            )
        # Der Name gehört der Klasse: Man kann ihn lesen, ohne erst einen Effekt zu erzeugen.
        for name, _aufruf, effekt in effekte:
            klasse = type(effekt)
            self.pruefe_gleich(
                getattr(klasse, "name", None), name, f"{klasse.__name__}.name", TIPP_NAME
            )

    # --- Frost -------------------------------------------------------------------------------

    def test_frost_ist_ein_effekt_und_erbt_dauer_rest_und_tick(self):
        frost = self.erzeuge("Frost", 2.0, 0.5)
        self.pruefe_ist_ein(frost, self.werkstatt.Effekt, "Frost", "Effekt")
        self.pruefe_zahl(
            self.lies_attribut(frost, "dauer", TIPP_ERBEN), 2.0, "Frost(2.0, 0.5).dauer", TIPP_ERBEN
        )
        self.pruefe_rest(frost, 2.0, "Frost(2.0, 0.5).rest", TIPP_ERBEN)
        self.ticke(frost, 0.5)
        self.pruefe_rest(frost, 1.5, "Frost(2.0, 0.5).rest nach tick(gegner, 0.5)", TIPP_ERBEN)
        self.ticke(frost, -1.0)
        self.pruefe_rest(frost, 1.5, "der Rest eines Frosts nach tick(gegner, -1.0)", TIPP_TICK)
        self.ticke(frost, 9.0)
        self.pruefe_rest(frost, 0.0, "der Rest eines Frosts nach viel zu langer Zeit", TIPP_TICK)

    def test_frost_bremst_mit_seinem_faktor(self):
        self.pruefe_faktor(
            self.erzeuge("Frost", 2.0, 0.5), 0.5, "Frost(2.0, 0.5).tempo_faktor()", TIPP_FROST
        )
        self.pruefe_faktor(
            self.erzeuge("Frost", 2.0, 0.25), 0.25, "Frost(2.0, 0.25).tempo_faktor()", TIPP_FROST
        )

    def test_frost_bremst_bis_zum_schluss_und_danach_nicht_mehr(self):
        frost = self.erzeuge("Frost", 2.0, 0.5)
        self.ticke(frost, 1.5)
        self.pruefe_faktor(
            frost, 0.5, "Frost(2.0, 0.5).tempo_faktor() nach 1.5 Sekunden", TIPP_FROST
        )
        self.ticke(frost, 0.5)
        self.pruefe_vorbei(
            frost, True, "Frost(2.0, 0.5).ist_vorbei() nach 2.0 Sekunden", TIPP_VORBEI
        )
        self.pruefe_faktor(
            frost, 1.0, "Frost(2.0, 0.5).tempo_faktor() nach 2.0 Sekunden", TIPP_FROST
        )

    def test_frost_verletzt_niemanden(self):
        frost = self.erzeuge("Frost", 2.0, 0.5)
        self.ticke(frost, 1.0)
        self.pruefe_unberuehrt("Frost(2.0, 0.5).tick(gegner, 1.0)")

    # --- Gift --------------------------------------------------------------------------------

    def test_gift_ist_ein_effekt_und_erbt_dauer_rest_und_das_ende(self):
        gift = self.erzeuge("Gift", 5.0, 4.0)
        self.pruefe_ist_ein(gift, self.werkstatt.Effekt, "Gift", "Effekt")
        self.pruefe_zahl(
            self.lies_attribut(gift, "dauer", TIPP_ERBEN), 5.0, "Gift(5.0, 4.0).dauer", TIPP_ERBEN
        )
        self.pruefe_rest(gift, 5.0, "Gift(5.0, 4.0).rest", TIPP_ERBEN)
        self.pruefe_vorbei(gift, False, "Gift(5.0, 4.0).ist_vorbei()", TIPP_VORBEI)
        self.pruefe_faktor(
            gift, 1.0, "Gift(5.0, 4.0).tempo_faktor()", "Gift schadet nur. Es bremst nicht: 1.0."
        )

    def test_gift_schadet_sekunde_fuer_sekunde(self):
        gift = self.erzeuge("Gift", 5.0, 4.0)
        self.ticke(gift, 0.5)
        aufruf = "Gift(5.0, 4.0).tick(gegner, 0.5)"
        self.pruefe_schaeden(self.gegner, [(2.0, "gift")], aufruf, TIPP_GIFT)
        self.pruefe_rest(gift, 4.5, f"der Rest nach {aufruf}", TIPP_GIFT)
        self.ticke(gift, 1.0)
        self.pruefe_schaeden(
            self.gegner, [(2.0, "gift"), (4.0, "gift")], "zwei Aufrufen von tick", TIPP_GIFT
        )
        self.pruefe_rest(gift, 3.5, "der Rest nach 0.5 und 1.0 Sekunden", TIPP_GIFT)

    def test_gift_schadet_nur_fuer_die_zeit_die_es_noch_wirkt(self):
        gift = self.erzeuge("Gift", 1.0, 4.0)
        self.ticke(gift, 3.0)
        aufruf = "Gift(1.0, 4.0).tick(gegner, 3.0)"
        # Nur 1 Sekunde war noch übrig: 4 Schaden und nicht 12.
        self.pruefe_schaeden(self.gegner, [(4.0, "gift")], aufruf, TIPP_GIFT_REST)
        self.pruefe_rest(gift, 0.0, f"der Rest nach {aufruf}", TIPP_TICK)
        self.pruefe_vorbei(gift, True, f"ist_vorbei() nach {aufruf}", TIPP_VORBEI)

    def test_abgelaufenes_gift_schadet_nicht_mehr(self):
        gift = self.erzeuge("Gift", 1.0, 4.0)
        self.ticke(gift, 1.0)
        self.ticke(gift, 1.0)
        self.ticke(gift, 0.5)
        self.pruefe_schaeden(
            self.gegner,
            [(4.0, "gift")],
            "drei Aufrufen von tick, von denen zwei nach dem Ende des Gifts kamen,",
            TIPP_KEIN_SCHADEN,
        )

    def test_gift_schadet_nicht_wenn_keine_zeit_vergangen_ist(self):
        gift = self.erzeuge("Gift", 5.0, 4.0)
        self.ticke(gift, 0)
        self.pruefe_unberuehrt("Gift(5.0, 4.0).tick(gegner, 0)")

    def test_gift_heilt_bei_negativer_zeit_nicht_und_bleibt_wie_es_war(self):
        gift = self.erzeuge("Gift", 5.0, 4.0)
        self.ticke(gift, -1.0)
        self.pruefe_unberuehrt("Gift(5.0, 4.0).tick(gegner, -1.0)")
        self.pruefe_rest(gift, 5.0, "der Rest nach Gift(5.0, 4.0).tick(gegner, -1.0)", TIPP_TICK)

    def test_gift_ueberlaesst_das_abziehen_des_lebens_dem_gegner(self):
        class Giftfest(TestGegner):
            """Dieser Gegner hält Gift gut aus: Bei ihm kommt nur die Hälfte an."""

            def erleide_schaden(self, menge, art):
                return super().erleide_schaden(menge / 2, art)

        gegner = Giftfest(leben=100.0)
        self.ticke(self.erzeuge("Gift", 5.0, 4.0), 1.0, gegner)
        self.pruefe_zahl(
            gegner.leben,
            98.0,
            "das Leben eines Gegners, bei dem nur die Hälfte ankommt, nach "
            "Gift(5.0, 4.0).tick(gegner, 1.0)",
            "Ändere gegner.leben nie selbst. Ruf nur gegner.erleide_schaden(menge, art) auf, "
            "und zwar genau einmal: Der Gegner weiß selbst, wie viel er davon abbekommt.",
        )

    def test_die_art_des_schadens_steht_als_schadensart_in_der_klasse(self):
        gift = self.erzeuge("Gift", 5.0, 4.0)
        brand = self.erzeuge("Brand", 5.0, 4.0)
        self.pruefe_gleich(
            self.lies_attribut(gift, "schadensart", TIPP_ART), "gift", "Gift.schadensart", TIPP_ART
        )
        self.pruefe_gleich(
            self.lies_attribut(brand, "schadensart", TIPP_ART),
            "feuer",
            "Brand.schadensart",
            TIPP_ART,
        )
        for klasse, art in ((type(gift), "gift"), (type(brand), "feuer")):
            self.pruefe_gleich(
                getattr(klasse, "schadensart", None),
                art,
                f"{klasse.__name__}.schadensart",
                TIPP_ART,
            )

    def test_ein_neues_kind_von_gift_braucht_nur_eine_andere_schadensart(self):
        class Saeure(self.werkstatt.Gift):
            """So entsteht aus Gift ein neuer Effekt, ohne dass tick noch einmal geschrieben wird."""

            schadensart = "saeure"

        saeure = self.rufe_sicher("Saeure(5.0, 4.0)", TIPP_ERBEN, Saeure, 5.0, 4.0)
        self.ticke(saeure, 0.5)
        self.pruefe_schaeden(
            self.gegner,
            [(2.0, "saeure")],
            'tick(gegner, 0.5) bei einer Klasse, die von Gift erbt und nur schadensart = "saeure" '
            "festlegt,",
            TIPP_ART,
        )

    # --- Brand -------------------------------------------------------------------------------

    def test_brand_ist_ein_gift_und_damit_auch_ein_effekt(self):
        brand = self.erzeuge("Brand", 4.0, 3.0)
        self.pruefe_ist_ein(brand, self.werkstatt.Gift, "Brand", "Gift")
        self.pruefe_ist_ein(brand, self.werkstatt.Effekt, "Brand", "Effekt")
        self.pruefe_zahl(
            self.lies_attribut(brand, "dauer", TIPP_ERBEN), 4.0, "Brand(4.0, 3.0).dauer", TIPP_ERBEN
        )
        self.pruefe_rest(brand, 4.0, "Brand(4.0, 3.0).rest", TIPP_ERBEN)
        self.pruefe_faktor(
            brand, 1.0, "Brand(4.0, 3.0).tempo_faktor()", "Brand schadet nur. Er bremst nicht: 1.0."
        )

    def test_brand_schadet_wie_gift_aber_mit_feuer(self):
        brand = self.erzeuge("Brand", 4.0, 3.0)
        self.ticke(brand, 0.5)
        aufruf = "Brand(4.0, 3.0).tick(gegner, 0.5)"
        self.pruefe_schaeden(self.gegner, [(1.5, "feuer")], aufruf, TIPP_ART)
        self.pruefe_rest(brand, 3.5, f"der Rest nach {aufruf}", TIPP_ERBEN)

    def test_brand_schadet_nur_fuer_die_zeit_die_er_noch_brennt(self):
        brand = self.erzeuge("Brand", 1.0, 3.0)
        self.ticke(brand, 3.0)
        self.ticke(brand, 1.0)
        self.pruefe_schaeden(
            self.gegner,
            [(3.0, "feuer")],
            "Brand(1.0, 3.0).tick(gegner, 3.0) und einem weiteren tick nach dem Ende",
            TIPP_GIFT_REST,
        )
        self.pruefe_vorbei(brand, True, "Brand(1.0, 3.0).ist_vorbei() nach 3 Sekunden", TIPP_VORBEI)
        self.pruefe_rest(brand, 0.0, "der Rest eines Brands nach viel zu langer Zeit", TIPP_TICK)

    def test_brand_heilt_bei_negativer_zeit_nicht_und_bleibt_wie_er_war(self):
        brand = self.erzeuge("Brand", 4.0, 3.0)
        self.ticke(brand, -1.0)
        self.pruefe_unberuehrt("Brand(4.0, 3.0).tick(gegner, -1.0)")
        self.pruefe_rest(brand, 4.0, "der Rest nach Brand(4.0, 3.0).tick(gegner, -1.0)", TIPP_TICK)

    # --- Betäubung ---------------------------------------------------------------------------

    def test_betaeubung_ist_ein_effekt_und_erbt_dauer_rest_und_tick(self):
        betaeubung = self.erzeuge("Betaeubung", 1.5)
        self.pruefe_ist_ein(betaeubung, self.werkstatt.Effekt, "Betaeubung", "Effekt")
        self.pruefe_zahl(
            self.lies_attribut(betaeubung, "dauer", TIPP_ERBEN),
            1.5,
            "Betaeubung(1.5).dauer",
            TIPP_ERBEN,
        )
        self.ticke(betaeubung, 0.5)
        self.pruefe_rest(betaeubung, 1.0, "Betaeubung(1.5).rest nach tick(gegner, 0.5)", TIPP_ERBEN)
        self.ticke(betaeubung, -1.0)
        self.pruefe_rest(
            betaeubung, 1.0, "der Rest einer Betäubung nach tick(gegner, -1.0)", TIPP_TICK
        )
        self.ticke(betaeubung, 9.0)
        self.pruefe_rest(
            betaeubung, 0.0, "der Rest einer Betäubung nach viel zu langer Zeit", TIPP_TICK
        )

    def test_ein_betaeubter_gegner_steht_still(self):
        betaeubung = self.erzeuge("Betaeubung", 1.5)
        self.pruefe_faktor(betaeubung, 0.0, "Betaeubung(1.5).tempo_faktor()", TIPP_BETAEUBUNG)
        self.ticke(betaeubung, 1.0)
        self.pruefe_faktor(
            betaeubung, 0.0, "Betaeubung(1.5).tempo_faktor() nach 1.0 Sekunden", TIPP_BETAEUBUNG
        )

    def test_nach_der_betaeubung_laeuft_der_gegner_wieder(self):
        betaeubung = self.erzeuge("Betaeubung", 1.5)
        self.ticke(betaeubung, 1.5)
        self.pruefe_vorbei(
            betaeubung, True, "Betaeubung(1.5).ist_vorbei() nach 1.5 Sekunden", TIPP_VORBEI
        )
        self.pruefe_faktor(
            betaeubung, 1.0, "Betaeubung(1.5).tempo_faktor() nach 1.5 Sekunden", TIPP_BETAEUBUNG
        )

    def test_betaeubung_verletzt_niemanden(self):
        betaeubung = self.erzeuge("Betaeubung", 1.5)
        self.ticke(betaeubung, 1.0)
        self.pruefe_unberuehrt("Betaeubung(1.5).tick(gegner, 1.0)")
