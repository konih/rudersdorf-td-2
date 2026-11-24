"""Referenz zu Spur A · Das Raster (Missionen 1 bis 5).

Eine Zelle ist ein Paar (spalte, zeile). Das Raster ist eine Liste von Zeilen,
man liest es mit raster[zeile][spalte].
"""

from collections import deque

from rudersdorf.daten import BEBAUBAR, BEGEHBAR


def lies_karte(text):
    """Mission 1: Die Karte lesen. Macht aus dem Kartentext ein Raster aus Zeichen."""
    raster = []
    for zeile in text.splitlines():
        # Leerzeichen am Ende einer Zeile sieht man im Editor nicht. Sie gehören nicht zur Karte.
        zeile = zeile.rstrip()
        # Eine leere Zeile ist keine Kartenzeile, sie wird übersprungen.
        if zeile != "":
            raster.append(list(zeile))

    if len(raster) == 0:
        raise ValueError("Die Karte ist leer: Im Text steht keine einzige Kartenzeile.")

    # Alle Zeilen müssen so lang sein wie die erste, sonst hat die Karte Löcher.
    breite = len(raster[0])
    nummer = 1
    for zeile in raster:
        if len(zeile) != breite:
            raise ValueError(
                f"Kartenzeile {nummer} hat {len(zeile)} Zeichen, die erste Zeile hat {breite}."
            )
        nummer = nummer + 1

    return raster


def finde(raster, zeichen):
    """Mission 1: Die Karte lesen. Sucht alle Zellen, in denen dieses Zeichen steht."""
    gefunden = []
    # Erst die Zeilen von oben nach unten, in jeder Zeile die Spalten von links nach rechts.
    for zeile in range(len(raster)):
        for spalte in range(len(raster[zeile])):
            if raster[zeile][spalte] == zeichen:
                # Eine Zelle nennt immer zuerst die Spalte und dann die Zeile.
                gefunden.append((spalte, zeile))
    return gefunden


def nachbarn(zelle, breite, hoehe):
    """Mission 2: Nachbarn. Liefert die Zellen oben, rechts, unten und links von der Zelle."""
    spalte, zeile = zelle
    # Die Reihenfolge ist fest: oben, rechts, unten, links. Die Wegsuche verlässt sich darauf.
    kandidaten = [
        (spalte, zeile - 1),
        (spalte + 1, zeile),
        (spalte, zeile + 1),
        (spalte - 1, zeile),
    ]

    ergebnis = []
    for nachbar_spalte, nachbar_zeile in kandidaten:
        # Nur Zellen, die auf der Karte liegen, sind Nachbarn.
        if 0 <= nachbar_spalte < breite and 0 <= nachbar_zeile < hoehe:
            ergebnis.append((nachbar_spalte, nachbar_zeile))
    return ergebnis


def ist_begehbar(raster, zelle, gesperrt):
    """Mission 2: Nachbarn. Sagt, ob ein Ork diese Zelle betreten kann."""
    spalte, zeile = zelle
    hoehe = len(raster)
    breite = len(raster[0])

    # Zuerst prüfen, ob die Zelle auf der Karte liegt. Das muss vor dem Nachschauen im Raster
    # passieren: raster[-1] wäre für Python kein Fehler, sondern die letzte Zeile.
    if spalte < 0 or spalte >= breite:
        return False
    if zeile < 0 or zeile >= hoehe:
        return False

    # Auf einer gesperrten Zelle steht ein Bauwerk. Da kommt kein Ork durch.
    if zelle in gesperrt:
        return False

    # Sonst entscheidet das Gelände: Wiese, Sumpf, Hügel und die Tore sind begehbar.
    return raster[zeile][spalte] in BEGEHBAR


