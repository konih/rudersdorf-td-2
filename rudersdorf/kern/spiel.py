"""Die Partie: Phasen, Rechenschritt, Aktionen und Ereignisse."""

from rudersdorf.kern.gegner import Gegner


class Spiel:
    """Eine Partie. Alles, was die Ansicht, das Labor und die Tests benutzen, steht hier."""

    def __init__(self, werkbank, karte="flusstal", schwierigkeit="normal", saat=1, kartentext=None):
        raise NotImplementedError

    def schritt(self, dt: float) -> None:
        """Rechnet die Partie um ``dt`` Sekunden weiter."""
        raise NotImplementedError

    def erzeuge_gegner(self, art: str, zelle=None, start=None) -> Gegner:
        """Stellt einen neuen Gegner auf das Feld und liefert ihn."""
        raise NotImplementedError

    def baue(self, art: str, zelle) -> bool:
        """Baut ein Bauwerk auf die Zelle, wenn es erlaubt und bezahlbar ist."""
        raise NotImplementedError

    def verkaufe(self, zelle) -> bool:
        """Verkauft das Bauwerk auf der Zelle."""
        raise NotImplementedError

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
        raise NotImplementedError

    def preis(self, art: str) -> dict:
        """Liefert den Preis eines Bauwerks, Rabatte schon abgezogen."""
        raise NotImplementedError

    def hole_ereignisse(self) -> list:
        """Liefert die Ereignisse seit dem letzten Aufruf und leert die Liste."""
        raise NotImplementedError

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
