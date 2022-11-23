from io import TextIOBase
from typing import Optional
from xml.etree.ElementTree import ElementTree
from pathlib import Path

from yatotem2scdl import logger

import os
import csv

from yatotem2scdl.exceptions import (
    AnneeExerciceInvalideErreur,
    ConversionErreur,
    CaractereAppostropheErreur,
    EtapeBudgetaireInconnueErreur,
    ExtractionMetadataErreur,
    NomenclatureInvalideErreur,
    SiretInvalideErreur,
    TotemInvalideErreur,
)

from yatotem2scdl.data_structures import EtapeBudgetaire, Options, TotemBudgetMetadata

from lxml import etree

_BUDGET_XSLT = Path(os.path.dirname(__file__)) / "xsl" / "totem2xmlcsv.xsl"
_PDC_VIDE = Path(os.path.dirname(__file__)) / "planDeCompte-vide.xml"


class ConvertisseurTotemBudget:
    def __init__(self, xslt_budget: Path = None):
        """Convertisseur de fichier totem budget vers SCDL

        Args:
            xslt_budget (Path, optional): Surcharge le fichier de transformation XSLT en
              charge de la construction du modèle intermédiaire. Defaults to None.
        """
        if xslt_budget is None:
            xslt_budget = _BUDGET_XSLT
        self.__xslt_budget = xslt_budget

    def totem_budget_vers_scdl(
        self,
        totem_fpath: Path,
        pdcs_dpath: Path,
        output: TextIOBase,
        options: Options = Options(),
    ):
        """Convertit un fichier totem vers un SCDL budget

        Args:
            totem_fpath (Path): Chemin vers le fichier totem.
            pdcs_dpath (Path): Chemin contenant les plans de comptes.
            output (TextIOBase): TextIO vers lequel le CSV est écrit.
            options (Options, optional): Diverses options. Defaults to Options().

        Raises:
            ConversionErreur: ou une classe fille suivant la nature de l'erreur.
        """

        def _extraire_pdc_for_conversion(tree, pdcs_dpath):
            try:
                pdc_path = _extraire_plan_de_compte(tree, pdcs_dpath)
                return pdc_path
            except TotemInvalideErreur:
                logger.warning(
                    f"Impossible de trouver un plan de compte pour le fichier totem."
                    f" Le SCDL sera probablement incomplet"
                )
                return None

        if options is None:
            options = Options()

        logger.info(f"Conversion du fichier budget totem: {totem_fpath}")
        try:
            totem_tree: ElementTree = etree.parse(totem_fpath)
            pdc_path = _extraire_pdc_for_conversion(totem_tree, pdcs_dpath)
            transformed_tree = self._transform(
                totem_tree=totem_tree, pdc_fpath=pdc_path, options=options
            )
            _xml_to_csv(transformed_tree, output, options)

        except ConversionErreur as err:
            raise err
        except Exception as err:
            raise ConversionErreur() from err

    def totem_budget_metadata(
        self,
        totem_fpath: Path,
        pdcs_dpath: Path,
    ) -> TotemBudgetMetadata:
        def _extraire_pdc_for_metadata(tree, pdcs_dpath):
            try:
                pdc_path = _extraire_plan_de_compte(tree, pdcs_dpath)
                return pdc_path
            except TotemInvalideErreur as err:
                logger.warning(str(err))
                return None

        try:
            totem_tree: ElementTree = etree.parse(totem_fpath)
            pdc_path = _extraire_pdc_for_metadata(totem_tree, pdcs_dpath)
            code_etape = _xpath_totem_budget_etape(totem_tree)
            id_etab = _xpath_totem_budget_id_etab(totem_tree)
            annee = _xpath_totem_budget_annee_exercice(totem_tree)

            etape = _parse_code_etape(code_etape)
            annee_i = _parse_annee_exercice(annee)
            id_etab_siret = _parse_siret(id_etab)

            return TotemBudgetMetadata(
                annee_exercice=annee_i,
                etape_budgetaire=etape,
                id_etablissement=id_etab_siret,
                plan_de_compte=pdc_path,
            )

        except Exception as err:
            raise ExtractionMetadataErreur(str(err)) from err

    def budget_scdl_entetes(self) -> str:
        """Récupère la ligne d'entete du SCDL correspondant aux budgets"""

        xslt_tree: ElementTree = etree.parse(self.__xslt_budget)
        entetes = xslt_tree.xpath(  # type:ignore
            "/xsl:stylesheet/xsl:template/csv/header/column/@name",
            namespaces={"xsl": "http://www.w3.org/1999/XSL/Transform"},
        )
        return ",".join(entetes)

    def _transform(
        self, totem_tree: ElementTree, pdc_fpath: Optional[Path], options: Options
    ) -> ElementTree:

        logger.debug(
            (
                f"\nTransformation du fichier totem"
                f"\n\tFichier XSL: {self.__xslt_budget}"
            )
        )

        xslt_tree = etree.parse(self.__xslt_budget.resolve())
        transform = etree.XSLT(xslt_input=xslt_tree)

        pdc_fpath_str = (
            str(pdc_fpath.resolve())
            if pdc_fpath is not None
            else str(_PDC_VIDE.resolve())
        )
        pdc_param = _as_xpath_str(pdc_fpath_str)

        transformed_tree = transform(totem_tree, plandecompte=pdc_param)

        intermediaire_fpath = options.xml_intermediaire_path
        if intermediaire_fpath is not None:
            _write_in_tmp(transformed_tree, intermediaire_fpath)

        return transformed_tree


