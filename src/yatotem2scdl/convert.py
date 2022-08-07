from dataclasses import dataclass
from io import StringIO, TextIOBase
import logging
from typing import Optional
from xdrlib import ConversionError
from xml.etree.ElementTree import ElementTree
import os
from pathlib import Path

from yatotem2scdl.exceptions import ConversionErreur, CaractereAppostropheErreur

from lxml import etree

BUDGET_XSLT = Path(os.path.dirname(__file__)) / "xsl" / "totem2xmlcsv.xsl"


@dataclass()
class Options:
    """Options du processus de conversion"""

    inclure_header_csv: bool = True  # Inclure le nom des colonnes dans le CSV generé.
    xml_intermediaire_path: Optional[
        str
    ] = None  # Chemin du fichier pour écrire le XML intermédiaire


def totem_budget_vers_scdl(
    totem_fpath: Path,
    pdcs_dpath: Path,
    output: TextIOBase,
    options: Options = Options(),
):

    logging.debug(f"Convertion du fichier totem {totem_fpath}")
    try:
        totem_tree: ElementTree = etree.parse(totem_fpath)
        pdc_path = _extraire_plan_de_compte(
            totem_tree=totem_tree, pdcs_dpath=pdcs_dpath
        )
        transformed_tree = _transform(
            totem_tree=totem_tree, pdc_fpath=pdc_path, options=options
        )
        _xml_to_csv(transformed_tree, output, options)
    except OSError as err:
        raise ConversionErreur from err


def _extraire_plan_de_compte(totem_tree: ElementTree, pdcs_dpath: Path) -> Path:

    namespaces = {
        "db": "http://www.minefi.gouv.fr/cp/demat/docbudgetaire"
    }  # add more as needed

    nomenclature: Optional[str] = totem_tree.findall(
        "/db:Budget/db:EnTeteBudget/db:Nomenclature", namespaces
    )[0].attrib.get("V")
    year: Optional[str] = totem_tree.findall(
        "/db:Budget/db:BlocBudget/db:Exer", namespaces
    )[0].attrib.get("V")

    if nomenclature is None or year is None:
        raise ConversionError(
            f"On s'attend à ce que le fichier totem contienne la nomenclature et l'année"
        )

    logging.info(f"Version de plan de compte trouvée: ({year}, {nomenclature})")

    (n1, n2) = nomenclature.split("-", 1)
    pdc_path = pdcs_dpath / year / n1 / n2 / "planDeCompte.xml"
    logging.debug(f"Utilisation du plan de compte situé ici: '{pdc_path}'")
    return pdc_path


def _transform(
    totem_tree: ElementTree, pdc_fpath: Path, options: Options
) -> ElementTree:
    # xmlstarlet tr xsl -s plandecompte=pdc totem | xmlstarlet fo - > temp

    logging.debug(
        (f"\nTransformation du fichier totem" f"\n\tFichier XSL: {BUDGET_XSLT}")
    )

    xslt_tree = etree.parse(BUDGET_XSLT.resolve())
    transform = etree.XSLT(xslt_input=xslt_tree)
    pdc_param = _as_xpath_str(str(pdc_fpath.resolve()))

    transformed_tree = transform(totem_tree, plandecompte=pdc_param)

    intermediaire_fpath = options.xml_intermediaire_path
    if intermediaire_fpath is not None:
        _write_in_tmp(transformed_tree, intermediaire_fpath)

    return transformed_tree


def _as_xpath_str(s: str):
    #
    # Puisque les chaînes de caractère en XPath
    # n'ont pas de mécanisme d'échappement, on n'accepte tout simplement pas les quote
    #
    if "'" in s:
        raise CaractereAppostropheErreur(s)
    return f"'{s}'"


def _xml_to_csv(tree: ElementTree, text_io: TextIOBase, options: Options):

    if options.inclure_header_csv:
        header_names = [elt.attrib["name"] for elt in tree.iterfind("/header/column")]
        text_io.write(",".join(header_names))

    for row_tag in tree.iterfind("/data/row"):
        row_data = [cell.attrib["value"] for cell in row_tag.iter("cell")]
        text_io.write("\n")
        text_io.write(",".join(row_data))


def _write_in_tmp(tree: ElementTree, intermediaire_fpath: str):
    tmp = Path(intermediaire_fpath)
    tree.write(tmp, pretty_print=True)
    logging.debug(f"Ecriture du totem transformé dans {tmp}")


if __name__ == "__main__":
    import os
    import logging

    logging.basicConfig(level=logging.DEBUG)

    testp = Path(os.path.dirname(__file__)) / "../.." / "tests"
    totemf = testp / "exemples" / "budget-crach-001" / "totem.xml"
    pdcsp = testp / "plans_de_comptes"
    # pdcsp = testp / "autres'pdcs"

    with StringIO() as output:
        scdl = totem_budget_vers_scdl(
            totem_fpath=totemf,
            pdcs_dpath=pdcsp,
            output=output,
            options=Options(xml_intermediaire_path="/tmp/temp_totem.xml"),
        )
        print(output.getvalue())
