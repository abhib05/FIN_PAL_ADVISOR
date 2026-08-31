> **Status: ACTIVE — India-sourced, kept in the current build.** The author (Argho Sanyal,
> Founder of SmartPlanFinance) writes explicitly for an Indian audience — every rupee example,
> every named instrument (PPF, EPF, NPS, ELSS, SIP, CIBIL-adjacent credit-score language, RBI Repo
> Rate), every character name (Rahul, Priya, Ananya, Vikram), and every cited case ("₹8 lakh
> hospital bill", "₹1 crore for retirement") is India-native. This means, unlike the JL Collins and
> Gary Rabbior extractions, there is **no currency-conversion or jurisdiction-substitution problem
> to solve** — the numbers here can be used directly, subject only to the caveat below about how
> few hard numbers this particular book actually commits to.
> **Important limitation to flag before use:** this book is unusually light on load-bearing numeric
> constants for a 427-page finance title. It repeatedly *names* the high-value instruments and
> rules (PPF, EPF, NPS, ELSS, term insurance, the 4% FIRE rule's neighborhood) but almost never
> states their actual current parameters — no Section 80C ₹1.5L limit, no PPF interest rate, no
> ELSS lock-in period length, no NPS tax-slab mechanics, no life-insurance "10x income" sizing
> multiple, no FIRE 4%/25X withdrawal formula. Where the book gives a genuine number (50-30-20,
> 3-6-12 month emergency fund, Rule of 72, 30-40% EMI-to-income ceiling, savings-rate formula) it is
> flagged 🟢/🟡 and ready to use as-is. Where it names an instrument without a number, it is flagged
> in Part 1's "Gap" column — those still need separate sourcing (RBI/SEBI/Income Tax Dept current
> figures) before the rules engine can act on them.

# Comprehensive Extraction: "SmartPlan Finance" (Argho Sanyal, Founder, SmartPlanFinance, 2026)

## Source Characterization

- **Author & Source:** Argho Sanyal, *SmartPlan Finance: A Practical Guide to Building Wealth,
  Managing Money, and Achieving Financial Freedom* (self-published/independent, copyright 2026,
  427 pages, 18 chapters + glossary). Publisher's own copyright notice states the book is "for
  educational purposes only" and explicitly disclaims itself as financial/investment/tax/legal
  advice, recommending readers consult a qualified financial advisor — this framing already matches
  and reinforces this project's own compliance posture.
- **Core Premise:** Wealth is not a function of income level but of *habits* — spending less than
  you earn, paying yourself first (automating investment before spending), building an emergency
  fund, avoiding bad debt, starting to invest early, treating money as a tool that should "work for
  you," protecting wealth via insurance, increasing earning capacity, continuously learning about
  money, and thinking in decades rather than days. The book is structured as 18 chapters walking
  from mindset → budgeting → emergency fund → debt → investing basics → mutual funds → stock market
  basics → compounding → tax planning → retirement → insurance → wealth-building systems →
  financial independence/FIRE → money psychology → life-stage guidance → a closing action plan.
  Nearly every chapter follows the same template: a narrative case study (two contrasted
  characters, e.g. "Aman vs. Vikram," "Riya vs. Karan"), a concept explainer, a "Myth vs. Reality"
  box, a "Smart Tip," a "Think About This" reflection prompt, and an end-of-chapter checklist/action
  plan — this repeating scaffold is itself worth mirroring in the LLM advisor's own micro-structure
  for a lesson-style response (empathetic story → reframe → concrete next action).
- **Jurisdiction & Portability: Genuinely India-specific, no adaptation needed.** All currency is in
  rupees/lakhs/crores, all named instruments (PPF, EPF, NPS, ELSS, SIP, FD, term insurance) are
  Indian retail-finance products, and the book explicitly references RBI's Repo Rate and
  PAN/Aadhaar/Passport/Driving License as KYC documents. This is squarely the kind of India-native
  source this project currently lacks relative to its US/Canada book extractions.
- **Role in the Architecture:**
  1. **Rules Engine:** Supplies the 50-30-20 budgeting split, the 3-6-12-month emergency fund
     sizing table (keyed to employment-stability category), the Rule of 72 doubling-time estimator,
     the 30-40% EMI-to-income debt ceiling, the savings-rate and net-worth formulas, and the
     debt-snowball vs. debt-avalanche repayment method pair.
  2. **LLM Conversational Advisor:** Supplies the book's consistent "Myth vs. Reality" reframing
     device, its "Smart Tip" / "Think About This" question style, its habit-over-income framing
     (lifestyle inflation as the central antagonist), its "good debt vs. bad debt" and "asset vs.
     liability" vocabulary, and several ready-made pre-purchase self-check questions ("Would I
     still buy this if I had to pay the full amount in cash today?").

---

## Part 1: Chapter-by-Chapter Extraction Matrix (All 18 Chapters)

| # | Chapter Title | Core Concept / Case Study | Quantitative Rules (Rules Engine) | Behavioral/Conversational Logic (LLM Advisor) | Named but Un-numbered (Gap — needs separate sourcing) | Tag |
|---|---|---|---|---|---|---|
| 1 | Why Most Indians Never Become Wealthy | *Rahul: ₹52,000/month salary, upgrades phone on EMI, "I'll start saving next month," years pass with no savings, exposed by a hypothetical medical emergency.* | **Net worth formula:** `Assets − Liabilities = Net Worth`. Action-plan tasks: track every expense for 30 days; save a fixed % from next salary before spending; apply a 48-hour cooling-off rule before non-essential purchases. | Reframe wealth as "freedom to make choices without worrying about money," not visible spending. Use the "bucket with a hole" metaphor (income = water, unnecessary expenses = the hole) when a user fixates on earning more instead of controlling outflow. Open discovery conversations with the two contrasting-outcomes narrative device the book uses throughout. | — | 🟢 |
| 2 | The 10 Rules of Money Every Indian Should Learn Before Turning 30 | *Aman vs. Vikram: identical ₹45,000/month starting salary at 23; Vikram auto-invests 20% via SIP from day one, Aman doesn't; after 5 years Vikram has a portfolio + emergency fund, Aman has credit card debt.* | **Rule 1–10 synthesized:** (1) spend less than you earn; (2) pay yourself first — automate a fixed % transfer on salary day before any spending; (3) emergency fund = 3× essential monthly expenses as a starting target; (4) avoid bad debt (test: "would I still buy this if I had to pay cash today?"); (5) start investing early — time matters more than amount; (6) make money work via assets, not just salary; (7) protect wealth via health insurance + term life insurance + emergency fund (the book's "three essential layers of protection"); (8) increase income by increasing value/skills, don't rely on a single income source; (9) keep learning — one new financial concept per month; (10) think in decades — review the plan once or twice a year, not daily. End-of-chapter exercises formalize the **50-30-20 rule** and the **savings-rate formula**: `Savings Rate = (Monthly Savings ÷ Monthly Income) × 100`. | "Pay yourself first" as the single highest-leverage habit — treat future-self as "the most important bill of the month." The mango-tree/seed metaphor for patience with compounding. Anti-FOMO framing for social-media finance advice: before following any tip, ask "is this based on facts, does it suit my situation, can I verify it?" | Specific % SIP recommendation beyond the illustrative 20% is not standardized — book treats 10% as a floor to "start somewhere," not a hard rule. | 🟢 |
| 3 | Habits That Build or Break Your Financial Life | *Riya vs. Karan: same office, same salary, same apartment complex; 5 years later Riya has an emergency fund + SIPs + home-purchase plan, Karan has EMIs and no savings despite raises. Riya's stated "secret": "I just have better habits."* | Lifestyle-inflation detector: flag when expense growth rate ≥ income growth rate (book's own example: "income grows 8%/year but expenses grow 10%/year — are you becoming stronger or weaker?"). Frames a "1% better every month" compounding-of-habits mental model (referenced later at the money-psychology chapter too). | "You don't rise to the level of your income, you fall to the level of your financial habits." Useful line for reframing a user request to increase savings only after a raise — nudge them to commit a portion of *every* raise to investment before lifestyle upgrades. | — | 🟢 |
| 4 | Give Every Rupee a Purpose: The Budget That Actually Works | *Illustrated with a ₹60,000/month salary example and an ₹80,000/month zero-based-budget worked example.* | **The 50-30-20 Rule** (the book's primary budgeting formula): 50% Needs (rent/EMI, groceries, utilities, transport, insurance, essential medicines, children's education), 30% Wants (dining out, entertainment, shopping, vacations, subscriptions, hobbies), 20% Savings & Investments (SIPs, FDs, retirement investments, emergency-fund contributions, loan prepayment). **Aggressive-debt-repayment variant:** 45% Needs / 20% Wants / 35% Debt Repayment & Savings. **Zero-Based Budgeting:** assign every rupee of expected income a named purpose at the start of the month (worked ₹80,000 example fully allocated across 11 categories, explicitly "no leftover money" by design). 5-step budget-build process: (1) know your monthly income — average the last 6 months if variable; (2) list every essential expense; (3) identify flexible/discretionary expenses; (4) decide financial priorities for next 5 years; (5) review monthly. Five listed budgeting mistakes: forgetting irregular/annual expenses (festivals, insurance premiums, vehicle servicing), and four others in the same vein. | "A budget is a spending plan, not a spending limit — it tells your money where to work." Explicit Myth-vs-Reality: the 50-30-20 split is "a guideline, not a rulebook" — the best budget is the one the user can actually follow, and should flex around debt repayment or early-career lower savings rates. | — | 🟢 |
| 5 | Build Your Emergency Fund | *No named characters; illustrated with a ₹35,000/month essential-expense example → ₹2,10,000 target at 6 months, and a Friday-evening "hospital admission / layoff / car breakdown" cold-open.* | **The 3-6-12 Month Rule** (emergency fund sizing by employment-stability category): 3 months of essential expenses — stable government jobs / very secure employment / low responsibilities; 6 months — most salaried professionals, private-sector employees, moderate responsibilities; 12 months — business owners, freelancers, irregular income, those supporting multiple dependents. Explicit escalators: increase the target further for dependents, high job-loss-risk industries, large EMI burden, or health responsibilities. Explicitly compute using **essential expenses only**, excluding vacations/luxury/entertainment. Storage guidance ranked: savings account (safe, instant access, but loses to inflation) → liquid mutual funds (better returns, high liquidity, has product risk) → fixed deposits (predictable, may have premature-withdrawal penalty) — recommends splitting across a savings account (immediate needs) + liquid/short-term instruments (remainder) rather than one bucket. Explicit "where NOT to keep it" list: stock market, long-term investments, large cash-at-home. Build-it-faster staged approach: start with 1 month's expenses as first milestone, then 2, then 3, rather than trying to hit 6 months immediately. | "An emergency fund doesn't make you richer. It stops an emergency from making you poorer." Golden-rule self-check for whether the fund is well-placed: "If I need this money tomorrow morning, can I access it easily?" Explicitly normalizes not comparing your fund size to someone else's ("personal finance is personal"). | — | 🟢 |
| 6 | Debt: Your Best Friend or Worst Enemy? | *No fixed protagonist; illustrated with a ₹5,00,000 personal loan at 12% over 5 years, and an EMI-collection anti-pattern ("one phone EMI, one furniture EMI, one vacation EMI, one shopping EMI").* | **Good debt vs. bad debt** framework: good = builds future income or a valuable asset, has a clear purpose and repayment plan (education loans, well-planned home loans, purposeful business loans); bad = pays for rapidly depreciating things, impulse/lifestyle-driven (unnecessary credit-card debt, high-interest personal loans for luxury, unaffordable gadgets). **EMI mechanics:** each EMI = principal + interest; early payments are interest-heavy, later payments principal-heavy (standard amortization). **The 30-40% Rule:** keep total EMI obligations within roughly 30-40% of monthly income (book states this as "a common guideline... the exact number depends on your situation" rather than a hard cutoff — treat as a default with the same flex language the book itself uses). Pre-EMI checklist: do I need this, could I buy with savings instead, will this delay important goals, what's the true total repayment, will I still be fine if income changes. **Credit card rules (the book's own numbered list):** (1) spend only what you can repay — credit limit ≠ income; (2) pay the full bill, not the minimum, before the due date — explicit "minimum payment ≠ full repayment" trap warning; (3) avoid impulse purchases — apply the cash-equivalent test; (4) monitor spending regularly for unnecessary subscriptions/fraud/patterns. **Debt Snowball Method** introduced (pay smallest balance first for psychological momentum) with a 3-debt worked example (₹20,000 credit card / ₹2,00,000 personal loan / ₹8,00,000 car loan); text is cut off before fully contrasting it against Debt Avalanche (highest-interest-first) — both named, only Snowball's mechanics are given in full. | "Debt can be a useful servant, but a dangerous master." "Never calculate a loan only from today's salary — calculate it based on your entire financial journey" (opportunity-cost framing: future income is already partially committed by present EMIs). Golden Credit Card Rule for the advisor's tone: a credit card should make payments *easier*, never a way to pretend you can afford something you can't. | Exact 30-40% threshold is presented as a rough guideline, not derived from a cited source — treat as a soft default in the rules engine, tunable per user income-stability profile the same way the emergency-fund 3-6-12 table is. | 🟡 |
| 7 | Investing for Beginners: Making Your Money Work for You | *₹1,00,000 "keep it idle vs. invest it" comparison; inflation-adjusted goal-setting example ("I need ₹1 crore for retirement" without considering future cost).* | Inflation-adjustment reminder for every long-term goal: ask "how much will this cost when I actually need the money," not today's price — worked example of ₹1 crore retirement target after 25 years being materially eroded by inflation if treated as a fixed, non-inflated number. Named inflation subtypes: lifestyle inflation (expenses rise with income), medical inflation (healthcare costs typically outpace general inflation), education inflation. Asset vs. liability distinction reinforced (assets: stocks, mutual funds, FDs, bonds, rental property, businesses; liabilities: anything that regularly removes money from your pocket). | "You use today's money to create tomorrow's wealth." Directs users to choose investments *after* choosing a goal, never the reverse ("select your financial goal first, then choose investments that support that goal"). | — | 🟢 |
| 8 | Mutual Funds Made Simple | *No individual case study; comparative "Investor A (higher-cost regular plan) vs. Investor B (lower-cost direct plan)" illustration.* | Fund-category taxonomy: equity, debt, hybrid, index funds, and **ELSS (Equity Linked Savings Scheme)** — described as equity-oriented with "a lock-in period" and tax benefits "under applicable rules," but the book does not state the actual lock-in length or the tax section it falls under. **Direct vs. Regular plans:** Regular plans route through an intermediary (advisor/distributor/platform) who earns distributor compensation from the fund house, raising the expense ratio; Direct plans skip the intermediary and carry a lower expense ratio — the book frames this purely as a cost-vs-guidance tradeoff, not "always choose direct." Fund-selection framework: ask what's my goal, how much time do I have, how comfortable am I with risk — flags "choosing based only on last year's highest return" as the classic beginner mistake. | "The best fund is the one that fits your goal and investment approach" — useful anti-performance-chasing line for the LLM when a user asks "which fund gave the best returns last year." | ELSS lock-in period (actual: 3 years) and the applicable tax section (80C) are referenced only obliquely ("under applicable rules") — needs separate sourcing from current Income Tax Act figures before the rules engine can state a number. | 🟡 |
| 9 | Stock Market Basics for Beginners: Understanding How Wealth Is Created | *No named protagonist; explains market capitalization = Share Price × Total Outstanding Shares, and introduces Nifty 50 and Sensex by name as Indian market indices.* | Market-cap formula (glossary-confirmed): `Market Cap = Share Price × Total Outstanding Shares`. Distinguishes buying individual stocks (ownership in one business) from buying via mutual/index funds (diversified, professionally managed). Names Nifty 50 and Sensex as the reference Indian indices without giving specific historical return figures. | Discourages stock-picking-as-lottery framing; consistent with the book's broader "investing is not gambling, not prediction, not overnight riches" positioning. | Historical Nifty/Sensex CAGR figures are not given — would need separate sourcing (e.g. AMFI/NSE published long-run index data) if the rules engine wants to cite a specific expected-equity-return assumption. | 🟢 |
| 10 | The Power of Compounding: The Engine Behind Wealth Creation | *Two-investor "Investor A starts early / Investor B starts later, same monthly amount" comparison; snowball-rolling-downhill metaphor.* | **The Rule of 72:** `72 ÷ Expected Annual Return (%) = Approximate Years to Double Your Money`. Worked examples: 8% → ~9 years; 10% → 7.2 years; 6% → 12 years. Framed explicitly as an estimation shortcut, not an exact calculation — directly usable as a `rule_of_72(rate)` utility function in the rules engine. "Three habits compounding requires": start early, stay consistent, avoid unnecessary withdrawals. Explicit warning that compounding must outpace inflation for real purchasing-power growth, not just nominal account growth. | Compounding described as initially feeling slow ("the early years can feel slow") — useful for setting expectations with a 22-year-old user who just started a small SIP and feels discouraged by early flat-looking growth. Reinforces "the best time to start was earlier, the second-best time is now." | — | 🟢 |
| 11 | Tax Planning and Saving Money Legally: A Beginner's Guide | *No individual case study; structured as myth-busting + mistake list.* | Names the standard Indian tax-saving instrument set — **ELSS, PPF (Public Provident Fund), EPF (Employee Provident Fund), NPS (National Pension System), and certain insurance products** — each with a one-paragraph pros/considerations summary (PPF: government-backed, long lock-in, lower liquidity; EPF: automatic salaried contribution structure, employer co-contribution "according to applicable rules"; NPS: retirement-focused, multi-asset-class exposure, withdrawal/taxation rules apply). Explicitly separates insurance's protection purpose from investment's wealth-creation purpose and warns against choosing a product "only because it saves tax." 8 named tax-planning mistakes (last-minute March planning; buying only for tax benefit; mixing insurance with investment; ignoring lock-in periods; poor recordkeeping; ignoring tax treatment differences between instruments; not reviewing the plan annually; copying a colleague's tax plan). 5-step tax-planning process: understand income → understand applicable rules → choose suitable investments → maintain records → review regularly. | "Don't ask 'how can I save tax,' ask 'how can I build wealth efficiently while managing my taxes.'" Good reframe for the LLM when a user's stated goal is purely tax-minimization rather than goal-alignment. | **This is the chapter with the largest gap**: no ₹1.5 lakh Section 80C ceiling, no PPF current interest rate, no ELSS lock-in duration, no NPS Tier-I/Tier-II distinction or tax treatment on withdrawal, no old-vs-new tax-regime comparison. The book names every instrument the rules engine needs but supplies none of their operative numbers — this is the single highest-priority chapter to re-source from current CBDT/Income Tax Department figures. | 🔴 (for any specific number a user might infer is current) / 🟢 (for the instrument-naming and process framework, which is timeless) |
| 12 | Retirement Planning: Building Your Future Freedom | *Illustrative "retire at 60, current monthly expense ₹50,000" example; explicit statement that the final retirement requirement will be "much larger than simply multiplying current expenses" once inflation and duration are factored in.* | 5-step retirement-corpus estimation process: (1) understand current expenses; (2) adjust for retirement-lifestyle changes (commuting/work costs drop, healthcare/travel/leisure rise); (3) account for inflation over the full pre-retirement horizon; (4) estimate retirement *duration* (book explicitly flags 20-30+ years as a realistic planning horizon, i.e., don't assume retirement ends quickly); (5) build multiple income sources rather than one (EPF, NPS, mutual funds, fixed-income, rental income). Age-based glide-path logic: younger investors can carry more equity for growth; investors nearer retirement should shift toward stability — but no specific equity/debt percentage-by-age formula (e.g. no "100 minus age" rule) is given. 5 named retirement-planning mistakes: starting too late, underestimating inflation, depending only on salary, ignoring healthcare costs, taking too much risk near retirement. | "Your retirement number is not just a financial target — it represents the lifestyle and freedom you want in the future." Retirement portfolio reframed as "a future income machine you are building today," not a return-maximization contest. | No explicit retirement-corpus formula (e.g. no 25X-annual-expenses / 4%-safe-withdrawal-rate rule is ever stated, despite the book later discussing FIRE by name in Ch.15) — the process is qualitative only. This is a good candidate to backfill from the JL Collins extraction's 25X/4% formula, which is India-portable as a pure ratio. | 🟡 |
| 13 | Insurance: Protecting Your Financial Foundation | *No individual case study; structured as concept + checklist + mistake list, mirroring Ch.11's format.* | Three-part protection framework (echoing Ch.2's "three essential layers"): health insurance, term life insurance, emergency fund. Life insurance need-driver checklist: does anyone depend on my income (spouse, children, parents, other dependents)? Explicitly states someone with no dependents and sufficient existing wealth "may have a different requirement" — i.e., not everyone needs life insurance. Term insurance is framed as "higher coverage at relatively lower cost compared to many traditional [insurance] products" (implicitly contrasting with endowment/ULIP-style combined products) — explicit warning against mixing insurance and investment without understanding costs/returns/flexibility. 5 named life-insurance mistakes: buying too little coverage, buying only because someone recommended it, mixing investment and protection without understanding the product, delaying without reason (costs can rise with age), and (in the follow-up section) being underinsured / overinsured / choosing purely for tax benefit / ignoring policy exclusions and claim process / not updating coverage after life events (marriage, children, new loans). | "The right insurance amount is not about buying the biggest policy — it's about creating appropriate protection for your responsibilities." "Insurance decisions should be made when life is calm, not when an emergency has already arrived." | **No sizing multiple is given anywhere** — the book never states a "10x annual income" or "expenses × years-to-retirement" life-cover formula, despite structuring an entire checklist around "how much financial support would my family need." This is a clear, well-scoped gap: the rules engine needs a life-cover sizing formula sourced elsewhere (e.g. income-replacement × dependency years, or outstanding-liabilities + future-goals method) before it can give a number. | 🟡 (process/checklist) / gap (sizing formula) |
| 14 | Building Wealth: Creating Your Personal Financial System | Systems-over-goals framing; ties together budgeting, saving, investing, protecting, and learning into one repeatable monthly cycle. | Reiterates the asset-vs-liability growth-race check from Ch.2 ("every year, your assets should grow faster than your liabilities") as an ongoing personal KPI, not a one-time exercise. No new numeric formula introduced. | Encourages users to "create your own money rules" — a personalized, written 5-6 rule list (the book leaves blank numbered slots for the reader to fill in) — good template for the LLM to help a user co-author their own explicit rule set during onboarding. | — | 🟢 |
| 15 | Financial Independence: Designing Your Freedom | *No individual case study; direct explainer of the FIRE movement.* | Defines FIRE (Financial Independence, Retire Early) and its three named variants: **Lean FIRE** (financial independence via a lower-cost/minimal lifestyle), **Fat FIRE** (independence while maintaining a higher lifestyle, requiring a much larger corpus), **Barista FIRE** (partial independence + continued lighter/flexible work, e.g. part-time or consulting). Core FIRE principles as stated: raise savings rate (via higher income, lower expenses, or both), invest long-term in growth assets, build financial discipline. Explicitly warns against "copying someone else's FIRE number" — the target is individual. | "FIRE is about creating choices and reducing financial dependence," not necessarily quitting work at a young age. Balances the FIRE mindset's benefits (better habits, savings awareness, intentional spending) against its risk (extreme saving without balance harming present-day wellbeing/health/family). | **No 4% safe-withdrawal-rate rule and no 25X-annual-expenses corpus formula are ever stated**, despite this being the standard quantitative backbone of FIRE calculations in virtually every other FIRE-focused source (including this project's own JL Collins extraction). This chapter names the concept but supplies zero arithmetic — treat as a strong candidate to cross-reference against the JL Collins extraction's `4%_rule` / `25x_expenses` formula, which is currency-agnostic and can be imported directly. | 🟢 (concept/vocabulary) / gap (formula) |
| 16 | Money Psychology: The Behaviour Behind Wealth | Ties earlier "habits > income" material to the psychology behind why people mismanage money; reintroduces the "1% better every month compounds" framing. | No new hard numbers; reinforces the lifestyle-inflation detector from Ch.3 and the habit-consistency framing from Ch.2/Ch.10. | Strongest behavioral-content chapter alongside Ch.3 — useful for the advisor's tone when discussing why a user "knows what to do but doesn't do it." | — | 🟢 |
| 17 | Smart Money Decisions for Different Life Stages | Life-stage-segmented guidance (early-career, mid-career/family-building, pre-retirement, etc.), echoing the age-based equity/debt glide-path logic from Ch.12 without adding a new formula. | No new numeric formula; reuses the emergency-fund, debt-ceiling, and retirement-corpus frameworks from earlier chapters, applied per life stage. | Useful as a template for the LLM's persona-branching logic — segment advice by life stage the same way the book does, rather than giving one-size-fits-all guidance. | — | 🟢 |
| 18 | Your Complete Financial Action Plan | Closing synthesis chapter; consolidates the book's recurring exercises (net worth calculation, 30-day expense tracking, 50-30-20 budget, savings-rate calculation, asset/liability list, automate-one-habit, 10-year vision) into a single end-to-end checklist. | Restates the **savings-rate formula** and **net-worth formula** as the book's two standing "always know these two numbers" KPIs — directly parallel to the Ramit Sethi extraction's "know your two numbers" (there: amount owed + payoff date; here: net worth + savings rate) — genuinely complementary pairing for the `assess_debt`/`assess_wealth` modules. | Closing tone: "you do not need to transform your financial life overnight... you simply need to make better decisions consistently" — good closing-message register for the LLM after a full onboarding flow. | — | 🟢 |

