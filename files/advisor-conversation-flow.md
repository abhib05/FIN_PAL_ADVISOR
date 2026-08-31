# Chatbot Conversation Design — Based on Human Advisor Transcript Analysis

Source: analysis of a "Fix Your Finance" episode (advisor Anshuman Sharma with a young couple,
Anjum & Firoz). This document extracts the advisor's *methodology* and converts it into a
conversation flow/decision tree for the app's chatbot. Numbers from the video are illustrative
only — the flow is what gets reused, not their specific figures.

---

## Design Principle

The advisor never asks "give me all your financial data" as a form. He asks **one human question
at a time**, uses each answer to inform the next question, and only synthesizes advice after the
full picture is built. The chatbot should follow the same rhythm: **conversational discovery →
synthesis → recommendation**, not a form wearing a chat UI.

**This is now a spoken conversation, not typed chat** — the app is a website where the user talks
to the assistant in real time and it talks back (see [llm-advisor-architecture.md](llm-advisor-architecture.md)
Section 0 for the full voice-style rules). This flow maps directly onto voice with almost no
change, because it was already modeled on a *spoken* human advisor conversation — the one-question-
at-a-time rhythm below is exactly right for voice and was arguably a worse fit for a typed chat UI
in the first place. Two things do change for voice specifically:
- **Numbers must be read back for confirmation** at the moment they're captured (rent, income,
  balances, APRs) — speech-to-text can mishear digits, and an unconfirmed wrong number silently
  poisons every calculation downstream in the flow.
- **Each bot turn should be short enough to say out loud naturally** — the sample lines below are
  already close to the right length; resist the temptation to have the bot expand them into
  longer written-style paragraphs.

---

## Phase 1: Rapport (before any numbers)

**Purpose:** Lower the guard before asking about money — people are more honest about finances
once they feel heard as a person first.

Sample bot flow:
- "Hey! Before we get into the numbers — tell me a bit about yourself. What do you do, and where are you based?"
- "How long have you been [working / living there / in this job]?"
- (if relevant) "Anyone else's finances tied into this — partner, family you support?"

Design note: keep this to 2-3 exchanges max — shorter than in the video, since a college student has
less complex context than a working couple. One or two questions, not five. Also useful here:
"Which year are you in, and roughly how much longer until you graduate?" — this timeline matters
later for anything loan- or placement-related in a way it wouldn't for a working adult.

---

## Phase 2: Money Coming In (not "income" in the traditional sense)

**Purpose:** For this audience, "income" is usually not a salary — it's some mix of family
support/allowance, occasional gig or part-time work, and possibly a scholarship or stipend. The
old framing ("what's your monthly take-home") doesn't fit and will confuse or embarrass a user who
has none. Ask about money *coming in*, however irregular or small, without assuming a paycheck.

Sample bot flow:
- "How does money usually come to you — allowance from family, part-time or gig work, a
  scholarship, or a mix?"
- If family-supported: "Roughly how much comes in, and is it a fixed amount each month or does it
  vary?"
- If gig/part-time: "How steady is that — same amount most months, or does it swing around a lot?"
- (if they mention tutoring, freelancing, campus jobs) "How long have you been doing that, and has
  it grown at all?"

Why this matters for your audience: **income stability here usually means something different than
"probation vs. permanent."** For a college student it more often means "is this a fixed monthly
transfer I can count on" vs. "this depends on how many gigs I get" — capture that distinction
explicitly, since it drives how conservative any savings/spending guidance should be (see
`income_stability` in the profile schema — extend its accepted values beyond "stable_salaried" /
"probation" / "freelance_variable" to include a family-support case, e.g. `"family_supported_fixed"`
vs. `"family_supported_variable"`).

---

## Phase 3: Expense Discovery (category by category, one follow-up each)

**Purpose:** Get real numbers with just enough context to spot inefficiencies later, without
turning it into an audit.

