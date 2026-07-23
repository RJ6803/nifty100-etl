import sys
from pathlib import Path
from xml.sax.saxutils import escape
import traceback
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)

from src.reports.charts import (
    revenue_chart,
    profit_chart,
    roe_roce_chart,
    balance_sheet_chart,
    cashflow_waterfall_chart,
)
# ----------------------------------------------------------
# Project Modules
# ----------------------------------------------------------

from src.reports.data_loader import (
    load_company,
    load_all_companies,
    load_ratios,
    load_profit_loss,
    load_balance_sheet,
    load_cashflow,
    load_pros_cons,
    load_cashflow_intelligence,
)

from src.reports.summary_generator import generate_summary
from src.reports.recommendation import get_recommendation

# ----------------------------------------------------------
# Output Folder
# ----------------------------------------------------------

REPORT_DIR = Path("reports/tearsheets")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------
# Styles
# ----------------------------------------------------------

styles = getSampleStyleSheet()

SECTION_STYLE = ParagraphStyle(
    "SECTION",
    parent=styles["Heading2"],
    textColor=colors.darkblue,
    spaceAfter=8,
)

BODY_STYLE = ParagraphStyle(
    "BODY",
    parent=styles["BodyText"],
    leading=15,
)

# ----------------------------------------------------------
# Helper
# ----------------------------------------------------------

def fmt(value, suffix=""):
    try:
        if pd.isna(value):
            return "N/A"
        return f"{float(value):,.2f}{suffix}"
    except Exception:
        return "N/A"

# ----------------------------------------------------------
# KPI Cards
# ----------------------------------------------------------

def kpi_cards(company, intelligence, ratios):

    if ratios.empty:
        return Paragraph("No financial ratio data available.", BODY_STYLE)

    valid = ratios.dropna(
            subset=[
                "return_on_equity_pct",
                "return_on_capital_employed_pct",
                "debt_to_equity",
            ]
        )

    if valid.empty:
        return Paragraph("Financial ratio data not available.", BODY_STYLE)
    latest = valid.iloc[-1]

    cards = [
        ("ROE", fmt(latest.get("return_on_equity_pct"), "%")),
        ("ROCE", fmt(latest.get("return_on_capital_employed_pct"), "%")),
        ("Debt / Equity", fmt(latest.get("debt_to_equity"))),
        ("Revenue CAGR", fmt(latest.get("revenue_cagr_5yr"), "%")),
        ("FCF Conversion", fmt(intelligence.get("fcf_conversion_pct"), "%")),
        ("Quality Score", fmt(company.get("composite_quality_score_raw"))),
            ]

    rows = []

    for i in range(0, len(cards), 3):

        row = []

        for title, value in cards[i:i+3]:

            row.append(
                Paragraph(
                    f"<b>{title}</b><br/><font color='darkblue' size='14'>{value}</font>",
                    BODY_STYLE,
                )
            )

        rows.append(row)

    table = Table(
        rows,
        colWidths=[2.1 * inch] * 3,
        rowHeights=[0.8 * inch] * len(rows),
    )

    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    return table


# ----------------------------------------------------------
# Company Profile
# ----------------------------------------------------------

def company_profile(company):

    rows = [

        ["Company", company.get("company_name","N/A")],
        ["Sector", company.get("broad_sector","N/A")],
        ["Industry", company.get("sub_sector","N/A")],

        ["Market Cap (₹ Cr)", fmt(company.get("market_cap_crore"))],

        ["P/E Ratio", fmt(company.get("pe_ratio"))],

        ["P/B Ratio", fmt(company.get("pb_ratio"))],

        ["Dividend Yield", fmt(company.get("dividend_yield_pct"), "%")],

    ]

    table = Table(
        rows,
        colWidths=[2.3 * inch, 3.9 * inch],
    )

    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF2F8")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    return table

# ----------------------------------------------------------
# Recommendation Table
# ----------------------------------------------------------

