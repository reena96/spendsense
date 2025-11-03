# Technical Assumptions

## Repository Structure

**Monorepo** - Single repository containing all modules for simplified development and deployment

## Service Architecture

**Modular Monolith** - Clear module separation with potential for future microservices extraction:
- `ingest/` - Data loading and validation
- `features/` - Signal detection and feature engineering
- `personas/` - Persona assignment logic
- `recommend/` - Recommendation engine
- `guardrails/` - Consent, eligibility, tone checks
- `ui/` - Operator view and user experience
- `eval/` - Evaluation harness
- `docs/` - Decision log and schema documentation

## Testing Requirements

**Full Testing Pyramid** - Minimum 10 unit/integration tests covering:
- Data validation and ingestion
- Behavioral signal detection accuracy
- Persona assignment logic
- Recommendation generation and rationales
- Consent and eligibility guardrails
- Evaluation metrics calculation

Use deterministic seeds for reproducibility in all tests.

## Additional Technical Assumptions and Requests

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
