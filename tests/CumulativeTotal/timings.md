# Server timings – DaxPatterns.CumulativeTotal 0.1.0-beta

Measured on 2026-10-26 on Contoso 10k and Contoso 100k (Power BI Premium capacity, XMLA endpoint, session trace).
Values in ms: QueryEnd duration. Warm: median of 3 runs. Cold: 1 run after ClearCache. FE/SE: formula engine / storage engine (warm).
"reference" is the original DAX of the pattern (or a hand-written variation for the new options).
The class scenarios (P6, P7) include about 900 ms to compute the query-scoped Customer Class columns.

| Scenario | Variant | 10k warm | 100k warm | 100k cold | 100k FE / SE (warm) |
|---|---|---:|---:|---:|---:|
| P1 by month | original V1 | 62 | 219 | 235 | 219 / 0 |
| P1 by month | CLASSIC | 62 | 250 | 219 | 250 / 0 |
| P1 by month | WINDOW | 235 | 1298 | 1111 | 1298 / 0 |
| P2 by day | original V1 | 1111 | 7260 | 6150 | 7243 / 0 |
| P2 by day | CLASSIC | 1189 | 7754 | 6258 | 7754 / 0 |
| P2 by day | WINDOW | 157 | 626 | 532 | 626 / 0 |
| P3 by month, year slicer, startAtSelection | reference | 47 | 31 | 31 | 31 / 0 |
| P3 by month, year slicer, startAtSelection | CLASSIC | 47 | 31 | 47 | 31 / 0 |
| P3 by month, year slicer, startAtSelection | WINDOW | 47 | 31 | 47 | 31 / 0 |
| P4 by day, year slicer, startAtSelection | reference | 125 | 125 | 125 | 125 / 0 |
| P4 by day, year slicer, startAtSelection | CLASSIC | 141 | 125 | 125 | 124 / 0 |
| P4 by day, year slicer, startAtSelection | WINDOW | 63 | 57 | 63 | 57 / 0 |
| P5 by month, keepFiltersTable (V2) | original V2 | 63 | 219 | 266 | 203 / 0 |
| P5 by month, keepFiltersTable (V2) | CLASSIC | 62 | 235 | 250 | 218 / 17 |
| P5 by month, keepFiltersTable (V2) | WINDOW | 109 | 422 | 438 | 407 / 0 |
| P6 by class (V3) | original V3 | 203 | 969 | 954 | 32 / 937 |
| P6 by class (V3) | CLASSIC | 219 | 955 | 986 | 44 / 923 |
| P6 by class (V3) | WINDOW | 110 | 939 | 893 | 51 / 893 |
| P7 by class, startAtSelection FALSE | reference | 125 | 939 | 860 | 48 / 860 |
| P7 by class, startAtSelection FALSE | CLASSIC | 125 | 876 | 923 | 47 / 830 |
| P7 by class, startAtSelection FALSE | WINDOW | 167 | 1143 | 1267 | 32 / 1110 |
| P8 by Year Month (sorted column), 2023 | original V3 | 31 | 47 | 31 | 47 / 0 |
| P8 by Year Month (sorted column), 2023 | CLASSIC | 31 | 31 | 47 | 31 / 0 |
| P8 by Year Month (sorted column), 2023 | WINDOW | 47 | 31 | 47 | 31 / 0 |
| P9 ADDCOLUMNS by month, direct call | measure (reference) | 47 | 172 | 204 | 172 / 0 |
| P9 ADDCOLUMNS by month, direct call | direct CLASSIC | 62 | 188 | 203 | 188 / 0 |
| P9 ADDCOLUMNS by month, direct call | direct WINDOW | 112 | 658 | 657 | 658 / 0 |
| P10 ADDCOLUMNS by day, direct call | measure (reference) | 1126 | 6264 | 6417 | 6264 / 0 |
| P10 ADDCOLUMNS by day, direct call | direct CLASSIC | 1063 | 6240 | 5850 | 6240 / 0 |
| P10 ADDCOLUMNS by day, direct call | direct WINDOW | 62 | 94 | 93 | 94 / 0 |
