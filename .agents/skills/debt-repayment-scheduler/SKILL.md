---
name: debt-repayment-scheduler
description: Prioritize debt payments given limited assets vs large liabilities. Use when net worth is negative and multiple creditors compete for small cash reserves.
---

# Debt repayment scheduler

## How to read current state
- Open `liabilities.csv` — read all rows where `status` = `owed`. Group by `category`.
- Open `summary_account.csv` — read latest row for `Balance_Cash`, `MTN_MobileMoney`, `Xeno_Savings`, `Total_Assets`, `Total_Liabilities`.
- Open `income.csv` — sum `amount` for the current month to estimate available inflow.

## Priority order
Apply in this sequence — do not pay lower priority until higher is addressed:

1. **Essential / time-sensitive** — `category = school` in `liabilities.csv`; sort by `due_date` ascending. Affects child access to education.
2. **Fee-bearing / service-blocking** — any debt that incurs recurring fees or blocks account access. Check `mtn_mobile_money.csv` for negative balance rows (overdraft/MomoAdvance).
3. **Recurring obligations (rent)** — `category = rent`; grows monthly. Check `due_date`; forecast monthly growth if unpaid using `rent-obligation-tracker` skill.
4. **Salary obligations** — `category = salary`; ethical obligation to domestic workers; treat as near-essential.
5. **Social / venue debt** — `category = social`; discretionary; freeze new spending here until priorities 1–4 addressed.
6. **Personal loans** — `category = loan`; informal; negotiate restructuring before full repayment.

## Procedure per session
1. Read `liabilities.csv` — filter `status = owed`; sort by `due_date` ascending, then by priority category.
2. Read `Balance_Cash` from `summary_account.csv` latest row.
3. Read `xeno_savings.csv` last balance.
4. Propose payments in priority order that do NOT fully liquidate savings (defer to `savings-protection` skill for threshold check).
5. Record planned payments as notes in `financial_analysis/YYYY_MM_DD.md` — do NOT alter `.csv` balances until cash actually moves.
6. After payment executes: run `clearance-verification` checklist before updating `summary_account.csv`.
