#!/usr/bin/env python3
"""
Migrate CSV data to Double-Entry Accounting System
Converts existing CSV data to proper journal entries with paired debit/credit.
"""

import csv
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "financial.db"
CSV_DIR = Path(__file__).parent


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def get_account_id(conn, account_code):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM chart_of_accounts WHERE account_code = ?", (account_code,))
    result = cursor.fetchone()
    return result[0] if result else None


def create_journal(conn, date, description, journal_number=None):
    """Create a new journal entry and return its ID."""
    cursor = conn.cursor()
    if journal_number is None:
        cursor.execute("SELECT COALESCE(MAX(journal_number), 0) + 1 FROM journals")
        journal_number = cursor.fetchone()[0]
    
    cursor.execute("""
        INSERT INTO journals (journal_number, date, description, total_debit, total_credit)
        VALUES (?, ?, ?, 0, 0)
    """, (journal_number, date, description))
    return cursor.lastrowid


def add_journal_entry(conn, journal_id, account_id, debit, credit, narration=None):
    """Add a line item to a journal entry."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO journal_entries (journal_id, account_id, debit, credit, narration)
        VALUES (?, ?, ?, ?, ?)
    """, (journal_id, account_id, float(debit), float(credit), narration))
    
    # Update journal totals
    cursor.execute("""
        UPDATE journals 
        SET total_debit = total_debit + ?, total_credit = total_credit + ?
        WHERE id = ?
    """, (float(debit), float(credit), journal_id))


def record_transaction(conn, date, debit_account_code, credit_account_code, 
                       amount, narration=None, reference=None, journal_number=None):
    """Record a double-entry transaction (debit one account, credit another)."""
    debit_account_id = get_account_id(conn, debit_account_code)
    credit_account_id = get_account_id(conn, credit_account_code)
    
    if not debit_account_id:
        raise ValueError(f"Debit account {debit_account_code} not found")
    if not credit_account_id:
        raise ValueError(f"Credit account {credit_account_code} not found")
    
    journal_id = create_journal(conn, date, narration or f"Transaction on {date}", journal_number)
    add_journal_entry(conn, journal_id, debit_account_id, amount, 0, narration)
    add_journal_entry(conn, journal_id, credit_account_id, 0, amount, narration)
    
    return journal_id


