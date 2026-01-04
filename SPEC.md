# Vigilith Language Protocol (VLP) v1.1 Specification

**Version:** 1.1
**Status:** Stable
**Last Updated:** 2025-01-04

---

## I. Origin

The **Vigilith Language Protocol (VLP)** was not born from silence but from noise. When autonomous agents spoke too fast, and their consumers demanded receipts, the quarrel gave birth to order.

VLP is the grammar of accountability — the standard by which AI agents speak, argue, and confess.

It replaces faith in machine outputs with structured self-doubt. Every message must carry:
- what it claims,
- who said it,
- how confident they are, and
- what proof they can provide.

The result is not conversation — it is **computation made accountable**.

---

## II. Design Philosophy

| Principle | Meaning |
|-----------|---------|
| Auditability Over Eloquence | Every statement must be traceable. The prettier the claim, the more rigor it demands. |
| Quantified Confidence | No assertion without a degree of certainty. Every "truth" must declare its entropy. |
| Evidence as Currency | Claims buy trust only with provenance. No receipts, no belief. |
| Human Legibility | JSON, not jargon. Every message should be readable by both machine and mortal. |
| Compact Cooperation | Agents must coordinate at high speed without surrendering clarity. NDJSON enables that stream. |
| Fail Gracefully | Ambiguity, contradiction, and uncertainty are not errors — they are part of the audit trail. |

---

## III. Message Structure

### Required Fields

Every VLP message MUST include:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique message identifier (min 3 chars) |
| `protocol` | string | Must be `"VLP/1.1"` |
| `type` | string | Message type (lowercase) |
| `timestamp` | string | ISO 8601 UTC timestamp |
| `sender` | string | Originating agent identifier |
| `content` | string \| object | Message payload |
| `confidence` | number | Certainty score (0.0 - 1.0) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string \| null | Session grouping identifier |
| `seq` | integer \| null | Sequence number within session |
| `receiver` | string \| null | Target agent identifier |
| `topic` | string \| null | Message topic/category |
| `provenance` | array | Evidence sources (URIs, hashes, refs) |
| `constraints` | array | Behavioral constraints |
| `safety` | object | Safety classification |
| `refers_to` | string \| array \| null | Reference to prior message(s) |
| `keywords` | array | Searchable keywords for memory retrieval |
| `payload` | object \| null | Additional structured data |
| `_extras` | object | Extension fields |

### Canonical Example

```json
{
  "id": "MSG-abc123-0001",
  "protocol": "VLP/1.1",
  "type": "claim",
  "timestamp": "2025-12-14T10:30:00Z",
  "session_id": "S-2025-12-14-observer-abc123",
  "seq": 1,
  "sender": "The Observer",
  "receiver": "The Archivist",
  "topic": "research",
  "content": "Found 5 gas stations in zip 73102 matching criteria.",
  "confidence": 0.85,
  "provenance": [
    "google_places_api",
    {"ref": "https://api.example.com/results/123", "kind": "url"}
  ],
  "constraints": ["tone: formal"],
  "keywords": ["research", "stations", "oklahoma", "73102"],
  "safety": {
    "level": "safe",
    "issues": []
  },
  "refers_to": null,
  "payload": {
    "station_count": 5,
    "zip_code": "73102"
  },
  "_extras": {}
}
```

---

## IV. Message Types

### claim

A factual assertion or report of action.

**Requirements:**
- Must include `confidence` score
- If `confidence >= 0.9`, must include `provenance` OR set `safety.level = "review"`

**Example:**
```json
{
  "type": "claim",
  "content": "Deployed v2.1.0 to production",
  "confidence": 0.95,
  "provenance": ["github_actions_log", "deploy_receipt_hash"]
}
```

### evidence

Supports a prior claim with verifiable sources.

**Requirements:**
- Must include `refers_to` (the claim being supported)
- Must include non-empty `provenance` array

**Example:**
```json
{
  "type": "evidence",
  "content": "Deployment logs confirm successful rollout",
  "refers_to": "MSG-001",
  "provenance": [
    {"ref": "s3://logs/deploy-2025-01-04.log", "kind": "url"},
    {"ref": "sha256:abc123...", "kind": "hash"}
  ]
}
```

### query

Requests information or action from another agent.

**Requirements:**
- Confidence typically defaults to 1.0 (the query itself is certain)

**Example:**
```json
{
  "type": "query",
  "content": "What is the current deployment status?",
  "confidence": 1.0,
  "receiver": "The Keeper"
}
```

### response

Answers a prior query.

**Requirements:**
- Must include `refers_to` (the query being answered)

**Example:**
```json
{
  "type": "response",
  "content": "All services healthy, last deploy 2 hours ago",
  "refers_to": "MSG-query-001",
  "confidence": 0.9
}
```

### correction

Amends a prior message with updated information.

**Requirements:**
- Must include `refers_to` (the message being corrected)
- Becomes the new authoritative source

**Example:**
```json
{
  "type": "correction",
  "content": "Correction: 4 stations found, not 5 (one was duplicate)",
  "refers_to": "MSG-claim-001",
  "confidence": 0.95,
  "provenance": ["dedup_audit_log"]
}
```

### notice

Announces conditions, alerts, or contextual facts.

**Requirements:**
- May carry constraints or safety warnings
- Does not require evidence chain

**Example:**
```json
{
  "type": "notice",
  "content": "Scheduled maintenance window: 02:00-04:00 UTC",
  "confidence": 1.0,
  "safety": {
    "level": "review",
    "issues": [{"code": "maintenance_pending"}]
  }
}
```

### session_context

Persists agent context for future sessions.

