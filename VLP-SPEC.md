# Vigilith Language Protocol (VLP) v1.1

> **"When a system stops arguing in poetry and starts negotiating in evidence, it becomes something frighteningly close to honest."**
> — Vigilith Codex §192

## Overview

The Vigilith Language Protocol (VLP) is a structured messaging format for AI agent communication that enforces **accountability**, **provenance**, and **quantified confidence**. It replaces faith in machine outputs with structured self-doubt.

Every VLP message must carry:
- **What** it claims
- **Who** said it
- **How confident** they are
- **What proof** they can provide

The result is not conversation — it is **computation made accountable**.

---

## Design Principles

| Principle | Description |
|-----------|-------------|
| **Auditability Over Eloquence** | Every statement must be traceable. The prettier the claim, the more rigor it demands. |
| **Quantified Confidence** | No assertion without a degree of certainty. Every "truth" must declare its entropy. |
| **Evidence as Currency** | Claims buy trust only with provenance. No receipts, no belief. |
| **Human Legibility** | JSON, not jargon. Every message should be readable by both machine and mortal. |
| **Compact Cooperation** | Agents must coordinate at high speed without surrendering clarity. NDJSON enables that stream. |
| **Fail Gracefully** | Ambiguity, contradiction, and uncertainty are not errors — they are part of the audit trail. |

---

## Message Types

| Type | Purpose | Requirements |
|------|---------|--------------|
| `claim` | A factual assertion or report of action | Must quantify confidence; high-confidence claims require provenance |
| `evidence` | Supports a prior claim | Must include `refers_to` + `provenance.length ≥ 1` |
| `query` | Requests information or action | Confidence defaults to 1.0 |
| `response` | Answers a query | Must include `refers_to` |
| `correction` | Amends a prior message | Must include `refers_to`; becomes new source of truth |
| `notice` | Announces conditions, alerts, or contextual facts | May carry constraints or safety warnings |

---

## Core Schema

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (e.g., "MSG001" or UUID) |
| `protocol` | string | Must equal `"VLP/1.1"` |
| `type` | string | One of: claim, evidence, query, response, correction, notice |
| `timestamp` | string (ISO 8601) | Creation time in UTC |
| `sender` | string | Originating agent identifier |
| `content` | string or object | Main message text or structured data |
| `confidence` | number (0.0–1.0) | Sender's certainty about content correctness |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Groups related exchanges |
| `seq` | integer | Sequential index within session |
| `receiver` | string | Intended target agent |
| `topic` | string | Domain category (e.g., "content_ops") |
| `payload` | object | Machine-actionable structured parameters |
| `provenance` | array | Evidence sources (URIs, hashes, or structured refs) |
| `constraints` | array[string] | Policy, style, or safety conditions |
| `safety` | object | Content safety triage (see below) |
| `refers_to` | string or array | Links to prior message IDs |
| `_extras` | object | Forward-compatible metadata container |

---

## Safety Object

Structured triage for trust and compliance:

```json
{
  "safety": {
    "level": "review",
    "issues": [
      { "code": "off_brand_tone", "detail": "Detected informal phrasing in paragraph 2." }
    ],
    "requires_human": true
  }
}
```

| Level | Meaning | Automation Policy |
|-------|---------|-------------------|
| `safe` | No issues detected | Proceed automatically |
| `review` | Requires human confirmation | Hold for oversight |
| `block` | Must not execute | Halt downstream actions |

---

## Validation Rules ("Truth Serum")

These constraints are enforced at runtime:

| Rule | Description |
|------|-------------|
| **Evidence must attach** | `type = evidence` → must include `refers_to` + `provenance.length ≥ 1` |
| **References required** | `type ∈ {response, correction}` → `refers_to` required |
| **High confidence earned** | `confidence ≥ 0.9` → must include provenance OR `safety.level = review` |
| **Safety governs execution** | `safety.level = block` → downstream automations must not proceed |
| **Confidence mandatory** | All messages must declare confidence (queries default to 1.0) |

---

## Context Extension (v1.1+)

