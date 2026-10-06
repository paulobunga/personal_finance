---
name: momo-advance-tracker
description: Track MTN MomoAdvance limit, current amount owed, and remaining borrowing headroom. Use whenever a MomoAdvance is taken, repaid, or the limit changes — and to answer "how much more can I borrow?".
---

# MomoAdvance tracker

## Where the data lives
- **Current limit**: read the most recent `MomoAdvance limit` row in `mtn_mobile_money.csv` (description contains "MomoAdvance limit"). This is the ceiling MTN allows.
- **Current owed**: read the most recent negative balance in `mtn_mobile_money.csv`, OR sum all uncleared MomoAdvance rows in `liabilities.csv` where `creditor = MTN MomoAdvance` and `status = owed`.
- **Remaining headroom** = Limit − Current owed (if result is negative, limit is exhausted).

## Key computations
- **Remaining headroom** = `MomoAdvance limit` − sum of `liabilities.csv` rows where `creditor = MTN MomoAdvance` and `status = owed`
- **MTN effective balance** = last `balance` row in `mtn_mobile_money.csv` (negative = MomoAdvance in use)
- **Repayment amount needed to clear** = same as current owed (MomoAdvance is cleared in full by next MTN receipt)

## How MomoAdvance works in this system
- MTN uses available MTN balance first, then auto-advances the shortfall up to the limit.
- The advance is not a separate borrowing event — it is automatically triggered when a send/payment exceeds available balance.
- Amount advanced = total transaction cost (send amount + fee) − MTN balance available at time of transaction.
- The full advance is due on the next significant MTN receipt (MTN auto-deducts).
- The limit may increase over time as MTN adjusts based on usage history.

## Recording a new MomoAdvance event
1. In `mtn_mobile_money.csv` add rows for:
   - The send/payment (debit)
   - The transaction fee (debit)
   - The MomoAdvance auto-coverage (credit entry showing amount MTN advanced; balance goes negative)
2. In `liabilities.csv` add a new row:
   - `creditor` = MTN MomoAdvance
   - `amount` = advanced amount (limit used)
   - `balance` = previous running balance + advanced amount
   - `status` = owed
   - `category` = loan
   - `due_date` = next expected MTN receipt date (or leave blank if unknown)
3. Update `summary_account.csv` with new MTN balance (negative) and new Total_Liabilities.

## Recording a MomoAdvance clearance
1. In `mtn_mobile_money.csv` add a row showing the incoming receipt and note "auto-deducted MomoAdvance XXXX".
2. In `liabilities.csv` add a clearance row:
   - `amount` = −(owed amount)
   - `balance` = previous running balance − cleared amount
   - `status` = paid in full
3. Run `clearance-verification` checklist.
4. Update `summary_account.csv`.

## Recording a limit change
- Add a row to `mtn_mobile_money.csv`:
  - `description` = MomoAdvance limit updated to XXXXX
  - `debit` and `credit` = 0
  - `balance` = unchanged (limit change is not a transaction)
  - `note` = new limit value

## Red flags
- Remaining headroom < 2,000 UGX → flag: "MomoAdvance nearly exhausted; limit XXXXX; owed XXXXX; headroom XXXXX"
- Headroom = 0 → flag: "MomoAdvance limit reached; no further advance available until cleared"
- MomoAdvance owed for > 7 days → flag: "MomoAdvance overdue; clear on next MTN receipt to avoid fee escalation"
- MomoAdvance owed > 30% of monthly income (from `income.csv`) → flag: "MomoAdvance exceeds safe borrowing threshold relative to income"

## Current state template (fill in each session)
- Limit: read from `mtn_mobile_money.csv` latest limit row
- Owed: sum `liabilities.csv` where `creditor = MTN MomoAdvance` and `status = owed`
- Remaining headroom: Limit − Owed
- MTN effective balance: last `balance` in `mtn_mobile_money.csv`
