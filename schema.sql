-- Double-Entry Accounting Database Schema
-- Implements proper accounting with journal entries and account types

PRAGMA foreign_keys = ON;

-- ============================================
-- TABLE: account_types
-- Categories of accounts (assets, liabilities, equity, revenue, expenses)
-- ============================================
CREATE TABLE IF NOT EXISTS account_types (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    normal_balance TEXT NOT NULL CHECK(normal_balance IN ('debit', 'credit')),
    category TEXT NOT NULL CHECK(category IN ('asset', 'liability', 'equity', 'revenue', 'expense'))
);

-- ============================================
-- TABLE: account_categories
-- Personal vs Business account categorization
-- ============================================
CREATE TABLE IF NOT EXISTS account_categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- ============================================
-- TABLE: chart_of_accounts
-- Complete chart of accounts with types and categories
-- ============================================
CREATE TABLE IF NOT EXISTS chart_of_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    account_type_id INTEGER NOT NULL,
    account_category_id INTEGER NOT NULL,
    parent_account_id INTEGER,
    is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_type_id) REFERENCES account_types(id),
    FOREIGN KEY (account_category_id) REFERENCES account_categories(id),
    FOREIGN KEY (parent_account_id) REFERENCES chart_of_accounts(id)
);

-- ============================================
-- TABLE: journals
-- Journal entries (each transaction is a journal entry)
-- ============================================
CREATE TABLE IF NOT EXISTS journals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    journal_number INTEGER NOT NULL UNIQUE,
    date TEXT NOT NULL,
    reference TEXT,
    description TEXT NOT NULL,
    total_debit REAL NOT NULL DEFAULT 0,
    total_credit REAL NOT NULL DEFAULT 0,
    is_posted INTEGER DEFAULT 0 CHECK(is_posted IN (0, 1)),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT DEFAULT 'system'
);

-- ============================================
-- TABLE: journal_entries
-- Line items within journal entries (debit/credit pairs)
-- ============================================
CREATE TABLE IF NOT EXISTS journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    journal_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    debit REAL DEFAULT 0,
    credit REAL DEFAULT 0,
    narration TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (journal_id) REFERENCES journals(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES chart_of_accounts(id)
);

-- ============================================
-- TABLE: account_balances
-- Running balances for each account (updated after each posting)
-- ============================================
CREATE TABLE IF NOT EXISTS account_balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    balance REAL NOT NULL DEFAULT 0,
    balance_type TEXT NOT NULL CHECK(balance_type IN ('debit', 'credit')),
    FOREIGN KEY (account_id) REFERENCES chart_of_accounts(id)
);

-- ============================================
-- TABLE: financial_periods
-- Fiscal periods for reporting
-- ============================================
CREATE TABLE IF NOT EXISTS financial_periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    is_closed INTEGER DEFAULT 0 CHECK(is_closed IN (0, 1)),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLE: trial_balance_snapshots
-- Periodic trial balance snapshots
-- ============================================
CREATE TABLE IF NOT EXISTS trial_balance_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id INTEGER,
    snapshot_date TEXT NOT NULL,
    total_debits REAL NOT NULL,
    total_credits REAL NOT NULL,
    is_balanced INTEGER DEFAULT 1 CHECK(is_balanced IN (0, 1)),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (period_id) REFERENCES financial_periods(id)
);

-- ============================================
-- TABLE: income_statement_snapshots
-- Periodic profit and loss snapshots
-- ============================================
CREATE TABLE IF NOT EXISTS income_statement_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id INTEGER,
    snapshot_date TEXT NOT NULL,
    revenue REAL NOT NULL DEFAULT 0,
    cost_of_goods_sold REAL NOT NULL DEFAULT 0,
    gross_profit REAL NOT NULL DEFAULT 0,
    operating_expenses REAL NOT NULL DEFAULT 0,
    net_income REAL NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (period_id) REFERENCES financial_periods(id)
);

-- ============================================
-- TABLE: balance_sheet_snapshots
-- Periodic balance sheet snapshots
-- ============================================
CREATE TABLE IF NOT EXISTS balance_sheet_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id INTEGER,
    snapshot_date TEXT NOT NULL,
    total_assets REAL NOT NULL DEFAULT 0,
    total_liabilities REAL NOT NULL DEFAULT 0,
    total_equity REAL NOT NULL DEFAULT 0,
    net_worth REAL NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (period_id) REFERENCES financial_periods(id)
);

-- ============================================
-- INDEXES for performance
-- ============================================
CREATE INDEX idx_journals_date ON journals(date);
CREATE INDEX idx_journals_journal_number ON journals(journal_number);
CREATE INDEX idx_journal_entries_account_id ON journal_entries(account_id);
CREATE INDEX idx_journal_entries_journal_id ON journal_entries(journal_id);
CREATE INDEX idx_chart_of_accounts_type ON chart_of_accounts(account_type_id);
CREATE INDEX idx_chart_of_accounts_category ON chart_of_accounts(account_category_id);
CREATE INDEX idx_account_balances_account_id ON account_balances(account_id);
CREATE INDEX idx_account_balances_date ON account_balances(date);

