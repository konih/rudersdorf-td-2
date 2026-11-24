"""Das Verzeichnis aller 26 Missionen.

Hier steht für jede Mission genau einmal, wie sie heißt, in welcher Datei der Werkstatt sie
liegt, welche Namen dort zu ihr gehören und welche Fähigkeit des Spiels sie freischaltet.
Der Prüfer, die Missionstafel, die Ersatz-Hinweise im Spiel und die Tests lesen alle diese
eine Liste.
"""

SPUREN = {
    "A": "Das Raster",
    "B": "Die Türme",
    "C": "Die Horde",
    "D": "Dorf und Magie",
    "E": "Die Werkstatt",
}

DOKUMENTE = {
    "A": "missionen/spur_a_raster.md",
    "B": "missionen/spur_b_tuerme.md",
    "C": "missionen/spur_c_horde.md",
    "D": "missionen/spur_d_dorf_und_magie.md",
    "E": "missionen/spur_e_werkstatt.md",
}


def mission(nummer, spur, titel, modul, namen, faehigkeit, sterne, braucht=()):
    """Baut den Eintrag einer Mission; Testklasse und Dokument ergeben sich aus der Nummer."""
    return {
        "nummer": nummer,
        "spur": spur,
        "titel": titel,
        "modul": modul,
        "namen": list(namen),
        "faehigkeit": faehigkeit,
        "braucht": list(braucht),
        "testklasse": f"tests.missionen.test_m{nummer:02d}.Mission{nummer:02d}",
        "dokument": f"{DOKUMENTE[spur]}#mission-{nummer}",
        "sterne": sterne,
    }


MISSIONEN = [
    # Spur A · Das Raster
    mission(1, "A", "Die Karte lesen", "raster", ["lies_karte", "finde"], "karten", 1),
    mission(2, "A", "Nachbarn", "raster", ["nachbarn", "ist_begehbar"], "wegfindung", 1),
    mission(3, "A", "Der kürzeste Weg", "raster", ["abstandskarte"], "wegfindung", 2),
    mission(4, "A", "Dem Weg folgen", "raster", ["naechster_schritt"], "wegfindung", 1),
    mission(5, "A", "Nicht einmauern!", "raster", ["darf_bauen"], "bauregel", 3, braucht=[2, 3, 4]),
    # Spur B · Die Türme
    mission(6, "B", "Wer ist in Reichweite?", "tuerme", ["in_reichweite"], "reichweite", 1),
    mission(
        7,
        "B",
        "Zielstrategien",
        "strategien",
        ["erster", "letzter", "staerkster", "schwaechster", "naechster", "STRATEGIEN"],
        "strategien",
        1,
    ),
    mission(8, "B", "Deine eigene Strategie", "strategien", ["STRATEGIEN"], "strategien", 2),
    mission(9, "B", "Der Kettenblitz", "tuerme", ["kettenblitz"], "kettenblitz", 2),
    mission(10, "B", "Die Turmschmiede", "tuerme", ["wende_ausbau_an"], "ausbau", 2),
    # Spur C · Die Horde
    mission(11, "C", "Schadensarten", "horde", ["berechne_schaden"], "schadensarten", 1),
    mission(
        12,
        "C",
        "Effekte",
        "horde",
        ["Effekt", "Frost", "Gift", "Brand", "Betaeubung"],
        "effekte",
        2,
    ),
    mission(
        13,
        "C",
        "Die Effektliste",
        "horde",
        ["fuege_effekt_hinzu", "gesamt_tempo_faktor", "raeume_effekte_auf"],
        "effekte",
        2,
    ),
    mission(
        14,
        "C",
        "Besondere Fähigkeiten",
        "horde",
        ["Regeneration", "Heiler", "Beschwoerer"],
        "faehigkeiten",
        2,
    ),
    mission(15, "C", "Die Wellenschmiede", "horde", ["erzeuge_welle"], "wellen", 3),
    # Spur D · Dorf und Magie
    mission(16, "D", "Was fehlt noch?", "dorf", ["fehlende_voraussetzungen"], "voraussetzungen", 1),
    mission(17, "D", "Die Kraft des Dorfes", "dorf", ["sammle_boni"], "boni", 2),
    mission(18, "D", "Der Bauplan", "dorf", ["bauplan"], "bauplan", 3),
    mission(19, "D", "Mana und Abklingzeit", "magie", ["Zauber"], "magie", 2),
    mission(
        20,
        "D",
        "Das Zauberbuch",
        "magie",
        ["Feuerball", "Eissturm", "Blitzschlag", "Segen", "Glockenschlag"],
        "magie",
        3,
        braucht=[9, 12, 13],
    ),
    # Spur E · Die Werkstatt
    mission(
        21,
        "E",
        "Fehlerjagd",
        "fehlerjagd",
        ["leeres_raster", "entferne_besiegte", "zaehle_arten"],
        None,
        2,
    ),
    mission(
        22,
        "E",
        "Aufräumen",
        "aufraeumen",
        ["turm_trifft", "anzahl_in_reichweite", "naechster_gegner", "ist_ueberlastet"],
        None,
        2,
    ),
    mission(23, "E", "Eigene Tests", "meine_tests", ["MeineTests"], None, 3),
    mission(24, "E", "Der Dorfschreiber", "schreiber", ["zu_daten", "aus_daten"], "speichern", 3),
    mission(25, "E", "Das Labor", "forschung", ["auswertung"], "auswertung", 2),
    mission(26, "E", "Der Bot", "forschung", ["mein_bot"], "bot", 3, braucht=[2, 3, 4, 5, 6, 7]),
]
