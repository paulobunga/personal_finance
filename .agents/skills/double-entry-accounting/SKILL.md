---
name: double-entry-accounting
description: Record financial transactions as paired journal entries in the SQLite database. Every transaction debits one account and credits another. Use when recording any movement of money across personal or business accounts.
---

# Double-entry accounting

## Database
All data lives in `financial.db`. Use `db_manager.py` for all reads and writes.

## Chart of accounts (account codes)

### Personal — Assets (normal balance: debit)
| Code | Name |
|------|------|
| 101  | Cash Account |
| 102  | Standard Chartered Bank |
| 103  | MTN Mobile Money |
| 104  | Xeno Savings |

### Business — Assets (normal balance: debit)
| Code | Name |
|------|------|
| 201  | Business Cash |
| 202  | Business Equipment |
| 203  | Inventory |

### Personal — Liabilities (normal balance: credit)
| Code | Name |
|------|------|
| 301  | Personal Loans |
| 302  | Credit Cards |
| 303  | MomoAdvance |

### Business — Liabilities (normal balance: credit)
| Code | Name |
|------|------|
| 401  | Accounts Payable |
| 402  | Business Loans |

### Equity (normal balance: credit)
| Code | Name |
|------|------|
| 501  | Owner's Capital |
| 502  | Retained Earnings |
| 503  | Business Capital |

### Business — Revenue (normal balance: credit)
| Code | Name |
|------|------|
| 601  | Feza Sales |
| 602  | Business Income |

### Personal — Revenue (normal balance: credit)
| Code | Name |
|------|------|
| 651  | Personal Income |
| 652  | Transfer Income |

### Business — Expenses (normal balance: debit)
| Code | Name |
|------|------|
| 701  | Cost of Goods Sold |
| 702  | Rent Expense |
| 703  | Salaries Expense |
| 704  | Utilities Expense |
| 705  | Transport Expense |

### Personal — Expenses (normal balance: debit)
| Code | Name |
|------|------|
| 751  | Food Expense |
| 752  | Transport Expense |
| 753  | Health Expense |
| 754  | Education Expense |
| 755  | Misc Expense |

## Double-entry rules

- Assets: debit = increase, credit = decrease
- Liabilities: credit = increase (new debt), debit = decrease (clearance)
- Revenue: credit = increase
- Expenses: debit = increase
- Every journal must balance: total debits = total credits

## Recording a transaction

```python
from db_manager import get_db_connection, record_transaction

conn = get_db_connection()

# Cash withdrawal from MTN
# MTN decreases (credit 103), Cash increases (debit 101)
record_transaction(conn, '2026-10-07', '101', '103', 36000, 'Withdrawal from MTN to cash')

conn.commit()
conn.close()
```

## Common transaction patterns

| Event | Debit | Credit |
|-------|-------|--------|
| Income received to MTN | 103 | 651 |
| MTN withdrawal to cash | 101 | 103 |
| Cash expense (food) | 751 | 101 |
| Cash expense (transport) | 752 | 101 |
| New personal debt recorded | 755 | 301 |
| Debt cleared from cash | 301 | 101 |
| MomoAdvance taken | 303 | 103 |
| MomoAdvance cleared | 103 | 303 |
| Feza sale (cash) | 101 | 601 |
| Feza ingredient purchase | 701 | 201 |
| Business rent due | 702 | 401 |
| Chef salary due | 703 | 401 |

## Verification

```python
from db_manager import get_db_connection, verify_double_entry

conn = get_db_connection()
result = verify_double_entry(conn)
print(f"Balanced: {result['balanced']}")
print(f"Unbalanced journals: {result['unbalanced_count']}")
conn.close()
```
