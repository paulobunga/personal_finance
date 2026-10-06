---
name: forecasting-calculations
description: Forecast future net worth, project debt accumulation, compute savings-to-debt ratios, and model scenarios. Use when planning repayment order, modeling clearance impact, or projecting future net worth.
---

# Forecasting and calculations

## How to read inputs
- Open `summary_account.csv` — use latest row for `Total_Assets`, `Total_Liabilities`, `Net_Worth`.
- Open `liabilities.csv` — filter `status = owed`; group by `category` for per-category totals.
- Open `income.csv` — sum `amount` for current month = monthly income.
- Open `xeno_savings.csv` — last `balance` row = savings reserve.

## Standard ratios
- **Debt-to-Asset Ratio** = `Total_Liabilities` / `Total_Assets` (lower is better; target < 1.0)
- **Savings Coverage Ratio** = `xeno_savings.csv` last balance / `Total_Liabilities` (target > 0.10 = 10%)
- **Monthly rent liability growth** = sum of `amount` for all `category = rent` rows added in the last 30 days (from `rent-obligation-tracker`)
- **Per-creditor share** = individual creditor's `amount` / `Total_Liabilities`

## Scenario modeling
For each scenario, compute: new `Total_Assets`, new `Total_Liabilities`, new `Net_Worth`, new `Savings Coverage Ratio`, new `Debt-to-Asset Ratio`.

**Scenario A — No income, no payments (baseline drift):**
- Each month: add monthly rent total (sum `amount` for `category = rent`, most recent month) to `Total_Liabilities`
- `Total_Assets` unchanged (no income, no spending assumed)
- Project for +1 month, +2 months, +3 months
- Formula: Net Worth at +N months = current `Net_Worth` − (monthly rent total × N)

**Scenario B — School fees cleared from Xeno savings:**
- School fees total = sum `amount` where `category = school` and `status = owed` in `liabilities.csv`
- Check: if school fees total > `xeno_savings.csv` last balance → Xeno insufficient alone; note remaining gap
- New `xeno_savings.csv` balance = current balance − amount paid toward school fees
- New `Total_Liabilities` = current − amount cleared
- Net Worth unchanged; Savings Coverage Ratio changes (compute new ratio)
- Flag: if post-withdrawal savings balance / new `Total_Liabilities` < 0.01 → breach of savings-protection threshold

**Scenario C — MomoAdvance cleared from next cash inflow:**
- MomoAdvance amount = read negative balance rows in `mtn_mobile_money.csv` (sum of overdraft + fees)
- If cash inflow >= MomoAdvance total: MTN unblocked; record clearance per `clearance-verification`
- New `Total_Liabilities` = current − MomoAdvance cleared
- Net Worth improves by cleared amount

**Scenario D — New income event:**
- Add projected income amount to `Total_Assets` (`Balance_Cash` increases by income amount)
- No change to `Total_Liabilities`
- New Net Worth = current `Net_Worth` + income amount
- New Debt-to-Asset Ratio = `Total_Liabilities` / new `Total_Assets`

## Output format
Add a `## Forecast` section to `financial_analysis/YYYY_MM_DD.md` with:
- Current ratios (Debt-to-Asset, Savings Coverage)
- Scenario A: projected net worth at +1, +2, +3 months
- Scenario B/C/D: net worth and key ratios after modeled event
- Recommendation: which scenario improves position most efficiently given available resources
