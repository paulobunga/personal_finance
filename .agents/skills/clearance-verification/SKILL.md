---
name: clearance-verification
description: Ensure every liability clearance (e.g. UG Plastic 7,000 cleared 6 Oct 2026) is verified in both liabilities.csv and a dated .md file before summary_account.csv is updated. Prevents phantom reductions in net liability totals.
---

# Clearance verification

Verification checklist (must complete before updating `summary_account.csv`):
1. `liabilities.csv` contains original debt entry (amount, running balance before clearance).
2. `liabilities.csv` contains clearance entry with: same creditor/description + `CLEARED` / `paid` note, amount = cleared value, new running balance = previous − cleared.
3. `financial_analysis/YYYY_MM_DD.md` (date of clearance event, e.g. 2026_10_05.md or 2026_10_07.md) records: creditor, original amount, cleared amount, date of clearance, note confirming books updated.
4. `summary_account.csv` reflects new liabilities total = previous total − cleared amount.
5. Net worth improves by cleared amount (assets unchanged, liabilities down).

Example (current):
- Original: UG 200ml Plastic 7,000 (Club17), running balance 11,000.
- Clearance entry: 7,000 cleared, running balance 824,000 (from previous 831,000 with Beverly's 145k added; check arithmetic per session).
- Confirm `summary_account.csv` row shows liabilities = 824,000 (pre-landlord) or 2,424,000 (post-landlord with clearance applied to running total correctly).
