---
name: income-tracker
description: Monitor income sources from income.csv, compute totals per period, identify income gaps, and flag sessions with zero recent income. Use at the start of each financial analysis session.
---

# Income tracker

## How to read income data
- Open `income.csv` — schema: `date, source, description, amount, balance, note, category`
- The `balance` column = cumulative income total (running all-time sum)
- To get period income: filter rows by `date` range and sum `amount`

## Standard computations
- **Total income this month** = sum `amount` where `date` falls in current calendar month
- **Total income last 7 days** = sum `amount` where `date` >= today − 7
- **Income by source** = group by `source`, sum `amount`
- **Income by category** = group by `category`, sum `amount`

## Categories (`income.csv` `category` column)
- `transport_allowance` — per-trip or per-event transport payment
- `salary` — regular employment income
- `business` — business revenue or client payment
- `transfer` — received transfer (mobile money, bank)
- `other` — miscellaneous

## Rules
- All income must be recorded in `income.csv` first. Cash credits in `cash_account.csv` reference the income event but `income.csv` is the canonical source for income totals.
- Do not double-count: when computing total income, use `income.csv` only. `cash_account.csv` credit rows for income events are for cash-flow tracking only.
- Each new income event: add a row to `income.csv` with running `balance` = previous `balance` + `amount`.

## Red flags
- Zero income in `income.csv` for the last 7 days → flag in daily `.md` as "No income recorded — 7-day gap"
- Single income source > 90% of all income → flag as income concentration risk
- Monthly income < 10% of `Total_Liabilities` (from `summary_account.csv`) → flag as structural deficit

## Integration
- Invoked in step 1 of `financial-analysis` skill daily workflow
- Monthly income total referenced in `forecasting-calculations` Scenario D
- Monthly income used by `debt-repayment-scheduler` to assess available cash inflow
