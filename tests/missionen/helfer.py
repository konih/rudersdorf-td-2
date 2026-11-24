"""Hilfen für die Missionstests: das richtige Paket laden, Karten zeichnen, klar melden.

Jede Meldung eines Missionstests hat drei Teile:

    Erwartet: was herauskommen sollte
    Bekommen: was dein Code geliefert hat
    Tipp: ein Hinweis, wo du suchen kannst

Geprüft wird die Werkstatt. Nur mit RUDERSDORF_LOESUNG=1 wird stattdessen die Lösung geprüft.
"""

import importlib
import unittest

from rudersdorf.fehler import NochOffen
from rudersdorf.werkbank import waehle_paket

# ---------------------------------------------------------------------------------------
# 1. Das Paket wählen
# ---------------------------------------------------------------------------------------


def lade_modul(name):
    """Lädt das Modul ``name`` aus dem Paket, das geprüft wird (``werkstatt`` oder ``loesung``)."""
    return importlib.import_module(f"{waehle_paket()}.{name}")


# ---------------------------------------------------------------------------------------
# 2. Meldungen
# ---------------------------------------------------------------------------------------


def meldung(erwartet, bekommen, tipp):
    """Baut die Meldung aus drei Teilen. Sie beginnt in einer neuen Zeile, damit man sie findet."""
    return f"\nErwartet: {erwartet}\nBekommen: {bekommen}\nTipp: {tipp}"


def nur_die_reihenfolge_ist_anders(bekommen, erwartet):
    """Sagt, ob ``bekommen`` dieselben Einträge hat wie die Liste ``erwartet``, nur anders gereiht.

    Die Funktion kommt mit jeder Antwort zurecht, auch mit ``None`` oder einer Liste, in der
    etwas Unpassendes steht. Dann ist die Antwort einfach ``False``.
    """
    if not isinstance(bekommen, list) or len(bekommen) != len(erwartet):
        return False
    if bekommen == erwartet:
        return False
    return all(eintrag in bekommen for eintrag in erwartet)


def fast_gleich(bekommen, erwartet):
    """Sagt, ob ``bekommen`` eine Zahl ist, die bis auf einen winzigen Rundungsrest ``erwartet`` ist.

    Kommazahlen runden ein wenig: 0.1 + 0.2 ist nicht genau 0.3. Darum vergleichen die Tests
    Zahlen so. Die Funktion kommt mit jeder Antwort zurecht: ``None``, ein Text oder ``True``
    sind einfach keine passende Zahl.
    """
    if isinstance(bekommen, bool) or not isinstance(bekommen, (int, float)):
        return False
    return abs(bekommen - erwartet) <= 1e-9


def alle_fast_gleich(bekommen, erwartet):
    """Sagt, ob ``bekommen`` eine Liste aus genau den Zahlen der Liste ``erwartet`` ist."""
    if not isinstance(bekommen, list) or len(bekommen) != len(erwartet):
        return False
    return all(fast_gleich(zahl, soll) for zahl, soll in zip(bekommen, erwartet, strict=True))


def schaeden_fast_gleich(bekommen, erwartet):
    """Sagt, ob die Schäden ``bekommen`` genau die Liste ``erwartet`` aus ``(menge, art)`` sind.

    Auch hier darf in ``bekommen`` stehen, was will: Eine Menge ``None`` passt einfach nicht.
    """
    if not isinstance(bekommen, list) or len(bekommen) != len(erwartet):
        return False
    for eintrag, (menge, art) in zip(bekommen, erwartet, strict=True):
        if not isinstance(eintrag, tuple) or len(eintrag) != 2:
            return False
        if not fast_gleich(eintrag[0], menge) or eintrag[1] != art:
            return False
    return True


def kurz(liste, hoechstens=12):
    """Schreibt eine Liste für eine Meldung auf. Von einer sehr langen zeigt sie nur den Anfang."""
    if not isinstance(liste, list) or len(liste) <= hoechstens:
        return repr(liste)
    anfang = ", ".join(repr(eintrag) for eintrag in liste[:hoechstens])
    return f"[{anfang}, ... und {len(liste) - hoechstens} weitere]"


