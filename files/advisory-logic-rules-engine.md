# Advisory Logic — Rules Engine Specification

This is the actual decision logic the platform uses to generate guidance — separate from the
conversational layer (LLM) that delivers it. Everything here should live in your deterministic
backend (`run_calculation` + a rules layer), versioned and unit-tested independently of prompts.

Each rule is tagged:
- 🟢 **Educational/calculator** — safe, factual, no personalization risk
- 🟡 **Rule-of-thumb guidance** — general principle applied to user's numbers, needs a disclaimer
- 🔴 **Would require licensing if made specific** — kept generic/instrument-type-level only, never
  named products

---

## 0. Priority Ordering (the sequencing logic itself is advice)

Before any specific calculation, the platform should enforce this priority order — mirrors the
advisor's sequencing (safety net before growth):

1. High-interest debt check (APR > ~15-18%, e.g. credit card debt) → flag as top priority over investing
2. Health insurance coverage check → flag as priority if missing/inadequate
3. Emergency fund adequacy → flag if below target
4. Only after 1-3 are addressed → surface investment/growth guidance

🟡 This ordering logic itself is a piece of advice ("pay off this before investing that") — keep it
rule-based and transparent (show the user *why* — e.g. "your credit card APR (36%) is higher than
any realistic investment return, so paying it down is the higher-value move") rather than a black
box.

---

## 1. Emergency Fund Target 🟢

**Reconciled from two sources**: this project's original 2-tier version (below, superseded) and the
more granular **3-6-12 Month Rule** from [smartplan-finance-extraction.md](smartplan-finance-extraction.md)
Ch.5, which is India-sourced and adds a third stability tier plus explicit escalators the original
version didn't have. This is now the authoritative version — update any code/prompt still using the
old 2-tier shape.

```
emergency_fund_target(monthly_essential_expenses, employment_stability, has_dependents=False, has_large_emi_burden=False):
    base_months = 3   if employment_stability == "stable_govt_or_secure"   # very secure employment, low responsibilities
                = 6   if employment_stability == "salaried_private"         # most salaried professionals, moderate responsibilities
                = 12  if employment_stability == "irregular_or_business"    # freelancers, business owners, irregular income

    months_buffer = base_months
                  + 1 if has_dependents
                  + 1 if has_large_emi_burden

    target = monthly_essential_expenses * months_buffer
    gap = target - current_emergency_fund_amount
    return { target, gap, months_buffer, storage_guidance }
```

Notes:
- Use *essential* expenses (housing, food, commute, insurance premiums, minimum debt payments),
  not total spending including discretionary — this is a common real-world calculation error to
  avoid, and matches SmartPlan Finance's own guidance on this point.
- **Escalators stack, tiers don't downgrade** — dependents and a large EMI burden each add a month
  regardless of base tier; a freelancer with dependents and a large EMI lands at 14 months, not
  capped back down to 12.
- **Where "probation" fits**: the original version grouped probation with freelance/variable at the
  higher tier; the reconciled version instead treats probation as `salaried_private` (6 months,
  same as a stable salaried role) unless the user's income is *also* variable during probation (e.g.
  a probation period with reduced/uncertain pay) — in that case use `irregular_or_business`. Don't
  auto-derive this from the word "probation" alone; ask, since it varies by employer.
- 🟢 **Storage guidance** (new, from the SmartPlan source — return this alongside the number, don't
  just hand back a bare target): immediate-access portion in a savings account, remainder in liquid
  mutual funds or short-term deposits, never in stocks/long-term investments/large cash-at-home
  holdings. This turns the calculator output into something actionable, not just a target number.
- 🟡 Optionally flag existing credit limit as a *temporary* buffer if the emergency fund is still
  being built — but always pair this with an explicit caveat: "credit is a stopgap, not a
  replacement for savings, because you'll owe it back with interest if not paid off quickly." Only
  surface this for users with demonstrated stable income — don't suggest it to someone flagged as
  income-unstable, since relying on credit is riskier for them.
