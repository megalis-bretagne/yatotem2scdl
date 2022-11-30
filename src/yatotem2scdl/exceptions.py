from pathlib import Path
from typing import Optional

#
# Exceptions liees aux traitements
#
class ConversionErreur(Exception):
    """Exception de base levée lors de la conversion en SCDL"""

    def __init__(self, message: Optional[str] = None) -> None:
        self.message = message
        super().__init__(self.message)


class ExtractionMetadataErreur(Exception):
    """Levée lorsqu'on ne peut extraire les metadata d'un fichier budget totem"""

    def __init__(self, message: Optional[str] = None) -> None:
        self.message = message
        super().__init__(self.message)


#
# Exceptions lorsque les donnees ne sont pas dans le format attendu
#
class CaractereAppostropheErreur(ConversionErreur):
    """Levée lorsqu'un caractère apostrophe interdit a été fourni par l'utilisateur"""

    def __init__(self, chaine: str) -> None:
        self.chaine = chaine
        message = "La chaîne suivante contient une apostrophe: " f"\n\t{self.chaine}"
        super().__init__(message)


class TotemInvalideErreur(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class SiretInvalideErreur(TotemInvalideErreur):
    """Levée lorsque le siret du fichier totem a un format invalide"""

    def __init__(self, siret: Optional[str]) -> None:
        self.siret = siret
        message = f"'{self.siret}' n'est pas un siret valide"
        super().__init__(message)


class NomenclatureInvalideErreur(TotemInvalideErreur):
    """Levée lorsque la nomenclature d'un fichier totem est introuvable vis-à-vis des plans de compte"""

    def __init__(self, nomenclature: Optional[str], pdcs_dpath: Path) -> None:
        self.nomenclature = nomenclature
        self.pdc_path = pdcs_dpath
        message = f"La nomenclature '{self.nomenclature}' est introuvable auprès des plans de comptes situés dans '{self.pdc_path}'"
        super().__init__(message)


class AnneeExerciceInvalideErreur(TotemInvalideErreur):
    """Levée lorsque l'année d'exercice d'un fichier totem est invalide"""

    def __init__(self, annee: Optional[str]) -> None:
        message = f"L'année {annee} est invalide"
        super().__init__(message)


class EtapeBudgetaireInconnueErreur(TotemInvalideErreur):
    """Levée lorsque l'étape budgetaire d'un fichier totem est invalide"""

    def __init__(self, etape_str: Optional[str]) -> None:
        message = f"L'étape budgetaire {etape_str} est invalide"
        super().__init__(message)
