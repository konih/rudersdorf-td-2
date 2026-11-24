"""Ein Gegner auf dem Spielfeld."""

from rudersdorf import daten


class Gegner:
    """Ein Gegner; seine Werte kommen aus ``daten.GEGNER[art]``.

    Wo er steht und wohin er läuft, trägt die Partie ein (``Spiel.erzeuge_gegner``).
    Zwei Gegner mit gleichen Werten bleiben zwei verschiedene Gegner: Die Klasse legt mit
    Absicht nicht fest, wann zwei Gegner "gleich" sind.
    """

    def __init__(self, art: str, werkbank, leben_faktor=1.0):
        werte = daten.GEGNER[art]
        self.werkbank = werkbank
        self.art = art
        self.name = werte["name"]
        self.max_leben = werte["leben"] * leben_faktor
        self.leben = self.max_leben
        self.tempo = werte["tempo"]  # Pixel pro Sekunde
        self.belohnung = werte["belohnung"]
        self.dorfschaden = werte["dorfschaden"]
        self.fliegt = werte["fliegt"]
        self.ist_boss = werte["boss"]
        self.bricht = werte["bricht"]
        # Eine eigene Kopie, damit niemand über den Gegner die Tabelle verändert.
        self.resistenzen = dict(werte["resistenzen"])
        self.effekte = []
        self.faehigkeiten = []
        self.abriss_rest = 0.0

        # Der Ort: die Pixel, die Zelle, auf deren Mitte er zuletzt stand, und die Zelle, in
        # die er gerade läuft (None, solange er genau auf einer Mitte steht).
        self.x = 0.0
        self.y = 0.0
        self.zelle = None
        self.ziel_zelle = None
        self.rest_weg = 0.0  # Pixel bis zum Dorftor

    def erleide_schaden(self, menge, art) -> float:
        """Zieht den Schaden nach den Resistenzen ab und liefert das verlorene Leben."""
        schaden = self.werkbank.rufe(
            "schadensarten", "berechne_schaden", menge, art, self.resistenzen
        )
        # Mehr als sein restliches Leben kann niemand verlieren, und Schaden heilt nie.
        verloren = max(0, min(schaden, self.leben))
        self.leben = self.leben - verloren
        return verloren

    def heile(self, menge):
        """Gibt Leben zurück, höchstens bis zum vollen Leben."""
        geheilt = max(0, min(menge, self.max_leben - self.leben))
        self.leben = self.leben + geheilt
        return geheilt

    def ist_besiegt(self):
        """Sagt, ob der Gegner kein Leben mehr hat."""
        return self.leben <= 0
