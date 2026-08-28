# Reconciled 3-6-12 Month Rule from advisory-logic-rules-engine.md §1
# Source: SmartPlan Finance (India) + Anshuman Sharma transcript

_STABILITY_MAP = {
    "family_supported_fixed": "salaried_private",
    "family_supported_variable": "irregular_or_business",
    "gig_variable": "irregular_or_business",
    "mixed": "irregular_or_business",
}

_BASE_MONTHS = {
    "stable_govt_or_secure": 3,
    "salaried_private": 6,
    "irregular_or_business": 12,
}


def calculate(params: dict) -> dict:
    """
    Params:
        monthly_essential_expenses: float
            Essential only — housing, food, commute, insurance premiums, minimum debt payments.
            NOT total spending including discretionary.
        employment_stability: str
            "stable_govt_or_secure" | "salaried_private" | "irregular_or_business"
            Student aliases: "family_supported_fixed" | "family_supported_variable"
                            | "gig_variable" | "mixed"
        has_dependents: bool  (default False)
        has_large_emi_burden: bool  (default False)
        current_emergency_fund_amount: float  (default 0)
    """
    monthly = float(params["monthly_essential_expenses"])
    raw_stability = params["employment_stability"]
    has_dependents = bool(params.get("has_dependents", False))
    has_large_emi = bool(params.get("has_large_emi_burden", False))
    current_savings = float(params.get("current_emergency_fund_amount", 0))

    stability = _STABILITY_MAP.get(raw_stability, raw_stability)
    if stability not in _BASE_MONTHS:
        raise ValueError(
            f"Unknown employment_stability: {raw_stability!r}. "
            f"Valid values: {list(_BASE_MONTHS) + list(_STABILITY_MAP)}"
        )

    months_buffer = _BASE_MONTHS[stability]
    if has_dependents:
        months_buffer += 1
    if has_large_emi:
        months_buffer += 1

    target = monthly * months_buffer
    gap = max(0.0, target - current_savings)

    return {
        "target": round(target, 2),
        "gap": round(gap, 2),
        "months_buffer": months_buffer,
        "current_savings": current_savings,
        "storage_guidance": (
            "Keep 1-2 months of expenses in a savings account for instant access. "
            "Park the rest in liquid mutual funds or short-term FDs — "
            "never in stocks, long-term investments, or large cash-at-home holdings."
        ),
        "disclaimer": (
            "Target uses essential expenses only (housing, food, commute, insurance premiums, "
            "minimum debt payments), not total monthly spending."
        ),
    }
