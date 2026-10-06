# AGENTS.md — Financial Ledger Agents

## Files (Root)
- `mtn_mobile_money.csv` — MTN balance, MomoAdvance debt, withdrawals, fees
- `cash_account.csv` — Cash flow (receipts, food, health, venue, transport, airtime); includes `category` column
- `bank_account.csv` — Standard Chartered Main Branch
- `xeno_savings.csv` — Savings reserve (Xeno)
- `income.csv` — Income ledger (canonical source for all income; categories: transport_allowance, salary, business, transfer, other)
- `liabilities.csv` — Running debt (Club17, personal loans, school fees, landlord rent, salary); includes `due_date` and `category` columns
- `summary_account.csv` — Combined assets/liabilities/net worth

## Financial Analysis Folder
- `financial_analysis/AGENT.md` — Workflow rules (read all ledgers → create dated .md → update summary → protect savings)
- `financial_analysis/YYYY_MM_DD.md` — Daily snapshots (e.g. 2026_10_05.md)
- `FINANCIAL_ANALYSIS.md` — Master analysis report (latest full review)

## Active Agents / Tracks
- MTN Mobile Money (overdraft tracking, withdrawal fees)
- Cash Pocket (rapid depletion monitoring; `category` column enables spend-type filtering)
- Xeno Savings (reserve protection; coverage ratio vs liabilities tracked each session)
- Liabilities Tracker (Club17 venue debt, personal loans, school fees, landlord rent, salary; `due_date` and `category` columns)
- Bank Account (Standard Chartered Main Branch)
- Income Tracker (all income sources; canonical record in `income.csv`)

## Skills (`.agents/skills/`)
- `financial-analysis` — daily analysis workflow
- `double-entry-accounting` — transaction recording rules
- `savings-protection` — Xeno savings guard rules
- `clearance-verification` — debt clearance verification checklist
- `debt-repayment-scheduler` — priority order for paying debts
- `rent-obligation-tracker` — recurring rent forecasting
- `forecasting-calculations` — ratios, projections, scenario modeling
- `income-tracker` — income monitoring and gap detection
- `momo-advance-tracker` — MomoAdvance limit, owed amount, and remaining headroom

## Rules (from financial_analysis/AGENT.md)
- Transaction dates = file dates (5 Oct = 2026_10_05.md)
- Clearances = clearance row in liabilities.csv (negative amount, updated running balance) + note in that date's .md
- Net worth = Assets - Liabilities; negative = insolvency state
- Savings must not be fully liquidated without recording reason in daily file
- Income must be recorded in `income.csv` first; `cash_account.csv` credits reference the event but do not replace `income.csv`
