#!/usr/bin/env python3
"""
Double-Entry Accounting Database Manager
Provides CRUD operations and reporting for the SQLite double-entry system.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


DB_PATH = Path(__file__).parent / "financial.db"


def get_db_connection():
    """Get database connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


# ==================== CHART OF ACCOUNTS OPERATIONS ====================

def get_account_by_code(conn, account_code: str) -> Optional[sqlite3.Row]:
    """Get account by account code."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chart_of_accounts WHERE account_code = ?", (account_code,))
    return cursor.fetchone()


def get_account_by_name(conn, name: str) -> Optional[sqlite3.Row]:
    """Get account by name."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chart_of_accounts WHERE name = ?", (name,))
    return cursor.fetchone()


def get_all_accounts(conn, category: str = None, account_type: str = None) -> List[Dict[str, Any]]:
    """Get all accounts, optionally filtered by category or type."""
    cursor = conn.cursor()
    
    query = """
        SELECT a.*, t.name as account_type, c.name as account_category
        FROM chart_of_accounts a
        JOIN account_types t ON a.account_type_id = t.id
        JOIN account_categories c ON a.account_category_id = c.id
    """
    
    conditions = []
    params = []
    
    if category:
        conditions.append("c.name = ?")
        params.append(category)
    
    if account_type:
        conditions.append("t.name = ?")
        params.append(account_type)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY a.account_code"
    
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]


def get_account_types(conn) -> List[Dict[str, Any]]:
    """Get all account types."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM account_types ORDER BY id")
    return [dict(row) for row in cursor.fetchall()]


def get_account_categories(conn) -> List[Dict[str, Any]]:
    """Get all account categories."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM account_categories ORDER BY id")
    return [dict(row) for row in cursor.fetchall()]


# ==================== JOURNAL ENTRY OPERATIONS ====================

def create_journal(conn, date: str, description: str, reference: str = None) -> int:
    """Create a new journal entry."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO journals (date, description, reference, total_debit, total_credit)
        VALUES (?, ?, ?, 0, 0)
    """, (date, description, reference))
    return cursor.lastrowid


def add_journal_entry(conn, journal_id: int, account_id: int, 
                      debit: float = 0, credit: float = 0, narration: str = None) -> int:
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
    
    return cursor.lastrowid


def record_transaction(conn, date: str, debit_account_code: str, credit_account_code: str,
                       amount: float, narration: str = None, reference: str = None) -> int:
    """Record a double-entry transaction (debit one account, credit another)."""
    debit_account = get_account_by_code(conn, debit_account_code)
    credit_account = get_account_by_code(conn, credit_account_code)
    
    if not debit_account:
        raise ValueError(f"Debit account {debit_account_code} not found")
    if not credit_account:
        raise ValueError(f"Credit account {credit_account_code} not found")
    
    journal_id = create_journal(conn, date, narration or f"Transaction on {date}", reference)
    add_journal_entry(conn, journal_id, debit_account['id'], amount, 0, narration)
    add_journal_entry(conn, journal_id, credit_account['id'], 0, amount, narration)
    
    return journal_id


def get_journal_by_number(conn, journal_number: int) -> Optional[Dict[str, Any]]:
    """Get journal entry by journal number."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM journals WHERE journal_number = ?", (journal_number,))
    journal = cursor.fetchone()
    if journal:
        return dict(journal)
    return None


def get_journal_entries(conn, journal_id: int = None) -> List[Dict[str, Any]]:
    """Get journal entries, optionally filtered by journal ID."""
    cursor = conn.cursor()
    
    if journal_id:
        cursor.execute("""
            SELECT * FROM journal_entries WHERE journal_id = ?
            ORDER BY id
        """, (journal_id,))
    else:
        cursor.execute("""
            SELECT * FROM journal_entries 
            ORDER BY id DESC
            LIMIT 100
        """)
    
    return [dict(row) for row in cursor.fetchall()]


# ==================== BALANCE REPORTING ====================

def get_trial_balance(conn) -> List[Dict[str, Any]]:
    """Get trial balance (unadjusted)."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM v_trial_balance ORDER BY account_code")
    return [dict(row) for row in cursor.fetchall()]


