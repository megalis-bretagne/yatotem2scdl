"""Tests concernant l'enum EtatBudgetaire"""

import pytest
from yatotem2scdl.conversion import EtapeBudgetaire
from yatotem2scdl.exceptions import EtapeBudgetaireInconnueErreur

def test_construction():
    etape = EtapeBudgetaire.from_str("compte administratif")
    assert etape is EtapeBudgetaire.COMPTE_ADMIN

def test_construction_mauvaise_chaine():
    with pytest.raises(EtapeBudgetaireInconnueErreur):
        EtapeBudgetaire.from_str("chaine sans correspondance")

def test_etape_produit_scdl_str():
    assert EtapeBudgetaire.PRIMITIF.to_scdl_compatible_str() \
        == str(EtapeBudgetaire.PRIMITIF) \
        == "budget primitif"