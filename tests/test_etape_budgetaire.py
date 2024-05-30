"""Tests concernant l'enum EtatBudgetaire"""

import pytest
from yatotem2scdl import EtapeBudgetaire, EtapeBudgetaireStrInvalideError


def test_construction():
    etape = EtapeBudgetaire.from_str("compte administratif")
    assert etape is EtapeBudgetaire.COMPTE_ADMIN


def test_construction_mauvaise_chaine():
    with pytest.raises(EtapeBudgetaireStrInvalideError):
        EtapeBudgetaire.from_str("chaine sans correspondance")

def test_etape_produit_scdl_str_works():
    for member in EtapeBudgetaire:
        member.to_scdl_compatible_str()

def test_etape_produit_scdl_cfu():
    scdl_cfu_str = EtapeBudgetaire.CFU.to_scdl_compatible_str()
    scdl_ca_str = EtapeBudgetaire.COMPTE_ADMIN.to_scdl_compatible_str()
    assert scdl_cfu_str == scdl_ca_str, "Le SCDL n'a pas de notion de CFU jusqu'à présent, on assimile un CFU à un CA"
    