# SpendSense Product Requirements Document (PRD)

**Version:** 3.1
**Owner:** Reena Mary Puthota
**Technical Contact:** bharris@peak6.com
**Last Updated:** November 3, 2025

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-11-03 | 3.1 | Expanded persona system from 5 to 6 personas (added Persona 6: Young Professional) | Reena Mary Puthota |
| 2025-11-03 | 3.0 | Initial BMad-structured PRD from original specs | Reena Mary Puthota |

---

## Goals and Background Context

### Goals

- Build an explainable, consent-aware AI system that transforms Plaid-style transaction data into actionable financial insights
- Detect behavioral patterns from financial transactions and assign users to educational personas
- Deliver personalized financial education with clear guardrails around eligibility and tone
- Demonstrate a fully auditable, modular, and fair personalization framework
- Empower users to understand and improve their financial behavior without providing regulated financial advice
- Create a system that prioritizes transparency, user control, education, and fairness

### Background Context

Banks generate massive transaction data through Plaid integrations but struggle to turn it into actionable customer insights without crossing into regulated financial advice. The challenge is to build a system that respects user consent, provides transparent explanations for every recommendation, and maintains strict ethical boundaries. This project aims to demonstrate that financial technology can be both powerful and trustworthy, putting user education and empowerment ahead of product sales.

This is an individual or small-team project with no strict deadline, focused on building a production-quality demonstration of responsible AI in financial services.

---

## Requirements

### Functional Requirements

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

### Non-Functional Requirements

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

## User Interface Design Goals

### Overall UX Vision

Create a transparent, educational interface that empowers users to understand their financial behavior while maintaining strict ethical boundaries. The experience should feel supportive and informative, never judgmental or sales-focused. Users should clearly see the data signals driving every recommendation and have full control over their consent and data processing.

### Key Interaction Paradigms

- **Consent-first flow**: No data processing occurs without explicit user permission with clear revocation options
- **Transparent rationale display**: Every recommendation shows the specific behavioral signals that triggered it
- **Time-window comparison**: Users can toggle between 30-day and 180-day views to understand short-term vs. long-term patterns
- **Education-focused content**: All recommendations emphasize learning and improvement, not product sales
- **Operator oversight**: Human review capabilities for quality assurance and ethical compliance

### Core Screens and Views

1. **Consent & Onboarding Screen**: Clear explanation of data usage with explicit opt-in
2. **User Dashboard**: Personalized view showing assigned persona, detected behavioral signals, and recommendations
3. **Behavioral Signals View**: Detailed breakdown of subscriptions, savings, credit, and income patterns
4. **Recommendations Feed**: 3-5 education items and 1-3 partner offers with rationales
5. **Operator Review Interface**: Administrative view for oversight, approval/override, and decision traces
6. **Evaluation Dashboard**: Metrics and fairness analysis for system performance

### Accessibility

WCAG AA compliance - system should be accessible to users with diverse abilities

### Branding

Clean, trustworthy financial services aesthetic with emphasis on transparency and education. Use calming colors (blues, greens) to convey stability and support. Avoid aggressive sales imagery or language.

### Target Device and Platforms

Web Responsive (primary), with consideration for future mobile app deployment

---

## Technical Assumptions

### Repository Structure

**Monorepo** - Single repository containing all modules for simplified development and deployment

### Service Architecture

**Modular Monolith** - Clear module separation with potential for future microservices extraction:
- `ingest/` - Data loading and validation
- `features/` - Signal detection and feature engineering
- `personas/` - Persona assignment logic
- `recommend/` - Recommendation engine
- `guardrails/` - Consent, eligibility, tone checks
- `ui/` - Operator view and user experience
- `eval/` - Evaluation harness
- `docs/` - Decision log and schema documentation

### Testing Requirements

**Full Testing Pyramid** - Minimum 10 unit/integration tests covering:
- Data validation and ingestion
- Behavioral signal detection accuracy
- Persona assignment logic
- Recommendation generation and rationales
- Consent and eligibility guardrails
- Evaluation metrics calculation

Use deterministic seeds for reproducibility in all tests.

### Additional Technical Assumptions and Requests

- **Primary Language**: Python (recommended for data processing and ML-ready future extensions) or JavaScript/TypeScript
- **Database**: SQLite for relational data, Parquet for analytics workloads
- **Storage Format**: JSON for configs and logs
- **API Framework**: REST API using Flask/FastAPI (Python) or Express (Node.js)
- **Data Generation**: Faker or similar library for realistic synthetic data
- **Local-first Design**: All processing runs on local machine without cloud dependencies
- **Cloud-portable Architecture**: Design supports future AWS/GCP deployment
- **Optional AI Integration**: LLMs may be used for educational content generation with documented prompts
- **Configuration Management**: YAML/JSON config files for persona definitions and recommendation catalog
- **Logging**: Structured logging for all decisions, signal detections, and recommendation generation

---

## Epic List