Order, adapted for a college student's actual expense categories:
1. **Housing/hostel/mess** — hostel fees, PG rent, or mess charges; note whether this is paid
   directly by family (invisible to the student's own spending) or something they manage themselves
2. **Commute** — mode of transport, distance, monthly cost (campus shuttle, auto/cab, own vehicle)
3. **Food beyond mess** — eating out, food delivery, canteen spending on top of any mess plan
4. **Split/shared expenses** — this replaces "dependents/family obligations" as the dominant
   category for this audience: splitting outings, trips, subscriptions, or a shared PG with
   roommates via UPI. This is often where a student's money silently disappears, and it's specific
   to this demographic in a way the earlier plan (aimed at working adults) didn't need to cover.
5. **Recurring subscriptions** — OTT, gym, SaaS-style subscriptions students accumulate; also ask
   about **BNPL app usage specifically** here ("do you use any pay-later apps like Simpl or
   LazyPay?") — this is a new, deliberate addition versus the general/early-grad flow, since BNPL
   is disproportionately a college-student on-ramp to debt
6. **Discretionary/lifestyle** — the "TV" category — ask neutrally, let them explain, don't judge

Sample bot flow per category:
- "Let's start with where you're staying — hostel, PG, or something else — and what that costs
  monthly? Is that something you handle, or does it go straight through your family?"
- "How do you get around campus and the city, and roughly what does that cost you a month?"
- "Do you split expenses with roommates or friends a lot — outings, subscriptions, that kind of
  thing? Roughly how much does that add up to?"
- "Any subscriptions running, or do you use any pay-later apps for shopping?"

Design note: the advisor's follow-up questions ("how far is your office," "do you use Ola or your
own car") aren't idle chat — they're the *reasoning trail* the bot needs to store, so that later
recommendations can be specific ("your commute is costing you X, here's a cheaper alternative")
rather than generic ("reduce your expenses").

---

## Phase 4: Safety Net Check (before investments — this ordering matters)

**Purpose:** The advisor checks insurance coverage *before* discussing investments. Don't let the
bot skip this or reorder it — recommending investments before checking for a safety net is a
common bad-advice pattern to avoid.

Sample bot flow:
- "Are you covered by health insurance — through family, college, or your own? Roughly what's the cover amount?"
- "If something urgent came up — a medical bill, a broken laptop right before finals — do you have
  any savings of your own to fall back on, or would it mean asking family or borrowing from
  friends?"

Design note for this audience: most college students don't have (and often can't reasonably have)
a formal emergency fund yet — "would you ask family or borrow from friends" is often the honest
answer, and that's fine to hear. The point of this phase isn't to demand savings that don't exist;
it's to surface the gap so it can inform later guidance (e.g. whether a small starter savings goal
belongs earlier in the priority ordering than it would for someone with more disposable income).

---

## Phase 5: Debt & Credit Audit

**Purpose:** Understand liabilities and existing credit capacity — the video's advisor notably
*reframes* existing credit limits as a usable emergency buffer rather than telling them to build
one from scratch. For this audience, this phase is also where the BNPL/credit-trap detector (see
[financial-advisor-app-plan.md](financial-advisor-app-plan.md) MVP features) gets its data.

Sample bot flow:
- "Any loans or credit card debt right now — an education loan already taken, a student credit
  card, or anything you owe friends or family?"
- "Do you use any pay-later apps — Simpl, LazyPay, or a card's EMI conversion? How's that going —
  ever missed a due date or just paid the minimum?"
- "What's your credit limit on any card you have, and roughly how much of it are you usually
  using?" (bot can later suggest: "your credit limit can double as an emergency buffer while you
  build your own fund" — this is a legitimate reframe *if* it comes with a clear caveat that credit
  is a stopgap, not a substitute for savings — and it should be offered *more* cautiously here than
  for a working adult, since a first-time cardholder is more likely to lean on it as a habit rather
  than a genuine one-off buffer)
- If a family education loan is being planned but not yet taken: route into the **education loan
  literacy** sub-flow (see main project plan MVP features) rather than a payoff-strategy
  conversation — "before it happens, not after" is the whole point for this audience.

---

## Phase 6: Investment Audit (instrument by instrument)

**Purpose:** Ask about each investment vehicle separately with "how much" and "since when" — this
is what let the advisor spot a risky/illiquid instrument precisely.

Sample bot flow:
- "Do you currently invest anywhere — PPF, mutual funds, NPS, fixed deposits, stocks, anything else?"
- For each one mentioned: "How much goes in monthly/yearly, and how long have you been doing this?"
- If user mentions something high-risk/informal (e.g., chit funds, unregulated schemes): ask about
  liquidity and regulation awareness, then explain trade-offs factually (liquidity, regulatory
  oversight) rather than issuing a flat "don't do this."

**Important for your compliance boundary (see main project plan, Section 2):** this is the exact
point where the bot must stay in "educational explanation" mode — describe how instruments work
and general trade-offs (liquidity, risk, regulation), not "you should put X% into fund Y." That
line is what keeps you out of unlicensed personalized-investment-advice territory.

---

## Phase 7: Goals (invited, not imposed)

**Purpose:** The advisor asks "how can I help you, any questions?" and lets the *user* name the
goal. This keeps the tool consultative rather than prescriptive — also good UX because people
engage more with plans they asked for.

Sample bot flow:
- "What's on your mind — any specific goal you're trying to plan for? (e.g., saving for something
  big, paying off a loan faster, starting to invest, buying a vehicle)"
- Branch based on answer into a goal-specific sub-flow (see Phase 8 for one example).

---

## Phase 8: Goal-Specific Guidance (example: big purchase, e.g. a vehicle)

**Purpose:** Mirror the advisor's concrete-numbers approach to the SUV question.

Example rules of thumb extracted from the video, generalized for your rules engine:
- Loan tenure: recommend keeping tenure well below the max the lender offers (advisor suggested
  ~4-5 years even when 7-8 was available) — shorter tenure = less total interest.
- EMI-to-income ratio: keep any single EMI under roughly 7-8% of total monthly income (this is a
  reasonable general rule of thumb to encode, though total-debt-to-income across all EMIs combined
  is the more standard metric to also check).
