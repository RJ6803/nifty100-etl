"""One-page-per-company portfolio reference PDF.

Day 35 specification:
- One page per company in alphabetical order by ticker
- Each page: company name, sector, top 6 KPIs, trend arrows
  - UP arrow (^) if metric improved vs prior year
  - DOWN arrow (v) if declined vs prior year
  - FLAT arrow (>) if change is within 2%
- 92 canonical companies from nifty100.db companies table
"""
import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
)

DB_PATH = "data/nifty100.db"


# ------------------------------------------------------------------
# Trend arrow logic
# ------------------------------------------------------------------

def trend_arrow(latest_val, prior_val, lower_is_better=False):
    """
    Return ASCII trend indicator comparing latest vs prior year value.
    ↑ (^) if improved by more than 2%, ↓ (v) if declined by more than 2%,
    → (>) if flat within ±2%.  For metrics where lower is better (D/E),
    set lower_is_better=True.
    """
    try:
        latest = float(latest_val)
        prior = float(prior_val)
        if prior == 0:
            return ">"
        change_pct = (latest - prior) / abs(prior) * 100
        if abs(change_pct) <= 2:
            return ">"
        improved = change_pct > 0
        if lower_is_better:
            improved = not improved
        return "^" if improved else "v"
    except (TypeError, ValueError):
        return ">"


# ------------------------------------------------------------------
# Load data
# ------------------------------------------------------------------

def load_canonical_companies():
    """Load the 92 canonical companies from nifty100.db ordered by ticker."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT id AS company_id, company_name FROM companies ORDER BY id",
        conn
    )
    conn.close()
    return df


def load_ratios_all():
    """Load financial_ratios for all companies, sorted by company_id + year."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM financial_ratios", conn)
    conn.close()
    df["year_num"] = (
        df["year"].astype(str)
        .str.extract(r"(\d{4})")[0]
        .astype(float)
    )
    df = df.sort_values(["company_id", "year_num"])
    return df


def load_sectors():
    """Load sector data."""
    try:
        return pd.read_excel(
            "data/raw/sectors.xlsx",
            usecols=["company_id", "broad_sector", "sub_sector"]
        )
    except Exception:
        return pd.DataFrame(columns=["company_id", "broad_sector", "sub_sector"])


def get_latest_and_prior(ratios_df, company_id, column):
    """Return (latest_value, prior_year_value) for a given column."""
    sub = ratios_df[ratios_df["company_id"] == company_id].sort_values("year_num")
    if column not in sub.columns:
        return None, None
    vals = sub[column].dropna()
    if len(vals) == 0:
        return None, None
    if len(vals) == 1:
        return vals.iloc[-1], None
    return vals.iloc[-1], vals.iloc[-2]


def fmt(value, suffix="", default="N/A"):
    """Format a numeric value, return default on None/NaN."""
    try:
        if value is None or pd.isna(value):
            return default
        return f"{float(value):,.2f}{suffix}"
    except Exception:
        return default


# ------------------------------------------------------------------
# Generate PDF
# ------------------------------------------------------------------

def generate(path="reports/portfolio/portfolio_summary.pdf"):

    companies = load_canonical_companies()
    ratios_all = load_ratios_all()
    sectors = load_sectors()

    # Merge sector info into companies
    companies = companies.merge(sectors, on="company_id", how="left")

    s = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "PortTitle",
        parent=s["Heading1"],
        textColor=colors.HexColor("#17365D"),
        fontSize=16,
        spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        "PortSub",
        parent=s["Normal"],
        textColor=colors.HexColor("#4A4A4A"),
        fontSize=11,
        spaceAfter=10,
    )
    note_style = ParagraphStyle(
        "PortNote",
        parent=s["Normal"],
        textColor=colors.grey,
        fontSize=8,
    )

    # KPI definitions: (display_label, column_name, suffix, lower_is_better)
    KPIS = [
        ("Return on Equity (ROE)",        "return_on_equity_pct",          "%",  False),
        ("Return on Capital (ROCE)",      "return_on_capital_employed_pct", "%",  False),
        ("Net Profit Margin",             "net_profit_margin_pct",          "%",  False),
        ("Debt to Equity",                "debt_to_equity",                 "",   True),
        ("Revenue CAGR 5yr",              "revenue_cagr_5yr",               "%",  False),
        ("Free Cash Flow (Cr)",           "free_cash_flow_cr",              "",   False),
    ]

    story = []
    total = len(companies)

    for i, row in enumerate(companies.itertuples(index=False)):
        company_id   = row.company_id
        company_name = row.company_name if pd.notna(row.company_name) else company_id
        broad_sector = row.broad_sector if hasattr(row, "broad_sector") and pd.notna(row.broad_sector) else "—"
        sub_sector   = row.sub_sector   if hasattr(row, "sub_sector")   and pd.notna(row.sub_sector)   else "—"

        # ----- Header -----
        story.append(Paragraph(f"{company_name}  ({company_id})", title_style))
        story.append(Paragraph(f"{broad_sector}  |  {sub_sector}", sub_style))

        # ----- KPI Table -----
        header_row = [
            Paragraph("<b>Metric</b>",  s["BodyText"]),
            Paragraph("<b>Latest</b>",  s["BodyText"]),
            Paragraph("<b>Prior Yr</b>",s["BodyText"]),
            Paragraph("<b>Trend</b>",   s["BodyText"]),
        ]
        table_data = [header_row]

        for label, col, suffix, lower_is_better in KPIS:
            latest_val, prior_val = get_latest_and_prior(ratios_all, company_id, col)
            arrow = trend_arrow(latest_val, prior_val, lower_is_better)

            # Colour the arrow
            arrow_color = {
                "^": "darkgreen",
                "v": "red",
                ">": "grey",
            }.get(arrow, "grey")

            table_data.append([
                Paragraph(label, s["BodyText"]),
                Paragraph(fmt(latest_val, suffix), s["BodyText"]),
                Paragraph(fmt(prior_val, suffix), s["BodyText"]),
                Paragraph(
                    f"<font color='{arrow_color}'><b>{arrow}</b></font>",
                    s["BodyText"]
                ),
            ])

        kpi_table = Table(
            table_data,
            colWidths=[3.0 * inch, 1.5 * inch, 1.5 * inch, 0.8 * inch],
        )
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#17365D")),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("GRID",          (0, 0), (-1, -1), 0.25, colors.grey),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1),
             [colors.white, colors.HexColor("#EEF3FA")]),
            ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ]))

        story.append(kpi_table)
        story.append(Spacer(1, 10))

        # Trend legend on each page
        story.append(Paragraph(
            "Trend: ^ = Improved  |  v = Declined  |  > = Flat (within 2%)",
            note_style
        ))

        if i < total - 1:
            story.append(PageBreak())

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)

    SimpleDocTemplate(
        str(out),
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    ).build(story)

    print(f"Portfolio summary PDF saved: {out}")
    print(f"Pages: {total} companies")


if __name__ == "__main__":
    generate()