**Epic 1: Data Foundation & Synthetic Data Generation**
Establish project infrastructure, create synthetic Plaid-style data generator, and build data ingestion/validation pipeline

**Epic 2: Behavioral Signal Detection Pipeline**
Implement feature engineering modules to detect subscription, savings, credit, and income patterns across time windows

**Epic 3: Persona Assignment System**
Build persona classification logic with deterministic prioritization and comprehensive audit logging

**Epic 4: Recommendation Engine & Content Catalog**
Create recommendation generation system with educational content, partner offers, and transparent rationales

**Epic 5: Consent, Eligibility & Tone Guardrails**
Implement ethical constraints including consent management, eligibility filtering, and tone validation

**Epic 6: Operator View & Oversight Interface**
Build administrative interface for human oversight, decision review, and recommendation approval/override

**Epic 7: Evaluation Harness & Metrics**
Create comprehensive evaluation system measuring coverage, explainability, latency, auditability, and fairness

---

## Epic 1: Data Foundation & Synthetic Data Generation

**Goal:** Establish foundational project infrastructure with version control, dependency management, and testing framework. Build a synthetic data generator producing realistic Plaid-style financial data for 50-100 users with diverse behavioral patterns. Implement data ingestion and validation pipeline ensuring schema compliance and data quality.

### Story 1.1: Project Setup & Infrastructure

As a **developer**,
I want **project scaffolding with repository structure, dependency management, and basic CI/CD configuration**,
so that **the team has a solid foundation for collaborative development with automated testing**.

#### Acceptance Criteria

1. Repository initialized with `.gitignore` for Python/Node.js
2. README.md created with project overview and setup instructions
3. Directory structure created matching technical architecture (`ingest/`, `features/`, `personas/`, `recommend/`, `guardrails/`, `ui/`, `eval/`, `docs/`)
4. Dependency file created (`requirements.txt` or `package.json`) with core libraries
5. One-command setup script created and documented in README
6. Basic test framework configured (pytest/jest) with example test
7. Configuration file system established using YAML/JSON
8. Logging framework configured with structured output
9. All setup executes successfully on clean environment

### Story 1.2: Synthetic Data Schema Definition

As a **data engineer**,
I want **comprehensive data schemas matching Plaid's structure for accounts, transactions, and liabilities**,
so that **synthetic data generation and validation can enforce realistic constraints**.

#### Acceptance Criteria

1. Account schema defined with fields: account_id, type/subtype, balances (available/current/limit), iso_currency_code, holder_category
2. Transaction schema defined with fields: account_id, date, amount, merchant_name/entity_id, payment_channel, personal_finance_category, pending status
3. Liability schema defined for credit cards: APRs, minimum_payment_amount, last_payment_amount, is_overdue, next_payment_due_date, last_statement_balance
4. Liability schema defined for mortgages/student loans: interest_rate, next_payment_due_date
5. Schema validation rules documented: non-negative balances, chronological order, valid currency codes
6. Schema documentation created in `docs/schemas.md` with examples
7. Schema validation functions implemented and tested
8. Example valid and invalid data created for testing

### Story 1.3: Synthetic User Profile Generator

As a **data engineer**,
I want **generation of 50-100 diverse synthetic user profiles with realistic financial characteristics**,
so that **the system can be tested across varied financial behaviors and demographics**.

#### Acceptance Criteria

1. User profile generator creates 50-100 unique users with fake names and masked IDs
2. Profiles include diverse income levels (e.g., $20K-$200K annual range)
3. Profiles include varied credit behaviors (low/medium/high utilization, overdue/current)
4. Profiles include different saving patterns (active savers, minimal savers, no savings)
5. Profiles include varied debt levels (no debt, moderate debt, high debt)
6. Generation uses fixed seed for reproducibility
7. Profile distribution validated for realistic statistical spread
8. Generated profiles stored in JSON format
9. Profile generator documented with usage examples

### Story 1.4: Synthetic Transaction Data Generator

As a **data engineer**,
I want **realistic transaction data generation for each user profile matching their financial characteristics**,
so that **behavioral signals can be accurately detected from transaction patterns**.

#### Acceptance Criteria

1. Transaction generator creates realistic monthly spending patterns per user profile
2. Recurring transactions generated for subscriptions (Netflix, gym, utilities) with consistent cadence
3. Income transactions generated with realistic pay cycles (biweekly, monthly, variable)
4. Credit card payments, savings transfers, and bill payments generated
5. Merchant names and categories assigned realistically per transaction type
6. Transaction amounts vary seasonally and by merchant category
7. Date distribution respects user pay cycles and spending patterns
8. Generated data spans 180+ days for long-term pattern detection
9. Transaction data validates against schema successfully

### Story 1.5: Synthetic Liability Data Generator

As a **data engineer**,
I want **realistic liability data generation including credit cards and loans matching user profiles**,
so that **credit utilization and debt signals can be accurately calculated**.

