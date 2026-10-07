---
name: financial-analysis
description: "Daily financial analysis routine: query the SQLite database for current balances, detect changes since last snapshot, create YYYY_MM_DD.md, and flag red flags. Replaces the old CSV-based workflow."
---

# Financial analysis

## Database
All data lives in `financial.db`. Use `db_manager.py` for all reads.

## Daily workflow

Run at the end of each accounting session:

1. **Read current state from DB**
   ```python
   from db_manager import get_db_connection, get_balance_sheet, get_income_statement, get_trial_balance
   conn = get_db_connection()
   bs = get_balance_sheet(conn)
   pl = get_income_statement(conn)
   conn.close()
   ```

2. **Read the most recent** `financial_analysis/YYYY_MM_DD.md` for comparison.

3. **Identify changes** since last snapshot: new journal entries, balance shifts, new income, new debts.

4. **Create** `financial_analysis/YYYY_MM_DD.md` with:
   - Asset state table: query `chart_of_accounts` joined to `journal_entries`, filter `account_type = Asset`
   - Liability state table: query `chart_of_accounts` joined to `journal_entries`, filter `account_type = Liability`
   - Net Worth = `bs['total_assets']` − `bs['total_liabilities']`
   - Income summary: query `journal_entries` joined to accounts with `account_type = Revenue` for current month
   - Forecast section (invoke `forecasting-calculations` skill)
   - Daily notes: key events, new debts, clearances, red flags, savings protection status
   - Debt repayment priority (invoke `debt-repayment-scheduler` skill)

5. **Save a balance sheet snapshot**
   ```python
   from db_manager import get_db_connection, create_balance_sheet_snapshot
   conn = get_db_connection()
   create_balance_sheet_snapshot(conn, period_id=1, snapshot_date='2026-10-07')
   conn.commit()
   conn.close()
   ```

6. **Never fully liquidate Xeno Savings (account 104)** without recording the reason in the daily `.md` file.

## Querying account balances

```python
from db_manager import get_db_connection
import sqlite3

conn = get_db_connection()
cursor = conn.cursor()

# Get net balance per account
cursor.execute("""
    SELECT a.account_code, a.name,
           COALESCE(SUM(je.debit),0) - COALESCE(SUM(je.credit),0) as balance
    FROM chart_of_accounts a
    JOIN account_types t ON a.account_type_id = t.id
    LEFT JOIN journal_entries je ON a.id = je.account_id
    WHERE t.category = 'asset'
    GROUP BY a.id ORDER BY a.account_code
""")
for row in cursor.fetchall():
    print(row)
conn.close()
```

## Red flags to check each session

- Net worth negative and worsening (compare `balance_sheet_snapshots` latest two rows)
- Cash (account 101) balance = 0 or < 5,000
- MTN (account 103) net balance negative (MomoAdvance in use)
- MomoAdvance (account 303) credit balance > 12,000 (invoke `momo-advance-tracker`)
- New liability journals added without corresponding revenue journal in same period
- Xeno Savings (account 104) debit balance < 2% of total liabilities
- No revenue journals recorded in any account for 7+ days

## Files maintained
- `financial.db` — single source of truth
- `financial_analysis/YYYY_MM_DD.md` — daily narrative snapshots
- `financial_analysis/AGENT.md` — workflow rules
