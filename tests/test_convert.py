import hashlib
import pytest
import os
from os import listdir
from os.path import isdir, join
from pathlib import Path
from yatotem2scdl.convert import totemxml2scdl as convert

_EXEMPLES_PATH = Path(os.path.dirname(__file__), "exemples")

@pytest.mark.parametrize(
    "totem, expected",
    [
        (d / "totem.xml", d / "expected.csv")
        for d in [Path(_EXEMPLES_PATH, d) for d in listdir(_EXEMPLES_PATH)]
        if isdir(join(_EXEMPLES_PATH, d))
    ],
)
def test_generation(totem: Path, expected: Path):

    scdl: str = convert(totem_fpath=totem)

    expected_hash = hashlib.md5(expected.read_bytes()).hexdigest()
    candidate_hash = hashlib.md5(scdl.encode()).hexdigest()

    assert expected_hash == candidate_hash, f"Le contenu de la genration de scdl doit correspondre à {expected}"
