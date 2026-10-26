# DaxPatterns.CumulativeTotal

Functions to implement the [Cumulative total](https://www.daxpatterns.com/cumulative-total/) pattern from [DAX Patterns](https://www.daxpatterns.com/).

## What it does

A cumulative total (running total) adds the values of all the previous periods or items to the value of the current one.
Use it for running totals, stock levels, and balances that you calculate from the transactions.

- `OverDates` calculates the cumulative total over the dates of a date table.
- `OverSortedColumn` calculates the cumulative total over any column that you can sort, for example a customer class.

---

## Functions

```DAX
DaxPatterns.CumulativeTotal.OverDates (
    <valueExpr>,           -- e.g., [Sales Amount] (additive)
    <dateColumn>,          -- e.g., 'Date'[Date]
    <lastDateColumn>,      -- e.g., Sales[Order Date]; use <dateColumn> to disable the check on the last date
    [<keepFiltersTable>],  -- optional, e.g., VALUES ( 'Date'[Day of Week] ); default: no filter
    [<startAtSelection>],  -- optional, FALSE (default) = first date of the date table, TRUE = first selected date
    [<implementation>]     -- optional, "CLASSIC" (default) or "WINDOW"
)
```

**Return:** The value of `<valueExpr>` for all the dates up to the last visible date.
The result is BLANK for the periods that start after the last date in `<lastDateColumn>`.
The function removes all the filters on the date table. Then it applies `<keepFiltersTable>` again.

```DAX
DaxPatterns.CumulativeTotal.OverSortedColumn (
    <valueExpr>,           -- e.g., [Sales Amount] (additive)
    <orderColumn>,         -- e.g., Customer[Customer Class Number]
    <displayColumn>,       -- e.g., Customer[Customer Class] (Sort by Column = <orderColumn>); if there is no Sort by Column, use <orderColumn> again
    [<startAtSelection>],  -- optional, TRUE (default) = only the selected values, FALSE = first value of the table
    [<implementation>]     -- optional, "CLASSIC" (default) or "WINDOW"
)
```

**Return:** The value of `<valueExpr>` for all the values of `<orderColumn>` up to the last visible value.
The function removes the filters on `<orderColumn>` and `<displayColumn>` only.

To skip an optional argument, leave it empty: `OverDates ( [Sales Amount], 'Date'[Date], Sales[Order Date], , , "WINDOW" )`.

---

## Model requirements

1. **Value:** An additive measure or expression, e.g.:

   ```DAX
   Sales Amount =
   SUMX ( Sales, Sales[Quantity] * Sales[Net Price] )
   ```

2. **For `OverDates`:**
   * A date table with one row for each date and no gaps. It is not necessary to mark it as a date table.
   * A relationship from the fact table to the date table.
   * A date column in the fact table (`<lastDateColumn>`), e.g., `Sales[Order Date]`.
3. **For `OverSortedColumn`:**
   * A column that the `<=` operator sorts correctly (number, date, or text).
   * If the report shows a different column, that column must use `<orderColumn>` as Sort by Column.
     Each value of `<displayColumn>` must have only one value of `<orderColumn>`.

---

## Basic usage

```DAX
Sales Amount RT =
DaxPatterns.CumulativeTotal.OverDates ( [Sales Amount], 'Date'[Date], Sales[Order Date] )
```

```DAX
Sales Amount RT Weekdays =
DaxPatterns.CumulativeTotal.OverDates (
    [Sales Amount],
    'Date'[Date],
    Sales[Order Date],
    VALUES ( 'Date'[Day of Week] )   -- keep the selection of the days of the week
)
```

```DAX
Sales Amount RT In Selection =
DaxPatterns.CumulativeTotal.OverDates ( [Sales Amount], 'Date'[Date], Sales[Order Date], , TRUE )
```

```DAX
Sales Amount RT Class =
DaxPatterns.CumulativeTotal.OverSortedColumn (
    [Sales Amount],
    Customer[Customer Class Number],
    Customer[Customer Class]
)
```

| Article variant | Call |
|---|---|
| Sales Amount RT | `OverDates ( [Sales Amount], 'Date'[Date], Sales[Order Date] )` |
| Date table not marked as date table | Same call |
| RT Weekdays | `OverDates ( [Sales Amount], 'Date'[Date], Sales[Order Date], VALUES ( 'Date'[Day of Week] ) )` |
| Sales Amount RT Class | `OverSortedColumn ( [Sales Amount], Customer[Customer Class Number], Customer[Customer Class] )` |

---

## Tips, constraints, and performance

* **Additivity:** `<valueExpr>` must be additive (SUM-based). For other expressions, the result is the value of the expression over all the accumulated dates or items.
* **Implementation:** `"CLASSIC"` is faster when the report has few cells (e.g., months). `"WINDOW"` is faster when the report has many cells (e.g., days): in our tests, by day, it was 7 to 12 times faster; by month, it was 4 to 5 times slower. Test both on your model.
* **Start at selection:** With `startAtSelection = TRUE`, `OverDates` starts at the first selected date and includes all the dates after it. `OverSortedColumn` includes only the selected values.
* **Date table of a marked date table:** If `<orderColumn>` is the date column of a marked date table, `OverSortedColumn` removes all the filters on the date table (the same behavior as the `CALCULATE` filter on a marked date table).
* **Iterators:** The functions use `CALCULATE` internally. A direct call inside an iterator (e.g., `ADDCOLUMNS`) gives the same result as a measure.
* **keepFiltersTable:** DAX evaluates this argument before the call, in the filter context of the caller.
* **Invalid values:** An `<implementation>` value other than `"CLASSIC"` or `"WINDOW"` raises an error.
* **Visual calculations:** If you need the running total only in one visual, `RUNNINGSUM` in a visual calculation is an alternative.

---

## Related reading

* [DAX Patterns: Cumulative total](https://www.daxpatterns.com/cumulative-total/).
* [DAX Lib package list](https://daxlib.org/packages/) (package repository).

---

## License

[MIT License](https://en.wikipedia.org/wiki/MIT_License).