def get_account_balances(conn, as_of_date: str = None) -> List[Dict[str, Any]]:
    """Get current balances for all accounts."""
    cursor = conn.cursor()
    if as_of_date:
        cursor.execute("SELECT * FROM v_account_balances WHERE date <= ? ORDER BY account_code", (as_of_date,))
    else:
        cursor.execute("SELECT * FROM v_account_balances ORDER BY account_code")
    return [dict(row) for row in cursor.fetchall()]


def calculate_account_balance(conn, account_code: str) -> Dict[str, Any]:
    """Calculate the current balance for a specific account."""
    account = get_account_by_code(conn, account_code)
    if not account:
        return {'error': f'Account {account_code} not found'}
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COALESCE(SUM(debit), 0) as total_debit,
            COALESCE(SUM(credit), 0) as total_credit
        FROM journal_entries
        WHERE account_id = ?
    """, (account['id'],))
    
    result = cursor.fetchone()
    total_debit = float(result[0])
    total_credit = float(result[1])
    
    account_type = get_account_type_info(conn, account['account_type_id'])
    
    # Calculate balance based on normal balance type
    if account_type['normal_balance'] == 'debit':
        balance = total_debit - total_credit
        balance_type = 'debit' if balance > 0 else 'credit'
    else:
        balance = total_credit - total_debit
        balance_type = 'credit' if balance > 0 else 'debit'
    
    return {
        'account_id': account['id'],
        'account_code': account['account_code'],
        'account_name': account['name'],
        'account_type': account_type['name'],
        'category': account_type['category'],
        'total_debit': total_debit,
        'total_credit': total_credit,
        'balance': abs(balance),
        'balance_type': balance_type
    }


def get_account_type_info(conn, account_type_id: int) -> Optional[Dict[str, Any]]:
    """Get account type information."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM account_types WHERE id = ?", (account_type_id,))
    result = cursor.fetchone()
    return dict(result) if result else None


def get_balance_sheet(conn, as_of_date: str = None) -> Dict[str, Any]:
    """Generate balance sheet report."""
    cursor = conn.cursor()
    
    # Get assets (debit balance accounts)
    cursor.execute("""
        SELECT a.name, a.account_code, 
               COALESCE(SUM(je.debit), 0) - COALESCE(SUM(je.credit), 0) as balance
        FROM chart_of_accounts a
        JOIN account_types t ON a.account_type_id = t.id
        LEFT JOIN journal_entries je ON a.id = je.account_id
        WHERE t.category = 'asset'
        GROUP BY a.id
        ORDER BY a.account_code
    """)
    assets = [dict(row) for row in cursor.fetchall()]
    total_assets = sum(abs(item['balance'] or 0) for item in assets)
    
    # Get liabilities (credit balance accounts)
    cursor.execute("""
        SELECT a.name, a.account_code, 
               COALESCE(SUM(je.credit), 0) - COALESCE(SUM(je.debit), 0) as balance
        FROM chart_of_accounts a
        JOIN account_types t ON a.account_type_id = t.id
        LEFT JOIN journal_entries je ON a.id = je.account_id
        WHERE t.category = 'liability'
        GROUP BY a.id
        ORDER BY a.account_code
    """)
    liabilities = [dict(row) for row in cursor.fetchall()]
    total_liabilities = sum(abs(item['balance'] or 0) for item in liabilities)
    
    # Get equity (credit balance accounts)
    cursor.execute("""
        SELECT a.name, a.account_code, 
               COALESCE(SUM(je.credit), 0) - COALESCE(SUM(je.debit), 0) as balance
        FROM chart_of_accounts a
        JOIN account_types t ON a.account_type_id = t.id
        LEFT JOIN journal_entries je ON a.id = je.account_id
        WHERE t.category = 'equity'
        GROUP BY a.id
        ORDER BY a.account_code
    """)
    equity = [dict(row) for row in cursor.fetchall()]
    total_equity = sum(abs(item['balance'] or 0) for item in equity)
    
    net_worth = total_assets - total_liabilities
    
    return {
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'net_worth': net_worth,
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity
    }


