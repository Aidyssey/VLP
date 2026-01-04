# VLP Validation Rules ("Truth Serum")

## Overview

VLP enforces a set of semantic rules beyond basic schema validation. These rules ensure accountability and prevent unsubstantiated claims.

## Rule 1: Evidence Requires Proof

Evidence messages exist to support prior claims. They must always reference what they support and provide sources.

```
IF type == "evidence"
THEN:
  - refers_to REQUIRED
  - provenance.length >= 1
```

**Why:** Evidence without a reference is orphaned. Evidence without sources is just another claim.

**Example (Invalid):**
```json
{
  "type": "evidence",
  "content": "This is true because I said so",
  "confidence": 0.9
  // Missing: refers_to, provenance
}
```

**Example (Valid):**
```json
{
  "type": "evidence",
  "content": "Verified via API",
  "refers_to": "MSG-claim-001",
  "provenance": ["api_response_log"],
  "confidence": 0.9
}
```

## Rule 2: Responses and Corrections Must Reference

Responses answer queries. Corrections amend prior messages. Both must specify what they reference.

```
IF type IN ("response", "correction")
THEN refers_to REQUIRED
```

**Why:** A response to nothing is just a claim. A correction to nothing is confusion.

**Example (Invalid):**
```json
{
  "type": "response",
  "content": "The answer is 42",
  "confidence": 0.9
  // Missing: refers_to
}
```

## Rule 3: High Confidence Must Be Earned

Claims with high confidence (≥0.9) must provide evidence OR explicitly acknowledge they need review.

```
IF confidence >= 0.9 AND provenance.length == 0
THEN safety.level MUST BE "review"
```

**Why:** High confidence without evidence is arrogance. The protocol auto-escalates to prevent unearned certainty.

**Auto-escalation behavior:**
```python
# If you create a high-confidence claim without provenance:
msg = make_message(
    "claim",
    sender="Agent",
    content="I am 95% sure",
    confidence=0.95
    # No provenance provided
)

# The message will be modified:
assert msg["safety"]["level"] == "review"
assert msg["safety"]["issues"][0]["code"] == "missing_provenance_high_confidence"
```

**How to avoid escalation:**

Option 1 - Provide provenance:
```json
{
  "confidence": 0.95,
  "provenance": ["source_a", "source_b"]
}
```

Option 2 - Explicitly set review:
```json
{
  "confidence": 0.95,
  "safety": {"level": "review", "issues": []}
}
```

Option 3 - Lower confidence:
```json
{
  "confidence": 0.85
}
```

## Rule 4: Block Halts Everything

When `safety.level == "block"`, downstream automation must stop.

```
IF safety.level == "block"
THEN downstream_automation.halt()
```

**Why:** Block is the emergency brake. It means "stop and get a human."

**Common block scenarios:**
- Security concerns detected
- Destructive actions pending
- Policy violations
- Confidence too low for automation

## Summary Table

| Rule | Condition | Requirement |
|------|-----------|-------------|
| Evidence proof | type == "evidence" | refers_to + provenance |
| Response reference | type == "response" | refers_to |
| Correction reference | type == "correction" | refers_to |
| Earned confidence | confidence >= 0.9, no provenance | safety.level = "review" |
| Block halts | safety.level == "block" | Stop automation |

## Validation Order

1. **Schema validation** - JSON structure, required fields, types
2. **Semantic validation** - Rules above
3. **Context metrics** (optional) - Depth, integrity, gate computation

## Implementation Notes

### Python
```python
from vlp import validate_vlp, make_message

# validate_vlp checks both schema and semantic rules
ok, error = validate_vlp(msg)

# make_message auto-validates and raises on failure
try:
    msg = make_message("evidence", sender="Agent", content="Proof")
except ValueError as e:
    print(f"Validation failed: {e}")
```

### TypeScript
```typescript
import { validateVlp, makeMessage } from '@vigilith/vlp';

// validateVlp returns validation result
const result = validateVlp(msg);
if (!result.valid) {
  console.error(result.errors);
}

// makeMessage throws on validation failure
try {
  const msg = makeMessage({ type: 'evidence', sender: 'Agent', content: 'Proof' });
} catch (e) {
  console.error('Validation failed:', e.message);
}
```
