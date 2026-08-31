# Implementation Plan — Voice Financial Advisor for College Students

This turns everything decided so far into a concrete build sequence. It assumes the reader has the
other files in this folder as reference (product plan, architecture, rules engine, conversation
flow, source extractions) and doesn't re-explain decisions already made there — it just sequences
the work.

---

## 0. Decisions this plan locks in (change these deliberately, not by drift)

| Decision | Choice | Why |
|---|---|---|
| Target user | Indian college students (not early-grads — see [financial-advisor-app-plan.md](financial-advisor-app-plan.md) §1/§3) | Narrower, validated scope |
| Interface | Website, real-time voice assistant as primary interface, text-chat fallback | See [financial-advisor-app-plan.md](financial-advisor-app-plan.md) §1, [llm-advisor-architecture.md](llm-advisor-architecture.md) |
| LLM brain | **Groq (`openai/gpt-oss-120b`)** — tested live, correct tool-calling, sub-400ms latency, near-zero cost | See test results earlier in this session; re-verify model availability before building since Groq's lineup shifts |
| STT / TTS | **Test Groq's `whisper-large-v3` and Orpheus TTS first** (Stage 2 below) — same key as the LLM, potentially a single-provider stack. Fall back to OpenAI (Whisper API + `tts-1`) using the $9.8 credit if Groq's audio quality/latency doesn't hold up | Not yet tested this session — first real task below |
| Rules engine logic | India-sourced: Anshuman Sharma transcript + Housel (universal) + SmartPlan Finance + partial Collins/Sethi/Rabbior (general formulas only, jurisdiction-specific numbers held) | See each source file's status banner |
| Backend | Python (FastAPI) — Groq's SDK and most voice/audio tooling has better Python support than Node right now | Deviates from the original Node/FastAPI either-or in the product plan; revisit if the team has a strong Node preference |
| Database | PostgreSQL | Per [financial-advisor-app-plan.md](financial-advisor-app-plan.md) §5 |

---

## 1. Build order (stages, not calendar weeks — each stage gates the next)

### Stage 0 — Project scaffold (a few hours)
- Repo structure (see §2 below)
- `.env` handling for the Groq key (never commit it — the file it currently lives in,
  `IBM_Project_GROQ_API_KEY.txt`, should be deleted from the project folder once it's copied into
  `.env` and `.gitignore`'d — a plaintext key file sitting in a folder that might get zipped/shared
  is a real leak risk)
- FastAPI skeleton with a health-check route
- Postgres running locally (or a free-tier hosted instance — Railway/Supabase both work) with the
  `User`/`financial_profile` tables from [llm-advisor-architecture.md](llm-advisor-architecture.md) §2

### Stage 1 — Text-only conversation brain (validates the hard part first)
**Goal:** prove the system prompt, profile schema, and tool-calling loop work — no audio yet.
- Implement `update_profile`, `run_calculation`, `get_profile` as real Python functions
- Implement `run_calculation`'s first calc type: **`emergency_fund_target`** using the reconciled
  3-6-12 rule from [advisory-logic-rules-engine.md](advisory-logic-rules-engine.md) §1
