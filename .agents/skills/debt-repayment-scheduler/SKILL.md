---
name: debt-repayment-scheduler
description: Prioritize debt payments given limited assets vs large liabilities. Use when net worth is negative and multiple creditors compete for small cash reserves.
---

# Debt repayment scheduler

## Database
All data lives in `financial.db`. Use `db_manager.py` for reads.

## How to read current state

```python
from db_manager import get_db_connection, get_balance_sheet
import sqlite3

conn = get_db_connection()
cursor = conn.cursor()

# All outstanding liabilities grouped by account
cursor.execute("""
    SELECT a.account_code, a.name,
           COALESCE(SUM(je.credit),0) - COALESCE(SUM(je.debit),0) as balance
    FROM chart_of_accounts a
    JOIN account_types t ON a.account_type_id = t.id
    LEFT JOIN journal_entries je ON a.id = je.account_id
    WHERE t.category = 'liability'
    GROUP BY a.id
    ORDER BY balance DESC
""")
liabilities = cursor.fetchall()

# Current liquid assets
cursor.execute("""
    SELECT a.account_code, a.name,
           COALESCE(SUM(je.debit),0) - COALESCE(SUM(je.credit),0) as balance
    FROM chart_of_accounts a
    JOIN account_types t ON a.account_type_id = t.id
    LEFT JOIN journal_entries je ON a.id = je.account_id
    WHERE t.category = 'asset' AND a.account_code IN ('101','102','103')
    GROUP BY a.id
""")
liquid_assets = cursor.fetchall()

# Monthly revenue
cursor.execute("""
    SELECT COALESCE(SUM(je.credit),0) - COALESCE(SUM(je.debit),0) as monthly_income
    FROM journal_entries je
    JOIN chart_of_accounts a ON je.account_id = a.id
    JOIN account_types t ON a.account_type_id = t.id
    WHERE t.category = 'revenue'
    AND strftime('%Y-%m', (SELECT date FROM journals WHERE id = je.journal_id)) = strftime('%Y-%m','now')
""")
monthly_income = cursor.fetchone()[0]
conn.close()
```

## Priority order

Apply in this sequence — do not pay lower priority until higher is addressed:

1. **Essential / time-sensitive** — Education (account 754 expense history; cross-ref liabilities for school fees). Affects child access to education.
2. **Fee-bearing / service-blocking** — MomoAdvance (account 303). Incurs fees daily when outstanding; invoke `momo-advance-tracker`.
3. **Recurring rent** — Business rent (account 702 / 401) and personal rent (account 301 rent-category journals). Grows monthly; invoke `rent-obligation-tracker`.
4. **Salary obligations** — Business staff (account 703 / 401) and personal (maid — account 301). Ethical obligation.
5. **Social / venue debt** — Small social debts (account 301 social-category). Discretionary; freeze new spending until 1–4 addressed.
6. **Personal loans** — Informal loans (account 301 loan-category). Negotiate restructuring before full repayment.

## Procedure per session

1. Query liabilities as above; sort by balance descending.
2. Check liquid assets (accounts 101, 102, 103).
3. Check Xeno Savings (account 104) — invoke `savings-protection` before proposing any use of savings.
4. Propose payments in priority order that do NOT fully liquidate savings.
5. Record planned payments as notes in `financial_analysis/YYYY_MM_DD.md` — do NOT write journals until cash actually moves.
6. After payment executes: run `clearance-verification` checklist, then write the clearance journal.
