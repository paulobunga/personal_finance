---
name: savings-protection
description: Protect the savings reserve (`xeno_savings.csv` currently 72,201 UGX = 87% of total assets) from full liquidation. Use before any proposal to use savings to clear debt; enforce that reason is recorded and coverage ratio stays above a safe threshold.
---

# Savings protection

Current reserve: `xeno_savings.csv` — 72,201 UGX.
Current total assets: 83,195 (MTN 997 + Cash 9,000 + Bank 997 + Xeno 72,201).
Savings as % of assets: 72,201 / 83,195 ≈ 86.8%.
Coverage ratio vs liabilities: 72,201 / 2,424,000 ≈ 0.03 (3%).

Protection rules:
- Do NOT fully liquidate `xeno_savings.csv` without recording explicit reason in `financial_analysis/YYYY_MM_DD.md`.
- Partial withdrawals allowed if: (a) emergency (health, school fee partial to prevent exclusion), (b) coverage ratio after withdrawal remains > 0.01 (1%), and (c) `AGENT.md` rules are cited.
- If savings are used to clear debt: net worth change = 0 (assets down = liabilities down); only liquidity/savings-coverage ratio improves. Record in `.md`.
- Preferred strategy: use savings only for essential, time-sensitive obligations (school fees, health); never for discretionary venue debt or agent outflows.
- Rebuild savings target: once liabilities < 100,000, redirect 50% of cash inflow back to `xeno_savings.csv`.