def get_income_statement(conn) -> Dict[str, Any]:
    """Generate income statement (profit & loss) report."""
    cursor = conn.cursor()
    
    # Get revenue (credit balance accounts)
    cursor.execute("""
        SELECT a.name, a.account_code, 
               COALESCE(SUM(je.credit), 0) - COALESCE(SUM(je.debit), 0) as amount
        FROM chart_of_accounts a
        JOIN account_types t ON a.account_type_id = t.id
        LEFT JOIN journal_entries je ON a.id = je.account_id
        WHERE t.category = 'revenue'
        GROUP BY a.id
        ORDER BY a.account_code
    """)
    revenue = [dict(row) for row in cursor.fetchall()]
    total_revenue = sum(abs(item['amount'] or 0) for item in revenue)
    
    # Get expenses (debit balance accounts)
    cursor.execute("""
        SELECT a.name, a.account_code, 
               COALESCE(SUM(je.debit), 0) - COALESCE(SUM(je.credit), 0) as amount
        FROM chart_of_accounts a
        JOIN account_types t ON a.account_type_id = t.id
        LEFT JOIN journal_entries je ON a.id = je.account_id
        WHERE t.category = 'expense'
        GROUP BY a.id
        ORDER BY a.account_code
    """)
    expenses = [dict(row) for row in cursor.fetchall()]
    total_expenses = sum(abs(item['amount'] or 0) for item in expenses)
    
    net_income = total_revenue - total_expenses
    
    return {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_income': net_income,
        'revenue': revenue,
        'expenses': expenses
    }


# ==================== PERIODIC REPORTING ====================

def create_balance_sheet_snapshot(conn, period_id: int = None, snapshot_date: str = None) -> int:
    """Create a balance sheet snapshot for a period."""
    if snapshot_date is None:
        snapshot_date = datetime.now().strftime('%Y-%m-%d')
    
    balance_sheet = get_balance_sheet(conn)
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO balance_sheet_snapshots (period_id, snapshot_date, 
            total_assets, total_liabilities, total_equity, net_worth)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (period_id, snapshot_date,
          balance_sheet['total_assets'],
          balance_sheet['total_liabilities'],
          balance_sheet['total_equity'],
          balance_sheet['net_worth']))
    
    return cursor.lastrowid


def create_income_statement_snapshot(conn, period_id: int = None, snapshot_date: str = None) -> int:
    """Create an income statement snapshot for a period."""
    if snapshot_date is None:
        snapshot_date = datetime.now().strftime('%Y-%m-%d')
    
    income_statement = get_income_statement(conn)
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO income_statement_snapshots (period_id, snapshot_date, 
            total_revenue, total_expenses, net_income)
        VALUES (?, ?, ?, ?, ?)
    """, (period_id, snapshot_date,
          income_statement['total_revenue'],
          income_statement['total_expenses'],
          income_statement['net_income']))
    
    return cursor.lastrowid


def create_trial_balance_snapshot(conn, snapshot_date: str = None) -> int:
    """Create a trial balance snapshot for verification."""
    if snapshot_date is None:
        snapshot_date = datetime.now().strftime('%Y-%m-%d')
    
    trial_balance = get_trial_balance(conn)
    total_debits = sum(abs(item.get('total_debit', 0)) for item in trial_balance)
    total_credits = sum(abs(item.get('total_credit', 0)) for item in trial_balance)
    is_balanced = abs(total_debits - total_credits) < 0.01
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trial_balance_snapshots (snapshot_date, total_debits, total_credits, is_balanced)
        VALUES (?, ?, ?, ?)
    """, (snapshot_date, total_debits, total_credits, 1 if is_balanced else 0))
    
    return cursor.lastrowid


# ==================== UTILITY FUNCTIONS ====================

