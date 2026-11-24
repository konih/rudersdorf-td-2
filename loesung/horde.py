"""Referenz zu Spur C · Die Horde (Missionen 11 bis 15).

Ein Gegner kennt sein leben, sein x und y und seine Liste effekte. Schaden bekommt er
mit gegner.erleide_schaden(menge, art), Heilung mit gegner.heile(menge). Sein Leben ändert
hier niemand direkt: Der Gegner weiß selbst am besten, wie viel bei ihm ankommt.
"""

from .tuerme import _abstand

# --- Mission 11: Schadensarten ---------------------------------------------------------------


def berechne_schaden(schaden, art, resistenzen):
    """Mission 11: Schadensarten. Rechnet aus, wie viel Schaden wirklich ankommt."""
    # Schaden von 0 oder weniger bleibt 0. Sonst würde "negativer Schaden" heilen.
    if schaden <= 0:
        return 0

    # Im Wörterbuch steht für jede Schadensart ein Faktor: 0.4 lässt weniger als die Hälfte
    # durch, 2.0 verdoppelt. get() liefert 1.0, wenn die Art gar nicht vorkommt.
    faktor = resistenzen.get(art, 1.0)
    return schaden * faktor


# --- Mission 12: Effekte ---------------------------------------------------------------------


class Effekt:
    """Mission 12: Effekte. Etwas, das eine Zeit lang auf einem Gegner liegt."""

    # Der Name gehört zur Klasse und nicht zum einzelnen Objekt: Jeder Effekt dieser Klasse
    # heißt gleich. Jede Unterklasse trägt hier ihren eigenen Namen ein.
    name = "effekt"

    def __init__(self, dauer):
        """Merkt sich die Dauer und wie viel davon noch übrig ist."""
        self.dauer = dauer
        # Am Anfang ist noch die ganze Dauer übrig.
        self.rest = dauer

    def tick(self, gegner, sekunden):
        """Lässt die Zeit vergehen."""
        # Die Zeit läuft nie rückwärts: Ein negativer Wert ändert nichts.
        if sekunden <= 0:
            return
        self.rest = self.rest - sekunden
        # Weniger als nichts kann nicht übrig sein.
        if self.rest < 0:
            self.rest = 0.0

    def ist_vorbei(self):
        """Sagt, ob der Effekt abgelaufen ist."""
        return self.rest <= 0

    def tempo_faktor(self):
        """Sagt, wie schnell der Gegner mit diesem Effekt noch läuft (1.0 ist normal)."""
        # Ein gewöhnlicher Effekt bremst nicht.
        return 1.0


class Frost(Effekt):
    """Mission 12: Effekte. Frost macht einen Gegner langsamer."""

    name = "frost"

    def __init__(self, dauer, faktor):
        """Merkt sich zusätzlich, wie stark der Frost bremst."""
        # super() ist die Oberklasse Effekt. Sie kümmert sich um dauer und rest,
        # hier kommt nur noch das dazu, was beim Frost anders ist.
        super().__init__(dauer)
        self.faktor = faktor

    def tempo_faktor(self):
        """Bremst, solange der Frost anhält."""
        # ist_vorbei() steht nicht in dieser Klasse. Frost hat es von Effekt geerbt.
        if self.ist_vorbei():
            return 1.0
        return self.faktor


class Gift(Effekt):
    """Mission 12: Effekte. Gift schadet einem Gegner Sekunde für Sekunde."""

    name = "gift"
    # Welche Art von Schaden das Gift macht. Eine Unterklasse kann das überschreiben.
    schadensart = "gift"

    def __init__(self, dauer, schaden_pro_sekunde):
        """Merkt sich zusätzlich, wie viel Schaden das Gift pro Sekunde macht."""
        super().__init__(dauer)
        self.schaden_pro_sekunde = schaden_pro_sekunde

    def tick(self, gegner, sekunden):
        """Fügt dem Gegner Schaden zu und lässt dann die Zeit vergehen."""
        # Das Gift wirkt höchstens so lange, wie noch Zeit übrig ist: Ist nur noch eine
        # Sekunde übrig, schaden auch drei vergangene Sekunden nur für eine.
        wirkzeit = min(sekunden, self.rest)
        menge = self.schaden_pro_sekunde * wirkzeit
        # self.schadensart und nicht "gift": So benutzt eine Unterklasse ihre eigene Art.
        if menge > 0:
            gegner.erleide_schaden(menge, self.schadensart)

        # Erst jetzt vergeht die Zeit. Das Herunterzählen kann Effekt schon.
        super().tick(gegner, sekunden)