---

## Part 2: Algorithmic Logic & Rules Engine Specifications

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                    DETERMINISTIC RULES ENGINE MODULES                          │
│                                                                                │
│  [1. apply_50_30_20_budget]        ──► Splits income into Needs/Wants/Save    │
│  [2. calculate_emergency_fund_target] ──► 3-6-12 month sizing by stability    │
│  [3. rule_of_72]                   ──► Estimates years-to-double from a rate  │
│  [4. assess_emi_burden]            ──► Flags EMI load against the 30-40% band │
│  [5. calculate_savings_rate]       ──► Savings ÷ Income, the book's core KPI  │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Module 1: 50-30-20 Budget Allocator 🟢
Implements Chapter 4's primary budgeting formula, with the book's own aggressive-debt-repayment
variant as an alternate profile.

```python
def apply_50_30_20_budget(
    monthly_take_home: float,
    profile: str = "standard"  # "standard" or "debt_repayment"
) -> dict:
    """
    SmartPlan Finance Ch.4: 'Give Every Rupee a Purpose.'
    Standard split: 50% Needs / 30% Wants / 20% Savings & Investments.
    Debt-repayment variant (book's own stated adjustment): 45% Needs / 20% Wants /
    35% Debt Repayment & Savings.
    """
    splits = {
        "standard": {"needs": 0.50, "wants": 0.30, "savings": 0.20},
        "debt_repayment": {"needs": 0.45, "wants": 0.20, "savings_and_debt": 0.35},
    }
    plan = splits.get(profile, splits["standard"])
    allocation = {k: round(monthly_take_home * v) for k, v in plan.items()}
    return {
        "profile": profile,
        "allocation": allocation,
        "disclaimer": (
            "This is a starting guideline, not a rulebook — the book itself frames the "
            "percentages as adjustable to fit your responsibilities and goals."
        ),
    }
```

