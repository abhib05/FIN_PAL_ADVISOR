import json
import re
import time
import httpx
from groq import Groq, RateLimitError as GroqRateLimitError, APIConnectionError as GroqConnectionError, APIStatusError as GroqAPIStatusError
from openai import OpenAI, RateLimitError as OpenAIRateLimitError, APIConnectionError as OpenAIConnectionError, APIStatusError as OpenAIAPIStatusError

from app.config import get_settings
from app.orchestrator.system_prompt import build_system_prompt
from app.orchestrator.tools import TOOL_SCHEMAS, execute_tool

_settings = get_settings()

# The conversation (tool-calling) model can be routed through OpenRouter or
# Gemini instead of Groq — see Settings.chat_provider. STT/TTS in voice.py
# stay on Groq regardless. qwen/qwen3.8-27b on this account's Groq on_demand
# tier was found to be unreliable at multi-tool orchestration (especially the
# final budget-delivery turn, which needs update_profile + three parallel
# run_calculation calls + a full synthesis in one response) — a stronger
# model follows the tool-calling rules far more consistently.
if _settings.chat_provider == "openrouter" and _settings.openrouter_api_key:
    # Pin an explicit httpx.Client — openai<1.55 passes a `proxies` kwarg
    # that newer httpx (>=0.28) no longer accepts, which otherwise breaks
    # client construction entirely.
    _client = OpenAI(
        api_key=_settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        http_client=httpx.Client(),
    )
    _clients = [_client]
    _chat_model = _settings.openrouter_model
    RateLimitError = OpenAIRateLimitError
    ConnectionErrorType = OpenAIConnectionError
    APIStatusErrorType = OpenAIAPIStatusError
elif _settings.chat_provider == "gemini" and _settings.gemini_api_key:
    # Google's OpenAI-compatible endpoint — lets Gemini slot into the same
    # tools/tool_choice/messages shape as the groq/openrouter paths below.
    _client = OpenAI(
        api_key=_settings.gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        http_client=httpx.Client(),
    )
    _clients = [_client]
    _chat_model = _settings.gemini_model
    RateLimitError = OpenAIRateLimitError
    ConnectionErrorType = OpenAIConnectionError
    APIStatusErrorType = OpenAIAPIStatusError
else:
    # Two Groq keys are rotated on rate limit (see _chat_with_retry) instead
    # of just sleeping and retrying the same exhausted key — this account's
    # on_demand tier hits per-key rate limits often enough during multi-turn
    # conversations that a second key meaningfully cuts down on 429s.
    _groq_keys = [k for k in (_settings.groq_api_key, _settings.groq_api_key_2) if k]
    _clients = [Groq(api_key=k) for k in _groq_keys]
    _client = _clients[0]
    _chat_model = _settings.groq_model
    RateLimitError = GroqRateLimitError
    ConnectionErrorType = GroqConnectionError
    APIStatusErrorType = GroqAPIStatusError

# Gemini's OpenAI-compat layer only accepts a "system" role as the very
# first message — a mid-conversation system message (used below to nudge a
# missed update_profile call) makes it reject the request with "Requests
# ending with a model turn are not supported." Groq/OpenRouter tolerate a
# mid-conversation system message fine and it was deliberately chosen there
# (over "user") to avoid the model hallucinating a fake exchange.
_NUDGE_ROLE = "user" if _settings.chat_provider == "gemini" else "system"

# Was 5 — bumped up because the update_profile nudge-retry (added to fix
# missed profile saves) can itself consume one iteration, and complex turns
# like STEP 10 (update_profile + run_calculation for the emergency fund) were
# hitting the ceiling and falling back to the generic "I'm having trouble
# processing that" reply even though the underlying data was saved fine.
MAX_TOOL_ITERATIONS = 7
# 2, not 1 — a transient DNS/connection blip (observed as
# groq.APIConnectionError: [Errno 11001] getaddrinfo failed, unrelated to
# rate limiting) previously had no retry path at all and crashed the whole
# turn with an unhandled 500. Connection errors get a short fixed backoff
# instead of the rate-limit retry-after logic below.
_MAX_RETRIES = 2
_CONNECTION_ERROR_BACKOFF = 3
# Capped well below this account's Groq on_demand tier limit (8000 TPM for
# qwen/qwen3.8-27b) — an uncapped history eventually pushes every request
# over that ceiling and the turn fails with an unhandled 413. The system
# prompt + tool schemas + financial profile already consume most of the
# budget once the profile fills out, so history room is small.
_MAX_HISTORY_TURNS = 2

