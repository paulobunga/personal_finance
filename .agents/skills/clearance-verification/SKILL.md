---
name: clearance-verification
description: Verify every liability clearance is recorded as a proper double-entry journal before a balance sheet snapshot is taken. Prevents phantom reductions in net liability totals.
---

# Clearance verification

## Database
All data lives in `financial.db`. Use `db_manager.py` for reads and writes.

## Verification checklist

Complete all steps before calling `create_balance_sheet_snapshot()`:

1. **Original debt journal exists** — a prior journal debited an expense/asset account and credited the relevant liability account (301, 303, 401, etc.) for the amount owed.

2. **Clearance journal exists** — a new journal debits the liability account (reduces it) and credits the payment account (101 Cash, 103 MTN, etc.):
   ```python
   from db_manager import get_db_connection, record_transaction
   conn = get_db_connection()
   # Clearing 7,000 UGX social debt from cash
   record_transaction(conn, '2026-10-07', '301', '101', 7000, 'Debt clearance: Club17 UG Plastic')
   conn.commit()
   conn.close()
   ```

3. **Double-entry is balanced** — run `verify_double_entry(conn)` and confirm `balanced = True`.

4. **Daily `.md` records the clearance** — `financial_analysis/YYYY_MM_DD.md` contains: creditor, original amount, cleared amount, date, and confirmation.

5. **Balance sheet snapshot created** — `create_balance_sheet_snapshot()` called after clearance. New `total_liabilities` must be lower by the cleared amount.

## How to compute post-clearance net worth

```python
from db_manager import get_db_connection, get_balance_sheet
conn = get_db_connection()
bs = get_balance_sheet(conn)
print(f"Net Worth: {bs['net_worth']:,.0f}")
conn.close()
```

Net worth improves by the cleared amount (assets decrease and liabilities decrease equally — no net change in equity, but liability burden reduced).

## Verifying correctness

```python
from db_manager import get_db_connection
import sqlite3

conn = get_db_connection()
cursor = conn.cursor()

# Check net balance of Personal Loans account (301)
cursor.execute("""
    SELECT COALESCE(SUM(credit),0) - COALESCE(SUM(debit),0) as net_liability
    FROM journal_entries
    WHERE account_id = (SELECT id FROM chart_of_accounts WHERE account_code = '301')
""")
print(f"Personal Loans balance: {cursor.fetchone()[0]:,.0f}")
conn.close()
```

The result must decrease by exactly the cleared amount relative to the previous snapshot.
