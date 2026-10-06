# Financial Analysis Agent — AGENT.md

Purpose: Daily financial tracking, analysis, and reporting for personal accounts.

Workflow (each day):
1. Read all .csv ledgers: `mtn_mobile_money.csv`, `cash_account.csv`, `bank_account.csv`, `xeno_savings.csv`, `liabilities.csv`, `summary_account.csv`, `income.csv`
2. Check for new entries / clearances / payments since last analysis date
3. Create dated analysis file: YYYY_MM_DD.md in this folder
4. Update `summary_account.csv` with combined net worth (new row if any balance changed)
5. Write / update `FINANCIAL_ANALYSIS.md` (master report at root)
6. Note spending patterns, debt movements, income events, savings protection status

Files maintained:
- `.csv` ledgers (root): assets + liabilities + income
- `summary_account.csv` (root): combined net worth
- `financial_analysis/YYYY_MM_DD.md`: daily snapshots
- `FINANCIAL_ANALYSIS.md` (root): latest master analysis

Rules:
- All entries dated to transaction date (5 Oct = 2026_10_05.md, 6 Oct = 2026_10_06.md, etc.)
- Clearance events: add a clearance row to `liabilities.csv` (negative amount, updated running balance) and note in that date's .md
- Net worth = Total Assets − Total Liabilities; negative = debt exceeds holdings
- Savings (`xeno_savings.csv`) must never be fully liquidated without recording reason in daily file
- Income must be recorded in `income.csv`; cash credits in `cash_account.csv` reference the event but `income.csv` is the canonical income record
- Skills are dynamic: they describe logic and formulas — never embed current balances in skill files