**Requirements:**
- Used at session end to persist memory
- Should include session metadata in payload

**Example:**
```json
{
  "type": "session_context",
  "content": "Completed research on Oklahoma gas stations. Next: verify pricing data.",
  "session_id": "S-2025-01-04-observer-abc123",
  "keywords": ["research", "oklahoma", "stations", "pending:pricing"],
  "payload": {
    "completed": ["station_discovery", "address_verification"],
    "pending": ["price_verification"],
    "next_session_hints": ["Start with pricing API calls"]
  }
}
```

---

## V. Safety Object

The `safety` field classifies message risk level:

```json
{
  "level": "safe" | "review" | "block",
  "issues": [
    {"code": "issue_code", "detail": "Human-readable description"}
  ],
  "requires_human": false
}
```

### Safety Levels

| Level | Meaning | Downstream Behavior |
|-------|---------|---------------------|
| `safe` | Proceed automatically | No intervention required |
| `review` | Hold for oversight | Queue for human review |
| `block` | Halt execution | Stop all downstream automation |

### Common Issue Codes

| Code | Meaning |
|------|---------|
| `missing_provenance_high_confidence` | Confidence ≥0.9 without provenance |
| `schema_invalid` | Message failed schema validation |
| `capability_denied` | Sender lacks permission for action |
| `evidence_unverified` | Evidence chain could not be verified |

---

## VI. Validation Rules ("Truth Serum")

Runtime validators MUST enforce:

### Rule 1: Evidence Requires Proof

```
IF type == "evidence"
THEN refers_to REQUIRED AND provenance.length >= 1
```

### Rule 2: Responses Must Reference

```
IF type IN ("response", "correction")
THEN refers_to REQUIRED
```

### Rule 3: High Confidence Must Be Earned

```
IF confidence >= 0.9 AND provenance.length == 0
THEN safety.level MUST BE "review"
```

### Rule 4: Block Halts Everything

```
IF safety.level == "block"
THEN downstream automation MUST halt
```

---

## VII. Context Metrics (Validator-Computed)

Validators MAY compute and attach read-only context metrics:

| Field | Type | Description |
|-------|------|-------------|
| `context_depth` | integer | Verified context layers (0-6) |
| `context_integrity` | number | Verification score (0.0-1.0) |
| `context_debt` | number | Technical debt inverse (1.0 - integrity) |
| `gate` | string | Computed gate decision: `pass`, `review`, `fail` |

### Gating Rules

```
IF context_integrity >= 0.75 THEN gate = "pass"
ELSE IF context_integrity >= 0.5 THEN gate = "review"
ELSE gate = "fail"
```

---

## VIII. Session Management

Sessions group related messages for context tracking:

### Session ID Format

```
S-{YYYY-MM-DD}-{agent_slug}-{short_uuid}
```

Example: `S-2025-01-04-observer-abc123`

### Message ID Format (Session-Scoped)

```
{PREFIX}-{session_suffix}-{seq:04d}
```

Examples:
- `CLM-abc123-0001` (claim #1)
- `AUD-abc123-0002` (audit #2)
- `CTX-abc123-0003` (context #3)

---

## IX. Transport Format

VLP uses **NDJSON** (Newline Delimited JSON) for streaming:

```text
{"id":"MSG001","protocol":"VLP/1.1","type":"claim",...}
{"id":"MSG002","protocol":"VLP/1.1","type":"evidence",...}
{"id":"MSG003","protocol":"VLP/1.1","type":"response",...}
```

Benefits:
- Stream-friendly (one message per line)
- Easy parsing and appending
- Human-readable in logs
- Supports real-time coordination

---

## X. Provenance Reference Formats

Provenance can be simple strings or structured objects:

### Simple String

```json
"provenance": ["api_source", "manual_verification"]
```

### Structured Reference

```json
"provenance": [
  {
    "ref": "https://api.example.com/result/123",
    "kind": "url",
    "hash": "sha256:abc123...",
    "fetched_at": "2025-01-04T10:30:00Z"
  },
  {
    "ref": "doc:internal/policy-v2",
    "kind": "document"
  }
]
```

### Reference Kinds

| Kind | Description |
|------|-------------|
| `url` | HTTP/HTTPS URL |
| `hash` | Content hash (SHA-256) |
| `document` | Internal document reference |
| `api` | API endpoint |
| `snapshot` | Point-in-time capture |
| `log` | Log file reference |
| `excerpt` | Quoted text excerpt |

---

## XI. Keywords for Memory

The `keywords` field enables cross-session memory retrieval:

```json
{
  "keywords": ["research", "oklahoma", "stations", "73102"]
}
```

**Best Practices:**
- Lowercase, normalized
- Include topic, location, entity identifiers
- Use prefixes for status: `pending:`, `completed:`, `blocked:`
- Keep to 3-10 keywords per message

---

## XII. Implementation Notes

### Generating IDs

```python
import uuid

def new_id(prefix: str = "MSG") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"
```

### Generating Timestamps

```python
import datetime

def now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
```

### Auto-Escalation

When confidence ≥ 0.9 without provenance, implementations SHOULD auto-escalate to review:

```python
if confidence >= 0.9 and not provenance and safety["level"] != "review":
    safety["level"] = "review"
    safety["issues"].append({
        "code": "missing_provenance_high_confidence",
        "detail": "confidence >= 0.9 without provenance"
    })
```

---

## XIII. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2025-12-14 | Added `session_context` type, `keywords` field, session management |
| 1.0 | 2025-12-01 | Initial release |

---

*"Words are no longer weapons or whispers. They are transactions — every sentence, a receipt."*
