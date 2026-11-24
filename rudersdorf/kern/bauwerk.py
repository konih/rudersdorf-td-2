"""Ein Bauwerk auf dem Spielfeld: ein Turm oder eine Palisade."""

from rudersdorf import daten
from rudersdorf.kern.karte import zentrum


class Bauwerk:
    """Ein Bauwerk; seine Werte kommen aus ``daten.BAUWERKE[art]``."""

    def __init__(self, art: str, zelle, auf_huegel=False):
        self.art = art
        self.zelle = zelle
        self.x, self.y = zentrum(zelle)
        self.stufe = 1
        self.meister = None  # der Ausbau der Stufe 3, sobald er gewählt ist
        self.strategie = None  # die Zielstrategie; die Partie trägt sie ein
        # Eine eigene Kopie der Werte: Ausbauten und der Hügel ändern nur dieses Bauwerk.
        self.werte = dict(daten.BAUWERKE[art]["werte"])
        if auf_huegel and "reichweite" in self.werte:
            self.werte["reichweite"] = self.werte["reichweite"] * daten.HUEGEL_REICHWEITE_FAKTOR
        self.ausgegeben = 0  # so viel Gold steckt im Bauwerk; die Partie trägt es ein
        self.abklingzeit = 0.0  # Sekunden bis zum nächsten Schuss
        self.winkel = 0.0  # wohin der Turm zuletzt gezielt hat (nur für das Bild)
