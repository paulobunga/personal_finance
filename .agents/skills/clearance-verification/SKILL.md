---
name: clearance-verification
description: Ensure every liability clearance is verified in both liabilities.csv and a dated .md file before summary_account.csv is updated. Prevents phantom reductions in net liability totals.
---

# Clearance verification

## Verification checklist
Complete all steps before updating `summary_account.csv`:

1. `liabilities.csv` contains the original debt entry (creditor, amount, running balance before clearance).
2. `liabilities.csv` contains a clearance row for the same creditor/description with:
   - `amount` = negative of cleared value
   - `balance` = previous running balance − cleared amount
   - `status` = `paid in full` or `cleared`
3. `financial_analysis/YYYY_MM_DD.md` (date of clearance event) records: creditor, original amount, cleared amount, date of clearance, confirmation that books updated.
4. `summary_account.csv` new row `Total_Liabilities` = previous `Total_Liabilities` − cleared amount.
5. Net worth improves by cleared amount (assets unchanged, liabilities down).

## How to compute post-clearance net worth
- New Net Worth = previous Net Worth + cleared amount
- Verify: new `summary_account.csv` `Net_Worth` = `Total_Assets` − new `Total_Liabilities`

## Running balance arithmetic rule
- Each new debt row: `balance` = previous row's `balance` + `amount`
- Each clearance row: `balance` = previous row's `balance` − cleared amount
- Final row's `balance` in `liabilities.csv` must equal `Total_Liabilities` in `summary_account.csv` latest row
- If there is a mismatch: re-trace row by row from the top of `liabilities.csv` to find the break