- **Related but distinct**: [psychology-of-money-extraction.md](psychology-of-money-extraction.md)'s
  `calculate_margin_of_safety` module uses a continuous multiplier (1.0x-2.0x against a 3-month base,
  plus a further stress-test cushion) rather than discrete tiers+escalators. Treat that as a
  complementary *stress-testing* lens for a "how much room for error do I really have" conversation,
  not a competing base calculation — this reconciled 3-6-12 version is the one to use for the actual
  `run_calculation("emergency_fund_target", ...)` tool call.
- **College-student audience note**: for the schema in [llm-advisor-architecture.md](llm-advisor-architecture.md)
  (which uses `family_supported_fixed`/`family_supported_variable`/`gig_variable`/`mixed` for
  students without a salary), map `family_supported_fixed` → `salaried_private` tier (6 months, since
  a fixed monthly transfer behaves like stable income for buffer-sizing purposes) and
  `family_supported_variable`/`gig_variable`/`mixed` → `irregular_or_business` tier (12 months) —
  the underlying logic (how predictable is the money) is the same regardless of whether the source
  is an employer or a parent.

<details>
<summary>Superseded 2-tier version (kept for reference only — do not implement)</summary>

```
emergency_fund_target(monthly_essential_expenses, income_stability):
    months_buffer = 3 if income_stability == "stable_salaried"
                  = 6 if income_stability == "variable" or "probation" or "freelance"
    target = monthly_essential_expenses * months_buffer
    gap = target - current_emergency_fund_amount
    return { target, gap, months_buffer }
```

</details>

---

## 2. Debt Payoff Ordering 🟢 (mechanics) / 🟡 (which strategy to suggest)

```
debt_payoff_order(debts: [{balance, apr, min_payment}], strategy):
    if strategy == "avalanche":
        order = sort(debts, by=apr, descending=True)
    if strategy == "snowball":
        order = sort(debts, by=balance, ascending=True)
    total_interest_avalanche = simulate(debts, order=avalanche_order)
    total_interest_snowball = simulate(debts, order=snowball_order)
    return { avalanche_order, snowball_order, interest_saved_by_avalanche }
```

Guidance logic:
- 🟢 Always show both orderings and the interest-cost difference — this is factual, not advice.
- 🟡 Default suggestion: avalanche (saves the most money) — but explicitly note snowball may work
  better for someone who needs motivational quick wins, and let the user choose. Frame as "here's
  the trade-off," not "you should do X."
- 🟡 Any debt with APR above a threshold (suggest ~15% as a starting point, adjustable) should be
  flagged as "pay this before considering investing," per the priority ordering in Section 0.

---

## 3. EMI / Big-Purchase Affordability 🟢 (calculation) / 🟡 (threshold guidance)

```
emi_calculation(principal, annual_rate, tenure_months):
    monthly_rate = annual_rate / 12 / 100
    emi = principal * monthly_rate * (1 + monthly_rate)^tenure_months
          / ((1 + monthly_rate)^tenure_months - 1)
    total_interest = emi * tenure_months - principal
    return { emi, total_interest }
```

Threshold rules extracted from the advisor's guidance, generalized:
- 🟡 Recommended max EMI as % of monthly income: **~7-8% for a single big-ticket EMI**; if the user
  has multiple EMIs running, flag if *combined* EMI load exceeds roughly **35-40% of monthly
  income** (this is a more standard overall debt-to-income guideline worth adding — the video only
  covered the single-EMI case).
- 🟡 Loan tenure guidance: even if a lender offers longer tenure (e.g. 7-8 years for a vehicle),
  suggest capping at ~4-5 years to limit total interest paid — show the total-interest comparison
  at both tenures so the user sees *why*, not just the recommendation.
- 🟡 Pre-owned asset loans: compare the effective interest rate of an asset-backed pre-owned loan
  against a personal loan rate — sometimes the personal loan is cheaper despite being unsecured.
  Always run both calculations and show the comparison rather than asserting one is better.

---

## 4. Investment Instrument Comparison 🟢 (factual attributes) / 🔴 boundary

```
instrument_comparison(instrument_type):
    return {
        liquidity: "...",       # e.g. lock-in period, redemption timeline
        regulatory_body: "...", # e.g. SEBI-regulated, RBI-regulated, unregulated
        typical_risk_level: "...",
        tax_treatment: "..."
    }
```

For instruments to cover initially (India-specific): PPF, ELSS mutual funds, regular mutual funds,
NPS, fixed deposits, chit funds, stocks (general category only).

