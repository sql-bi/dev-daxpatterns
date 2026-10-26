# Dax Patterns

This is the repository for the libraries of all [DAX Patterns](https://www.daxpatterns.com/). Each pattern has a corresponding library, which is one folder of this repository.

## Libraries

| Pattern | Library | Source | Tests | LLM skill |
|---|---|---|---|---|
| [ABC classification](https://www.daxpatterns.com/abc-classification/) | DaxPatterns.AbcClassification | [src/AbcClassification](src/AbcClassification) | – | – |
| [Cumulative total](https://www.daxpatterns.com/cumulative-total/) | DaxPatterns.CumulativeTotal | [src/CumulativeTotal](src/CumulativeTotal) | [tests/CumulativeTotal](tests/CumulativeTotal) | [skills/CumulativeTotal](skills/CumulativeTotal/SKILL.md) |

## Repository layout

- `src/<Pattern>/`: the DAX Lib package (`manifest.daxlib`, `lib/functions.tmdl`, `README.md`, `icon.png`). The workflow `publish-<pattern>.yml` publishes this folder.
- `tests/<Pattern>/`: test queries, expected results, and a test runner.
- `skills/<Pattern>/`: an LLM skill that applies the library to a specific semantic model.
