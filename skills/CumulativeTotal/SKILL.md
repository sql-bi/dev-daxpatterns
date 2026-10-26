---
name: daxpatterns-cumulative-total
description: Apply the DaxPatterns.CumulativeTotal library (DAX Lib) to a Power BI semantic model. Use when a user asks for a running total, cumulative total, stock or balance from transactions, or a cumulative total by a sortable column (class, rank). Inspect the model, validate the requirements, create missing objects only with approval, install the library, and generate model-specific wrapper functions and measures.
---

# Cumulative total with DAX Lib

This skill applies the `DaxPatterns.CumulativeTotal` library to one semantic model.
Library source: `src/CumulativeTotal/`. Pattern: https://www.daxpatterns.com/cumulative-total/

## Rules

- Do not change the model without the approval of the user. First show the list of changes.
- Use read-only DAX queries to inspect and validate the model.
- Write "DAX Lib" in text for users. Write `DaxLib` only in code.
- Do not copy the library code by hand. Install the package (step 4).

## 1. Inspect the model

Get the tables, columns, relationships, and measures. Use one of these sources:

- TMDL files of the model (Power BI Project), or
- DAX queries: `INFO.VIEW.TABLES ()`, `INFO.VIEW.COLUMNS ()`, `INFO.VIEW.RELATIONSHIPS ()`, `INFO.VIEW.MEASURES ()`.

Find these objects. Write them in a table for the user:

| Object | How to find it | Example |
|---|---|---|
| Date table | `DataCategory = "Time"`, or a table with a unique column of type Date | `'Date'` |
| Date column | The unique Date column of the date table | `'Date'[Date]` |
| Fact table and its date column | Active many-to-one relationship to the date table | `Sales[Order Date]` |
| Value measure | Additive measure (SUM, SUMX) | `[Sales Amount]` |
| Sortable column (optional) | Column in the report with a Sort by Column | `Customer[Customer Class]` sorted by `Customer[Customer Class Number]` |
| Columns that keep the filter (optional) | Ask the user | `'Date'[Day of Week]` |

## 2. Validate the requirements

Run these queries. Replace the names with the names of the model.

Date table has no gaps and one row for each date (expect `Gaps = 0`, `Duplicates = 0`):

```DAX
EVALUATE
VAR MinDate = MIN ( 'Date'[Date] )
VAR MaxDate = MAX ( 'Date'[Date] )
RETURN
    ROW (
        "Gaps", DATEDIFF ( MinDate, MaxDate, DAY ) + 1 - DISTINCTCOUNT ( 'Date'[Date] ),
        "Duplicates", COUNTROWS ( 'Date' ) - DISTINCTCOUNT ( 'Date'[Date] )
    )
```

Date table covers all the fact dates (expect `MissingDates = 0`):

```DAX
EVALUATE
ROW (
    "MissingDates",
        COUNTROWS ( EXCEPT ( DISTINCT ( Sales[Order Date] ), DISTINCT ( 'Date'[Date] ) ) ) + 0
)
```

Sortable column: one order value for each display value (expect `Conflicts = 0`):

```DAX
EVALUATE
ROW (
    "Conflicts",
        COUNTROWS ( SUMMARIZE ( Customer, Customer[Customer Class], Customer[Customer Class Number] ) )
            - DISTINCTCOUNT ( Customer[Customer Class] )
)
```

The relationship from the fact table to the date table must be active and many-to-one.
If a check fails, tell the user the problem and the fix. Do not continue until the user agrees.

## 3. Create the missing objects (only with approval)

- No date table: propose a calculated table, then a relationship to the fact table:

  ```DAX
  Date =
  VAR FirstYear = YEAR ( MIN ( Sales[Order Date] ) )
  VAR LastYear = YEAR ( MAX ( Sales[Order Date] ) )
  RETURN
      ADDCOLUMNS (
          CALENDAR ( DATE ( FirstYear, 1, 1 ), DATE ( LastYear, 12, 31 ) ),
          "Year", YEAR ( [Date] ),
          "Year Month", FORMAT ( [Date], "mmm yyyy" ),
          "Year Month Number", YEAR ( [Date] ) * 12 + MONTH ( [Date] ) - 1,
          "Day of Week", FORMAT ( [Date], "dddd" )
      )
  ```

  Set Sort by Column: `Year Month` by `Year Month Number`. Mark as date table is optional.
- No additive measure: propose one, e.g. `Sales Amount = SUMX ( Sales, Sales[Quantity] * Sales[Net Price] )`.

## 4. Install the library

- Power BI Desktop: use the DAX Lib MCP server (tool to install a package), or daxlib.org.
- Package id: `DaxPatterns.CumulativeTotal`. Use the latest version.
- After the installation, check that the functions exist:
  `EVALUATE FILTER ( INFO.FUNCTIONS ( "ORIGIN", "2" ), CONTAINSSTRING ( [FUNCTION_NAME], "DaxPatterns.CumulativeTotal" ) )`

## 5. Generate the model-specific functions and measures

Ask the user these questions:

1. Start at the first date of the date table, or at the first selected date? (`startAtSelection`)
2. Which columns of the date table must keep their filters? (`keepFiltersTable`)
3. Which granularity does the report use most: days or months? (`implementation`: many cells, e.g. days, use `"WINDOW"`; few cells use `"CLASSIC"`)

Then generate one wrapper function for each cumulative total, with the prefix `Local.` (model-dependent function),
and one measure that calls it:

```DAX
FUNCTION Local.CumulativeTotal.SalesAmountRT = () =>
    DaxPatterns.CumulativeTotal.OverDates (
        [Sales Amount],
        'Date'[Date],
        Sales[Order Date]
    )

MEASURE Sales[Sales Amount RT] = Local.CumulativeTotal.SalesAmountRT ()
```

With a parameter for the value, to use the same settings for many measures:

```DAX
FUNCTION Local.CumulativeTotal.OverOrderDate = ( valueExpr : ANYREF EXPR ) =>
    DaxPatterns.CumulativeTotal.OverDates (
        valueExpr,
        'Date'[Date],
        Sales[Order Date],
        VALUES ( 'Date'[Day of Week] ),
        FALSE,
        "CLASSIC"
    )

MEASURE Sales[Sales Amount RT] = Local.CumulativeTotal.OverOrderDate ( [Sales Amount] )
MEASURE Sales[Quantity RT] = Local.CumulativeTotal.OverOrderDate ( [Total Quantity] )
```

Sortable column:

```DAX
FUNCTION Local.CumulativeTotal.OverCustomerClass = ( valueExpr : ANYREF EXPR ) =>
    DaxPatterns.CumulativeTotal.OverSortedColumn (
        valueExpr,
        Customer[Customer Class Number],
        Customer[Customer Class]
    )
```

Note: in a wrapper function, `keepFiltersTable` is evaluated in the filter context of the call to the wrapper. This is the filter context of the measure.

## 6. Test

1. Run the tests of the library on a copy of the model, or on dax.do:
   `python3 tests/CumulativeTotal/run_tests.py daxdo`
2. Compare the new measure with a reference measure (original DAX of the pattern) on the model of the user:
   by month, by day, with a slicer, and at the grand total. Use the queries in `tests/CumulativeTotal/cases/` as templates.
   Expect 0 differences.
3. If the report is slow, test `"WINDOW"` and `"CLASSIC"` with the real visual (Performance Analyzer or DAX Studio server timings).

## 7. Report

Give the user:

- The objects found (table of step 1) and the result of each check (step 2).
- The objects created or changed.
- The test results and any warning (e.g. a date table with gaps, a non-additive measure).
