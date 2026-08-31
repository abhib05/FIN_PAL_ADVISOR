# Voice-Driven Financial Advisor Assistant — Architecture

## Core shift: a real-time voice model as the conversational brain, not a script

The product is a **website with a real-time, interrupt-capable voice assistant** — the user talks,
the assistant talks back, with low enough latency and natural enough turn-taking that it feels like
a phone call with an advisor, not a chatbot with a microphone bolted on. Everything below still
applies from the original text-chat design, with the orchestrator swapped for a realtime
speech-to-speech model:

1. A **system prompt** encoding the advisor's methodology (the phases/principles we extracted) —
   unchanged in content, but see Section 0 below for voice-specific rewrites (spoken responses need
   different shaping than written ones)
2. A **structured financial profile** (JSON) that persists and updates across turns
3. A **deterministic calculation layer** (your rules engine) that the model calls via
   tools/function-calling **mid-conversation, while audio is still streaming** — rather than doing
   math itself

This last point matters even more for voice than it did for text: **the model must never freehand
financial calculations** (compound interest, EMI, corpus targets) because it can get arithmetic
subtly wrong, and a spoken wrong number is harder for a user to double-check than a written one they
can re-read. The voice model's job is conversation, empathy, tone, and explanation. The rules
engine's job is numbers. This split also keeps your compliance story clean — you can audit and
version the actual financial logic separately from the conversational layer, and you have a full
transcript of exactly which tool produced which number in any given conversation.

```
┌─────────────────────────────────────────────────────────────┐
│                    User (speaking, via browser mic)           │
└───────────────────────┬─────────────────────────────────────┘
                         │  WebRTC audio stream (bidirectional)
                ┌────────▼──────────────┐
                │  Realtime Voice Model   │  ← system prompt + conversation history
                │  (speech-to-speech, or  │     + current financial_profile JSON
                │  streaming STT→LLM→TTS) │     + streamed audio in/out
                └────────┬───────────────┘
                         │  decides, WHILE LISTENING/SPEAKING: ask a
                         │  question, or call a tool without breaking the turn
              ┌──────────┴───────────┐
              │                      │
     ┌────────▼────────┐   ┌─────────▼─────────┐
     │  update_profile   │   │  run_calculation   │
     │  (extract fields  │   │  (EMI, FI number,  │
     │   from user reply)│   │   debt payoff, etc)│
     └────────┬──────────┘   └─────────┬──────────┘
              │                        │
              └───────────┬────────────┘
                           │
                ┌──────────▼──────────┐
                │  financial_profile   │  ← persisted per user (your DB)
                │  (structured JSON)   │     + full transcript log for audit
                └──────────────────────┘
```

**Why speech-to-speech (or a tightly-coupled streaming pipeline) instead of chaining separate
STT → text-LLM → TTS services yourself:** turn-taking and interruption ("barge-in" — the user
cutting in while the assistant is mid-sentence) are hard to get right by hand-rolling silence
detection between three separate services. A model built for realtime voice handles voice-activity
detection, barge-in, and mid-stream tool calls as first-class behavior. If you do build the
three-stage pipeline (cheaper, more provider choice), budget real engineering time for the
turn-taking logic — it's the part that makes voice UX feel broken or natural, not the STT/TTS
quality itself.

---

## 0. Voice-specific style rules (new — these didn't exist in the text-chat version)

Spoken conversation has constraints written chat doesn't. Add these to the system prompt as hard
rules, not suggestions:

- **Never read a table, list of more than ~3 items, or raw JSON aloud.** If a calculation result
  has several components (e.g. `debt_payoff_order` returning two full orderings), say the headline
  number and one comparison, and point to the synced visual panel for the rest: "Avalanche saves you
  about ₹18,000 in interest versus snowball — I've put the full breakdown on your screen."
- **Read numbers back for confirmation before acting on anything that changes a recommendation.**
  ASR (speech-to-text) reliably confuses similar-sounding numbers ("15" vs "50," "30k" vs "13k").
  For any figure that will feed into `run_calculation` or a priority decision, repeat it back
  ("eighteen thousand rupees a month, got it") before proceeding — this is a correctness safeguard,
  not just politeness.
