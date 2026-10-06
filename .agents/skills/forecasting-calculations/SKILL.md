---
name: forecasting-calculations
description: Forecast future net worth from current assets/liabilities, project debt accumulation, compute savings-to-debt ratios, and estimate when liabilities will exceed assets further. Use when planning repayment order, modeling clearance impact, or comparing debt-to-asset ratios.
---

# Forecasting and calculations

Inputs: all `.csv` ledgers in root and `summary_account.csv`.

Standard calculations:
- Assets = MTN + Cash + Bank + Xeno (from `summary_account.csv` or sum of last balances)
- Liabilities = last running balance in `liabilities.csv`
- Net Worth = Assets − Liabilities
- Debt-to-Asset Ratio = Liabilities / Assets (current: 2,424,000 / 83,195 ≈ 29.1 → 29:1 liability-to-asset exposure)
- Savings Coverage = Xeno / Liabilities (current: 72,201 / 2,424,000 ≈ 0.03 → savings cover 3% of debt)
- Per-creditor share = individual liability / total liabilities (e.g. Landlord 1,600,000 = 66% of debt)

Forecasting rules (from current trajectory):
- Without new income or clearance, liabilities grow faster than assets.
- Each clearance (e.g. UG Plastic 7,000) reduces liabilities by that amount: model as new liabilities = current liabilities − clearance.
- If savings are protected (not liquidated), net improvement = clearance amount only.
- If savings are used to clear debt, net change = −clearance (assets down) − clearance (liabilities down) = 0 net improvement on net worth, but improves liquidity/savings-coverage ratio.
- Rent obligations repeat monthly; forecast monthly liability growth = 1,600,000 (Sept + Oct) per cycle if unpaid.

Output format: add a forecast section to `financial_analysis/YYYY_MM_DD.md` with ratios and projected net worth after modeled events.
