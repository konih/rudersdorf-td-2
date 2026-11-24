"""Die Werkbank: der einzige Weg, auf dem das Spiel Code aus der Werkstatt benutzt.

Sie lädt ein Paket (``werkstatt`` oder ``loesung``), probiert aus, welche Fähigkeiten schon
gelöst sind, und reicht jeden Aufruf weiter. Ist eine Mission noch offen, antwortet der
Ersatz aus ``rudersdorf/ersatz.py``. Macht der Code der Werkstatt einen echten Fehler, wird
daraus ein ``Lernfehler`` mit Datei und Zeile.

Die Datei liest sich von oben nach unten:

1. die Verzeichnisse ``FAEHIGKEITEN`` und ``ABHAENGIG``, gebaut aus der Liste der Missionen,
2. die Proben: kleine Aufrufe, an denen die Werkbank merkt, ob eine Mission noch offen ist,
3. das ``Werkstueck``: ein Objekt aus der Werkstatt, dessen Methoden über die Werkbank laufen,
4. die ``Werkbank`` selbst und ``waehle_paket``.
"""

import functools
import importlib
import importlib.util
import inspect
import os
import random
import sys
import traceback

from rudersdorf import ersatz
from rudersdorf.fehler import Lernfehler, NochOffen
from rudersdorf.missionen import MISSIONEN

# ---------------------------------------------------------------------------------------
# 1. Die Verzeichnisse
# ---------------------------------------------------------------------------------------

# Nummer -> Eintrag der Mission, zum schnellen Nachschlagen.
MISSION = {eintrag["nummer"]: eintrag for eintrag in MISSIONEN}


def baue_faehigkeiten():
    """Fasst die Missionen nach ihrer Fähigkeit zusammen, in der Reihenfolge der Missionen."""
    faehigkeiten = {}
    for eintrag in MISSIONEN:
        schluessel = eintrag["faehigkeit"]
        if schluessel is None:
            continue  # Die Missionen 21 bis 23 geben dem Spiel keine Fähigkeit.
        if schluessel not in faehigkeiten:
            faehigkeiten[schluessel] = {"missionen": [], "modul": eintrag["modul"], "namen": []}
        faehigkeiten[schluessel]["missionen"].append(eintrag["nummer"])
        for name in eintrag["namen"]:
            if name not in faehigkeiten[schluessel]["namen"]:
                faehigkeiten[schluessel]["namen"].append(name)
    return faehigkeiten


def baue_abhaengig():
    """Liest aus ``braucht`` der Missionen, welche Fähigkeit auf welche anderen wartet."""
    abhaengig = {schluessel: [] for schluessel in FAEHIGKEITEN}
    for schluessel in FAEHIGKEITEN:
        for nummer in gebrauchte_missionen(schluessel):
            andere = MISSION[nummer]["faehigkeit"]
            if andere != schluessel and andere not in abhaengig[schluessel]:
                abhaengig[schluessel].append(andere)
    return abhaengig


def gebrauchte_missionen(faehigkeit):
    """Liefert die Nummern aller Missionen, auf denen diese Fähigkeit aufbaut."""
    nummern = []
    for nummer in FAEHIGKEITEN[faehigkeit]["missionen"]:
        for gebraucht in MISSION[nummer]["braucht"]:
            if gebraucht not in nummern:
                nummern.append(gebraucht)
    return sorted(nummern)


def mission_von(faehigkeit, name):
    """Liefert die Nummer der Mission, zu der ``name`` gehört.

    Ein Name, der in keiner Mission steht (eine selbst erfundene Strategie aus Mission 8),
    zählt zur letzten Mission der Fähigkeit.
    """
    nummern = FAEHIGKEITEN[faehigkeit]["missionen"]
    for nummer in nummern:
        if name in MISSION[nummer]["namen"]:
            return nummer
    return nummern[-1]


# Fähigkeit -> {"missionen": [Nummern], "modul": Name, "namen": [Namen]}, aus dem Verzeichnis
# der Missionen gebaut, in dessen Reihenfolge.
FAEHIGKEITEN: dict[str, dict] = baue_faehigkeiten()

