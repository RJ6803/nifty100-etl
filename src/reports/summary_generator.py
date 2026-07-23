import pandas as pd
def generate_summary(
    company,
    ratios,
    intelligence,
    pros=None,
    cons=None,
    recommendation=None
):

    valid = ratios.dropna(subset=["return_on_equity_pct"])

    if valid.empty:
        return {
            "company_name": company.get("company_name", "Unknown Company"),
            "financial_score": 0,
            "recommendation": "Not Available",
            "summary": "Financial ratio data is unavailable for this company.",
            "strengths": [],
            "risks": [],
        }
    latest = valid.iloc[-1]

    company_name = company.get("company_name", "Unknown Company")

    score = company.get("composite_quality_score_raw", 0)
    if pd.isna(score):
        score = 0

    score = float(score)
    if intelligence is None:
        intelligence = {}

    cfo = intelligence.get("cfo_quality_label", "Unknown")

    if cfo is None or str(cfo).lower() == "nan":
        cfo = "Unknown"

    if recommendation is None or str(recommendation).lower() == "nan":
        recommendation = "Not Available"
    else:
        recommendation = str(recommendation).title()

    roe = safe_float(latest.get("return_on_equity_pct"))
    roce = safe_float(latest.get("return_on_capital_employed_pct"))
    revenue = safe_float(latest.get("revenue_cagr_5yr"))
    debt = safe_float(latest.get("debt_to_equity"))

    if not pros:
        pros = ["No major financial strengths identified."]
    else:
        pros = [
            p["text"] if isinstance(p, dict) else p
            for p in pros[:3]
             if p is not None
        ]

    if not cons:
        cons = ["No major financial weaknesses identified."]
    else:
        cons = [
            p["text"] if isinstance(p, dict) else p
            for p in cons[:3]
             if p is not None
        ]

    

    # --------------------
    # Profitability
    # --------------------
    if roe >= 25:
        profitability = "excellent"
    elif roe >= 15:
        profitability = "healthy"
    else:
        profitability = "moderate"

    # --------------------
    # Capital efficiency
    # --------------------
    if roce >= 20:
        capital = "strong"
    else:
        capital = "average"

    # --------------------
    # Revenue growth
    # --------------------
    if revenue >= 15:
        growth = "rapid"
    elif revenue >= 8:
        growth = "steady"
    else:
        growth = "limited"

    # --------------------
    # Debt
    # --------------------
    if debt < 0.5:
        leverage = "conservative"
    elif debt < 1:
        leverage = "manageable"
    else:
        leverage = "elevated"

    # --------------------
    # Overall view
    # --------------------
    if score >= 80:
        verdict = "a high-quality long-term compounder."
        intro = (
            f"{company_name} is an excellent quality business with strong financial fundamentals."
        )
    elif score >= 65:
        verdict = "financially strong with manageable risks."
        intro = (
            f"{company_name} maintains healthy financial performance and stable business fundamentals."
        )
    elif score >= 50:
        verdict = "financially average and requires monitoring."
        intro = (
            f"{company_name} demonstrates average financial performance with a few areas requiring monitoring."
        )

    else:
        verdict = "financially weak with elevated investment risk."
        intro = (
            f"{company_name} currently faces multiple financial challenges that increase investment risk."
        )

    strength_text = (
        "; ".join(pros)
        if pros
        else "No major financial strengths identified."
    )

    risk_text = (
        "; ".join(cons)
        if cons
        else "No major financial weaknesses identified."
    )
    
    summary_text = (
        f"{intro} "

        f"It currently has {profitability} profitability, "
        f"{capital} capital efficiency, "
        f"{growth} revenue growth, "
        f"{str(cfo).lower()} cash-flow quality "
        f"and {leverage} leverage. "

        f"The overall financial quality score is {score:.1f}/100. "

        f"Key strengths include: {strength_text}. "

        f"Key risks include: {risk_text}. "

        f"Investment recommendation: {recommendation}. "

        f"Overall, the company appears to be {verdict}"
    )
    return {
        "company_name": company_name,
        "financial_score": score,
        "recommendation": recommendation,
        "summary": summary_text,
        "strengths": pros,
        "risks": cons,
    }

def safe_float(value):
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except:
        return 0.0