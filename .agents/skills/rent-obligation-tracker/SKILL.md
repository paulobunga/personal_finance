---
name: rent-obligation-tracker
description: Track recurring rent obligations for both personal (home) and business (Feza Kitchen & Grill). Use when forecasting monthly liability growth from unpaid rent.
---

# Rent obligation tracker

## Database
All data lives in `financial.db`. Rent is tracked through:
- **Personal rent**: journals crediting account 301 (Personal Loans), narration contains "rent"
- **Business rent**: journals crediting account 401 (Accounts Payable), expense account 702 (Rent Expense)

## How to read current rent obligations

```python
from db_manager import get_db_connection
import sqlite3

conn = get_db_connection()
cursor = conn.cursor()

# Total outstanding on business rent expense account
cursor.execute("""
    SELECT COALESCE(SUM(je.debit),0) - COALESCE(SUM(je.credit),0) as balance
    FROM journal_entries je
    JOIN chart_of_accounts a ON je.account_id = a.id
    WHERE a.account_code = '702'
""")
business_rent = cursor.fetchone()[0]

# Total outstanding on personal loans (rent component — filter by narration)
cursor.execute("""
    SELECT COALESCE(SUM(je.credit),0) - COALESCE(SUM(je.debit),0) as balance
    FROM journal_entries je
    JOIN chart_of_accounts a ON je.account_id = a.id
    JOIN journals j ON je.journal_id = j.id
    WHERE a.account_code = '301'
      AND (j.description LIKE '%rent%' OR j.description LIKE '%Rent%')
""")
personal_rent = cursor.fetchone()[0]
conn.close()

print(f"Business rent outstanding: {business_rent:,.0f}")
print(f"Personal rent outstanding: {personal_rent:,.0f}")
```

## Monthly rates (as of Oct 2026)

| Obligation | Monthly Rate (UGX) | Account |
|------------|-------------------|---------|
| Home rent (Landlord) | 800,000 | 301 |
| Feza Kitchen rent (Club17 Management) | 400,000 | 401 / 702 |
| **Total monthly rent** | **1,200,000** | |

## Forecasting monthly growth

If nothing is paid, each month adds 1,200,000 UGX to total liabilities.

Formula: `Projected liabilities at +N months = total_liabilities + (1,200,000 × N)`

## Recording a new month's rent

```python
from db_manager import get_db_connection, record_transaction

conn = get_db_connection()
# Business rent due for November
record_transaction(conn, '2026-11-01', '702', '401', 400000,
                   'Feza Kitchen rent — November 2026')
# Personal home rent due for November
record_transaction(conn, '2026-11-01', '755', '301', 800000,
                   'Home rent — November 2026')
conn.commit()
conn.close()
```

## Rules

- Rent is recurring; unlike one-time social debt, unpaid rent leads to eviction or venue loss risk.
- Treat rent as essential after school fees in `debt-repayment-scheduler`.
- Partial payments: even partial amounts slow accumulation. Record partial clearance journals immediately when cash moves.
- Note negotiation status in `financial_analysis/YYYY_MM_DD.md`.
