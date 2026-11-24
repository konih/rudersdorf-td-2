"""Architektur: Wer darf wen importieren?

Der Spielkern rechnet nur und kennt kein pygame. Werkstatt und Lösung kennen vom Spiel nur
die Daten, die Fehlerklassen und die Übungen. Dieser Test liest jede Python-Datei der
bewachten Ordner mit ``ast`` und meldet jeden Import, der eine dieser Regeln bricht.
"""

import ast
import pathlib
import tempfile
import unittest
from typing import NamedTuple

WURZEL = pathlib.Path(__file__).resolve().parent.parent.parent

# Welche Regel in welchem Ordner gilt.
OHNE_PYGAME = ("rudersdorf/kern", "rudersdorf/labor", "werkstatt", "loesung")
OHNE_ANSICHT = ("rudersdorf/kern",)
NUR_ERLAUBTES = ("werkstatt", "loesung")
ERLAUBT = ("rudersdorf.daten", "rudersdorf.fehler", "rudersdorf.uebung")
BEWACHT = tuple(dict.fromkeys(OHNE_PYGAME + OHNE_ANSICHT + NUR_ERLAUBTES))

REGEL_PYGAME = "pygame ist hier verboten"
REGEL_ANSICHT = "der Kern darf die Ansicht nicht kennen"
REGEL_ERLAUBT = "aus rudersdorf sind hier nur daten, fehler und uebung erlaubt"
REGEL_ORDNER = "der Ordner fehlt"
REGEL_LESBAR = "die Datei lässt sich nicht als Python lesen"


class Verstoss(NamedTuple):
    """Ein Import, der eine Schichtregel bricht."""

    datei: str
    zeile: int
    regel: str
    name: str

    def __str__(self):
        ort = f"{self.datei}:{self.zeile}" if self.zeile else self.datei
        zusatz = f" ({self.name})" if self.name else ""
        return f"{ort}: {self.regel}{zusatz}"


def gehoert_zu(name, paket):
    """``rudersdorf.daten.ZELLE`` gehört zu ``rudersdorf.daten``, ``rudersdorf.datenbank`` nicht."""
    return name == paket or name.startswith(paket + ".")


def importierte_namen(baum, paket):
    """Liefert (zeile, voller Name) für alles, was die Datei importiert.

    ``paket`` sind die Ordner von der Wurzel bis zur Datei; damit werden relative Importe
    (``from ..ansicht import hud``) zu vollen Namen (``rudersdorf.ansicht.hud``).
    """
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.Import):
            for alias in knoten.names:
                yield knoten.lineno, alias.name
        elif isinstance(knoten, ast.ImportFrom):
            teile = []
            if knoten.level:
                teile.extend(paket[: max(0, len(paket) - (knoten.level - 1))])
            if knoten.module:
                teile.extend(knoten.module.split("."))
            for alias in knoten.names:
                yield knoten.lineno, ".".join([*teile, alias.name])
        elif isinstance(knoten, ast.Call):
            # importlib.import_module("pygame") und __import__("pygame") mit festem Text.
            funktion = knoten.func
            aufruf = getattr(funktion, "id", None) or getattr(funktion, "attr", None)
            if aufruf in ("__import__", "import_module") and knoten.args:
                erstes = knoten.args[0]
                if isinstance(erstes, ast.Constant) and isinstance(erstes.value, str):
                    yield knoten.lineno, erstes.value


def regeln_fuer(ordner, name):
    """Liefert die Regeln, die der Import ``name`` in ``ordner`` bricht."""
    if ordner in OHNE_PYGAME and gehoert_zu(name, "pygame"):
        yield REGEL_PYGAME
    if ordner in OHNE_ANSICHT and gehoert_zu(name, "rudersdorf.ansicht"):
        yield REGEL_ANSICHT
    if ordner in NUR_ERLAUBTES and gehoert_zu(name, "rudersdorf"):
        if not any(gehoert_zu(name, erlaubt) for erlaubt in ERLAUBT):
            yield REGEL_ERLAUBT


def finde_verstoesse(wurzel):
    """Durchsucht die bewachten Ordner unter ``wurzel`` und liefert alle Verstöße, sortiert."""
    wurzel = pathlib.Path(wurzel)
    verstoesse = []
    for ordner in BEWACHT:
        if not (wurzel / ordner).is_dir():
            verstoesse.append(Verstoss(ordner, 0, REGEL_ORDNER, ""))
            continue
        for datei in (wurzel / ordner).rglob("*.py"):
            kurz = datei.relative_to(wurzel)
            try:
                baum = ast.parse(datei.read_bytes(), filename=str(datei))
            except (SyntaxError, ValueError) as fehler:
                zeile = getattr(fehler, "lineno", None) or 1
                verstoesse.append(Verstoss(kurz.as_posix(), zeile, REGEL_LESBAR, ""))
                continue
            for zeile, name in importierte_namen(baum, kurz.parent.parts):
                for regel in regeln_fuer(ordner, name):
                    verstoesse.append(Verstoss(kurz.as_posix(), zeile, regel, name))
    return sorted(verstoesse)