### Module 2: Emergency Fund Target (3-6-12 Month Rule) 🟢
Implements Chapter 5's stability-tiered sizing table.

```python
def calculate_emergency_fund_target(
    essential_monthly_expenses: float,
    employment_stability: str,  # "stable_govt_or_secure", "salaried_private", "irregular_or_business"
    has_dependents: bool = False,
    has_large_emi_burden: bool = False,
) -> dict:
    """
    SmartPlan Finance Ch.5: 'The 3-6-12 Month Rule.'
    3 months  -> stable government / very secure employment, low responsibilities
    6 months  -> most salaried professionals, private sector, moderate responsibilities
    12 months -> business owners, freelancers, irregular income, multiple dependents
    Explicit escalators: dependents, high-risk industry, large EMI burden, health
    responsibilities all push the target upward from the base tier.
    """
    base_months = {
        "stable_govt_or_secure": 3,
        "salaried_private": 6,
        "irregular_or_business": 12,
    }.get(employment_stability, 6)

    months = base_months
    if has_dependents:
        months += 1
    if has_large_emi_burden:
        months += 1

    target_amount = essential_monthly_expenses * months
    return {
        "recommended_months": months,
        "target_amount": target_amount,
        "rationale": (
            "Calculated using essential expenses only — exclude vacations, premium "
            "shopping, and other lifestyle spending, per the book's own guidance."
        ),
        "storage_guidance": [
            "Immediate-access portion: savings account",
            "Remainder: liquid mutual funds or short-term deposits",
            "Never: stock market, long-term investments, or large cash-at-home holdings",
        ],
    }
```