# Fähigkeit -> Fähigkeiten, auf die sie wartet (aus "braucht" im Verzeichnis der Missionen).
ABHAENGIG: dict[str, list] = baue_abhaengig()

# Die Module der Werkstatt, die das Spiel braucht, jedes einmal.
MODULE = list(dict.fromkeys(eintrag["modul"] for eintrag in FAEHIGKEITEN.values()))

# ---------------------------------------------------------------------------------------
# 2. Die Proben
# ---------------------------------------------------------------------------------------
# Eine Probe bekommt ein Modul der Werkstatt und ruft dort genau einen Namen einmal auf, mit
# der kleinsten Eingabe, die erlaubt ist. Was dabei herauskommt, ist egal. Es zählt nur:
# Meldet sich der Code mit NochOffen, dann ist die Mission noch offen.
#
# Jede Probe baut ihre Eingabe selbst und jedes Mal neu. So kann Code der Werkstatt, der eine
# Liste verändert, der nächsten Probe nichts verderben.


class ProbeGegner:
    """Ein Gegner nur zum Ausprobieren, mit allem, was die Werkstatt von einem Gegner kennt."""

    def __init__(self, x=20.0, y=20.0):
        self.leben = 10.0
        self.max_leben = 10.0
        self.x = x
        self.y = y
        self.rest_weg = 100.0
        self.effekte = []
        self.fliegt = False
        self.ist_boss = False

    def erleide_schaden(self, menge, art):
        pass

    def heile(self, menge):
        pass


class ProbeTurm:
    """Ein Turm nur zum Ausprobieren: Eine Strategie kennt von ihm nur x und y."""

    x = 20.0
    y = 20.0


class ProbeDorf:
    """Ein Dorf nur zum Ausprobieren: Der Segen ruft ``heile`` auf."""

    def heile(self, menge):
        return 0


class ProbeEffekt:
    """Ein Effekt nur zum Ausprobieren, damit Mission 13 nicht von Mission 12 abhängt."""

    name = "frost"
    rest = 1.0

    def ist_vorbei(self):
        return False

    def tempo_faktor(self):
        return 0.5


PROBE_PUNKT = (20.0, 20.0)


def probe_raster():
    """Eine Karte aus zwei Zeilen: Start links oben, Ziel rechts oben, sonst Wiese."""
    return [["S", ".", "Z"], [".", ".", "."]]


def probe_dorfkatalog():
    return {
        "kirche": {
            "name": "Kirche",
            "stufen": [
                {"name": "Kapelle", "kosten": {"gold": 1}, "braucht": {}, "boni": {"mana": 1}}
            ],
        }
    }


def probe_zustand():
    """Ein Spielstand, wie ihn Mission 24 aufschreibt: ganz am Anfang, nichts gebaut."""
    return {
        "karte": "flusstal",
        "schwierigkeit": "normal",
        "saat": 1,
        "welle": 0,
        "endlos": False,
        "vorraete": {"gold": 0},
        "dorf_leben": 1,
        "dorf_stufen": {},
        "zauber_stufen": {},
        "bauwerke": {},
    }


def probe_daten():
    """Derselbe Spielstand so, wie er in der Datei steht."""
    daten = probe_zustand()
    daten["version"] = 2
    daten["bauwerke"] = []
    return daten


def probe_sicht():
    """Das, was ein Bot vom Spiel sieht: die kleine Karte, kein Gegner, nichts gebaut."""
    return {
        "phase": "bauen",
        "welle": 0,
        "wellen_gesamt": 1,
        "endlos": False,
        "raster": probe_raster(),
        "starts": [(0, 0)],
        "ziel": (2, 0),
        "abstaende": {(0, 0): 2, (1, 0): 1, (2, 0): 0},
        "vorraete": {"gold": 0, "stein": 0, "mana": 0},
        "dorf_leben": 1,
        "dorf_max_leben": 1,
        "dorf_stufen": {},
        "bauwerke": {},
        "gegner": [],
        "vorschau": {},
        "preise": {},
        "zauber": {},
    }


