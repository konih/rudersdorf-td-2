"""Spur D · Dorf und Magie: Die Zauber der Kirche von Rudersdorf.

Hier liegen die Missionen 19 und 20. Was genau zu tun ist, steht in
missionen/spur_d_dorf_und_magie.md. Prüfen:  python pruefen.py 19

Mission 20 baut auf deinen Lösungen der Missionen 9, 12 und 13 auf. Darum sind
kettenblitz, die Effekte und fuege_effekt_hinzu hier schon importiert.
"""

from math import hypot

from rudersdorf.fehler import NochOffen

from .horde import Betaeubung, Brand, Frost, fuege_effekt_hinzu
from .tuerme import kettenblitz


class Zauber:
    """Mission 19: Mana und Abklingzeit. Ein Zauber kostet Mana und braucht danach Pause."""

    def __init__(self, name, kosten, abklingzeit):
        """Merkt sich Name, Kosten und Abklingzeit; am Anfang ist der Zauber bereit."""
        raise NochOffen("Mission 19: Mana und Abklingzeit")

    def bereit(self, mana):
        """Sagt, ob der Zauber jetzt gewirkt werden kann."""
        raise NochOffen("Mission 19: Mana und Abklingzeit")

    def tick(self, sekunden):
        """Lässt die Abklingzeit ablaufen."""
        raise NochOffen("Mission 19: Mana und Abklingzeit")

    def wirke(self, punkt, gegner, dorf):
        """Das, was der Zauber tut. Jeder echte Zauber bringt sein eigenes wirke mit."""
        raise NochOffen("Mission 19: Mana und Abklingzeit")

    def zaubere(self, mana, punkt, gegner, dorf):
        """Wirkt den Zauber, wenn er bereit ist, und liefert das Mana, das übrig bleibt."""
        raise NochOffen("Mission 19: Mana und Abklingzeit")


class Feuerball(Zauber):
    """Mission 20: Das Zauberbuch. Ein Feuerball trifft alle Gegner in einem Kreis."""

    def __init__(self, kosten, abklingzeit, radius, schaden, brand_dauer, brand_schaden):
        """Merkt sich die Werte des Feuerballs."""
        raise NochOffen("Mission 20: Das Zauberbuch")

    def wirke(self, punkt, gegner, dorf):
        """Verbrennt die Gegner im Kreis und liefert, wie viele getroffen wurden."""
        raise NochOffen("Mission 20: Das Zauberbuch")


class Eissturm(Zauber):
    """Mission 20: Das Zauberbuch. Ein Eissturm lässt alle Gegner in einem Kreis frieren."""

    def __init__(self, kosten, abklingzeit, radius, dauer, faktor):
        """Merkt sich die Werte des Eissturms."""
        raise NochOffen("Mission 20: Das Zauberbuch")

    def wirke(self, punkt, gegner, dorf):
        """Legt Frost auf die Gegner im Kreis und liefert, wie viele getroffen wurden."""
        raise NochOffen("Mission 20: Das Zauberbuch")


class Blitzschlag(Zauber):
    """Mission 20: Das Zauberbuch. Ein Blitz schlägt ein und springt von Gegner zu Gegner."""

    def __init__(self, kosten, abklingzeit, schaden, spruenge, sprungweite):
        """Merkt sich die Werte des Blitzschlags."""
        raise NochOffen("Mission 20: Das Zauberbuch")

    def wirke(self, punkt, gegner, dorf):
        """Trifft die Kette der Gegner und liefert, wie viele getroffen wurden."""
        raise NochOffen("Mission 20: Das Zauberbuch")


class Segen(Zauber):
    """Mission 20: Das Zauberbuch. Der Segen heilt das Dorf."""

    def __init__(self, kosten, abklingzeit, heilung):
        """Merkt sich die Werte des Segens."""
        raise NochOffen("Mission 20: Das Zauberbuch")

    def wirke(self, punkt, gegner, dorf):
        """Heilt das Dorf und liefert, wie viele Lebenspunkte zurückgekommen sind."""
        raise NochOffen("Mission 20: Das Zauberbuch")


class Glockenschlag(Zauber):
    """Mission 20: Das Zauberbuch. Die Glocken betäuben alle Gegner außer dem Boss."""

    def __init__(self, kosten, abklingzeit, dauer):
        """Merkt sich die Werte des Glockenschlags."""
        raise NochOffen("Mission 20: Das Zauberbuch")

    def wirke(self, punkt, gegner, dorf):
        """Betäubt die Gegner und liefert, wie viele getroffen wurden."""
        raise NochOffen("Mission 20: Das Zauberbuch")