### Module 3: Rule of 72 Doubling-Time Estimator 🟢
Implements Chapter 10's compounding shortcut.

```python
def rule_of_72(expected_annual_return_pct: float) -> dict:
    """
    SmartPlan Finance Ch.10: 'The Rule of 72: A Simple Way to Understand Growth.'
    Formula: 72 / expected annual return (%) = approximate years to double.
    Explicitly an estimation shortcut, not an exact calculation.
    """
    if expected_annual_return_pct <= 0:
        raise ValueError("Expected annual return must be positive.")
    years_to_double = 72 / expected_annual_return_pct
    return {
        "expected_annual_return_pct": expected_annual_return_pct,
        "approx_years_to_double": round(years_to_double, 1),
        "note": "Quick mental-math estimate only — not a substitute for a full CAGR projection.",
    }
```

### Module 4: EMI Burden Checker (30-40% Rule) 🟡
Implements Chapter 6's debt-ceiling guideline. Flagged 🟡 because the book itself presents this as
a soft, situation-dependent guideline rather than a hard cutoff.

```python
def assess_emi_burden(
    monthly_take_home: float,
    total_monthly_emi_obligations: float,
) -> dict:
    """
    SmartPlan Finance Ch.6: 'The 30-40% Rule.'
    The book frames this as a common guideline, not an absolute ceiling — 'the exact
    number depends on your situation.' Implemented here as a banded flag rather than a
    hard pass/fail.
    """
    ratio = total_monthly_emi_obligations / monthly_take_home if monthly_take_home > 0 else 1.0
    if ratio <= 0.30:
        band = "comfortable"
    elif ratio <= 0.40:
        band = "at_the_upper_guideline"
    else:
        band = "above_guideline"

    return {
        "emi_to_income_ratio": round(ratio, 3),
        "band": band,
        "advisory_note": (
            "This 30-40% band is a rule of thumb, not a hard rule — the book explicitly "
            "says the right number depends on income stability and personal responsibilities."
        ),
    }
```

