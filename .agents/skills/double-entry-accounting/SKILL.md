---
name: double-entry-accounting
description: Double-entry bookkeeping with paired debit/credit entries, running balances per account, and a combined net-worth summary. Use when recording transactions across MTN, Cash, Bank, Savings, and Liabilities ledgers.
---

# Double-entry accounting

## Account map
Each `.csv` file is one account ledger:
- `mtn_mobile_money.csv` — MTN Mobile Money (asset)
- `cash_account.csv` — Cash Pocket (asset)
- `bank_account.csv` — Standard Chartered Bank (asset)
- `xeno_savings.csv` — Xeno Savings (asset)
- `liabilities.csv` — All debts (liability; running balance increases with new debt, decreases with clearance)
- `income.csv` — Income sources (revenue)
- `summary_account.csv` — Combined net worth statement (Paul Obunga — personal finances)

## Double-entry rules
- Every transaction touches at least two accounts.
- Asset accounts: debit = increase, credit = decrease.
- Liability accounts: credit = increase (new debt), debit = decrease (clearance).

**Example — cash withdrawal from MTN:**
- Credit `mtn_mobile_money.csv` (MTN balance decreases; debit column entry)
- Debit `cash_account.csv` (cash increases; credit column entry)

**Example — new debt recorded (no cash moved yet):**
- Credit `liabilities.csv` (liability increases; new row with updated running balance)
- No asset entry until cash is actually paid out

**Example — debt clearance paid from cash:**
- Debit `liabilities.csv` (clearance row; running balance decreases by cleared amount)
- Credit `cash_account.csv` (cash decreases; debit column entry)

**Example — income received:**
- Debit `cash_account.csv` or asset account (asset increases; credit column entry)
- Record in `income.csv` (canonical income record)

## Running balance rule
- Each row in every `.csv` must have a `balance` value = previous row's `balance` ± this transaction.
- `liabilities.csv` last row `balance` must equal `summary_account.csv` latest `Total_Liabilities`.
- `summary_account.csv` `Net_Worth` = `Total_Assets` − `Total_Liabilities`.

## Verification procedure per session
1. Read last `balance` row from each asset `.csv` (`mtn_mobile_money`, `cash_account`, `bank_account`, `xeno_savings`); sum = `Total_Assets`.
2. Read last `balance` row from `liabilities.csv` = `Total_Liabilities`.
3. Compute Net Worth = Total_Assets − Total_Liabilities.
4. Compare to `summary_account.csv` latest row — all three values must match.
5. If mismatch: re-trace running balances row by row in the mismatched file to find the break.
