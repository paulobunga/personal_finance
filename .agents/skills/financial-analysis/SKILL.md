---
name: financial-analysis
description: "Daily financial analysis routine: read all ledgers, detect changes since last .md snapshot, create YYYY_MM_DD.md, update summary_account.csv, update FINANCIAL_ANALYSIS.md master report, and flag red flags."
---

# Financial analysis

## Daily workflow
Run at the end of each accounting session:

1. Read all `.csv` ledgers: `mtn_mobile_money.csv`, `cash_account.csv`, `bank_account.csv`, `xeno_savings.csv`, `liabilities.csv`, `summary_account.csv`, `income.csv`.
2. Read the most recent `financial_analysis/YYYY_MM_DD.md` and `FINANCIAL_ANALYSIS.md`.
3. Identify changes since last snapshot: new entries, clearances, balance shifts, new income.
4. Create `financial_analysis/YYYY_MM_DD.md` with:
   - Asset state table (one row per account; balance = last row in each asset `.csv`)
   - Liability state table (all `status = owed` rows from `liabilities.csv`; sum = `Total_Liabilities`)
   - Net Worth = Total Assets − Total Liabilities
   - Income summary: total from `income.csv` for the current month
   - Forecast section (invoke `forecasting-calculations` skill for ratios and scenario projections)
   - Daily notes: key events, new debts, clearances, spending pattern flags, savings protection status
   - Debt repayment priority (invoke `debt-repayment-scheduler` skill)
5. Add a new row to `summary_account.csv` if any balance changed.
6. Update `FINANCIAL_ANALYSIS.md` at root with the latest full review.
7. Never fully liquidate `xeno_savings.csv` without recording reason in the daily file.

## Red flags to check each session
- Net worth negative and worsening (compare to previous day's `.md`)
- Cash balance = 0 or below 5,000
- MTN balance negative (MomoAdvance or overdraft recorded in `mtn_mobile_money.csv`)
- MomoAdvance headroom < 2,000 UGX (invoke `momo-advance-tracker` skill for limit vs owed calculation)
- New liabilities added without corresponding income in `income.csv`
- Savings coverage ratio < 2% (`xeno_savings.csv` last balance / `Total_Liabilities`)
- No income recorded in `income.csv` for 7+ days

## Files maintained
- `income.csv` — income ledger (read in step 1)
- `financial_analysis/AGENT.md` — workflow rules
- `financial_analysis/YYYY_MM_DD.md` — daily snapshots
- `FINANCIAL_ANALYSIS.md` — master report
- All `.csv` ledgers (root)
