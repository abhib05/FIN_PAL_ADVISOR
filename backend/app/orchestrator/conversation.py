import json
import time
from groq import Groq, RateLimitError

from app.config import get_settings
from app.orchestrator.system_prompt import build_system_prompt
from app.orchestrator.tools import TOOL_SCHEMAS, execute_tool

_settings = get_settings()
_client = Groq(api_key=_settings.groq_api_key)

MAX_TOOL_ITERATIONS = 5
_MAX_RETRIES = 1
# No artificial history cap — the model's 32k context window is the real limit.
# A full 10-phase student conversation (~40 turns × ~175 tokens) uses ~7k tokens,
# well within the window alongside the system prompt and tool schemas.
_MAX_HISTORY_TURNS = None


def _chat_with_retry(messages: list[dict]) -> object:
    for attempt in range(_MAX_RETRIES + 1):
        try:
            return _client.chat.completions.create(
                model=_settings.groq_model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
            )
        except RateLimitError as exc:
            if attempt == _MAX_RETRIES:
                raise
            retry_after = 10
            if hasattr(exc, "response") and exc.response is not None:
                retry_after = int(exc.response.headers.get("retry-after", 10))
            retry_after = min(retry_after, 15)
            time.sleep(retry_after)
    raise RuntimeError("Unreachable")


def _tag_with_memory(text: str, profile_updates: list[str]) -> str:
    """
    Prefix the stored assistant message with a compact memory note.
    This keeps tool-call results visible in future history turns even after
    tool-call intermediates are discarded from the working context.
    """
    if not profile_updates:
        return text
    # Cap at 8 entries to keep the tag concise
    note = "[Memory: " + "; ".join(profile_updates[:8]) + "] "
    return note + text


def run_turn(
    user_message: str,
    financial_profile: dict,
    messages: list[dict],
) -> tuple[str, dict, list[dict]]:
    system_prompt = build_system_prompt(json.dumps(financial_profile, indent=2))

    # Send full history — trimming only if an explicit cap is set
    trimmed_messages = (
        messages[-(2 * _MAX_HISTORY_TURNS):]
        if _MAX_HISTORY_TURNS and len(messages) > 2 * _MAX_HISTORY_TURNS
        else messages
    )

    # Working context for this turn — grows with tool call intermediates
    context: list[dict] = list(trimmed_messages) + [{"role": "user", "content": user_message}]

    # Track update_profile calls this turn so we can tag history for continuity
    profile_updates: list[str] = []

    # Save any text the model produces even when it also makes tool calls —
    # used as fallback if the loop exhausts before a clean text-only response.
    last_text: str | None = None

    for iteration in range(MAX_TOOL_ITERATIONS):
        response = _chat_with_retry(
            [{"role": "system", "content": system_prompt}] + context,
        )

        message = response.choices[0].message

        # Capture any text the model produced this iteration (may accompany tool calls)
        if message.content and message.content.strip():
            last_text = message.content.strip()

        if not message.tool_calls:
            # Clean text response — done
            assistant_text = last_text or ""
            stored_text = _tag_with_memory(assistant_text, profile_updates)
            updated_messages = list(messages) + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": stored_text},
            ]
            return assistant_text, financial_profile, updated_messages

        # Append assistant turn with tool calls to working context
        context.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ],
        })

        # Execute each tool call and append results
        for tc in message.tool_calls:
            args = json.loads(tc.function.arguments)
            result, financial_profile = execute_tool(tc.function.name, args, financial_profile)

            # Track profile mutations for the memory tag
            if tc.function.name == "update_profile":
                field = args.get("field", "?")
                value = args.get("value", "?")
                profile_updates.append(f"{field}={value}")

            context.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result),
            })

    # Exhausted iterations — use the last text the model produced (if any)
    # rather than a generic error, so context isn't corrupted by a confusing fallback.
    fallback_text = last_text or "I'm having trouble processing that. Could you repeat your question?"
    stored_text = _tag_with_memory(fallback_text, profile_updates)
    updated_messages = list(messages) + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": stored_text},
    ]
    return fallback_text, financial_profile, updated_messages
