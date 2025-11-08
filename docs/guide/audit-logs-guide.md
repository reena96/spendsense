# Audit Logs - Complete Guide

## Overview

Audit logs in SpendSense provide a comprehensive, immutable trail of all significant system events for compliance, debugging, and regulatory requirements. They track user actions, system decisions, operator interventions, and security events.

## Purpose

### Compliance & Regulatory
- **7-year retention**: Meet financial industry requirements (2 years active + 5 years archived)
- **Consent tracking**: Prove GDPR/CCPA compliance with consent opt-in/opt-out history
- **Decision traceability**: Show why recommendations were made or blocked
- **Operator accountability**: Track who approved, overrode, or flagged content

### Security & Monitoring
- **Login attempts**: Detect brute force attacks or unauthorized access
- **Permission violations**: Track unauthorized endpoint access attempts
- **Operator actions**: Monitor admin overrides and manual interventions

### Debugging & Analytics
- **System behavior**: Understand recommendation generation patterns
- **Guardrail effectiveness**: Analyze eligibility and tone validation pass/fail rates
- **User journey**: Trace complete timeline of events for specific users

## Architecture

### Database Schema

```sql
CREATE TABLE comprehensive_audit_log (
    log_id TEXT PRIMARY KEY,           -- Unique identifier: log_{uuid}
    event_type TEXT NOT NULL,          -- Type of event (see Event Types below)
    user_id TEXT,                      -- User involved (nullable for operator-only events)
    operator_id TEXT,                  -- Operator who triggered event (nullable for system events)
    recommendation_id TEXT,            -- Related recommendation (nullable)
    timestamp DATETIME NOT NULL,       -- When event occurred (UTC)
    event_data TEXT NOT NULL,          -- JSON string with full event context
    ip_address TEXT,                   -- Source IP address
    user_agent TEXT,                   -- Browser/client user agent
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (operator_id) REFERENCES operators (operator_id)
);

-- Performance indexes for common queries
CREATE INDEX idx_audit_timestamp ON comprehensive_audit_log (timestamp);
CREATE INDEX idx_audit_event_type ON comprehensive_audit_log (event_type);
CREATE INDEX idx_audit_user ON comprehensive_audit_log (user_id);
CREATE INDEX idx_audit_operator ON comprehensive_audit_log (operator_id);
```

### Event Types

| Event Type | Description | User ID | Operator ID | Recommendation ID |
|------------|-------------|---------|-------------|-------------------|
| `recommendation_generated` | System created a recommendation | ✓ | — | ✓ |
| `consent_changed` | User opt-in/opt-out status changed | ✓ | Optional | — |
| `eligibility_checked` | Guardrail validation performed | ✓ | — | ✓ |
| `tone_validated` | Tone guardrail validation performed | ✓ | — | ✓ |
| `operator_action` | Operator approved/overrode/flagged | ✓ | ✓ | ✓ |
| `persona_assigned` | Persona assigned to user | ✓ | — | — |
| `persona_overridden` | Operator manually changed persona | ✓ | ✓ | — |
| `login_attempt` | Operator login (success/failure) | — | ✓ | — |
| `unauthorized_access` | Permission denied on endpoint | — | ✓ | — |

## How Audit Logs Are Created

### 1. Recommendation Generation Flow

When the system generates a recommendation:

```python
from spendsense.config.database import get_db_session
from spendsense.ingestion.database_writer import AuditLog
import json
import uuid
from datetime import datetime

def create_recommendation_audit(user_id: str, recommendation_id: str,
                               content_data: dict, guardrail_results: dict):
    """Log recommendation generation event."""
    session = get_db_session()

    try:
        log = AuditLog(
            log_id=f'log_{uuid.uuid4().hex}',
            event_type='recommendation_generated',
            user_id=user_id,
            operator_id=None,  # System-generated
            recommendation_id=recommendation_id,
            timestamp=datetime.utcnow(),
            event_data=json.dumps({
                'content_type': content_data['content_type'],
                'title': content_data['title'],
                'passed_guardrails': guardrail_results['passed'],
                'guardrail_results': guardrail_results
            }),
            ip_address=None,  # System event
            user_agent='SpendSense/Recommendation-Engine'
        )

        session.add(log)
        session.commit()
    finally:
        session.close()
```