#### Acceptance Criteria

1. Credit card data generated with realistic limits ($500-$25,000 range)
2. Credit card balances set based on user profile utilization targets
3. APR rates assigned realistically (15%-30% range)
4. Minimum payment amounts calculated correctly (typically 2-3% of balance)
5. Overdue status and payment history generated based on profile
6. Student loan and mortgage data generated for applicable profiles
7. Interest rates match realistic market conditions
8. All liability data validates against schema
9. Liability data consistent with transaction history

### Story 1.6: Data Ingestion & Validation Pipeline

As a **developer**,
I want **data ingestion pipeline that loads CSV/JSON files and validates against schemas**,
so that **the system can safely process financial data with guaranteed quality**.

#### Acceptance Criteria

1. CSV reader implemented supporting account, transaction, and liability files
2. JSON reader implemented supporting same data structures
3. Schema validation applied to all loaded data
4. Invalid records logged with specific validation error messages
5. Valid records stored in SQLite database with appropriate schema
6. Valid records also stored in Parquet format for analytics
7. Ingestion process handles missing optional fields gracefully
8. Ingestion logs summary statistics (records processed/valid/invalid)
9. Ingestion can be run via command-line script with file paths as arguments
10. Unit tests cover validation edge cases and error handling

---

## Epic 2: Behavioral Signal Detection Pipeline

**Goal:** Implement comprehensive feature engineering modules that analyze user financial data to detect subscription patterns, savings behaviors, credit utilization, and income stability. All signals computed over both 30-day and 180-day time windows with standardized aggregation logic and complete audit logging.

### Story 2.1: Time Window Aggregation Framework

As a **data scientist**,
I want **standardized time window calculation framework supporting 30-day and 180-day analysis periods**,
so that **all behavioral signals can be computed consistently across different time horizons**.

#### Acceptance Criteria

1. Time window utility function created accepting reference date and window size (30/180 days)
2. Function returns filtered dataset for specified window
3. Function handles edge cases (insufficient historical data)
4. Window calculations use consistent date arithmetic across all modules
5. Default fallback values defined for users with insufficient data
6. Window framework documented with usage examples
7. Unit tests verify correct date filtering and edge case handling

### Story 2.2: Subscription Pattern Detection

As a **data scientist**,
I want **detection of recurring subscription patterns from transaction data**,
so that **subscription-heavy users can be identified and receive relevant education**.

#### Acceptance Criteria

1. Recurring merchant detection identifies merchants with ≥3 transactions in 90 days
2. Cadence analysis determines if transactions are monthly or weekly recurring
3. Monthly recurring spend total calculated for each time window
4. Subscription share calculated as percentage of total spend
5. Results computed for both 30-day and 180-day windows
6. Detected subscriptions logged with merchant name, frequency, and amount
7. Edge cases handled: irregular timing, amount variations, cancelled subscriptions
8. Subscription metrics stored per user per time window
9. Unit tests verify detection accuracy with synthetic recurring patterns

### Story 2.3: Savings Behavior Detection

As a **data scientist**,
I want **detection of savings patterns including account growth and emergency fund coverage**,
so that **savings builders can be identified and encouraged to optimize their strategy**.

#### Acceptance Criteria

1. Net inflow calculated for savings-type accounts (savings, money market, HSA)
2. Savings growth rate calculated as percentage change over time window
3. Emergency fund coverage calculated as savings balance ÷ average monthly expenses
4. Monthly expense average computed from spending transactions
5. Results computed for both 30-day and 180-day windows
6. Savings metrics handle accounts with zero balance gracefully
7. All derived metrics logged for explainability and traceability
8. Savings metrics stored per user per time window
9. Unit tests verify calculations with various saving patterns

### Story 2.4: Credit Utilization & Debt Signal Detection

As a **data scientist**,
I want **detection of credit card utilization levels and debt stress indicators**,
so that **high-utilization users can receive debt paydown education and resources**.

#### Acceptance Criteria

1. Credit utilization calculated as balance ÷ limit for each credit card
2. Utilization flags set for ≥30%, ≥50%, ≥80% thresholds
3. Minimum-payment-only behavior detected from payment history
4. Interest charges presence identified from liability data
5. Overdue status flagged from is_overdue field
6. Aggregate utilization calculated across all cards
7. Results computed for both 30-day and 180-day windows
8. All credit signals logged with specific card identifiers
9. Credit metrics stored per user per time window
10. Unit tests verify detection across various credit scenarios

### Story 2.5: Income Stability Detection

As a **data scientist**,
I want **detection of income patterns including pay frequency and cash-flow buffer**,
so that **variable income users can receive budgeting strategies appropriate for their situation**.

#### Acceptance Criteria