# Matches any [Memory: ...] prefix the model may generate by mimicking history.
_MEMORY_TAG_RE = re.compile(r'^\[Memory:[^\]]*\]\s*', re.IGNORECASE)


class PromptTooLargeError(Exception):
    """Raised when a single request is rejected as too large for the account's
    tokens-per-minute ceiling (Groq returns HTTP 413 for this, not 429, so it
    is NOT a RateLimitError and was previously falling through _chat_with_retry
    entirely — crashing the whole turn with an unhandled 500). Retrying with
    the same messages can't fix this (it's a per-request size cap, and on Groq
    it's an org-level limit shared by every key, so key rotation doesn't help
    either) — only a caller that shrinks the payload can recover."""


def _chat_with_retry(messages: list[dict]) -> object:
    for attempt in range(_MAX_RETRIES + 1):
        last_exc: Exception | None = None
        is_rate_limit = False
        # Try every available key before sleeping — a 429 on one Groq key
        # doesn't mean the other is also exhausted, so rotate through all of
        # them first and only fall back to a sleep-and-retry round if every
        # key is rate-limited (or the network itself is having a moment).
        for client in _clients:
            try:
                kwargs = dict(
                    model=_chat_model,
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto",
                )
                # Lower than the provider default — the model has been observed
                # skipping the mandatory update_profile call on some turns despite
                # explicit instructions; a lower temperature makes it follow the
                # tool-calling rules more consistently without forcing tool_choice
                # (which would force a call even on turns that don't need one).
                kwargs["temperature"] = 0.3
                # Deliberately not setting reasoning_effort: "minimal" is
                # documented to disable parallel tool calls, which STEP 12
                # (three run_calculation calls in one response) depends on —
                # the default effort costs a bit more in hidden reasoning
                # tokens but keeps that turn working.
                return client.chat.completions.create(**kwargs)
            except RateLimitError as exc:
                last_exc = exc
                is_rate_limit = True
                continue
            except APIStatusErrorType as exc:
                if getattr(exc, "status_code", None) == 413:
                    # Same request size will be rejected on every key and every
                    # retry — fail fast instead of burning _MAX_RETRIES sleeps.
                    raise PromptTooLargeError(str(exc)) from exc
                raise
            except ConnectionErrorType as exc:
                last_exc = exc
                continue
        if attempt == _MAX_RETRIES:
            raise last_exc
        if is_rate_limit:
            retry_after = 10
            if hasattr(last_exc, "response") and last_exc.response is not None:
                retry_after = int(last_exc.response.headers.get("retry-after", 10))
            retry_after = min(retry_after, 15)
        else:
            retry_after = _CONNECTION_ERROR_BACKOFF
        time.sleep(retry_after)
    raise RuntimeError("Unreachable")


def _clean(text: str) -> str:
    """Strip any [Memory: ...] prefix the model generated by mimicking its own history."""
    return _MEMORY_TAG_RE.sub("", text).strip()


