---
name: agent-pending-tracker
description: Track unverified agent outflows (e.g. Leuben/Askari 1,500 UGX for ORIS) until delivery/confirmation is recorded. Use when cash_account shows a handoff with no matching asset or receipt entry.
---

# Agent pending tracker

Trigger: any `cash_account.csv` entry with note containing "Given to" / agent name / unverified outflow (e.g. `Leuben (Askari) for ORIS, 1500`).

Procedure:
1. Create or update a tracking note in `financial_analysis/YYYY_MM_DD.md`: agent name, amount, purpose, date given, expected outcome.
2. Do NOT reduce liabilities or count as expense until confirmation (delivery receipt, product confirmation, agent acknowledgment) is recorded.
3. If no confirmation after 30 days: treat as probable loss; recommend recording as confirmed expense in `cash_account.csv` with note `unverified — probable loss`.
4. Never rely solely on agent memory; require a second `.csv` entry or `.md` confirmation line before closing.

Current pending (from `cash_account.csv`):
- 2026-10-05: Given to Leuben (Askari) for ORIS — 1,500 UGX — no confirmation file.
