import argparse
import os
from pathlib import Path
import sys

from yatotem2scdl.conversion import ConvertisseurTotemBudget


def process(args):

    totem_filep = Path(args.totem_file)
    pdcs_dpath = Path(args.plans_de_comptes)

    convertisseur = ConvertisseurTotemBudget()
    convertisseur.totem_budget_vers_scdl(
        totem_fpath=totem_filep, pdcs_dpath=pdcs_dpath, output=sys.stdout
    )


def main():

    pdc_argname = "--plans-de-comptes"
    pdc_envname = "PLANS_DE_COMPTES_DIR"

    parser = argparse.ArgumentParser(description="Convertit un fichier totem en SCDL")
    parser.add_argument("nature_acte", type=str, help="Nature de l'acte (seul la valeur budget est supporté pour le moment)")
    parser.add_argument("totem_file", type=str, help="Chemin du fichier totem")
    parser.add_argument(
        pdc_argname,
        default=os.environ.get(pdc_envname),
        type=str,
        dest="plans_de_comptes",
        help="Dossier contenant les plans de comptes",
        required=False,
    )
    args = parser.parse_args()

    status = 0

    if args.nature_acte != "budget":
        sys.stderr.write("Seul les budgets sont supportés.")
        sys.exit(-1)
    
    if args.plans_de_comptes is None:
        sys.stderr.write("Vous devez spécifier oú se trouvent les plans de comptes ")
        sys.stderr.write(
            f"via l'argument {pdc_argname} ou la variable d'environnement {pdc_envname}"
        )
        sys.stderr.write("\n")
        sys.exit(-1)

    try:
        process(args)
    except Exception as e:
        sys.stderr.write(str(e))
        status = -1

    sys.exit(status)
