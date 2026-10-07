---
name: momo-advance-tracker
description: Track MTN MomoAdvance limit, current amount owed, and remaining borrowing headroom. Use whenever a MomoAdvance is taken, repaid, or the limit changes — and to answer "how much more can I borrow?".
---

# MomoAdvance tracker

## Database
All data lives in `financial.db`. MomoAdvance is tracked via account **303 (MomoAdvance)** — a personal liability account.

## How to read current state

```python
from db_manager import get_db_connection
import sqlite3

conn = get_db_connection()
cursor = conn.cursor()

# Current MomoAdvance balance owed
cursor.execute("""
    SELECT COALESCE(SUM(je.credit),0) - COALESCE(SUM(je.debit),0) as owed
    FROM journal_entries je
    JOIN chart_of_accounts a ON je.account_id = a.id
    WHERE a.account_code = '303'
""")
owed = cursor.fetchone()[0]
print(f"MomoAdvance owed: {owed:,.0f}")

# MTN Mobile Money effective balance
cursor.execute("""
    SELECT COALESCE(SUM(je.debit),0) - COALESCE(SUM(je.credit),0) as balance
    FROM journal_entries je
    JOIN chart_of_accounts a ON je.account_id = a.id
    WHERE a.account_code = '103'
""")
mtn_balance = cursor.fetchone()[0]
print(f"MTN effective balance: {mtn_balance:,.0f}")
conn.close()
```

**Remaining headroom** = MomoAdvance limit (14,000 UGX as of Oct 2026) − amount owed on account 303.

## How MomoAdvance works in double-entry

- MTN uses available MTN balance (103) first, then auto-advances the shortfall.
- Amount advanced = transaction cost − MTN balance available at time.
- The full advance is auto-deducted on next significant MTN receipt.

## Recording a new MomoAdvance event

```python
from db_manager import get_db_connection, record_transaction

conn = get_db_connection()
# MTN sent 13,000 to wife; only 997 available; MTN advanced 12,503
# 1. Send debit on MTN (net of available balance)
record_transaction(conn, '2026-10-06', '752', '103', 997,
                   'Transport to wife (MTN balance used)')
# 2. MomoAdvance covers shortfall: liability increases, MTN credited
record_transaction(conn, '2026-10-06', '303', '103', 12503,
                   'MomoAdvance auto-coverage shortfall')
conn.commit()
conn.close()
```

## Recording a MomoAdvance clearance

```python
from db_manager import get_db_connection, record_transaction

conn = get_db_connection()
# 20,000 received; MTN auto-deducted 13,360 to clear advance
record_transaction(conn, '2026-10-06', '103', '651', 20000,
                   'Received from James Katana')
record_transaction(conn, '2026-10-06', '103', '303', 13360,
                   'MomoAdvance auto-repayment cleared')
conn.commit()
conn.close()
```

Then run `clearance-verification` checklist.

## Red flags

- Account 303 credit balance > 12,000 → flag: "MomoAdvance nearly at limit; headroom < 2,000"
- Account 303 credit balance = 14,000 → flag: "MomoAdvance limit reached; no further advance available"
- Account 303 balance owed for > 7 days → flag: "MomoAdvance overdue"
- MomoAdvance balance > 30% of monthly revenue → flag: "Exceeds safe borrowing threshold"