def wellenfehler(welle, nummer, budget, katalog):
    """Prüft eine Welle aus Mission 15 an den Regeln und liefert den ersten Verstoß.

    Das Ergebnis ist ``None``, wenn alles stimmt, sonst die drei Teile einer Meldung als Tupel
    ``(erwartet, bekommen, tipp)``. Welche Arten genau in der Welle stehen, ist Zufall. Geprüft
    wird darum nur, was für jede richtige Welle gilt:

    - sie ist eine Liste aus Namen von Arten des Katalogs,
    - kein Boss und keine Art, die erst in einer späteren Welle erscheint,
    - alle zusammen kosten höchstens das Budget,
    - für das Geld, das übrig bleibt, gäbe es keinen erlaubten Gegner mehr.

    Die Funktion kommt mit jeder Antwort zurecht, auch mit ``None`` oder einer endlos langen Liste.
    """
    if not isinstance(welle, list):
        return (
            "eine Liste mit den Namen der Arten",
            repr(welle),
            "Beginne mit einer leeren Liste, hänge jeden gekauften Gegner an und gib sie am "
            "Ende mit return zurück.",
        )
    billigster = min((eintrag["preis"] for eintrag in katalog.values()), default=1)
    if len(welle) > max(budget, 0) // billigster:
        return (
            f"höchstens {max(budget, 0) // billigster} Gegner, denn mehr kann man für "
            f"{budget} Münzen gar nicht kaufen (der billigste kostet {billigster})",
            f"eine Welle mit {len(welle)} Gegnern: {kurz(welle)}",
            "Die Welle wächst viel zu lang. Jeder Kauf kostet etwas: Zieh den Preis vom Rest "
            "ab und hör auf, sobald sich niemand mehr bezahlen lässt.",
        )
    for art in welle:
        if not isinstance(art, str) or art not in katalog:
            return (
                f"nur Namen aus dem Katalog: {sorted(katalog)}",
                f"den Eintrag {art!r} in der Welle {kurz(welle)}",
                'In die Welle kommt der Name der Art, also der Schlüssel des Katalogs wie "ork".',
            )
        if katalog[art]["boss"]:
            return (
                "eine Welle ohne Boss",
                f"den Boss {art!r} in der Welle {kurz(welle)}",
                'Ein Boss wird nie gekauft. Lass alle Arten weg, bei denen "boss" True ist.',
            )
        if katalog[art]["ab_welle"] > nummer:
            return (
                f"in Welle {nummer} nur Arten, die schon freigeschaltet sind",
                f"die Art {art!r}, die erst ab Welle {katalog[art]['ab_welle']} erscheint, "
                f"in der Welle {kurz(welle)}",
                'Eine Art darf erst mitlaufen, wenn ihr "ab_welle" höchstens so groß ist wie '
                "die Nummer der Welle.",
            )
    summe = sum(katalog[art]["preis"] for art in welle)
    if summe > max(budget, 0):  # bei einem Budget unter 0 ist die leere Welle richtig
        return (
            f"eine Welle, die höchstens {budget} Münzen kostet",
            f"eine Welle für {summe} Münzen: {kurz(welle)}",
            "Als Kandidat zählt nur, wer höchstens so viel kostet, wie noch übrig ist. "
            "Prüfe das vor jedem Kauf neu.",
        )
    rest = budget - summe
    noch_bezahlbar = sorted(
        art
        for art, eintrag in katalog.items()
        if not eintrag["boss"] and eintrag["ab_welle"] <= nummer and eintrag["preis"] <= rest
    )
    if noch_bezahlbar:
        return (
            f"das Budget {budget} wird ausgegeben, bis sich kein erlaubter Gegner mehr "
            "bezahlen lässt",
            f"es sind noch {rest} Münzen übrig, das reicht für {noch_bezahlbar}; "
            f"die Welle war {kurz(welle)}",
            "Hör erst auf, wenn die Liste der Kandidaten leer ist. Ist nur der gerade "
            "gewählte Gegner zu teuer, passt vielleicht noch ein billigerer.",
        )
    return None


