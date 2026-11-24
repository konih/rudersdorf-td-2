"""Spur C · Die Horde: Schaden, Frost, Gift und die Tricks der Orks.

Hier liegen die Missionen 11 bis 15. Was genau zu tun ist, steht in
missionen/spur_c_horde.md. Prüfen:  python pruefen.py 11

Ein Gegner kennt sein leben, sein x und y und seine Liste effekte. Schaden bekommt er
mit gegner.erleide_schaden(menge, art), Heilung mit gegner.heile(menge).
"""

from math import hypot

from rudersdorf.fehler import NochOffen


def berechne_schaden(schaden, art, resistenzen):
    """Mission 11: Schadensarten. Rechnet aus, wie viel Schaden wirklich ankommt."""
    raise NochOffen("Mission 11: Schadensarten")


class Effekt:
    """Mission 12: Effekte. Etwas, das eine Zeit lang auf einem Gegner liegt."""

    def __init__(self, dauer):
        """Merkt sich die Dauer und wie viel davon noch übrig ist."""
        raise NochOffen("Mission 12: Effekte")

    def tick(self, gegner, sekunden):
        """Lässt die Zeit vergehen."""
        raise NochOffen("Mission 12: Effekte")

    def ist_vorbei(self):
        """Sagt, ob der Effekt abgelaufen ist."""
        raise NochOffen("Mission 12: Effekte")

    def tempo_faktor(self):
        """Sagt, wie schnell der Gegner mit diesem Effekt noch läuft (1.0 ist normal)."""
        raise NochOffen("Mission 12: Effekte")


class Frost(Effekt):
    """Mission 12: Effekte. Frost macht einen Gegner langsamer."""

    def __init__(self, dauer, faktor):
        """Merkt sich zusätzlich, wie stark der Frost bremst."""
        raise NochOffen("Mission 12: Effekte")

    def tempo_faktor(self):
        """Bremst, solange der Frost anhält."""
        raise NochOffen("Mission 12: Effekte")


class Gift(Effekt):
    """Mission 12: Effekte. Gift schadet einem Gegner Sekunde für Sekunde."""

    def __init__(self, dauer, schaden_pro_sekunde):
        """Merkt sich zusätzlich, wie viel Schaden das Gift pro Sekunde macht."""
        raise NochOffen("Mission 12: Effekte")

    def tick(self, gegner, sekunden):
        """Fügt dem Gegner Schaden zu und lässt dann die Zeit vergehen."""
        raise NochOffen("Mission 12: Effekte")


class Brand(Gift):
    """Mission 12: Effekte. Brand wirkt wie Gift, nur mit Feuer."""


class Betaeubung(Effekt):
    """Mission 12: Effekte. Ein betäubter Gegner bleibt stehen."""

    def __init__(self, dauer):
        """Merkt sich die Dauer wie jeder Effekt."""
        raise NochOffen("Mission 12: Effekte")

    def tempo_faktor(self):
        """Hält den Gegner an, solange die Betäubung wirkt."""
        raise NochOffen("Mission 12: Effekte")


def fuege_effekt_hinzu(effekte, neu):
    """Mission 13: Die Effektliste. Legt einen Effekt in die Liste, aber nie doppelt."""
    raise NochOffen("Mission 13: Die Effektliste")


def gesamt_tempo_faktor(effekte):
    """Mission 13: Die Effektliste. Findet heraus, wie stark alle Effekte zusammen bremsen."""
    raise NochOffen("Mission 13: Die Effektliste")


def raeume_effekte_auf(effekte):
    """Mission 13: Die Effektliste. Liefert eine Liste ohne die abgelaufenen Effekte."""
    raise NochOffen("Mission 13: Die Effektliste")


class Regeneration:
    """Mission 14: Besondere Fähigkeiten. Der Troll heilt sich selbst."""

    def __init__(self, pro_sekunde):
        """Merkt sich, wie viel Leben pro Sekunde zurückkommt."""
        raise NochOffen("Mission 14: Besondere Fähigkeiten")

    def aktualisiere(self, traeger, alle, sekunden):
        """Heilt den Träger und liefert die Liste der Gegner, die neu erscheinen sollen."""
        raise NochOffen("Mission 14: Besondere Fähigkeiten")


class Heiler:
    """Mission 14: Besondere Fähigkeiten. Der Schamane heilt die Gegner um sich herum."""

    def __init__(self, radius, pro_sekunde):
        """Merkt sich, wie weit und wie stark die Heilung wirkt."""
        raise NochOffen("Mission 14: Besondere Fähigkeiten")

    def aktualisiere(self, traeger, alle, sekunden):
        """Heilt die anderen in der Nähe und liefert, wer neu erscheinen soll."""
        raise NochOffen("Mission 14: Besondere Fähigkeiten")


class Beschwoerer:
    """Mission 14: Besondere Fähigkeiten. Der Orkkönig ruft Verstärkung herbei."""

    def __init__(self, intervall, art, anzahl=1):
        """Merkt sich, wie oft, wen und wie viele er ruft."""
        raise NochOffen("Mission 14: Besondere Fähigkeiten")

    def aktualisiere(self, traeger, alle, sekunden):
        """Zählt die Zeit herunter und liefert die Arten der Gegner, die jetzt erscheinen."""
        raise NochOffen("Mission 14: Besondere Fähigkeiten")


def erzeuge_welle(nummer, budget, katalog, zufall):
    """Mission 15: Die Wellenschmiede. Kauft mit dem Budget die Gegner der nächsten Welle."""
    raise NochOffen("Mission 15: Die Wellenschmiede")