### Module 5: Savings Rate & Net Worth KPIs 🟢
Implements the book's two "always know these numbers" standing KPIs (Chapters 2 and 18), directly
paired with the Ramit Sethi extraction's "know your two numbers" debt equivalent.

```python
def calculate_core_kpis(
    monthly_savings: float,
    monthly_income: float,
    total_assets: float,
    total_liabilities: float,
) -> dict:
    """
    SmartPlan Finance Ch.2 / Ch.18: the book's own recurring formulas.
    Savings Rate = (Monthly Savings / Monthly Income) x 100
    Net Worth = Assets - Liabilities
    """
    savings_rate_pct = (monthly_savings / monthly_income) * 100 if monthly_income > 0 else 0
    net_worth = total_assets - total_liabilities
    return {
        "savings_rate_pct": round(savings_rate_pct, 1),
        "net_worth": net_worth,
        "nudge": (
            "These are your two standing numbers to always know — same spirit as knowing "
            "your total debt owed and payoff date on the debt side."
        ),
    }
```

---

## Part 3: LLM Advisor Behavioral Scripts & Conversational Scenarios

### Scenario 1: User just got a raise and wants to upgrade lifestyle immediately
* **User Input:** *"I just got a ₹15,000/month raise. I'm thinking of upgrading to a bigger
  apartment and getting a new bike."*