def probiere_kettenblitz(werkstatt):
    erster = ProbeGegner()
    werkstatt.kettenblitz(erster, [erster, ProbeGegner(x=40.0)], 1, 50.0)


def probiere_effekt(effekt):
    """Ruft jede Methode eines Effekts einmal auf."""
    effekt.tick(ProbeGegner(), 0.1)
    effekt.ist_vorbei()
    effekt.tempo_faktor()


def probiere_faehigkeit(faehigkeit):
    """Ruft die eine Methode einer besonderen Fähigkeit (Mission 14) einmal auf."""
    traeger = ProbeGegner()
    faehigkeit.aktualisiere(traeger, [traeger], 0.1)


def probiere_zauber(zauber):
    """Ruft die Methoden der Klasse Zauber einmal auf.

    ``wirke`` kommt zuletzt: In der gelösten Mission 19 meldet es NotImplementedError, und
    danach wäre die Probe zu Ende.
    """
    zauber.bereit(1)
    zauber.tick(0.1)
    zauber.zaubere(0, PROBE_PUNKT, [], ProbeDorf())
    zauber.wirke(PROBE_PUNKT, [], ProbeDorf())


def probiere_wirkung(zauber):
    """Lässt einen fertigen Zauber (Mission 20) einmal auf einen Gegner wirken."""
    zauber.wirke(PROBE_PUNKT, [ProbeGegner()], ProbeDorf())


# Fähigkeit -> Liste kleiner Funktionen, die je einen Namen der Werkstatt einmal ausprobieren.
# ``lambda w: ...`` ist eine Funktion ohne Namen; ``w`` ist das Modul der Werkstatt.
PROBEN: dict[str, list] = {
    "karten": [
        lambda w: w.lies_karte("S.Z\n...\n"),
        lambda w: w.finde(probe_raster(), "Z"),
    ],
    "wegfindung": [
        lambda w: w.nachbarn((0, 0), 3, 2),
        lambda w: w.ist_begehbar(probe_raster(), (1, 0), set()),
        lambda w: w.abstandskarte(probe_raster(), (2, 0), set()),
        lambda w: w.naechster_schritt({(0, 0): 2, (1, 0): 1, (2, 0): 0}, (0, 0), 3, 1),
    ],
    "bauregel": [
        lambda w: w.darf_bauen(probe_raster(), (1, 1), set(), [(0, 0)], (2, 0), set()),
    ],
    "reichweite": [
        lambda w: w.in_reichweite(PROBE_PUNKT, 50.0, [ProbeGegner()]),
    ],
    "strategien": [
        lambda w: w.erster([ProbeGegner()], ProbeTurm()),
        lambda w: w.letzter([ProbeGegner()], ProbeTurm()),
        lambda w: w.staerkster([ProbeGegner()], ProbeTurm()),
        lambda w: w.schwaechster([ProbeGegner()], ProbeTurm()),
        lambda w: w.naechster([ProbeGegner()], ProbeTurm()),
    ],
    "kettenblitz": [probiere_kettenblitz],
    "ausbau": [
        lambda w: w.wende_ausbau_an({"schaden": 10}, {"schaden": ("+", 5)}),
    ],
    "schadensarten": [
        lambda w: w.berechne_schaden(10, "feuer", {"feuer": 0.5}),
    ],
    "effekte": [
        lambda w: probiere_effekt(w.Effekt(1.0)),
        lambda w: probiere_effekt(w.Frost(1.0, 0.5)),
        lambda w: probiere_effekt(w.Gift(1.0, 2.0)),
        lambda w: probiere_effekt(w.Brand(1.0, 2.0)),
        lambda w: probiere_effekt(w.Betaeubung(1.0)),
        lambda w: w.fuege_effekt_hinzu([], ProbeEffekt()),
        lambda w: w.gesamt_tempo_faktor([ProbeEffekt()]),
        lambda w: w.raeume_effekte_auf([ProbeEffekt()]),
    ],
    "faehigkeiten": [
        lambda w: probiere_faehigkeit(w.Regeneration(1.0)),
        lambda w: probiere_faehigkeit(w.Heiler(50.0, 1.0)),
        lambda w: probiere_faehigkeit(w.Beschwoerer(1.0, "ork")),
    ],
    "wellen": [
        lambda w: w.erzeuge_welle(
            1, 10, {"ork": {"preis": 5, "ab_welle": 1, "boss": False}}, random.Random(1)
        ),
    ],
    "voraussetzungen": [
        lambda w: w.fehlende_voraussetzungen({"kirche": 1}, {}),
    ],
    "boni": [
        lambda w: w.sammle_boni({"kirche": 1}, probe_dorfkatalog()),
    ],
    "bauplan": [
        lambda w: w.bauplan("kirche", 1, {}, probe_dorfkatalog()),
    ],
    "magie": [
        lambda w: probiere_zauber(w.Zauber("probe", 1, 1.0)),
        lambda w: probiere_wirkung(w.Feuerball(1, 1.0, 50.0, 1, 1.0, 1)),
        lambda w: probiere_wirkung(w.Eissturm(1, 1.0, 50.0, 1.0, 0.5)),
        lambda w: probiere_wirkung(w.Blitzschlag(1, 1.0, 1, 1, 50.0)),
        lambda w: probiere_wirkung(w.Segen(1, 1.0, 1)),
        lambda w: probiere_wirkung(w.Glockenschlag(1, 1.0, 1.0)),
    ],
    "speichern": [
        lambda w: w.zu_daten(probe_zustand()),
        lambda w: w.aus_daten(probe_daten()),
    ],
    "auswertung": [
        lambda w: w.auswertung([{"schwierigkeit": "leicht", "sieg": True, "welle": 1, "gold": 0}]),
    ],
    "bot": [
        lambda w: w.mein_bot(probe_sicht()),
    ],
}