def verify_double_entry(conn) -> Dict[str, Any]:
    """Verify that all journal entries are balanced (debit = credit)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, journal_number, total_debit, total_credit,
               ABS(total_debit - total_credit) as difference
        FROM journals
        ORDER BY id
    """)
    
    journals = [dict(row) for row in cursor.fetchall()]
    unbalanced = [j for j in journals if j['difference'] > 0.01]
    
    return {
        'total_journals': len(journals),
        'balanced': len(unbalanced) == 0,
        'unbalanced_count': len(unbalanced),
        'unbalanced_journals': unbalanced
    }


def get_database_stats(conn) -> Dict[str, int]:
    """Get database statistics."""
    cursor = conn.cursor()
    tables = ['chart_of_accounts', 'journals', 'journal_entries',
              'account_balances', 'financial_periods', 'trial_balance_snapshots',
              'income_statement_snapshots', 'balance_sheet_snapshots']
    
    stats = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]
    
    return stats


def export_journal_to_csv(conn, output_path: str, journal_id: int = None):
    """Export journal entries to CSV."""
    cursor = conn.cursor()
    
    if journal_id:
        cursor.execute("""
            SELECT j.journal_number, j.date, j.description, a.name as account_name,
                   je.debit, je.credit, je.narration
            FROM journals j
            JOIN journal_entries je ON j.id = je.journal_id
            JOIN chart_of_accounts a ON je.account_id = a.id
            WHERE j.id = ?
            ORDER BY j.id, a.name
        """, (journal_id,))
    else:
        cursor.execute("""
            SELECT j.journal_number, j.date, j.description, a.name as account_name,
                   je.debit, je.credit, je.narration
            FROM journals j
            JOIN journal_entries je ON j.id = je.journal_id
            JOIN chart_of_accounts a ON je.account_id = a.id
            ORDER BY j.date DESC, j.journal_number DESC
        """)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Journal', 'Date', 'Description', 'Account', 'Debit', 'Credit', 'Narration'])
        writer.writerows(cursor.fetchall())


def get_recent_transactions(conn, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent transactions."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT j.journal_number, j.date, j.description, 
               SUM(je.debit) as total_debit, SUM(je.credit) as total_credit
        FROM journals j
        JOIN journal_entries je ON j.id = je.journal_id
        GROUP BY j.id
        ORDER BY j.date DESC
        LIMIT ?
    """, (limit,))
    return [dict(row) for row in cursor.fetchall()]


if __name__ == "__main__":
    conn = get_db_connection()
    
    print("=== Double-Entry Accounting System ===")
    print()
    
    print("Database Statistics:")
    stats = get_database_stats(conn)
    for table, count in stats.items():
        print(f"  {table}: {count}")
    print()
    
    print("=== Trial Balance ===")
    for item in get_trial_balance(conn)[:10]:
        debit = item.get('total_debit', 0) or 0
        credit = item.get('total_credit', 0) or 0
        print(f"  {item['account_code']} {item['name']}: "
              f"Debit={debit:,.2f}, Credit={credit:,.2f}")
    print()
    
    print("=== Balance Sheet ===")
    bs = get_balance_sheet(conn)
    print(f"  Total Assets: {bs['total_assets']:,.2f}")
    print(f"  Total Liabilities: {bs['total_liabilities']:,.2f}")
    print(f"  Total Equity: {bs['total_equity']:,.2f}")
    print(f"  Net Worth: {bs['net_worth']:,.2f}")
    print()
    
    print("=== Income Statement ===")
    is_report = get_income_statement(conn)
    print(f"  Total Revenue: {is_report['total_revenue']:,.2f}")
    print(f"  Total Expenses: {is_report['total_expenses']:,.2f}")
    print(f"  Net Income: {is_report['net_income']:,.2f}")
    print()
    
    print("=== Double-Entry Verification ===")
    verification = verify_double_entry(conn)
    print(f"  Total Journals: {verification['total_journals']}")
    print(f"  All Balanced: {verification['balanced']}")
    
    conn.close()