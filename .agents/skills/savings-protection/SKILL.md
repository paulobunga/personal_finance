---
name: savings-protection
description: Protect the Xeno savings reserve (account 104) from full liquidation. Use before any proposal to use savings to clear debt; enforce that reason is recorded and coverage ratio stays above a safe threshold.
---

# Savings protection

## Database
All data lives in `financial.db`. Xeno Savings is account **104**.

## How to read the current reserve

```python
from db_manager import get_db_connection, get_balance_sheet
import sqlite3

conn = get_db_connection()
cursor = conn.cursor()

# Xeno Savings balance
cursor.execute("""
    SELECT COALESCE(SUM(je.debit),0) - COALESCE(SUM(je.credit),0) as balance
    FROM journal_entries je
    JOIN chart_of_accounts a ON je.account_id = a.id
    WHERE a.account_code = '104'
""")
xeno_balance = cursor.fetchone()[0]

bs = get_balance_sheet(conn)
coverage_ratio = xeno_balance / bs['total_liabilities'] if bs['total_liabilities'] > 0 else 0
print(f"Xeno balance: {xeno_balance:,.0f}")
print(f"Coverage ratio: {coverage_ratio:.2%}")
conn.close()
```

## Protection rules

- **Do NOT** fully liquidate Xeno Savings (account 104) without recording explicit reason in `financial_analysis/YYYY_MM_DD.md`.
- Partial withdrawals allowed if:
  - Emergency (health, school fee partial to prevent exclusion)
  - Coverage ratio after withdrawal remains > 1%
  - Reason cited in daily `.md`
- If savings used to clear debt: net worth change = 0 (assets down = liabilities down equally); only coverage ratio changes. Record in `.md`.
- Preferred strategy: use savings only for essential, time-sensitive obligations (school fees, health). Never for discretionary social debt.
- Rebuild target: once total liabilities < 100,000, redirect 50% of cash inflow back to account 104.

## Minimum safe threshold

Coverage ratio floor: **1%** — Xeno balance / total liabilities ≥ 0.01.

If a proposed withdrawal would breach 1%, flag and require explicit written justification in the daily `.md` before proceeding.

## Savings goals

Xeno Savings funds the freelancing equipment savings goals (MacBook Air M2 first, then Mac Mini M4, etc.). Query the `savings_goals` table for current progress:

```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT goal_name, saved, target, remaining FROM savings_goals ORDER BY priority")
for row in cursor.fetchall():
    print(row)
conn.close()
```