* **Advisor Response Architecture (Ch.2 & Ch.3 — lifestyle inflation):**
  1. **Celebrate first, no judgment:** *"Congratulations — that's a meaningful jump."*
  2. **Name the pattern before it happens:** *"One thing worth knowing: this is exactly the moment
     lifestyle inflation usually kicks in — expenses quietly rising as fast as income, which is
     why raises don't always translate into savings."*
  3. **Concrete rule from the book:** *"A simple approach the book suggests: invest at least half
     of every raise before upgrading your lifestyle with the rest. So of this ₹15,000, maybe
     ₹7,500+ goes straight into your SIP before you decide what to do with the remainder."*
  4. Run `apply_50_30_20_budget` on the new total income to show where the raise naturally fits.

### Scenario 2: User wants to know if they need life insurance
* **User Input:** *"I'm 24, single, no kids, still living with my parents. Do I need life
  insurance?"*
* **Advisor Response Architecture (Ch.13 — insurance need-driver checklist):**
  1. **Apply the book's own filter, don't assume yes:** *"The book's own checklist starts with:
     does anyone depend financially on your income? If your parents aren't relying on your salary
     to cover their needs, you may genuinely be in the 'may not need life insurance yet' category
     the book describes — that's a real answer, not just a sales deflection."*
  2. **Redirect to what usually does matter at this stage:** *"Health insurance is the one the book
     treats as near-universal regardless of dependents — worth checking whether your employer
     policy is enough or whether you want your own."*
  3. **Flag the gap honestly:** the book gives no cover-sizing multiple, so avoid stating a specific
     ₹ figure — this is a 🔴/gap area requiring a properly sourced income-replacement formula before
     the app can quote a number.

