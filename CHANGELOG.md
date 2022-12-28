# Changelog

Changelog basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.21]

### Added

- `TotemBudgetMetadata` detient maintenant la date de scellement

## [0.0.20]

### Changed

- `TotemBudgetMetadata` est maintenant immutable

## [0.0.19] - 2022-12-18

### Changed

- `totem_budget_metadata` sax parser, meilleures perfs

## [0.0.18] - 2022-11-30

### Changed

- la méthode `EtapeBudgetaire.from_str` renvoit une exception `EtapeBudgetaireStrInvalideError` au lieu d'une exception spécifique au parsing de fichier totem.

## [0.0.17] - 2022-11-24

### Added

- Ajout d'un logger au sein du module `yatotem2scdl`

## [0.0.23] - 2022-11-23

*Release cassée, ne pas l'utiliser*