- Pre-owned vs. new: compare the *effective* interest rate of a pre-owned-asset loan against a
  personal loan — pre-owned loans can sometimes carry a higher rate, making a personal loan cheaper
  even though it sounds counterintuitive.

This is a good template for your rules-engine style: **discovery question → clarifying number →
rule-of-thumb calculation → plain-language explanation of the trade-off**.

---

## Phase 9: Near-Term Goal Anchoring (reframed — full FI/retirement anchoring is a later-Phase feature for this audience)

**Purpose:** The advisor doesn't hand over a generic formula — he ties the number back to the
lifestyle the user already described earlier in the conversation. For a college student, "target
corpus ≈ 25x annual expenses" is too distant an anchor to be motivating or even meaningful yet —
keep the same *callback-to-their-own-numbers* technique, but aim it at a nearer horizon.

Sample bot flow:
- "Based on what you've told me — [reference their actual stated expenses/goals], you've got about
  [X years] left before you graduate. What do you want to be true about your money by the time you
  start your first job — debt-free, some savings built up, good credit, all of the above?"
- Bot then runs a **nearer-term projection** using their own stated numbers — e.g. "if you keep
  saving ₹[X]/month at your current rate, you'll have ₹[Y] saved by graduation" (via
  `sip_projection` with a short timeline) or "at this rate, your credit card balance clears by
  [month]" (via `debt_payoff_order`) — not the 25x-annual-expenses FI number, which belongs later
  once a user has real income to anchor it to.
- The full FI-number calculator from the main rules engine doc still has a place here, but treat it
  as an **optional, explicitly-invited "curious about the long game?" branch** for students who ask
  about it themselves, not a default phase every conversation walks through — most users in this
  phase of life aren't ready for a 25-year-out number to feel real or useful.

---

## Phase 10: Light Close

**Purpose:** End on a human note, not a spreadsheet. Good for retention — people remember how a
conversation made them feel.

Sample bot flow (rapid-fire style, optional/skippable):
- "Quick fun one before we wrap — what's the last thing you bought that you're really happy about?"
- "Anything you've been meaning to ask about money but haven't had the chance to?"

---

## How this maps to your rules engine (Phase 1 of the main project plan)

| Conversation Phase | Data Captured | Feeds Into |
|---|---|---|
| Money Coming In | allowance/family support, gig income, stability type | Budget baseline, affordability calculations |
| Expense Discovery | category-wise spend (hostel/mess, split expenses, subscriptions, BNPL usage) | Budget view, spending nudges, BNPL/credit-trap detector |
| Safety Net Check | insurance cover, any personal savings, would-fall-back-on-family flag | Priority flag if missing — before any investment nudge; informs whether a starter savings goal outranks other suggestions |
| Debt & Credit Audit | debts (education loan planned/taken, credit card, BNPL, informal), APRs, credit limits/utilization | Debt payoff calculator, BNPL/credit-trap detector, routes to education loan literacy sub-flow if a loan is being planned |
| Investment Audit | instrument, amount, tenure (often empty/minimal for this audience — that's expected, not a gap to force-fill) | Portfolio overview, liquidity/risk flags (educational only) |
| Goals | user-stated goal | Routes to goal-specific sub-flow |
| Goal-Specific Guidance | goal parameters (amount, timeline) | Rules-engine recommendation (rule of thumb, not personalized security advice) |
| Near-Term Anchoring | desired state at graduation/first job | Short-horizon `sip_projection`/`debt_payoff_order` calculators; full FI number only if explicitly requested |

---

## One structural recommendation

Build this as a **branching conversation state machine**, not a single linear script:
- Each phase is a node with 1-3 questions
- User answers update a shared "financial profile" object
- Later phases can reference earlier answers dynamically (this callback behavior — referencing
  their commute distance, their stated lifestyle — is what made the human advisor feel genuinely
  personalized rather than scripted)
- The goal phase (Phase 7) should branch into different sub-flows depending on what the user names
  — build 3-4 of these for your MVP based on what a college student actually asks about most, which
  is a different list than an early-grad's: probably **understanding an education loan before it's
  taken**, **getting out of/avoiding a BNPL or credit-card debt spiral**, **building a small,
  realistic savings habit**, and **understanding a first credit card/building credit correctly**.
  "Starting to invest" and "buying a vehicle" — the early-grad plan's top sub-flows — are real but
  secondary here; most users in this audience aren't there yet.

This structure is what I'll build into the actual chatbot script/prompt design when you're ready —
happy to draft the first sub-flow next. Given the audience shift, I'd suggest **"understanding my
education loan"** or **"stopping the BNPL/credit trap before it starts"** as the highest-value one
to build first, since both address problems specific to this audience that the earlier plan didn't
cover at all.

**One addition for voice:** each phase node should also carry a short "recap on resume" line, since
a live conversation can get interrupted (dropped connection, user distracted, user leaves and comes
back) in a way a persistent chat window doesn't force you to handle. On reconnect, briefly state
where things left off ("last time we talked about your rent and commute — want to pick up with your
safety net, or is there something more pressing today?") rather than silently resuming or restarting
from Phase 1.
