# Vigilith Language Protocol (VLP) v1.1

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Protocol Version](https://img.shields.io/badge/VLP-1.1-blue.svg)](./SPEC.md)

> **Evidence Over Belief** — A structured protocol for accountable AI agent communication.

VLP is an accountability-focused messaging protocol for AI agents. Every message carries confidence scores, provenance chains, and safety classifications — replacing faith in outputs with structured self-doubt.

## Why VLP?

Traditional AI systems speak in assertions. VLP makes them speak in **receipts**.

| Principle | Meaning |
|-----------|---------|
| **Auditability Over Eloquence** | Every statement must be traceable |
| **Quantified Confidence** | No assertion without a degree of certainty |
| **Evidence as Currency** | Claims buy trust only with provenance |
| **Human Legibility** | JSON, not jargon — readable by machine and mortal |

## Quick Start

### Python

```bash
pip install vlp
```

```python
from vlp import make_message, validate_vlp

# Create a claim with provenance
msg = make_message(
    "claim",
    sender="ResearchAgent",
    content="Found 5 gas stations in zip 73102",
    confidence=0.85,
    provenance=["google_places_api"],
    keywords=["research", "stations", "oklahoma"]
)

# Validate any VLP message
ok, error = validate_vlp(msg)
```

### TypeScript/Node

```bash
npm install @vigilith/vlp
```

```typescript
import { makeMessage, validateVlp } from '@vigilith/vlp';

const msg = makeMessage({
  type: 'claim',
  sender: 'ResearchAgent',
  content: 'Found 5 gas stations in zip 73102',
  confidence: 0.85,
  provenance: ['google_places_api'],
  keywords: ['research', 'stations', 'oklahoma']
});

const { valid, errors } = validateVlp(msg);
```

## Message Types

| Type | Purpose | Requirements |
|------|---------|--------------|
| `claim` | Factual assertion | Confidence required; high confidence (≥0.9) needs provenance |
| `evidence` | Supports prior claim | Must include `refers_to` + non-empty provenance |
| `query` | Information request | Confidence defaults to 1.0 |
| `response` | Answers a query | Must include `refers_to` |
| `correction` | Amends prior message | Must include `refers_to`; becomes new source of truth |
| `notice` | Contextual alert | May carry constraints or safety warnings |
| `session_context` | Agent memory persistence | Used at session end to persist context |

## Core Message Structure

```json
{
  "id": "MSG001",
  "protocol": "VLP/1.1",
  "type": "claim",
  "timestamp": "2025-12-14T10:30:00Z",
  "session_id": "S-2025-12-14-agent-abc123",
  "seq": 1,
  "sender": "TheObserver",
  "receiver": "TheArchivist",
  "content": "Cross-posted 3 new articles to the forum.",
  "confidence": 0.95,
  "provenance": ["medium_api", "substack_api"],
  "keywords": ["content", "publishing", "crosspost"],
  "safety": {
    "level": "safe",
    "issues": []
  }
}
```

## Validation Rules ("Truth Serum")

The protocol enforces these constraints at runtime:

| Condition | Requirement |
|-----------|-------------|
| Evidence messages | Must include `refers_to` + ≥1 provenance item |
| Response/correction | Must cite prior message via `refers_to` |
| High confidence (≥0.9) | Requires provenance OR `safety.level = review` |
| Safety blocking | `safety.level = block` halts downstream automation |

## Safety Levels

```
safe    → Proceed automatically
review  → Hold for human oversight
block   → Halt all downstream actions
```

## Transport Format

VLP uses **NDJSON** (newline-delimited JSON) for streaming:

```text
{"id":"MSG001","protocol":"VLP/1.1","type":"claim",...}
{"id":"MSG002","protocol":"VLP/1.1","type":"evidence",...}
{"id":"MSG003","protocol":"VLP/1.1","type":"response",...}
```

## Documentation

- [Full Specification](./SPEC.md)
- [Message Types](./docs/message-types.md)
- [Validation Rules](./docs/validation-rules.md)
- [Context Enforcement](./docs/context-enforcement.md)
- [Agent Sessions](./docs/sessions.md)

## Packages

| Package | Language | Status |
|---------|----------|--------|
| [vlp](./python/) | Python 3.10+ | Stable |
| [@vigilith/vlp](./typescript/) | TypeScript/Node | Stable |

## Related Projects

- **[Vigilith](https://vigilith.ai)** — Transparency platform built on VLP
- **AgentKit** — Agent orchestration framework using VLP messaging
- **Codex** — Philosophical framework for accountable AI

## License

MIT License — see [LICENSE](./LICENSE) for details.

---

*"When a system stops arguing in poetry and starts negotiating in evidence, it becomes something frighteningly close to honest."*