- Wire these as Groq tool-calling functions against `openai/gpt-oss-120b`, using the system prompt
  template from [llm-advisor-architecture.md](llm-advisor-architecture.md) §0-1 (voice-style rules
  included even though there's no audio yet — cheaper to build the habit now than retrofit later)
- Test surface: a plain terminal/REPL loop (type a message, see the reply + any tool calls) — no
  frontend needed yet
- **Exit criteria:** a full scripted conversation through phases 1-4 (rapport → income → expenses →
  safety net) for the "Aditi" and "Rohan" personas from [financial-advisor-app-plan.md](financial-advisor-app-plan.md)
  §3 correctly builds a profile and produces a sane emergency-fund number without hallucinated math

### Stage 2 — Audio round-trip test (before building the pipeline)
**Goal:** decide the STT/TTS provider before writing pipeline code around it.
- Hit Groq's `whisper-large-v3` with a handful of real short recordings (include some noisy/accented
  ones — this is where ASR-mishearing-numbers risk actually shows up, per
  [llm-advisor-architecture.md](llm-advisor-architecture.md)'s voice-style rules)
- Hit Groq's Orpheus TTS model with a few short spoken-style replies, check naturalness and latency
- Compare against OpenAI's Whisper API + `tts-1` on the same test clips
- **Decision point:** pick one provider pairing for Stage 3. Don't split STT and TTS across two
  providers without a real reason — it doubles your integration surface for no clear benefit unless
  one provider is meaningfully better at one job

### Stage 3 — Turn-based voice loop (push-to-talk)
**Goal:** the full pipeline working end-to-end, still not real-time-streaming.
- Minimal web page: hold-to-record button (MediaRecorder API) → send clip to backend → STT →
  Stage 1's conversation brain → TTS → play reply
- Add the live conversation transcript + synced visual panel (numbers/charts) from
  [financial-advisor-app-plan.md](financial-advisor-app-plan.md)'s MVP feature list — even a plain
  table/number display satisfies this for now, polish later
- Test the **number-confirmation rule** specifically (Section 0 of the architecture doc) — this is
  the one behavior that doesn't exist in Stage 1's text-only test and is the highest-risk-if-wrong
  piece of the whole voice UX
- **Exit criteria:** a full voice conversation, start to finish, through the emergency-fund goal
  sub-flow, without the user having to repeat themselves due to mishearing

### Stage 4 — Realtime streaming (optional, capped spend, only after Stage 3 feels right)
- Brief, deliberately time-boxed test against a speech-to-speech realtime API (see
  [financial-advisor-app-plan.md](financial-advisor-app-plan.md)'s cost note) to feel out
  barge-in/interruption
- Only invest in building the full realtime pipeline if this test clearly justifies the added cost
  and engineering complexity over Stage 3's turn-based version

### Stage 5 — Expand calculation coverage + remaining conversation phases
- Add `debt_payoff_order`, `emi_calculation`, `sip_projection`, `fi_number` from
  [advisory-logic-rules-engine.md](advisory-logic-rules-engine.md)
- Add the BNPL/credit-trap detector and education-loan-literacy module from
  [financial-advisor-app-plan.md](financial-advisor-app-plan.md)'s MVP feature list
- Extend the conversation flow through phases 5-9 (debt/credit, investments, goals, goal-specific
  guidance, close) per [advisor-conversation-flow.md](advisor-conversation-flow.md)

### Stage 6 — Bank/UPI linking, private beta
- Only after the conversation itself is validated — this is expensive infra (Setu Account Aggregator
  integration, compliance review) not worth building before you know the core experience works

---

## 2. Suggested repo structure

```
/backend
  /app
    main.py                 # FastAPI app, health check
    /orchestrator
      system_prompt.py       # the voice-style + methodology prompt template
      tools.py                # update_profile, run_calculation, get_profile definitions
      conversation.py         # the Groq/LLM call loop
    /rules_engine
      emergency_fund.py       # reconciled 3-6-12 rule
      debt_payoff.py
      emi.py
      fi_number.py
      sip_projection.py
    /voice
      stt.py                  # Groq/OpenAI STT wrapper
      tts.py                  # Groq/OpenAI TTS wrapper
    /db
      models.py               # User, FinancialProfile, ConversationTranscript
      session.py
  .env                        # GROQ_API_KEY, OPENAI_API_KEY (if used), DATABASE_URL — gitignored
  requirements.txt

/frontend
  (Next.js app — mic capture, transcript panel, visual data panel)

/files                        # already exists — planning/knowledge-base docs, unchanged
```

---

## 3. What's still an open decision (don't let this plan silently answer these for you)

1. **Groq vs. OpenAI for STT/TTS** — genuinely untested until Stage 2 runs
2. **Whether to keep Python/FastAPI or switch to Node/NestJS** — locked above as Python for Groq SDK
   ergonomics, but worth revisiting if you're more fluent in Node
3. **Next.js vs. a simpler frontend for the early stages** — Stage 3's minimal test page doesn't need
   the full Next.js setup; you could prototype in a single HTML+JS file first and move to Next.js once
   the UI needs real structure (routing, the visual panel, auth)

---

## 4. Immediate next action

Run Stage 2 (the Groq STT/TTS test) — it's a 20-minute task that unblocks every stage after it, and
nothing else in this plan depends on decisions you haven't made yet except that one.
