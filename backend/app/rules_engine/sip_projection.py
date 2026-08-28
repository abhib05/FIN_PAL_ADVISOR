def calculate(params: dict) -> dict:
    """
    SIP (Systematic Investment Plan) future value — standard compound growth formula.

    Params:
        monthly_amount: float
        years: float
        expected_annual_return: float  (percentage, e.g. 12 for 12% p.a.)
    """
    monthly_amount = float(params["monthly_amount"])
    years = float(params["years"])
    annual_return = float(params["expected_annual_return"])

    months = years * 12
    r = annual_return / 12 / 100

    if r == 0:
        future_value = monthly_amount * months
    else:
        future_value = monthly_amount * (((1 + r) ** months - 1) / r) * (1 + r)

    total_invested = monthly_amount * months

    return {
        "future_value": round(future_value, 2),
        "total_invested": round(total_invested, 2),
        "estimated_returns": round(future_value - total_invested, 2),
        "assumptions": {
            "monthly_amount": monthly_amount,
            "years": years,
            "expected_annual_return_pct": annual_return,
        },
        "disclaimer": (
            "Estimate based on assumed returns — not a guarantee. "
            "Actual returns vary; past performance does not predict future results. "
            "Always label this as an illustration when sharing with users."
        ),
    }