def migrate_cash_account(conn):
    """Migrate cash_account.csv - all debits/credits are cash movements."""
    print("Migrating cash_account.csv...")
    
    # Read all transactions
    with open(CSV_DIR / "cash_account.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Determine transaction type
            amount = float(row['debit']) if row['debit'] else float(row['credit'])
            is_debit = bool(row['debit'])
            
            # Determine source/destination account
            if is_debit:  # Debit = cash received
                # Cash increased, source decreased
                if row['category'] == 'income':
                    # Income received in cash
                    # Debit: Cash, Credit: Personal Income
                    record_transaction(
                        conn, row['date'],
                        '101', '651',  # Cash, Personal Income
                        amount,
                        f"Income: {row['description']}"
                    )
                else:
                    # Cash withdrawal from another account (MTN or Bank)
                    # Debit: Cash, Credit: MTN/Bank
                    record_transaction(
                        conn, row['date'],
                        '101', '103',  # Cash, MTN
                        amount,
                        f"Withdrawal: {row['description']}"
                    )
            else:  # Credit = cash spent
                # Cash decreased, expense increased
                # Debit: Expense, Credit: Cash
                expense_account = f"75{row['category'][:1]}" if row['category'] else '755'
                # Map categories to expense accounts
                category_map = {
                    'food': '751', 'transport': '752', 'health': '753',
                    'school': '754', 'expense': '755', 'debt_clearance': '301'
                }
                exp_acc_code = category_map.get(row['category'], '755')
                record_transaction(
                    conn, row['date'],
                    exp_acc_code, '101',  # Expense, Cash
                    amount,
                    row['description']
                )


def migrate_bank_account(conn):
    """Migrate bank_account.csv."""
    print("Migrating bank_account.csv...")
    
    with open(CSV_DIR / "bank_account.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['credit']:
                amount = float(row['credit'])
                record_transaction(
                    conn, row['date'],
                    '102', '651',  # Bank, Personal Income
                    amount,
                    row['description']
                )
            if row['debit']:
                amount = float(row['debit'])
                record_transaction(
                    conn, row['date'],
                    '755', '102',  # Expense, Bank
                    amount,
                    row['description']
                )


def migrate_mtn_mobile_money(conn):
    """Migrate mtn_mobile_money.csv with proper asset/liability tracking."""
    print("Migrating mtn_mobile_money.csv...")
    
    with open(CSV_DIR / "mtn_mobile_money.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            amount = float(row['debit']) if row['debit'] else float(row['credit'])
            is_debit = bool(row['debit'])
            desc = row['description']
            
            # Check if this is a MomoAdvance liability transaction
            if 'MomoAdvance' in desc:
                if is_debit:  # MomoAdvance fee (expense)
                    record_transaction(
                        conn, row['date'],
                        '755', '103',  # Expense, MTN
                        amount,
                        desc
                    )
                else:  # MomoAdvance limit adjustment (liability)
                    record_transaction(
                        conn, row['date'],
                        '303', '103',  # MomoAdvance Liability, MTN
                        amount,
                        desc
                    )
            elif is_debit:  # Cash spent via MTN
                record_transaction(
                    conn, row['date'],
                    '755', '103',  # Expense, MTN
                    amount,
                    desc
                )
            else:  # MTN received
                record_transaction(
                    conn, row['date'],
                    '103', '651',  # MTN, Personal Income
                    amount,
                    desc
                )


def migrate_xeno_savings(conn):
    """Migrate xeno_savings.csv."""
    print("Migrating xeno_savings.csv...")
    
    with open(CSV_DIR / "xeno_savings.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['credit']:
                amount = float(row['credit'])
                record_transaction(
                    conn, row['date'],
                    '104', '651',  # Xeno Savings, Personal Income
                    amount,
                    row['description']
                )
            if row['debit']:
                amount = float(row['debit'])
                record_transaction(
                    conn, row['date'],
                    '755', '104',  # Expense, Xeno Savings
                    amount,
                    row['description']
                )


def migrate_income(conn):
    """Migrate income.csv - already in cash where received."""
    print("Migrating income.csv...")
    
    with open(CSV_DIR / "income.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            amount = float(row['amount'])
            record_transaction(
                conn, row['date'],
                '101', '651',  # Cash, Personal Income
                amount,
                f"Income from {row['source']}: {row['description']}"
            )


def migrate_liabilities(conn):
    """Migrate liabilities.csv - track debts."""
    print("Migrating liabilities.csv...")
    
    with open(CSV_DIR / "liabilities.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            amount = float(row['amount'])
            credit = float(row['credit'])
            balance = float(row['balance'])
            status = row['status']
            
            # Determine liability account based on category
            liability_accounts = {
                'social': '301',  # Personal loans
                'loan': '301',
                'rent': '301',  # Personal rent
                'rent_business': '401',  # Business rent
                'salary': '301',  # Personal salaries
                'salary_business': '401'  # Business salaries
            }
            liability_code = liability_accounts.get(row['category'], '301')
            
            # For paid entries (negative amounts in credit column)
            if credit > 0 and credit < amount:
                # Partial payment
                record_transaction(
                    conn, row['date'],
                    liability_code, '101',  # Liability, Cash
                    credit,
                    f"Partial payment to {row['creditor']}: {row['description']}"
                )
            elif status == 'paid in full':
                # Debt clearance
                record_transaction(
                    conn, row['date'],
                    liability_code, '101',  # Liability, Cash
                    amount,
                    f"Clearance to {row['creditor']}: {row['description']}"
                )
            elif status in ['owed', 'owed - CLEARED']:
                # New debt or existing debt
                record_transaction(
                    conn, row['date'],
                    '301', liability_code,  # Personal Liability, Specific Liability
                    amount,
                    f"New debt to {row['creditor']}: {row['description']}"
                )


def migrate_planned_expenses(conn):
    """Migrate planned_expenses.csv - create liability for future expenses."""
    print("Migrating planned_expenses.csv...")
    
    with open(CSV_DIR / "planned_expenses.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Create a liability for the planned expense
            record_transaction(
                conn, '2026-10-07',  # Today
                '301', '401',  # Personal Liability, Accounts Payable
                float(row['estimated_cost_ugx']),
                f"Planned expense: {row['item']} - {row['description']}"
            )


def migrate_savings_goals(conn):
    """Migrate savings_goals.csv."""
    print("Migrating savings_goals.csv...")
    
    with open(CSV_DIR / "savings_goals.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            saved = float(row['saved_ugx'])
            if saved > 0:
                record_transaction(
                    conn, '2026-10-05',
                    '104', '651',  # Xeno Savings, Personal Income
                    saved,
                    f"Savings goal: {row['goal']}"
                )


def migrate_feza_sales(conn):
    """Migrate feza_sales.csv - business revenue."""
    print("Migrating feza_sales.csv...")
    
    with open(CSV_DIR / "feza_sales.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total = float(row['total_ugx'])
            # Business revenue: Debit Cash/Accounts Receivable, Credit Revenue
            record_transaction(
                conn, row['date'],
                '101', '601',  # Cash, Feza Sales
                total,
                f"Feza sale: {row['item']}"
            )


def migrate_summary(conn):
    """Migrate daily_summary.csv - create balance sheet snapshots."""
    print("Migrating summary_account.csv...")
    
    with open(CSV_DIR / "summary_account.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        entry_index = {}
        for row in reader:
            date = row['date']
            entry_index[date] = entry_index.get(date, 0) + 1
            
            # Create balance sheet entry
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO balance_sheet_snapshots (period_id, snapshot_date, 
                    total_assets, total_liabilities, net_worth)
                VALUES (1, ?, ?, ?, ?)
            """, (date, 
                  float(row['Total_Assets']),
                  float(row['Total_Liabilities']),
                  float(row['Net_Worth'])))


def main():
    print(f"Starting migration to double-entry system at {datetime.now().isoformat()}")
    print(f"Database: {DB_PATH}")
    print(f"CSV Directory: {CSV_DIR}")
    print("-" * 50)
    
    conn = get_db_connection()
    
    try:
        # Clear existing data (for clean migration)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM journal_entries")
        cursor.execute("DELETE FROM journals")
        conn.commit()
        
        # Migrate transaction data
        migrate_cash_account(conn)
        migrate_bank_account(conn)
        migrate_mtn_mobile_money(conn)
        migrate_xeno_savings(conn)
        migrate_income(conn)
        migrate_liabilities(conn)
        
        # Migrate planning data
        migrate_planned_expenses(conn)
        migrate_savings_goals(conn)
        
        # Migrate business data
        migrate_feza_sales(conn)
        
        # Migrate summaries
        migrate_summary(conn)
        
        conn.commit()
        print("-" * 50)
        print("Migration completed!")
        
        # Verify
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM journals")
        print(f"Total journals: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        print(f"Total journal entries: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT SUM(debit), SUM(credit) FROM journal_entries")
        result = cursor.fetchone()
        print(f"Total debits: {result[0]}, Total credits: {result[1]}")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()