def recommendation_table(recommendation, risk, confidence, color):

    rows = [
        ["Recommendation", recommendation],
        ["Risk Level", risk],
        ["Confidence", confidence],
    ]

    table = Table(
        rows,
        colWidths=[2.4 * inch, 3.8 * inch],
    )

    style = TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF2F8")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (1, 0), (1, 0), color),
        ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])

    if risk == "LOW":
        risk_color = colors.darkgreen
    elif risk == "MODERATE":
        risk_color = colors.orange
    else:
        risk_color = colors.red

    style.add("TEXTCOLOR", (1, 1), (1, 1), risk_color)

    if confidence == "HIGH":
        conf_color = colors.darkgreen
    elif confidence == "MEDIUM":
        conf_color = colors.orange
    else:
        conf_color = colors.red

    style.add("TEXTCOLOR", (1, 2), (1, 2), conf_color)

    table.setStyle(style)

    return table


# ----------------------------------------------------------
# Financial Health Table
# ----------------------------------------------------------


def safe_number(value, default=0.0):
    import math
    import pandas as pd

    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    try:
        value = float(value)
    except Exception:
        return default

    if math.isnan(value):
        return default

    return value


def financial_health_table(company, ratios, intelligence):

    if ratios.empty:
        return Paragraph(
            "Financial health data unavailable.",
            BODY_STYLE
        )
    latest = ratios.iloc[-1]

    print("Company:", company.get("symbol", company.get("company_name", "Unknown")))


    def grade_color(label):

        if label in ["Strong", "Cheap"]:
            return colors.darkgreen

        if label in ["Moderate", "Fair"]:
            return colors.orange

        return colors.red

    # ---------------- Profitability ----------------
    roe = safe_number(latest.get("return_on_equity_pct"))

    if roe == 0:
        roe = safe_number(latest.get("return_on_capital_employed_pct"))
    growth_rate = safe_number(latest.get("revenue_cagr_5yr"))
    cfo = safe_number(latest.get("cfo_pat_ratio"))

    if cfo == 0:
        cfo = 1 if latest.get("fcf_positive_flag")==1 else 0.5

    if roe >= 20:
        profitability = "Strong"
    elif roe >= 12:
        profitability = "Moderate"
    else:
        profitability = "Weak"

    # ---------------- Growth ----------------
    
    if growth_rate >= 10:
        growth = "Strong"
    elif growth_rate >= 5:
        growth = "Moderate"
    else:
        growth = "Weak"

    # ---------------- Cash Flow ----------------

    if cfo >= 1:
        cashflow = "Strong"
    elif cfo >= 0.8:
        cashflow = "Moderate"
    else:
        cashflow = "Weak"

    # ---------------- Leverage ----------------

    de = safe_number(latest.get("debt_to_equity"))

    if de == 0:
        de = safe_number(latest.get("total_debt_cr"))

    if de <= 0.5:
        leverage = "Strong"
    elif de <= 1:
        leverage = "Moderate"
    else:
        leverage = "Weak"

    # ---------------- Valuation ----------------

    pe = safe_number(company.get("pe_ratio"))

    if pe <= 25:
        valuation = "Cheap"
    elif pe <= 40:
        valuation = "Fair"
    else:
        valuation = "Expensive"

    rows = [
        ["Profitability", profitability],
        ["Growth", growth],
        ["Cash Flow", cashflow],
        ["Leverage", leverage],
        ["Valuation", valuation],
    ]

    table = Table(
        rows,
        colWidths=[2.8 * inch, 2.8 * inch],
    )

    style = TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF2F8")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("WORDWRAP", (0, 0), (-1, -1), True),
    ])

    for r in range(len(rows)):
        style.add(
            "TEXTCOLOR",
            (1, r),
            (1, r),
            grade_color(rows[r][1]),
        )

    table.setStyle(style)

    return table

# ----------------------------------------------------------
# Page 1
# ----------------------------------------------------------

