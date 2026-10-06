---
name: savings-protection
description: Protect the Xeno savings reserve from full liquidation. Use before any proposal to use savings to clear debt; enforce that reason is recorded and coverage ratio stays above a safe threshold.
---

# Savings protection

## How to read the current reserve
- Open `xeno_savings.csv` — read the last `balance` row value. This is the current reserve.
- Open `summary_account.csv` — read the latest row for `Total_Assets` and `Total_Liabilities`.
- Savings coverage ratio = `xeno_savings.csv` last balance / `Total_Liabilities` (from `summary_account.csv` latest row).
- Savings as % of assets = `xeno_savings.csv` last balance / `Total_Assets`.

## Protection rules
- Do NOT fully liquidate `xeno_savings.csv` without recording explicit reason in `financial_analysis/YYYY_MM_DD.md`.
- Partial withdrawals allowed if: (a) emergency (health, school fee partial to prevent exclusion), (b) coverage ratio after withdrawal remains > 0.01 (1%), and (c) `financial_analysis/AGENT.md` rules are cited.
- If savings are used to clear debt: net worth change = 0 (assets down = liabilities down); only liquidity/savings-coverage ratio changes. Record in `.md`.
- Preferred strategy: use savings only for essential, time-sensitive obligations (school fees, health); never for discretionary venue debt.
- Rebuild savings target: once `Total_Liabilities` < 100,000, redirect 50% of cash inflow back to `xeno_savings.csv`.

## Minimum safe threshold
- Coverage ratio floor: 1% (`xeno_savings.csv` balance / `Total_Liabilities` >= 0.01).
- If a proposed withdrawal would breach 1%, flag and require explicit written justification in the daily `.md` file before proceeding.
