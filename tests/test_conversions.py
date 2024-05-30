import hashlib
import json
from sys import stderr
import tempfile
from os.path import isdir
from pathlib import Path
from csv_diff import load_csv, compare

import pytest

from yatotem2scdl import ConvertisseurTotemBudget, Options

from data import PLANS_DE_COMPTE_PATH
from data import examples_directories


@pytest.mark.parametrize(
    "totem_path, expected_path",
    [(d / "totem.xml", d / "expected.csv") for d in examples_directories() if isdir(d)],
)
def test_generation(totem_path: Path, expected_path: Path):

    _, candidate_file_str = tempfile.mkstemp(".csv")
    candidate_filepath = Path(candidate_file_str)

    xslt_custom = totem_path.parent / "totem2xmlcsv-custom.xsl"
    convert_options_conf = totem_path.parent / "convert-options.json"

    if xslt_custom.exists():
        print("On utilise un totem2xmlcsv custom")
        convertisseur = ConvertisseurTotemBudget(xslt_budget=xslt_custom)
    else:
        convertisseur = ConvertisseurTotemBudget()

    options = Options()
    if convert_options_conf.exists():
        with convert_options_conf.open("r") as f:
            json_opts = json.load(f)
            print(f"On utilise les options de conversion suivantes: {json_opts}")
            options.__dict__.update(json_opts)

    with open(candidate_filepath, "wt", encoding="UTF-8") as output:
        convertisseur.totem_budget_vers_scdl(
            totem_fpath=totem_path,
            pdcs_dpath=PLANS_DE_COMPTE_PATH,
            output=output,
            options=options,
        )

    # tmp_dir = tempfile.mkdtemp("-test-generation")
    # shutil.copy(candidate_file_str, tmp_dir)
    # shutil.copy(expected_path, tmp_dir)

    candidate_csv = load_csv(open(candidate_filepath))
    expected_csv = load_csv(open(expected_path))
    diff = ["Ne peut pas calculer la différence"]
    try:
        diff = compare(candidate_csv, expected_csv)
    except Exception:
        stderr.write("Erreur lors de la comparaisons des csv\n")

    expected_hash = hashlib.md5(expected_path.read_bytes()).hexdigest()
    candidate_hash = hashlib.md5(candidate_filepath.read_bytes()).hexdigest()

    assert (
        expected_hash == candidate_hash
    ), f"Le contenu de la genration de scdl doit correspondre à {expected_path}\n Liste des differences: \n{diff}"


def test_scdl_entetes():
    convertisseur = ConvertisseurTotemBudget()
    entetes = convertisseur.budget_scdl_entetes()
    assert "BGT_NOM" in entetes