class Missionstest(unittest.TestCase):
    """Die Grundlage aller Missionstests: lädt das Modul und meldet Fehler in drei Teilen."""

    modul = "raster"  # so heißt die Datei in der Werkstatt, ohne ".py"
    longMessage = False  # nur unsere eigene Meldung zeigen, nicht noch eine englische davor

    def setUp(self):
        self.werkstatt = lade_modul(self.modul)

    def pruefe_gleich(self, bekommen, erwartet, aufruf, tipp):
        """Meldet einen Fehler, wenn ``bekommen`` nicht genau ``erwartet`` ist."""
        if bekommen != erwartet:
            self.fail(meldung(f"{aufruf} ergibt {erwartet!r}", repr(bekommen), tipp))

    def pruefe_fehler(self, fehlerart, aufruf, tipp, funktion, *argumente):
        """Ruft ``funktion`` auf und verlangt, dass sie einen Fehler dieser Art meldet."""
        erwartet = f"{aufruf} meldet einen {fehlerart.__name__}"
        try:
            ergebnis = funktion(*argumente)
        except NochOffen:
            raise
        except fehlerart:
            return
        except Exception as fehler:
            self.fail(meldung(erwartet, f"ein {type(fehler).__name__}: {fehler}", tipp))
        self.fail(meldung(erwartet, f"kein Fehler, sondern das Ergebnis {ergebnis!r}", tipp))

    def rufe_sicher(self, aufruf, tipp, funktion, *argumente):
        """Ruft ``funktion`` auf. Stürzt sie ab, gibt es eine Meldung mit Tipp statt nur den Absturz."""
        try:
            return funktion(*argumente)
        except NochOffen:
            raise
        except Exception as fehler:
            self.fail(
                meldung(
                    f"{aufruf} läuft ohne Absturz durch",
                    f"ein {type(fehler).__name__}: {fehler}",
                    tipp,
                )
            )

    def erzeuge(self, klasse, *argumente, tipp=None):
        """Erzeugt ein Objekt der Klasse mit dem Namen ``klasse`` aus der Werkstatt.

        Stürzt das Erzeugen ab, gibt es wie bei ``rufe_sicher`` eine Meldung mit Tipp.
        """
        aufruf = f"{klasse}({', '.join(repr(argument) for argument in argumente)})"
        if tipp is None:
            tipp = (
                f"Der Fehler entsteht beim Erzeugen, also im __init__ von {klasse} oder im "
                "__init__ der Klasse, von der geerbt wird. Weiter oben in der Ausgabe steht "
                "die Zeile in deiner Datei."
            )
        return self.rufe_sicher(aufruf, tipp, lambda: getattr(self.werkstatt, klasse)(*argumente))

    def pruefe_unveraendert(self, vorher, nachher, was, aufruf, tipp):
        """Meldet einen Fehler, wenn der Aufruf etwas verändert hat, das ihm nur geliehen war."""
        if vorher != nachher:
            self.fail(
                meldung(
                    f"{aufruf} lässt {was} so, wie es war: {vorher!r}",
                    f"danach war {was} {nachher!r}",
                    tipp,
                )
            )

    def pruefe_zahl(self, bekommen, erwartet, aufruf, tipp):
        """Meldet einen Fehler, wenn ``bekommen`` nicht die Zahl ``erwartet`` ist (siehe ``fast_gleich``)."""
        if not fast_gleich(bekommen, erwartet):
            self.fail(meldung(f"{aufruf} ergibt {erwartet!r}", repr(bekommen), tipp))

    def lies_attribut(self, ding, name, tipp):
        """Liest ``ding.name``. Fehlt das Attribut, gibt es eine Meldung mit Tipp statt eines Absturzes."""
        fehlt = object()
        wert = getattr(ding, name, fehlt)
        if wert is fehlt:
            self.fail(
                meldung(
                    f"{type(ding).__name__} hat das Attribut {name}",
                    f"{type(ding).__name__} hat kein Attribut {name}",
                    tipp,
                )
            )
        return wert

    def pruefe_schaeden(self, gegner, erwartet, aufruf, tipp):
        """Meldet einen Fehler, wenn der Testgegner nicht genau diese Schäden ``(menge, art)`` erlitt."""
        if not schaeden_fast_gleich(gegner.schaeden, erwartet):
            self.fail(
                meldung(
                    f"nach {aufruf} hat der Gegner diese Schäden (menge, art) erlitten: {erwartet}",
                    f"er hat diese erlitten: {gegner.schaeden}",
                    tipp,
                )
            )

    def pruefe_heilungen(self, gegner, erwartet, aufruf, tipp):
        """Meldet einen Fehler, wenn der Testgegner nicht genau diese Mengen an Heilung bekam."""
        if not alle_fast_gleich(gegner.heilungen, erwartet):
            self.fail(
                meldung(
                    f"nach {aufruf} wurde {gegner} mit diesen Mengen geheilt: {erwartet}",
                    f"geheilt wurde mit diesen Mengen: {gegner.heilungen}",
                    tipp,
                )
            )

    def pruefe_abstaende(self, bekommen, erwartet, aufruf, tipp):
        """Vergleicht zwei Abstandskarten und nennt die erste Zelle, die nicht stimmt."""
        if not isinstance(bekommen, dict):
            self.fail(
                meldung(
                    f"{aufruf} ergibt ein Wörterbuch von Zelle zu Abstand",
                    repr(bekommen),
                    "Die Abstandskarte ist ein dict. Der Schlüssel ist die Zelle (spalte, zeile), "
                    "der Wert die Zahl der Schritte bis zum Ziel.",
                )
            )
        for zelle in sorted(erwartet, key=lambda z: (z[1], z[0])):
            if zelle not in bekommen:
                self.fail(
                    meldung(
                        f"{aufruf}: Zelle {zelle} hat den Abstand {erwartet[zelle]}",
                        f"Zelle {zelle} fehlt in der Abstandskarte",
                        tipp,
                    )
                )
            if bekommen[zelle] != erwartet[zelle]:
                self.fail(
                    meldung(
                        f"{aufruf}: Zelle {zelle} hat den Abstand {erwartet[zelle]}",
                        f"Zelle {zelle} hat den Abstand {bekommen[zelle]!r}",
                        tipp,
                    )
                )
        zu_viel = sorted((zelle for zelle in bekommen if zelle not in erwartet), key=repr)
        if zu_viel:
            zelle = zu_viel[0]
            self.fail(
                meldung(
                    f"{aufruf}: Zelle {zelle} steht nicht in der Abstandskarte, "
                    "weil von dort kein Weg zum Ziel führt",
                    f"Zelle {zelle} hat den Abstand {bekommen[zelle]!r}",
                    tipp,
                )
            )