def abstandskarte(raster, ziel, gesperrt):
    """Mission 3: Der kürzeste Weg. Zählt für jede Zelle die Schritte bis zum Ziel."""
    hoehe = len(raster)
    breite = len(raster[0])

    # Die Suche beginnt am Ziel und breitet sich von dort aus wie eine Welle im Wasser.
    abstaende = {ziel: 0}

    # Warum eine Warteschlange? Wer zuerst hineinkommt, ist zuerst dran. So werden erst alle
    # Zellen mit Abstand 1 besucht, dann alle mit Abstand 2 und so weiter. Darum ist der erste
    # Abstand, den eine Zelle bekommt, auch ihr kürzester.
    warteschlange = deque()
    warteschlange.append(ziel)

    while len(warteschlange) > 0:
        zelle = warteschlange.popleft()
        for nachbar in nachbarn(zelle, breite, hoehe):
            # Warum die Prüfung "schon besucht"? Eine Zelle, die schon einen Abstand hat, wurde
            # auf einem kürzeren oder gleich langen Weg erreicht. Ohne diese Prüfung würde die
            # Suche zwischen zwei Nachbarn endlos hin und her laufen.
            if nachbar not in abstaende:
                if ist_begehbar(raster, nachbar, gesperrt):
                    abstaende[nachbar] = abstaende[zelle] + 1
                    warteschlange.append(nachbar)

    return abstaende


def naechster_schritt(abstaende, zelle, breite, hoehe):
    """Mission 4: Dem Weg folgen. Wählt die Nachbarzelle, die näher am Ziel liegt."""
    # Von einer Zelle ohne Abstand führt kein Weg zum Ziel.
    if zelle not in abstaende:
        return None

    eigener_abstand = abstaende[zelle]
    # Am Ziel gibt es keinen Schritt mehr.
    if eigener_abstand == 0:
        return None

    bester = None
    bester_abstand = eigener_abstand
    for nachbar in nachbarn(zelle, breite, hoehe):
        # Nachbarn ohne Abstand sind Fels, Wasser, Bauwerke oder abgeschnitten.
        if nachbar in abstaende:
            # Nur echt kleiner zählt. So gewinnt bei Gleichstand der Nachbar, der in der
            # Reihenfolge oben, rechts, unten, links zuerst kommt, und bergauf geht es nie.
            if abstaende[nachbar] < bester_abstand:
                bester = nachbar
                bester_abstand = abstaende[nachbar]
    return bester


def darf_bauen(raster, zelle, gesperrt, starts, ziel, besetzt):
    """Mission 5: Nicht einmauern! Erlaubt ein Bauwerk nur, wenn alle Wege offen bleiben."""
    spalte, zeile = zelle
    hoehe = len(raster)
    breite = len(raster[0])

    # Die einfachen Gründe zuerst. Wie bei ist_begehbar kommt die Karte vor dem Gelände,
    # weil eine negative Zahl sonst von hinten zählt.
    if spalte < 0 or spalte >= breite:
        return False
    if zeile < 0 or zeile >= hoehe:
        return False
    # Gebaut wird nur auf Wiese und Hügel.
    if raster[zeile][spalte] not in BEBAUBAR:
        return False
    # Hier steht schon ein Bauwerk.
    if zelle in gesperrt:
        return False
    # Hier steht gerade ein Ork, oder er ist auf dem Weg hierher.
    if zelle in besetzt:
        return False

    # Jetzt die Probe: Wir tun so, als stünde das Bauwerk schon da. Dafür brauchen wir eine
    # neue Menge. In gesperrt selbst dürfen wir nichts eintragen, das gehört dem Spiel.
    probe = set(gesperrt)
    probe.add(zelle)
    abstaende = abstandskarte(raster, ziel, probe)

    # Jedes Orktor braucht weiter einen Weg zum Dorf.
    for start in starts:
        if start not in abstaende:
            return False
    # Und kein Ork, der schon unterwegs ist, darf eingesperrt werden.
    for ork_zelle in besetzt:
        if ork_zelle not in abstaende:
            return False

    return True
