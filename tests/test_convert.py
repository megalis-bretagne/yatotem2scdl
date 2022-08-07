import hashlib
import os
import shutil
import tempfile
from os import listdir
from os.path import isdir, join
from pathlib import Path
from csv_diff import load_csv, compare

import pytest
from yatotem2scdl.convert import totem_budget_vers_scdl as convert

_EXEMPLES_PATH = Path(os.path.dirname(__file__)) / "exemples"
_PLANS_DE_COMPTE_PATH = Path(os.path.dirname(__file__)) / "plans_de_comptes"


@pytest.mark.parametrize(
    "totem_path, expected_path",
    [
        (d / "totem.xml", d / "expected.csv")
        for d in [Path(_EXEMPLES_PATH, d) for d in listdir(_EXEMPLES_PATH)]
        if isdir(join(_EXEMPLES_PATH, d))
    ],
)
def test_generation(totem_path: Path, expected_path: Path):

    _, candidate_file_str = tempfile.mkstemp(".csv")
    candidate_filepath = Path(candidate_file_str)

    with open(candidate_filepath, "wt", encoding="UTF-8") as output:
        convert(totem_fpath=totem_path, pdcs_dpath=_PLANS_DE_COMPTE_PATH, output=output)

    # tmp_dir = tempfile.mkdtemp("-test-generation")
    # shutil.copy(candidate_file_str, tmp_dir)
    # shutil.copy(expected_path, tmp_dir)

    candidate_csv = load_csv(open(candidate_filepath))
    expected_csv = load_csv(open(expected_path))
    diff = compare(candidate_csv, expected_csv)

    expected_hash = hashlib.md5(expected_path.read_bytes()).hexdigest()
    candidate_hash = hashlib.md5(candidate_filepath.read_bytes()).hexdigest()

    assert (
        expected_hash == candidate_hash
    ), f"Le contenu de la genration de scdl doit correspondre à {expected_path}\n Liste des differences: \n{diff}"