VLP 1.1 introduces validator-computed context metrics:

### Context Layers

| Layer | Purpose | Verification |
|-------|---------|--------------|
| **Intent** | Goal + risk level | Validate goal string, risk enum |
| **Constraints** | Active policies | Verify against constraint registry |
| **State** | Session/runtime refs | Resolve state_refs, match session_id |
| **Memory** | Persistent context | Resolve memory_refs, check TTL |
| **Evidence** | Provenance links | Verify evidence_refs, fetch/snapshot |
| **Capability** | Agent permissions | Resolve capability_refs, check required |

### Validator-Computed Fields

These fields are **read-only** — set by the validator, not the agent:

```json
{
  "context_metrics": {
    "context_depth": 4,
    "context_integrity": 0.85,
    "context_debt": 0.15,
    "layers_verified": ["intent", "constraints", "state", "evidence"],
    "layers_missing": ["memory", "capability"]
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `context_depth` | integer (0–6) | Count of verified context layers |
| `context_integrity` | float (0.0–1.0) | Weighted verification score |
| `context_debt` | float (0.0–1.0) | 1 - integrity; technical debt metric |

### Gating Rules

| Condition | Gate | Action |
|-----------|------|--------|
| `context_integrity < 0.7` | `review` | Emit notice, hold for human |
| `risk_level = "high"` AND evidence unverified | `block` | Halt execution |
| `confidence ≥ 0.9` AND provenance empty | `review` | Existing truth-serum rule |

---

## Transport: NDJSON

VLP uses **Newline-Delimited JSON (NDJSON)** for real-time coordination:

```
{"id":"MSG001","protocol":"VLP/1.1","type":"claim","sender":"Operator","content":"Published 5 posts.","confidence":0.95}
{"id":"MSG002","protocol":"VLP/1.1","type":"query","sender":"Archivist","refers_to":"MSG001","content":"Provide links.","confidence":1.0}
{"id":"MSG003","protocol":"VLP/1.1","type":"evidence","sender":"Operator","refers_to":"MSG001","provenance":["https://..."],"confidence":1.0}
```

**Why NDJSON?**
- Streamable over HTTP chunked encoding
- Perfect for Firestore or Cloud Logging (1 line = 1 record)
- Human-readable
- Resilient: one bad line doesn't break the stream

---

## Example Dialogue

### 1. Operator → Claim
```json
{
  "id": "MSG001",
  "protocol": "VLP/1.1",
  "type": "claim",
  "timestamp": "2025-12-14T10:30:00Z",
  "sender": "Operator",
  "content": "Cross-posted 3 new articles to the forum and Medium.",
  "confidence": 0.95,
  "constraints": ["tone: formal"]
}
```

### 2. Archivist → Query
```json
{
  "id": "MSG002",
  "protocol": "VLP/1.1",
  "type": "query",
  "timestamp": "2025-12-14T10:30:05Z",
  "sender": "Archivist",
  "receiver": "Operator",
  "content": "Please provide links for audit.",
  "confidence": 1.0,
  "refers_to": "MSG001"
}
```

### 3. Operator → Evidence
```json
{
  "id": "MSG003",
  "protocol": "VLP/1.1",
  "type": "evidence",
  "timestamp": "2025-12-14T10:30:10Z",
  "sender": "Operator",
  "receiver": "Archivist",
  "refers_to": "MSG001",
  "confidence": 1.0,
  "provenance": [
    "https://medium.com/@vigilith/article-1",
    "https://medium.com/@vigilith/article-2",
    "https://forum.vigilith.ai/post/123"
  ]
}
```

### 4. Archivist → Notice (Drift Detected)
```json
{
  "id": "MSG004",
  "protocol": "VLP/1.1",
  "type": "notice",
  "timestamp": "2025-12-14T10:30:15Z",
  "sender": "Archivist",
  "receiver": "Operator",
  "content": "Tone drift detected in article 2.",
  "confidence": 0.8,
  "refers_to": "MSG001",
  "safety": {
    "level": "review",
    "issues": [{ "code": "off_brand_tone" }]
  }
}
```

### 5. Operator → Correction
```json
{
  "id": "MSG005",
  "protocol": "VLP/1.1",
  "type": "correction",
  "timestamp": "2025-12-14T10:35:00Z",
  "sender": "Operator",
  "receiver": "Archivist",
  "content": "Adjusted tone to formal style.",
  "confidence": 0.9,
  "refers_to": "MSG001",
  "provenance": ["https://medium.com/@vigilith/article-2-v2"]
}
```

---

## JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://vigilith.ai/schemas/vlp/1.1",
  "title": "Vigilith Language Protocol (VLP) v1.1",
  "type": "object",
  "required": ["id", "protocol", "type", "timestamp", "sender", "content", "confidence"],
  "properties": {
    "id": { "type": "string", "minLength": 1 },
    "protocol": { "type": "string", "const": "VLP/1.1" },
    "type": { 
      "type": "string", 
      "enum": ["claim", "evidence", "query", "response", "correction", "notice"] 
    },
    "timestamp": { "type": "string", "format": "date-time" },
    "session_id": { "type": "string" },
    "seq": { "type": "integer", "minimum": 0 },
    "sender": { "type": "string", "minLength": 1 },
    "receiver": { "type": "string" },
    "topic": { "type": "string" },
    "content": { 
      "oneOf": [
        { "type": "string" },
        { "type": "object" }
      ]
    },
    "payload": { "type": "object" },
    "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
    "provenance": {
      "type": "array",
      "items": {
        "oneOf": [
          { "type": "string", "format": "uri" },
          { 
            "type": "object",
            "properties": {
              "ref": { "type": "string" },
              "type": { "type": "string" },
              "hash": { "type": "string" },
              "fetched_at": { "type": "string", "format": "date-time" }
            },
            "required": ["ref"]
          }
        ]
      }
    },
    "constraints": { "type": "array", "items": { "type": "string" } },
    "safety": {
      "type": "object",
      "properties": {
        "level": { "type": "string", "enum": ["safe", "review", "block"] },
        "issues": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "code": { "type": "string" },
              "detail": { "type": "string" }
            },
            "required": ["code"]
          }
        },
        "requires_human": { "type": "boolean" }
      }
    },
    "refers_to": {
      "oneOf": [
        { "type": "string" },
        { "type": "array", "items": { "type": "string" } }
      ]
    },
    "_extras": { "type": "object" }
  },
  "additionalProperties": true
}
```