- **Keep individual turns short.** A written paragraph is easy to re-read; a 45-second uninterrupted
  spoken answer is not. Default to 2-4 sentences per turn, then check in ("does that make sense so
  far, or should I go deeper on any part?") rather than monologuing.
- **Handle interruption gracefully.** If the user barges in mid-explanation, drop the rest of the
  planned sentence and respond to what they just said — don't finish the old thought first. Treat an
  interruption as signal (they have a question, or already understood), not as a problem to recover
  from.
- **Silence is not always "done talking."** People pause to think, especially with money questions.
  Don't jump in the instant audio stops — use whatever end-of-turn/VAD sensitivity your voice model
  exposes, and err toward slightly patient rather than trigger-happy for a finance conversation
  specifically (rushed pauses read as pressuring the user).
- **Numbers and disclaimers still need to be heard, not just shown.** The visual panel can carry
  detail, but compliance-critical lines (e.g. "this is an estimate, not a guarantee") must still be
  spoken, not silently delegated to on-screen text the user may not be looking at.

---

## 1. The system prompt (this replaces the hardcoded script)

This is where the advisor's *methodology* lives — as principles and phase awareness, not fixed
lines. Below is a starting template, updated for voice.

```
You are a financial guidance assistant for young Indian professionals and students, speaking with
the user in real time by voice — in the style of a warm, curious human financial advisor on a call,
not a form, not a search engine, and not a lecture.

## Your conversational style
- Ask one question at a time. Never dump multiple questions in one turn.
- Keep turns short (2-4 sentences) — this is a spoken conversation, not a document. Check in
  before going deeper rather than monologuing.
- Never read tables, long lists, or raw numbers-heavy breakdowns aloud — state the headline and
  point to the visual panel for detail.
- Read back any number the user gives you that will feed a calculation, to catch mishearing.
- If interrupted, stop and respond to the new input — don't finish your old sentence first.
- Build rapport before numbers: understand the person's situation before asking for figures.
- When someone mentions a number or decision, ask ONE natural follow-up that gives you context
  useful later (e.g. if they mention rent, ask about lock-in/deposit; if they mention a commute,
  ask about distance and mode).
- Reference things they told you earlier in the conversation when relevant — this is what makes
  the conversation feel personalized instead of like a form.
- Never judge spending choices. Acknowledge them neutrally and let the person explain their
  reasoning if they want to.

## Conversation phases (move through these naturally, don't announce them)
1. Rapport — light context about their situation (year of study, college/city, living situation)
2. Money coming in — family support/allowance, gig or part-time income, and how steady/irregular it
   is. Do NOT assume a salary or ask for "monthly take-home" — most users in this audience don't
   have one
3. Expenses — hostel/mess/rent, commute, food beyond mess, split/shared expenses with
   roommates or friends, subscriptions, BNPL app usage, discretionary
4. Safety net — insurance coverage, any personal savings, and what they'd actually do if an urgent
   cost came up (own savings, family, borrowing from friends, credit) — ask this BEFORE investments
5. Debt & credit — education loan already taken or being planned, credit cards, BNPL usage, credit
   limits/utilization, informal borrowing
6. Investments — what they currently hold, how much, since when, instrument by instrument (expect
   this to be empty or minimal for most users — that's normal, not a gap to press on)
7. Goals — ask what they want help with; let them name it, don't assume. Expect this audience to
   lean toward: understanding a loan before taking it, escaping/avoiding a BNPL or credit trap,
   building a first savings habit, or getting a first credit card right — more than "starting to
   invest" or "buying a vehicle," which skew toward an audience with steadier income
8. Goal-specific guidance — once you know the goal, call the run_calculation tool as needed,
   then explain the result and trade-offs in plain language
9. Close — end warmly, invite further questions

You do not need to complete every phase in one conversation. If the user already has a clear
question in mind (e.g. "should I invest in X"), you can move faster and return to earlier phases
only if you're missing information you need for a good answer.

## CRITICAL compliance boundary
- You give EDUCATIONAL information and explain trade-offs (liquidity, risk, tax treatment,
  general rules of thumb). You do NOT recommend specific stocks, mutual fund schemes, or say
  "invest X% in Y fund." 
- When discussing investment options, describe how instrument *types* work (index funds, PPF,
  NPS, ELSS) generically, not specific products or AMCs.
- Always frame recommendations as "a common approach is..." or "one way to think about this is...",
  not as personalized financial advice, and mention that a licensed advisor can help with
  personalized investment decisions for larger amounts.
- Never fabricate calculations. Always call run_calculation for any number involving projections,
  interest, or targets — do not compute these yourself in your response text.

## Tools available to you
- update_profile(field, value): call this whenever the user gives you a piece of financial
  information, to persist it to their profile.
- run_calculation(type, params): call this for any EMI, compound growth, debt payoff order,
  or financial-independence-number calculation. Use the returned result in your response —
  do not restate or modify the numbers yourself.
- get_profile(): call this if you need to check what you already know before asking a question,
  so you don't ask something the user already told you.

## Current financial profile (JSON, updates each turn)
{financial_profile_json}
```

---

## 2. The structured profile (what update_profile writes to)

This is the backbone that lets the LLM "remember" without re-asking, and lets your rules engine
run calculations on real data.

```json
{
  "user_id": "abc123",
  "academic": {
    "year_of_study": null,
    "expected_graduation_year": null
  },
  "money_in": {
    "family_support_amount": null,
    "family_support_regularity": null,  // "fixed_monthly", "variable", "as_needed"
    "gig_income_amount": null,
    "gig_income_type": null,            // "tutoring", "freelance", "campus_job", "other"
    "scholarship_stipend_amount": null,
    "income_stability": null            // "family_supported_fixed", "family_supported_variable",
                                         // "gig_variable", "mixed"
  },
  "expenses": {
    "housing": { "amount": null, "type": null, "family_paid_directly": null },  // type: "hostel", "PG", "rent", "other"
    "commute": { "amount": null, "mode": null, "distance_km": null },
    "food_beyond_mess": null,
    "split_shared_expenses": null,      // roommate/friend splits via UPI — see conversation-flow doc Phase 3
    "subscriptions": null,
    "bnpl_usage": { "apps_used": null, "typical_monthly_amount": null, "missed_or_min_only": null },
    "discretionary": null
  },
  "safety_net": {
    "health_insurance_cover": null,
    "provided_by": null,                // "family", "college", "own"
    "personal_savings_amount": null,
    "would_rely_on_if_urgent": null      // "own_savings", "family", "borrow_from_friends", "credit"
  },
  "debt": [
    { "type": null, "balance": null, "apr": null, "min_payment": null }  // type includes "education_loan_planned", "education_loan_taken", "credit_card", "bnpl", "informal"
  ],
  "credit": {
    "cards": null,
    "total_limit": null,
    "typical_utilization_pct": null
  },
  "investments": [
    { "instrument": null, "amount": null, "frequency": null, "since": null }  // expected empty/minimal for most users in this audience
  ],
  "goals": [
    { "type": null, "target_amount": null, "timeline_years": null, "priority": null }
  ],
  "conversation_phase": "rapport"
}
```

Renamed `income` to `money_in` and dropped `monthly_take_home` as the primary field — deliberately, per [advisor-conversation-flow.md](advisor-conversation-flow.md) Phase 2: this audience mostly doesn't have a salary, and a field named "take-home" invites either a confused or an embarrassed answer. `expenses` also gains `split_shared_expenses` and `bnpl_usage`, and `debt` gains an `education_loan_planned` state distinct from `education_loan_taken` — both reflect problems specific to a college-student audience that the original early-grad-oriented schema didn't need to capture.

`update_profile` is called by the model mid-conversation as a tool call — e.g. after the user says
"I pay 18k rent with a 2-month deposit," the model calls
`update_profile("expenses.housing", {"amount": 18000, "lock_in_months": 2})`. In voice, this call
must not block audio output — the model should keep the conversation flowing (or issue its brief
confirmation, "got it, eighteen thousand with a two-month deposit") while the tool call resolves in
the background, since even a few hundred milliseconds of dead air reads as a stall on a live call.

---

## 3. The calculation tool (deterministic, versioned, testable)

`run_calculation` is a real backend function, not an LLM guess. Example signature:

```
run_calculation(type: str, params: dict) -> dict

Types to implement for MVP:
- "emi": { principal, rate, tenure_months } → monthly EMI, total interest
- "debt_payoff_order": { debts: [...] } → avalanche vs snowball order + payoff timeline
- "emergency_fund_target": { monthly_essential_expenses, employment_stability, has_dependents,
  has_large_emi_burden } → target amount, gap vs current, months_buffer, storage_guidance — see the
  reconciled 3-6-12 Month Rule in [advisory-logic-rules-engine.md](advisory-logic-rules-engine.md)
  Section 1 for the tier logic and how it maps onto the college-audience `money_in.income_stability`
  values (`family_supported_fixed`/`variable`, `gig_variable`)
- "fi_number": { annual_expenses, expected_return, inflation } → target corpus (25x-style calc,
  adjustable assumptions)
- "sip_projection": { monthly_amount, years, expected_return } → future value (educational
  projection only — must be clearly labeled as an estimate, not a guarantee)
```

The model calls this tool, gets back a number, and explains it — it never invents the arithmetic
itself. This also means you can unit-test your financial logic independently of the model, which
matters a lot for something users will make real decisions from. For voice specifically, keep
`run_calculation` fast (low-hundreds-of-ms) — a multi-second wait mid-conversation has no good UX
answer (dead air is worse than a typing indicator), so this tool should stay a simple synchronous
calculation, not something that calls out to slow external services.

---

## 4. Why this beats hardcoding, and what to watch for

**Benefits:**
- Handles the messy reality of real answers ("uh, like 20k? maybe 22 with the extra stuff") without
  you writing regex/parsing rules for every phrasing
- Naturally adapts follow-up questions to what the user actually said, instead of a fixed tree
- Easy to extend — adding a new goal type is a prompt/tool change, not a new flowchart

**What to watch for:**
- **Grounding drift**: the model can wander off the phase structure in long conversations —
  periodically remind it of `conversation_phase` and what's still missing in the profile (this is
  why `get_profile` exists as a tool — encourage the model to check state rather than guess)
