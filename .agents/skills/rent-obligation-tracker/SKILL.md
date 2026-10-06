---
name: rent-obligation-tracker
description: Track recurring rent obligations separately from one-time debts. Use when landlord and venue rent debts accumulate and monthly liability growth must be forecasted.
---

# Rent obligation tracker

## How to read current rent obligations
- Open `liabilities.csv` — filter rows where `category` = `rent` and `status` = `owed`.
- Sum all `amount` values in those rows = total current rent liability.
- Count distinct `creditor` values = number of active rent obligations.

## Forecasting monthly growth
- For each active rent creditor: if `status` remains `owed` and a new month passes, a new row will be added with `amount` = that creditor's monthly rate.
- Monthly liability growth (if nothing paid) = sum of all active monthly rent rates.
- To find the monthly rate per creditor: look at the most recent `rent` row for that creditor and use its `amount` as the recurring monthly charge.
- Project forward: New Total Liabilities at +N months = current `Total_Liabilities` + (monthly rent total × N).

## Rules
- Rent is recurring; unlike one-time `social` debt, rent accumulation leads to eviction or venue loss risk.
- Record each new month's rent as a new line in `liabilities.csv` with the correct running `balance`.
- In `financial_analysis/YYYY_MM_DD.md`: note part-payment proposals (even partial amounts slow accumulation) or negotiation status.
- Treat rent as essential after school fees in `debt-repayment-scheduler` priority order.
- Part-payment guidance: any partial payment toward rent slows monthly accumulation; record in `liabilities.csv` as a clearance row for the partial amount paid.