1. Payroll ACH transactions detected from transaction category and amount patterns
2. Payment frequency calculated from time gaps between payroll transactions
3. Median pay gap calculated to identify regular vs. irregular income
4. Cash-flow buffer calculated in months of expenses coverage
5. Income variability metric calculated from payment amount standard deviation
6. Results computed for both 30-day and 180-day windows
7. Edge cases handled: first job, job changes, missing income data
8. All income metrics logged with detected payroll dates
9. Income metrics stored per user per time window
10. Unit tests verify detection with biweekly, monthly, and irregular patterns

### Story 2.6: Behavioral Summary Aggregation

As a **data scientist**,
I want **aggregated behavioral summaries per user combining all detected signals**,
so that **persona classification has complete feature set available for decision logic**.

#### Acceptance Criteria

1. User behavioral summary created combining subscription, savings, credit, and income signals
2. Summary includes all metrics computed for both time windows
3. Summary includes metadata: calculation timestamp, data completeness flags
4. Missing data indicators added where signals could not be computed
5. Summary stored in structured format (JSON) for recommendation engine access
6. Summary accessible via API endpoint GET /profile/{user_id}
7. Fallback defaults applied consistently for incomplete data
8. Summary generation logged for audit trail
9. Unit tests verify summary completeness and data structure

---

## Epic 3: Persona Assignment System

**Goal:** Build persona classification logic that assigns each user to exactly one of 5 personas based on their behavioral signals. Implement deterministic prioritization when multiple personas match, maintain comprehensive audit logging of all qualifying personas, and ensure persona assignments are explainable and traceable.

### Story 3.1: Persona Definition Registry

As a **product manager**,
I want **structured persona definitions with clear criteria, focus areas, and prioritization rules**,
so that **persona assignment logic is maintainable, extensible, and auditable**.

#### Acceptance Criteria

1. Persona registry created as YAML/JSON configuration file
2. Each persona defined with: ID, name, description, priority rank, match criteria
3. Persona 1 (High Utilization) defined with priority 1 and criteria documented
4. Persona 2 (Variable Income Budgeter) defined with priority 2 and criteria documented
5. Persona 3 (Subscription-Heavy) defined with priority 3 and criteria documented
6. Persona 4 (Savings Builder) defined with priority 4 and criteria documented
7. Persona 5 (custom) defined with priority 5, criteria, and rationale documented
8. Each persona includes educational focus areas and recommended content types
9. Registry schema validated and documented
10. Registry loaded at application startup

### Story 3.2: Persona Matching Engine

As a **data scientist**,
I want **evaluation of user behavioral signals against all persona criteria**,
so that **all qualifying personas can be identified before prioritization is applied**.

#### Acceptance Criteria

1. Matching function evaluates user signals against each persona's criteria
2. Boolean match result returned for each persona with supporting evidence
3. Match logic correctly implements AND/OR conditions per persona criteria
4. Threshold comparisons handle edge cases (exact matches, missing data)
5. All qualifying personas logged before prioritization
6. Match evaluation traced with specific signal values that triggered match
7. Matching supports both 30-day and 180-day time windows
8. Unit tests cover all persona criteria combinations
9. Unit tests verify correct boolean logic for complex criteria

### Story 3.3: Deterministic Prioritization Logic

As a **product manager**,
I want **deterministic selection of highest-priority persona when multiple personas match**,
so that **users receive consistent, predictable persona assignments focused on their most critical need**.

#### Acceptance Criteria

1. Prioritization function accepts list of matching personas
2. Function returns single highest-priority persona (lowest priority number)
3. Tie-breaking logic documented if personas have same priority
4. Priority selection traced in audit log
5. All qualifying personas recorded separately from selected persona
6. Selection logic handles edge case of zero qualifying personas
7. Fallback persona or "unclassified" status defined for no-match scenario
8. Unit tests verify prioritization with various match combinations
9. Deterministic behavior verified across multiple runs with same data

### Story 3.4: Persona Assignment & Audit Logging

As a **developer**,
I want **persona assignment results stored with complete audit trail of decision logic**,
so that **every persona assignment is explainable and can be reviewed for quality assurance**.

#### Acceptance Criteria

1. Assigned persona stored per user per time window (30-day and 180-day)
2. Assignment record includes: persona ID, assignment timestamp, confidence level
3. All qualifying personas logged with match evidence
4. Audit log includes specific signal values that triggered each match
5. Audit log includes reason why highest-priority persona was selected
6. Assignment accessible via API GET /profile/{user_id}
7. Audit logs stored in structured format (JSON) in database
8. Operator can view full decision trace in UI
9. Unit tests verify complete audit trail generation

### Story 3.5: Custom Personas 5 & 6 Implementation

As a **product manager**,
I want **definition and implementation of two custom personas addressing underserved user segments**,
so that **the system covers diverse user needs from early-career to optimization opportunities**.

#### Acceptance Criteria

