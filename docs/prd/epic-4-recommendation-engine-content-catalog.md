# Epic 4: Recommendation Engine & Content Catalog

**Goal:** Build recommendation generation system that produces 3-5 educational items and 1-3 partner offers per user based on persona and behavioral signals. Every recommendation must include transparent rationale citing specific data. Implement structured content catalog with metadata for educational resources and partner offers.

## Story 4.1: Educational Content Catalog

As a **product manager**,
I want **structured catalog of educational content items with metadata linking them to personas and signals**,
so that **relevant education can be programmatically matched to user needs**.

### Acceptance Criteria

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

## Story 4.2: Partner Offer Catalog

As a **product manager**,
I want **structured catalog of partner offers with eligibility rules and persona targeting**,
so that **relevant financial products can be recommended only to eligible users**.

### Acceptance Criteria

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

## Story 4.3: Recommendation Matching Logic

As a **developer**,
I want **matching algorithm that selects relevant content and offers based on persona and signals**,
so that **users receive personalized recommendations aligned with their financial situation**.

### Acceptance Criteria

1. Matching function accepts user persona and behavioral signals as input
2. Function filters content catalog for items matching user's persona
3. Function ranks content items by relevance to detected signals
4. Function selects top 3-5 educational items with diversity (different types)
5. Function filters partner offers by persona and eligibility checks
6. Function selects 1-3 partner offers matching user eligibility
7. Duplicate recommendations prevented within time window
8. Matching logic traced in audit log
9. Unit tests verify correct filtering and ranking

## Story 4.4: Rationale Generation Engine

As a **developer**,
I want **generation of transparent rationales citing specific behavioral data for every recommendation**,
so that **users understand exactly why they received each recommendation**.

### Acceptance Criteria

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

## Story 4.5: Recommendation Assembly & Output

As a **developer**,
I want **assembly of complete recommendation set with education, offers, and rationales per user per time window**,
so that **recommendations can be delivered via API and UI with full transparency**.

### Acceptance Criteria

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
