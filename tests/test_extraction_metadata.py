from genericpath import isdir
from pathlib import Path
import pytest
import time

from yatotem2scdl import (
    ConvertisseurTotemBudget,
    AnneeExerciceInvalideErreur,
    EtapeBudgetaireInconnueErreur,
    ExtractionMetadataErreur,
    SiretInvalideErreur,
    TotemInvalideErreur,
    EtapeBudgetaire,
)

from data import PLANS_DE_COMPTE_PATH, EXTRACT_METADATA_PATH
from data import examples_directories


@pytest.fixture
def _convertisseur() -> ConvertisseurTotemBudget:
    return ConvertisseurTotemBudget()

@pytest.mark.parametrize(
    "totem_path",
    [(d / "totem.xml") for d in examples_directories() if isdir(d)],
)
def test_parse_metadata_smoke(
    _convertisseur: ConvertisseurTotemBudget, totem_path: Path
):

    metadata = _convertisseur.totem_budget_metadata(
        totem_path, pdcs_dpath=PLANS_DE_COMPTE_PATH
    )
    assert metadata is not None

    assert metadata.etape_budgetaire is not None
    assert metadata.annee_exercice is not None
    assert metadata.id_etablissement is not None

    # Le plan de compte peut etre None

def test_parse_metadata_of_ca(_convertisseur: ConvertisseurTotemBudget):
    totem_filep = EXTRACT_METADATA_PATH / "totem_ca_valide.xml"

    metadata = _convertisseur.totem_budget_metadata(
        totem_filep, pdcs_dpath=PLANS_DE_COMPTE_PATH
    )
    
    assert metadata.annee_exercice == 2021
    assert metadata.etape_budgetaire == EtapeBudgetaire.COMPTE_ADMIN
    assert str(metadata.id_etablissement) == "22560001400016"
    assert "M57/M57/" in str(metadata.plan_de_compte)

def test_parse_metadata_of_cfu(_convertisseur: ConvertisseurTotemBudget):
    totem_filep = EXTRACT_METADATA_PATH / "totem_cfu_valide.xml"

    metadata = _convertisseur.totem_budget_metadata(
        totem_filep, pdcs_dpath=PLANS_DE_COMPTE_PATH
    )
    
    assert metadata.annee_exercice == 2023
    assert metadata.etape_budgetaire == EtapeBudgetaire.CFU
    assert str(metadata.id_etablissement) == "21560134500014"
    assert "M57/M57_A" in str(metadata.plan_de_compte)

def test_parse_metadata_performance(_convertisseur: ConvertisseurTotemBudget):
    """
    C'est un smoke test pour vérifier que la lecture des metadata reste relativement performante.
    """
    totem_filep = EXTRACT_METADATA_PATH / "totem_valid_huge.xml"

    start = time.perf_counter_ns()
    _convertisseur.totem_budget_metadata(
        totem_filep, pdcs_dpath=PLANS_DE_COMPTE_PATH
    )
    end = time.perf_counter_ns()
    elapsed_ns = end - start
    
    milli = 1_000_000
    assert elapsed_ns < (80*milli), "Parser les metadata doit être une opération relativement performante."

def test_parse_metadata_mauvais_siret(_convertisseur: ConvertisseurTotemBudget):

    totem_filep = EXTRACT_METADATA_PATH / "totem_mauvais_siret.xml"

    with pytest.raises(ExtractionMetadataErreur) as err:
        _convertisseur.totem_budget_metadata(totem_filep, PLANS_DE_COMPTE_PATH)

    assert (
        type(err.value.__cause__) is SiretInvalideErreur
        and isinstance(err.value.__cause__, TotemInvalideErreur) is True
    )


def test_parse_metadata_mauvaise_annee(_convertisseur: ConvertisseurTotemBudget):
    totem_filep = EXTRACT_METADATA_PATH / "totem_mauvaise_annee.xml"

    with pytest.raises(ExtractionMetadataErreur) as err:
        _convertisseur.totem_budget_metadata(totem_filep, PLANS_DE_COMPTE_PATH)

    assert (
        type(err.value.__cause__) is AnneeExerciceInvalideErreur
        and isinstance(err.value.__cause__, TotemInvalideErreur) is True
    )


def test_parse_metadata_mauvaise_nomenclature(_convertisseur: ConvertisseurTotemBudget):
    totem_filep = EXTRACT_METADATA_PATH / "totem_mauvaise_nomenclature.xml"

    metadata = _convertisseur.totem_budget_metadata(totem_filep, PLANS_DE_COMPTE_PATH)
    assert metadata.plan_de_compte is None


def test_parse_metadata_mauvaise_etape(_convertisseur: ConvertisseurTotemBudget):
    totem_filep = EXTRACT_METADATA_PATH / "totem_mauvaise_etape.xml"

    with pytest.raises(ExtractionMetadataErreur) as err:
        _convertisseur.totem_budget_metadata(totem_filep, PLANS_DE_COMPTE_PATH)

    assert (
        type(err.value.__cause__) is EtapeBudgetaireInconnueErreur
        and isinstance(err.value.__cause__, TotemInvalideErreur) is True
    )
