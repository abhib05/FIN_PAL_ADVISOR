import copy


def _simulate_total_interest(debts: list[dict]) -> float:
    """Simulate total interest paid following a fixed payoff order (minimum payments only)."""
    state = copy.deepcopy(debts)
    total_interest = 0.0

    for _ in range(600):  # 50-year safety cap
        if not any(d["balance"] > 0 for d in state):
            break
        for d in state:
            if d["balance"] <= 0:
                continue
            monthly_rate = d["apr"] / 100 / 12
            interest = d["balance"] * monthly_rate
            total_interest += interest
            payment = min(d["min_payment"], d["balance"] + interest)
            d["balance"] = max(0.0, d["balance"] + interest - payment)

    return round(total_interest, 2)


def calculate(params: dict) -> dict:
    """
    Params:
        debts: list of {balance: float, apr: float, min_payment: float, label?: str}
    """
    raw = params["debts"]
    debts = []
    for i, d in enumerate(raw):
        debts.append({
            "label": d.get("label", f"Debt {i + 1}"),
            "balance": float(d["balance"]),
            "apr": float(d["apr"]),
            "min_payment": float(d["min_payment"]),
        })

    avalanche = sorted(debts, key=lambda d: d["apr"], reverse=True)
    snowball = sorted(debts, key=lambda d: d["balance"])

    interest_avalanche = _simulate_total_interest(avalanche)
    interest_snowball = _simulate_total_interest(snowball)

    high_interest = [d["label"] for d in debts if d["apr"] > 15]

    return {
        "avalanche_order": [d["label"] for d in avalanche],
        "snowball_order": [d["label"] for d in snowball],
        "total_interest_avalanche": interest_avalanche,
        "total_interest_snowball": interest_snowball,
        "interest_saved_by_avalanche": round(interest_snowball - interest_avalanche, 2),
        "high_interest_debts": high_interest,
        "guidance": (
            "Avalanche (highest APR first) saves the most money in interest. "
            "Snowball (lowest balance first) gives quicker psychological wins. "
            "Both orderings and the interest difference are shown — you choose."
        ),
        "priority_note": (
            f"{len(high_interest)} debt(s) above 15% APR flagged — "
            "consider paying these before directing money toward investments."
        ) if high_interest else None,
    }
