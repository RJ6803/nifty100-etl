PRAGMA foreign_keys = ON;

-- =====================================================
-- COMPANIES
-- =====================================================

CREATE TABLE companies (
    id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    face_value REAL,
    book_value REAL,
    roce_percentage REAL,
    roe_percentage REAL
);

-- =====================================================
-- PROFIT & LOSS
-- =====================================================

CREATE TABLE profit_loss (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    company_id TEXT NOT NULL,
    year INTEGER NOT NULL,

    sales REAL,
    expenses REAL,
    operating_profit REAL,
    opm_percentage REAL,

    other_income REAL,
    interest REAL,
    depreciation REAL,

    profit_before_tax REAL,
    tax_percentage REAL,
    net_profit REAL,

    eps REAL,
    dividend_payout REAL,

    UNIQUE(company_id, year),

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- BALANCE SHEET
-- =====================================================

CREATE TABLE balance_sheet (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    company_id TEXT NOT NULL,
    year INTEGER NOT NULL,

    equity_capital REAL,
    reserves REAL,
    borrowings REAL,
    other_liabilities REAL,

    total_liabilities REAL,

    fixed_assets REAL,
    cwip REAL,
    investments REAL,
    other_asset REAL,

    total_assets REAL,

    UNIQUE(company_id, year),

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- CASHFLOW
-- =====================================================

CREATE TABLE cashflow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    company_id TEXT NOT NULL,
    year INTEGER NOT NULL,

    operating_activity REAL,
    investing_activity REAL,
    financing_activity REAL,

    net_cash_flow REAL,

    UNIQUE(company_id, year),

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- STOCK PRICES
-- =====================================================

CREATE TABLE stock_prices (
    company_id TEXT NOT NULL,
    date TEXT NOT NULL,

    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,

    volume INTEGER,
    adjusted_close REAL,

    PRIMARY KEY(company_id, date),

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- COMPANY KPIs
-- =====================================================

CREATE TABLE company_kpis (
    company_id TEXT PRIMARY KEY,

    sales REAL,
    net_profit REAL,
    eps REAL,
    opm_percentage REAL,

    net_profit_margin REAL,
    borrowings REAL,
    total_assets REAL,

    debt_ratio REAL,
    asset_turnover REAL,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- COMPANY GROWTH
-- =====================================================

CREATE TABLE company_growth (
    company_id TEXT PRIMARY KEY,

    sales_cagr REAL,
    profit_cagr REAL,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- FINAL FEATURES
-- =====================================================

CREATE TABLE final_company_features (
    company_id TEXT PRIMARY KEY,

    sales REAL,
    net_profit REAL,
    eps REAL,
    opm_percentage REAL,

    net_profit_margin REAL,
    borrowings REAL,
    total_assets REAL,

    debt_ratio REAL,
    asset_turnover REAL,

    sales_cagr REAL,
    profit_cagr REAL,

    roa REAL,
    earnings_yield REAL,
    operating_margin_ratio REAL,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- VALIDATION FAILURES
-- =====================================================

CREATE TABLE validation_failures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    rule TEXT,
    severity TEXT,
    table_name TEXT,
    message TEXT
);

-- =====================================================
-- LOAD AUDIT
-- =====================================================

CREATE TABLE load_audit (
    table_name TEXT PRIMARY KEY,

    rows_loaded INTEGER,
    rejections INTEGER
);