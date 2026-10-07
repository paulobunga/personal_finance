---
name: income-tracker
description: Monitor income sources from the database, compute totals per period, identify income gaps, and flag sessions with zero recent income. Use at the start of each financial analysis session.
---

# Income tracker

## Database
All data lives in `financial.db`. Income is recorded in journal entries against revenue accounts (651 Personal Income, 652 Transfer Income, 601 Feza Sales, 602 Business Income).

## How to read income data

```python
from db_manager import get_db_connection
import sqlite3

conn = get_db_connection()
cursor = conn.cursor()

# All income this month
cursor.execute("""
    SELECT a.account_code, a.name,
           COALESCE(SUM(je.credit),0) - COALESCE(SUM(je.debit),0) as amount
    FROM journal_entries je
    JOIN journals j ON je.journal_id = j.id
    JOIN chart_of_accounts a ON je.account_id = a.id
    JOIN account_types t ON a.account_type_id = t.id
    WHERE t.category = 'revenue'
      AND strftime('%Y-%m', j.date) = strftime('%Y-%m','now')
    GROUP BY a.id
""")
for row in cursor.fetchall():
    print(row)
conn.close()
```

## Standard computations

- **Total income this month** — filter `journals.date` in current calendar month, sum credits on revenue accounts
- **Total income last 7 days** — filter `journals.date >= date('now','-7 days')`, sum credits on revenue accounts
- **Income by source** — group by `chart_of_accounts.name`
- **Personal vs business income** — group by `account_categories.name` (Personal / Business)

## Revenue account reference

| Code | Name | Category |
|------|------|----------|
| 601 | Feza Sales | Business |
| 602 | Business Income | Business |
| 651 | Personal Income | Personal |
| 652 | Transfer Income | Personal |

## Recording new income

```python
from db_manager import get_db_connection, record_transaction

conn = get_db_connection()
# Payment received to MTN (personal income)
record_transaction(conn, '2026-10-08', '103', '651', 52000,
                   'James Katana UHPAB payment')
conn.commit()
conn.close()
```

Always record income before recording the subsequent cash movement (withdrawal, transfer, etc.).

## Red flags

- Zero revenue journal entries in last 7 days → flag: "No income recorded — 7-day gap"
- Single revenue account > 90% of all income → flag: "Income concentration risk"
- Monthly revenue total < 10% of total liabilities (from `get_balance_sheet()`) → flag: "Structural deficit"

## Integration

- Invoked in step 1 of `financial-analysis` skill daily workflow
- Monthly income total referenced in `forecasting-calculations` Scenario D
- Monthly income used by `debt-repayment-scheduler` to assess available cash inflow