### 2. Operator Action Flow

When an operator approves/overrides a recommendation:

```python
def create_operator_action_audit(user_id: str, operator_id: str,
                                recommendation_id: str, action: str,
                                reason: str, request):
    """Log operator action event."""
    session = get_db_session()

    try:
        log = AuditLog(
            log_id=f'log_{uuid.uuid4().hex}',
            event_type='operator_action',
            user_id=user_id,
            operator_id=operator_id,
            recommendation_id=recommendation_id,
            timestamp=datetime.utcnow(),
            event_data=json.dumps({
                'action': action,  # 'approved', 'overridden', 'flagged'
                'reason': reason,
                'original_status': 'pending',
                'new_status': action
            }),
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )

        session.add(log)
        session.commit()
    finally:
        session.close()
```

### 3. Consent Change Flow

When a user changes consent status:

```python
def create_consent_change_audit(user_id: str, old_status: str,
                               new_status: str, changed_via: str):
    """Log consent status change."""
    session = get_db_session()

    try:
        log = AuditLog(
            log_id=f'log_{uuid.uuid4().hex}',
            event_type='consent_changed',
            user_id=user_id,
            operator_id=None,  # User-initiated (unless operator override)
            recommendation_id=None,
            timestamp=datetime.utcnow(),
            event_data=json.dumps({
                'old_status': old_status,
                'new_status': new_status,
                'consent_version': '1.0',
                'changed_via': changed_via  # 'web', 'api', 'operator_action'
            }),
            ip_address=None,
            user_agent=None
        )

        session.add(log)
        session.commit()
    finally:
        session.close()
```

### 4. Login Attempt Flow

When an operator attempts to log in:

```python
def create_login_audit(operator_id: str, username: str, success: bool,
                      failure_reason: str, request):
    """Log operator login attempt."""
    session = get_db_session()

    try:
        log = AuditLog(
            log_id=f'log_{uuid.uuid4().hex}',
            event_type='login_attempt',
            user_id=None,
            operator_id=operator_id if success else None,
            recommendation_id=None,
            timestamp=datetime.utcnow(),
            event_data=json.dumps({
                'status': 'success' if success else 'failure',
                'username': username,
                'failure_reason': failure_reason
            }),
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent')
        )

        session.add(log)
        session.commit()
    finally:
        session.close()
```

## Integration Points

### Where Audit Logs Should Be Created

1. **Recommendation Engine** (`spendsense/recommendations/assembler.py`)
   - After generating recommendation
   - After guardrail checks (eligibility, tone)

2. **Authentication System** (`spendsense/api/operator_auth.py`)
   - Login attempts (success/failure)
   - Token refresh
   - Logout events

3. **RBAC Middleware** (`spendsense/auth/rbac.py`)
   - Unauthorized access attempts
   - Permission denials

4. **Review Queue API** (`spendsense/api/operator_review.py`)
   - Operator approvals
   - Operator overrides
   - Manual flags

5. **Persona Management** (`spendsense/api/operator_personas.py`)
   - Persona assignments
   - Manual persona overrides

6. **Consent Management** (Future: Story 6.6)
   - Consent opt-in/opt-out changes
   - Consent version updates

## Querying Audit Logs

### API Endpoints

#### Get Audit Log (Paginated)
```bash
GET /api/operator/audit/log?event_type=operator_action&user_id=user_MASKED_000&page=1&page_size=50
Authorization: Bearer {token}
```

