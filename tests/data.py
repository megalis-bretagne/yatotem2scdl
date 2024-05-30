import os


from pathlib import Path
from typing import Optional

EXTRACT_METADATA_PATH = Path(os.path.dirname(__file__)) / "data_extract_metadata"
A_LA_MARGE_PATH = Path(os.path.dirname(__file__)) / "data_alamarge"
PLANS_DE_COMPTE_PATH = Path(os.path.dirname(__file__)) / "plans_de_comptes"

EXEMPLES_PATH: Path = Path(os.path.dirname(__file__)) / "exemples"


def additionnal_exemples_path() -> Optional[Path]:
    env_dir = os.environ.get("YATOTEM2SCDL_EXEMPLES_ADDITIONNELS")
    return Path(env_dir) if env_dir is not None else None


def examples_directories() -> list[Path]:
    dir_additionnel = additionnal_exemples_path()
    use_case_dirs_1 = [Path(EXEMPLES_PATH) / d for d in os.listdir(EXEMPLES_PATH)]
    use_case_dirs_2 = (
        [Path(dir_additionnel) / d for d in os.listdir(dir_additionnel)]
        if dir_additionnel is not None
        else []
    )
    return use_case_dirs_1 + use_case_dirs_2
