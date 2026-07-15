# Sprint 4 Retrospective Report

## Project
**Nifty 100 Financial Analytics Dashboard**

## Sprint
**Sprint 4 — Dashboard & Valuation Module**

## Sprint Duration
**Day 22 – Day 28**

## Sprint Goal

The objective of Sprint 4 was to develop a fully interactive Streamlit dashboard for financial analytics and implement a valuation engine capable of identifying undervalued and overvalued companies using financial multiples and free cash flow yield.

The sprint also focused on improving usability through visualization, interactive filtering, and performance optimization while ensuring the dashboard remained responsive across the complete Nifty 100 dataset.

---

# Sprint Objectives

- Develop an interactive Streamlit dashboard
- Implement 8 dashboard modules
- Integrate dashboard with SQLite database
- Build valuation engine
- Generate valuation reports
- Improve application performance
- Handle missing financial data gracefully
- Complete project documentation

---

# User Stories Completed

# Epic 05 — Streamlit Dashboard

---

## Story 1 — Dashboard Framework

Implemented the main Streamlit application.

Developed

```
src/dashboard/app.py
```

Features

- Wide layout
- Sidebar navigation
- Multi-page dashboard
- Cached database access
- Responsive design

---

## Story 2 — Dashboard Data Layer

Implemented

```
src/dashboard/utils/db.py
```

Functions created

- get_companies()
- get_ratios()
- get_pl()
- get_bs()
- get_cf()
- get_sectors()
- get_peers()
- get_valuation()

Performance improvements

- Streamlit cache
- SQLite optimization
- Faster repeated queries

---

## Story 3 — Home Dashboard

Implemented

```
01_home.py
```

Features

- Average ROE KPI
- Median P/E KPI
- Median Debt-to-Equity KPI
- Total Companies KPI
- Revenue CAGR KPI
- Debt-Free Companies KPI

Visualizations

- Sector Distribution Donut Chart
- Top Quality Companies Table

---

## Story 4 — Company Profile

Implemented

```
02_profile.py
```

Features

- Company Search
- Autocomplete
- Company Overview
- Financial KPIs
- Revenue Trend
- Net Profit Trend
- ROE Trend
- ROCE Trend
- Pros & Cons

Edge Cases

- Missing company
- Missing ratios
- Missing reports

All handled gracefully.

---

## Story 5 — Financial Screener

Implemented

```
03_screener.py
```

Features

- Interactive filters
- Live filtering
- Preset screeners

Supported filters

- ROE
- Debt/Equity
- Revenue CAGR
- PAT CAGR
- Operating Margin
- P/E
- P/B
- Dividend Yield
- Interest Coverage
- Free Cash Flow

Additional features

- Result counter
- CSV Export

---

## Story 6 — Peer Comparison

Implemented

```
04_peers.py
```

Features

- Peer Group Selector
- Radar Chart
- Peer Average Comparison
- KPI Table
- Benchmark Highlighting

---

## Story 7 — Trend Analysis

Implemented

```
05_trends.py
```

Features

- Company Search
- Multiple Metric Selection
- Historical Financial Trends
- Interactive Plotly Charts

Supported Metrics

- Revenue
- PAT
- ROE
- ROCE
- Operating Margin
- Free Cash Flow
- Debt to Equity

---

## Story 8 — Sector Analysis

Implemented

```
06_sectors.py
```

Features

- Sector Selector
- Bubble Chart

Bubble dimensions

- X-axis → Revenue
- Y-axis → ROE
- Bubble Size → Market Cap
- Bubble Color → Sub-sector

Additional

- Sector Median KPI Chart

---

## Story 9 — Capital Allocation

Implemented

```
07_capital.py
```

Features

- Treemap
- Pattern Distribution
- Pattern-wise Company List
- Capital Allocation KPIs

Visualization

- Plotly Treemap
- Distribution Bar Chart

---

## Story 10 — Annual Reports

Implemented

```
08_reports.py
```

Features

- Company Search
- Annual Report Listing
- BSE PDF Links
- Download Access
- Missing Report Handling

---

# Epic 06 — Valuation Engine

---

## Story 11 — Valuation Module

Implemented