1. Persona 5 (Cash Flow Optimizer) name, description, and educational focus documented
2. Persona 5 criteria defined: high liquidity (≥6 months expenses), minimal debt usage (<10% utilization)
3. Persona 6 (Young Professional) name, description, and educational focus documented
4. Persona 6 criteria defined: limited transaction history (<180 days), low credit limits (<$3000)
5. Clear behavioral criteria defined using measurable signals for both personas
6. Rationale documented explaining why each persona matters
7. Priority ranks assigned (Persona 5: rank 5, Persona 6: rank 6 - lowest priority)
8. Match criteria implemented in persona matching engine for both personas
9. Educational content recommendations defined for both personas
10. Both persona definitions added to persona registry
11. Documentation explains persona value and target user characteristics for each
12. Unit tests verify Persona 5 and Persona 6 matching criteria work correctly

---

## Epic 4: Recommendation Engine & Content Catalog

**Goal:** Build recommendation generation system that produces 3-5 educational items and 1-3 partner offers per user based on persona and behavioral signals. Every recommendation must include transparent rationale citing specific data. Implement structured content catalog with metadata for educational resources and partner offers.

### Story 4.1: Educational Content Catalog

As a **product manager**,
I want **structured catalog of educational content items with metadata linking them to personas and signals**,
so that **relevant education can be programmatically matched to user needs**.

#### Acceptance Criteria

1. Content catalog created as YAML/JSON configuration file
2. Each content item includes: ID, title, type (article/template/calculator/video), description
3. Each item tagged with relevant personas (can apply to multiple personas)
4. Each item tagged with triggering signals (subscription, savings, credit, income patterns)
5. Content items defined for all persona educational focus areas
6. At least 15 unique educational items covering all 5 personas
7. Content includes: debt paydown strategies, budget templates, subscription audit checklists, emergency fund calculators, credit utilization explainers
8. Each item includes plain-language summary (grade-8 readability)
9. Catalog schema validated and documented
10. Catalog loaded at application startup

### Story 4.2: Partner Offer Catalog

As a **product manager**,
I want **structured catalog of partner offers with eligibility rules and persona targeting**,
so that **relevant financial products can be recommended only to eligible users**.

#### Acceptance Criteria

1. Partner offer catalog created as YAML/JSON configuration file
2. Each offer includes: ID, title, type (savings account/credit card/app/tool), description
3. Each offer includes eligibility criteria (minimum income, credit requirements, account exclusions)
4. Each offer tagged with relevant personas
5. Partner offers defined covering all personas: balance transfer cards, high-yield savings, budgeting apps, subscription management tools
6. At least 10 unique partner offers covering all 5 personas
7. Harmful/predatory products explicitly excluded from catalog
8. Each offer includes plain-language summary
9. Catalog schema validated and documented
10. Catalog loaded at application startup

### Story 4.3: Recommendation Matching Logic

As a **developer**,
I want **matching algorithm that selects relevant content and offers based on persona and signals**,
so that **users receive personalized recommendations aligned with their financial situation**.

#### Acceptance Criteria

1. Matching function accepts user persona and behavioral signals as input
2. Function filters content catalog for items matching user's persona
3. Function ranks content items by relevance to detected signals
4. Function selects top 3-5 educational items with diversity (different types)
5. Function filters partner offers by persona and eligibility checks
6. Function selects 1-3 partner offers matching user eligibility
7. Duplicate recommendations prevented within time window
8. Matching logic traced in audit log
9. Unit tests verify correct filtering and ranking

### Story 4.4: Rationale Generation Engine

As a **developer**,
I want **generation of transparent rationales citing specific behavioral data for every recommendation**,
so that **users understand exactly why they received each recommendation**.

#### Acceptance Criteria

1. Rationale template system created with placeholders for signal values
2. Each content item includes rationale template in catalog
3. Each partner offer includes rationale template in catalog
4. Rationale generator replaces placeholders with user's actual signal values
5. Generated rationales cite specific data: account numbers (masked), amounts, percentages, dates
6. Rationales use plain language (grade-8 readability)
7. Example format: "We noticed your Visa ending in 4523 is at 68% utilization ($3,400 of $5,000 limit). Bringing this below 30% could improve your credit score and reduce interest charges of $87/month."
8. All recommendations include "because" statement with concrete data citation
9. Rationale generation logged for audit trail
10. Unit tests verify correct placeholder replacement and data citation

### Story 4.5: Recommendation Assembly & Output

As a **developer**,
I want **assembly of complete recommendation set with education, offers, and rationales per user per time window**,
so that **recommendations can be delivered via API and UI with full transparency**.

#### Acceptance Criteria

1. Recommendation assembler combines education items and partner offers
2. Each recommendation includes: content/offer details, rationale, persona match reason, signal citations
3. Recommendations generated for both 30-day and 180-day windows
4. Recommendation set includes mandatory disclaimer: "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."
5. Assembled recommendations stored in database with timestamp
6. Recommendations accessible via API GET /recommendations/{user_id}
7. API response includes full recommendation details and metadata
8. Recommendation generation completes in <5 seconds per user
9. Unit tests verify complete recommendation structure and required fields

