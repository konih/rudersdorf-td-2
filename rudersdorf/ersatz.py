"""Der Ersatz: was das Spiel benutzt, solange eine Mission noch offen ist.

``ERSATZ`` ist das Verzeichnis dafür: Fähigkeit -> Name -> Funktion oder Klasse. Der Name
ist derselbe wie in der Werkstatt (``ERSATZ["schadensarten"]["berechne_schaden"]``), und der
Ersatz nimmt dieselben Argumente wie das Original.

So ist es vereinbart:

- Die Werkbank schlägt bei jedem Aufruf frisch in ``ERSATZ`` nach. Sie kopiert das
  Verzeichnis nicht und merkt sich keinen Eintrag.
- Beim Erzeugen einer Werkbank und beim Prüfen, was offen ist, wird ``ERSATZ`` nicht
  gebraucht. Ein Eintrag wird erst gesucht, wenn eine offene Fähigkeit wirklich benutzt wird.
- Ein Ersatz für eine Klasse ist selbst eine Klasse. Sie wird mit denselben Argumenten
  erzeugt wie das Original, und ihre Methoden antworten statt der Methoden des Originals.
- Ein Test trägt seinen eigenen Ersatz mit ``unittest.mock.patch.dict(ERSATZ, {...})`` ein
  und bekommt danach den alten Stand zurück.

Ein Ersatz ist mit Absicht schwächer als die echte Regel, und er ist nie die Lösung einer
Mission. Jeder Ersatz kommt zusammen mit dem Teil des Spiels, zu dem er gehört. Bis jetzt
gibt es den Ersatz zu Spur A (Karten, Wegfindung und Bauregel) und zu Spur B (Reichweite,
Zielstrategien, Kettenblitz und Ausbau).
"""

import math

from rudersdorf.daten import BEBAUBAR, ZELLE

# --- Fähigkeit "karten" (Mission 1) ---------------------------------------------------------

# Die eine Karte, die das Spiel auswendig kennt. Sie ist dieselbe wie karten/flusstal.txt.
FLUSSTAL = (
    "...##...~~........DDDDDD",
    "........~~....^...DDDDDD",
    "..^.....~~........DDDDDD",
    "........~~...#....DDDDDD",
    "..................DDDDDD",
    "........~~........DDDDDD",
    "....^...~~~.......DDDDDD",
    "S........~~...^...DDDDDD",
    ".........~~......ZDDDDDD",
    "..#......~~.......DDDDDD",
    "........~~~.......DDDDDD",
    "........%%...##...DDDDDD",
    "........~~........DDDDDD",
    "...^....~~....^...DDDDDD",
    "........~~........DDDDDD",
    ".....#..~~........DDDDDD",
)
# Wo im Flusstal die beiden Tore liegen, als Zellen (spalte, zeile).
FLUSSTAL_ORKTOR = (0, 7)
FLUSSTAL_DORFTOR = (17, 8)


def ersatz_lies_karte(text):
    """Ersatz für ``lies_karte``: liest den Text gar nicht und liefert immer das Flusstal.

    Darum kann man im Spiel keine andere Karte wählen und keine eigene bauen.
    Mission 1 (Die Karte lesen) ersetzt das.
    """
    raster = []
    for zeile in FLUSSTAL:
        raster.append(list(zeile))
    return raster


def ersatz_finde(raster, zeichen):
    """Ersatz für ``finde``: sucht nicht, sondern kennt nur die beiden Tore des Flusstals.

    Für "S" und "Z" nennt er die Zelle, die er auswendig weiß. Jedes andere Zeichen findet
    er nicht, und in das Raster schaut er nie hinein. Mission 1 (Die Karte lesen) ersetzt das.
    """
    if zeichen == "S":
        return [FLUSSTAL_ORKTOR]
    if zeichen == "Z":
        return [FLUSSTAL_DORFTOR]
    return []


# --- Fähigkeit "wegfindung" (Missionen 2 bis 4): der Geisterlauf ------------------------------


