-- 1. Total companies
SELECT COUNT(*) FROM companies;

-- 2. Top 10 companies by sales
SELECT company_name, sales
FROM analysis
ORDER BY sales DESC
LIMIT 10;

-- 3. Top 10 by OPM
SELECT company_name, opm
FROM analysis
ORDER BY opm DESC
LIMIT 10;

-- 4. Top ROCE companies
SELECT company_name, roce
FROM analysis
ORDER BY roce DESC
LIMIT 10;

-- 5. Highest dividend yield
SELECT company_name, dividend_yield
FROM analysis
ORDER BY dividend_yield DESC
LIMIT 10;

-- 6. Highest market capitalization
SELECT company_name, market_cap
FROM analysis
ORDER BY market_cap DESC
LIMIT 10;

-- 7. Companies with negative cash flow
SELECT company_name, net_cash_flow
FROM cashflow
WHERE net_cash_flow < 0;

-- 8. Sector wise company count
SELECT sector_name, COUNT(*)
FROM companies
GROUP BY sector_name;

-- 9. Top PE ratio companies
SELECT company_name, pe_ratio
FROM financial_ratios
ORDER BY pe_ratio DESC
LIMIT 10;

-- 10. Lowest PE ratio companies
SELECT company_name, pe_ratio
FROM financial_ratios
ORDER BY pe_ratio ASC
LIMIT 10;