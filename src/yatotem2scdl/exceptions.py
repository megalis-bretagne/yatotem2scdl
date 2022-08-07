
class ConversionErreur(Exception):
    """Exception de base levée lors de la conversion en SCDL"""
    pass

class CaractereAppostropheErreur(ConversionErreur):
    """Levée lorsqu'un caractère apostrophe interdit a été fourni par l'utilisateur"""

    def __init__(self, chaine: str) -> None:
        self.chaine = chaine
        message = (
            "La chaîne suivante contient une apostrophe: "
            f"\n\t{self.chaine}"
        )
        super().__init__(message)
    pass