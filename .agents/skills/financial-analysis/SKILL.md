---
name: financial-analysis
description: Daily financial analysis routine: read ledgers, detect changes since last .md, create YYYY_MM_DD.md snapshot, update summary_account.csv, update FINANCIAL_ANALYSIS.md master report, and flag red flags (negative net, rapid cash depletion, pending agent outflows, savings exposure). Use at end of each accounting session.
---

# Financial analysis

Daily workflow (from `financial_analysis/AGENT.md`):

1. Read `.csv` ledgers: `mtn_mobile_money.csv`, `cash_account.csv`, `bank_account.csv`, `xeno_savings.csv`, `liabilities.csv`, `summary_account.csv`.
2. Read previous dated file (most recent `financial_analysis/YYYY_MM_DD.md`) and `FINANCIAL_ANALYSIS.md`.
3. Identify changes: new entries, clearances (`liabilities.csv` clearance lines), balance shifts.
4. Create `financial_analysis/YYYY_MM_DD.md` with:
   - Date snapshot line (`date | Net worth | Assets | Liabilities | Key event`)
   - Short note of any debt added, cleared, or agent outflow
5. Update `summary_account.csv` (add new row with updated net worth if changed).
6. Update `FINANCIAL_ANALYSIS.md` at root with latest full review (assets, liabilities, net, red flags, recommendations).
7. Never fully liquidate `xeno_savings.csv` balance without recording reason in the daily file.

Files:
- `financial_analysis/AGENT.md`
- `FINANCIAL_ANALYSIS.md`
- All `.csv` ledgers (root)
