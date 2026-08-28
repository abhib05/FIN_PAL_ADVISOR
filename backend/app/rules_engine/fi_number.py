def calculate(params: dict) -> dict:
    """
    FIRE-style financial independence corpus estimate.

    Params:
        annual_expenses: float
        multiplier: float  (default 25; valid range 20-30 depending on withdrawal-rate assumption)
        expected_return_pct: float  (default 7.0 — India-relevant post-tax equity estimate)
        inflation_pct: float  (default 6.5 — India long-run CPI estimate)

    Defaults are India-specific starting points — treat as configurable, not final values.
    """
    annual_expenses = float(params["annual_expenses"])
    multiplier = float(params.get("multiplier", 25))
    expected_return = float(params.get("expected_return_pct", 7.0))
    inflation = float(params.get("inflation_pct", 6.5))

    if not (20 <= multiplier <= 30):
        raise ValueError("multiplier must be between 20 and 30")

    target_corpus = annual_expenses * multiplier

    return {
        "target_corpus": round(target_corpus, 2),
        "annual_expenses": annual_expenses,
        "assumptions": {
            "multiplier": multiplier,
            "withdrawal_rate_pct": round(100 / multiplier, 2),
            "expected_return_pct": expected_return,
            "inflation_pct": inflation,
        },
        "disclaimer": (
            "Educational estimate based on the assumptions shown — not a guarantee or financial advice. "
            "India-specific defaults: ~7% post-tax equity return, ~6.5% long-run inflation. "
            "Consult a SEBI-registered investment advisor for personalized retirement planning."
        ),
    }
