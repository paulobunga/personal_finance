# AGENTS.md — Financial Ledger Agents
**Account Holder: Paul Obunga**

## Files (Root)
- `mtn_mobile_money.csv` — MTN balance, MomoAdvance debt, withdrawals, fees
- `cash_account.csv` — Cash flow (receipts, food, health, venue, transport, airtime); includes `category` column
- `bank_account.csv` — Standard Chartered Main Branch
- `xeno_savings.csv` — Savings reserve (Xeno)
- `income.csv` — Income ledger (canonical source for all personal income; categories: transport_allowance, salary, business, transfer, other); Feza Kitchen & Grill profit withdrawals recorded here as category=business
- `liabilities.csv` — Running debt (all personal + business obligations); includes `due_date` and `category` columns
- `summary_account.csv` — Combined assets/liabilities/net worth
- `planned_expenses.csv` — Planned freelancing equipment purchases (priority-ordered; linked to savings goals)
- `savings_goals.csv` — Savings goals linked to Xeno; tracks target, saved, and remaining per item

## Business Ledger — Feza Kitchen & Grill
- `feza_sales.csv` — Itemized daily sales (one row per transaction; columns: date, item, quantity, unit_price_ugx, total_ugx, category, note)
- `feza_expenses.csv` — Daily ingredient and operating costs (one row per item; columns: date, item, amount_ugx, category, note)
- `feza_profit_loss.csv` — Daily P&L summary (gross profit = sales − expenses; net profit = gross − rent − staff)

## Financial Analysis Folder
- `financial_analysis/AGENT.md` — Workflow rules (read all ledgers → create dated .md → update summary → protect savings)
- `financial_analysis/YYYY_MM_DD.md` — Daily snapshots (e.g. 2026_10_05.md)
- `FINANCIAL_ANALYSIS.md` — Master analysis report (latest full review)

## Business Context — Feza Kitchen & Grill
- **Business**: Feza Kitchen & Grill — food/catering business operated by **Paul Obunga**
- **Venue**: Kitchen space rented from Club17 Management at 450,000 UGX/month (Sept rate); 400,000 UGX/month from Oct onwards
- **Staff**:
  - Chef — 400,000 UGX/month; salary due end of each week completing a full month
  - Waitress — 38,000 UGX/week; salary due end of each working week
- **Income source**: Feza Events (U) Ltd transport allowances and business revenue flow through `income.csv`
- **Liability categories**:
  - `rent_business` — Feza Kitchen & Grill venue rent (Club17 Management); separate from residential `rent`
  - `salary_business` — Chef and Waitress salaries; separate from personal `salary` (Maid at home)
- **Upcoming obligations**: Nov rent 400,000 (due 2026-11-30); Dec rent 400,000 (due 2026-12-31); recorded as `upcoming` in `liabilities.csv`

## Liability Categories (liabilities.csv)
- `social` — discretionary venue/social debts (Club17 sodas, beer)
- `loan` — personal loans (Patricia, Remmy, Ahmed) and mobile money advances (MTN MomoAdvance)
- `school` — school fees (Britney, Beverly)
- `rent` — residential rent (Landlord home)
- `rent_business` — business venue rent (Club17 Management / Feza Kitchen & Grill)
- `salary` — personal salary obligations (Maid at home)
- `salary_business` — business staff salaries (Chef, Waitress)

## Active Agents / Tracks
- MTN Mobile Money (overdraft tracking, MomoAdvance limit/headroom, withdrawal fees)
- Cash Pocket (rapid depletion monitoring; `category` column enables spend-type filtering)
- Xeno Savings (reserve protection; coverage ratio vs liabilities tracked each session; linked to savings goals)
- Liabilities Tracker (personal + business debts; `due_date` and `category` columns; upcoming obligations flagged)
- Bank Account (Standard Chartered Main Branch)
- Income Tracker (all income sources; canonical record in `income.csv`)
- Feza Kitchen & Grill (business rent, chef salary, waitress salary; separate from personal obligations)
- Savings Goals Tracker (freelancing equipment goals; linked to Xeno; `savings_goals.csv`)

## Skills (`.agents/skills/`)
- `financial-analysis` — daily analysis workflow
- `double-entry-accounting` — transaction recording rules
- `savings-protection` — Xeno savings guard rules
- `clearance-verification` — debt clearance verification checklist
- `debt-repayment-scheduler` — priority order for paying debts
- `rent-obligation-tracker` — recurring rent forecasting (personal + business)
- `forecasting-calculations` — ratios, projections, scenario modeling
- `income-tracker` — income monitoring and gap detection
- `feza-business-tracker` — Feza Kitchen & Grill daily sales, expenses, P&L, break-even analysis

## Rules (from financial_analysis/AGENT.md)
- Transaction dates = file dates (5 Oct = 2026_10_05.md)
- Clearances = clearance row in liabilities.csv (negative amount, updated running balance) + note in that date's .md
- Net worth = Assets - Liabilities (includes both personal and business liabilities); negative = insolvency state
- Savings must not be fully liquidated without recording reason in daily file
- Income must be recorded in `income.csv` first; `cash_account.csv` credits reference the event but do not replace `income.csv`
- Business obligations (rent_business, salary_business) tracked separately from personal in `liabilities.csv` via category column
- Upcoming obligations (status = upcoming) are not counted in current net worth but must be flagged in daily .md
