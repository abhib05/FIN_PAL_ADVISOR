"""
Stage 1 terminal REPL — no database required.

Usage:
    cd backend
    pip install -r requirements.txt
    python repl.py
"""
import sys
import uuid
import json
from pathlib import Path

# Load .env from the backend directory
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from app.orchestrator.conversation import run_turn
from app.orchestrator.tools import default_profile

DIVIDER = "-" * 60


def _print_profile(profile: dict) -> None:
    print(f"\n{DIVIDER}")
    print("Current profile:")
    print(json.dumps(profile, indent=2))
    print(DIVIDER)


def main() -> None:
    session_id = str(uuid.uuid4())
    profile = default_profile(session_id)
    messages: list[dict] = []

    print(f"\n{DIVIDER}")
    print("Voice Financial Advisor — Stage 1 text REPL")
    print("Commands: 'profile' to view current profile, 'quit' to exit")
    print(DIVIDER + "\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            sys.exit(0)

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break

        if user_input.lower() == "profile":
            _print_profile(profile)
            continue

        try:
            response, profile, messages = run_turn(
                user_message=user_input,
                financial_profile=profile,
                messages=messages,
            )
        except Exception as e:
            print(f"\n[Error] {e}\n")
            continue

        print(f"\nAdvisor: {response}\n")


if __name__ == "__main__":
    main()