def ersatz_nachbarn(zelle, breite, hoehe):
    """Ersatz für ``nachbarn``: die Zellen rechts, links, unten und oben, in dieser Reihenfolge.

    Ein Geist schaut zuerst zur Seite. Die Reihenfolge der Mission (oben, rechts, unten,
    links) kennt er nicht. Mission 2 (Nachbarn) ersetzt das.
    """
    spalte, zeile = zelle
    ergebnis = []
    if spalte + 1 < breite:
        ergebnis.append((spalte + 1, zeile))
    if spalte - 1 >= 0:
        ergebnis.append((spalte - 1, zeile))
    if zeile + 1 < hoehe:
        ergebnis.append((spalte, zeile + 1))
    if zeile - 1 >= 0:
        ergebnis.append((spalte, zeile - 1))
    return ergebnis


def ersatz_ist_begehbar(raster, zelle, gesperrt):
    """Ersatz für ``ist_begehbar``: Für einen Geist ist jede Zelle der Karte begehbar.

    Fels, Wasser und Bauwerke halten ihn nicht auf. Mission 2 (Nachbarn) ersetzt das.
    """
    spalte, zeile = zelle
    return 0 <= zeile < len(raster) and 0 <= spalte < len(raster[0])


def ersatz_abstandskarte(raster, ziel, gesperrt):
    """Ersatz für ``abstandskarte``: die Luftlinie statt des Weges.

    Jede Zelle der Karte bekommt als Abstand, wie viele Spalten und Zeilen sie vom Ziel
    entfernt ist. Wände, Wasser und Bauwerke zählen nicht, auch sie bekommen einen Abstand.
    Mission 3 (Der kürzeste Weg) ersetzt das.
    """
    ziel_spalte, ziel_zeile = ziel
    abstaende = {}
    for zeile in range(len(raster)):
        for spalte in range(len(raster[zeile])):
            abstaende[(spalte, zeile)] = abs(spalte - ziel_spalte) + abs(zeile - ziel_zeile)
    return abstaende


def ersatz_naechster_schritt(abstaende, zelle, breite, hoehe):
    """Ersatz für ``naechster_schritt``: der erstbeste Nachbar, der näher am Ziel liegt.

    Der Geist vergleicht die Nachbarn nicht miteinander. Zusammen mit der Luftlinie läuft er
    so erst zur Seite und dann hinauf oder hinunter, mitten durch alles hindurch.
    Mission 4 (Dem Weg folgen) ersetzt das.
    """
    if zelle not in abstaende:
        return None
    for nachbar in ersatz_nachbarn(zelle, breite, hoehe):
        if nachbar in abstaende and abstaende[nachbar] < abstaende[zelle]:
            return nachbar
    return None


# --- Fähigkeit "bauregel" (Mission 5) -------------------------------------------------------


def ersatz_darf_bauen(raster, zelle, gesperrt, starts, ziel, besetzt):
    """Ersatz für ``darf_bauen``: nie neben ein anderes Bauwerk, auch nicht schräg.

    Nach einem Weg sucht der Ersatz nicht. Er verbietet einfach alle acht Zellen rund um jedes
    Bauwerk. So kann keine Mauer entstehen, aber auch kein Labyrinth. Dass man nur auf freies
    Bauland (Wiese und Hügel) bauen darf, weiß er. Mission 5 (Nicht einmauern!) ersetzt das.
    """
    spalte, zeile = zelle
    if not (0 <= zeile < len(raster) and 0 <= spalte < len(raster[0])):
        return False
    if raster[zeile][spalte] not in BEBAUBAR:
        return False
    if zelle in besetzt:
        return False
    # Die Zelle eines Bauwerks ist mit verboten: Sie hat zu sich selbst den Abstand 0.
    for bau_spalte, bau_zeile in gesperrt:
        if abs(bau_spalte - spalte) <= 1 and abs(bau_zeile - zeile) <= 1:
            return False
    return True


# --- Fähigkeit "reichweite" (Mission 6): der Tunnelblick --------------------------------------


