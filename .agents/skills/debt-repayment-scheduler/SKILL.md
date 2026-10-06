---
name: debt-repayment-scheduler
description: Prioritize debt payments given limited assets vs large liabilities. Use when net worth is negative and multiple creditors compete for small cash reserves (e.g. school fees 195k, MomoAdvance 13.6k, Club17 9k, landlord 1.6M, personal loans 620k against 83,195 assets).
---

# Debt repayment scheduler

Priority order (from current `liabilities.csv` and `summary_account.csv`):

1. Essential / time-sensitive: School fees (Britney 50k + Beverly 145k = 195k) — affects access; date-sensitive.
2. Fee-bearing / service-blocking: MTN MomoAdvance (13,613 + 1,390 fee recorded) — blocks mobile-money use; recurring fee exposure.
3. Recurring obligations: Landlord rent (Sept 800k + Oct 800k = 1,600k) — grows monthly; prevents eviction risk.
4. Venue/social: Club17 (Sodas 4k + Tusker 5k = 9k after UG Plastic 7k clearance) — discretionary; freeze until 1–3 covered.
5. Large personal loans: Patricia 100k, Remmy 220k, Ahmed 300k (620k total) — informal; negotiate restructuring before full repayment.
6. Agent pending: Leuben/Askari 1,500 — verify before counting as cleared.

Procedure per session:
- Read `liabilities.csv` running balance.
- Read `cash_account.csv` remaining cash (currently 9,000) and `xeno_savings.csv` (72,201).
- Propose payments in priority order that do NOT fully liquidate savings (protect per `savings-protection` skill).
- Record planned payments as notes in `financial_analysis/YYYY_MM_DD.md` but do NOT alter `.csv` balances until cash actually moves.
