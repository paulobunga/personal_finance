# Financial Analysis Agent — AGENT.md

Purpose: Daily financial tracking, analysis, and reporting for personal accounts.

Workflow (each day):
1. Read all .csv ledgers (mtn_mobile_money.csv, cash_account.csv, bank_account.csv, xeno_savings.csv, liabilities.csv)
2. Check for new entries / clearances / payments since last analysis date
3. Create dated analysis file: YYYY_MM_DD.md in this folder
4. Update summary_account.csv with combined net worth
5. Write / update FINANCIAL_ANALYSIS.md (master report at root)
6. Note spending patterns, debt movements, agent/pending outflows, savings protection status

Files maintained:
- .csv ledgers (root): assets + liabilities
- summary_account.csv (root): combined net worth
- financial_analysis/YYYY_MM_DD.md: daily snapshots
- FINANCIAL_ANALYSIS.md (root): latest master analysis

Rules:
- All entries dated to transaction date (5 Oct = 2026_10_05.md, 6 Oct = 2026_10_06.md, etc.)
- Clearance events get their own entry in liabilities.csv and are noted in that date's .md
- Net worth = Total Assets - Total Liabilities; negative = debt exceeds holdings
- Savings (Xeno) must never be fully liquidated without recording reason in daily file
