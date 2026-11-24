"""Die Partie: Phasen, Rechenschritt, Aktionen und Ereignisse."""

import math
import random

from rudersdorf import daten
from rudersdorf.kern.bauwerk import Bauwerk
from rudersdorf.kern.dorf import Dorf
from rudersdorf.kern.gegner import Gegner
from rudersdorf.kern.karte import Karte, lade_karte, lies_raster, zentrum

SUMPF = "%"
HUEGEL = "^"
# In diesen Phasen läuft die Partie: Es wird gebaut, verkauft und gelaufen.
LAUFENDE_PHASEN = ("bauen", "welle")
KEIN_WEG = "Hier nicht: Die Orks brauchen immer einen Weg zum Dorf."


class Spiel:
    """Eine Partie. Alles, was die Ansicht, das Labor und die Tests benutzen, steht hier."""

    def __init__(self, werkbank, karte="flusstal", schwierigkeit="normal", saat=1, kartentext=None):
        self.werkbank = werkbank
        self.schwierigkeit = schwierigkeit
        self.saat = saat
        self.zufall = random.Random(saat)  # der einzige Zufall der Partie
        self.phase = "bauen"  # "bauen", "welle", "sieg" oder "verloren"
        self.welle = 0  # Nummer der zuletzt gestarteten Welle
        self.endlos = False
        self.zeit = 0.0  # gespielte Sekunden
        self.meldung = ""  # der letzte Satz an die Spielerin oder den Spieler
        self.ereignisse = []
        self.dorf = Dorf(schwierigkeit)
        self.bauwerke = {}  # Zelle -> Bauwerk
        self.gegner = []
        self.karte = self._waehle_karte(karte, kartentext)

    def _waehle_karte(self, name, kartentext):
        """Liefert die Karte der Partie: aus dem Text, sonst aus der Datei mit diesem Namen."""
        if kartentext is not None:
            # Ein kaputter Text ist ein Fehler dessen, der ihn hereingibt: ValueError.
            return Karte(lies_raster(kartentext, self.werkbank))
        try:
            return lade_karte(name, self.werkbank)
        except ValueError as fehler:
            # Eine fehlende oder kaputte Kartendatei hält das Spiel nicht auf.
            self.meldung = (
                f"Die Karte {name!r} geht nicht: {fehler} "
                f"Gespielt wird auf der Karte {daten.STANDARD_KARTE}."
            )
            return lade_karte(daten.STANDARD_KARTE, self.werkbank)

    # ----- Der Rechenschritt ------------------------------------------------------------

    def schritt(self, dt: float) -> None:
        """Rechnet die Partie um ``dt`` Sekunden weiter."""
        if self.phase not in LAUFENDE_PHASEN:
            return
        self.zeit = self.zeit + dt
        for gegner in self.gegner:
            self._bewege(gegner, dt)
        self._werte_durchbrueche_aus()

    def _bewege(self, gegner, dt):
        """Lässt einen Gegner ``dt`` Sekunden lang von Zellmitte zu Zellmitte laufen.

        Kommt er mitten im Schritt auf einer Mitte an, fragt er nach der nächsten Zelle und
        läuft mit der restlichen Zeit weiter. So ist die Strecke immer Tempo mal Zeit, egal
        wie groß die Schritte sind.
        """
        zeit = dt
        while zeit > 0:
            if gegner.ziel_zelle is None:
                if gegner.zelle == self.karte.ziel:
                    break  # Er steht auf dem Dorftor: gleich bricht er durch.
                # Den Weg sucht hier niemand neu: Ein Blick in die Abstandskarte genügt.
                gegner.ziel_zelle = self.werkbank.rufe(
                    "wegfindung",
                    "naechster_schritt",
                    self.abstaende(),
                    gegner.zelle,
                    self.karte.breite,
                    self.karte.hoehe,
                )
                if gegner.ziel_zelle is None or gegner.ziel_zelle == gegner.zelle:
                    gegner.ziel_zelle = None
                    break  # Es gibt gerade keinen Schritt: Er wartet.
            tempo = self._tempo(gegner)
            if tempo <= 0:
                break
            ziel_x, ziel_y = zentrum(gegner.ziel_zelle)
            entfernung = math.hypot(ziel_x - gegner.x, ziel_y - gegner.y)
            strecke = tempo * zeit
            if strecke >= entfernung:
                # Angekommen. Die Zeit, die übrig ist, gehört dem nächsten Stück.
                gegner.x = ziel_x
                gegner.y = ziel_y
                gegner.zelle = gegner.ziel_zelle
                gegner.ziel_zelle = None
                zeit = zeit - entfernung / tempo
            else:
                anteil = strecke / entfernung
                gegner.x = gegner.x + (ziel_x - gegner.x) * anteil
                gegner.y = gegner.y + (ziel_y - gegner.y) * anteil
                zeit = 0
        self._miss_rest_weg(gegner)

    def _tempo(self, gegner):
        """Liefert das Tempo des Gegners auf seinem jetzigen Stück in Pixeln pro Sekunde."""
        tempo = gegner.tempo
        # Wer in eine Sumpfzelle hineinläuft, kommt nur langsam voran.
        if self.karte.gelaende(gegner.ziel_zelle) == SUMPF:
            tempo = tempo * daten.SUMPF_TEMPO_FAKTOR
        return tempo

    def _miss_rest_weg(self, gegner):
        """Trägt beim Gegner ein, wie viele Pixel er noch bis zum Dorftor laufen muss."""
        abstaende = self.abstaende()
        if gegner.ziel_zelle is None:
            if gegner.zelle in abstaende:
                gegner.rest_weg = abstaende[gegner.zelle] * daten.ZELLE
        elif gegner.ziel_zelle in abstaende:
            # Erst das Stück bis zur nächsten Mitte, von dort zählt die Abstandskarte.
            ziel_x, ziel_y = zentrum(gegner.ziel_zelle)
            bis_zur_mitte = math.hypot(ziel_x - gegner.x, ziel_y - gegner.y)
            gegner.rest_weg = abstaende[gegner.ziel_zelle] * daten.ZELLE + bis_zur_mitte

    def _miss_alle_wege(self):
        """Nach dem Bauen oder Verkaufen hat sich für alle Gegner der Weg geändert."""
        for gegner in self.gegner:
            self._miss_rest_weg(gegner)

    def _werte_durchbrueche_aus(self):
        """Wer auf der Mitte des Dorftors steht, bricht durch: Das Dorf verliert Leben."""
        uebrig = []
        for gegner in self.gegner:
            # Auf die Zelle des Dorftors kommt nur, wer ihre Mitte erreicht hat.
            if gegner.zelle == self.karte.ziel:
                self.dorf.erleide_schaden(gegner.dorfschaden)
                self.ereignisse.append(
                    {"art": "durchbruch", "schaden": gegner.dorfschaden, "gegner_art": gegner.art}
                )
            else:
                uebrig.append(gegner)
        self.gegner = uebrig

    # ----- Gegner aufstellen ------------------------------------------------------------

    def erzeuge_gegner(self, art: str, zelle=None, start=None) -> Gegner:
        """Stellt einen neuen Gegner auf das Feld und liefert ihn.

        Ohne ``zelle`` erscheint er auf einem Orktor: ``start`` ist die Nummer des Orktors in
        ``karte.starts`` (ohne Angabe das erste).
        """
        if zelle is None:
            if start is None:
                start = 0
            zelle = self.karte.starts[start]
        gegner = Gegner(art, self.werkbank)
        gegner.zelle = tuple(zelle)
        gegner.x, gegner.y = zentrum(gegner.zelle)
        self._miss_rest_weg(gegner)
        self.gegner.append(gegner)
        return gegner

    # ----- Bauen und Verkaufen ----------------------------------------------------------

    def baue(self, art: str, zelle) -> bool:
        """Baut ein Bauwerk auf die Zelle, wenn es erlaubt und bezahlbar ist."""
        if self.phase not in LAUFENDE_PHASEN:
            return self._lehne_ab("Die Partie ist vorbei: Jetzt wird nicht mehr gebaut.")
        if art not in daten.BAUWERKE:
            return self._lehne_ab(f"Ein Bauwerk mit dem Namen {art!r} gibt es nicht.")
        zelle = tuple(zelle)
        besetzt = self._besetzte_zellen()

        # Zuerst wird die Bauregel der Werkstatt gefragt (Mission 5) ...
        erlaubt = self.werkbank.rufe(
            "bauregel",
            "darf_bauen",
            self.karte.raster,
            zelle,
            self.karte.gesperrt,
            self.karte.starts,
            self.karte.ziel,
            besetzt,
        )
        # ... dann schaut der Kern selbst nach. Das ist das Sicherheitsnetz: Auch eine
        # fehlende oder falsche Bauregel darf den Orks nie den Weg zum Dorf nehmen.
        grund = self._hindernis(zelle, besetzt)
        neue_abstaende = None
        if grund is None:
            neue_abstaende = self.karte.abstaende_mit(self.karte.gesperrt | {zelle}, self.werkbank)
            if not self._alle_haben_einen_weg(neue_abstaende, besetzt):
                grund = KEIN_WEG

        if not erlaubt:
            if grund is None:
                grund = self._grund_der_bauregel()
            return self._lehne_ab(grund)
        if grund is not None:
            if not self.werkbank.ist_offen("bauregel"):
                grund = grund + " Deine Bauregel hätte das verbieten müssen (Mission 5)."
            return self._lehne_ab(grund)

        preis = self.preis(art)
        fehlend = self.dorf.fehlende_vorraete(preis)
        if len(fehlend) > 0:
            namen = " und ".join(name.capitalize() for name in fehlend)
            return self._lehne_ab(f"Dafür reicht der Vorrat nicht: Es fehlt {namen}.")
        self.dorf.bezahle(preis)

        bauwerk = Bauwerk(art, zelle, auf_huegel=self.karte.gelaende(zelle) == HUEGEL)
        bauwerk.ausgegeben = preis["gold"]
        self.bauwerke[zelle] = bauwerk
        # Die Abstandskarte mit dem neuen Bauwerk ist schon ausgerechnet: Sie gilt ab jetzt.
        self.karte.sperre(zelle, neue_abstaende)
        self._miss_alle_wege()
        self.meldung = ""
        self.ereignisse.append({"art": "gebaut", "zelle": zelle, "bauwerk_art": art})
        return True

    def _lehne_ab(self, grund):
        """Merkt sich den Grund einer Ablehnung als Meldung und liefert False."""
        self.meldung = grund
        return False

    def _besetzte_zellen(self):
        """Liefert die Zellen, auf denen Gegner stehen oder in die sie gerade laufen."""
        besetzt = set()
        for gegner in self.gegner:
            besetzt.add(gegner.zelle)
            if gegner.ziel_zelle is not None:
                besetzt.add(gegner.ziel_zelle)
        return besetzt

    def _hindernis(self, zelle, besetzt):
        """Liefert, was auf der Zelle selbst gegen ein Bauwerk spricht; ``None``: nichts."""
        if not self.karte.enthaelt(zelle):
            return "Diese Zelle liegt nicht auf der Karte."
        gelaende = self.karte.gelaende(zelle)
        if gelaende not in daten.BEBAUBAR:
            return f"Auf {daten.GELAENDE[gelaende]} kann man nicht bauen."
        if zelle in self.bauwerke:
            return "Hier steht schon ein Bauwerk."
        if zelle in besetzt:
            return "Hier ist gerade ein Gegner unterwegs."
        return None

    def _alle_haben_einen_weg(self, abstaende, besetzt):
        """Sagt, ob in dieser Abstandskarte jedes Orktor und jeder Gegner einen Weg hat."""
        for start in self.karte.starts:
            if start not in abstaende:
                return False
        for zelle in besetzt:
            if zelle not in abstaende:
                return False
        return True

    def _grund_der_bauregel(self):
        """Der Satz für ein Nein der Bauregel, für das der Kern selbst keinen Grund sieht."""
        if self.werkbank.ist_offen("bauregel"):
            return (
                "Solange die Mission 5 offen ist, muss rund um jedes Bauwerk "
                "eine Zelle frei bleiben."
            )
        return "Deine Bauregel (Mission 5) erlaubt hier kein Bauwerk."

    def verkaufe(self, zelle) -> bool:
        """Verkauft das Bauwerk auf der Zelle."""
        zelle = tuple(zelle)
        if self.phase not in LAUFENDE_PHASEN:
            return self._lehne_ab("Die Partie ist vorbei: Jetzt wird nicht mehr verkauft.")
        if zelle not in self.bauwerke:
            return self._lehne_ab("Hier steht kein Bauwerk, das man verkaufen könnte.")
        bauwerk = self.bauwerke.pop(zelle)
        # Zurück gibt es einen Teil des Goldes, abgerundet. Stein gibt es nicht zurück.
        gold = math.floor(daten.VERKAUF_ANTEIL * bauwerk.ausgegeben)
        self.dorf.vorraete["gold"] = self.dorf.vorraete["gold"] + gold
        self.karte.gib_frei(zelle)
        self._miss_alle_wege()
        self.meldung = ""
        self.ereignisse.append(
            {"art": "verkauft", "zelle": zelle, "bauwerk_art": bauwerk.art, "gold": gold}
        )
        return True

    def baue_aus(self, zelle, meister: str | None = None) -> bool:
        """Baut das Bauwerk auf der Zelle aus; ``meister`` wählt den Ausbau der Stufe 3."""
        raise NotImplementedError

    def setze_strategie(self, zelle, name: str) -> bool:
        """Gibt dem Turm auf der Zelle eine andere Zielstrategie."""
        raise NotImplementedError

    def starte_welle(self) -> bool:
        """Startet die nächste Welle."""
        raise NotImplementedError

    def weiter_endlos(self) -> bool:
        """Spielt nach dem Sieg endlos weiter."""
        raise NotImplementedError

    def dorf_ausbau(self, gebaeude: str) -> bool:
        """Kauft die nächste Stufe eines Dorfgebäudes."""
        raise NotImplementedError

    def dorf_info(self, gebaeude: str) -> dict:
        """Liefert nächste Stufe, Kosten, fehlende Voraussetzungen und den Bauplan."""
        raise NotImplementedError

    def zaubere(self, name: str, punkt) -> bool:
        """Wirkt einen Zauber auf einen Punkt."""
        raise NotImplementedError

    def zauber_ausbau(self, name: str) -> bool:
        """Kauft die nächste Stufe eines Zaubers."""
        raise NotImplementedError

    def zauber_info(self) -> dict:
        """Liefert zu jedem Zauber: frei, Stufe, Kosten, Rest der Abklingzeit, bereit."""
        raise NotImplementedError

    def vorschau(self) -> dict:
        """Liefert die Gegner der nächsten Welle: Art -> Anzahl."""
        raise NotImplementedError

    def abstaende(self) -> dict:
        """Liefert die Abstandskarte, nach der die Gegner gerade laufen."""
        return self.karte.abstaende(self.werkbank)

    def preis(self, art: str) -> dict:
        """Liefert den Preis eines Bauwerks, Rabatte schon abgezogen."""
        return dict(daten.BAUWERKE[art]["kosten"])

    def hole_ereignisse(self) -> list:
        """Liefert die Ereignisse seit dem letzten Aufruf und leert die Liste."""
        ereignisse = self.ereignisse
        self.ereignisse = []
        return ereignisse

    def sicht(self) -> dict:
        """Liefert die Partie als einfaches Wörterbuch für einen Bot."""
        raise NotImplementedError

    def fuehre_aus(self, aktion: dict) -> bool:
        """Führt eine Aktion eines Bots aus."""
        raise NotImplementedError

    def statistik(self) -> dict:
        """Liefert erreichte Welle, besiegte Gegner und verdientes Gold."""
        raise NotImplementedError

    def zustand(self) -> dict:
        """Liefert den Stand der Partie als Wörterbuch (Mission 24)."""
        raise NotImplementedError

    def zustand_hash(self) -> str:
        """Liefert einen Fingerabdruck des Stands; gleiche Partien haben denselben."""
        raise NotImplementedError

    def speichere(self, pfad) -> bool:
        """Speichert die Partie in eine Datei."""
        raise NotImplementedError

    def lade(self, pfad) -> bool:
        """Lädt die Partie aus einer Datei."""
        raise NotImplementedError
