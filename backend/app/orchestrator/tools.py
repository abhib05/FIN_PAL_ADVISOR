import json
from typing import Any

from app.rules_engine import (
    emergency_fund,
    debt_payoff,
    emi as emi_calc,
    fi_number,
    sip_projection,
    subscription_audit,
    instrument_comparison,
    bnpl_trap,
    priority_check,
    budget_allocator,
)

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "update_profile",
            "description": (
                "Persist a field from the conversation to the user's financial profile. "
                "Call this whenever the user gives you a piece of financial information."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "field": {
                        "type": "string",
                        "description": (
                            "Dot-notation path to the profile field, e.g. "
                            "'expenses.housing.amount', 'money_in.family_support_amount', "
                            "'safety_net.personal_savings_amount', 'conversation_phase'."
                        ),
                    },
                    "value": {
                        "description": "The value to set. Any JSON-compatible type.",
                    },
                },
                "required": ["field", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_calculation",
            "description": (
                "Run a deterministic financial calculation. "
                "Never compute numbers yourself — always use this tool for any math."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "emergency_fund_target",
                            "emi",
                            "debt_payoff_order",
                            "fi_number",
                            "sip_projection",
                            "subscription_audit",
                            "instrument_comparison",
                            "bnpl_trap_check",
                            "priority_check",
                            "budget_allocator",
                        ],
                        "description": "The calculation type to run.",
                    },
                    "params": {
                        "type": "object",
                        "description": "Parameters specific to the chosen calculation type.",
                    },
                },
                "required": ["type", "params"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_profile",
            "description": (
                "Retrieve the current financial profile. "
                "Call this before asking a question to avoid re-asking something the user already told you."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

_CALC_DISPATCH = {
    "emergency_fund_target": emergency_fund.calculate,
    "emi": emi_calc.calculate,
    "debt_payoff_order": debt_payoff.calculate,
    "fi_number": fi_number.calculate,
    "sip_projection": sip_projection.calculate,
    "subscription_audit": subscription_audit.calculate,
    "instrument_comparison": instrument_comparison.calculate,
    "bnpl_trap_check": bnpl_trap.calculate,
    "priority_check": priority_check.calculate,
    "budget_allocator": budget_allocator.calculate,
}


def _set_nested(d: dict, path: str, value: Any) -> dict:
    keys = path.split(".")
    current = d
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    return d


def execute_tool(name: str, arguments: dict, profile: dict) -> tuple[Any, dict]:
    """Execute a tool call and return (result, updated_profile)."""
    import logging
    _log = logging.getLogger(__name__)
    _log.info("TOOL CALL: %s %s", name, arguments)
    if name == "update_profile":
        field = arguments["field"]
        value = arguments["value"]
        _set_nested(profile, field, value)
        _log.info("PROFILE UPDATE: %s = %s", field, value)
        return {"status": "updated", "field": field, "value": value}, profile

    if name == "run_calculation":
        calc_type = arguments["type"]
        params = arguments["params"]
        if calc_type not in _CALC_DISPATCH:
            return {"error": f"Unknown calculation type: {calc_type!r}"}, profile
        try:
            result = _CALC_DISPATCH[calc_type](params)
        except (KeyError, ValueError) as e:
            return {"error": str(e)}, profile
        return result, profile

    if name == "get_profile":
        return profile, profile

    return {"error": f"Unknown tool: {name!r}"}, profile


def default_profile(user_id: str) -> dict:
    return {
        "user_id": user_id,
        "academic": {
            "year_of_study": None,
            "expected_graduation_year": None,
        },
        "money_in": {
            "family_support_amount": None,
            "family_support_regularity": None,
            "gig_income_amount": None,
            "gig_income_type": None,
            "scholarship_stipend_amount": None,
            "income_stability": None,
        },
        "expenses": {
            "housing": {"amount": None, "type": None, "family_paid_directly": None},
            "commute": {"amount": None, "mode": None, "distance_km": None},
            "food_beyond_mess": None,
            "split_shared_expenses": None,
            "subscriptions": None,
            "bnpl_usage": {
                "apps_used": None,
                "typical_monthly_amount": None,
                "missed_or_min_only": None,
            },
            "discretionary": None,
        },
        "safety_net": {
            "health_insurance_cover": None,
            "provided_by": None,
            "personal_savings_amount": None,
            "would_rely_on_if_urgent": None,
        },
        "debt": [],
        "credit": {
            "cards": None,
            "total_limit": None,
            "typical_utilization_pct": None,
        },
        "investments": [],
        "goals": [],
        "conversation_phase": "rapport",
    }
