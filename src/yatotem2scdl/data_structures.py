from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

class EtapeBudgetaireStrInvalideError(Exception):
    """Levée lorsqu'une chaine ne correspond pas à une étape budgetaire valide"""

    def __init__(self, etape_str: Optional[str]):
        self.message = f"L'étape budgetaire {etape_str} est invalide"


class EtapeBudgetaire(Enum):
    # Alias des différentes étapes budgetaires
    # Le premier alias corresponse à la valeur au sein de la norme scdl
    # https://schema.data.gouv.fr/scdl/budget/0.8.1/documentation.html#etape-budgetaire-propriete-bgt-natdec
    __primitif_aliases__ = ["budget primitif", "Budget primitif", "primitif"]
    __supplementaire_aliases__ = [
        "budget supplémentaire",
        "Budget supplémentaire",
        "supplémentaire",
        "supplementaire",
    ]
    __modificative_aliases__ = [
        "décision modificative",
        "Décision modificative",
        "modificative",
        "modificatif",
    ]
    __ca_aliases__ = [
        "compte administratif",
        "compte administratif",
        "ca",
        "administratif",
    ]

    # Les valeurs de l'enum correspondent au code NatDec des fichiers totem
    PRIMITIF = 1
    DECISION_MODIF = 2
    BUDGET_SUPP = 3
    COMPTE_ADMIN = 9

    @staticmethod
    def from_str(chaine: str):
        """ Parse la chaine donnée pour en faire une étape budgetaire.

        Chaque étape budgétaire accepte une liste d'alias comme chaine valide. 
        Par exemple, pour le compte administratif, les valeurs acceptées sont:

         - compte administratif
         - ca
         - administratif

        Raises:
            EtapeBudgetaireStrInvalideError: en cas de chaine invalide
        """
        if chaine in EtapeBudgetaire.__primitif_aliases__:
            return EtapeBudgetaire.PRIMITIF
        elif chaine in EtapeBudgetaire.__supplementaire_aliases__:
            return EtapeBudgetaire.BUDGET_SUPP
        elif chaine in EtapeBudgetaire.__modificative_aliases__:
            return EtapeBudgetaire.DECISION_MODIF
        elif chaine in EtapeBudgetaire.__ca_aliases__:
            return EtapeBudgetaire.COMPTE_ADMIN
        else:
            raise EtapeBudgetaireStrInvalideError(chaine)

    def to_scdl_compatible_str(self):
        if self is EtapeBudgetaire.PRIMITIF:
            return EtapeBudgetaire.__primitif_aliases__[0]
        elif self is EtapeBudgetaire.DECISION_MODIF:
            return EtapeBudgetaire.__modificative_aliases__[0]
        elif self is EtapeBudgetaire.BUDGET_SUPP:
            return EtapeBudgetaire.__supplementaire_aliases__[0]
        elif self is EtapeBudgetaire.COMPTE_ADMIN:
            return EtapeBudgetaire.__ca_aliases__[0]
        else:
            assert (
                False
            ), "Erreur de programmation, merci de bien utiliser l'enum EtapeBudgetaire"

    def __str__(self) -> str:
        return self.to_scdl_compatible_str()


@dataclass()
class TotemBudgetMetadata:
    annee_exercice: int  # Année d'exercice
    id_etablissement: int  # ID de l'établissement, son SIRET
    etape_budgetaire: EtapeBudgetaire  # Etape budgetaire concernée par le document
    plan_de_compte: Optional[
        Path
    ]  # Chemin vers le plan de compte concernant ce fichier totem. Peut être None.


@dataclass()
class Options:
    """Options du processus de conversion"""

    lineterminator: Optional[str] = None
    inclure_header_csv: bool = True  # Inclure le nom des colonnes dans le CSV generé.
    xml_intermediaire_path: Optional[
        str
    ] = None  # Chemin du fichier pour écrire le XML intermédiaire
