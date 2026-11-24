"""Das Dorf: Leben, Vorräte, Stufen der Gebäude und ihre Boni."""

from rudersdorf import daten


class Dorf:
    """Das Dorf einer Partie; Startwerte kommen aus ``daten.SCHWIERIGKEIT``."""

    def __init__(self, schwierigkeit: str):
        werte = daten.SCHWIERIGKEIT[schwierigkeit]
        self.max_leben = werte["dorf_leben"]
        self.leben = self.max_leben
        # Ein eigenes Wörterbuch, damit die Tabelle der Startwerte bleibt, wie sie ist.
        self.vorraete = {
            "gold": werte["start"]["gold"],
            "stein": werte["start"]["stein"],
            "mana": 0,
        }

    def heile(self, menge) -> int:
        """Gibt dem Dorf Leben zurück, höchstens bis zum vollen Leben."""
        geheilt = max(0, min(menge, self.max_leben - self.leben))
        self.leben = self.leben + geheilt
        return geheilt

    def erleide_schaden(self, menge):
        """Zieht dem Dorf Leben ab, nie unter 0."""
        verloren = max(0, min(menge, self.leben))
        self.leben = self.leben - verloren
        return verloren

    def fehlende_vorraete(self, kosten):
        """Liefert die Namen der Vorräte, von denen für diese Kosten zu wenig da ist."""
        fehlend = []
        for name, menge in kosten.items():
            if self.vorraete.get(name, 0) < menge:
                fehlend.append(name)
        return fehlend

    def kann_bezahlen(self, kosten):
        """Sagt, ob die Vorräte für diese Kosten reichen."""
        return len(self.fehlende_vorraete(kosten)) == 0

    def bezahle(self, kosten) -> bool:
        """Zieht die Kosten ab, wenn die Vorräte reichen; sonst bleibt alles, wie es war."""
        if not self.kann_bezahlen(kosten):
            return False
        for name, menge in kosten.items():
            self.vorraete[name] = self.vorraete[name] - menge
        return True