class Brand(Gift):
    """Mission 12: Effekte. Brand wirkt wie Gift, nur mit Feuer."""

    # Mehr braucht es nicht: __init__ und tick kommen von Gift, und tick liest
    # self.schadensart. Dort steht bei einem Brand jetzt "feuer".
    name = "brand"
    schadensart = "feuer"


class Betaeubung(Effekt):
    """Mission 12: Effekte. Ein betäubter Gegner bleibt stehen."""

    name = "betaeubung"

    def __init__(self, dauer):
        """Merkt sich die Dauer wie jeder Effekt."""
        # Hier kommt nichts dazu. Darum könnte diese Methode auch ganz fehlen:
        # Dann würde Python von selbst die von Effekt nehmen.
        super().__init__(dauer)

    def tempo_faktor(self):
        """Hält den Gegner an, solange die Betäubung wirkt."""
        if self.ist_vorbei():
            return 1.0
        # Tempo mal 0.0 ist 0: Der Gegner steht.
        return 0.0


# --- Mission 13: Die Effektliste -------------------------------------------------------------


def fuege_effekt_hinzu(effekte, neu):
    """Mission 13: Die Effektliste. Legt einen Effekt in die Liste, aber nie doppelt."""
    # Gibt es schon einen Effekt mit demselben Namen? Gesucht wird mit der Nummer des
    # Platzes, damit der alte Effekt an genau diesem Platz ersetzt werden kann.
    for platz in range(len(effekte)):
        alter = effekte[platz]
        if alter.name == neu.name:
            # Von zwei gleichen Effekten bleibt der, der länger hält.
            # ">=" und nicht ">": Bei gleichem Rest gewinnt der neue.
            if neu.rest >= alter.rest:
                effekte[platz] = neu
            # Ob ersetzt oder nicht: Ein zweiter Effekt dieser Art kommt nicht dazu.
            return

    # Diese Art gab es noch nicht.
    effekte.append(neu)


def gesamt_tempo_faktor(effekte):
    """Mission 13: Die Effektliste. Findet heraus, wie stark alle Effekte zusammen bremsen."""
    # Es zählt die stärkste Bremse, also der kleinste Faktor. Die Faktoren werden nicht
    # miteinander malgenommen.
    kleinster = None
    for effekt in effekte:
        # Ein abgelaufener Effekt bremst nicht mehr, auch wenn er noch in der Liste steht.
        if effekt.ist_vorbei():
            continue
        faktor = effekt.tempo_faktor()
        if kleinster is None or faktor < kleinster:
            kleinster = faktor

    # Ohne wirksamen Effekt läuft der Gegner normal.
    if kleinster is None:
        return 1.0
    return kleinster


def raeume_effekte_auf(effekte):
    """Mission 13: Die Effektliste. Liefert eine Liste ohne die abgelaufenen Effekte."""
    # Eine neue Liste bauen und nichts aus der alten löschen. Wer aus einer Liste löscht,
    # während er sie durchläuft, überspringt Einträge.
    uebrig = []
    for effekt in effekte:
        if not effekt.ist_vorbei():
            uebrig.append(effekt)
    return uebrig


# --- Mission 14: Besondere Fähigkeiten -------------------------------------------------------


def _brennt(gegner):
    """Hilfsfunktion: Trägt der Gegner einen Brand, der noch nicht vorbei ist?"""
    for effekt in gegner.effekte:
        if effekt.name == "brand" and not effekt.ist_vorbei():
            return True
    return False


class Regeneration:
    """Mission 14: Besondere Fähigkeiten. Der Troll heilt sich selbst."""

    def __init__(self, pro_sekunde):
        """Merkt sich, wie viel Leben pro Sekunde zurückkommt."""
        self.pro_sekunde = pro_sekunde

    def aktualisiere(self, traeger, alle, sekunden):
        """Heilt den Träger und liefert die Liste der Gegner, die neu erscheinen sollen."""
        # Wer besiegt ist, steht nicht wieder auf. Und Feuer hält die Heilung auf.
        if traeger.leben > 0 and not _brennt(traeger):
            traeger.heile(self.pro_sekunde * sekunden)
        # Ein Troll ruft niemanden herbei.
        return []