```
src/analytics/valuation.py
```

Computed

- FCF Yield
- Sector Median P/E
- P/E Premium
- P/E Discount
- Fair Valuation
- EV/EBITDA
- P/B

Generated

```
output/valuation_summary.xlsx
```

and

```
output/valuation_flags.csv
```

---

## Story 12 — Valuation Classification

Implemented valuation labels

| Condition | Label |
|------------|--------|
| P/E > 1.5 × Sector Median | Caution |
| P/E < 0.7 × Sector Median | Discount |
| Otherwise | Fair |

---

# Technical Deliverables

Successfully developed

```
src/dashboard/
│
├── app.py
│
├── pages/
│   ├── 01_home.py
│   ├── 02_profile.py
│   ├── 03_screener.py
│   ├── 04_peers.py
│   ├── 05_trends.py
│   ├── 06_sectors.py
│   ├── 07_capital.py
│   └── 08_reports.py
│
└── utils/
    └── db.py
```

---

Generated outputs

```
output/

valuation_summary.xlsx

valuation_flags.csv

screener_results.csv

Portfolio_Report.xlsx

peer_comparison.xlsx
```

---

# Testing Summary

Dashboard Testing

Completed testing on multiple companies from different sectors.

Verified

- IT
- Banking
- FMCG
- Healthcare
- Energy
- Industrials

Verified dashboard behavior for

- Missing values
- Partial historical data
- Invalid search
- Extreme screener values

---

Application Performance

Measured

- Dashboard startup
- Company Profile loading
- Database queries
- Streamlit rendering

Result

Company Profile loads within the required response time for normal usage.

---

# Challenges Faced

During Sprint 4 several technical challenges were encountered.

## Streamlit Integration

Resolved

- Page routing
- Multi-page imports
- Sidebar navigation

---

## Database Queries

Optimized SQLite queries using

- Cached functions
- Reduced joins
- Query reuse

---

## Financial Data

Handled

- Missing values
- Null financial metrics
- Companies with fewer historical years

Dashboard now displays

```
N/A
```

instead of crashing.

---

## Visualization

Implemented

- Plotly
- Radar Charts
- Bubble Charts
- Treemaps
- KPI Cards
- Interactive Filters

---

## Valuation Module

Resolved

- Market cap integration
- Sector median calculations
- Fair valuation classification

---

# Lessons Learned

Sprint 4 provided practical experience in

- Streamlit Development
- Interactive Dashboard Design
- Financial Data Visualization
- Plotly Charts
- SQLite Optimization
- Performance Tuning
- Financial Valuation Models
- User Experience Design

---

# Sprint Outcome

Successfully delivered

- Complete Streamlit Dashboard
- Eight Interactive Dashboard Pages
- Financial Screener
- Peer Comparison Dashboard
- Trend Analysis
- Sector Analysis
- Capital Allocation Dashboard
- Annual Reports Viewer
- Valuation Engine
- Valuation Reports

---

# Definition of Done Checklist

| Requirement | Status |
|------------|--------|
| Streamlit dashboard created | ✅ |
| Eight dashboard pages completed | ✅ |
| Dashboard loads without errors | ✅ |
| Company Profile implemented | ✅ |
| Screener supports CSV export | ✅ |
| Peer comparison completed | ✅ |
| Trend analysis completed | ✅ |
| Sector analysis completed | ✅ |
| Capital allocation dashboard completed | ✅ |
| Annual reports page completed | ✅ |
| Valuation module implemented | ✅ |
| valuation_summary.xlsx generated | ✅ |
| valuation_flags.csv generated | ✅ |
| README updated | ✅ |
| Dashboard reviewed successfully | ✅ |

---

# Sprint Review Summary

Sprint 4 successfully transformed the project into a complete financial analytics platform with an interactive Streamlit dashboard and valuation engine. Users can now analyze companies, compare peers, screen investments, visualize financial performance, review annual reports, and evaluate valuation metrics through a unified interface.

The dashboard integrates seamlessly with the ETL pipeline, financial ratio engine, screener, peer comparison system, and valuation module developed in previous sprints.

All planned Sprint 4 objectives were completed successfully.

---

