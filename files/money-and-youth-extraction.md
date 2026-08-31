> **⚠️ PARTIALLY ACTIVE — process/conceptual content usable now, Canadian-specific figures
> disregarded permanently (not just "for now" — see below).**
> **Usable now** (this file was already almost entirely non-numeric — see its own Source
> Characterization: "essentially doesn't contain" budget/allocation percentages): the **Six-Step
> Decision-Making Model** (Part A — genuinely the standout asset here, a generic decision framework
> your project had nowhere else), the opportunity-cost prompt that goes with it, the debt-trouble
> behavioral checklist (Part B), the "3 Cs of credit" explanation, the buy-vs-lease framework for
> major purchases, the net-worth-as-tracking-concept, and the term-vs-permanent life insurance
> conceptual distinction. None of these carry a dollar figure or a Canada-specific account type.
> **Disregarded**: any Canadian dollar figure, RRSP/RESP and other Canada-specific account types,
> and the Bank of Canada/household-debt commentary — this file's own analysis already called these
> "actively wrong to reference at all for Indian users," which is a stronger and more permanent
> discard than "needs adaptation" (there's no Indian number to substitute in; the claims just don't
> apply).
> Kept in the repo for later reference.

# Extraction: "Money and Youth: A Guide to Financial Literacy" (Gary Rabbior, CFEE, 2018)

## Source characterization

- **What this is:** the complete, genuine primary text (not a summary) of a Canadian financial
  literacy curriculum aimed at teens/young adults, published by the Canadian Foundation for
  Economic Education, freely distributed with IG Wealth Management sponsorship. Copyright held by
  CFEE (© 1997-2018) — free to read, not openly licensed for reuse; treat the same way as Halan's
  book for licensing purposes (a real, named, credible source to cite — not something to reproduce
  wholesale).
- **What it is NOT:** a source of numeric financial rules. I searched specifically for
  percentage-based budget splits, asset allocation formulas, retirement multiples, and emergency
  fund sizing — the kind of content that made Halan's book valuable — and this book essentially
  doesn't contain them. It teaches concepts (compound interest, diversification, credit ratings)
  through definitions and examples, not prescriptive thresholds.
- **Jurisdiction problem, more severe than the LibreTexts book:** this is Canada-specific, with
  Canadian dollar figures (2018 average house price, Canadian household debt levels, RRSP/RESP —
  Canadian retirement/education savings vehicles with no direct Indian equivalent) that are not
  just "need adaptation," they're actively wrong to reference at all for Indian users, and also
  dated (2018 statistics). **Every dollar figure and Canada-specific product name in this book
  should be discarded, not adapted** — this is different from the LibreTexts situation where
  numbers needed a substitute; here there's usually no numeric claim to substitute in the first
  place, since the book teaches the concept without a hard number attached.
- **What it fills that the other two sources didn't:** a genuinely novice-appropriate pedagogical
  approach — this is written for teenagers with no financial background, which is closer to your
  actual target demographic's starting knowledge level than either Halan's book (assumes some
  baseline financial literacy) or the LibreTexts college textbook. Its value to your project is
  mostly in **process/explanation design**, not in numeric rules.

---

## Part A — The one major structural asset: the Six-Step Decision-Making Model (Module 4)

This is the standout find, and it's a genuine gap-filler — none of your other sources gave you a
generic decision framework, and your project needs exactly this for goal-specific sub-flows (e.g.,
"should I buy this car," "which job offer should I take," "should I do this course or that one").

```
STEP 1: Clearly define the problem/decision
STEP 2: Establish criteria (what matters to the user — pick their top 3-5)
STEP 3: List alternatives (their top 3-4 real options)
STEP 4: Score each alternative against each criterion (-2 to +2 scale), sum totals
STEP 5: Make the decision (the score is an input, not the answer — the book is explicit that
         the highest score doesn't have to win; it's a thinking tool, not an oracle)
STEP 6: Review the decision later; learn from it if it can't be undone
```

Plus one framing concept worth carrying into the LLM's conversational style directly: before any
big decision, ask **"what is your opportunity cost — what's the next-best alternative you're
giving up?"** This is a much better prompt for the LLM to use when helping with a goal-specific
decision than a bare pros/cons list, because it forces a genuine trade-off comparison rather than
an isolated evaluation.

**Concrete application to your architecture:** this maps directly onto a `weigh_alternatives` tool
the LLM can call in the Phase 8 "goal-specific guidance" flow (from the conversation-design doc) —
take the user's stated criteria, their 3-4 real options, have the LLM (or the user directly) score
them, and return the weighted result **alongside** an explicit opportunity-cost prompt, exactly as
the book's own Step 5 warns not to treat the score as automatically final.

---

## Part B — Qualitative behavioral checklist: signs of debt trouble (Module 12)

Unlike the APR-threshold approach from your rules-engine doc (Section 2, debt priority based on a
numeric APR cutoff), this is a **behavioral/self-report checklist**, useful as a complementary
signal alongside the numeric one, since a user might not always know or disclose exact APRs but can
usually answer behavioral questions:

