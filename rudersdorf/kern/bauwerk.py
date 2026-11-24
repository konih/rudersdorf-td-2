"""Ein Bauwerk auf dem Spielfeld: ein Turm oder eine Palisade."""


class Bauwerk:
    """Ein Bauwerk; seine Werte kommen aus ``daten.BAUWERKE[art]``."""

    def __init__(self, art: str, zelle, auf_huegel=False):
        raise NotImplementedError