# ---------------------------------------------------------------------------------------
# 3. Karten und Abstandskarten als Text zeichnen
# ---------------------------------------------------------------------------------------


def raster_aus(bild):
    """Macht aus einer gezeichneten Karte ein Raster. Eingerückte Zeilen sind erlaubt.

    Das benutzen die Tests ab Mission 2, damit sie nicht von Mission 1 abhängen.
    """
    return [list(zeile.strip()) for zeile in bild.strip().splitlines()]


def abstaende_aus(bild):
    """Macht aus gezeichneten Zahlen eine Abstandskarte: ``{(spalte, zeile): abstand}``.

    Die Einträge einer Zeile sind durch Leerzeichen getrennt. Wo keine Zahl steht (zum Beispiel
    ``#`` für Fels oder ``-`` für "nicht erreichbar"), bekommt die Zelle keinen Eintrag.
    """
    abstaende = {}
    for zeile, text in enumerate(bild.strip().splitlines()):
        for spalte, eintrag in enumerate(text.split()):
            if eintrag.isdigit():
                abstaende[(spalte, zeile)] = int(eintrag)
    return abstaende


# ---------------------------------------------------------------------------------------
# 4. Ein Gegner, ein Effekt und ein Turm zum Testen
# ---------------------------------------------------------------------------------------


class TestGegner:
    """Ein Gegner nur für Tests. Er hat genau das, was Code der Werkstatt von Gegnern benutzt.

    Er schreibt mit, was mit ihm geschieht: ``schaeden`` ist die Liste aller ``(menge, art)``,
    ``heilungen`` die Liste aller Mengen. Resistenzen kennt er nicht, er zieht die Menge so ab,
    wie sie kommt.
    """

    def __init__(
        self, leben=100.0, x=0.0, y=0.0, rest_weg=0.0, max_leben=None, fliegt=False, ist_boss=False
    ):
        self.leben = leben
        self.max_leben = leben if max_leben is None else max_leben
        self.x = x
        self.y = y
        self.rest_weg = rest_weg
        self.effekte = []
        self.fliegt = fliegt
        self.ist_boss = ist_boss
        self.schaeden = []
        self.heilungen = []

    def erleide_schaden(self, menge, art):
        """Zieht Leben ab, nie unter 0, und liefert, wie viel Leben wirklich verloren ging."""
        self.schaeden.append((menge, art))
        verloren = min(self.leben, max(menge, 0))
        self.leben -= verloren
        return verloren

    def heile(self, menge):
        """Gibt Leben zurück, nie über ``max_leben`` hinaus."""
        self.heilungen.append(menge)
        self.leben = min(self.max_leben, self.leben + max(menge, 0))

    def __repr__(self):
        return f"TestGegner(leben={self.leben}, x={self.x}, y={self.y}, rest_weg={self.rest_weg})"


class TestEffekt:
    """Ein Effekt nur für Tests, damit die Missionen 13 und 14 nicht von Mission 12 abhängen.

    Er hat, was die Effekte aus Mission 12 haben: ``name``, ``dauer``, ``rest``, ``tick``,
    ``ist_vorbei`` und ``tempo_faktor``. In einem ist er mit Absicht dumm: Er nennt seinen
    Faktor auch dann noch, wenn er längst vorbei ist. Wer nur die Effekte fragt, die noch
    wirken, merkt davon nichts.
    """

    def __init__(self, name, rest=1.0, faktor=1.0):
        self.name = name
        self.dauer = rest
        self.rest = rest
        self.faktor = faktor

    def tick(self, gegner, sekunden):
        """Lässt die Zeit vergehen, nie unter 0. Negative Zeit ändert nichts."""
        if sekunden > 0:
            self.rest = max(0.0, self.rest - sekunden)

    def ist_vorbei(self):
        return self.rest <= 0

    def tempo_faktor(self):
        return self.faktor

    def __repr__(self):
        return f"TestEffekt({self.name!r}, rest={self.rest}, faktor={self.faktor})"


class TestTurm:
    """Ein Turm nur für Tests. Eine Zielstrategie kennt von ihm nur, wo er steht: ``x`` und ``y``."""

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"TestTurm(x={self.x}, y={self.y})"