🔴 **Hard boundary:** this function returns *category-level* facts about instrument *types*. It
never:
- names a specific fund, AMC, or stock
- says "put X% of your money into Y"
- predicts specific returns as a promise (projections must be clearly labeled as estimates using
  assumptions, not predictions — see Section 6)

The chit fund vs. mutual fund comparison from the video is the model case: explain liquidity
(lock-in periods, redemption timelines) and regulatory oversight factually, and let the user draw
their own conclusion, rather than issuing "don't invest in chit funds" as a directive.

---

## 5. Recurring/Discretionary Spend Flags 🟢

```
subscription_audit(recurring_charges: [...]):
    total = sum(recurring_charges)
    pct_of_income = total / monthly_income
    flag if pct_of_income > threshold (suggest ~5-8% as a starting point for "worth reviewing")
    return { total, pct_of_income, items_flagged }
```

Purely observational — surface the number, don't moralize about specific purchases (mirrors the
advisor's neutral handling of the TV/gadget spending — acknowledge, don't judge).

---

## 6. Financial Independence / Retirement Number 🟢 (mechanics) / 🟡 (assumptions)

```
fi_number(annual_expenses, expense_growth_assumption, expected_return_assumption):
    # Standard FIRE-style multiplier, adjustable
    multiplier = 25   # default; can expose as adjustable (20-30 range depending on
                       # withdrawal-rate assumption used)
    target_corpus = annual_expenses * multiplier
    return { target_corpus, assumptions_used: {...} }
```

Notes:
- 🟡 Always show the assumptions used (expected return %, inflation %, withdrawal rate) alongside
  the number — never present a single bare figure as fact. The video's "50-60 crore" answer came
  *from the user's own stated lifestyle*, not a generic number — replicate that by using their
  actual profile data (Section 6 of the architecture doc) rather than a template figure.
- 🟡 For India specifically, default assumptions should reflect India-relevant inflation (~6-7%
  long-run) and realistic post-tax equity return assumptions rather than borrowing US FIRE-community
  defaults — flag this as a config value to research/validate with real data before shipping, not
  something to hardcode from memory.

---

## 7. SIP / Compound Growth Projection 🟢 (mechanics) / 🔴 boundary on framing

```
sip_projection(monthly_amount, years, expected_annual_return):
    months = years * 12
    monthly_rate = expected_annual_return / 12 / 100
    future_value = monthly_amount * (((1 + monthly_rate)^months - 1) / monthly_rate) * (1 + monthly_rate)
    return { future_value, assumptions: {expected_annual_return, years} }
```

🔴 Must always be labeled clearly as an **estimate based on assumed returns, not a guarantee** —
this is a standard, necessary disclaimer for any return projection, not optional legal boilerplate
to skip. Never let this number appear in a UI without the assumption and disclaimer attached in the
same view.

---

## 8. Expense Reallocation Module 🟢 (mechanics) / 🟡 (benchmark-based flags)

**Purpose:** unlike Sections 1-7, this module doesn't answer "what should you prioritize" — it
answers "where's the money to fund that priority," by finding gaps between the user's spending and
a sourced benchmark, then connecting any potential saving back to whatever gap the priority modules
identified (emergency fund shortfall, debt payoff acceleration, etc.).