**Response:**
```json
{
  "entries": [
    {
      "log_id": "log_abc123",
      "event_type": "operator_action",
      "user_id": "user_MASKED_000",
      "operator_id": "op_admin_default",
      "recommendation_id": "rec_xyz789",
      "timestamp": "2025-11-06T10:30:00Z",
      "event_data": {
        "action": "approved",
        "reason": "Content meets all guidelines"
      },
      "ip_address": "127.0.0.1",
      "user_agent": "Mozilla/5.0"
    }
  ],
  "total_count": 150,
  "page": 1,
  "page_size": 50
}
```

#### Export Audit Log
```bash
GET /api/operator/audit/export?format=csv&start_date=2025-10-01&end_date=2025-11-01
Authorization: Bearer {token}
```

Returns CSV or JSON file download.

#### Get Compliance Metrics
```bash
GET /api/operator/audit/metrics?start_date=2025-10-01&end_date=2025-11-01
Authorization: Bearer {token}
```

**Response:**
```json
{
  "consent_metrics": {
    "total_users": 100,
    "opted_in_count": 75,
    "opted_out_count": 25,
    "opt_in_rate_pct": 75.0
  },
  "eligibility_metrics": {
    "total_checks": 500,
    "passed": 450,
    "failed": 50,
    "pass_rate_pct": 90.0,
    "failure_reasons": [
      {"reason": "consent_opted_out", "count": 30},
      {"reason": "no_persona_match", "count": 20}
    ]
  },
  "tone_metrics": {
    "total_validations": 500,
    "passed": 475,
    "failed": 25,
    "pass_rate_pct": 95.0,
    "violations_by_category": [
      {"category": "urgency_detected", "count": 15},
      {"category": "fear_language", "count": 10}
    ]
  },
  "operator_metrics": {
    "total_actions": 100,
    "approvals": 80,
    "overrides": 15,
    "flags": 5,
    "actions_by_operator": [
      {"operator_id": "op_admin_default", "count": 50},
      {"operator_id": "op_reviewer_001", "count": 50}
    ]
  },
  "date_range": {
    "start_date": "2025-10-01T00:00:00Z",
    "end_date": "2025-11-01T23:59:59Z"
  }
}
```

### Direct SQL Queries

```sql
-- Find all operator actions for a user
SELECT * FROM comprehensive_audit_log
WHERE user_id = 'user_MASKED_000'
  AND event_type = 'operator_action'
ORDER BY timestamp DESC;

-- Count events by type in last 30 days
SELECT event_type, COUNT(*) as count
FROM comprehensive_audit_log
WHERE timestamp >= datetime('now', '-30 days')
GROUP BY event_type
ORDER BY count DESC;

-- Find failed guardrail checks
SELECT user_id, timestamp, event_data
FROM comprehensive_audit_log
WHERE event_type IN ('eligibility_checked', 'tone_validated')
  AND json_extract(event_data, '$.check_result') = 'failed'
ORDER BY timestamp DESC;

-- Track consent opt-out patterns
SELECT user_id, timestamp,
       json_extract(event_data, '$.old_status') as old_status,
       json_extract(event_data, '$.new_status') as new_status
FROM comprehensive_audit_log
WHERE event_type = 'consent_changed'
  AND json_extract(event_data, '$.new_status') = 'opted_out'
ORDER BY timestamp DESC;
```

## UI Features

### Audit Log Page (`/audit`)

**Features:**
- **Filters**: Event type, user ID, operator ID, date range
- **Pagination**: 50 entries per page (configurable)
- **Detail View**: Click any entry to see full event_data JSON
- **Export**: Download filtered results as CSV or JSON
- **Real-time**: Auto-refreshes when new logs are available

**Access Control:**
- Requires `admin` or `compliance` role
- Viewer role cannot access audit logs

### Compliance Metrics Page (`/metrics`)

**Features:**
- **Consent Metrics**: Opt-in rate, total opted-in/out users
- **Eligibility Metrics**: Pass rate, failure reasons breakdown
- **Tone Metrics**: Pass rate, violation categories
- **Operator Metrics**: Action counts by operator
- **Date Range**: Default 30 days, customizable
- **Visual Charts**: Bar charts and pie charts for metrics

