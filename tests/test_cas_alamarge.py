import tempfile
from yatotem2scdl.conversion import totem_budget_vers_scdl
from yatotem2scdl.exceptions import ConversionErreur, CaractereAppostropheErreur

import pytest

from data import A_LA_MARGE_PATH, PLANS_DE_COMPTE_PATH


def test_io_lecture_seule():

    with pytest.raises(ConversionErreur) as err:
        totem_filep = A_LA_MARGE_PATH / "totem.xml"
        _, csv_file_str = tempfile.mkstemp(".csv")

        with open(csv_file_str, "r") as output:
            totem_budget_vers_scdl(
                totem_fpath=totem_filep, pdcs_dpath=PLANS_DE_COMPTE_PATH, output=output
            )

    assert "lecture seule" in str(err)


def test_mauvais_fichier_totem():
    with pytest.raises(ConversionErreur):
        mauvais_totem_filep = A_LA_MARGE_PATH / "mauvais_totem.xml"
        _, csv_file_str = tempfile.mkstemp(".csv")

        with open(csv_file_str, "r+") as output:
            totem_budget_vers_scdl(
                totem_fpath=mauvais_totem_filep,
                pdcs_dpath=PLANS_DE_COMPTE_PATH,
                output=output,
            )


def test_pas_de_pdc():
    mauvais_totem_filep = A_LA_MARGE_PATH / "totem.xml"
    pdc_path = PLANS_DE_COMPTE_PATH / "wrong"
    _, csv_file_str = tempfile.mkstemp(".csv")

    with open(csv_file_str, "r+") as output:
        totem_budget_vers_scdl(
            totem_fpath=mauvais_totem_filep, pdcs_dpath=pdc_path, output=output
        )


def test_apostrophe_in_pdc():
    with pytest.raises(CaractereAppostropheErreur):
        mauvais_totem_filep = A_LA_MARGE_PATH / "totem.xml"
        pdc_path = PLANS_DE_COMPTE_PATH / ".." / "plans_de_comptes'avec_apostrophe"
        _, csv_file_str = tempfile.mkstemp(".csv")

        with open(csv_file_str, "r+") as output:
            totem_budget_vers_scdl(
                totem_fpath=mauvais_totem_filep, pdcs_dpath=pdc_path, output=output
            )