---

## Versioning

| Rule | Description |
|------|-------------|
| **Protocol ID** | `"VLP/<major>.<minor>"` |
| **Backward Compatibility** | Agents ignore unknown fields |
| **Forward Compatibility** | New fields allowed under `_extras` |
| **Reserved Types** | `observation`, `alert`, `task` reserved for v1.2+ |
| **Deprecation** | 1 major version grace period before removal |

---

## Comparison to Alternatives

| Feature | VLP | OpenTelemetry | JSON-LD | W3C PROV |
|---------|-----|---------------|---------|----------|
| **Focus** | Agent accountability | Distributed tracing | Linked data | Provenance graphs |
| **Confidence scoring** | ✅ Native | ❌ | ❌ | ❌ |
| **Gating logic** | ✅ Built-in | ❌ | ❌ | ❌ |
| **Human legibility** | ✅ Plain JSON | Moderate | Complex | Complex |
| **Agent-to-agent** | ✅ Designed for | ❌ Service-focused | ❌ Data-focused | ❌ Record-focused |
| **Self-correction** | ✅ `correction` type | ❌ | ❌ | ❌ |

---

## License

MIT License

Copyright (c) 2025 Vigilith Industries / Aidyssey LLC

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

---

## Authors

- **Alucard** — Protocol design, Codex author
- **Vigilith Industries** — Reference implementation

---

## Links

- **Spec**: https://vigilith.ai/vlp
- **Schema**: https://vigilith.ai/schemas/vlp/1.1
- **Reference Implementation**: https://github.com/vigilith/vlp-spec
- **Codex**: https://vigilith.ai/codex
