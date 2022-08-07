import hashlib
from io import StringIO
from tokenize import String
import pytest
import os
from os import listdir, scandir
from os.path import isdir, join
from pathlib import Path
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

    with StringIO() as output:
        convert(totem_fpath=totem, pdcs_dpath=_PLANS_DE_COMPTE_PATH, output=output)

        scdl_str = output.getvalue()
        expected_hash = hashlib.md5(expected.read_bytes()).hexdigest()
        candidate_hash = hashlib.md5(scdl_str.encode()).hexdigest()

        assert expected_hash == candidate_hash, f"Le contenu de la genration de scdl doit correspondre à {expected}"
