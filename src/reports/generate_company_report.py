import os
import sqlite3
import pandas as pd

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch

# ==========================================================
# CONFIGURATION
# ==========================================================

DATABASE = "data/nifty100.db"
OUTPUT_FOLDER = "reports"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ==========================================================
# DATABASE CONNECTION
# ==========================================================

conn = sqlite3.connect(DATABASE)

companies = pd.read_sql(
    "SELECT * FROM companies",
    conn
)

financial_ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

cashflow = pd.read_sql(
    "SELECT * FROM cashflow_intelligence",
    conn
)

peer_percentiles = pd.read_sql(
    "SELECT * FROM peer_percentiles",
    conn
)

conn.close()

# ==========================================================
# PDF STYLES
# ==========================================================

styles = getSampleStyleSheet()

title_style = styles["Heading1"]
title_style.alignment = TA_CENTER

heading_style = styles["Heading2"]

normal_style = styles["BodyText"]

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def latest_company_record(df, company_id):
    """
    Returns latest available year for a company.
    """

    company = df[
        df["company_id"] == company_id
    ].copy()

    if company.empty:
        return None

    company["year_num"] = pd.to_datetime(
        company["year"],
        format="%b %Y",
        errors="coerce"
    ).dt.year

    company = company.sort_values("year_num")

    return company.iloc[-1]


def safe_value(value):

    if pd.isna(value):
        return "N/A"

    if isinstance(value, float):
        return f"{value:,.2f}"

    return str(value)


# ==========================================================
# BUILD REPORT
# ==========================================================

