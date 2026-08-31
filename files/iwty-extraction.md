> **⚠️ PARTIALLY ACTIVE — general formula/behavioral content usable now, US-specific
> numbers disregarded until sourced.**
> **Usable now** (currency- and scoring-system-agnostic, per Part B of this file's own analysis):
> the credit-utilization formula (`balance ÷ limit`), the "know your two numbers" rule
> (amount owed + payoff date), the credit-limit-increase cadence/precondition rule, and the
> behavioral content — the "invisible money scripts" list, the "85% solution" onboarding
> philosophy, "playing offense vs. defense" framing, and negotiation-as-first-resort for fee/rate
> problems. None of these are tied to a currency or a specific credit bureau.
> **Disregarded for now**: FICO score composition weights (35%/30%), US typical card APR ranges
> (13-16%), the FICO point-drop figure, and the ~$35 late-fee figure — all tied to the US credit
> system (FICO scale, US issuer norms) and not usable until CIBIL's actual methodology and real
> Indian card terms are separately sourced.
> Kept in the repo for later reference; the disregarded parts should be re-activated deliberately
> once sourced, not by default.

# Extraction: "I Will Teach You to Be Rich" (Ramit Sethi) — Introduction + Chapter 1

## Source characterization — read this before using anything below

- **What this is:** the genuine primary text (front matter + Introduction + full Chapter 1,
  "Optimize Your Credit Cards") of Ramit Sethi's book, Workman Publishing, 2019 edition. Chapters
  2-9 are **not** in this file — only their table-of-contents descriptions are visible, no content.
- **Copyright status — the strongest caution of any source so far.** This is a purchased,
  commercially sold, all-rights-reserved trade book (New York Times bestseller), with an explicit
  publisher copyright notice ("...without written permission of the publisher"). This is materially
  different from your other two sources: the CFEE book is freely distributed for education, and
  even Halan's book (via the Bookey summary) sits in a grayer, but at least third-party-summarized,
  zone. This is a direct scan of purchased commercial content. **Extracting the underlying facts,
  numeric thresholds, and named frameworks (e.g., "credit utilization = balance ÷ limit") is
  defensible — those are facts/formulas, not copyrightable expression. But Sethi's distinctive
  voice, anecdotes, and phrasing below are described/paraphrased, never reproduced, and none of it
  should be treated as cleared for reuse in a commercial product without an actual rights
  conversation** — treat this extraction as research notes for your own rule-writing, not
  as source material to publish from.
- **Jurisdiction: US-specific**, same substitution problem as the LibreTexts book — FICO score,
  401(k), Roth IRA, IRS-specific mechanics. Every dollar figure and percentage tied to the US credit
  system needs the same "concept transfers, number doesn't" treatment as before.

---

## Part A — Numeric rules and formulas (candidates for the rules engine, US-sourced — need Indian equivalents before use)

| # | Rule | Value (US) | Indian equivalent needed |
|---|---|---|---|
| 1 | Credit score composition: payment history weight | 35% of score | CIBIL/Experian India use a different, less publicly transparent weighting — **do not import 35% directly**; needs its own sourcing from CIBIL's public methodology notes if available |
| 2 | Credit score composition: amounts owed/utilization weight | 30% of score | Same caution as #1 |
| 3 | Credit utilization formula | `utilization = balance owed ÷ total available credit`, expressed as % | **This formula itself is universal, not US-specific** — directly usable as-is in your `assess_debt`/credit module |
| 4 | "Good" utilization threshold example given | 25% framed as "much better" than 100% | The formula transfers; the specific threshold number should be checked against CIBIL guidance rather than imported verbatim |
| 5 | Typical credit card APR range | 13-16% (India: recall your earlier extraction already cited 24-36% for missed-payment penalty APR from a different source — these aren't necessarily inconsistent, since US "typical carried-balance APR" and "India penalty APR on missed payment" may be different measurements; don't merge them into one number without checking what each actually measures) | Needs an Indian-market equivalent sourced separately |
| 6 | Missed-payment consequence: credit score drop | "Can drop more than 100 points" (on the 300-850 FICO scale) | CIBIL score scale (300-900) is different — this can't be numerically transposed, only the *qualitative* lesson (missed payments cause significant, multi-month score damage) transfers |
| 7 | Missed-payment late fee | ~$35 | Needs Indian equivalent (varies significantly by issuer) |
| 8 | Credit-limit-increase request cadence | Every 6-12 months, only once debt-free | **This behavioral rule (cadence + precondition) is not currency-specific — directly usable as a process rule**, independent of the dollar amounts in the illustrative example |
| 9 | Extra debt payment impact example | +$100/month on a $30k loan cuts ~7 years off a 10-year term and saves ~$3,500 in interest | The *mechanism* (extra principal payments disproportionately cut both time and interest) is universal and matches your existing `emi_calculation`/debt payoff logic (Section 3 of your rules-engine doc) — don't import the dollar example, but this is good validation that your existing amortization calculator should expose this "what if I pay X more" comparison as a feature, since it's clearly a high-value, easy-to-grasp insight |
| 10 | "Know your two numbers" standard for debt | How much you owe (total), and your payoff date | **Directly usable, currency-independent** — a good addition to your `assess_debt` module: don't just calculate a payoff plan, explicitly surface these two numbers back to the user as the baseline "you should always know this" pair |

---

## Part B — Process/behavioral content (genuinely portable, no currency conversion needed)

This is the strongest part of this extraction — unlike the numeric thresholds, these patterns are
psychological/behavioral and transfer directly regardless of country.

- **"Invisible money scripts" around debt** — a named list of common rationalization patterns
  people use to avoid confronting debt:
  - Social comparison ("at least I don't owe as much as X")
  - Minimization of small purchases against a large existing balance ("$X is nothing compared to
    what I already owe")
  - Normalizing interest payments as "just another fee"
  - Externalizing blame entirely onto lenders/credit card companies
  - Not knowing the actual amount owed
  - Learned helplessness ("I'm just doing my best," implying no agency)

  **Direct application:** this is excellent material for the LLM's conversational tone when a user
  is discussing debt — it gives the system a way to *recognize* these patterns in what a user says
  without being preachy about it, and to gently redirect toward the two concrete numbers (amount
  owed, payoff date) rather than staying in the emotional/avoidant register. This complements the
  Money and Youth debt-trouble checklist (behavioral warning signs) with the *why* behind those
  behaviors — Money and Youth tells you the signs, this explains the psychology producing them.

- **Debt-awareness statistic as a design cue, not a hard rule**: the book claims a majority of
  people in debt don't know their exact amount owed or payoff date. Whether or not the exact
  percentage holds in India, the underlying product implication is clear and worth acting on: **your
  app's debt module should make "amount owed" and "payoff date" impossible to avoid seeing** —
  surfaced prominently rather than buried, since not knowing these two numbers is apparently the
  norm rather than the exception.

- **The "85 Percent Solution"** — a philosophy that getting a financial system "good enough" and
  acting beats waiting for a perfect plan. This is a useful framing principle for your onboarding
  UX specifically: don't require complete financial profile data before giving any value — this
  supports the proactivity/default-and-proceed design pattern already used in your conversation
  architecture (asking one question at a time, giving partial guidance rather than blocking on
  complete data).

- **"Playing offense vs. defense" framing for credit** — a useful reframe for the LLM's tone when
  discussing debt/credit: presenting credit management as an active, structured game with concrete
  next steps rather than a source of anxiety to be endured. Complements the "invisible money
  scripts" content — one explains the trap, the other gives a way to talk about escaping it.

- **Negotiation as a first resort, not a last resort, for fee/rate problems**: the book's core
  behavioral prescription for cutting credit costs is *call and ask* (fee waivers, APR reduction,
  credit limit increases) before anything more drastic. This is a good candidate for a concrete,
  scripted suggestion the LLM can offer when a user's debt-assessment module flags a high-APR
  card — "have you called to ask for a lower rate" is a low-effort, high-value first suggestion,
  and the general shape of the ask (state tenure as a customer, state a specific number, end
  firmly rather than as a question) is a genuinely reusable communication pattern, independent of
  currency.

---

## Part C — What this source does NOT give you (be aware of the gap)

- No asset allocation formula, no retirement corpus multiple, no budget percentage split — Chapter
  1 is entirely about credit/debt; the book's investing and budgeting content (Chapters 3, 4, 7) is
  described only in the table of contents, not present in this file. If you want that content,
  you'd need those chapters specifically.
- No India-market credit data (CIBIL scoring weights, typical Indian card APRs, RBI penalty
  fee caps) — every number here is a US Chapter-1-only starting point requiring separate sourcing,
  not a finished Indian rule.

---

## Cross-reference with what you already have

| Content | Source you already have | This book |
|---|---|---|
| Debt APR threshold for "pay this first" priority | Your rules-engine doc's own default (~15-18%) | Confirms the *shape* of the rule (there's a threshold above which paying debt beats investing) using a similar range (13-16% typical, vs. ~8% average market return) — a second independent source arriving at a comparable structure, though still not India-sourced data |
| Credit utilization formula | Not previously extracted anywhere | New, and directly usable as-is since it's a pure formula, not a currency-dependent number |
| Debt behavioral/psychological patterns | Money and Youth gave you the *symptom checklist* | This book gives you the *underlying rationalization patterns* — genuinely complementary, not overlapping |
| "Know your two numbers" (owed + payoff date) | Not previously extracted | New, directly usable, currency-independent — recommend adding to your `assess_debt` module's required output fields |

**Bottom line:** the numeric content here needs the same India-sourcing work as your LibreTexts
extraction before anything touches the rules engine. The behavioral/psychological content and the
credit utilization formula are ready to use now, with the appropriate care about not reproducing
Sethi's actual text described above.
