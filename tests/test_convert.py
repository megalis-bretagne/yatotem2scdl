import hashlib
import os
import tempfile
from os import listdir
from os.path import isdir, join
from pathlib import Path

import pytest
from yatotem2scdl.convert import Options
from yatotem2scdl.convert import totem_budget_vers_scdl as convert

_EXEMPLES_PATH = Path(os.path.dirname(__file__)) / "exemples"
_PLANS_DE_COMPTE_PATH = Path(os.path.dirname(__file__)) / "plans_de_comptes"

@pytest.mark.parametrize(
    "totem, expected",
    [
        (d / "totem.xml", d / "expected.csv")
        for d in [Path(_EXEMPLES_PATH, d) for d in listdir(_EXEMPLES_PATH)]
        if isdir(join(_EXEMPLES_PATH, d))
    ],
)
def test_generation(totem: Path, expected: Path):

    _, temp_file_str = tempfile.mkstemp(".csv")
    with open(temp_file_str, 'r+') as output:
        convert(totem_fpath=totem, pdcs_dpath=_PLANS_DE_COMPTE_PATH, output=output)

        expected_hash = hashlib.md5(expected.read_bytes()).hexdigest()
        candidate_hash = hashlib.md5(Path(temp_file_str).read_bytes()).hexdigest()

        assert expected_hash == candidate_hash, f"Le contenu de la genration de scdl doit correspondre à {expected}"