def page_one(
    story,
    company,
    ratios,
    intelligence,
    pnl,
    revenue_img,
    profit_img,
    roe_roce_img,
):

    # -----------------------------
    # Header
    # -----------------------------

    header = Table(
        [[
            Paragraph(
                # ReportLab's paragraph markup must have perfectly balanced
                # tags.  Keep colour in the style instead of nesting <font>
                # tags around a line break, and escape company-supplied text.
                f"<b>{escape(str(company.get('company_name') or 'Unknown'))}</b>"
                f"<br/><font size='12'>{escape(str(company.get('company_id') or 'N/A'))}</font>",
                ParagraphStyle(
                    "TearsheetHeader",
                    parent=styles["BodyText"],
                    textColor=colors.white,
                    fontSize=18,
                    leading=22,
                ),
            )
        ]],
        colWidths=[6.8*inch]
    )

    header.setStyle(
        TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#17365D")),
            ("LEFTPADDING",(0,0),(-1,-1),15),
            ("TOPPADDING",(0,0),(-1,-1),14),
            ("BOTTOMPADDING",(0,0),(-1,-1),14),
            ("WORDWRAP",(0,0),(-1,-1),True),
        ])
    )

    story.append(header)
    story.append(Spacer(1,15))
    story.append(Spacer(1, 2))

    # -----------------------------
    # KPI Cards
    # -----------------------------

    story.append(
        Paragraph(
            "Key Financial Metrics",
            SECTION_STYLE,
        )
    )

    story.append(
        kpi_cards(
            company,
            intelligence,
            ratios,
        )
    )

    story.append(Spacer(1, 0.10 * inch))

    # -----------------------------
    # Company Profile
    # -----------------------------

    story.append(
        Paragraph(
            "Company Profile",
            SECTION_STYLE,
        )
    )

    story.append(
        company_profile(company)
    )

    story.append(Spacer(1, 2))

    # -----------------------------
    # Financial Performance
    # -----------------------------

    story.append(
        Paragraph(
            "Financial Performance",
            SECTION_STYLE,
        )
    )

    charts = Table(
        [
            [
                Image(
                    revenue_img,
                    width=2.6 * inch,
                    height=1.5 * inch,
                ),
                Image(
                    profit_img,
                    width=2.6 * inch,
                    height=1.5 * inch,
                ),
            ]
        ],
        colWidths=[3.2 * inch, 3.2 * inch],
    )

    charts.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )

    story.append(charts)
    
    comparison = Table(
        [[
            Image(
                roe_roce_img,
                width=5.8 * inch,
                height=1.6 * inch,
            )
        ]],
        colWidths=[6.3 * inch]
    )

    comparison.setStyle(
        TableStyle([
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"TOP")
        ])
    )

    story.append(comparison)
    story.append(Spacer(1,4))

    return story

# ----------------------------------------------------------
# Page 2
# ----------------------------------------------------------

