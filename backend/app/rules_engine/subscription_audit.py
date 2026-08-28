def calculate(params: dict) -> dict:
    """
    Flag recurring charges that exceed a threshold of monthly income.

    Params:
        recurring_charges: list of {label: str, amount: float}
        monthly_income: float
        flag_threshold_pct: float  (default 8.0 — flag if total > 8% of income)
    """
    charges = params["recurring_charges"]
    monthly_income = float(params["monthly_income"])
    threshold_pct = float(params.get("flag_threshold_pct", 8.0))

    total = sum(float(c["amount"]) for c in charges)
    pct_of_income = (total / monthly_income * 100) if monthly_income > 0 else 0

    flagged = [c for c in charges if float(c["amount"]) > 0]
    flagged_sorted = sorted(flagged, key=lambda c: float(c["amount"]), reverse=True)

    return {
        "total_monthly": round(total, 2),
        "pct_of_income": round(pct_of_income, 1),
        "flagged": pct_of_income > threshold_pct,
        "items": [{"label": c["label"], "amount": float(c["amount"])} for c in flagged_sorted],
        "note": (
            f"Total recurring charges are {pct_of_income:.1f}% of monthly income. "
            + ("Worth reviewing — a common guideline is keeping this under 8%."
               if pct_of_income > threshold_pct else "Within a reasonable range.")
        ),
        "disclaimer": "Observational only — this flags amounts for review, not specific cuts.",
    }
