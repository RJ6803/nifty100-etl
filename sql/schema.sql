CREATE TABLE "companies" (
"id" TEXT PRIMARY KEY,
  "company_name" TEXT,
  "face_value" REAL,
  "book_value" REAL,
  "roce_percentage" REAL,
  "roe_percentage" REAL
);

CREATE TABLE "profit_loss" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "company_id" TEXT,
  "year" TEXT,
  "sales" INTEGER,
  "expenses" INTEGER,
  "operating_profit" REAL,
  "opm_percentage" REAL,
  "other_income" INTEGER,
  "interest" INTEGER,
  "depreciation" INTEGER,
  "profit_before_tax" INTEGER,
  "tax_percentage" REAL,
  "net_profit" INTEGER,
  "eps" REAL,
  "dividend_payout" REAL,
  FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE "balance_sheet" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "company_id" TEXT,
  "year" TEXT,
  "equity_capital" REAL,
  "reserves" INTEGER,
  "borrowings" INTEGER,
  "other_liabilities" INTEGER,
  "total_liabilities" INTEGER,
  "fixed_assets" INTEGER,
  "cwip" INTEGER,
  "investments" INTEGER,
  "other_asset" INTEGER,
  "total_assets" INTEGER,
  FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE "cashflow" (
"id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "company_id" TEXT,
  "year" TEXT,
  "operating_activity" REAL,
  "investing_activity" REAL,
  "financing_activity" REAL,
  "net_cash_flow" REAL,
  FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
);

CREATE TABLE "stock_prices" (
"company_id" TEXT ,
  "date" TEXT,
  "open_price" REAL,
  "high_price" REAL,
  "low_price" REAL,
  "close_price" REAL,
  "volume" INTEGER,
  "adjusted_close" REAL,
  primary key(company_id, date),
  FOREIGN KEY(company_id)
    REFERENCES companies(company_id)
  
);

CREATE TABLE "company_kpis" (
"company_id" TEXT  PRIMARY KEY,
  "sales" INTEGER,
  "net_profit" INTEGER,
  "eps" REAL,
  "opm_percentage" REAL,
  "net_profit_margin" REAL,
  "borrowings" INTEGER,
  "total_assets" INTEGER,
  "debt_ratio" REAL,
  "asset_turnover" REAL,
  FOREIGN KEY(company_id)
REFERENCES companies(company_id)
);

CREATE TABLE "company_growth" (
"company_id" TEXT PRIMARY KEY,
  "sales_cagr" REAL,
  "profit_cagr" REAL,
  FOREIGN KEY(company_id)
REFERENCES companies(company_id)
);

CREATE TABLE "final_company_features" (
"company_id" TEXT PRIMARY KEY,
  "sales" INTEGER,
  "net_profit" INTEGER,
  "eps" REAL,
  "opm_percentage" REAL,
  "net_profit_margin" REAL,
  "borrowings" INTEGER,
  "total_assets" INTEGER,
  "debt_ratio" REAL,
  "asset_turnover" REAL,
  "sales_cagr" REAL,
  "profit_cagr" REAL,
  "roa" REAL,
  "earnings_yield" REAL,
  "operating_margin_ratio" REAL,
  FOREIGN KEY(company_id)
REFERENCES companies(company_id)
);

CREATE TABLE "validation_failures" (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
"rule" TEXT,
  "severity" TEXT,
  "table" TEXT,
  "message" TEXT
);

CREATE TABLE "load_audit" (
"table" TEXT PRIMARY KEY,
  "rows_loaded" INTEGER,
  "rejections" INTEGER
);