---

## Epic 5: Consent, Eligibility & Tone Guardrails

**Goal:** Implement ethical constraints ensuring user control, recommendation appropriateness, and supportive communication. Build consent management system, eligibility filtering, and tone validation to maintain trust and compliance.

### Story 5.1: Consent Management System

As a **compliance officer**,
I want **explicit consent tracking with opt-in/opt-out capabilities and audit logging**,
so that **user data is only processed with permission and consent changes are traceable**.

#### Acceptance Criteria

1. Consent database table created with fields: user_id, consent_status (opted_in/opted_out), timestamp, consent_version
2. Consent opt-in flow implemented requiring explicit user action (no pre-checked boxes)
3. Consent opt-out/revoke functionality implemented allowing anytime withdrawal
4. Consent status checked before any data processing or recommendation generation
5. Processing halted immediately upon consent revocation
6. Consent changes logged in audit trail with timestamp and user ID
7. Consent audit log accessible to operators
8. API endpoint POST /consent implemented for recording consent changes
9. API endpoint GET /consent/{user_id} implemented for checking consent status
10. Unit tests verify processing blocked without consent

### Story 5.2: Eligibility Filtering System

As a **compliance officer**,
I want **eligibility checks preventing inappropriate product recommendations**,
so that **users only see offers they qualify for and don't already have**.

#### Acceptance Criteria

1. Eligibility checker evaluates minimum income requirements against user profile
2. Eligibility checker evaluates credit requirements against user credit signals
3. Eligibility checker prevents duplicate recommendations (filters existing accounts)
4. Eligibility checker blocks harmful/predatory products (payday loans, etc.)
5. Eligibility rules loaded from partner offer catalog metadata
6. Failed eligibility checks logged with specific reason
7. Only eligible recommendations passed to final output
8. Eligibility check results included in recommendation audit trail
9. Unit tests verify filtering across various eligibility scenarios
10. Unit tests confirm harmful products never recommended

### Story 5.3: Tone Validation & Language Safety

As a **UX writer**,
I want **automated validation ensuring all recommendation text uses supportive, non-judgmental language**,
so that **users feel empowered and educated, never shamed or blamed**.

#### Acceptance Criteria

1. Tone validation rules defined prohibiting shaming phrases ("overspending", "bad with money", "irresponsible")
2. Tone validator checks all recommendation rationales against prohibited phrases
3. Validator ensures neutral, empowering language (e.g., "opportunity to optimize" vs. "you're doing it wrong")
4. Readability checker validates grade-8 reading level for all text
5. Tone validation runs before recommendations are stored/delivered
6. Failed validations logged with specific flagged phrases
7. Manual review queue created for flagged recommendations
8. Tone validation results included in audit trail
9. Unit tests verify detection of problematic language
10. Unit tests confirm acceptable language passes validation

### Story 5.4: Mandatory Disclaimer System

As a **compliance officer**,
I want **automatic inclusion of "not financial advice" disclaimer on all recommendations**,
so that **regulatory boundaries are clear and users understand the educational nature of content**.

#### Acceptance Criteria

1. Standard disclaimer text defined: "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."
2. Disclaimer automatically appended to every recommendation set
3. Disclaimer included in all API responses containing recommendations
4. Disclaimer rendered prominently in UI (not hidden in fine print)
5. Disclaimer text configurable for future regulatory updates
6. Disclaimer presence verified in recommendation validation checks
7. Unit tests confirm all recommendation outputs include disclaimer
8. Integration tests verify disclaimer appears in UI

### Story 5.5: Guardrails Integration & Testing

As a **developer**,
I want **integrated guardrail pipeline enforcing all ethical constraints before recommendation delivery**,
so that **every recommendation passes consent, eligibility, tone, and disclaimer checks**.

#### Acceptance Criteria

1. Guardrail pipeline created executing checks in sequence: consent → eligibility → tone → disclaimer
2. Pipeline halts at first failure and logs specific violation
3. Only fully validated recommendations proceed to storage/delivery
4. Pipeline execution traced in audit log with pass/fail status per check
5. Failed recommendations flagged for manual operator review
6. Guardrail metrics tracked: total checks, pass rate, failure reasons
7. Pipeline integrated into recommendation generation workflow
8. Integration tests verify end-to-end guardrail enforcement
9. Performance tested to ensure <5 second total recommendation generation
10. Documentation created explaining each guardrail check and rationale

---

## Epic 6: Operator View & Oversight Interface

**Goal:** Build administrative interface providing human oversight of recommendation system. Enable operators to view behavioral signals, review recommendations with decision traces, approve or override suggestions, and monitor consent/eligibility compliance.

### Story 6.1: Operator Authentication & Authorization

As a **system administrator**,
I want **secure operator authentication with role-based access control**,
so that **only authorized personnel can access sensitive user data and override decisions**.

#### Acceptance Criteria