class Heiler:
    """Mission 14: Besondere Fähigkeiten. Der Schamane heilt die Gegner um sich herum."""

    def __init__(self, radius, pro_sekunde):
        """Merkt sich, wie weit und wie stark die Heilung wirkt."""
        self.radius = radius
        self.pro_sekunde = pro_sekunde

    def aktualisiere(self, traeger, alle, sekunden):
        """Heilt die anderen in der Nähe und liefert, wer neu erscheinen soll."""
        # Ein besiegter Schamane heilt niemanden mehr.
        if traeger.leben <= 0:
            return []

        for anderer in alle:
            # Der Schamane steht selbst in der Liste. Sich selbst heilt er nie.
            # "is" fragt: Ist das genau derselbe Gegner?
            if anderer is traeger:
                continue
            # Besiegte werden nicht geheilt.
            if anderer.leben <= 0:
                continue
            # "<=": Wer genau auf dem Rand des Kreises steht, gehört noch dazu.
            if _abstand(traeger.x, traeger.y, anderer.x, anderer.y) <= self.radius:
                anderer.heile(self.pro_sekunde * sekunden)
        return []


class Beschwoerer:
    """Mission 14: Besondere Fähigkeiten. Der Orkkönig ruft Verstärkung herbei."""

    def __init__(self, intervall, art, anzahl=1):
        """Merkt sich, wie oft, wen und wie viele er ruft."""
        self.intervall = intervall
        self.art = art
        self.anzahl = anzahl
        # Die Uhr: So lange dauert es noch bis zum nächsten Rufen.
        self.rest = intervall

    def aktualisiere(self, traeger, alle, sekunden):
        """Zählt die Zeit herunter und liefert die Arten der Gegner, die jetzt erscheinen."""
        self.rest = self.rest - sekunden

        # Die Uhr ist noch nicht abgelaufen.
        if self.rest > 0:
            return []
        # Ein besiegter König ruft niemanden.
        if traeger.leben <= 0:
            return []

        # Das Intervall wird dazugezählt und die Uhr nicht einfach neu gestellt. So geht
        # die Zeit nicht verloren, die schon über das Ziel hinaus vergangen ist.
        self.rest = self.rest + self.intervall
        # Eine Liste mal eine Zahl wiederholt die Liste: ["ork"] * 3 ist ["ork", "ork", "ork"].
        return [self.art] * self.anzahl


# --- Mission 15: Die Wellenschmiede ----------------------------------------------------------


def _kandidaten(nummer, rest, katalog):
    """Hilfsfunktion: die Arten, die in dieser Welle mit dem Rest noch gekauft werden können."""
    kandidaten = []
    # sorted() geht die Namen nach dem Alphabet durch. So kommt immer dieselbe Liste heraus,
    # egal in welcher Reihenfolge die Arten im Katalog stehen.
    for art in sorted(katalog):
        eintrag = katalog[art]
        # Ein Boss wird nie gekauft. Er hat seine eigene Welle.
        if eintrag["boss"]:
            continue
        # Diese Art kommt erst in einer späteren Welle.
        if eintrag["ab_welle"] > nummer:
            continue
        # Zu teuer für das, was noch übrig ist.
        if eintrag["preis"] > rest:
            continue
        kandidaten.append(art)
    return kandidaten


def erzeuge_welle(nummer, budget, katalog, zufall):
    """Mission 15: Die Wellenschmiede. Kauft mit dem Budget die Gegner der nächsten Welle."""
    welle = []
    rest = budget

    while True:
        # Nach jedem Kauf neu fragen: Mit weniger Geld kommen weniger Arten in Frage.
        kandidaten = _kandidaten(nummer, rest, katalog)
        # Kann niemand mehr bezahlt werden, ist die Welle fertig.
        if len(kandidaten) == 0:
            break

        # Nur das zufall benutzen, das die Funktion bekommt: Mit derselben Saat kommt dann
        # immer dieselbe Welle heraus.
        gekauft = zufall.choice(kandidaten)
        welle.append(gekauft)
        # Ohne diese Zeile würde die Schleife nie aufhören.
        rest = rest - katalog[gekauft]["preis"]

    return welle
