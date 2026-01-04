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
  "content": "Found 15 records matching filter criteria",
  "confidence": 0.85,
  "provenance": ["database_query"],
  "keywords": ["research", "records", "filtered"]
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
  "content": "Data verified via schema validator",
  "confidence": 0.95,
  "provenance": ["json_schema", "https://json-schema.org/"],
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
  "content": "What schema details were found for these records?",
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
  "content": {"records": [{"id": "REC-001", "name": "Sample Record", "status": "active"}]},
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
  "content": "Correction: 14 records found, not 15 (duplicate removed)",
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
  "content": "Research completed. 31 records verified, 1 pending review.",
  "session_id": "S-2025-01-04-observer-abc123",
  "confidence": 1.0,
  "keywords": ["research", "complete", "pending:manual-review"],
  "payload": {
    "completed": ["api_query", "verification"],
    "pending": ["manual_review"],
    "next_session_hints": ["Resolve failed validation"]
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