1. Operator login system implemented with username/password authentication
2. Role-based permissions defined: viewer (read-only), reviewer (approve/flag), admin (override)
3. Session management implemented with secure tokens
4. Access control enforced on all operator endpoints
5. Unauthorized access attempts logged and blocked
6. Operator actions logged with operator ID and timestamp
7. Password security requirements enforced (minimum length, complexity)
8. Login failures limited to prevent brute force attacks
9. Unit tests verify access control enforcement
10. Security review completed for authentication implementation

### Story 6.2: User Signal Dashboard

As an **operator**,
I want **comprehensive view of detected behavioral signals for any user**,
so that **I can verify signal detection accuracy and understand persona assignment rationale**.

#### Acceptance Criteria

1. User search interface allows lookup by user ID or masked account number
2. Signal dashboard displays subscription metrics: recurring merchants, monthly spend, subscription share
3. Signal dashboard displays savings metrics: net inflow, growth rate, emergency fund coverage
4. Signal dashboard displays credit metrics: utilization by card, minimum payment behavior, overdue status
5. Signal dashboard displays income metrics: pay frequency, median gap, cash-flow buffer
6. Dashboard shows signals for both 30-day and 180-day windows side-by-side
7. Time window toggle allows switching between short-term and long-term views
8. Raw signal values displayed alongside computed metrics
9. Signal calculation timestamps shown
10. Export functionality allows downloading signal data as CSV

### Story 6.3: Persona Assignment Review Interface

As an **operator**,
I want **view of persona assignments with complete decision trace**,
so that **I can audit persona classification accuracy and understand prioritization logic**.

#### Acceptance Criteria

1. Persona assignment displayed prominently for selected user
2. Both 30-day and 180-day persona assignments shown
3. All qualifying personas listed with match evidence (specific signal values that triggered match)
4. Prioritization logic explanation shown (why highest-priority persona was selected)
5. Persona definition displayed: criteria, educational focus, priority rank
6. Assignment confidence level displayed if applicable
7. Assignment timestamp and data version shown
8. Persona change history displayed if persona shifted between time windows
9. Manual persona override capability for admin role
10. Override actions logged with operator ID and justification required

### Story 6.4: Recommendation Review & Approval Queue

As an **operator**,
I want **review queue of generated recommendations with approve/override/flag capabilities**,
so that **I can ensure recommendation quality and appropriateness before user delivery**.

#### Acceptance Criteria

1. Review queue displays pending recommendations requiring operator approval
2. Each recommendation shown with full details: content/offer, rationale, persona match, signal citations
3. Guardrail check results displayed: consent status, eligibility pass/fail, tone validation
4. Decision trace displayed showing why recommendation was generated
5. Operator can approve recommendation (marks as ready for delivery)
6. Operator can override recommendation (blocks delivery and requires justification)
7. Operator can flag recommendation for further review (adds to watch list)
8. Approval/override actions logged in audit trail
9. Filters available: persona type, recommendation type, guardrail failures
10. Batch approval capability for high-confidence recommendations

### Story 6.5: Audit Trail & Compliance Reporting

As a **compliance officer**,
I want **comprehensive audit trail of all system decisions and operator actions**,
so that **the system can demonstrate compliance with ethical guidelines and regulatory requirements**.

#### Acceptance Criteria

1. Audit log displays all recommendation decisions with full trace
2. Audit log displays all consent changes with timestamps
3. Audit log displays all eligibility check results
4. Audit log displays all tone validation results
5. Audit log displays all operator actions (approvals, overrides, flags)
6. Search and filter capabilities: date range, user ID, operator ID, action type
7. Export functionality allows downloading audit logs as CSV/JSON
8. Compliance metrics displayed: consent opt-in rate, eligibility failure reasons, tone validation issues
9. Data retention policy documented for audit logs
10. Audit log access restricted to admin and compliance roles

---

## Epic 7: Evaluation Harness & Metrics

**Goal:** Create comprehensive evaluation system measuring recommendation quality, system performance, and ethical compliance. Generate reproducible metrics reports with fairness analysis and per-user decision traces for transparency and continuous improvement.

### Story 7.1: Coverage Metrics Calculation

As a **data scientist**,
I want **calculation of user coverage metrics showing persona assignment and behavioral signal detection rates**,
so that **system completeness and data quality can be quantified**.

#### Acceptance Criteria

1. Coverage metric calculated: % of users with assigned persona (target 100%)
2. Coverage metric calculated: % of users with ≥3 detected behavioral signals (target 100%)
3. Coverage by persona calculated: distribution of users across 5 personas
4. Coverage by time window calculated: 30-day vs. 180-day completion rates
5. Missing data analysis performed: users with insufficient history
6. Coverage metrics computed for both synthetic test dataset and any real data
7. Metrics stored in JSON format with timestamp
8. Coverage trends tracked over time if multiple evaluation runs
9. Unit tests verify calculation accuracy
10. Failure case reporting: list of users missing signals or personas with reasons

