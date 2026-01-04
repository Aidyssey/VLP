# VLP Context Enforcement

## Overview

Context enforcement computes trust metrics for VLP messages, enabling automated gating decisions.

## Context Metrics

Validators compute these read-only fields:

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `context_depth` | integer | 0-6 | Number of verified context layers |
| `context_integrity` | number | 0.0-1.0 | Overall verification score |
| `context_debt` | number | 0.0-1.0 | 1.0 - integrity (technical debt) |
| `gate` | string | pass/review/fail | Computed gate decision |

## Integrity Calculation

Integrity is computed from:
- Provenance count and quality
- Constraint satisfaction
- Evidence chain verification
- Safety classification

**Simplified formula:**
```
integrity = 0.5
          + (0.12 * provenance_count)
          + (0.09 * constraint_count)
          - (0.10 * unknown_constraints)
```

**Capped to [0.0, 1.0]**

## Gate Decisions

Gates determine automated handling:

```
IF integrity >= 0.75 THEN gate = "pass"
ELSE IF integrity >= 0.5 THEN gate = "review"
ELSE gate = "fail"
```

| Gate | Integrity | Behavior |
|------|-----------|----------|
| `pass` | ≥ 0.75 | Proceed automatically |
| `review` | 0.5 - 0.74 | Queue for human review |
| `fail` | < 0.5 | Halt automation |

## Gate-Safety Escalation

Gates can escalate safety levels:

```python
if gate == "fail" and safety.level == "safe":
    safety.level = "review"
    safety.issues.append({"code": "low_integrity_gate"})
```

## Improving Integrity

### Add Provenance

Each provenance item increases integrity:

```json
{
  "provenance": [
    "api_source",
    {"ref": "https://example.com/doc", "kind": "url"},
    {"ref": "sha256:abc123", "kind": "hash"}
  ]
}
```

### Satisfy Constraints

Known constraints boost integrity:

```json
{
  "constraints": ["tone: formal", "format: json"]
}
```

### Provide Evidence

Evidence chains verify claims:

```json
{
  "type": "evidence",
  "refers_to": "MSG-claim-001",
  "provenance": ["verification_log"]
}
```

## Context Layers

The six context layers (depth 0-6):

1. **Intent** - Goal and risk level
2. **Constraints** - Behavioral rules
3. **State** - Current system state
4. **Memory** - Historical context
5. **Evidence** - Supporting proof
6. **Capability** - Agent permissions

More verified layers = higher depth.

## Example Message with Metrics

After validation, a message may include:

```json
{
  "id": "MSG001",
  "type": "claim",
  "content": "Research completed",
  "confidence": 0.9,
  "provenance": ["api_source", "verification_log"],
  "constraints": ["tone: formal"],
  "safety": {"level": "safe", "issues": []},

  "context_depth": 4,
  "context_integrity": 0.82,
  "context_debt": 0.18,
  "gate": "pass"
}
```

## Implementation

### Python (Validator)

```python
from vlp.validator import normalize_and_validate, ConstraintRegistry

registry = ConstraintRegistry(known_constraints={"tone: formal", "format: json"})

messages = normalize_and_validate(
    payload=raw_message,
    schema=vlp_schema,
    reg=registry,
    artifact_resolver=...,
    capability_resolver=...,
    evidence_verifier=...
)

for msg in messages:
    print(f"Integrity: {msg['context_integrity']}")
    print(f"Gate: {msg['gate']}")
```

### TypeScript (Validator Service)

```typescript
import { validateAndNormalizeVlp } from '@vigilith/vlp-registry';

const result = await validateAndNormalizeVlp(inbound, {
  tenantId: 'tenant-1',
  workspaceId: 'workspace-1',
  registry: registryConfig
});

console.log(`Integrity: ${result.context_integrity}`);
console.log(`Gate: ${result.gate}`);
```

## Best Practices

1. **Aim for integrity ≥ 0.75** for automated processing
2. **Include provenance** for high-confidence claims
3. **Use known constraints** to boost integrity
4. **Monitor gate distribution** to tune thresholds
5. **Review "fail" gates** before manual override
