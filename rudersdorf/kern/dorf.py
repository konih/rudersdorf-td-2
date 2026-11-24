"""Das Dorf: Leben, Vorräte, Stufen der Gebäude und ihre Boni."""


class Dorf:
    """Das Dorf einer Partie; Startwerte kommen aus ``daten.SCHWIERIGKEIT``."""

    def __init__(self, schwierigkeit: str):
        raise NotImplementedError

    def heile(self, menge) -> int:
        """Gibt dem Dorf Leben zurück, höchstens bis zum vollen Leben."""
        raise NotImplementedError

    def erleide_schaden(self, menge):
        """Zieht dem Dorf Leben ab, nie unter 0."""
        raise NotImplementedError

    def kann_bezahlen(self, kosten):
        """Sagt, ob die Vorräte für diese Kosten reichen."""
        raise NotImplementedError

    def bezahle(self, kosten) -> bool:
        """Zieht die Kosten ab, wenn die Vorräte reichen; sonst bleibt alles, wie es war."""
        raise NotImplementedError