def page_two(
    story,
    company,
    ratios,
    intelligence,
    pros_cons,
    recommendation,
    risk,
    confidence,
    color,
    reason,
    adjusted_score,
    balance_sheet_img,
    cashflow_img,
):

    # -------------------------------------------------
    # AI Investment Summary
    # -------------------------------------------------

    story.append(
        Paragraph(
            "AI Investment Summary",
            SECTION_STYLE,
        )
    )

    if pros_cons is None or pros_cons.empty:
        pros_cons = pd.DataFrame(columns=["type","text"])

    pros_records = pros_cons[pros_cons["type"] == "pro"]["text"].tolist()
    cons_records = pros_cons[pros_cons["type"] == "con"]["text"].tolist()

    summary_data = generate_summary(
        company,
        ratios,
        intelligence,
        pros=pros_records,
        cons=cons_records,
        recommendation=recommendation
    )

    summary = summary_data.get(
        "summary",
        "Summary unavailable."
    )
    story.append(
        Paragraph(
            summary,
            BODY_STYLE,
        )
    )

    story.append(Spacer(1, 2))

   # -------------------------------------------------
    # Pros & Cons (Side by Side)
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Pros & Cons",
            SECTION_STYLE,
        )
    )

    pros = pros_cons[pros_cons["type"] == "pro"].head(6)
    cons = pros_cons[pros_cons["type"] == "con"].head(6)

    pros_text = "<br/>".join(
        [f"• {x}" for x in pros["text"]]
    ) or "No major positives."

    cons_text = "<br/>".join(
        [f"• {x}" for x in cons["text"]]
    ) or "No major negatives."

    pros_cons_table = Table(
        [[
            Paragraph("<b><font color='green'>Pros</font></b><br/><br/>" + pros_text, BODY_STYLE),
            Paragraph("<b><font color='red'>Cons</font></b><br/><br/>" + cons_text, BODY_STYLE),
        ]],
        colWidths=[3.1*inch,3.1*inch]
    )

    pros_cons_table.setStyle(
        TableStyle([
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("GRID",(0,0),(-1,-1),0.25,colors.lightgrey),
            ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ])
    )

    story.append(pros_cons_table)

    story.append(Spacer(1,6))

    # -------------------------------------------------
    # Recommendation
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Investment Recommendation",
            SECTION_STYLE,
        )
    )

    story.append(
        recommendation_table(
            recommendation,
            risk,
            confidence,
            color,
        )
    )

    story.append(Spacer(1,6))

    story.append(
        Paragraph(
            f"<b>Recommendation Reason:</b><br/>{reason}",
            BODY_STYLE
        )
    )

    story.append(Spacer(1,6))
    
    story.append(
        Paragraph(
            f"<b>Adjusted Score:</b> {adjusted_score:.1f}",
            BODY_STYLE,
        )
    )
    story.append(Spacer(1, 6))

    story.append(
        Paragraph(
            "Balance Sheet & Cash Flow",
            SECTION_STYLE,
        )
    )

    charts = Table(
        [[
            Image(
                balance_sheet_img,
                width=3.0*inch,
                height=1.6*inch,
            ),
            Image(
                cashflow_img,
                width=3.0*inch,
                height=1.6*inch,
            ),
        ]],
        colWidths=[3.1*inch,3.1*inch]
    )

    charts.setStyle(
        TableStyle([
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
        ])
    )

    story.append(charts)

    story.append(Spacer(1,6))

    # -------------------------------------------------
    # Financial Health
    # -------------------------------------------------

    story.append(
        Paragraph(
            "Financial Health",
            SECTION_STYLE,
        )
    )

    story.append(

        financial_health_table(
            company,
            ratios,
            intelligence,
        )

    )

    story.append(Spacer(1,2))

    story.append(
        Paragraph(
            "Capital Allocation",
            SECTION_STYLE,
        )
    )

    badge = Table(
        [[intelligence.get("capital_allocation_label","Not Available")]],
        colWidths=[4.5 * inch],
    )

    badge.setStyle(
        TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#D9EAD3")),
            ("TEXTCOLOR",(0,0),(-1,-1),colors.darkgreen),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),12),
            ("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("TOPPADDING",(0,0),(-1,-1),8),
        ])
    )

    story.append(badge)

    return story
# ----------------------------------------------------------
# Build Complete Tear Sheet
# ----------------------------------------------------------

