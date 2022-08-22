
from genericpath import isdir
from pathlib import Path
import pytest

import pytest
from yatotem2scdl.conversion import ConvertisseurTotemBudget
from yatotem2scdl.exceptions import AnneeExerciceInvalideErreur, EtapeBudgetaireInconnueErreur, ExtractionMetadataErreur,SiretInvalideErreur, TotemInvalideErreur

from data import PLANS_DE_COMPTE_PATH, EXTRACT_METADATA_PATH
from data import test_case_dirs

@pytest.fixture
def _convertisseur() -> ConvertisseurTotemBudget:
    return ConvertisseurTotemBudget()

@pytest.mark.parametrize(
    "totem_path",
    [(d / "totem.xml") for d in test_case_dirs() if isdir(d)],
)
def test_parse_metadata_smoke(_convertisseur: ConvertisseurTotemBudget, totem_path: Path):
    
    metadata = _convertisseur.totem_budget_metadata(totem_path,  pdcs_dpath=PLANS_DE_COMPTE_PATH)
    assert metadata is not None

    assert metadata.etape_budgetaire is not None
    assert metadata.annee_exercice is not None
    assert metadata.id_etablissement is not None

    # Le plan de compte peut etre None

def test_parse_metadata_mauvais_siret(_convertisseur: ConvertisseurTotemBudget):

    totem_filep = EXTRACT_METADATA_PATH / "totem_mauvais_siret.xml"

    with pytest.raises(ExtractionMetadataErreur) as err:
        _convertisseur.totem_budget_metadata(totem_filep, PLANS_DE_COMPTE_PATH)
    
    assert type(err.value.__cause__) is SiretInvalideErreur \
        and isinstance(err.value.__cause__, TotemInvalideErreur) is True

def test_parse_metadata_mauvaise_annee(_convertisseur: ConvertisseurTotemBudget):
    totem_filep = EXTRACT_METADATA_PATH / "totem_mauvaise_annee.xml"

    with pytest.raises(ExtractionMetadataErreur) as err:
        _convertisseur.totem_budget_metadata(totem_filep, PLANS_DE_COMPTE_PATH)
    
    assert type(err.value.__cause__) is AnneeExerciceInvalideErreur \
        and isinstance(err.value.__cause__, TotemInvalideErreur) is True

def test_parse_metadata_mauvaise_nomenclature(_convertisseur: ConvertisseurTotemBudget):
    totem_filep = EXTRACT_METADATA_PATH / "totem_mauvaise_nomenclature.xml"

    metadata = _convertisseur.totem_budget_metadata(totem_filep, PLANS_DE_COMPTE_PATH)
    assert metadata.plan_de_compte is None

def test_parse_metadata_mauvaise_etape(_convertisseur: ConvertisseurTotemBudget):
    totem_filep = EXTRACT_METADATA_PATH / "totem_mauvaise_etape.xml"

    with pytest.raises(ExtractionMetadataErreur) as err:
        _convertisseur.totem_budget_metadata(totem_filep, PLANS_DE_COMPTE_PATH)

    assert type(err.value.__cause__) is EtapeBudgetaireInconnueErreur \
        and isinstance(err.value.__cause__, TotemInvalideErreur) is True