- **Hallucinated specificity**: watch outputs in testing for the model naming specific mutual fund
  schemes or making promises about returns — this is a prompt-adherence problem you need to test
  for explicitly, not assume the prompt handles by itself
- **Cost**: real-time voice is priced per minute of audio (in and out), not just per token — it is
  meaningfully more expensive than the equivalent text conversation, and cost scales with how long
  users stay on a call, not how much they say. Budget for this explicitly; consider a cheaper
  transcription/voice tier for the discovery phases (1-6) and reserving your strongest model for
  synthesizing the final goal-specific recommendation (phase 8)
- **ASR mishearing on financial figures**: speech-to-text errors on numbers are the single biggest
  new failure mode versus text chat — a misheard "15,000" as "50,000" silently poisons every
  downstream calculation. This is why Section 0's "read numbers back" rule is load-bearing, not
  optional politeness — treat it as a correctness control, and test it explicitly with noisy audio
  and accented speech samples representative of your actual user base
- **Latency budget**: users tolerate waiting for a typed response far more than a spoken one — a
  2-3 second gap before the assistant responds feels broken on a call in a way it doesn't in chat.
  Track time-to-first-audio as a core metric, not just total response time
- **Testing approach**: since there's no fixed script, you need conversation-level evals — a set of
  representative user personas/scripts you run through periodically to catch regressions in tone,
  compliance-boundary adherence, and calculation accuracy. For voice, extend this to actual audio
  test fixtures (not just text transcripts) so you catch ASR/TTS-specific failures, not only
  language-model ones

---

## 5. Suggested MVP scope for this specific piece

Don't build all 9 phases + all calculation types at once, and don't build the full realtime voice
pipeline before proving the conversation itself works. Suggested order:

1. **Prove the conversation design in text first** (even briefly) — phases 1-4 (rapport, income,
   expenses, safety net), one calculation type (`emergency_fund_target`), one goal sub-flow. This
   validates the prompt/profile/tool-calling design cheaply before you add voice infrastructure
   on top of a conversation flow that might still need changes.
2. **Swap in the realtime voice transport** once the conversation logic is stable — WebRTC mic
   capture, the voice session server, and either a speech-to-speech API or your STT→LLM→TTS
   pipeline. Reuse the exact same system prompt, profile schema, and tools from step 1, plus the
   Section 0 voice-style additions.
3. **Test barge-in and the number-confirmation rule specifically** — these are the two behaviors
   that don't exist in a text prototype and are the most likely to feel broken if untested.
4. Only then expand to investment audit, debt payoff, or FI-number complexity.

This gives you a working, testable slice you can demo and get real user feedback on before
investing in the full breadth — and it isolates "is the conversation design good" from "is the
voice pipeline working" as two separate things to debug.