# ---------------------------------------------------------------------------------------
# 3. Das Werkstück
# ---------------------------------------------------------------------------------------

# Das Zeichen dafür, dass die Werkstatt nicht geantwortet hat, weil die Mission offen ist.
# (None geht dafür nicht: None kann eine richtige Antwort sein.)
OHNE_ANTWORT = object()


def erste_zeile(ziel):
    """Liefert (Datei, Zeile), wo eine Funktion oder Klasse der Werkstatt anfängt."""
    try:
        return inspect.getsourcefile(ziel) or "?", inspect.getsourcelines(ziel)[1]
    except (OSError, TypeError):
        return "?", 0


class Werkstueck:
    """Ein Objekt aus der Werkstatt, eingepackt: Seine Methoden laufen über die Werkbank.

    Das Spiel benutzt ein Werkstück wie das Objekt selbst (``frost.tempo_faktor()``,
    ``frost.rest``). Meldet eine Methode NochOffen, antwortet ab dann ein Objekt der
    Ersatzklasse, das mit denselben Argumenten erzeugt wird.

    Zwei Regeln für das Spiel: Es schreibt nichts in ein Werkstück hinein (``frost.rest = 0``
    bliebe an der Verpackung hängen). Und es fragt nicht auf Verdacht nach Werten (``hasattr``
    oder ``getattr`` mit Ersatzwert): Was dem echten Objekt fehlt, gilt als Lernfehler.
    """

    def __init__(self, werkbank, faehigkeit, klasse, echtes, args, kwargs):
        self._werkbank = werkbank
        self._faehigkeit = faehigkeit
        self._klasse = klasse
        self._echtes = echtes  # None, wenn die Fähigkeit beim Erzeugen schon offen war
        self._ersatz = None  # entsteht erst, wenn es gebraucht wird
        self._args = args
        self._kwargs = kwargs

    def _aktives(self):
        """Liefert das Objekt, das gerade antwortet: das echte oder das der Ersatzklasse.

        Entscheidung: Ein Objekt, das vor dem Öffnen der Fähigkeit entstand, antwortet danach
        nur noch über den Ersatz. Echte und Ersatz-Regeln mischen sich so auch hier nicht.
        """
        if self._echtes is not None and not self._werkbank.ist_offen(self._faehigkeit):
            return self._echtes
        if self._ersatz is None:
            ersatzklasse = ersatz.ersatz_fuer(self._faehigkeit, self._klasse)
            self._ersatz = ersatzklasse(*self._args, **self._kwargs)
        return self._ersatz

    def __getattr__(self, name):
        """Python fragt hier nach allem, was das Werkstück nicht selbst hat.

        Werte (``rest``, ``name``) kommen direkt vom Objekt, das gerade antwortet. Für eine
        Methode gibt es eine kleine Funktion zurück, die den Aufruf über die Werkbank schickt.
        """
        if name.startswith("_"):
            raise AttributeError(name)
        wert = self._lies(name)
        if not callable(wert):
            return wert

        def methode(*args, **kwargs):
            return self._rufe_methode(name, args, kwargs)

        return methode

    def _lies(self, name):
        """Holt ``name`` vom Objekt, das gerade antwortet.

        Auch das Nachschauen im echten Objekt läuft über die Werkbank: Fehlt dort eine
        Methode (ein Tippfehler im Namen) oder ein Wert (``self.rest`` vergessen), dann ist
        das ein Lernfehler, der auf die Klasse zeigt.
        """
        aktives = self._aktives()
        if aktives is self._echtes:
            wert = self._werkbank.versuche(
                self._faehigkeit, self._klasse, getattr, (aktives, name), {}, anfang=type(aktives)
            )
            if wert is not OHNE_ANTWORT:
                return wert
            aktives = self._aktives()  # Die Fähigkeit ist jetzt offen: Das ist der Ersatz.
        return getattr(aktives, name)

    def _rufe_methode(self, name, args, kwargs):
        aktives = self._aktives()
        if aktives is self._echtes:
            methode = getattr(aktives, name)
            ergebnis = self._werkbank.versuche(
                self._faehigkeit, self._klasse, methode, args, kwargs
            )
            if ergebnis is not OHNE_ANTWORT:
                return ergebnis
            aktives = self._aktives()  # Die Fähigkeit ist jetzt offen: Das ist der Ersatz.
        return getattr(aktives, name)(*args, **kwargs)


