# Requirements

## Functional Requirements

**FR1:** System shall generate synthetic Plaid-style data for 50-100 users with diverse financial situations (various income levels, credit behaviors, saving patterns)

**FR2:** System shall ingest financial data from CSV/JSON formats without requiring live Plaid connection

**FR3:** System shall validate all input data against schema constraints (non-negative balances, chronological transaction order, valid currency codes)

**FR4:** System shall store validated data in both SQLite (relational) and Parquet (analytics) formats

**FR5:** System shall detect subscription patterns by identifying recurring merchants (≥3 occurrences in 90 days with consistent monthly/weekly cadence)

**FR6:** System shall calculate monthly recurring spend total and subscription share of total spend

**FR7:** System shall compute savings signals including net inflow to savings-type accounts, growth rate, and emergency fund coverage

**FR8:** System shall detect credit utilization patterns with flags for ≥30%, ≥50%, and ≥80% thresholds

**FR9:** System shall identify minimum-payment-only behavior, interest charges, and overdue status for credit accounts

**FR10:** System shall detect income stability through payroll ACH transactions, payment frequency, variability, and cash-flow buffer calculations

**FR11:** System shall compute all behavioral signals over both 30-day (short-term) and 180-day (long-term) time windows

**FR12:** System shall assign each user to exactly one persona from a maximum of 6 personas based on deterministic prioritization logic

**FR13:** System shall support Persona 1 (High Utilization) with criteria: card utilization ≥50% OR interest charges >0 OR minimum-payment-only OR overdue status

**FR14:** System shall support Persona 2 (Variable Income Budgeter) with criteria: median pay gap >45 days AND cash-flow buffer <1 month

**FR15:** System shall support Persona 3 (Subscription-Heavy) with criteria: recurring merchants ≥3 AND (monthly recurring spend ≥$50 OR subscription share ≥10%)

**FR16:** System shall support Persona 4 (Savings Builder) with criteria: savings growth rate ≥2% OR net inflow ≥$200/month, AND all card utilizations <30%

**FR17:** System shall support two custom personas (Persona 5: Cash Flow Optimizer, Persona 6: Young Professional) with documented criteria, rationale, and educational focus

**FR18:** System shall record all qualifying personas in audit logs while assigning only the highest-priority persona for recommendations

**FR19:** System shall generate 3-5 education items per user per time window mapped to persona and detected signals

**FR20:** System shall generate 1-3 partner offers per user per time window with eligibility checks

**FR21:** System shall include a concrete "because" rationale for every recommendation citing specific data signals

**FR22:** System shall use plain-language explanations with grade-8 readability for all recommendations

**FR23:** System shall require explicit user opt-in before processing any financial data

**FR24:** System shall allow users to revoke consent at any time and halt all future processing

**FR25:** System shall track consent status and timestamps per user in a separate consent audit log

**FR26:** System shall enforce eligibility checks preventing recommendations for products the user doesn't qualify for or already has

**FR27:** System shall exclude harmful or predatory financial products from all recommendations

**FR28:** System shall validate all recommendation text for neutral, empowering, educational tone with no shaming language

**FR29:** System shall include disclaimer "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance" on every recommendation

**FR30:** System shall provide operator view showing detected signals and computed metrics for any user

**FR31:** System shall display both short-term (30-day) and long-term (180-day) persona assignments in operator view

**FR32:** System shall allow operators to approve, override, or flag recommendations

**FR33:** System shall provide complete decision trace showing why each recommendation was made

**FR34:** System shall provide REST API endpoints for user creation, consent management, profile retrieval, recommendations, feedback, and operator review

**FR35:** System shall generate evaluation metrics including coverage, explainability, latency, auditability, and fairness

**FR36:** System shall output evaluation results as JSON/CSV metrics file, summary report, and per-user decision traces

**FR37:** System shall complete recommendation generation for any user in under 5 seconds

## Non-Functional Requirements

**NFR1:** System shall use only anonymized synthetic data with fake names and masked account numbers

**NFR2:** System shall encrypt local data storage using AES-256 encryption

**NFR3:** System shall maintain audit trail for every data access and modification

**NFR4:** System shall achieve 100% coverage (users with assigned persona and ≥3 detected behaviors)

**NFR5:** System shall achieve 100% explainability (recommendations with rationales)

**NFR6:** System shall achieve 100% auditability (recommendations with decision traces)

**NFR7:** System shall support deterministic behavior using fixed seeds for reproducibility

**NFR8:** System shall be testable with ≥10 unit/integration tests

**NFR9:** System shall support one-command setup via requirements.txt or package.json

**NFR10:** System shall run locally without external dependencies

**NFR11:** System shall be cloud-portable to support future scalability

**NFR12:** System shall use modular architecture supporting extension of persona registry

**NFR13:** System shall document all code with clear decision log explaining key choices and limitations

**NFR14:** System shall validate realistic statistical distributions in synthetic data (spend frequency, seasonal variation, pay cycles)

**NFR15:** System shall standardize time-window aggregation logic across all feature detection modules

---
