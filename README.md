# 📊 Nifty 100 Analytics Dashboard

A comprehensive financial analytics platform for **Nifty 100 companies** that automates ETL, financial ratio computation, stock screening, portfolio construction, valuation analysis, peer comparison, and an interactive Streamlit dashboard.

---

# 🚀 Features

## ETL Pipeline
- Import raw financial data from Excel workbooks
- Validate and normalize datasets
- Store processed data in SQLite
- Generate audit logs and validation reports

## Financial Ratio Engine
- Profitability Ratios
- Liquidity Ratios
- Leverage Ratios
- Efficiency Ratios
- Cash Flow Metrics
- CAGR Calculations
- Composite Quality Score

## Stock Screener
Pre-built screening presets:

- Quality Compounder
- Value Pick
- Growth Accelerator
- Dividend Champion
- Debt-Free Blue Chip
- Turnaround Watch

Supports live filtering using:

- ROE
- Debt/Equity
- Free Cash Flow
- Revenue CAGR
- PAT CAGR
- Operating Margin
- P/E
- P/B
- Dividend Yield
- Interest Coverage Ratio

---

# 📈 Portfolio Module

Features include:

- Equal Weight Portfolio
- Portfolio Report Generation
- Risk Metrics
- Performance Metrics
- Portfolio Rebalancing

---

# 💰 Valuation Module

Calculates:

- FCF Yield
- Sector Median P/E
- P/E Premium / Discount
- Valuation Flags

Generated Reports:

- valuation_summary.xlsx
- valuation_flags.csv

---

# 📊 Streamlit Dashboard

The dashboard contains **8 interactive pages**.

## 1. Home

Displays

- Summary KPI cards
- Sector Distribution
- Top Quality Companies

---

## 2. Company Profile

Displays

- Company Overview
- Financial KPIs
- Revenue Trend
- Net Profit Trend
- ROE & ROCE Trend
- Pros & Cons

---

## 3. Financial Screener

Supports

- Interactive Filters
- Preset Screeners
- Live Results
- CSV Export

---

## 4. Peer Comparison

Includes

- Peer Group Selection
- Radar Chart
- KPI Comparison Table

---

## 5. Trend Analysis

Displays

- Multi-Metric Trend Analysis
- Historical Performance
- Interactive Charts

---

## 6. Sector Analysis

Displays

- Bubble Chart
- Sector Median KPIs
- Company Distribution

---

## 7. Capital Allocation

Shows

- Treemap Visualization
- Allocation Pattern Distribution
- Company Lists by Pattern

---

## 8. Annual Reports

Allows users to

- Search Companies
- View Available Reports
- Open BSE Annual Report Links

---

# 🛠 Tech Stack

## Programming Language

- Python 3.10

## Database

- SQLite

## Dashboard

- Streamlit

## Data Processing

- Pandas
- NumPy

## Visualizations

- Plotly
- Matplotlib

## Excel Processing

- OpenPyXL

## Testing

- PyTest

---

# 📁 Project Structure

```
nifty100-etl/

│
├── config/
├── data/
│   ├── raw/
│   └── nifty100.db
│
├── docs/
│
├── output/
│
├── reports/
│
├── sql/
│
├── src/
│   ├── analytics/
│   ├── dashboard/
│   ├── db/
│   ├── etl/
│   ├── features/
│   ├── portfolio/
│   ├── reports/
│   ├── risk/
│   └── screener/
│
├── tests/
│
└── README.md
```

---

# ⚙ Installation

Clone the repository

```bash
git clone <repository-url>

cd nifty100-etl
```

Create virtual environment

```bash
python -m venv venv
```

Activate

Windows

```powershell
venv\Scripts\activate
```

Install dependencies

```powershell
pip install -r requirements.txt
```

---

# ▶ Running the ETL Pipeline

```powershell
python -m src.etl.loader
```

---

# ▶ Running the Screener

```powershell
python -m src.screener.engine
```

Generated outputs

- screener_output.xlsx
- screener_results.csv

---

# ▶ Running Peer Comparison

```powershell
python -m src.analytics.peer
```

Output

- peer_comparison.xlsx

---

# ▶ Running Portfolio Builder

```powershell
python -m src.portfolio.builder
```

Output

- Portfolio_Report.xlsx

---

# ▶ Running Valuation Module

```powershell
python -m src.analytics.valuation
```

Outputs

- valuation_summary.xlsx
- valuation_flags.csv

---

# ▶ Running the Dashboard

```powershell
streamlit run src/dashboard/app.py
```

The dashboard launches locally at

```
http://localhost:8501
```

---

# 📂 Generated Reports

The project generates

- Portfolio_Report.xlsx
- peer_comparison.xlsx
- screener_output.xlsx
- screener_results.csv
- valuation_summary.xlsx
- valuation_flags.csv
- quality_compounder.xlsx
- value_pick.xlsx
- growth_accelerator.xlsx
- dividend_champion.xlsx
- debt_free_blue_chip.xlsx
- turnaround_watch.xlsx

---

# ✅ Testing

Run all tests

```powershell
pytest
```

Current status

```
116 tests passed
```

---

# 📸 Dashboard Screens

> Add screenshots of the following pages.

- Home
- Company Profile
- Financial Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation
- Annual Reports

---

# 📌 Future Enhancements

- Live NSE/BSE API Integration
- Real-Time Stock Prices
- DCF Valuation
- Portfolio Optimization
- Backtesting Engine
- Authentication
- Cloud Deployment
- Docker Support

---

# 📄 License

This project is developed for educational and academic purposes.