def ersatz_in_reichweite(position, reichweite, gegner):
    """Ersatz für ``in_reichweite``: Der Turm sieht nur geradeaus, nie schräg.

    Er sieht einen lebenden Gegner nur, wenn der in derselben Zeile oder in derselben Spalte
    der Karte steht wie der Turm, und auch dann nur bis zu seiner Reichweite. Wer schräg
    neben dem Turm vorbeiläuft, bleibt unbemerkt. Mission 6 (Wer ist in Reichweite?) ersetzt das.
    """
    turm_x, turm_y = position
    turm_spalte = turm_x // ZELLE
    turm_zeile = turm_y // ZELLE
    gesehen = []
    for einer in gegner:
        if einer.leben <= 0:
            continue
        if einer.x // ZELLE != turm_spalte and einer.y // ZELLE != turm_zeile:
            continue
        if math.hypot(einer.x - turm_x, einer.y - turm_y) <= reichweite:
            gesehen.append(einer)
    return gesehen


# --- Fähigkeit "strategien" (Missionen 7 und 8) ----------------------------------------------


def ersatz_zufall(kandidaten, turm):
    """Ersatz für die Zielstrategien: irgendein Kandidat, mal dieser und mal jener.

    Der Ersatz würfelt nicht wirklich, und er merkt sich nichts von einem Aufruf zum nächsten.
    Er zählt zusammen, wo die Kandidaten gerade stehen (alle x und alle y), und nimmt die
    ganze Zahl davon als Nummer in der Liste. Weil die Gegner laufen, kommt dabei ständig ein
    anderer heraus, ohne dass eine Regel dahintersteckt. Und weil nichts gewürfelt wird, läuft
    dieselbe Partie jedes Mal genau gleich ab. Mission 7 (Zielstrategien) ersetzt das.
    """
    if len(kandidaten) == 0:
        return None
    summe = 0.0
    for einer in kandidaten:
        summe += einer.x + einer.y
    return kandidaten[int(summe) % len(kandidaten)]


# --- Fähigkeit "kettenblitz" (Mission 9) -----------------------------------------------------


def ersatz_kettenblitz(start, gegner, spruenge, sprungweite):
    """Ersatz für ``kettenblitz``: Der Blitz springt nicht, er trifft nur den ersten Gegner.

    Mission 9 (Der Kettenblitz) ersetzt das.
    """
    return [start]


# --- Fähigkeit "ausbau" (Mission 10) ---------------------------------------------------------


def ersatz_wende_ausbau_an(werte, ausbau):
    """Ersatz für ``wende_ausbau_an``: Es gibt noch keine Turmschmiede.

    Der Ersatz sieht sich den Ausbau gar nicht an und antwortet immer mit ``None``. Für das
    Spiel heißt das: Dieser Turm kann nicht ausgebaut werden. Mission 10 (Die Turmschmiede)
    ersetzt das.
    """
    return None


ERSATZ: dict[str, dict[str, object]] = {
    "karten": {
        "lies_karte": ersatz_lies_karte,
        "finde": ersatz_finde,
    },
    "wegfindung": {
        "nachbarn": ersatz_nachbarn,
        "ist_begehbar": ersatz_ist_begehbar,
        "abstandskarte": ersatz_abstandskarte,
        "naechster_schritt": ersatz_naechster_schritt,
    },
    "bauregel": {
        "darf_bauen": ersatz_darf_bauen,
    },
    "reichweite": {
        "in_reichweite": ersatz_in_reichweite,
    },
    # Die Werkbank fragt bei offenen Strategien nur nach "zufall".
    "strategien": {
        "zufall": ersatz_zufall,
    },
    "kettenblitz": {
        "kettenblitz": ersatz_kettenblitz,
    },
    "ausbau": {
        "wende_ausbau_an": ersatz_wende_ausbau_an,
    },
}


def ersatz_fuer(faehigkeit, name):
    """Schlägt den Ersatz für ``name`` nach, bei jedem Aufruf frisch.

    Entscheidung: Fehlt der Eintrag, ist das ein Fehler im Spiel selbst und kein Fehler in
    der Werkstatt. Darum gibt es einen RuntimeError mit dem Namen der Fähigkeit und keinen
    Lernfehler.
    """
    eintraege = ERSATZ.get(faehigkeit, {})
    if name not in eintraege:
        raise RuntimeError(
            f"Für die Fähigkeit {faehigkeit!r} ist kein Ersatz für {name!r} eingetragen. "
            "Das ist ein Fehler im Spiel, nicht in deiner Werkstatt."
        )
    return eintraege[name]
