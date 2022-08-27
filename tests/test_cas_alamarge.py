import tempfile
from yatotem2scdl import (
    ConvertisseurTotemBudget,
    ConversionErreur,
    CaractereAppostropheErreur,
)

import pytest

from data import A_LA_MARGE_PATH, PLANS_DE_COMPTE_PATH


@pytest.fixture()
def _convertisseur():
    return ConvertisseurTotemBudget()


def test_io_lecture_seule(_convertisseur):

    with pytest.raises(ConversionErreur) as err:
        totem_filep = A_LA_MARGE_PATH / "totem.xml"
        _, csv_file_str = tempfile.mkstemp(".csv")

        with open(csv_file_str, "r") as output:
            _convertisseur.totem_budget_vers_scdl(
                totem_fpath=totem_filep, pdcs_dpath=PLANS_DE_COMPTE_PATH, output=output
            )

    assert "lecture seule" in str(err)


def test_mauvais_fichier_totem(_convertisseur):
    with pytest.raises(ConversionErreur):
        mauvais_totem_filep = A_LA_MARGE_PATH / "mauvais_totem.xml"
        _, csv_file_str = tempfile.mkstemp(".csv")

        with open(csv_file_str, "r+") as output:
            _convertisseur.totem_budget_vers_scdl(
                totem_fpath=mauvais_totem_filep,
                pdcs_dpath=PLANS_DE_COMPTE_PATH,
                output=output,
            )


def test_pas_de_pdc(_convertisseur):
    mauvais_totem_filep = A_LA_MARGE_PATH / "totem.xml"
    pdc_path = PLANS_DE_COMPTE_PATH / "wrong"
    _, csv_file_str = tempfile.mkstemp(".csv")

    with open(csv_file_str, "r+") as output:
        _convertisseur.totem_budget_vers_scdl(
            totem_fpath=mauvais_totem_filep, pdcs_dpath=pdc_path, output=output
        )


def test_apostrophe_in_pdc(_convertisseur):
    with pytest.raises(CaractereAppostropheErreur):
        mauvais_totem_filep = A_LA_MARGE_PATH / "totem.xml"
        pdc_path = PLANS_DE_COMPTE_PATH / ".." / "plans_de_comptes'avec_apostrophe"
        _, csv_file_str = tempfile.mkstemp(".csv")

        with open(csv_file_str, "r+") as output:
            _convertisseur.totem_budget_vers_scdl(
                totem_fpath=mauvais_totem_filep, pdcs_dpath=pdc_path, output=output
            )