# ---------------------------------------------------------------------------------------
# 4. Die Werkbank
# ---------------------------------------------------------------------------------------


class Werkbank:
    """Lädt ein Paket der Werkstatt und leitet die Aufrufe des Spiels dorthin."""

    def __init__(self, paket: str, gesperrt=()):
        """Lädt ``paket``; ``gesperrt`` nennt Fähigkeiten, die für Tests als offen gelten."""
        self.paket = paket
        self._gesperrt = tuple(gesperrt)
        # Der Ordner des Pakets: Daran erkennt die Werkbank, welche Zeile einer Fehlerspur
        # in der Werkstatt liegt.
        ordner = os.path.abspath(importlib.import_module(paket).__path__[0])
        self._ordner = os.path.normcase(ordner) + os.sep
        # Fähigkeiten, die selbst offen sind: gesperrt, ein Name fehlt, oder NochOffen kam.
        # Fähigkeiten, die nur auf eine andere warten, stehen hier nicht.
        self._selbst_offen = set()
        self._module = self._lade(frisch=False)
        self._probiere_alles()

    # ----- Laden ------------------------------------------------------------------------

    def lade_neu(self) -> None:
        """Liest die Module neu ein; bei einem Fehler bleibt der alte Code in Betrieb."""
        self._module = self._lade(frisch=True)
        self._probiere_alles()

    def _lade(self, frisch):
        """Importiert die Module der Werkstatt und liefert Modulname -> Modul (oder None).

        ``frisch`` wirft zuerst alle schon geladenen Module des Pakets weg, damit Python die
        Dateien wirklich neu liest und auch gelöschte Namen verschwinden. Geht dabei etwas
        schief, kommen die alten Module zurück an ihren Platz.
        """
        importlib.invalidate_caches()
        vorher = {}
        if frisch:
            vorher = self._geladene_module()
            self._wirf_weg(vorher)
        module = {}
        try:
            for modulname in MODULE:
                module[modulname] = self._lade_modul(modulname)
        except Exception as fehler:
            if frisch:
                self._setze_zurueck(vorher)
            raise self._lernfehler_beim_laden(fehler) from fehler
        return module

    def _lade_modul(self, modulname):
        voller_name = f"{self.paket}.{modulname}"
        try:
            return importlib.import_module(voller_name)
        except ModuleNotFoundError as fehler:
            if fehler.name == voller_name:
                return None  # Die Datei fehlt: Ihre Fähigkeiten sind offen.
            raise  # Das Modul gibt es, aber es importiert selbst etwas, das fehlt.

    def _geladene_module(self):
        """Liefert alle geladenen Module unterhalb des Pakets: voller Name -> Modul."""
        anfang = self.paket + "."
        return {name: modul for name, modul in sys.modules.items() if name.startswith(anfang)}

    def _wirf_weg(self, module):
        """Lässt Python diese Module vergessen, an allen drei Stellen, an denen es sie kennt.

        1. ``sys.modules``: Sonst liefert ``import`` einfach das alte Modul.
        2. Das Paket selbst: ``from . import horde`` schaut zuerst dort nach.
        3. Die übersetzte Datei in ``__pycache__``: Python erkennt eine Änderung nur an
           Uhrzeit (in ganzen Sekunden) und Größe der Datei; beides kann gleich geblieben sein.
        """
        paket = sys.modules[self.paket]
        for name, modul in module.items():
            del sys.modules[name]
            kurz = name[len(self.paket) + 1 :]
            if getattr(paket, kurz, None) is modul:
                delattr(paket, kurz)
            quelle = getattr(modul, "__file__", None)
            if quelle and quelle.endswith(".py"):
                try:
                    os.remove(importlib.util.cache_from_source(quelle))
                except (OSError, NotImplementedError):
                    pass  # Es gab keine übersetzte Datei, oder sie lässt sich nicht löschen.

    def _setze_zurueck(self, vorher):
        """Räumt halb geladene Module weg und setzt die alten wieder ein.

        Weggeräumt wird wie beim frischen Laden an allen drei Stellen. Sonst bliebe ein
        Hilfsmodul, das erst der misslungene Versuch geladen hat, am Paket hängen.
        """
        self._wirf_weg(self._geladene_module())
        sys.modules.update(vorher)
        paket = sys.modules[self.paket]
        for name, modul in vorher.items():
            kurz = name[len(self.paket) + 1 :]
            if "." not in kurz:
                setattr(paket, kurz, modul)

    # ----- Was ist offen? ---------------------------------------------------------------

    def _probiere_alles(self):
        """Stellt für jede Fähigkeit fest, ob sie selbst offen ist."""
        self._selbst_offen = set(self._gesperrt)
        for faehigkeit in FAEHIGKEITEN:
            if self._probe_meldet_offen(faehigkeit):
                self._selbst_offen.add(faehigkeit)

    def _probe_meldet_offen(self, faehigkeit):
        eintrag = FAEHIGKEITEN[faehigkeit]
        modul = self._module[eintrag["modul"]]
        if modul is None:
            return True
        for name in eintrag["namen"]:
            if not hasattr(modul, name):
                return True
        for probe in PROBEN[faehigkeit]:
            try:
                probe(modul)
            except NochOffen:
                return True
            except Exception:
                # Ein anderer Fehler heißt nicht "offen". Er zeigt sich im Spiel als
                # Lernfehler mit Datei und Zeile; hier soll er den Start nicht aufhalten.
                pass
        return False

    def ist_offen(self, faehigkeit: str) -> bool:
        """Sagt, ob für diese Fähigkeit gerade der Ersatz benutzt wird."""
        if faehigkeit in self._selbst_offen:
            return True
        for andere in ABHAENGIG[faehigkeit]:
            if self.ist_offen(andere):
                return True
        return False

    def offene(self) -> list[str]:
        """Liefert alle offenen Fähigkeiten in der Reihenfolge des Verzeichnisses."""
        return [faehigkeit for faehigkeit in FAEHIGKEITEN if self.ist_offen(faehigkeit)]

    def wartet_auf(self, faehigkeit: str) -> list[int]:
        """Liefert die Nummern der Missionen, auf die diese Fähigkeit wartet.

        Entscheidung: Genannt werden nur die Missionen aus ``braucht``, deren Fähigkeit
        gerade offen ist. Eine Fähigkeit, die selbst offen ist, wartet auf nichts: Bei ihr
        ist die eigene Mission der nächste Schritt.
        """
        if faehigkeit in self._selbst_offen:
            return []
        nummern = []
        for nummer in gebrauchte_missionen(faehigkeit):
            if self.ist_offen(MISSION[nummer]["faehigkeit"]):
                nummern.append(nummer)
        return nummern

    # ----- Aufrufen ---------------------------------------------------------------------

    def rufe(self, faehigkeit: str, name: str, *args, **kwargs):
        """Ruft die Funktion ``name`` der Werkstatt auf, oder ihren Ersatz."""
        if not self.ist_offen(faehigkeit):
            funktion = self._hole(faehigkeit, name)
            ergebnis = self.versuche(faehigkeit, name, funktion, args, kwargs)
            if ergebnis is not OHNE_ANTWORT:
                return ergebnis
        return ersatz.ersatz_fuer(faehigkeit, name)(*args, **kwargs)

    def erzeuge(self, faehigkeit: str, klasse: str, *args, **kwargs):
        """Erzeugt ein Objekt der Klasse ``klasse`` der Werkstatt, oder ihres Ersatzes."""
        echtes = None
        if not self.ist_offen(faehigkeit):
            bauplan = self._hole(faehigkeit, klasse)
            echtes = self.versuche(faehigkeit, klasse, bauplan, args, kwargs)
            if echtes is OHNE_ANTWORT:
                echtes = None
        werkstueck = Werkstueck(self, faehigkeit, klasse, echtes, args, kwargs)
        if echtes is None:
            # Die Ersatzklasse wird sofort gebraucht. Fehlt sie, fällt das hier auf und
            # nicht erst irgendwann beim ersten Methodenaufruf.
            werkstueck._aktives()
        return werkstueck

    def strategien(self) -> dict:
        """Liefert die Zielstrategien: Name -> Funktion.

        Entscheidung: Ist die Fähigkeit gelöst, sind es die Einträge von ``STRATEGIEN`` der
        Werkstatt, jeder so eingepackt, dass sein Aufruf wie bei ``rufe`` behandelt wird.
        Ist sie offen, gibt es nur ``{"zufall": Ersatz}``.
        """
        if self.ist_offen("strategien"):
            return {"zufall": ersatz.ersatz_fuer("strategien", "zufall")}
        modul = self._module[FAEHIGKEITEN["strategien"]["modul"]]
        tabelle = modul.STRATEGIEN
        if not isinstance(tabelle, dict):
            raise Lernfehler(
                "strategien",
                modul.__file__,
                0,
                "TypeError",
                "STRATEGIEN muss ein Wörterbuch sein: Name -> Funktion",
                mission_von("strategien", "STRATEGIEN"),
            )
        return {name: self._packe_strategie_ein(name, tabelle[name]) for name in tabelle}

    def _packe_strategie_ein(self, name, funktion):
        # functools.wraps merkt sich die echte Funktion (als ``__wrapped__``). So findet das
        # Spiel später noch ihre Datei und Zeile.
        @functools.wraps(funktion)
        def strategie(kandidaten, turm):
            if not self.ist_offen("strategien"):
                ergebnis = self.versuche("strategien", name, funktion, (kandidaten, turm), {})
                if ergebnis is not OHNE_ANTWORT:
                    return ergebnis
            return ersatz.ersatz_fuer("strategien", "zufall")(kandidaten, turm)

        return strategie

    def _hole(self, faehigkeit, name):
        """Holt einen Namen der Fähigkeit aus dem Modul der Werkstatt."""
        eintrag = FAEHIGKEITEN[faehigkeit]
        if name not in eintrag["namen"]:
            # Das wäre ein Fehler im Spiel selbst, nicht in der Werkstatt.
            raise RuntimeError(f"Die Fähigkeit {faehigkeit!r} hat keinen Namen {name!r}.")
        return getattr(self._module[eintrag["modul"]], name)

    def versuche(self, faehigkeit, name, ziel, args, kwargs, anfang=None):
        """Ruft ``ziel`` aus der Werkstatt auf und behandelt, was dabei schiefgehen kann.

        Meldet der Code NochOffen, gilt die Fähigkeit ab jetzt als offen, und es kommt
        ``OHNE_ANTWORT`` zurück: Dann ist der Ersatz an der Reihe. Jeder andere Fehler wird
        ein ``Lernfehler``. ``name`` ist der Name aus dem Verzeichnis der Missionen (bei
        einer Methode der Name ihrer Klasse); daran hängt die Nummer der Mission. Liegt
        keine Zeile der Fehlerspur in der Werkstatt, zeigt der Lernfehler auf die erste Zeile
        von ``anfang`` (ohne Angabe: von ``ziel``).
        """
        try:
            return ziel(*args, **kwargs)
        except NochOffen:
            self._selbst_offen.add(faehigkeit)
            return OHNE_ANTWORT
        except Lernfehler:
            raise  # Kommt schon fertig von einem Aufruf weiter innen.
        except Exception as fehler:
            ort = self._ort_in_der_werkstatt(fehler) or erste_zeile(anfang or ziel)
            raise Lernfehler(
                faehigkeit,
                ort[0],
                ort[1],
                type(fehler).__name__,
                str(fehler),
                mission_von(faehigkeit, name),
                "".join(traceback.format_exception(fehler)),
            ) from fehler

    # ----- Fehler mit Ort ---------------------------------------------------------------

    def _ort_in_der_werkstatt(self, fehler):
        """Sucht in der Fehlerspur die innerste Zeile, die in der Werkstatt liegt."""
        ort = None
        for rahmen in traceback.extract_tb(fehler.__traceback__):
            datei = os.path.normcase(os.path.abspath(rahmen.filename))
            if datei.startswith(self._ordner):
                ort = (rahmen.filename, rahmen.lineno)
        return ort

    def _lernfehler_beim_laden(self, fehler):
        """Macht aus einem Fehler beim Importieren einen Lernfehler.

        Entscheidung: Bei einem Tippfehler (SyntaxError) stehen Datei und Zeile des
        Tippfehlers im Lernfehler. Fähigkeit und Mission bleiben None, denn die Datei ist als
        Ganzes nicht lesbar, und in ihr liegen meist mehrere Missionen.
        """
        if isinstance(fehler, SyntaxError):
            ort = (fehler.filename, fehler.lineno)
            text = fehler.msg
        else:
            ort = self._ort_in_der_werkstatt(fehler) or ("?", 0)
            text = str(fehler)
        spur = "".join(traceback.format_exception(fehler))
        return Lernfehler(None, ort[0], ort[1], type(fehler).__name__, text, None, spur)


def waehle_paket(loesung: bool | None = None) -> str:
    """Entscheidet zwischen ``werkstatt`` und ``loesung``; ``None`` fragt RUDERSDORF_LOESUNG.

    Entscheidung: ``False`` heißt immer ``werkstatt``, auch wenn die Variable gesetzt ist.
    Die Lösung wird nur geladen, wenn jemand das ausdrücklich verlangt: mit ``True`` oder mit
    RUDERSDORF_LOESUNG=1.
    """
    if loesung is None:
        loesung = os.environ.get("RUDERSDORF_LOESUNG") == "1"
    if loesung:
        return "loesung"
    return "werkstatt"
