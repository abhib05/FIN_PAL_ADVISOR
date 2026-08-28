# Educational, category-level only. Never names specific funds, AMCs, or stocks.
# Compliance boundary: describe how instrument *types* work — never "put X% in Y fund".

_INSTRUMENTS = {
    "ppf": {
        "full_name": "Public Provident Fund (PPF)",
        "liquidity": "Low — 15-year lock-in; partial withdrawal allowed after year 7",
        "regulatory_body": "Government of India / Ministry of Finance",
        "typical_risk": "Very low (sovereign guarantee)",
        "tax_treatment": "EEE — contributions, interest, and maturity are all tax-free",
        "notes": "Good for long-term, tax-free corpus. Lock-in makes it illiquid for short-term needs.",
    },
    "elss": {
        "full_name": "Equity-Linked Savings Scheme (ELSS)",
        "liquidity": "Low — 3-year lock-in per investment",
        "regulatory_body": "SEBI-regulated mutual fund",
        "typical_risk": "Moderate to high (equity exposure)",
        "tax_treatment": "Deduction under 80C; LTCG above ₹1 lakh taxable at 10%",
        "notes": "Shortest lock-in among 80C instruments. Returns not guaranteed.",
    },
    "mutual_fund": {
        "full_name": "Mutual Fund (general — open-ended equity/debt/hybrid)",
        "liquidity": "High for open-ended funds — redeem within 1-3 business days",
        "regulatory_body": "SEBI-regulated",
        "typical_risk": "Varies by category: debt (low-moderate), hybrid (moderate), equity (moderate-high)",
        "tax_treatment": "STCG/LTCG depends on fund type and holding period",
        "notes": "Returns not guaranteed. Past performance does not predict future returns.",
    },
    "fd": {
        "full_name": "Fixed Deposit (FD)",
        "liquidity": "Moderate — premature withdrawal allowed with a penalty (typically 0.5-1%)",
        "regulatory_body": "RBI-regulated (bank FDs); DICGC insured up to ₹5 lakh per depositor per bank",
        "typical_risk": "Very low",
        "tax_treatment": "Interest is taxable as income; TDS applies above ₹40,000/year (₹50,000 for seniors)",
        "notes": "Good for capital preservation. Returns fixed but eroded by inflation over long periods.",
    },
    "nps": {
        "full_name": "National Pension System (NPS)",
        "liquidity": "Very low — primarily a retirement product; partial withdrawal only under specific conditions",
        "regulatory_body": "PFRDA-regulated",
        "typical_risk": "Varies by asset allocation chosen (equity / corporate bonds / government securities)",
        "tax_treatment": "Additional ₹50,000 deduction under 80CCD(1B) beyond the 80C limit; 60% of corpus tax-free at maturity",
        "notes": "Useful for retirement planning. Long lock-in — not suitable as a liquid investment.",
    },
    "chit_fund": {
        "full_name": "Chit Fund",
        "liquidity": "Variable — depends on when you bid; early exit can mean a loss",
        "regulatory_body": "Regulated under the Chit Funds Act 1982; enforcement varies widely by state",
        "typical_risk": "Moderate to high — counterparty risk depends on organiser reliability",
        "tax_treatment": "Dividend received is taxable; foreman commission is a cost",
        "notes": (
            "Returns can be comparable to FDs if the fund is well-run and registered. "
            "Key risk: if the organiser is not registered or defaults, recovery is difficult. "
            "Always verify registration before joining."
        ),
    },
    "stocks": {
        "full_name": "Direct Equity / Stocks",
        "liquidity": "High — listed shares can be sold on any trading day",
        "regulatory_body": "SEBI-regulated; traded on NSE/BSE",
        "typical_risk": "High — individual stock prices can fall significantly",
        "tax_treatment": "STCG (held < 1 year): 20%; LTCG (held > 1 year) above ₹1.25 lakh: 12.5%",
        "notes": (
            "Returns entirely depend on individual stock performance. "
            "Requires research and risk tolerance. "
            "Diversification (e.g., via index funds) reduces single-stock risk."
        ),
    },
}


def calculate(params: dict) -> dict:
    """
    Return educational, category-level facts about an investment instrument type.

    Params:
        instrument: str  — one of: ppf, elss, mutual_fund, fd, nps, chit_fund, stocks
    """
    key = params["instrument"].lower().replace(" ", "_").replace("-", "_")
    if key not in _INSTRUMENTS:
        available = list(_INSTRUMENTS.keys())
        raise ValueError(f"Unknown instrument {key!r}. Available: {available}")

    info = _INSTRUMENTS[key]
    return {
        **info,
        "disclaimer": (
            "This is educational information about how this instrument type works in general. "
            "It is not a recommendation to invest or not invest. "
            "For personalised advice, consult a SEBI-registered investment advisor."
        ),
    }
