# Sprint 3 Retrospective Report

## Project
**Nifty 100 Financial Analytics Dashboard**

## Sprint
**Sprint 3 — Screener & Peer Comparison Engine**

## Sprint Duration
**Day 15 – Day 21**

## Sprint Goal

The objective of Sprint 3 was to develop a robust financial screening engine and peer comparison system capable of identifying fundamentally strong companies using configurable investment strategies. The sprint also aimed to generate comprehensive screening reports, peer percentile rankings, radar chart visualizations, and Excel reports suitable for financial analysis.

---

# Sprint Objectives

- Build configurable financial screener
- Implement six predefined investment screeners
- Calculate composite quality scores
- Compute peer percentile rankings
- Generate radar chart visualizations
- Export screening reports to Excel
- Validate all screening logic using automated unit tests

---

# User Stories Completed

## Epic 03 — Financial Screener Engine

### Story 1 — Dynamic Filter Engine

Implemented a configurable screening engine that loads analyst-defined thresholds from YAML configuration files.

Supported filtering metrics include:

- Return on Equity (ROE)
- Debt to Equity Ratio
- Free Cash Flow
- Revenue CAGR (5 Year)
- PAT CAGR (5 Year)
- Operating Profit Margin
- Price to Earnings Ratio
- Price to Book Ratio
- Dividend Yield
- Interest Coverage Ratio
- Market Capitalization
- Net Profit
- EPS CAGR
- Asset Turnover
- Revenue

---

### Story 2 — Preset Investment Screeners

Successfully implemented six predefined screening strategies.

| Screener | Purpose |
|----------|----------|
| Quality Compounder | High-quality businesses |
| Value Pick | Undervalued companies |
| Growth Accelerator | High-growth companies |
| Dividend Champion | Consistent dividend-paying companies |
| Debt-Free Blue Chip | Financially strong large-cap companies |
| Turnaround Watch | Improving businesses with positive cash flow |

Each screener successfully returned meaningful companies within the expected range.

---

### Story 3 — Composite Quality Score

Implemented a weighted composite scoring model.

Weight distribution:

| Category | Weight |
|----------|---------|
| Profitability | 35% |
| Cash Quality | 30% |
| Growth | 20% |
| Leverage | 15% |

The score is normalized on a **0–100 scale** and adjusted relative to sector performance.

---

### Story 4 — Screener Report Export

Generated:

```
output/screener_output.xlsx
```

Features:

- Six worksheets
- One worksheet per screener
- Sorted by Composite Quality Score
- Color-coded cells
- Business-friendly formatting

---

# Epic 04 — Peer Comparison Engine

## Story 5 — Peer Percentile Rankings

Developed a peer ranking engine capable of computing percentile rankings for all peer groups.

Metrics ranked:

- ROE
- ROCE
- Net Profit Margin
- Debt to Equity (inverse ranking)
- Free Cash Flow
- Revenue CAGR
- PAT CAGR
- EPS CAGR
- Interest Coverage
- Asset Turnover

Generated percentile rankings for every company belonging to a peer group.

---

## Story 6 — Radar Charts

Generated radar chart visualizations for companies.

Features:

- Company performance polygon
- Peer average comparison
- Eight financial dimensions
- PNG export

Output folder:

```
reports/radar_charts/
```

---

## Story 7 — Peer Comparison Report

Generated:

```
output/peer_comparison.xlsx
```

Features:

- Eleven worksheets
- One worksheet per peer group
- Percentile rankings
- Color-coded performance
- Benchmark highlighting
- Peer median summary

---

# Technical Deliverables

Successfully developed:

```
config/
└── screener_config.yaml
```

```
src/
├── analytics/
│   └── peer.py
│
└── screener/
    └── engine.py
```

Generated reports:

```
output/
├── screener_output.xlsx
├── peer_comparison.xlsx
├── quality_compounder.xlsx
├── value_pick.xlsx
├── growth_accelerator.xlsx
├── dividend_champion.xlsx
├── debt_free_blue_chip.xlsx
└── turnaround_watch.xlsx
```

Generated charts:

```
reports/
└── radar_charts/
```

---

# Testing Summary

Unit testing completed successfully.

```
116 Tests Passed
0 Failures
```

Validated:

- Screener logic
- Financial ratios
- CAGR calculations
- Portfolio functions
- Peer engine
- Screening engine
- Risk metrics
- Export functionality

---

# Challenges Faced

During Sprint 3, several technical challenges were encountered.

### Data Cleaning

- Missing financial values
- Inconsistent company names
- Duplicate records
- Sector mapping inconsistencies

Resolved using preprocessing and validation routines.

---

### YAML Configuration

Ensured dynamic loading of screener thresholds without requiring code modifications.

---

### Peer Ranking

Implemented inverse percentile logic for Debt-to-Equity so that lower leverage receives higher rankings.

---

### Excel Formatting

Developed reusable formatting logic for:

- Conditional colors
- Multiple worksheets
- Professional financial report layout

---

# Lessons Learned

Sprint 3 provided practical experience in:

- Financial ratio analysis
- Investment screening
- YAML-based configuration
- Percentile ranking
- Sector normalization
- Excel automation
- Data visualization
- Financial analytics

---

# Sprint Outcome

## Completed Deliverables

- Financial Screener Engine
- Six Investment Screeners
- Composite Quality Score
- Peer Ranking Engine
- Radar Chart Generator
- Peer Comparison Report
- Screener Report
- Automated Tests

---

# Definition of Done Checklist

| Requirement | Status |
|------------|--------|
| Six preset screeners implemented | ✅ |
| Presets return valid company sets | ✅ |
| Composite quality score implemented | ✅ |
| Screener report generated | ✅ |
| Peer percentile rankings computed | ✅ |
| Radar charts generated | ✅ |
| Peer comparison workbook generated | ✅ |
| Unit tests passed | ✅ |
| Sprint review completed | ✅ |

---

# Sprint Review Summary

Sprint 3 successfully delivered a configurable financial screening system together with an advanced peer comparison engine. The resulting platform enables analysts to identify high-quality investment opportunities using multiple screening methodologies while comparing companies against sector peers using percentile rankings and visual dashboards.

All planned objectives for Sprint 3 were completed successfully and the sprint was accepted for progression to Sprint 4.

---

