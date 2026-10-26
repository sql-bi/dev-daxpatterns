# Tests for DaxPatterns.CumulativeTotal

Each test compares a call of a library function with a reference measure.
The reference measures are the original DAX of the [Cumulative total](https://www.daxpatterns.com/cumulative-total/) pattern.
A test passes when there are 0 differences and the checksum is the same as the expected checksum.

## Folders

| Folder | Content |
|---|---|
| `cases/` | One DAX query for each group of tests. Each query returns one row for each test: `Test`, `Rows`, `Mismatches`, `Checksum`. |
| `common/` | Reference measures (original DAX) and query-scoped columns for the customer class. |
| `expected/` | Expected `Rows` and `Checksum` for each test model. |
| `run_tests.py` | Test runner (Python 3, no extra packages). |
| `timings.md` | Server timings of CLASSIC and WINDOW (Contoso 10k and 100k). |

## Test models

| Model | Profile | Expected results |
|---|---|---|
| dax.do Contoso (public, https://dax.do) | `daxdo` | `expected/daxdo-contoso.json` |
| Contoso 10k (Contoso Data Generator) | `contoso` | `expected/contoso-10k.json` |
| Contoso 100k (Contoso Data Generator) | `contoso` | `expected/contoso-100k.json` |

The runner replaces the placeholders `@@...@@` in the queries with the names of the profile (for example, `Year Month` or `Calendar Year Month`).

## Run the tests

The runner adds the functions of `src/CumulativeTotal/lib/functions.tmdl` to the query (`DEFINE FUNCTION`).
It is not necessary to install the package in the model.

dax.do (no authentication):

```bash
python3 tests/CumulativeTotal/run_tests.py daxdo --expected tests/CumulativeTotal/expected/daxdo-contoso.json
```

Power BI semantic model (REST API executeQueries, service principal):

```bash
export PBI_TENANT_ID=<tenant id> PBI_CLIENT_ID=<app id> PBI_CLIENT_SECRET=<secret>
python3 tests/CumulativeTotal/run_tests.py pbi <workspace id> <dataset id> --profile contoso --expected tests/CumulativeTotal/expected/contoso-10k.json
```

DAX query view, DAX Studio, or Tabular Editor: print the full query, then paste it:

```bash
python3 tests/CumulativeTotal/run_tests.py print 01-over-dates --profile contoso
```

Use `--write-expected <file>` to save new expected results. Do this only after a review of the differences.

## Test list

| Test | Function | Scenario | Reference |
|---|---|---|---|
| T01a, T01b | OverDates | By month, CLASSIC and WINDOW | V1 Sales Amount RT |
| T01c | OverDates | By month | V1b (date table not marked) |
| T01d, T01e | OverDates | By day, CLASSIC and WINDOW | V1 |
| T01f, T01g | OverDates | Year slicer, start at the first date of the table | V1 |
| T01h | OverDates | Expression `SUM ( Sales[Quantity] )` instead of a measure | V1 with SUM |
| T02a, T02b | OverDates | keepFiltersTable = Day of Week, CLASSIC and WINDOW | V2 RT Weekdays |
| T02c | OverDates | Day of Week filter without keepFiltersTable | V1 |
| T03a, T03b | OverDates | startAtSelection = TRUE with a year slicer, CLASSIC and WINDOW | V1 + start at first selected date |
| T03c | OverDates | startAtSelection = TRUE without a selection | V1 |
| T04a, T04b | OverSortedColumn | By customer class, CLASSIC and WINDOW | V3 Sales Amount RT Class |
| T04c, T04d | OverSortedColumn | Selection of classes 2-4 and a Gender filter | V3 |
| T04e, T04f | OverSortedColumn | startAtSelection = FALSE (ALL) | V3 with ALL |
| T05a, T05b | OverSortedColumn | Year Month with Sort by Column, year slicer | V3 on Year Month |
| T06a, T06b, T06c | both | Direct call in ADDCOLUMNS (context transition) | Same call in a measure |
| 07 | OverDates | Invalid implementation value | Error expected |

The customer class is not in the Contoso models. `common/customer-class.dax` creates it with query-scoped columns.
