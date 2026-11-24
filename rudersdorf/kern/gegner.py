"""Ein Gegner auf dem Spielfeld."""


class Gegner:
    """Ein Gegner; seine Werte kommen aus ``daten.GEGNER[art]``."""

    def __init__(self, art: str, werkbank, leben_faktor=1.0):
        raise NotImplementedError

    def erleide_schaden(self, menge, art) -> float:
        """Zieht den Schaden nach den Resistenzen ab und liefert das verlorene Leben."""
        raise NotImplementedError

    def heile(self, menge):
        """Gibt Leben zurück, höchstens bis zum vollen Leben."""
        raise NotImplementedError

    def ist_besiegt(self):
        """Sagt, ob der Gegner kein Leben mehr hat."""
        raise NotImplementedError
