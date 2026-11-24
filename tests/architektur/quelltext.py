"""Hilfen der Architekturtests: Python-Dateien lesen, ohne sie auszuführen."""

import ast
import pathlib

FUNKTION = (ast.FunctionDef, ast.AsyncFunctionDef)


def lies_modul(ordner, modul):
    """Liefert den Syntaxbaum von ``ordner/modul.py``; ``None``, wenn das kein Python ist."""
    datei = pathlib.Path(ordner) / f"{modul}.py"
    try:
        return ast.parse(datei.read_bytes(), filename=str(datei))
    except (OSError, SyntaxError, ValueError):
        return None


def definitionen(baum, name):
    """Alle Funktionen und Klassen mit diesem Namen, die ganz außen im Modul stehen."""
    arten = (*FUNKTION, ast.ClassDef)
    return [k for k in baum.body if isinstance(k, arten) and k.name == name]


def methoden(klasse):
    """Die Funktionen, die direkt im Rumpf der Klasse stehen."""
    return [k for k in klasse.body if isinstance(k, FUNKTION)]


def zugewiesene_namen(baum):
    """Die Namen, denen ganz außen im Modul etwas zugewiesen wird (``STRATEGIEN = {...}``)."""
    namen = set()
    for knoten in baum.body:
        if isinstance(knoten, ast.Assign):
            ziele = knoten.targets
        elif isinstance(knoten, ast.AnnAssign) and knoten.value is not None:
            ziele = [knoten.target]
        else:
            continue
        namen.update(ziel.id for ziel in ziele if isinstance(ziel, ast.Name))
    return namen


def schreibe_dateien(wurzel, dateien):
    """Schreibt ``{"paket/modul.py": text}`` unter ``wurzel``; für die Selbsttests."""
    for pfad, text in dateien.items():
        ziel = pathlib.Path(wurzel) / pfad
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(text, encoding="utf-8")
