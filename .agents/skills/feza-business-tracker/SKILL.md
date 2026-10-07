---
name: feza-business-tracker
description: Track Feza Kitchen & Grill daily sales, expenses, and profit/loss using the SQLite database. Use when recording new sales or purchases, computing daily/weekly/monthly P&L, analyzing best-selling items, flagging loss days, and projecting whether business revenue covers operating costs.
---

# Feza Kitchen & Grill — Business Tracker

## Database
All data lives in `financial.db`. Business accounts:

| Code | Account | Type |
|------|---------|------|
| 201  | Business Cash | Asset |
| 401  | Accounts Payable | Liability |
| 601  | Feza Sales | Revenue |
| 701  | Cost of Goods Sold | Expense |
| 702  | Rent Expense | Expense |
| 703  | Salaries Expense | Expense |
| 704  | Utilities Expense | Expense |
| 705  | Transport Expense | Expense |

## Recording a new trading day

```python
from db_manager import get_db_connection, record_transaction

conn = get_db_connection()

# Record sales — Dr Business Cash (201), Cr Feza Sales (601)
record_transaction(conn, '2026-09-10', '201', '601', 47000, 'Feza daily sales 10 Sep')

# Record expenses — Dr COGS (701), Cr Business Cash (201)
record_transaction(conn, '2026-09-10', '701', '201', 17000, 'Chicken ingredient')
record_transaction(conn, '2026-09-10', '701', '201', 1000,  'Matooke')
record_transaction(conn, '2026-09-10', '705', '201', 6000,  'Ingredient transport')

conn.commit()
conn.close()
```

## Standard computations

### Daily P&L query

```python
from db_manager import get_db_connection
import sqlite3

conn = get_db_connection()
cursor = conn.cursor()

date = '2026-09-10'

cursor.execute("""
    SELECT
        SUM(CASE WHEN a.account_code = '601' THEN je.credit ELSE 0 END) as sales,
        SUM(CASE WHEN a.account_code IN ('701','702','703','704','705') THEN je.debit ELSE 0 END) as expenses
    FROM journal_entries je
    JOIN chart_of_accounts a ON je.account_id = a.id
    JOIN journals j ON je.journal_id = j.id
    WHERE j.date = ?
""", (date,))
row = cursor.fetchone()
print(f"Sales: {row[0]:,.0f}  Expenses: {row[1]:,.0f}  Gross Profit: {(row[0] or 0)-(row[1] or 0):,.0f}")
conn.close()
```

### Monthly P&L

Filter `journals.date` by `strftime('%Y-%m', date) = '2026-09'`. Sum credits on 601 for revenue, sum debits on 701–705 for expenses.

### Best-selling items

Query `feza_business` table (sales records) grouped by `item`, order by `total DESC`.

### Break-even analysis

| Fixed cost | UGX/month |
|------------|-----------|
| Kitchen rent (Club17) | 400,000 |
| Chef salary | 400,000 |
| Waitress salary | ~152,000 |
| **Monthly break-even** | **952,000** |

Weekly pace needed: 952,000 / 4 = **238,000 UGX gross profit/week**.

## Transferring profit to personal finances

When Paul Obunga withdraws cash from Feza profit:

```python
# Dr Cash (101) — personal cash increases
# Cr Business Cash (201) — business cash decreases
record_transaction(conn, '2026-10-07', '101', '201', amount,
                   'Feza profit withdrawal to personal cash')
# Also record as personal income
record_transaction(conn, '2026-10-07', '101', '651', amount,
                   'Feza Kitchen & Grill income')
```

## Red flags

- Daily gross profit < 0 → flag: "Loss day — expenses exceed sales"
- Weekly gross profit < 238,000 → flag: "Below break-even pace"
- Monthly gross profit < 952,000 → flag: "Business not covering fixed operating costs"
- No sales journals on account 601 for 2+ consecutive days → flag: "Trading gap — verify kitchen is operational"
- Single expense journal > 40% of daily total expenses → flag: "High cost concentration"
