# Yet Another totem to scdl

## Rationale

Largement inspiré de [datafin - totem](https://gitlab.com/datafin/totem).

Le but de ce projet est de proposer une bibliothèque python de conversion de fichiers totem vers le format SCDL.
En effet, le projet de base cité plus haut n'est pas conçu pour être utilisé comme une bibliothèque.

## Limitations

- Actuellement, seuls les budgets sont supportés.
- Les plans de comptes ne sont pas fournis avec le package. 
  - [norme-budgetaire-downloader](https://gitlab.com/datafin/totem/-/tree/master/norme-budgetaire-downloader)

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