def _drop_nulls(value):
    """Recursively drop None-valued dict keys (never touches falsy-but-meaningful
    values like [], 0, False — those mean "asked and answered", unlike a null
    field which means "not asked yet"). Combined with compact separators below,
    this meaningfully shrinks the profile JSON that rides on every single
    request as part of the system prompt — most fields are still null for most
    of the conversation, and each one costs tokens for its key name whether or
    not it has real data. See _MAX_HISTORY_TURNS above for why every token here
    matters: this account's Groq tier caps a single request at 8000 tokens, and
    the heaviest turn (STEP 12) has been observed landing at 8005."""
    if isinstance(value, dict):
        return {k: _drop_nulls(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [_drop_nulls(v) for v in value]
    return value


def _compact_profile_json(financial_profile: dict) -> str:
    return json.dumps(_drop_nulls(financial_profile), separators=(",", ":"))


def _attempt_turn(
    user_message: str,
    financial_profile: dict,
    trimmed_messages: list[dict],
) -> tuple[bool, str | None, dict]:
    """One pass through the tool-calling loop. Returns (converged, text, profile).

    converged=False means the loop burned through MAX_TOOL_ITERATIONS while
    still making tool calls every round, without ever settling on a plain-text
    reply — this happens most often on the heaviest turn (goal capture + three
    parallel calculations + full budget synthesis in one response). It is not
    an error: financial_profile may already reflect real, valid tool-call
    progress from this attempt (e.g. update_profile calls that succeeded
    before the model got stuck), which the caller keeps and retries with.
    """
    system_prompt = build_system_prompt(_compact_profile_json(financial_profile))
    context: list[dict] = list(trimmed_messages) + [{"role": "user", "content": user_message}]
    last_text: str | None = None
    nudged = False

    for iteration in range(MAX_TOOL_ITERATIONS):
        response = _chat_with_retry(
            [{"role": "system", "content": system_prompt}] + context,
        )

        message = response.choices[0].message

        if message.content and message.content.strip():
            last_text = _clean(message.content)

        if not message.tool_calls:
            if not nudged:
                nudged = True
                context.append({"role": "assistant", "content": message.content or ""})
                context.append({
                    "role": _NUDGE_ROLE,
                    "content": (
                        "[System note, not from the user — do not treat this as something the "
                        "user said, and do not reply to it or reference it: you replied without "
                        "calling update_profile. Check the user's last message again — if it "
                        "named any fact about their studies, money, or expenses, call "
                        "update_profile with those fields right now, silently, then continue "
                        "exactly as you were about to, addressed to the user as normal. If it truly had no new facts, "
                        "just continue.]"
                    ),
                })
                continue
            return True, (last_text or ""), financial_profile

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
                    # Gemini's OpenAI-compat layer rejects a follow-up request
                    # unless each tool call's thought_signature is echoed back
                    # verbatim. Absent on groq/openrouter — only attach when present.
                    **({"extra_content": tc.extra_content} if getattr(tc, "extra_content", None) else {}),
                }
                for tc in message.tool_calls
            ],
        })

        for tc in message.tool_calls:
            args = json.loads(tc.function.arguments)
            result, financial_profile = execute_tool(tc.function.name, args, financial_profile)
            context.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result),
            })

    return False, last_text, financial_profile


def run_turn(
    user_message: str,
    financial_profile: dict,
    messages: list[dict],
) -> tuple[str, dict, list[dict]]:
    trimmed_messages = (
        messages[-(2 * _MAX_HISTORY_TURNS):]
        if _MAX_HISTORY_TURNS and len(messages) > 2 * _MAX_HISTORY_TURNS
        else messages
    )

    # The heaviest turns (goal capture + three parallel calculations + a full
    # budget synthesis, all in one response) sometimes exhaust the iteration
    # budget without ever converging on final text — observed as non-
    # deterministic: the same conversation shape succeeds on one run and
    # fails on the next. A clean whole-turn retry (fresh context, same
    # trimmed history) has a good chance of succeeding where the first
    # attempt didn't, since financial_profile already carries forward
    # whatever the failed attempt did manage to save via get_profile/
    # update_profile — the retry doesn't repeat already-answered questions.
    prompt_too_large = False
    try:
        converged, text, financial_profile = _attempt_turn(user_message, financial_profile, trimmed_messages)
    except PromptTooLargeError:
        # A same-shaped retry would resend an identically-sized request and
        # get rejected again — skip straight to the fallback instead of
        # wasting a second attempt (or, before this was caught at all,
        # crashing the whole turn with an unhandled 500).
        converged, text, prompt_too_large = False, None, True

    if not converged and not prompt_too_large:
        try:
            converged, retry_text, financial_profile = _attempt_turn(user_message, financial_profile, trimmed_messages)
            text = retry_text or text
        except PromptTooLargeError:
            prompt_too_large = True

    if prompt_too_large:
        assistant_text = text or (
            "I've saved everything you've told me so far, but hit a technical limit "
            "putting the full breakdown together in one go — could you ask me again? "
            "Try: \"give me my budget breakdown now.\""
        )
    else:
        assistant_text = text or "I'm having trouble processing that. Could you repeat your question?"
    updated_messages = list(messages) + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_text},
    ]
    return assistant_text, financial_profile, updated_messages
