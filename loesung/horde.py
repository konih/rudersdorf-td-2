"""Referenz zu Spur C · Die Horde (Missionen 11 bis 15).

Hier entsteht die vollständige Lösung. Solange eine Mission noch nicht gebaut ist,
meldet sie sich als offen, und das Spiel benutzt den Ersatz.
"""

from rudersdorf.fehler import NochOffen


def berechne_schaden(schaden, art, resistenzen):
    """Mission 11: Schadensarten. Rechnet aus, wie viel Schaden wirklich ankommt."""
    raise NochOffen("Referenz folgt: Mission 11")


class Effekt:
    """Mission 12: Effekte. Etwas, das eine Zeit lang auf einem Gegner liegt."""

    def __init__(self, dauer):
        """Merkt sich die Dauer und wie viel davon noch übrig ist."""
        raise NochOffen("Referenz folgt: Mission 12")

    def tick(self, gegner, sekunden):
        """Lässt die Zeit vergehen."""
        raise NochOffen("Referenz folgt: Mission 12")

    def ist_vorbei(self):
        """Sagt, ob der Effekt abgelaufen ist."""
        raise NochOffen("Referenz folgt: Mission 12")

    def tempo_faktor(self):
        """Sagt, wie schnell der Gegner mit diesem Effekt noch läuft (1.0 ist normal)."""
        raise NochOffen("Referenz folgt: Mission 12")


class Frost(Effekt):
    """Mission 12: Effekte. Frost macht einen Gegner langsamer."""

    def __init__(self, dauer, faktor):
        """Merkt sich zusätzlich, wie stark der Frost bremst."""
        raise NochOffen("Referenz folgt: Mission 12")

    def tempo_faktor(self):
        """Bremst, solange der Frost anhält."""
        raise NochOffen("Referenz folgt: Mission 12")


class Gift(Effekt):
    """Mission 12: Effekte. Gift schadet einem Gegner Sekunde für Sekunde."""

    def __init__(self, dauer, schaden_pro_sekunde):
        """Merkt sich zusätzlich, wie viel Schaden das Gift pro Sekunde macht."""
        raise NochOffen("Referenz folgt: Mission 12")

    def tick(self, gegner, sekunden):
        """Fügt dem Gegner Schaden zu und lässt dann die Zeit vergehen."""
        raise NochOffen("Referenz folgt: Mission 12")


class Brand(Gift):
    """Mission 12: Effekte. Brand wirkt wie Gift, nur mit Feuer."""


class Betaeubung(Effekt):
    """Mission 12: Effekte. Ein betäubter Gegner bleibt stehen."""

    def __init__(self, dauer):
        """Merkt sich die Dauer wie jeder Effekt."""
        raise NochOffen("Referenz folgt: Mission 12")

    def tempo_faktor(self):
        """Hält den Gegner an, solange die Betäubung wirkt."""
        raise NochOffen("Referenz folgt: Mission 12")


def fuege_effekt_hinzu(effekte, neu):
    """Mission 13: Die Effektliste. Legt einen Effekt in die Liste, aber nie doppelt."""
    raise NochOffen("Referenz folgt: Mission 13")


def gesamt_tempo_faktor(effekte):
    """Mission 13: Die Effektliste. Findet heraus, wie stark alle Effekte zusammen bremsen."""
    raise NochOffen("Referenz folgt: Mission 13")


def raeume_effekte_auf(effekte):
    """Mission 13: Die Effektliste. Liefert eine Liste ohne die abgelaufenen Effekte."""
    raise NochOffen("Referenz folgt: Mission 13")


class Regeneration:
    """Mission 14: Besondere Fähigkeiten. Der Troll heilt sich selbst."""

    def __init__(self, pro_sekunde):
        """Merkt sich, wie viel Leben pro Sekunde zurückkommt."""
        raise NochOffen("Referenz folgt: Mission 14")

    def aktualisiere(self, traeger, alle, sekunden):
        """Heilt den Träger und liefert die Liste der Gegner, die neu erscheinen sollen."""
        raise NochOffen("Referenz folgt: Mission 14")


class Heiler:
    """Mission 14: Besondere Fähigkeiten. Der Schamane heilt die Gegner um sich herum."""

    def __init__(self, radius, pro_sekunde):
        """Merkt sich, wie weit und wie stark die Heilung wirkt."""
        raise NochOffen("Referenz folgt: Mission 14")

    def aktualisiere(self, traeger, alle, sekunden):
        """Heilt die anderen in der Nähe und liefert, wer neu erscheinen soll."""
        raise NochOffen("Referenz folgt: Mission 14")


class Beschwoerer:
    """Mission 14: Besondere Fähigkeiten. Der Orkkönig ruft Verstärkung herbei."""

    def __init__(self, intervall, art, anzahl=1):
        """Merkt sich, wie oft, wen und wie viele er ruft."""
        raise NochOffen("Referenz folgt: Mission 14")

    def aktualisiere(self, traeger, alle, sekunden):
        """Zählt die Zeit herunter und liefert die Arten der Gegner, die jetzt erscheinen."""
        raise NochOffen("Referenz folgt: Mission 14")


def erzeuge_welle(nummer, budget, katalog, zufall):
    """Mission 15: Die Wellenschmiede. Kauft mit dem Budget die Gegner der nächsten Welle."""
    raise NochOffen("Referenz folgt: Mission 15")