-- ============================================
-- VIEWS for common queries
-- ============================================

-- View: Account balances summary
CREATE VIEW IF NOT EXISTS v_account_balances AS
SELECT 
    a.id,
    a.account_code,
    a.name,
    t.name as account_type,
    c.name as account_category,
    b.balance,
    b.balance_type
FROM chart_of_accounts a
JOIN account_types t ON a.account_type_id = t.id
JOIN account_categories c ON a.account_category_id = c.id
JOIN account_balances b ON a.id = b.account_id
WHERE b.date = (SELECT MAX(date) FROM account_balances WHERE account_id = a.id);

-- View: Journal entries with account names
CREATE VIEW IF NOT EXISTS v_journal_entries AS
SELECT 
    j.id as journal_id,
    j.journal_number,
    j.date,
    j.reference,
    j.description,
    je.id as line_id,
    je.account_id,
    a.name as account_name,
    a.account_code,
    je.debit,
    je.credit,
    je.narration
FROM journals j
JOIN journal_entries je ON j.id = je.journal_id
JOIN chart_of_accounts a ON je.account_id = a.id
ORDER BY j.date DESC, j.journal_number DESC;

-- View: Trial balance (unadjusted)
CREATE VIEW IF NOT EXISTS v_trial_balance AS
SELECT 
    a.id,
    a.account_code,
    a.name,
    t.name as account_type,
    SUM(je.debit) as total_debit,
    SUM(je.credit) as total_credit,
    (SUM(je.debit) - SUM(je.credit)) as net_change
FROM chart_of_accounts a
JOIN account_types t ON a.account_type_id = t.id
LEFT JOIN journal_entries je ON a.id = je.account_id
GROUP BY a.id, a.account_code, a.name, t.name;

-- View: Balance Sheet
CREATE VIEW IF NOT EXISTS v_balance_sheet AS
SELECT 
    c.name as category,
    a.name as account_name,
    a.account_code,
    SUM(je.debit) - SUM(je.credit) as balance
FROM chart_of_accounts a
JOIN account_categories c ON a.account_category_id = c.id
JOIN account_types t ON a.account_type_id = t.id
LEFT JOIN journal_entries je ON a.id = je.account_id
WHERE t.category IN ('asset', 'liability', 'equity')
GROUP BY a.id, a.name, c.name, a.account_code;

-- View: Income Statement
CREATE VIEW IF NOT EXISTS v_income_statement AS
SELECT 
    c.name as category,
    a.name as account_name,
    a.account_code,
    SUM(je.credit) - SUM(je.debit) as amount
FROM chart_of_accounts a
JOIN account_categories c ON a.account_category_id = c.id
JOIN account_types t ON a.account_type_id = t.id
LEFT JOIN journal_entries je ON a.id = je.account_id
WHERE t.category IN ('revenue', 'expense')
GROUP BY a.id, a.name, c.name, a.account_code;

-- ============================================
-- SEED DATA: Account Types
-- ============================================
INSERT INTO account_types (id, name, normal_balance, category) VALUES 
(1, 'Asset', 'debit', 'asset'),
(2, 'Liability', 'credit', 'liability'),
(3, 'Equity', 'credit', 'equity'),
(4, 'Revenue', 'credit', 'revenue'),
(5, 'Expense', 'debit', 'expense');

-- ============================================
-- SEED DATA: Account Categories
-- ============================================
INSERT INTO account_categories (id, name, description) VALUES 
(1, 'Personal', 'Personal finances and assets'),
(2, 'Business', 'Business operations and finances');

-- ============================================
-- SEED DATA: Chart of Accounts
-- ============================================

-- Personal Assets
INSERT INTO chart_of_accounts (account_code, name, account_type_id, account_category_id, description) VALUES 
('101', 'Cash Account', 1, 1, 'Physical cash on hand'),
('102', 'Standard Chartered Bank', 1, 1, 'Bank account'),
('103', 'MTN Mobile Money', 1, 1, 'MTN mobile money wallet'),
('104', 'Xeno Savings', 1, 1, 'Xeno savings account');

-- Business Assets
INSERT INTO chart_of_accounts (account_code, name, account_type_id, account_category_id, description) VALUES 
('201', 'Business Cash', 1, 2, 'Business operating cash'),
('202', 'Business Equipment', 1, 2, 'Computers, furniture, equipment'),
('203', 'Inventory', 1, 2, 'Feza kitchen inventory');

-- Personal Liabilities
INSERT INTO chart_of_accounts (account_code, name, account_type_id, account_category_id, description) VALUES 
('301', 'Personal Loans', 2, 1, 'Personal loans and debts'),
('302', 'Credit Cards', 2, 1, 'Credit card balances'),
('303', 'MomoAdvance', 2, 1, 'MTN MomoAdvance overdraft');