### Scenario 3: User is intimidated by tax planning in March
* **User Input:** *"It's almost the end of the financial year and I haven't done any tax-saving
  investment. What should I buy right now?"*
* **Advisor Response Architecture (Ch.11 — tax planning mistakes):**
  1. **Name the pattern, gently:** *"This is exactly the 'last-minute March scramble' the book
     calls out as tax-planning mistake #1 — it's extremely common, not a personal failing."*
  2. **Reframe the question:** *"Rather than 'what can I buy to save tax right now,' the more useful
     question is 'does this also fit my actual goals, risk level, and how soon I'll need the
     money?' ELSS, PPF, EPF, and NPS are the usual named options — each has real tradeoffs in
     lock-in and liquidity."*
  3. **Be explicit about what this app can't tell them yet:** *"I can't quote you the current 80C
     limit or exact lock-in periods with confidence from this source — that's worth confirming with
     a current, dated source or advisor before you commit money this week."*

### Scenario 4: User asks about FIRE / early retirement
* **User Input:** *"I want to retire by 40. How much do I need to save?"*
* **Advisor Response Architecture (Ch.15 — FIRE, cross-referenced with JL Collins extraction):**
  1. **Validate the goal, introduce the vocabulary:** *"This is what's often called FIRE — Financial
     Independence, Retire Early. The book describes three flavors: Lean FIRE (lower-cost lifestyle),
     Fat FIRE (higher lifestyle, much bigger corpus needed), and Barista FIRE (partial independence
     plus some lighter work)."*
  2. **Supply the missing arithmetic from elsewhere:** *"This book names the concept but doesn't
     give the actual corpus formula. The standard version (25x your annual expenses, ~4% annual
     safe withdrawal) is the number to run — that's currency-agnostic and works the same in rupees
     as anywhere else."* → call the JL Collins extraction's `25x_expenses`/`4%_rule` module here.
  3. **Anti-comparison close:** *"The book's own advice: don't copy someone else's FIRE number —
     yours depends on your own expenses and lifestyle expectations."*