# --- Hilfen für den Selbsttest ---------------------------------------------------------------

# Mit Absicht ausgeschrieben und nicht aus den Regeln oben abgeleitet: Fällt dort ein Ordner
# weg, muss der Selbsttest das merken.
ALLE_BEWACHTEN = ("rudersdorf/kern", "rudersdorf/labor", "werkstatt", "loesung")
GERUEST = ("rudersdorf", "rudersdorf/ansicht", "rudersdorf/uebung") + ALLE_BEWACHTEN


def baue_baum(wurzel, dateien, ohne=()):
    """Legt ein sauberes Grundgerüst an und schreibt die Dateien aus ``dateien`` hinein."""
    for ordner in GERUEST:
        if ordner not in ohne:
            (wurzel / ordner).mkdir(parents=True, exist_ok=True)
            (wurzel / ordner / "__init__.py").write_text("", encoding="utf-8")
    for pfad, text in dateien.items():
        ziel = wurzel / pfad
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(text, encoding="utf-8")


def pruefe_baum(dateien, ohne=()):
    """Baut einen Baum in einem temporären Ordner und liefert (datei, zeile, regel) je Verstoß."""
    with tempfile.TemporaryDirectory() as ordner:
        wurzel = pathlib.Path(ordner)
        baue_baum(wurzel, dateien, ohne)
        return [(v.datei, v.zeile, v.regel) for v in finde_verstoesse(wurzel)]


PYGAME_FORMEN = (
    "import pygame\n",
    "import os, pygame\n",
    "import pygame.draw as malen\n",
    "from pygame import Rect\n",
    "from pygame.locals import *\n",
    "import importlib\nimportlib.import_module('pygame')\n",
    "x = 1\n__import__('pygame.mixer')\n",
    "def zeichne():\n    import pygame\n",
)

ANSICHT_FORMEN = (
    "import rudersdorf.ansicht\n",
    "import rudersdorf.ansicht.hud as hud\n",
    "from rudersdorf import ansicht\n",
    "from rudersdorf.ansicht import hud\n",
    "from rudersdorf.ansicht.hud import zeichne\n",
    "from .. import ansicht\n",
    "from ..ansicht import hud\n",
)

VERBOTENE_FORMEN = (
    "import rudersdorf\n",
    "import rudersdorf.kern.spiel\n",
    "import rudersdorf.werkbank as w\n",
    "from rudersdorf import werkbank\n",
    "from rudersdorf import *\n",
    "from rudersdorf.kern import spiel\n",
    "from rudersdorf.kern.spiel import Spiel\n",
    "from rudersdorf import datenbank\n",
    "import rudersdorf.fehlerhaft\n",
    "from rudersdorf.uebungen import x\n",
    "from ..rudersdorf import ersatz\n",
)

SAUBER = {
    # Die Ansicht darf pygame benutzen, und sie darf den Kern kennen.
    "rudersdorf/ansicht/fenster.py": "import pygame\nfrom rudersdorf.kern import spiel\n",
    # Der Kern kennt sich selbst, die Daten und die Standardbibliothek.
    "rudersdorf/kern/spiel.py": (
        '"""Hier steht nur das Wort: import pygame, from rudersdorf.ansicht import hud."""\n'
        "import random\n"
        "import pygame_werkzeug\n"
        "import rudersdorf\n"
        "from . import karte\n"
        "from .karte import Karte\n"
        "from .. import daten, werkbank\n"
        "from ..fehler import Lernfehler\n"
        "from rudersdorf.ansichten import x\n"
        "text = 'import pygame'\n"
        "ansicht = __import__(text)\n"
    ),
    "rudersdorf/labor/lauf.py": "from rudersdorf.kern.spiel import Spiel\n",
    "werkstatt/tuerme.py": (
        "import math\n"
        "import rudersdorf.daten\n"
        "import rudersdorf.uebung.pruefer as pruefer\n"
        "from rudersdorf import daten, fehler, uebung\n"
        "from rudersdorf.daten import ZELLE\n"
        "from rudersdorf.fehler import NochOffen\n"
        "from rudersdorf.uebung.pruefer import KammerTest\n"
        "from . import horde\n"
        "from .horde import Frost\n"
    ),
    "loesung/tuerme.py": "from rudersdorf.daten import ZELLE\nfrom .horde import Frost\n",
}


