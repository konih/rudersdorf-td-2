"""Referenz zu Spur B · Die Türme (Missionen 6, 9 und 10).

Ein Punkt ist ein Paar (x, y) in Pixeln. Ein Gegner hat seinen Platz in gegner.x und gegner.y.
"""

import math


def _abstand(x1, y1, x2, y2):
    """Hilfsfunktion: die Länge der geraden Linie zwischen den Punkten (x1, y1) und (x2, y2)."""
    # Der Satz des Pythagoras: Die beiden Unterschiede sind die kurzen Seiten eines
    # rechtwinkligen Dreiecks, der Abstand ist die lange Seite.
    unterschied_x = x2 - x1
    unterschied_y = y2 - y1
    return math.sqrt(unterschied_x * unterschied_x + unterschied_y * unterschied_y)


def in_reichweite(position, reichweite, gegner):
    """Mission 6: Wer ist in Reichweite? Liefert die lebenden Gegner, die nah genug sind."""
    turm_x, turm_y = position

    # Immer eine neue Liste bauen. Die Liste gegner gehört dem Spiel und bleibt, wie sie ist.
    ergebnis = []
    for einer in gegner:
        # Ein besiegter Gegner ist kein Ziel mehr.
        if einer.leben <= 0:
            continue
        # "<=" und nicht "<": Wer genau auf dem Rand des Kreises steht, gehört noch dazu.
        if _abstand(turm_x, turm_y, einer.x, einer.y) <= reichweite:
            ergebnis.append(einer)
    return ergebnis


def kettenblitz(start, gegner, spruenge, sprungweite):
    """Mission 9: Der Kettenblitz. Liefert, wen der Blitz der Reihe nach trifft."""
    # Der Start wird immer getroffen, auch wenn er in der Liste gegner gar nicht vorkommt.
    getroffen = [start]

    for _ in range(spruenge):
        # Der Blitz springt immer von dem weiter, den er zuletzt getroffen hat.
        letzter = getroffen[-1]

        # Unter allen, die noch in Frage kommen, den Nächsten suchen.
        naechster = None
        kleinster_abstand = None
        for einer in gegner:
            # Besiegte Gegner überspringt der Blitz.
            if einer.leben <= 0:
                continue
            # Niemand wird zweimal getroffen. Sonst spränge der Blitz hin und her.
            if einer in getroffen:
                continue
            abstand = _abstand(letzter.x, letzter.y, einer.x, einer.y)
            # Zu weit weg für einen Sprung.
            if abstand > sprungweite:
                continue
            # "<" und nicht "<=": Bei gleichem Abstand bleibt es beim Früheren in der Liste.
            if kleinster_abstand is None or abstand < kleinster_abstand:
                naechster = einer
                kleinster_abstand = abstand

        # Ist keiner nah genug, endet die Kette vorzeitig.
        if naechster is None:
            break
        getroffen.append(naechster)

    return getroffen


def wende_ausbau_an(werte, ausbau):
    """Mission 10: Die Turmschmiede. Rechnet aus den Werten eines Turms die verbesserten."""
    # Mit einer Kopie arbeiten. Die alten Werte braucht das Spiel noch, zum Beispiel wenn
    # mitten im Ausbau ein Fehler gemeldet wird.
    neue_werte = dict(werte)

    for name in ausbau:
        # Jeder Eintrag ist ein Paar, zum Beispiel ("+", 5). Hier wird es ausgepackt.
        zeichen, zahl = ausbau[name]

        if zeichen == "=":
            # "=" setzt den Wert. Das geht auch, wenn es den Wert vorher noch nicht gab.
            neue_werte[name] = zahl
        elif zeichen == "+" or zeichen == "*":
            # Rechnen kann man nur mit einem Wert, den der Turm schon hat.
            if name not in werte:
                raise ValueError(
                    f"Der Turm hat keinen Wert {name!r}, mit dem {zeichen!r} rechnen könnte."
                )
            if zeichen == "+":
                neue_werte[name] = werte[name] + zahl
            else:
                neue_werte[name] = werte[name] * zahl
        else:
            raise ValueError(f"Unbekanntes Zeichen {zeichen!r} beim Ausbau von {name!r}.")

    return neue_werte
