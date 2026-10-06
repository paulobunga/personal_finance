---
name: rent-obligation-tracker
description: Track recurring rent obligations separately from one-time debts. Use when landlord debts accumulate (e.g. Sept 800k + Oct 800k) and monthly liability growth must be forecasted separately from one-time venue/loan debt.
---

# Rent obligation tracker

Input: `liabilities.csv` entries with creditor = Landlord.

Current state (2026-10-05):
- September Rent (unpaid): 800,000
- October Rent (unpaid): 800,000
- Running liability contribution from rent: 1,600,000 (66% of total 2,424,000 liabilities)

Rules:
- Rent is recurring; forecast monthly liability growth = 800,000 if unpaid.
- Unlike one-time Club17 debt (freezeable), rent accumulation leads to eviction risk; treat as essential after school fees.
- Record each new month's rent as new line in `liabilities.csv` with running balance added.
- Suggest in `financial_analysis/YYYY_MM_DD.md`: part-payments (even 200k–300k) to slow accumulation, or negotiation note.
