"""Mission 14 · Besondere Fähigkeiten: Der Troll heilt sich, der Schamane heilt andere, der
Orkkönig ruft Verstärkung.

Alle drei haben dieselbe Methode aktualisiere(traeger, alle, sekunden). Sie liefert immer eine
Liste: die Arten der Gegner, die jetzt neu erscheinen sollen. Meistens ist diese Liste leer.
"""

from tests.missionen import helfer
from tests.missionen.helfer import TestEffekt, TestGegner

TIPP_LISTE = (
    "aktualisiere gibt immer eine Liste zurück. Wer niemanden herbeiruft, liefert die leere "
    "Liste [] und nicht None."
)
TIPP_HEILE = (
    "Geheilt wird mit traeger.heile(menge), genau einmal pro Aufruf. Die Menge ist die "
    "Heilung pro Sekunde mal die vergangenen Sekunden. Ändere leben nicht selbst."
)
TIPP_BRAND = (
    "Wer brennt, heilt nicht. Schau in traeger.effekte nach einem Effekt mit dem Namen "
    '"brand", der noch nicht vorbei ist. Andere Effekte und ein erloschener Brand stören nicht.'
)
TIPP_LEBT = "Nur wer lebt, kann etwas tun oder geheilt werden: leben muss größer als 0 sein."
TIPP_ANDERE = (
    "Der Schamane geht die Liste alle durch und heilt jeden lebenden Gegner in seinem Radius "
    "mit dessen heile(menge). Sich selbst lässt er aus: Er steht auch in alle."
)
TIPP_RADIUS = (
    "Gemessen wird die gerade Linie vom Schamanen (traeger.x, traeger.y) zum anderen Gegner, "
    "wie in Mission 6. Genau auf dem Rand des Radius zählt noch dazu."
)
TIPP_UHR = (
    "Der Beschwörer hat eine Uhr: self.rest beginnt beim Intervall und wird bei jedem Aufruf "
    "um sekunden kleiner. Erst wenn sie bei 0 ankommt, ruft er, und dann wird das Intervall "
    "wieder auf die Uhr gezählt (dazugezählt, nicht neu gesetzt)."
)