def _extraire_plan_de_compte(totem_tree: ElementTree, pdcs_dpath: Path) -> Path:
    """Extrait le plan de compte à partir d'un xml totem

    Args:
        totem_tree (ElementTree): XML correspondant au fichier budget totem
        pdcs_dpath (Path): Chemin vers les plans de comptes

    Raises:
        AnneeExerciceInvalideErreur: Si l'année d'exercice est irrécupérable
        NomenclatureInvalideErreur: Si la nomenclature est invalide (aussi si aucun plan de compte ne correspond)

    Returns:
        Path: Chemin vers le plan de compte correspondant
    """

    namespaces = _namespaces()

    nomenclature: Optional[str] = totem_tree.findall(
        "/db:Budget/db:EnTeteBudget/db:Nomenclature", namespaces
    )[0].attrib.get("V")
    year: Optional[str] = _xpath_totem_budget_annee_exercice(totem_tree)

    if nomenclature is None:
        raise NomenclatureInvalideErreur(None, pdcs_dpath)  # type: ignore
    if year is None:
        raise AnneeExerciceInvalideErreur(year)

    logger.debug(f"Version de plan de compte trouvée: ({year}, {nomenclature})")

    (n1, n2) = nomenclature.split("-", 1)
    pdc_path = pdcs_dpath / year / n1 / n2 / "planDeCompte.xml"

    if not pdc_path.is_file():
        raise NomenclatureInvalideErreur(
            nomenclature=nomenclature, pdcs_dpath=pdcs_dpath
        )

    logger.debug(f"Utilisation du plan de compte situé ici: '{pdc_path}'")
    return pdc_path


def _xpath_totem_budget_annee_exercice(totem_tree: ElementTree) -> Optional[str]:

    namespaces = _namespaces()

    year_elmt = totem_tree.find("/db:Budget/db:BlocBudget/db:Exer", namespaces)
    if year_elmt is None:
        return None
    year: Optional[str] = year_elmt.attrib.get("V")
    return year


def _xpath_totem_budget_id_etab(totem_tree: ElementTree) -> Optional[str]:

    namespaces = _namespaces()
    id_etab_elmt = totem_tree.find("/db:Budget/db:EnTeteBudget/db:IdEtab", namespaces)
    if id_etab_elmt is None:
        return None
    id_etab: Optional[str] = id_etab_elmt.attrib.get("V")
    return id_etab


def _xpath_totem_budget_etape(totem_tree: ElementTree) -> Optional[str]:
    namespaces = _namespaces()

    nat_dec_elmt = totem_tree.find("//db:Budget/db:BlocBudget/db:NatDec", namespaces)
    if nat_dec_elmt is None:
        return None

    code_etape = nat_dec_elmt.attrib.get("V")
    if code_etape is None:
        return None

    return code_etape


def _namespaces() -> dict[str, str]:
    namespaces = {"db": "http://www.minefi.gouv.fr/cp/demat/docbudgetaire"}
    return namespaces


def _as_xpath_str(s: str):
    #
    # Puisque les chaînes de caractère en XPath
    # n'ont pas de mécanisme d'échappement, on n'accepte tout simplement pas les quote
    #
    if "'" in s:
        raise CaractereAppostropheErreur(s)
    return f"'{s}'"


def _xml_to_csv(tree: ElementTree, text_io: TextIOBase, options: Options):

    if not text_io.writable():
        raise ConversionErreur(f"{str(text_io)} est en lecture seule.")

    writer = _make_writer(text_io, options)

    if options.inclure_header_csv:
        header_names = [elt.attrib["name"] for elt in tree.iterfind("/header/column")]
        writer.writerow(header_names)

    for row_tag in tree.iterfind("/data/row"):
        row_data = [cell.attrib["value"] for cell in row_tag.iter("cell")]
        writer.writerow(row_data)


def _make_writer(text_io, options: Options):
    if options.lineterminator is None:
        return csv.writer(text_io)
    else:
        return csv.writer(text_io, lineterminator=options.lineterminator)


def _write_in_tmp(tree: ElementTree, intermediaire_fpath: str):
    tmp = Path(intermediaire_fpath)
    tree.write(tmp, pretty_print=True)  # type: ignore[call-arg]
    logger.debug(f"Ecriture du totem transformé dans {tmp}")


def _parse_annee_exercice(annee: Optional[str]) -> int:

    try:
        if annee is None:
            raise Exception("L'annee ne peut pas etre None")
        if len(annee) != 4:
            raise Exception("L'annee doit etre une chaine de 4 digit.")
        return int(annee)
    except Exception as err:
        raise AnneeExerciceInvalideErreur(annee) from err


def _parse_siret(siret: Optional[str]) -> int:

    try:
        if siret is None:
            raise Exception("le siret ne peut pas etre None")

        if len(siret) != 14:
            raise Exception("Nombre de digit incorrect")

        siret_int = int(siret)

        return siret_int
    except Exception as err:
        raise SiretInvalideErreur(siret) from err


def _parse_code_etape(code_etape: Optional[str]) -> EtapeBudgetaire:

    try:
        if code_etape is None:
            raise Exception("le siret ne peut pas etre None")

        code_etape_i = int(code_etape)

        return EtapeBudgetaire(code_etape_i)
    except Exception as err:
        raise EtapeBudgetaireInconnueErreur(code_etape) from err
