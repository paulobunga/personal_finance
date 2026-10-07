---
name: forecasting-calculations
description: Forecast future net worth, project debt accumulation, compute savings-to-debt ratios, and model scenarios. Use when planning repayment order, modeling clearance impact, or projecting future net worth.
---

# Forecasting and calculations

## Database
All data lives in `financial.db`. Use `db_manager.py` functions `get_balance_sheet()` and `get_income_statement()` as the primary inputs.

## How to read inputs

```python
from db_manager import get_db_connection, get_balance_sheet, get_income_statement
import sqlite3

conn = get_db_connection()
bs  = get_balance_sheet(conn)
pl  = get_income_statement(conn)

total_assets      = bs['total_assets']
total_liabilities = bs['total_liabilities']
net_worth         = bs['net_worth']
monthly_revenue   = pl['total_revenue']

# Xeno savings
cursor = conn.cursor()
cursor.execute("""
    SELECT COALESCE(SUM(je.debit),0) - COALESCE(SUM(je.credit),0)
    FROM journal_entries je
    JOIN chart_of_accounts a ON je.account_id = a.id
    WHERE a.account_code = '104'
""")
xeno_balance = cursor.fetchone()[0]
conn.close()
```

## Standard ratios

- **Debt-to-Asset Ratio** = `total_liabilities / total_assets` (target < 1.0)
- **Savings Coverage Ratio** = `xeno_balance / total_liabilities` (target > 10%)
- **Monthly rent liability growth** = 1,200,000 UGX (home 800k + Feza 400k) — invoke `rent-obligation-tracker`
- **Monthly break-even (Feza)** = 952,000 UGX (rent 400k + chef 400k + waitress 152k)

## Scenario modeling

For each scenario compute: new assets, new liabilities, new net worth, new savings coverage, new debt-to-asset.

**Scenario A — No income, no payments (baseline drift):**
```
Net Worth at +N months = net_worth − (1,200,000 × N)
```
Project for +1, +2, +3 months.

**Scenario B — School fees cleared from Xeno savings:**
- School fees total = query `balance_sheet_snapshots` or sum liability journals with narration "school"
- If school fees > `xeno_balance`: insufficient; note gap
- New Xeno balance = `xeno_balance − fees_paid`
- New liabilities = `total_liabilities − fees_paid`
- Coverage ratio after = new Xeno / new liabilities
- Flag if post-withdrawal coverage < 1% (invoke `savings-protection`)

**Scenario C — MomoAdvance cleared from next cash inflow:**
- MomoAdvance owed = net credit balance on account 303
- If inflow ≥ MomoAdvance: MTN unblocked; record clearance journal; invoke `clearance-verification`
- New liabilities = `total_liabilities − momo_cleared`
- Net worth improves by cleared amount

**Scenario D — New income event:**
- New assets = `total_assets + projected_income`
- Liabilities unchanged
- New net worth = `net_worth + projected_income`
- New debt-to-asset = `total_liabilities / new_assets`

## Output format

Add a `## Forecast` section to `financial_analysis/YYYY_MM_DD.md`:

```
### Current ratios
- Debt-to-Asset: X.XX
- Savings Coverage: X.XX%

### Scenario A — Drift (+1/+2/+3 months)
- +1 month: Net Worth = XXX,XXX
- +2 months: Net Worth = XXX,XXX
- +3 months: Net Worth = XXX,XXX

### Scenario D — Expected income (amount)
- New Net Worth: XXX,XXX
- New Debt-to-Asset: X.XX

### Recommendation
...
```