def build_company_report(company_id):

    company_info = companies[
        companies["id"] == company_id
    ]

    if company_info.empty:

        print(f"{company_id} not found")

        return

    company_info = company_info.iloc[0]

    latest_financial = latest_company_record(
        financial_ratios,
        company_id
    )

    latest_cashflow = latest_company_record(
        cashflow,
        company_id
    )

    if latest_financial is None:

        print(f"No financial data for {company_id}")

        return

    pdf_path = os.path.join(
        OUTPUT_FOLDER,
        f"{company_id}_Report.pdf"
    )

    document = SimpleDocTemplate(
        pdf_path,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []

    # ======================================================
    # TITLE
    # ======================================================

    story.append(
        Paragraph(
            f"{company_info['company_name']}<br/>Financial Analysis Report",
            title_style
        )
    )

    story.append(
        Spacer(
            1,
            0.30 * inch
        )
    )

    # ======================================================
    # COMPANY INFORMATION
    # ======================================================

    story.append(
        Paragraph(
            "1. Company Information",
            heading_style
        )
    )

    company_table = [
        ["Company ID", company_info["id"]],
        ["Company Name", company_info["company_name"]],
        ["Face Value", safe_value(company_info["face_value"])],
        ["Book Value", safe_value(company_info["book_value"])],
        ["Latest Financial Year", latest_financial["year"]]
    ]

    table = Table(
        company_table,
        colWidths=[2.3 * inch, 3.5 * inch]
    )

    table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(table)

    story.append(
        Spacer(
            1,
            0.25 * inch
        )
    )

    # ======================================================
    # FINANCIAL SUMMARY
    # ======================================================

    story.append(
        Paragraph(
            "2. Financial Summary",
            heading_style
        )
    )

    summary = [

        [
            "Net Profit Margin (%)",
            safe_value(
                latest_financial["net_profit_margin_pct"]
            )
        ],

        [
            "Operating Margin (%)",
            safe_value(
                latest_financial["operating_profit_margin_pct"]
            )
        ],

        [
            "Return on Equity (%)",
            safe_value(
                latest_financial["return_on_equity_pct"]
            )
        ],

        [
            "ROCE (%)",
            safe_value(
                latest_financial["return_on_capital_employed_pct"]
            )
        ],

        [
            "Debt to Equity",
            safe_value(
                latest_financial["debt_to_equity"]
            )
        ],

        [
            "Interest Coverage",
            safe_value(
                latest_financial["interest_coverage"]
            )
        ],

        [
            "Composite Quality Score",
            safe_value(
                latest_financial["composite_quality_score"]
            )
        ]

    ]

    summary_table = Table(
        summary,
        colWidths=[3.5 * inch, 2.0 * inch]
    )

    summary_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.beige),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(summary_table)

    story.append(
        Spacer(
            1,
            0.30 * inch
        )
    )

    # ======================================================
    # Part 2 continues here...
    # ======================================================

    # ======================================================
    # 3. CASH FLOW ANALYSIS
    # ======================================================

    story.append(
        Paragraph(
            "3. Cash Flow Analysis",
            heading_style
        )
    )

    if latest_cashflow is not None:

        cashflow_table = [

            ["Free Cash Flow (Cr)",
            safe_value(latest_cashflow["free_cash_flow_cr"])],

            ["Cash From Operations (Cr)",
            safe_value(latest_cashflow["cash_from_operations_cr"])],

            ["CapEx (Cr)",
            safe_value(latest_financial["capex_cr"])],

            ["CFO / PAT Ratio",
            safe_value(latest_cashflow["cfo_pat_ratio"])],

            ["Cash Flow Health",
            safe_value(latest_cashflow["cash_quality_label"])],

            ["FCF Positive",
            "YES" if latest_cashflow["fcf_positive_flag"] else "NO"]

        ]

        table = Table(
            cashflow_table,
            colWidths=[3.5 * inch, 2.0 * inch]
        )

        table.setStyle(
            TableStyle([
                ("GRID",(0,0),(-1,-1),0.5,colors.grey),
                ("BACKGROUND",(0,0),(0,-1),colors.lightgreen),
                ("BOTTOMPADDING",(0,0),(-1,-1),6)
            ])
        )

        story.append(table)

    else:

        story.append(
            Paragraph(
                "Cashflow intelligence unavailable.",
                normal_style
            )
        )

    story.append(
        Spacer(
            1,
            0.25 * inch
        )
    )

    # ======================================================
    # 4. PEER COMPARISON
    # ======================================================

    story.append(
        Paragraph(
            "4. Peer Comparison",
            heading_style
        )
    )

    peer = peer_percentiles[
        peer_percentiles["company_id"] == company_id
    ]

    peer = peer.sort_values(
        "metric"
    )

    peer_rows = [
        ["Metric", "Sector Percentile"]
    ]

    for _, row in peer.iterrows():

        peer_rows.append([
            row["metric"],
            f"{row['percentile_rank']:.1f}%"
        ])

    peer_table = Table(
        peer_rows,
        colWidths=[3.8 * inch, 2.0 * inch]
    )

    peer_table.setStyle(
        TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,colors.grey),
            ("BACKGROUND",(0,0),(-1,0),colors.lightblue),
            ("BOTTOMPADDING",(0,0),(-1,-1),6)
        ])
    )

    story.append(peer_table)

    story.append(
        Spacer(
            1,
            0.30 * inch
        )
    )

    # ======================================================
    # 5. AI INVESTMENT SUMMARY
    # ======================================================

    story.append(
        Paragraph(
            "5. AI Investment Summary",
            heading_style
        )
    )

    score = latest_financial["composite_quality_score"]

    de = latest_financial["debt_to_equity"]

    roe = latest_financial["return_on_equity_pct"]

    fcf = latest_cashflow["fcf_positive_flag"] if latest_cashflow is not None else 0

    strengths = []

    weaknesses = []

    if roe >= 20:
        strengths.append("High Return on Equity")

    else:
        weaknesses.append("Low ROE")

    if de <= 0.5:
        strengths.append("Low Debt")

    else:
        weaknesses.append("Debt Level Elevated")

    if fcf == 1:
        strengths.append("Positive Free Cash Flow")

    else:
        weaknesses.append("Negative Free Cash Flow")

    if score >= 80:

        recommendation = "BUY"

    elif score >= 60:

        recommendation = "HOLD"

    else:

        recommendation = "SELL"

    story.append(
        Paragraph(
            f"<b>Composite Quality Score:</b> {score:.2f}/100",
            normal_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Recommendation:</b> {recommendation}",
            normal_style
        )
    )

    story.append(
        Spacer(
            1,
            0.15 * inch
        )
    )

    story.append(
        Paragraph(
            "<b>Strengths</b>",
            normal_style
        )
    )

    for s in strengths:

        story.append(
            Paragraph(
                f"• {s}",
                normal_style
            )
        )

    story.append(
        Spacer(
            1,
            0.10 * inch
        )
    )

    story.append(
        Paragraph(
            "<b>Weaknesses</b>",
            normal_style
        )
    )

    for w in weaknesses:

        story.append(
            Paragraph(
                f"• {w}",
                normal_style
            )
        )

    story.append(
        Spacer(
            1,
            0.30 * inch
        )
    )

    # ======================================================
    # 6. RISK ANALYSIS
    # ======================================================

    story.append(
        Paragraph(
            "6. Risk Analysis",
            heading_style
        )
    )

    if de < 0.5:

        debt_risk = "Low"

    elif de < 1:

        debt_risk = "Moderate"

    else:

        debt_risk = "High"

    if score >= 80:

        overall_risk = "Low"

    elif score >= 60:

        overall_risk = "Moderate"

    else:

        overall_risk = "High"

    risk_table = [

        ["Debt Risk", debt_risk],

        ["Cash Flow",
        "Healthy" if fcf else "Weak"],

        ["Overall Financial Risk",
        overall_risk]

    ]

    risk_pdf = Table(
        risk_table,
        colWidths=[3.5 * inch,2.0 * inch]
    )

    risk_pdf.setStyle(
        TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,colors.grey),
            ("BACKGROUND",(0,0),(0,-1),colors.pink),
            ("BOTTOMPADDING",(0,0),(-1,-1),6)
        ])
    )

    story.append(risk_pdf)

    story.append(
        Spacer(
            1,
            0.30 * inch
        )
    )

    # ======================================================
    # 7. REPORT END
    # ======================================================

    story.append(
        Paragraph(
            "<b>End of Automated Financial Report</b>",
            title_style
        )
    )

    document.build(story)

    print(f"Generated: {pdf_path}")


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    build_company_report("TCS")