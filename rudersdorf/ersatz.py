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

Noch ist das Verzeichnis leer: Jeder Ersatz kommt zusammen mit dem Teil des Spiels, zu dem
er gehört.
"""

ERSATZ: dict[str, dict[str, object]] = {}