### Story 7.2: Explainability Metrics Calculation

As a **data scientist**,
I want **measurement of recommendation explainability ensuring all outputs have transparent rationales**,
so that **system transparency can be verified and rationale quality can be assessed**.

#### Acceptance Criteria

1. Explainability metric calculated: % of recommendations with rationales (target 100%)
2. Rationale quality check: presence of concrete data citations in each rationale
3. Rationale completeness check: signal values, account identifiers, numeric specifics included
4. Explainability by persona calculated: rationale presence across all persona types
5. Decision trace completeness verified: all recommendations have full audit trail
6. Explainability failures logged: recommendations missing or incomplete rationales
7. Sample rationales extracted for manual quality review
8. Metrics stored in JSON format with examples
9. Unit tests verify calculation and quality checks
10. Improvement recommendations generated for low-quality rationales

### Story 7.3: Performance & Latency Metrics

As a **developer**,
I want **measurement of system performance including recommendation generation latency**,
so that **user experience quality and scalability limits can be assessed**.

#### Acceptance Criteria

1. Latency metric measured: time to generate recommendations per user (target <5 seconds)
2. Latency breakdown by component: signal detection, persona assignment, recommendation matching, guardrail checks
3. Performance metrics: throughput (users processed per minute)
4. Resource utilization tracked: memory, CPU during batch processing
5. Performance tested with full 50-100 user synthetic dataset
6. Latency percentiles calculated: p50, p95, p99
7. Performance bottlenecks identified if latency exceeds target
8. Metrics compared across multiple runs to verify consistency
9. Performance report generated with visualization of latency distribution
10. Scalability projections documented: estimated performance at 1K, 10K, 100K users

### Story 7.4: Auditability & Compliance Metrics

As a **compliance officer**,
I want **verification that all recommendations are fully auditable with complete decision traces**,
so that **regulatory compliance and ethical transparency can be demonstrated**.

#### Acceptance Criteria

1. Auditability metric calculated: % of recommendations with decision traces (target 100%)
2. Consent compliance verified: 0% processing without consent
3. Eligibility compliance measured: % of recommendations passing eligibility checks
4. Tone compliance measured: % of recommendations passing tone validation
5. Disclaimer presence verified: 100% of recommendations include mandatory disclaimer
6. Audit log completeness verified: all user actions and system decisions logged
7. Compliance failures categorized: consent violations, eligibility issues, tone problems
8. Compliance report generated with pass/fail status per guardrail
9. Recommendation age tracked: time from generation to delivery
10. Data retention compliance verified: audit logs persisted per policy

### Story 7.5: Fairness & Bias Analysis

As a **data scientist**,
I want **analysis of recommendation fairness across demographic groups if applicable**,
so that **potential bias in persona assignment or recommendations can be detected and mitigated**.

#### Acceptance Criteria

1. Demographic parity calculated if synthetic data includes demographic attributes
2. Persona distribution analyzed by demographic group
3. Recommendation distribution analyzed by demographic group
4. Statistical significance tested for observed differences
5. Potential bias indicators flagged if disparities exceed threshold
6. Fairness metrics computed: demographic parity ratio, equal opportunity difference
7. Bias analysis documented with interpretation of results
8. Limitations documented: fairness analysis constraints with synthetic data
9. Fairness report generated with visualizations
10. Mitigation recommendations provided if bias detected

### Story 7.6: Evaluation Report Generation & Output

As a **product manager**,
I want **automated generation of comprehensive evaluation report with all metrics and analysis**,
so that **system quality can be assessed and communicated to stakeholders**.

#### Acceptance Criteria

1. Evaluation script executes all metric calculations in sequence
2. JSON metrics file generated with structured results
3. CSV summary file generated for spreadsheet analysis
4. Per-user decision traces exported showing full recommendation logic
5. 1-2 page summary report generated (Markdown/PDF) with key findings
6. Report includes: coverage, explainability, latency, auditability, fairness metrics
7. Report includes: success criteria status (target met/not met per metric)
8. Report includes: failure case analysis and improvement recommendations
9. Report includes: assumptions and limitations documentation
10. Evaluation reproducible with fixed seed for synthetic data generation
11. Evaluation runs via single command with results in `docs/eval/` directory

---

## Checklist Results Report

*(This section will be populated after running the PM Checklist to verify PRD completeness)*

---

## Next Steps

### UX Expert Prompt

> "I need a comprehensive UX specification for SpendSense. The attached PRD defines the product requirements. Please create a detailed front-end specification covering user flows, wireframes, component design, and accessibility requirements. Focus on transparent rationale display, consent-first interactions, and educational tone."

### Architect Prompt

> "I need a comprehensive technical architecture for SpendSense. The attached PRD defines the product requirements. Please create a detailed architecture document covering system design, module structure, data models, API specifications, and technology stack recommendations. Ensure the design supports local-first development with cloud portability."

---
