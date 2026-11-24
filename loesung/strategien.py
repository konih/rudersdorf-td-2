"""Referenz zu Spur B · Die Türme (Missionen 7 und 8).

Alle Strategien hier benutzen min() oder max() mit einem Schlüssel. Der Schlüssel (key) ist
eine Funktion: Sie bekommt einen Gegner und liefert die Zahl, nach der verglichen wird.
Haben zwei Gegner dieselbe Zahl, nehmen min() und max() den, der in der Liste früher steht.
Genau das verlangt die Mission bei Gleichstand.
"""

from .tuerme import _abstand

# --- Die Schlüssel: Was wird an einem Gegner verglichen? -------------------------------------


def _rest_weg(gegner):
    """Schlüssel: wie weit der Gegner noch bis zum Dorf laufen muss."""
    return gegner.rest_weg


def _leben(gegner):
    """Schlüssel: wie viel Leben der Gegner jetzt gerade hat."""
    return gegner.leben


# --- Mission 7: die fünf Regeln --------------------------------------------------------------


def erster(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner, der dem Dorf am nächsten ist."""
    # min() und max() melden bei einer leeren Liste einen Fehler. Darum kommt diese Frage
    # in jeder Strategie zuerst.
    if len(kandidaten) == 0:
        return None
    return min(kandidaten, key=_rest_weg)


def letzter(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner, der noch am weitesten laufen muss."""
    if len(kandidaten) == 0:
        return None
    return max(kandidaten, key=_rest_weg)


def staerkster(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner mit dem meisten Leben."""
    if len(kandidaten) == 0:
        return None
    return max(kandidaten, key=_leben)


def schwaechster(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner mit dem wenigsten Leben."""
    if len(kandidaten) == 0:
        return None
    return min(kandidaten, key=_leben)


def naechster(kandidaten, turm):
    """Mission 7: Zielstrategien. Wählt den Gegner, der dem Turm am nächsten steht."""
    if len(kandidaten) == 0:
        return None
    # Dieser Schlüssel braucht außer dem Gegner auch den Turm. Eine Funktion wie _leben
    # oben kennt den Turm nicht. Ein lambda ist eine kleine Funktion ohne Namen, die genau
    # hier entsteht und darum turm benutzen kann.
    return min(kandidaten, key=lambda gegner: _abstand(turm.x, turm.y, gegner.x, gegner.y))


# --- Mission 8: eine eigene Regel ------------------------------------------------------------


def gefaehrlichster(kandidaten, turm):
    """Mission 8: Deine eigene Strategie. Wählt aus der Vorhut den Gegner mit dem meisten Leben.

    Die Vorhut sind die Gegner, die dem Dorf schon am nächsten sind: das vorderste Viertel
    zwischen dem kleinsten und dem größten Restweg. Wer weit vorn ist und viel aushält,
    ist für das Dorf am gefährlichsten.
    """
    if len(kandidaten) == 0:
        return None

    # Wo endet das vorderste Viertel?
    kleinster = min(kandidaten, key=_rest_weg).rest_weg
    groesster = max(kandidaten, key=_rest_weg).rest_weg
    grenze = kleinster + 0.25 * (groesster - kleinster)

    # Die Vorhut einsammeln. Der Gegner mit dem kleinsten Restweg gehört immer dazu,
    # die Vorhut ist also nie leer.
    vorhut = []
    for gegner in kandidaten:
        if gegner.rest_weg <= grenze:
            vorhut.append(gegner)

    return max(vorhut, key=_leben)


# Das Spiel zeigt diese Namen im Menü eines Turms an.
STRATEGIEN = {
    "erster": erster,
    "letzter": letzter,
    "staerkster": staerkster,
    "schwaechster": schwaechster,
    "naechster": naechster,
    "gefaehrlichster": gefaehrlichster,
}
