# VLP Message Types

## Overview

VLP defines seven message types, each with specific semantics and validation rules.

## claim

**Purpose:** Assert a fact or report an action.

**When to use:**
- Reporting completed actions
- Stating observations
- Making assertions about state

**Requirements:**
- Must include `confidence` score
- If `confidence >= 0.9`, must have `provenance` OR `safety.level = "review"`

**Example:**
```json
{
  "type": "claim",
  "sender": "The Observer",
  "content": "Found 5 gas stations in zip 73102",
  "confidence": 0.85,
  "provenance": ["google_places_api"],
  "keywords": ["research", "stations", "oklahoma"]
}
```

## evidence

**Purpose:** Support a prior claim with verifiable sources.

**When to use:**
- Providing proof for a claim
- Citing sources
- Documenting verification

**Requirements:**
- Must include `refers_to` (the claim being supported)
- Must include non-empty `provenance` array

**Example:**
```json
{
  "type": "evidence",
  "sender": "The Observer",
  "content": "Address verified via USPS API",
  "confidence": 0.95,
  "provenance": ["usps_api", "https://tools.usps.com/verify"],
  "refers_to": "MSG-claim-001"
}
```

## query

**Purpose:** Request information or action.

**When to use:**
- Asking another agent for data
- Requesting action
- Seeking clarification

**Requirements:**
- Confidence typically defaults to 1.0 (the query itself is certain)

**Example:**
```json
{
  "type": "query",
  "sender": "The Archivist",
  "receiver": "The Observer",
  "content": "What addresses were found for these stations?",
  "confidence": 1.0
}
```

## response

**Purpose:** Answer a prior query.

**When to use:**
- Replying to a query
- Providing requested information

**Requirements:**
- Must include `refers_to` (the query being answered)

**Example:**
```json
{
  "type": "response",
  "sender": "The Observer",
  "receiver": "The Archivist",
  "content": {"stations": [{"name": "QuikTrip", "address": "123 Main St"}]},
  "confidence": 0.9,
  "refers_to": "MSG-query-001"
}
```

## correction

**Purpose:** Amend a prior message.

**When to use:**
- Fixing errors in previous claims
- Updating outdated information
- Retracting incorrect statements

**Requirements:**
- Must include `refers_to` (the message being corrected)
- Becomes the new authoritative source

**Example:**
```json
{
  "type": "correction",
  "sender": "The Observer",
  "content": "Correction: 4 stations found, not 5 (duplicate removed)",
  "confidence": 0.95,
  "provenance": ["dedup_audit"],
  "refers_to": "MSG-claim-001"
}
```

## notice

**Purpose:** Announce conditions, alerts, or contextual facts.

**When to use:**
- System alerts
- Rate limit warnings
- Status updates
- Maintenance announcements

**Requirements:**
- May carry safety warnings
- Does not require evidence chain

**Example:**
```json
{
  "type": "notice",
  "sender": "The Dispatcher",
  "content": "API rate limit at 80% of daily quota",
  "confidence": 1.0,
  "safety": {
    "level": "review",
    "issues": [{"code": "quota_warning"}]
  }
}
```

## session_context

**Purpose:** Persist agent context for future sessions.

**When to use:**
- End of a work session
- Saving state for resumption
- Recording session summary

**Requirements:**
- Should include session metadata in payload
- Keywords should indicate completion status

**Example:**
```json
{
  "type": "session_context",
  "sender": "The Observer",
  "content": "Research completed. 7 stations verified, 1 pending review.",
  "session_id": "S-2025-01-04-observer-abc123",
  "confidence": 1.0,
  "keywords": ["research", "complete", "pending:manual-review"],
  "payload": {
    "completed": ["api_query", "verification"],
    "pending": ["manual_review"],
    "next_session_hints": ["Resolve unverified address"]
  }
}
```

## Type Selection Guide

| Situation | Type |
|-----------|------|
| "I found X" | `claim` |
| "Here's proof of X" | `evidence` |
| "What is X?" | `query` |
| "X is Y" (answering) | `response` |
| "X was wrong, it's Y" | `correction` |
| "Warning: X" | `notice` |
| "Session complete: X" | `session_context` |
