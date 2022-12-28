import pytest
import dataclasses

from yatotem2scdl.data_structures import TotemBudgetMetadata, EtapeBudgetaire

@pytest.fixture
def metadata2():
    return TotemBudgetMetadata(
        2021,
        21220282400018,
        EtapeBudgetaire.PRIMITIF,
        scellement=None,
        plan_de_compte=None
    )

@pytest.fixture
def metadata1():
    return TotemBudgetMetadata(
        2022,
        21220282400018,
        EtapeBudgetaire.COMPTE_ADMIN,
        scellement=None,
        plan_de_compte=None
    )

@pytest.fixture
def metadata1bis(metadata1):
    return dataclasses.replace(metadata1)

def test_TotemBudgetMetadata_hashable(metadata1: TotemBudgetMetadata, metadata1bis: TotemBudgetMetadata):
    hash(metadata1)
    assert hash(metadata1) == hash(metadata1bis)
    assert hash(metadata1) != hash(metadata2)

def test_TotemBudgetMetadata_immutable(metadata1: TotemBudgetMetadata):
    with pytest.raises(Exception):
        metadata1.annee_exercice = 1999

def test_TotemBudgetMetadata_equality(metadata1: TotemBudgetMetadata, metadata1bis: TotemBudgetMetadata, metadata2: TotemBudgetMetadata):
    assert id(metadata1) != id(metadata1bis), "metadata1 et metadata1bis ne doivent pas être les mêmes objets"
    assert metadata1 == metadata1bis, "metadata1 et metadata1bis devraient être egaux"
    assert metadata1 != metadata2, "metadata1 et metadata2 ne devraient pas être égaux"

