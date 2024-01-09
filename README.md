# Yet Another totem to scdl

## Rationale

Largement inspiré de [datafin - totem](https://gitlab.com/datafin/totem).

Le but de ce projet est de proposer une bibliothèque python de conversion de fichiers totem vers le format SCDL.
En effet, le projet de base cité plus haut n'est pas conçu pour être utilisé comme une bibliothèque.

## Limitations

- Actuellement, seuls les budgets sont supportés.
- Les plans de comptes ne sont pas fournis avec le package. 
  - [norme-budgetaire-downloader](https://gitlab.com/opendatafrance/totem/-/tree/main/norme-budgetaire-downloader?ref_type=heads)

## Quickstart

### Préparer l'environnement

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### Construire le package

```bash
python -m build
```

### Tests

```bash
pytest
```

#### Ajouter des tests boite noire

Le fichier [test_conversions.py](./tests/test_conversions.py) contient des tests boite noire, les jeux de données étant quant à eux situés dans [exemples](./tests/exemples/).
Il est possible d'ajouter des cas de test via la variable d'environnement `YATOTEM2SCDL_EXEMPLES_ADDITIONNELS`, qui pointe vers un dossier suivant la même nomenclature que [exemples](./tests/exemples/).

```fish
set -lx YATOTEM2SCDL_EXEMPLES_ADDITIONNELS <DOSSIER_AVEC_JEUX_DE_TESTS_ADDITIONNELS>
pytest
```

### CLI

Après installation du package, la commande `yatotem2scdl` devient disponible:

```bash
$ yatotem2scdl --help
```

### Upload

Pour upload sur un repository PyPI:

```bash
python -m build
twine upload --repository-url https://<REPO_URL>/repository/pypi-hosted/ dist/*
```

## Générer les plans de comptes

**Testé avec nodejs v16.20.2 et python 3.11.5**

- Cloner le repository [norme-budgetaire-downloader](https://gitlab.com/opendatafrance/totem/-/tree/main/norme-budgetaire-downloader?ref_type=heads)

- executer:
```
npm ci
npm run build
npm run run # Télécharge les plans de compte dans le dossier output
```

- Copier coller les plans de compte dans le dossier correspondant.