**Access Control:**
- Requires `admin` or `compliance` role

## Best Practices

### 1. Always Log Complete Context

```python
# GOOD: Complete event data
event_data = json.dumps({
    'action': 'approved',
    'reason': reason,
    'original_status': original_status,
    'new_status': new_status,
    'recommendation_id': rec_id,
    'content_type': content_type
})

# BAD: Minimal data
event_data = json.dumps({'action': 'approved'})
```

### 2. Use Consistent Timestamps (UTC)

```python
# GOOD: UTC timestamp
timestamp = datetime.utcnow()

# BAD: Local timezone
timestamp = datetime.now()  # Ambiguous during DST transitions
```

### 3. Capture IP and User Agent for Security Events

```python
# GOOD: Full context for login attempts
ip_address = request.client.host
user_agent = request.headers.get('user-agent')

# BAD: Missing security context
ip_address = None
user_agent = None
```

### 4. Log Before and After Critical Operations

```python
# GOOD: Log failures too
try:
    result = approve_recommendation(rec_id)
    create_audit('operator_action', status='success')
except Exception as e:
    create_audit('operator_action', status='failed', error=str(e))
    raise

# BAD: Only log success
result = approve_recommendation(rec_id)
create_audit('operator_action')
```

### 5. Use Structured event_data (JSON)

```python
# GOOD: Structured, queryable
event_data = json.dumps({
    'check_result': 'failed',
    'failure_reason': 'consent_opted_out',
    'consent_status': 'opted_out'
})

# BAD: Unstructured string
event_data = "Check failed because user opted out"
```

## Retention & Archival

### Active Storage (2 years)
- Stored in `comprehensive_audit_log` table
- Full query and export access
- Indexed for fast retrieval

### Cold Storage (5+ years)
- Export to compressed JSON/CSV files
- Store in long-term archive (S3, Azure Blob, etc.)
- Accessible on-demand for regulatory requests

### Archival Script (Future)

```bash
# Archive logs older than 2 years
python scripts/archive_audit_logs.py --older-than 730 --output s3://bucket/audit-archive/
```

## Troubleshooting

### Issue: Audit logs not appearing

**Check:**
1. Is the function calling the audit creation code?
2. Are there any database errors in backend logs?
3. Is the session being committed?
4. Check `SELECT COUNT(*) FROM comprehensive_audit_log;`

### Issue: Compliance metrics showing zero

**Check:**
1. Are there audit log entries for the date range?
2. Is the `ComplianceMetricsCalculator` implemented?
3. Check backend logs for calculation errors
4. Verify event_data JSON format matches expected schema

### Issue: Export timing out

**Solution:**
- Reduce date range
- Add pagination to export endpoint
- Use streaming response for large exports

## Testing

### Generate Test Data

```bash
# Generate 50 logs over 7 days
python scripts/generate_audit_logs.py --count 50 --days 7

# Generate 200 logs over 30 days
python scripts/generate_audit_logs.py --count 200 --days 30

# Clear and regenerate
python scripts/generate_audit_logs.py --clear --count 100 --days 14
```

### Verify Audit Trail

```python
# Test audit log creation
def test_recommendation_audit():
    create_recommendation_audit(
        user_id='test_user',
        recommendation_id='test_rec',
        content_data={'content_type': 'education', 'title': 'Test'},
        guardrail_results={'passed': True}
    )

    session = get_db_session()
    log = session.query(AuditLog).filter_by(
        event_type='recommendation_generated',
        user_id='test_user'
    ).first()

    assert log is not None
    assert log.recommendation_id == 'test_rec'
    session.close()
```

## Summary

Audit logs provide:
- ✅ Complete system transparency
- ✅ Regulatory compliance (GDPR, CCPA, SOX)
- ✅ Security monitoring and incident response
- ✅ Debugging and analytics capabilities
- ✅ Operator accountability
- ✅ User consent tracking

Every significant event should create an audit log entry with complete context for future analysis and compliance reporting.
