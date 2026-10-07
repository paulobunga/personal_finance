---
name: feza-business-tracker
description: Track Feza Kitchen & Grill daily sales, expenses, and profit/loss. Use when recording new sales or purchases, computing daily/weekly/monthly P&L, analyzing best-selling items, flagging loss days, and projecting whether business revenue covers operating costs (rent + staff).
---

# Feza Kitchen & Grill — Business Tracker

## Files
- `feza_sales.csv` — itemized sales (one row per sale transaction)
- `feza_expenses.csv` — daily ingredient and operating costs (one row per expense item)
- `feza_profit_loss.csv` — daily P&L summary (one row per trading day)

## Schemas

### feza_sales.csv
`date, item, quantity, unit_price_ugx, total_ugx, category, note`
- `date` — transaction date (YYYY-MM-DD)
- `item` — menu item name (e.g. Boiled Chicken, Chips & Salad, Chips & Eggs)
- `quantity` — number of units sold
- `unit_price_ugx` — price per unit
- `total_ugx` — quantity × unit_price_ugx
- `category` — food / drink / other
- `note` — optional (special order, discount, etc.)

### feza_expenses.csv
`date, item, amount_ugx, category, note`
- `date` — purchase date (YYYY-MM-DD)
- `item` — ingredient or cost item (e.g. Chicken, Matooke, Irish Potatoes, Coriander, Transport)
- `amount_ugx` — cost paid
- `category` — ingredient / transport / utilities / other
- `note` — optional (supplier, market, etc.)

### feza_profit_loss.csv
`date, total_sales_ugx, total_expenses_ugx, gross_profit_ugx, kitchen_rent_ugx, chef_salary_ugx, waitress_salary_ugx, net_profit_ugx, note`
- `gross_profit_ugx` = total_sales_ugx − total_expenses_ugx
- `kitchen_rent_ugx` — daily share of monthly rent (monthly rent / trading days in month); leave blank if tracking rent in `liabilities.csv` only
- `chef_salary_ugx` — daily share of monthly chef salary; leave blank if tracking in `liabilities.csv` only
- `waitress_salary_ugx` — daily share of weekly waitress salary; leave blank if tracking in `liabilities.csv` only
- `net_profit_ugx` = gross_profit_ugx − kitchen_rent_ugx − chef_salary_ugx − waitress_salary_ugx

## Recording a new trading day
1. Add one row per sale to `feza_sales.csv`.
2. Add one row per expense item to `feza_expenses.csv`.
3. Compute totals:
   - Total sales = sum `total_ugx` for that date in `feza_sales.csv`
   - Total expenses = sum `amount_ugx` for that date in `feza_expenses.csv`
   - Gross profit = Total sales − Total expenses
4. Add one row to `feza_profit_loss.csv` with computed totals.
5. If gross profit > 0: record net cash available for Paul Obunga withdrawal or debt service.
6. If gross profit < 0 (loss day): flag in `financial_analysis/YYYY_MM_DD.md`.

## Standard computations

### Daily P&L
- Gross profit = Total sales − Total ingredient/operating expenses
- Net profit = Gross profit − daily share of rent − daily share of staff salaries

### Weekly summary
- Total sales = sum `total_ugx` in `feza_sales.csv` for the week
- Total expenses = sum `amount_ugx` in `feza_expenses.csv` for the week
- Weekly gross profit = Total sales − Total expenses

### Monthly summary
- Monthly sales = sum `total_ugx` in `feza_sales.csv` for the month
- Monthly expenses = sum `amount_ugx` in `feza_expenses.csv` for the month
- Monthly gross profit = Monthly sales − Monthly expenses
- Monthly net profit = Monthly gross profit − kitchen rent (400,000) − chef salary (400,000) − waitress salary (~152,000 for 4 weeks)
- **Monthly break-even point** = kitchen rent + chef salary + waitress salary = **952,000 UGX/month**

### Best-selling items
- Group `feza_sales.csv` by `item`, sum `total_ugx` and `quantity` — highest revenue and volume items

### Cost analysis
- Group `feza_expenses.csv` by `item`, sum `amount_ugx` — highest cost ingredients
- Cost-to-sales ratio = Total expenses / Total sales (target < 60%; current: 27,500 / 47,000 = 58.5%)

## Business operating costs (monthly fixed costs)
| Cost | Amount (UGX/month) | Tracked in |
|---|---|---|
| Kitchen rent (Club17 Management) | 400,000 | `liabilities.csv` (rent_business) |
| Chef salary | 400,000 | `liabilities.csv` (salary_business) |
| Waitress salary | ~152,000 (38k × 4 weeks) | `liabilities.csv` (salary_business) |
| **Total fixed costs** | **~952,000** | |

## Transferring profit to personal finances
- When Paul Obunga withdraws cash from Feza Kitchen profit:
  - Record in `cash_account.csv` as credit (cash received), category = `income`
  - Record in `income.csv` as new row, source = "Feza Kitchen & Grill", category = `business`
  - Do NOT record in `feza_expenses.csv` — Paul Obunga's withdrawal is not a business expense

## Red flags
- Daily gross profit < 0 → flag: "Loss day — expenses exceed sales"
- Weekly gross profit < 238,000 (weekly share of 952k monthly fixed costs) → flag: "Below break-even pace"
- Monthly gross profit < 952,000 → flag: "Business not covering fixed operating costs"
- Single ingredient > 40% of daily expenses → flag: "High ingredient concentration risk"
- No sales recorded for 2+ consecutive days → flag: "Trading gap — verify kitchen is operational"
