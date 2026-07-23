


def get_recommendation(
    score,
    pros_count=0,
    cons_count=0,
    cfo_quality="Unknown"
):
    if score is None:
        score = 0

    try:
        adjusted_score = float(score)
    except (TypeError, ValueError):
        adjusted_score = 0

    if pros_count >= 8:
        adjusted_score += 3
    elif pros_count >= 5:
        adjusted_score += 2

    if cons_count >= 8:
        adjusted_score -= 5
    elif cons_count >= 5:
        adjusted_score -= 3

    cfo = str(cfo_quality).lower()

    if cfo == "excellent":
        adjusted_score += 3
    elif cfo == "good":
        adjusted_score += 1
    elif cfo == "weak":
        adjusted_score -= 4
    elif cfo == "poor":
        adjusted_score -= 6

    adjusted_score = max(0, min(100, adjusted_score))
    if adjusted_score >= 80:
        recommendation = "STRONG BUY"
        risk = "LOW"
        confidence = "HIGH"
        color =  "darkgreen"
        

    elif adjusted_score >= 65:
        
        recommendation = "BUY"
        risk = "LOW"
        confidence = "HIGH"
        color = "green"

    elif adjusted_score >= 50:
        recommendation = "HOLD"
        risk = "MODERATE"
        confidence = "MEDIUM"
        color = "orange"
        

    elif adjusted_score >= 35:
        recommendation = "REDUCE"
        risk = "HIGH"
        confidence = "LOW"
        color = "red"
        

    else:
        recommendation = "AVOID"
        risk = "VERY HIGH"
        confidence = "LOW"
        color = "darkred"

    reason = (
        f"The recommendation is based on an adjusted financial score of "
        f"{adjusted_score:.1f}/100, supported by {pros_count} identified strengths, "
        f"{cons_count} identified risks, and cash-flow quality rated as "
        f"{cfo_quality}."
    )

    return {
        "recommendation": recommendation,
        "risk": risk,
        "confidence": confidence,
        "color": color,
        "reason": reason,
        "adjusted_score": adjusted_score,
    }