```
find_expense_reallocation(profile, target_gap_amount):

    # Step 1 — categorize (mechanical, no judgment)
    categorized = categorize_transactions(profile.transactions)
    # buckets: housing, food, transport, subscriptions, debt_service,
    #          insurance_premiums, family_obligations, discretionary

    # Step 2 — detect recurring charges even if unlabeled
    recurring = detect_recurring(categorized)
    # same merchant/amount at ~monthly cadence -> flagged as subscription-like

    # Step 3 — benchmark each category against sourced reference data
    # (e.g. MoSPI Household Consumption Expenditure Survey, matched by
    #  income bracket and city tier — NOT an invented "X% of income" rule)
    benchmarked = []
    for category, amount in categorized:
        if category in EXCLUDED_FROM_FLAGGING:   # see guardrail below
            continue
        benchmark_range = get_benchmark(category, profile.income_bracket, profile.city_tier)
        if amount > benchmark_range.high:
            # Step 4 — diagnose driver using variance decomposition
            driver = diagnose_variance(category, profile.transactions)
            # driver = "quantity_effect" (too many purchases/trips)
            #        | "price_effect" (too expensive per purchase/trip)
            potential_saving = amount - benchmark_range.midpoint
            benchmarked.append({
                "category": category,
                "current_monthly": amount,
                "benchmark_range": benchmark_range,
                "driver": driver,
                "potential_monthly_saving": potential_saving,
                "source": benchmark_range.source
            })

    # Step 5 — rank by potential saving, not by moral weight
    ranked = sort(benchmarked, by="potential_monthly_saving", descending=True)

    # Step 6 — tie back to whatever goal/gap triggered this call
    for item in ranked:
        item["reallocation_impact"] = project_impact(item["potential_monthly_saving"], target_gap_amount)
        # e.g. "closes your emergency fund gap ~3 months sooner if redirected"

    return ranked
```

**Where it's called from:** not as a standalone Section 0 priority step — it's invoked *by* the
other modules once they've identified a gap (e.g. Section 1's emergency fund shortfall, or a debt
payoff timeline from Section 2) to make the recommendation actionable: "here's a shortfall, and
here's where your own spending could close it."

**Guardrails (hard rules, not suggestions):**
- 🟢 **Variance decomposition uses the book's own formula** (`Variance = quantity effect + price
  effect`) to distinguish "spending too often" from "spending too much per instance" — this
  determines whether the surfaced suggestion is about frequency or substitution, not a guess.
- 🟡 **Benchmarks must come from sourced survey data** (MoSPI HCES or equivalent), matched by
  income bracket and city tier — never a flat invented percentage. If no sourced benchmark exists
  for a category yet, that category is simply not flagged rather than filled with a guessed number.
- 🔴 **`EXCLUDED_FROM_FLAGGING` is a hard exclusion list, not a soft preference** — categories tied
  to stated life circumstances (family support/remittances, dependents, medical/health-related
  spend, childcare) are visible in the full report for transparency but never appear in the
  "recommended cuts" ranking by default. A benchmark flag on medically or family-necessary spending
  is more likely to be wrong or unwelcome than helpful — mirrors the video advisor's neutral,
  non-judgmental handling of lifestyle spending (the TV, the long commute chosen for childcare).
- 🔴 **No causal/psychological narrative is ever generated** — the module (and the LLM narrating
  it) states the number and the mechanical driver (quantity vs. price effect) only. It never
  speculates about *why* the user spends this way (stress, habit, upbringing) — that's outside
  what any of this data can actually support and risks feeling invasive rather than helpful.

---

## Summary table: what's safe to automate now vs. what needs a compliance review first

| Feature | Status |
|---|---|
| Emergency fund calculator | 🟢 Build now |
| Debt payoff calculator (avalanche/snowball) | 🟢 Build now |
| EMI/affordability calculator | 🟢 Build now |
| Instrument comparison (educational, category-level) | 🟢 Build now |
| Subscription/spend audit | 🟢 Build now |
| Expense reallocation (category benchmarking + variance driver) | 🟡 Build now, but gate on sourcing real benchmark data (MoSPI HCES or equivalent) — don't ship with invented benchmarks |
| FI number calculator | 🟢 Build now (with clear assumptions shown) |
| SIP projection calculator | 🟢 Build now (with clear disclaimer) |
| Priority ordering logic (what to do first) | 🟡 Build now, but review wording with a compliance-aware eye — this is the most "advice-like" piece even though it's rule-based |
| Naming specific funds/stocks/products | 🔴 Do not build without licensing/RIA partnership review |
| "Should I buy X specific investment" type answers | 🔴 Redirect to educational explanation only |

---

This is the logic layer as it stands from everything discussed. It's not yet validated against a
real compliance review — treat the 🟡 thresholds (7-8% EMI ratio, 3-6 month emergency fund, 25x FI
multiplier, 15% debt-priority APR cutoff) as reasonable starting defaults to build with, not final
numbers — they're worth sanity-checking against current Indian personal-finance norms before
launch, and should be configurable rather than hardcoded so you can tune them as you learn from
real users.
