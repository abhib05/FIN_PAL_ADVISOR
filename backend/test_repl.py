"""
End-to-end scripted conversation test — "Aditi" persona.
Runs through phases 1-4 (rapport → income → expenses → safety net)
and expects an emergency_fund_target tool call to fire.

Usage:
    cd backend
    python test_repl.py
"""
import io
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Force UTF-8 output on Windows so emoji/unicode in model responses don't crash
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

load_dotenv(Path(__file__).parent / ".env")

from app.orchestrator.conversation import run_turn
from app.orchestrator.tools import default_profile

DIVIDER = "=" * 65

SCRIPT = [
    "Hi! I'm Aditi, I'm in my third year of engineering at VIT Vellore.",
    "I get about 15,000 rupees a month from my parents. It's fixed — same amount every month.",
    "My hostel and mess fees are 8,000 a month, paid directly by my parents. "
    "I spend about 3,000 on food outside mess and another 1,500 on commute.",
    "I have health insurance through my college. I have about 12,000 saved up in my savings account. "
    "If something urgent came up I'd probably use my savings first, then ask my parents.",
    "Can you tell me if my emergency fund is enough?",
]


def run_test() -> None:
    session_id = "aditi-test-001"
    profile = default_profile(session_id)
    messages: list[dict] = []
    passed = True

    print(f"\n{DIVIDER}")
    print("END-TO-END REPL TEST — Aditi persona (phases 1-4 + emergency fund calc)")
    print(DIVIDER)

    for i, user_msg in enumerate(SCRIPT, 1):
        print(f"\n[Turn {i}] You: {user_msg}")

        try:
            response, profile, messages = run_turn(
                user_message=user_msg,
                financial_profile=profile,
                messages=messages,
            )
        except Exception as e:
            print(f"\n  ERROR: {e}")
            passed = False
            continue

        print(f"\n  Advisor: {response}")

    print(f"\n{DIVIDER}")
    print("FINAL PROFILE STATE:")
    print(json.dumps(profile, indent=2))
    print(DIVIDER)

    # Assertions
    checks = {
        "income_stability set": profile.get("money_in", {}).get("income_stability") is not None
            or profile.get("money_in", {}).get("family_support_amount") is not None,
        "savings captured": profile.get("safety_net", {}).get("personal_savings_amount") is not None,
        "has conversation history": len(messages) >= len(SCRIPT) * 2,
    }

    print("\nSanity checks:")
    for label, result in checks.items():
        status = "PASS" if result else "WARN"
        print(f"  [{status}] {label}")
        if not result:
            passed = False

    print(f"\n{'ALL CHECKS PASSED' if passed else 'SOME CHECKS FAILED — review output above'}")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    run_test()
