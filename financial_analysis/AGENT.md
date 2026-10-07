# Financial Analysis Agent — AGENT.md
**Account Holder: Paul Obunga**

Purpose: Daily financial tracking, analysis, and reporting for personal accounts.

Workflow (each day):
1. Read all .csv ledgers: `mtn_mobile_money.csv`, `cash_account.csv`, `bank_account.csv`, `xeno_savings.csv`, `liabilities.csv`, `summary_account.csv`, `income.csv`, `feza_sales.csv`, `feza_expenses.csv`, `feza_profit_loss.csv`
2. Check for new entries / clearances / payments since last analysis date
3. Create dated analysis file: YYYY_MM_DD.md in this folder
4. Update `summary_account.csv` with combined net worth (new row if any balance changed)
5. Write / update `FINANCIAL_ANALYSIS.md` (master report at root)
6. Note spending patterns, debt movements, income events, savings protection status

Files maintained:
- `.csv` ledgers (root): assets + liabilities + income + business (feza_sales, feza_expenses, feza_profit_loss)
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

## Feza Kitchen & Grill — Business Ledger Rules
- `feza_sales.csv` — one row per sale transaction; record immediately after each sale
- `feza_expenses.csv` — one row per ingredient/cost item; record at time of purchase
- `feza_profit_loss.csv` — one row per trading day; compute after all sales and expenses for the day are entered
- Gross profit = total sales − total expenses (ingredients + transport only)
- Net profit = gross profit − daily share of rent − daily share of staff salaries
- Monthly break-even = 952,000 UGX (rent 400k + chef 400k + waitress ~152k)
- Paul Obunga cash withdrawals from business profit: record in `income.csv` (category=business) and `cash_account.csv` (credit, category=income)
- Business expenses (ingredients, transport) stay in `feza_expenses.csv` only — do NOT record in `cash_account.csv`
- Invoke `feza-business-tracker` skill for P&L analysis, break-even check, and best-seller analysis