def build_pdf(company_id):

    print("Generating Tear Sheet...")

    # -----------------------------
    # Load Data
    # -----------------------------

    company = load_company(company_id)

    ratios = load_ratios(company_id)

    pnl = load_profit_loss(company_id)

    bs = load_balance_sheet(company_id)

    cf = load_cashflow(company_id)

    pros_cons = load_pros_cons(company_id)

    intelligence = load_cashflow_intelligence(company_id)

    if company is None or company.empty:
        raise ValueError("Company not found")

    company = company.iloc[-1]

    if intelligence is None or intelligence.empty:
        print(f"[WARNING] Cashflow intelligence missing for {company_id}")

        intelligence = pd.DataFrame([{
            "fcf_conversion_pct": 0,
            "capital_allocation_label": "Not Available",
            "cashflow_strength": "Unknown",
            "cashflow_score": 50,
            "cashflow_summary": "Cashflow intelligence not available."
        }])

    intelligence = intelligence.iloc[0]

    # -----------------------------
    # Create Charts
    # -----------------------------
    if pnl is None:
        pnl = pd.DataFrame()
    revenue_img = revenue_chart(pnl, company_id)

    profit_img = profit_chart(pnl, company_id)

    #roe_img = roe_chart(ratios, company_id)
    #roce_img = roce_chart(ratios, company_id)

    roe_roce_img = roe_roce_chart(
        ratios,
        company_id
    )
    if bs is None:
        bs = pd.DataFrame()
    balance_sheet_img = balance_sheet_chart(bs, company_id)
    if cf is None:
        cf = pd.DataFrame()
    cashflow_img = cashflow_waterfall_chart(cf, company_id)

    # -----------------------------
    # Recommendation
    # -----------------------------

    score = safe_number(company.get("composite_quality_score_raw"))

    pros_count = len(
        pros_cons[pros_cons["type"]=="pro"]
    )

    cons_count = len(
        pros_cons[pros_cons["type"]=="con"]
    )

    rec = get_recommendation(
        score,
        pros_count,
        cons_count,
        intelligence.get("cfo_quality_label", "Unknown")
    )

    recommendation = rec.get("recommendation","HOLD")
    risk = rec.get("risk","MEDIUM")
    confidence = rec.get("confidence","LOW")
    color = rec.get("color",colors.black)
    reason = rec.get("reason","No reason available.")
    adjusted_score = rec.get("adjusted_score",0)

    # -----------------------------
    # PDF
    # -----------------------------

    pdf = REPORT_DIR / f"{company_id}_tearsheet.pdf"

    doc = SimpleDocTemplate(
        str(pdf),
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25,
    )

    story = []

    # -----------------------------
    # Page 1
    # -----------------------------

    page_one(
        story,
        company,
        ratios,
        intelligence,
        pnl,
        revenue_img,
        profit_img,
        roe_roce_img,
    )

    # -----------------------------
    # Page 2
    # -----------------------------

    page_two(
        story,
        company,
        ratios,
        intelligence,
        pros_cons,
        recommendation,
        risk,
        confidence,
        color,
        reason,
        adjusted_score,
        balance_sheet_img,
        cashflow_img,
    )

    # -----------------------------
    # Build PDF
    # -----------------------------

    doc.build(story)

    print()

    print("Tear sheet saved to:")

    print(pdf)

# ==========================================================
# Batch Generation
# ==========================================================

def batch_generate():

    companies = load_all_companies()

    skipped = []

    total = len(companies)

    print(f"\nGenerating {total} tear sheets...\n")

    for i, company_id in enumerate(companies, start=1):

        try:

            ratios = load_ratios(company_id)

            if ratios is None or ratios.empty or len(ratios)<3:

                skipped.append(company_id)

                print(f"[{i}/{total}] Skipped {company_id}")

                continue

            build_pdf(company_id)

            print(f"[{i}/{total}] Completed {company_id}")

        except Exception as e:

            skipped.append(company_id)

            print(f"[{i}/{total}] ERROR : {company_id}")

            print(e)

    skipped_file = Path("output/skipped_tearsheets.csv")

    skipped_file.parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        {
            "company_id": skipped
        }
    ).to_csv(
        skipped_file,
        index=False,
    )

    print("----------------------------------------")

    print("Batch Generation Completed")

    print("----------------------------------------")

    print(f"Generated : {total-len(skipped)}")

    print(f"Skipped   : {len(skipped)}")

    print(f"Log File  : {skipped_file}")

    print("----------------------------------------")


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":
    batch_generate()
