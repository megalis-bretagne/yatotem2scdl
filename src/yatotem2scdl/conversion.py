from dataclasses import dataclass
from io import TextIOBase
import logging
from typing import Optional
from xdrlib import ConversionError
from xml.etree.ElementTree import ElementTree
from pathlib import Path

import os
import csv

from yatotem2scdl.exceptions import ConversionErreur, CaractereAppostropheErreur

from lxml import etree

_BUDGET_XSLT = Path(os.path.dirname(__file__)) / "xsl" / "totem2xmlcsv.xsl"
_PDC_VIDE = Path(os.path.dirname(__file__)) / "planDeCompte-vide.xml"


@dataclass()
class Options:
    """Options du processus de conversion"""

    lineterminator: Optional[str] = None
    inclure_header_csv: bool = True  # Inclure le nom des colonnes dans le CSV generé.
    xml_intermediaire_path: Optional[
        str
    ] = None  # Chemin du fichier pour écrire le XML intermédiaire


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

        if options is None:
            options = Options()

        logging.info(f"Conversion du fichier budget totem: {totem_fpath}")
        try:
            totem_tree: ElementTree = etree.parse(totem_fpath)
            pdc_path = _extraire_plan_de_compte(
                totem_tree=totem_tree, pdcs_dpath=pdcs_dpath
            )
            transformed_tree = self._transform(
                totem_tree=totem_tree, pdc_fpath=pdc_path, options=options
            )
            _xml_to_csv(transformed_tree, output, options)
            logging.info("OK")
        except ConversionErreur as err:
            raise err
        except Exception as err:
            raise ConversionErreur() from err

    def budget_scdl_entetes(self) -> str:
        """Récupère la ligne d'entete du SCDL correspondant aux budgets"""

        xslt_tree: ElementTree = etree.parse(self.__xslt_budget)
        entetes = xslt_tree.xpath(  # type:ignore
            "/xsl:stylesheet/xsl:template/csv/header/column/@name",
            namespaces={"xsl": "http://www.w3.org/1999/XSL/Transform"},
        )
        return ",".join(entetes)

    def _transform(
        self, totem_tree: ElementTree, pdc_fpath: Path, options: Options
    ) -> ElementTree:

        logging.debug(
            (
                f"\nTransformation du fichier totem"
                f"\n\tFichier XSL: {self.__xslt_budget}"
            )
        )

        xslt_tree = etree.parse(self.__xslt_budget.resolve())
        transform = etree.XSLT(xslt_input=xslt_tree)

        pdc_exists = os.path.exists(pdc_fpath)

        pdc_param = _as_xpath_str(
            str(pdc_fpath.resolve()) if pdc_exists else str(_PDC_VIDE.resolve())
        )

        if not pdc_exists:
            logging.warning(
                f"Impossible de trouver un plan de compte pour le fichier totem."
                f" Le SCDL sera probablement incomplet"
            )

        transformed_tree = transform(totem_tree, plandecompte=pdc_param)

        intermediaire_fpath = options.xml_intermediaire_path
        if intermediaire_fpath is not None:
            _write_in_tmp(transformed_tree, intermediaire_fpath)

        return transformed_tree


def _extraire_plan_de_compte(totem_tree: ElementTree, pdcs_dpath: Path) -> Path:

    namespaces = {"db": "http://www.minefi.gouv.fr/cp/demat/docbudgetaire"}

    nomenclature: Optional[str] = totem_tree.findall(
        "/db:Budget/db:EnTeteBudget/db:Nomenclature", namespaces
    )[0].attrib.get("V")
    year: Optional[str] = totem_tree.findall(
        "/db:Budget/db:BlocBudget/db:Exer", namespaces
    )[0].attrib.get("V")

    if nomenclature is None or year is None:
        raise ConversionError(
            "On s'attend à ce que le fichier totem contienne la nomenclature et l'année"
        )

    logging.info(f"Version de plan de compte trouvée: ({year}, {nomenclature})")

    (n1, n2) = nomenclature.split("-", 1)
    pdc_path = pdcs_dpath / year / n1 / n2 / "planDeCompte.xml"
    logging.debug(f"Utilisation du plan de compte situé ici: '{pdc_path}'")
    return pdc_path


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
    logging.debug(f"Ecriture du totem transformé dans {tmp}")
