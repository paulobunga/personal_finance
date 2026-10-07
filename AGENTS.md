# AGENTS.md — Financial Ledger Agents
**Account Holder: Paul Obunga**

## System Architecture

This system uses a **SQLite double-entry accounting database** as the single source of truth.

| File | Purpose |
|------|---------|
| `financial.db` | Single source of truth — all financial data |
| `db_manager.py` | Python API for all reads, writes, and reports |
| `schema.sql` | Database schema (reference only — do not re-run against existing DB) |
| `migrate_to_double_entry.py` | Historical migration script (reference only) |
| `csv_archive/` | Original CSV backups (read-only reference) |
| `financial_analysis/` | Daily narrative snapshots (YYYY_MM_DD.md) |

---

## Chart of Accounts

### Personal Accounts (category: Personal)

| Code | Name | Type |
|------|------|------|
| 101 | Cash Account | Asset |
| 102 | Standard Chartered Bank | Asset |
| 103 | MTN Mobile Money | Asset |
| 104 | Xeno Savings | Asset |
| 301 | Personal Loans | Liability |
| 302 | Credit Cards | Liability |
| 303 | MomoAdvance | Liability |
| 501 | Owner's Capital | Equity |
| 502 | Retained Earnings | Equity |
| 651 | Personal Income | Revenue |
| 652 | Transfer Income | Revenue |
| 751 | Food Expense | Expense |
| 752 | Transport Expense | Expense |
| 753 | Health Expense | Expense |
| 754 | Education Expense | Expense |
| 755 | Misc Expense | Expense |

### Business Accounts — Feza Kitchen & Grill (category: Business)

| Code | Name | Type |
|------|------|------|
| 201 | Business Cash | Asset |
| 202 | Business Equipment | Asset |
| 203 | Inventory | Asset |
| 401 | Accounts Payable | Liability |
| 402 | Business Loans | Liability |
| 503 | Business Capital | Equity |
| 601 | Feza Sales | Revenue |
| 602 | Business Income | Revenue |
| 701 | Cost of Goods Sold | Expense |
| 702 | Rent Expense | Expense |
| 703 | Salaries Expense | Expense |
| 704 | Utilities Expense | Expense |
| 705 | Transport Expense | Expense |

---

## Double-Entry Rules

- Every transaction creates a journal with at least two line items: one debit, one credit.
- Total debits must always equal total credits in every journal.
- Assets: debit = increase, credit = decrease.
- Liabilities & Revenue: credit = increase, debit = decrease.
- Expenses: debit = increase.
- See `double-entry-accounting` skill for the full transaction pattern table.

---

## Working with the Database

### Reading balances
```python
from db_manager import get_db_connection, get_balance_sheet, get_income_statement
conn = get_db_connection()
bs = get_balance_sheet(conn)   # assets, liabilities, equity, net_worth
pl = get_income_statement(conn) # revenue, expenses, net_income
conn.close()
```

### Recording a transaction
```python
from db_manager import get_db_connection, record_transaction
conn = get_db_connection()
record_transaction(conn, '2026-10-08', '103', '651', 52000,
                   'Payment from James Katana UHPAB')
conn.commit()
conn.close()
```

### Verifying books are balanced
```python
from db_manager import get_db_connection, verify_double_entry
conn = get_db_connection()
result = verify_double_entry(conn)
print(result['balanced'])  # must always be True
conn.close()
```

---

## Business Context — Feza Kitchen & Grill

- **Venue**: Kitchen space rented from Club17 Management — 400,000 UGX/month (from Oct 2026)
- **Staff**:
  - Chef — 400,000 UGX/month; salary due end of each week completing a full month
  - Waitress — 38,000 UGX/week; salary due end of each working week
- **Monthly break-even**: 952,000 UGX gross profit (rent 400k + chef 400k + waitress ~152k)
- **Personal income from Feza**: Profit withdrawals recorded as Dr 101 / Cr 601 then Dr 101 / Cr 651

---

## Financial Periods

| Period | Start | End | DB period_id |
|--------|-------|-----|-------------|
| October 2026 | 2026-10-01 | 2026-10-31 | 1 |

Add new periods to `financial_periods` table at the start of each month.

---

## Active Agents / Tracks

| Track | Accounts | Skill |
|-------|----------|-------|
| MTN Mobile Money | 103, 303 | `momo-advance-tracker` |
| Cash Pocket | 101 | `double-entry-accounting` |
| Xeno Savings | 104 | `savings-protection` |
| Personal Liabilities | 301, 302, 303 | `debt-repayment-scheduler`, `clearance-verification` |
| Business Operations | 201, 401, 601, 701–705 | `feza-business-tracker` |
| Income Tracking | 601, 602, 651, 652 | `income-tracker` |
| Rent Obligations | 702, 401, 301 | `rent-obligation-tracker` |
| Forecasting | all accounts | `forecasting-calculations` |
| Daily Analysis | all accounts | `financial-analysis` |

---

## Skills (`.agents/skills/`)

| Skill | Purpose |
|-------|---------|
| `double-entry-accounting` | Transaction recording — account codes and journal patterns |
| `financial-analysis` | Daily analysis workflow — DB queries, snapshot creation, red flags |
| `income-tracker` | Income monitoring across revenue accounts |
| `feza-business-tracker` | Feza P&L, break-even, best-sellers, expense analysis |
| `momo-advance-tracker` | MomoAdvance limit, headroom, clearance recording |
| `savings-protection` | Xeno savings guard rules and coverage ratio enforcement |
| `clearance-verification` | Debt clearance checklist before balance sheet snapshot |
| `debt-repayment-scheduler` | Priority order for debt payments given limited cash |
| `rent-obligation-tracker` | Recurring rent forecasting — personal and business |
| `forecasting-calculations` | Ratios, scenarios, net worth projections |

---

## Daily Analysis Workflow

1. Run `financial-analysis` skill — queries DB, generates `financial_analysis/YYYY_MM_DD.md`.
2. Check red flags (cash < 5k, MTN negative, MomoAdvance headroom, 7-day income gap).
3. Run `verify_double_entry(conn)` — confirm books are balanced.
4. Call `create_balance_sheet_snapshot(conn, period_id=1)` to record end-of-day state.
5. Review `debt-repayment-scheduler` output for payment priority.
6. Never write journals for planned-but-not-yet-executed payments.

---

## Rules

- `financial.db` is the single source of truth. Never edit CSV files — they are archived backups only.
- Every money movement requires a journal entry with balanced debits and credits.
- Income must be journaled before the subsequent cash movement that follows it.
- Savings (account 104) must not be fully liquidated without a written reason in the daily `.md`.
- Upcoming obligations (future rent, salary due dates) must be noted in `financial_analysis/YYYY_MM_DD.md` even before journals are written.
- Net worth = Total Assets − Total Liabilities. Negative = insolvency state.
- Business obligations (401, 702, 703) are tracked separately from personal (301, 302, 303).