- Finding it difficult to save anything
- Continually short of money
- Using savings to pay debt costs
- Near the credit limit on most/all cards
- Missing payment due dates
- Always paying only the minimum on credit cards
- Unaware of how much is owed (in total)
- Debt causing persistent worry / affecting sleep
- Borrowing to pay off past debt
- Borrowing to cover week-to-week/month-to-month living expenses

**Application:** this is a good candidate for a short screening question set the LLM can ask
conversationally when a user's stated numbers are ambiguous or incomplete (e.g., they mention debt
but not a clear APR) — a fallback signal, not a replacement for the numeric threshold check. Also
useful as **the recovery guidance sequence** the book gives (face the problem, contact creditors
directly rather than avoiding them, stop further borrowing, consider consolidation, seek
professional advice) — a reasonable template for what the LLM says to a user who screens positive
on several of these.

---

## Part C — Reusable definitional/conceptual content (for the LLM's explanation layer)

These aren't numeric rules but are well-explained concepts worth having the LLM draw on when
explaining *why*, matching the pattern from the "instrument comparison" module in your rules-engine
doc (Section 4) — the *how it works* layer, not the *what to do* layer:

- **The "3 Cs" of credit** (as this book frames it): **Capacity** (ability to repay, based on
  income), **Character** (track record of reliability/responsibility), **Capital** (assets you
  could liquidate to repay if needed). Useful for explaining to a user why lenders evaluate them
  the way they do, and indirectly, why building a repayment track record matters even before they
  need a large loan.
- **Compound interest walkthrough**: a concrete step-by-step numeric example (grows by increasing
  amounts each year as interest earns interest on interest) — good raw material for the LLM's
  explanation on why starting early matters, though the illustrative numbers themselves are
  arbitrary and can be regenerated by your `run_calculation` tool rather than quoted from the book.
- **Buy vs. lease framework for major purchases (cars)**: the book lays out a clean pros/cons
  structure — leasing means lower monthly payments and lower repair costs but no ownership at the
  end and mileage-limit penalties; buying means full ownership and no mileage restriction but
  higher upfront/monthly cost. This slots naturally alongside your existing EMI/loan-tenure logic
  (Section 3 of the rules-engine doc) as a **prior decision** (buy vs. lease) that should happen
  before the EMI-affordability calculation, not instead of it.
- **Net worth as a tracking concept**: "assets minus liabilities" — simple, but worth having as an
  explicit periodic check-in metric your app could surface (net worth trend over time), distinct
  from the monthly cash-flow tracking already in your MVP feature list.
- **Term vs. permanent life insurance distinction**: explained conceptually (term = coverage for a
  defined period, ends when the need — e.g., dependent children — ends; permanent/whole life =
  lasts for life, structured differently). No numeric guidance given, but the conceptual framing
  is a clean complement to Halan's specific term-insurance-preference rule and multiplier (Section
  6 of the "Let's Talk Money" extraction, if you're keeping that document) — this book explains
  *why* term exists as a category; Halan's book gives *the sizing rule*. Neither alone is complete.

---

## Part D — What to explicitly discard

- Any dollar figure in this book (Canadian, 2018, and specifically flagged in the book as national
  averages that were already described as concerning/too-high by the author) — none of it applies
  to Indian users or is even current for Canadian ones anymore.
- RRSP, RESP, and other Canada-specific account types — do not attempt a 1:1 mapping to Indian
  equivalents (PPF/NPS/Sukanya Samriddhi) without separately verifying the actual mechanics match;
  a naive name-swap would misrepresent how the Indian instruments actually work.
- The Bank of Canada / Canadian household debt commentary — purely illustrative for a Canadian
  audience, not usable as country context for India.

---

## Cross-reference: how this source relates to what you already have

| Content type | LibreTexts (US textbook) | Halan (India, via Bookey summary — now removed per your instruction) | This book (Canada, youth literacy) |
|---|---|---|---|
| Numeric thresholds (budget %, allocation %, retirement multiple) | Some (TVM formulas, DTI framework) | Many (now discarded) | **Almost none** |
| Generic decision-making process | Not extracted | Not present | **Yes — the standout asset here** |
| Behavioral/qualitative checklists | Not extracted | Not present | **Yes — debt trouble signs** |
| Conceptual/pedagogical explanations for a true beginner | Moderate (college-level) | Moderate (assumes some literacy) | **Strongest fit — written for absolute beginners, closest to your actual user's starting point** |
| India-specific applicability | Needs substitution | Direct (was the main value) | **None — actively discard all figures** |

**Net effect on your project:** this source is best used for *how the LLM teaches and frames
things* and for the *decision-making tool* — not for populating the rules-engine's numeric
thresholds table, which should keep leaning on regulator/survey-sourced Indian data per your Route
A/B plan, or a primary-source Indian book like Halan's if you obtain the actual text rather than a
third-party summary of it.
