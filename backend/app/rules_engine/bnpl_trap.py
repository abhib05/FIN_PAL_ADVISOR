def calculate(params: dict) -> dict:
    """
    BNPL / credit-trap risk assessment for college students.

    Params:
        bnpl_apps_used: list of str  (e.g. ["Simpl", "LazyPay"])
        typical_monthly_bnpl_amount: float
        missed_or_min_only_payments: bool
        monthly_income: float
        existing_credit_card_debt: float  (default 0)
        credit_utilization_pct: float  (default None)
    """
    apps = params.get("bnpl_apps_used", [])
    monthly_bnpl = float(params.get("typical_monthly_bnpl_amount", 0))
    missed_payments = bool(params.get("missed_or_min_only_payments", False))
    monthly_income = float(params.get("monthly_income", 0))
    cc_debt = float(params.get("existing_credit_card_debt", 0))
    utilization = params.get("credit_utilization_pct")

    risk_flags = []
    risk_score = 0  # 0-3: 0=low, 1=moderate, 2=high, 3=critical

    if missed_payments:
        risk_flags.append("Missed or minimum-only BNPL payments — late fees and credit score impact accumulate fast.")
        risk_score += 2

    if monthly_income > 0 and monthly_bnpl / monthly_income > 0.15:
        risk_flags.append(
            f"BNPL usage is {monthly_bnpl/monthly_income:.0%} of monthly income — above 15%, "
            "which leaves little room if income dips."
        )
        risk_score += 1

    if len(apps) >= 2:
        risk_flags.append(
            f"Using {len(apps)} BNPL apps simultaneously makes it easy to lose track of total dues."
        )
        risk_score += 1

    if cc_debt > 0 and monthly_bnpl > 0:
        risk_flags.append("Carrying both credit card debt and BNPL balances — high-interest compounding on multiple fronts.")
        risk_score += 1

    if utilization is not None and float(utilization) > 30:
        risk_flags.append(f"Credit utilisation at {utilization}% — above 30% starts hurting your credit score.")
        risk_score += 1

    risk_level = ["low", "moderate", "high", "critical"][min(risk_score, 3)]

    recommendations = []
    if missed_payments:
        recommendations.append("Pay the full BNPL balance this month before it converts to high-interest debt.")
    if len(apps) >= 2:
        recommendations.append("Pick one BNPL app and close the others — fewer accounts = fewer missed-due-date surprises.")
    if monthly_bnpl > 0:
        recommendations.append(
            "Treat BNPL like cash, not credit — if you can't pay it in full this month, don't buy it."
        )
    if cc_debt > 0:
        recommendations.append("Prioritise clearing credit card debt first — BNPL late fees are high but CC interest compounds daily.")

    return {
        "risk_level": risk_level,
        "risk_flags": risk_flags,
        "recommendations": recommendations,
        "bnpl_apps_count": len(apps),
        "monthly_bnpl_amount": monthly_bnpl,
        "disclaimer": (
            "Risk assessment based on general financial guidelines — not personalised advice. "
            "If debt feels unmanageable, consider speaking to a financial counsellor."
        ),
    }
