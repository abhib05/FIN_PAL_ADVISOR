def calculate(params: dict) -> dict:
    """
    Standard reducing-balance EMI formula.

    Params:
        principal: float
        annual_rate: float  (percentage, e.g. 12 for 12% p.a.)
        tenure_months: int
    """
    principal = float(params["principal"])
    annual_rate = float(params["annual_rate"])
    tenure = int(params["tenure_months"])

    if annual_rate == 0:
        emi = principal / tenure
        total_interest = 0.0
    else:
        r = annual_rate / 12 / 100
        emi = principal * r * (1 + r) ** tenure / ((1 + r) ** tenure - 1)
        total_interest = emi * tenure - principal

    return {
        "emi": round(emi, 2),
        "total_interest": round(total_interest, 2),
        "total_amount_paid": round(emi * tenure, 2),
        "principal": principal,
        "tenure_months": tenure,
        "annual_rate_pct": annual_rate,
        "affordability_note": (
            "A common guideline: a single large-ticket EMI should not exceed ~7-8% of monthly income; "
            "combined EMI burden across all loans ideally stays under ~35-40% of monthly income."
        ),
    }
