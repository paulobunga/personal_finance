---
name: double-entry-accounting
description: Double-entry bookkeeping with paired debit/credit entries, running balances per account, and a combined net-worth summary. Use when recording transactions across MTN, Cash, Bank, Savings, and Liabilities ledgers so assets always equal liabilities plus equity.
---

# Double-entry accounting

Rules (derived from the current ledger set):

- Every transaction touches at least two accounts (debit = increase in assets/expenses, or decrease in liabilities/revenue; credit = opposite).
- Each `.csv` ledger is one account: `mtn_mobile_money.csv`, `cash_account.csv`, `bank_account.csv`, `xeno_savings.csv`, `liabilities.csv`.
- The combined position is computed as: **Assets (MTN + Cash + Bank + Savings) − Liabilities**. This equals Net Worth (equity in a single-owner setup).
- Liabilities use an increasing running balance: each new debt increases the running total (`4000 → 11000 → 824000 → 2424000` shown in `liabilities.csv`).
- Clearances reduce running liabilities: enter a clearance line in `liabilities.csv` with amount = cleared value and a new running balance.

Procedure:
1. Read all `.csv` ledgers in root.
2. Confirm each new entry has date, account, debit/credit, amount, running balance, and note.
3. For liabilities: add new debt amount to previous running balance; for clearances: subtract and record clearance date.
4. Update `summary_account.csv`: Total_Assets (sum of MTN + Cash + Bank + Xeno), Total_Liabilities (last running balance from liabilities.csv), Net_Worth = Assets − Liabilities.
5. Write or append to `financial_analysis/YYYY_MM_DD.md` with the new net worth.

Files referenced:
- `mtn_mobile_money.csv` — MTN account
- `cash_account.csv` — cash account
- `bank_account.csv` — bank
- `xeno_savings.csv` — savings
- `liabilities.csv` — liabilities (increasing running balance)
- `summary_account.csv` — combined statement
- `AGENT.md` — agent rules
