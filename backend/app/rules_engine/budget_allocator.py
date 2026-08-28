def calculate(params: dict) -> dict:
    """
    50-30-20 budget allocation calculator.

    Params:
        monthly_income: float           (total monthly inflow)
        needs_amount: float             (optional — actual spending on needs)
        wants_amount: float             (optional — actual spending on wants)
        savings_debt_amount: float      (optional — actual savings + debt repayments)
    """
    income = float(params.get("monthly_income", 0))
    if income <= 0:
        return {"error": "monthly_income must be greater than 0"}

    target_needs = round(income * 0.50, 2)
    target_wants = round(income * 0.30, 2)
    target_savings = round(income * 0.20, 2)

    result = {
        "monthly_income": income,
        "50_30_20_targets": {
            "needs_50pct": target_needs,
            "wants_30pct": target_wants,
            "savings_or_debt_20pct": target_savings,
        },
        "disclaimer": (
            "50-30-20 is a guideline, not a rule. For students with debt, redirect the 20% "
            "to debt repayment first before investing. Adjust targets to your actual situation."
        ),
    }

    actual_needs = params.get("needs_amount")
    actual_wants = params.get("wants_amount")
    actual_savings = params.get("savings_debt_amount")

    if actual_needs is not None or actual_wants is not None or actual_savings is not None:
        analysis = {}
        if actual_needs is not None:
            needs = float(actual_needs)
            needs_pct = round(needs / income * 100, 1)
            needs_gap = round(needs - target_needs, 2)
            analysis["needs"] = {
                "actual": needs,
                "actual_pct": needs_pct,
                "target": target_needs,
                "target_pct": 50,
                "gap": needs_gap,
                "status": "over_budget" if needs_gap > 0 else "on_track",
            }
        if actual_wants is not None:
            wants = float(actual_wants)
            wants_pct = round(wants / income * 100, 1)
            wants_gap = round(wants - target_wants, 2)
            analysis["wants"] = {
                "actual": wants,
                "actual_pct": wants_pct,
                "target": target_wants,
                "target_pct": 30,
                "gap": wants_gap,
                "status": "over_budget" if wants_gap > 0 else "on_track",
            }
        if actual_savings is not None:
            savings = float(actual_savings)
            savings_pct = round(savings / income * 100, 1)
            savings_gap = round(target_savings - savings, 2)
            analysis["savings_or_debt"] = {
                "actual": savings,
                "actual_pct": savings_pct,
                "target": target_savings,
                "target_pct": 20,
                "shortfall": max(0, savings_gap),
                "status": "below_target" if savings_gap > 0 else "on_track",
            }
        result["actual_vs_target"] = analysis

    return result