-- Business Liabilities
INSERT INTO chart_of_accounts (account_code, name, account_type_id, account_category_id, description) VALUES 
('401', 'Accounts Payable', 2, 2, 'Business bills and payables'),
('402', 'Business Loans', 2, 2, 'Business loans and financing');

-- Equity
INSERT INTO chart_of_accounts (account_code, name, account_type_id, account_category_id, description) VALUES 
('501', 'Owner''s Capital', 3, 1, 'Paul Obunga - personal capital'),
('502', 'Retained Earnings', 3, 1, 'Accumulated profits/losses'),
('503', 'Business Capital', 3, 2, 'Business capital contribution');

-- Revenue (Business)
INSERT INTO chart_of_accounts (account_code, name, account_type_id, account_category_id, description) VALUES 
('601', 'Feza Sales', 4, 2, 'Feza Kitchen & Grill sales'),
('602', 'Business Income', 4, 2, 'Other business income');

-- Personal Income (Income transfers)
INSERT INTO chart_of_accounts (account_code, name, account_type_id, account_category_id, description) VALUES 
('651', 'Personal Income', 4, 1, 'Personal income from employment'),
('652', 'Transfer Income', 4, 1, 'Income from transfers and gifts');

-- Business Expenses
INSERT INTO chart_of_accounts (account_code, name, account_type_id, account_category_id, description) VALUES 
('701', 'Cost of Goods Sold', 5, 2, 'Feza food ingredients and supplies'),
('702', 'Rent Expense', 5, 2, 'Business rent and lease'),
('703', 'Salaries Expense', 5, 2, 'Business staff salaries'),
('704', 'Utilities Expense', 5, 2, 'Business utilities'),
('705', 'Transport Expense', 5, 2, 'Business transport costs');

-- Personal Expenses
INSERT INTO chart_of_accounts (account_code, name, account_type_id, account_category_id, description) VALUES 
('751', 'Food Expense', 5, 1, 'Personal food and groceries'),
('752', 'Transport Expense', 5, 1, 'Personal transport'),
('753', 'Health Expense', 5, 1, 'Personal healthcare'),
('754', 'Education Expense', 5, 1, 'Personal education costs'),
('755', 'Misc Expense', 5, 1, 'Personal miscellaneous');

-- ============================================
-- SEED DATA: Initial Account Balances
-- ============================================

-- Get current balances from existing data and seed initial balances
-- These will be updated with transactions

-- ============================================
-- SEED DATA: Financial Period (Oct 2026)
-- ============================================
INSERT INTO financial_periods (name, start_date, end_date) VALUES 
('October 2026', '2026-10-01', '2026-10-31');

-- ============================================
-- SEED DATA: Initial Journal Entry (Opening Balances)
-- ============================================
-- Create opening balance journal entry for October 1
INSERT INTO journals (journal_number, date, description, total_debit, total_credit) VALUES 
(1, '2026-10-01', 'Opening balances migration', 0, 0);

-- Get the journal ID
INSERT INTO journal_entries (journal_id, account_id, debit, credit, narration) VALUES 
(1, (SELECT id FROM chart_of_accounts WHERE account_code = '101'), 0, 0, 'Opening balance'),
(1, (SELECT id FROM chart_of_accounts WHERE account_code = '102'), 0, 0, 'Opening balance'),
(1, (SELECT id FROM chart_of_accounts WHERE account_code = '103'), 0, 0, 'Opening balance'),
(1, (SELECT id FROM chart_of_accounts WHERE account_code = '104'), 0, 0, 'Opening balance');

-- ============================================
-- SEED DATA: Initial Journal Entry (Current Balances)
-- ============================================
-- Create journal entry for current balances (Oct 5-6)
INSERT INTO journals (journal_number, date, description, total_debit, total_credit) VALUES 
(2, '2026-10-05', 'Migrate Oct 5-6 balances', 0, 0);

-- ============================================
-- SEED DATA: Current Balances Migration
-- ============================================
-- Cash Account: 3000 UGX (from last transaction)
INSERT INTO journals (journal_number, date, description, total_debit, total_credit) VALUES 
(3, '2026-10-06', 'Update cash balance to 3000', 0, 0);

-- MTN Mobile Money: 640 UGX
INSERT INTO journals (journal_number, date, description, total_debit, total_credit) VALUES 
(4, '2026-10-06', 'Update MTN balance to 640', 0, 0);

-- Bank: 997 UGX
INSERT INTO journals (journal_number, date, description, total_debit, total_credit) VALUES 
(5, '2026-10-05', 'Update bank balance to 997', 0, 0);

-- Xeno Savings: 72201 UGX
INSERT INTO journals (journal_number, date, description, total_debit, total_credit) VALUES 
(6, '2026-10-05', 'Update Xeno balance to 72201', 0, 0);

-- Schema complete
SELECT 'Double-entry accounting schema created successfully!' AS status;
SELECT 'Chart of accounts populated with ' || COUNT(*) || ' accounts' AS info FROM chart_of_accounts;