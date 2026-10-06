# AGENTS.md — Financial Ledger Agents

## Files (Root)
- `mtn_mobile_money.csv` — MTN balance, MomoAdvance debt, withdrawals, fees
- `cash_account.csv` — Cash flow (receipts, food, health, venue, agent outflows, airtime)
- `bank_account.csv` — Standard Chartered Main Branch
- `xeno_savings.csv` — Savings reserve (Xeno)
- `liabilities.csv` — Running debt (Club17, personal loans, school fees, landlord rent)
- `summary_account.csv` — Combined assets/liabilities/net worth

## Financial Analysis Folder
- `financial_analysis/AGENT.md` — Workflow rules (read ledgers → create dated .md → update summary → protect savings)
- `financial_analysis/YYYY_MM_DD.md` — Daily snapshots (e.g. 2026_10_05.md)
- `FINANCIAL_ANALYSIS.md` — Master analysis report (latest full review)

## Active Agents / Tracks
- MTN Mobile Money (overdraft tracking, withdrawal fees)
- Cash Pocket (rapid depletion monitoring — 36k → 9k observed)
- Xeno Savings (reserve protection — 72,201; 87% of assets)
- Liabilities Tracker (Club17 venue debt, personal loans, school fees, landlord rent)
- Bank Account (Standard Chartered Main Branch — 997)
- Pending Agent (Leuben/Askari 1,500 — unverified; tracked in cash notes)

## Rules (from AGENT.md)
- Transaction dates = file dates (5 Oct = 2026_10_05.md)
- Clearances = entry in liabilities.csv + note in that date's .md
- Net worth = Assets - Liabilities; negative = insolvency state
- Savings must not be fully liquidated without recording reason in daily file
