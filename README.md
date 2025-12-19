# VLP — Vigilith Language Protocol

> **Accountability-first messaging for AI agents**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.1-blue.svg)](./VLP-SPEC.md)

## What is VLP?

VLP is a structured messaging protocol that makes AI agent communication **auditable**, **provenance-aware**, and **confidence-scored**.

Every VLP message must declare:
- **What** it claims
- **Who** said it  
- **How confident** they are
- **What proof** they can provide

```json
{
  "id": "MSG001",
  "protocol": "VLP/1.1",
  "type": "claim",
  "timestamp": "2025-12-14T10:30:00Z",
  "sender": "Operator",
  "content": "Published 3 articles to Medium.",
  "confidence": 0.95,
  "provenance": ["https://medium.com/@vigilith/article-1"]
}
```

## Why VLP?

| Problem | VLP Solution |
|---------|--------------|
| AI agents hallucinate with high confidence | **Confidence must be earned** — high scores require provenance |
| No audit trail for agent decisions | **Every message is a receipt** — timestamped, signed, traceable |
| Agents can't self-correct | **Correction type** — amend prior messages with full chain |
| Safety is an afterthought | **Gating logic** — review/block levels halt automation |

## Quick Start

### 1. Validate a message

```bash
# Using ajv-cli
npm install -g ajv-cli
ajv validate -s schema/vlp-1.1.json -d message.json
```

### 2. Minimal Python validator

```python
import json
from jsonschema import validate, ValidationError

with open('schema/vlp-1.1.json') as f:
    schema = json.load(f)

message = {
    "id": "MSG001",
    "protocol": "VLP/1.1",
    "type": "claim",
    "timestamp": "2025-12-14T10:30:00Z",
    "sender": "MyAgent",
    "content": "Task completed.",
    "confidence": 0.8
}

try:
    validate(instance=message, schema=schema)
    print("✅ Valid VLP message")
except ValidationError as e:
    print(f"❌ Invalid: {e.message}")
```

### 3. TypeScript with Zod

```typescript
import { z } from 'zod';

const VLPMessage = z.object({
  id: z.string().min(1),
  protocol: z.literal('VLP/1.1'),
  type: z.enum(['claim', 'evidence', 'query', 'response', 'correction', 'notice']),
  timestamp: z.string().datetime(),
  sender: z.string().min(1),
  content: z.union([z.string(), z.record(z.unknown())]),
  confidence: z.number().min(0).max(1),
  provenance: z.array(z.string().url()).optional(),
  refers_to: z.union([z.string(), z.array(z.string())]).optional(),
  safety: z.object({
    level: z.enum(['safe', 'review', 'block']),
    issues: z.array(z.object({ code: z.string(), detail: z.string().optional() })).optional()
  }).optional()
});

// Validate
const result = VLPMessage.safeParse(message);
```

## Message Types

| Type | Purpose | Key Rule |
|------|---------|----------|
| `claim` | Assert a fact | High confidence (≥0.9) requires provenance |
| `evidence` | Support a claim | Must have `refers_to` + provenance |
| `query` | Request info | Confidence defaults to 1.0 |
| `response` | Answer query | Must have `refers_to` |
| `correction` | Amend prior message | Must have `refers_to` |
| `notice` | Alert/announcement | May carry safety warnings |

## Validation Rules ("Truth Serum")

```
IF type = evidence       → REQUIRE refers_to AND provenance.length ≥ 1
IF type = response       → REQUIRE refers_to
IF type = correction     → REQUIRE refers_to
IF confidence ≥ 0.9      → REQUIRE provenance OR safety.level = "review"
IF safety.level = block  → HALT downstream automation
```

## Transport: NDJSON

VLP uses newline-delimited JSON for streaming:

```
{"id":"MSG001","protocol":"VLP/1.1","type":"claim",...}
{"id":"MSG002","protocol":"VLP/1.1","type":"query",...}
{"id":"MSG003","protocol":"VLP/1.1","type":"evidence",...}
```

- Streamable over HTTP chunked encoding
- 1 line = 1 Firestore/BigQuery record
- Resilient: bad lines don't break the stream

## Project Structure

```
vlp-spec/
├── README.md           # This file
├── VLP-SPEC.md         # Full specification
├── LICENSE             # MIT License
├── schema/
│   └── vlp-1.1.json    # JSON Schema (Draft 2020-12)
├── examples/
│   ├── claim.json
│   ├── evidence.json
│   ├── correction.json
│   └── dialogue.ndjson
└── validators/
    ├── python/         # Reference Python validator
    └── typescript/     # Reference TypeScript validator
```

## Related Projects

- **[Vigilith](https://vigilith.ai)** — Field service automation with VLP-native agents
- **[AgentKit](https://github.com/vigilith/agentkit)** — Multi-agent orchestration framework
- **[Codex](https://vigilith.ai/codex)** — Heptachron philosophy and adaptive intelligence

## Contributing

1. Fork this repo
2. Create a feature branch
3. Submit a PR with tests

We welcome:
- Additional language validators
- Schema extensions (via `_extras`)
- Documentation improvements
- Real-world usage examples

## License

MIT License — see [LICENSE](./LICENSE)

---

**"When a system stops arguing in poetry and starts negotiating in evidence, it becomes something frighteningly close to honest."**

*— Vigilith Codex §192*