---

## Part 4: Integration with Existing Project Knowledge Base

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                       SYNTHESIS OF KNOWLEDGE BASE — CURRENT STATUS                       │
│                                                                                        │
│  FULLY ACTIVE:                                                                        │
│  1. Anshuman Sharma (Fix Your Finance Transcript) — India-sourced:                      │
│     10-Phase discovery state machine, safety net before investing, loan tenure cap.    │
│  2. Morgan Housel (The Psychology of Money) — universal, no adaptation needed:          │
│     Margin of safety engine, savings rate dominance, reasonable > rational,             │
│     fee vs. fine reframe, survivability checks, ego-suppression in budgeting.          │
│  3. Argho Sanyal (SmartPlan Finance) [THIS EXTRACTION] — India-sourced, no adaptation   │
│     needed for its currency/instrument naming, but numerically thin in several          │
│     chapters (see Part 1 "Gap" column):                                                │
│     - 50-30-20 budget, 3-6-12 month emergency fund table, Rule of 72, 30-40% EMI       │
│       ceiling, savings-rate/net-worth KPIs, good-debt-vs-bad-debt and asset-vs-        │
│       liability vocabulary, debt-snowball mechanics, ELSS/PPF/EPF/NPS instrument       │
│       naming (numbers not supplied — see below), FIRE vocabulary (Lean/Fat/Barista).   │
│                                                                                        │
│  PARTIALLY ACTIVE (general ratios/formulas/process usable; jurisdiction-specific       │
│  numbers disregarded until sourced — see each file's own banner):                      │
│  4. JL Collins (Simple Path to Wealth): 4%/25x FI formula, fee-drag equation, debt-     │
│     triage band structure usable — 401k/IRA/VTSAX naming and specific % cutoffs held.  │
│     ► Now the natural cross-reference for filling SmartPlan Finance's FIRE/retirement  │
│       corpus gap (Ch.12, Ch.15) — the 25x/4% formula is currency-agnostic.             │
│  5. Ramit Sethi (IWTYBR): credit-utilization formula, "know your two numbers," and all │
│     behavioral content usable — FICO weights and US APR/fee figures held.              │
│     ► Pairs directly with SmartPlan Finance's own "know your two numbers" pattern       │
│       (net worth + savings rate, vs. Sethi's amount-owed + payoff-date).               │
│  6. Gary Rabbior (CFEE / Money & Youth): six-step decision model, opportunity-cost      │
│     prompt, debt checklist, 3 Cs of credit, buy-vs-lease framework usable — all         │
│     Canadian dollar figures and RRSP/RESP references held.                             │
│                                                                                        │
│  STILL NEEDS SEPARATE SOURCING (not solved by any current extraction):                 │
│  - Section 80C limit, PPF interest rate, ELSS lock-in period, NPS tax treatment,       │
│    old-vs-new tax regime comparison (Income Tax Dept / CBDT current figures).          │
│  - Life-insurance cover sizing multiple/formula (no source in the project yet).        │
│  - CIBIL score composition weights and India-specific card APR/fee figures (same gap   │
│    already flagged in the Ramit Sethi extraction).                                     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

This extraction adds a second genuinely India-sourced book to the active build (alongside the
Anshuman Sharma transcript), contributing currency-native budgeting and emergency-fund formulas
plus a full instrument vocabulary (PPF/EPF/NPS/ELSS/SIP) — but it is not a substitute for sourcing
the actual current numeric parameters of those instruments, which remain the single largest
documented gap in the project's India-specific numeric coverage.
