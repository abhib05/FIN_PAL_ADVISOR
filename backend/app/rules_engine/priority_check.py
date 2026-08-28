def calculate(params: dict) -> dict:
    """
    Priority ordering: determines what the user should focus on first.
    Mirrors the advisor's sequencing: safety net before growth.

    Params:
        has_high_interest_debt: bool       (APR > 15%)
        high_interest_debt_apr: float      (highest APR among debts, 0 if none)
        has_health_insurance: bool
        emergency_fund_months: float       (current savings / monthly essential expenses)
        emergency_fund_target_months: float (from emergency_fund_target calc)
        has_investments: bool
    """
    has_hi_debt = bool(params.get("has_high_interest_debt", False))
    hi_apr = float(params.get("high_interest_debt_apr", 0))
    has_insurance = bool(params.get("has_health_insurance", False))
    ef_months = float(params.get("emergency_fund_months", 0))
    ef_target = float(params.get("emergency_fund_target_months", 6))
    has_investments = bool(params.get("has_investments", False))

    priorities = []
    explanations = []

    # 1. High-interest debt
    if has_hi_debt and hi_apr > 15:
        priorities.append({
            "rank": 1,
            "action": "Pay down high-interest debt first",
            "reason": (
                f"Your highest debt APR is {hi_apr}%. Any realistic investment return is lower than this, "
                "so paying down this debt gives a guaranteed return equal to the interest rate you stop paying."
            ),
        })

    # 2. Health insurance
    if not has_insurance:
        priorities.append({
            "rank": len(priorities) + 1,
            "action": "Get health insurance coverage",
            "reason": (
                "Without health insurance, a single medical event can wipe out savings or force debt. "
                "Check if your college provides cover, or look at a low-cost student plan."
            ),
        })

    # 3. Emergency fund
    if ef_months < ef_target:
        gap_months = round(ef_target - ef_months, 1)
        priorities.append({
            "rank": len(priorities) + 1,
            "action": f"Build emergency fund to {ef_target}-month target",
            "reason": (
                f"You currently have about {ef_months:.1f} months of cover — "
                f"{gap_months} months short of your target. "
                "An emergency fund prevents you from going into debt when something unexpected happens."
            ),
        })

    # 4. Investments (only after 1-3 are addressed)
    if not priorities:
        priorities.append({
            "rank": 1,
            "action": "Ready to focus on savings and investments",
            "reason": (
                "Your high-interest debt, insurance, and emergency fund are in order — "
                "a good foundation to start building longer-term savings."
            ),
        })
    elif has_investments:
        explanations.append(
            "Note: it may be worth pausing or reducing investment contributions temporarily "
            "to address the higher-priority items above — but this is a trade-off, not a rule."
        )

    return {
        "priorities": priorities,
        "explanations": explanations,
        "disclaimer": (
            "Priority ordering based on general financial planning principles. "
            "Individual circumstances vary — this is guidance, not a directive."
        ),
    }