class Mission14(helfer.Missionstest):
    modul = "horde"

    def aktualisiere(self, faehigkeit, traeger, alle, sekunden, erwartet, tipp=TIPP_LISTE):
        aufruf = f"{type(faehigkeit).__name__}.aktualisiere(traeger, alle, {sekunden})"
        bekommen = self.rufe_sicher(aufruf, tipp, faehigkeit.aktualisiere, traeger, alle, sekunden)
        self.pruefe_gleich(bekommen, erwartet, aufruf, tipp)

    # --- Regeneration ------------------------------------------------------------------------

    def test_ein_verwundeter_troll_heilt_sich_sekunde_fuer_sekunde(self):
        troll = TestGegner(leben=50.0, max_leben=100.0)
        regeneration = self.erzeuge("Regeneration", 2.0)
        self.aktualisiere(regeneration, troll, [troll], 0.5, [])
        self.pruefe_heilungen(
            troll, [1.0], "Regeneration(2.0).aktualisiere(troll, alle, 0.5)", TIPP_HEILE
        )
        self.pruefe_zahl(
            troll.leben, 51.0, "das Leben des Trolls nach einer halben Sekunde", TIPP_HEILE
        )
        self.aktualisiere(regeneration, troll, [troll], 2.0, [])
        self.pruefe_heilungen(
            troll,
            [1.0, 4.0],
            "zwei Aufrufen mit 0.5 und 2.0 Sekunden bei Regeneration(2.0)",
            TIPP_HEILE,
        )

    def test_ein_brennender_troll_heilt_sich_nicht(self):
        troll = TestGegner(leben=50.0, max_leben=100.0)
        troll.effekte = [TestEffekt("frost", rest=2.0, faktor=0.5), TestEffekt("brand", rest=2.0)]
        self.aktualisiere(self.erzeuge("Regeneration", 2.0), troll, [troll], 1.0, [])
        self.pruefe_heilungen(troll, [], "aktualisiere bei einem brennenden Troll", TIPP_BRAND)
        self.pruefe_zahl(troll.leben, 50.0, "das Leben des brennenden Trolls", TIPP_BRAND)

    def test_ist_der_brand_erloschen_heilt_sich_der_troll_wieder(self):
        troll = TestGegner(leben=50.0, max_leben=100.0)
        troll.effekte = [TestEffekt("brand", rest=0.0)]
        self.aktualisiere(self.erzeuge("Regeneration", 2.0), troll, [troll], 1.0, [])
        self.pruefe_heilungen(
            troll, [2.0], "aktualisiere bei einem Troll, dessen Brand schon vorbei ist,", TIPP_BRAND
        )

    def test_frost_und_gift_halten_die_heilung_nicht_auf(self):
        troll = TestGegner(leben=50.0, max_leben=100.0)
        troll.effekte = [TestEffekt("frost", rest=2.0, faktor=0.5), TestEffekt("gift", rest=2.0)]
        self.aktualisiere(self.erzeuge("Regeneration", 2.0), troll, [troll], 1.0, [])
        self.pruefe_heilungen(
            troll,
            [2.0],
            "aktualisiere bei einem Troll mit Frost und Gift, aber ohne Brand,",
            TIPP_BRAND,
        )

    def test_ein_besiegter_troll_steht_nicht_wieder_auf(self):
        troll = TestGegner(leben=0, max_leben=100.0)
        self.aktualisiere(self.erzeuge("Regeneration", 2.0), troll, [troll], 1.0, [])
        self.pruefe_heilungen(troll, [], "aktualisiere bei einem besiegten Troll", TIPP_LEBT)
        self.pruefe_zahl(troll.leben, 0, "das Leben des besiegten Trolls", TIPP_LEBT)

    def test_regeneration_heilt_nur_den_traeger(self):
        troll = TestGegner(leben=50.0, max_leben=100.0, x=100.0, y=100.0)
        ork = TestGegner(leben=10.0, max_leben=45.0, x=100.0, y=100.0)
        self.aktualisiere(self.erzeuge("Regeneration", 2.0), troll, [ork, troll], 1.0, [])
        self.pruefe_heilungen(troll, [2.0], "aktualisiere(troll, [ork, troll], 1.0)", TIPP_HEILE)
        self.pruefe_heilungen(
            ork,
            [],
            "Regeneration(2.0).aktualisiere(troll, [ork, troll], 1.0)",
            "Die Regeneration heilt nur ihren Träger. Die Liste alle braucht sie gar nicht.",
        )

    # --- Heiler ------------------------------------------------------------------------------

    def schamane_und(self, *andere):
        """Ein verwundeter Schamane auf (200, 200) und die Liste aller Gegner, er mittendrin."""
        schamane = TestGegner(leben=20.0, max_leben=60.0, x=200.0, y=200.0)
        return schamane, [*andere[:1], schamane, *andere[1:]]

    def test_der_schamane_heilt_einen_verwundeten_in_seiner_naehe(self):
        ork = TestGegner(leben=10.0, max_leben=45.0, x=250.0, y=200.0)
        schamane, alle = self.schamane_und(ork)
        self.aktualisiere(self.erzeuge("Heiler", 100.0, 4.0), schamane, alle, 0.5, [])
        self.pruefe_heilungen(
            ork, [2.0], "Heiler(100.0, 4.0).aktualisiere(schamane, alle, 0.5)", TIPP_ANDERE
        )
        self.pruefe_zahl(
            ork.leben, 12.0, "das Leben des Orks nach einer halben Sekunde", TIPP_ANDERE
        )

    def test_der_schamane_heilt_sich_nie_selbst(self):
        ork = TestGegner(leben=10.0, max_leben=45.0, x=250.0, y=200.0)
        schamane, alle = self.schamane_und(ork)
        self.aktualisiere(self.erzeuge("Heiler", 100.0, 4.0), schamane, alle, 0.5, [])
        self.pruefe_heilungen(
            schamane, [], "Heiler(100.0, 4.0).aktualisiere(schamane, alle, 0.5)", TIPP_ANDERE
        )

    def test_der_schamane_heilt_alle_in_seinem_radius_jeden_einmal(self):
        links = TestGegner(leben=10.0, max_leben=45.0, x=150.0, y=200.0)
        oben = TestGegner(leben=10.0, max_leben=45.0, x=200.0, y=140.0)
        schraeg = TestGegner(leben=10.0, max_leben=45.0, x=260.0, y=260.0)  # etwa 84,9 entfernt
        schamane, alle = self.schamane_und(links, oben, schraeg)
        self.aktualisiere(self.erzeuge("Heiler", 100.0, 4.0), schamane, alle, 1.0, [])
        for name, gegner in (("links", links), ("oben", oben), ("schraeg", schraeg)):
            self.pruefe_heilungen(
                gegner, [4.0], f"aktualisiere(schamane, alle, 1.0) beim Gegner {name}", TIPP_ANDERE
            )

    def test_wer_genau_auf_dem_rand_des_radius_steht_wird_noch_geheilt(self):
        am_rand = TestGegner(leben=10.0, max_leben=45.0, x=300.0, y=200.0)
        schamane, alle = self.schamane_und(am_rand)
        self.aktualisiere(self.erzeuge("Heiler", 100.0, 4.0), schamane, alle, 1.0, [])
        self.pruefe_heilungen(
            am_rand, [4.0], "aktualisiere bei einem Gegner genau 100 entfernt", TIPP_RADIUS
        )

    def test_wer_ausserhalb_des_radius_steht_wird_nicht_geheilt(self):
        knapp_draussen = TestGegner(leben=10.0, max_leben=45.0, x=301.0, y=200.0)
        weit_weg = TestGegner(leben=10.0, max_leben=45.0, x=200.0, y=600.0)
        schamane, alle = self.schamane_und(knapp_draussen, weit_weg)
        self.aktualisiere(self.erzeuge("Heiler", 100.0, 4.0), schamane, alle, 1.0, [])
        self.pruefe_heilungen(
            knapp_draussen, [], "aktualisiere bei einem Gegner 101 entfernt", TIPP_RADIUS
        )
        self.pruefe_heilungen(
            weit_weg, [], "aktualisiere bei einem Gegner 400 entfernt", TIPP_RADIUS
        )

    def test_der_radius_ist_ein_kreis_um_den_schamanen(self):
        # 80 nach rechts und 80 nach unten: Das sind etwa 113, also mehr als der Radius 100.
        in_der_ecke = TestGegner(leben=10.0, max_leben=45.0, x=280.0, y=280.0)
        # Nah am Schamanen, aber weit weg von der Ecke (0, 0) der Karte.
        nah = TestGegner(leben=10.0, max_leben=45.0, x=230.0, y=240.0)
        schamane, alle = self.schamane_und(in_der_ecke, nah)
        self.aktualisiere(self.erzeuge("Heiler", 100.0, 4.0), schamane, alle, 1.0, [])
        self.pruefe_heilungen(
            in_der_ecke, [], "aktualisiere bei einem Gegner etwa 113 entfernt", TIPP_RADIUS
        )
        self.pruefe_heilungen(nah, [4.0], "aktualisiere bei einem Gegner 50 entfernt", TIPP_RADIUS)

    def test_besiegte_werden_nicht_geheilt(self):
        besiegt = TestGegner(leben=0, max_leben=45.0, x=250.0, y=200.0)
        ork = TestGegner(leben=10.0, max_leben=45.0, x=150.0, y=200.0)
        schamane, alle = self.schamane_und(besiegt, ork)
        self.aktualisiere(self.erzeuge("Heiler", 100.0, 4.0), schamane, alle, 1.0, [])
        self.pruefe_heilungen(
            besiegt, [], "aktualisiere bei einem besiegten Gegner im Radius", TIPP_LEBT
        )
        self.pruefe_zahl(besiegt.leben, 0, "das Leben des Besiegten", TIPP_LEBT)
        self.pruefe_heilungen(ork, [4.0], "aktualisiere beim lebenden Ork daneben", TIPP_ANDERE)

    def test_ein_besiegter_schamane_heilt_niemanden_mehr(self):
        ork = TestGegner(leben=10.0, max_leben=45.0, x=250.0, y=200.0)
        schamane, alle = self.schamane_und(ork)
        schamane.leben = 0
        self.aktualisiere(self.erzeuge("Heiler", 100.0, 4.0), schamane, alle, 1.0, [])
        self.pruefe_heilungen(
            ork,
            [],
            "aktualisiere bei einem besiegten Schamanen",
            "Prüfe zuerst, ob der Träger selbst noch lebt. " + TIPP_LEBT,
        )

    def test_der_heiler_laesst_die_liste_aller_gegner_wie_sie_war(self):
        ork = TestGegner(leben=10.0, max_leben=45.0, x=250.0, y=200.0)
        besiegt = TestGegner(leben=0, max_leben=45.0, x=150.0, y=200.0)
        schamane, alle = self.schamane_und(ork, besiegt)
        vorher = list(alle)
        self.aktualisiere(self.erzeuge("Heiler", 100.0, 4.0), schamane, alle, 1.0, [])
        self.pruefe_unveraendert(
            vorher,
            alle,
            "die Liste alle",
            "Heiler(100.0, 4.0).aktualisiere(schamane, alle, 1.0)",
            "Nimm niemanden aus der Liste heraus, auch nicht den Schamanen. Überspring ihn nur.",
        )

    # --- Beschwoerer -------------------------------------------------------------------------

    def test_der_beschwoerer_stellt_seine_uhr_auf_das_intervall(self):
        beschwoerer = self.erzeuge("Beschwoerer", 3.0, "ork", 2)
        self.pruefe_zahl(
            self.lies_attribut(beschwoerer, "rest", TIPP_UHR),
            3.0,
            'Beschwoerer(3.0, "ork", 2).rest',
            TIPP_UHR,
        )

    def test_vor_ablauf_des_intervalls_ruft_der_beschwoerer_niemanden(self):
        koenig = TestGegner(leben=500.0, ist_boss=True)
        beschwoerer = self.erzeuge("Beschwoerer", 3.0, "ork", 2)
        self.aktualisiere(beschwoerer, koenig, [koenig], 1.0, [], TIPP_UHR)
        self.aktualisiere(beschwoerer, koenig, [koenig], 1.0, [], TIPP_UHR)
        self.pruefe_zahl(
            self.lies_attribut(beschwoerer, "rest", TIPP_UHR),
            1.0,
            "die Uhr rest nach 2 von 3 Sekunden",
            TIPP_UHR,
        )

    def test_ist_das_intervall_um_ruft_er_die_art_so_oft_wie_die_anzahl_sagt(self):
        koenig = TestGegner(leben=500.0, ist_boss=True)
        beschwoerer = self.erzeuge("Beschwoerer", 3.0, "ork", 2)
        self.aktualisiere(beschwoerer, koenig, [koenig], 1.0, [], TIPP_UHR)
        self.aktualisiere(beschwoerer, koenig, [koenig], 1.0, [], TIPP_UHR)
        # Jetzt ist die dritte Sekunde um: Die Uhr steht genau auf 0.
        self.aktualisiere(
            beschwoerer,
            koenig,
            [koenig],
            1.0,
            ["ork", "ork"],
            "Steht die Uhr auf 0 oder darunter, liefert er eine Liste, in der die Art so oft "
            "steht, wie anzahl sagt. " + TIPP_UHR,
        )

    def test_ohne_angabe_ruft_er_genau_einen(self):
        koenig = TestGegner(leben=500.0, ist_boss=True)
        beschwoerer = self.erzeuge("Beschwoerer", 2.0, "wolf")
        self.aktualisiere(beschwoerer, koenig, [koenig], 2.0, ["wolf"], TIPP_UHR)

    def test_nach_dem_rufen_beginnt_das_naechste_intervall(self):
        koenig = TestGegner(leben=500.0, ist_boss=True)
        beschwoerer = self.erzeuge("Beschwoerer", 2.0, "ork", 3)
        erwartet = [[], ["ork"] * 3, [], ["ork"] * 3, [], ["ork"] * 3]
        for schritt, liste in enumerate(erwartet, start=1):
            self.aktualisiere(
                beschwoerer,
                koenig,
                [koenig],
                1.0,
                liste,
                f"Das war Sekunde {schritt}. Bei einem Intervall von 2 Sekunden ruft er in "
                "jeder zweiten Sekunde und dazwischen nicht. " + TIPP_UHR,
            )

    def test_zu_viel_vergangene_zeit_geht_nicht_verloren(self):
        koenig = TestGegner(leben=500.0, ist_boss=True)
        beschwoerer = self.erzeuge("Beschwoerer", 3.0, "ork")
        tipp = (
            "Die Uhr lief so: 3 - 2 = 1, dann 1 - 2 = -1 (rufen, plus 3 macht 2), dann "
            "2 - 2 = 0 (wieder rufen). Zähl das Intervall dazu, statt die Uhr neu zu stellen."
        )
        self.aktualisiere(beschwoerer, koenig, [koenig], 2.0, [], tipp)
        self.aktualisiere(beschwoerer, koenig, [koenig], 2.0, ["ork"], tipp)
        self.aktualisiere(beschwoerer, koenig, [koenig], 2.0, ["ork"], tipp)
        self.aktualisiere(beschwoerer, koenig, [koenig], 2.0, [], tipp)

    def test_ein_besiegter_beschwoerer_ruft_niemanden(self):
        koenig = TestGegner(leben=0, max_leben=500.0, ist_boss=True)
        beschwoerer = self.erzeuge("Beschwoerer", 2.0, "ork", 2)
        self.aktualisiere(beschwoerer, koenig, [koenig], 2.0, [], TIPP_LEBT)
        self.aktualisiere(beschwoerer, koenig, [koenig], 2.0, [], TIPP_LEBT)

    def test_jeder_beschwoerer_hat_seine_eigene_uhr(self):
        koenig = TestGegner(leben=500.0, ist_boss=True)
        erster = self.erzeuge("Beschwoerer", 2.0, "ork")
        zweiter = self.erzeuge("Beschwoerer", 2.0, "wolf")
        tipp = (
            "Die Uhr gehört zu einem einzelnen Beschwörer: self.rest in __init__, nicht eine "
            "Zahl direkt in der Klasse oder außerhalb."
        )
        self.aktualisiere(erster, koenig, [koenig], 1.5, [], tipp)
        self.aktualisiere(zweiter, koenig, [koenig], 0.5, [], tipp)
        self.aktualisiere(erster, koenig, [koenig], 0.5, ["ork"], tipp)
        self.aktualisiere(zweiter, koenig, [koenig], 0.5, [], tipp)

    def test_der_beschwoerer_heilt_und_verletzt_niemanden(self):
        koenig = TestGegner(leben=300.0, max_leben=500.0, ist_boss=True)
        ork = TestGegner(leben=10.0, max_leben=45.0)
        beschwoerer = self.erzeuge("Beschwoerer", 1.0, "ork")
        self.aktualisiere(beschwoerer, koenig, [koenig, ork], 1.0, ["ork"], TIPP_UHR)
        for gegner in (koenig, ork):
            self.pruefe_heilungen(
                gegner, [], "Beschwoerer.aktualisiere", "Der Beschwörer ruft nur."
            )
            self.pruefe_schaeden(gegner, [], "Beschwoerer.aktualisiere", "Der Beschwörer ruft nur.")
