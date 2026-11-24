"""Referenz zu Spur D · Dorf und Magie (Missionen 19 und 20).

Hier entsteht die vollständige Lösung. Solange eine Mission noch nicht gebaut ist,
meldet sie sich als offen, und das Spiel benutzt den Ersatz.
"""

from rudersdorf.fehler import NochOffen


class Zauber:
    """Mission 19: Mana und Abklingzeit. Ein Zauber kostet Mana und braucht danach Pause."""

    def __init__(self, name, kosten, abklingzeit):
        """Merkt sich Name, Kosten und Abklingzeit; am Anfang ist der Zauber bereit."""
        raise NochOffen("Referenz folgt: Mission 19")

    def bereit(self, mana):
        """Sagt, ob der Zauber jetzt gewirkt werden kann."""
        raise NochOffen("Referenz folgt: Mission 19")

    def tick(self, sekunden):
        """Lässt die Abklingzeit ablaufen."""
        raise NochOffen("Referenz folgt: Mission 19")

    def wirke(self, punkt, gegner, dorf):
        """Das, was der Zauber tut. Jeder echte Zauber bringt sein eigenes wirke mit."""
        raise NochOffen("Referenz folgt: Mission 19")

    def zaubere(self, mana, punkt, gegner, dorf):
        """Wirkt den Zauber, wenn er bereit ist, und liefert das Mana, das übrig bleibt."""
        raise NochOffen("Referenz folgt: Mission 19")


class Feuerball(Zauber):
    """Mission 20: Das Zauberbuch. Ein Feuerball trifft alle Gegner in einem Kreis."""

    def __init__(self, kosten, abklingzeit, radius, schaden, brand_dauer, brand_schaden):
        """Merkt sich die Werte des Feuerballs."""
        raise NochOffen("Referenz folgt: Mission 20")

    def wirke(self, punkt, gegner, dorf):
        """Verbrennt die Gegner im Kreis und liefert, wie viele getroffen wurden."""
        raise NochOffen("Referenz folgt: Mission 20")


class Eissturm(Zauber):
    """Mission 20: Das Zauberbuch. Ein Eissturm lässt alle Gegner in einem Kreis frieren."""

    def __init__(self, kosten, abklingzeit, radius, dauer, faktor):
        """Merkt sich die Werte des Eissturms."""
        raise NochOffen("Referenz folgt: Mission 20")

    def wirke(self, punkt, gegner, dorf):
        """Legt Frost auf die Gegner im Kreis und liefert, wie viele getroffen wurden."""
        raise NochOffen("Referenz folgt: Mission 20")


class Blitzschlag(Zauber):
    """Mission 20: Das Zauberbuch. Ein Blitz schlägt ein und springt von Gegner zu Gegner."""

    def __init__(self, kosten, abklingzeit, schaden, spruenge, sprungweite):
        """Merkt sich die Werte des Blitzschlags."""
        raise NochOffen("Referenz folgt: Mission 20")

    def wirke(self, punkt, gegner, dorf):
        """Trifft die Kette der Gegner und liefert, wie viele getroffen wurden."""
        raise NochOffen("Referenz folgt: Mission 20")


class Segen(Zauber):
    """Mission 20: Das Zauberbuch. Der Segen heilt das Dorf."""

    def __init__(self, kosten, abklingzeit, heilung):
        """Merkt sich die Werte des Segens."""
        raise NochOffen("Referenz folgt: Mission 20")

    def wirke(self, punkt, gegner, dorf):
        """Heilt das Dorf und liefert, wie viele Lebenspunkte zurückgekommen sind."""
        raise NochOffen("Referenz folgt: Mission 20")


class Glockenschlag(Zauber):
    """Mission 20: Das Zauberbuch. Die Glocken betäuben alle Gegner außer dem Boss."""

    def __init__(self, kosten, abklingzeit, dauer):
        """Merkt sich die Werte des Glockenschlags."""
        raise NochOffen("Referenz folgt: Mission 20")

    def wirke(self, punkt, gegner, dorf):
        """Betäubt die Gegner und liefert, wie viele getroffen wurden."""
        raise NochOffen("Referenz folgt: Mission 20")
