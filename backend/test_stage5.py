"""
Stage 5 end-to-end test — full 10-phase conversation covering:
  - BNPL trap detection
  - Debt payoff ordering
  - Subscription audit
  - Instrument comparison
  - Education loan literacy
  - Priority check
  - SIP projection (near-term)
"""
import io, sys, json, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

API = "http://localhost:8000"
DIVIDER = "=" * 65

SCRIPT = [
    # Phase 1 — Rapport
    "Hi, I'm Rohan. Final year at BITS Pilani, graduating in May.",
    # Phase 2 — Money
    "I get a fixed 20,000 a month from my parents. No gig work.",
    # Phase 3a — Housing and commute
    "Hostel and mess is 9,000, paid directly by my parents. Commute is maybe 500 a month.",
    # Phase 3b — BNPL and subscriptions
    "Food outside mess is about 3,500. I use Simpl for shopping, around 4,000 a month. "
    "I missed a payment last month. I pay 300 for Netflix and 200 for Spotify.",
    # Phase 4 — Safety net
    "I have health insurance through college. I have about 8,000 in my savings account. "
    "If something urgent came up I'd ask my parents.",
    # Phase 5 — Debt
    "I have a student credit card with a 25,000 limit and I'm using about 18,000 of it. "
    "Also planning to take an education loan of 8 lakhs for my MBA next year.",
    # Phase 6 — Investments
    "I started a SIP of 1,000 a month in a mutual fund six months ago. Nothing else.",
    # Phase 7 — Goals
    "I want to understand the MBA loan before I take it, and also get out of this Simpl mess.",
    # Phase 8 — Education loan + BNPL
    "The loan would be from SBI, about 8 lakhs. My expected starting salary is around 60,000 a month.",
    # Phase 9 — Near-term projection
    "What if I save 3,000 a month until I graduate in May? That's about 4 months away.",
]


def run():
    r = requests.post(f"{API}/api/sessions", timeout=10)
    sid = r.json()["session_id"]
    print(f"\n{DIVIDER}\nSTAGE 5 TEST — Rohan persona (full 10-phase)\nSession: {sid}\n{DIVIDER}")

    profile = {}
    for i, msg in enumerate(SCRIPT, 1):
        print(f"\n[Turn {i}] You: {msg[:90]}{'...' if len(msg)>90 else ''}")
        r = requests.post(f"{API}/api/sessions/{sid}/chat", json={"message": msg}, timeout=300)
        if not r.ok:
            print(f"  ERROR {r.status_code}: {r.text[:200]}")
            continue
        d = r.json()
        profile = d["profile"]
        print(f"  Advisor [{profile.get('conversation_phase','?')}]: {d['advisor_text'][:200]}")

    print(f"\n{DIVIDER}\nFINAL PROFILE\n{DIVIDER}")
    print(json.dumps(profile, indent=2))

    print(f"\n{DIVIDER}\nCHECKS\n{DIVIDER}")
    checks = {
        "Family support captured":    profile.get("money_in", {}).get("family_support_amount") == 20000,
        "BNPL recorded":              profile.get("expenses", {}).get("bnpl_usage", {}).get("apps_used") is not None
                                      or profile.get("expenses", {}).get("bnpl_usage", {}).get("typical_monthly_amount") is not None,
        "Savings captured":           profile.get("safety_net", {}).get("personal_savings_amount") is not None,
        "Investments captured":       len(profile.get("investments", [])) > 0,
        "Goals captured":             len(profile.get("goals", [])) > 0 or profile.get("conversation_phase") in ("guidance","close","goals"),
        "Conversation progressed":    profile.get("conversation_phase") not in ("rapport", None),
    }
    all_pass = True
    for label, result in checks.items():
        status = "PASS" if result else "WARN"
        if not result: all_pass = False
        print(f"  [{status}] {label}")

    print(f"\n{'ALL CHECKS PASSED' if all_pass else 'SOME WARNS — review profile above'}")

if __name__ == "__main__":
    run()