class Selbsttest(unittest.TestCase):
    """Beweist an erfundenen Bäumen, dass die Suche jede Regel wirklich prüft."""

    def test_sauberer_baum_ist_ohne_verstoss(self):
        self.assertEqual([], pruefe_baum(SAUBER))

    def test_pygame_ist_in_jedem_bewachten_ordner_verboten(self):
        for ordner in ALLE_BEWACHTEN:
            for form in PYGAME_FORMEN:
                with self.subTest(ordner=ordner, form=form):
                    zeile = form.count("\n")
                    self.assertEqual(
                        [(f"{ordner}/x.py", zeile, REGEL_PYGAME)],
                        pruefe_baum({f"{ordner}/x.py": form}),
                    )

    def test_pygame_wird_auch_in_unterordnern_gefunden(self):
        self.assertEqual(
            [("rudersdorf/kern/tief/tiefer/x.py", 1, REGEL_PYGAME)],
            pruefe_baum({"rudersdorf/kern/tief/tiefer/x.py": "import pygame\n"}),
        )

    def test_kern_importiert_ansicht(self):
        for form in ANSICHT_FORMEN:
            with self.subTest(form=form):
                self.assertEqual(
                    [("rudersdorf/kern/x.py", 1, REGEL_ANSICHT)],
                    pruefe_baum({"rudersdorf/kern/x.py": form}),
                )

    def test_kern_importiert_ansicht_aus_einem_unterordner(self):
        self.assertEqual(
            [("rudersdorf/kern/tief/x.py", 2, REGEL_ANSICHT)],
            pruefe_baum({"rudersdorf/kern/tief/x.py": "import os\nfrom ...ansicht.hud import z\n"}),
        )

    def test_werkstatt_und_loesung_importieren_nur_erlaubtes(self):
        for ordner in ("werkstatt", "loesung"):
            for form in VERBOTENE_FORMEN:
                with self.subTest(ordner=ordner, form=form):
                    self.assertEqual(
                        [(f"{ordner}/x.py", 1, REGEL_ERLAUBT)],
                        pruefe_baum({f"{ordner}/x.py": form}),
                    )

    def test_nur_der_verbotene_name_einer_zeile_wird_gemeldet(self):
        with tempfile.TemporaryDirectory() as ordner:
            wurzel = pathlib.Path(ordner)
            baue_baum(wurzel, {"werkstatt/x.py": "from rudersdorf import daten, werkbank\n"})
            namen = [v.name for v in finde_verstoesse(wurzel)]
        self.assertEqual(["rudersdorf.werkbank"], namen)

    def test_fehlender_ordner_ist_ein_verstoss(self):
        for ordner in ALLE_BEWACHTEN:
            with self.subTest(ordner=ordner):
                self.assertEqual([(ordner, 0, REGEL_ORDNER)], pruefe_baum({}, ohne=(ordner,)))

    def test_unlesbare_datei_ist_ein_verstoss(self):
        self.assertEqual(
            [("loesung/x.py", 1, REGEL_LESBAR)],
            pruefe_baum({"loesung/x.py": "def kaputt(:\n"}),
        )

    def test_ein_baum_mit_einem_verstoss_jeder_art(self):
        dateien = dict(SAUBER)
        dateien.update(
            {
                "rudersdorf/kern/a.py": "import pygame\n",
                "rudersdorf/kern/b.py": "import os\nfrom rudersdorf.ansicht import hud\n",
                "rudersdorf/labor/c.py": "from pygame import Rect\n",
                "werkstatt/d.py": "import os\n\nimport pygame\n",
                "werkstatt/e.py": "from rudersdorf.kern import spiel\n",
                "loesung/f.py": "import pygame.draw\n",
                "loesung/g.py": "from rudersdorf import werkbank\n",
            }
        )
        self.assertEqual(
            [
                ("loesung/f.py", 1, REGEL_PYGAME),
                ("loesung/g.py", 1, REGEL_ERLAUBT),
                ("rudersdorf/kern/a.py", 1, REGEL_PYGAME),
                ("rudersdorf/kern/b.py", 2, REGEL_ANSICHT),
                ("rudersdorf/labor/c.py", 1, REGEL_PYGAME),
                ("werkstatt/d.py", 3, REGEL_PYGAME),
                ("werkstatt/e.py", 1, REGEL_ERLAUBT),
            ],
            pruefe_baum(dateien),
        )

    def test_die_meldung_nennt_datei_zeile_regel_und_namen(self):
        verstoss = Verstoss("werkstatt/x.py", 7, REGEL_ERLAUBT, "rudersdorf.kern")
        self.assertEqual(
            "werkstatt/x.py:7: aus rudersdorf sind hier nur daten, fehler und uebung erlaubt"
            " (rudersdorf.kern)",
            str(verstoss),
        )
        self.assertEqual("loesung: der Ordner fehlt", str(Verstoss("loesung", 0, REGEL_ORDNER, "")))


class Schichten(unittest.TestCase):
    def test_das_projekt_haelt_die_schichten_ein(self):
        verstoesse = [str(v) for v in finde_verstoesse(WURZEL)]
        self.assertEqual([], verstoesse, "Verbotene Importe:\n" + "\n".join(verstoesse))


if __name__ == "__main__":
    unittest.main()
