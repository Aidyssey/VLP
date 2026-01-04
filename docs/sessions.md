# VLP Session Management

## Overview

Sessions group related VLP messages together, enabling:
- Context tracking across multiple messages
- Sequential message ordering
- Session-scoped identifiers
- Memory persistence via `session_context`

## Session ID Format

```
S-{YYYY-MM-DD}-{agent_slug}-{short_uuid}
```

**Components:**
- `S-` prefix identifies session IDs
- Date in ISO format
- Agent name slug (lowercase, hyphens, max 12 chars)
- 6-character UUID suffix

**Examples:**
- `S-2025-01-04-observer-abc123`
- `S-2025-01-04-sentinel-def456`
- `S-2025-01-04-the-keeper-789abc`

## Message ID Format (Session-Scoped)

```
{PREFIX}-{session_suffix}-{seq:04d}
```

**Common prefixes:**
- `MSG` - Generic message
- `CLM` - Claim
- `AUD` - Audit
- `CTX` - Context
- `QRY` - Query
- `RSP` - Response
- `EVD` - Evidence

**Examples:**
- `CLM-abc123-0001` (first claim in session)
- `CLM-abc123-0002` (second claim)
- `CTX-abc123-0010` (session context at message 10)

## Session Lifecycle

### 1. Start Session

```python
from vlp.sessions import AgentSessionRegistry

registry = AgentSessionRegistry()
session = registry.start_session("The Observer", agent_number=4)

print(session.session_id)    # S-2025-01-04-observer-abc123
print(session.started_at)    # 2025-01-04T10:00:00Z
```

### 2. Create Messages

```python
# Using the registry
claim = registry.create_claim(
    session,
    content="Research started",
    confidence=0.9,
    keywords=["research", "start"]
)

# Or manually with session info
from vlp import make_message

msg = make_message(
    "claim",
    sender=session.agent_name,
    content="Manual claim",
    session_id=session.session_id,
    seq=session.next_seq()
)
```

### 3. End Session

```python
context_msg = registry.end_session(
    session,
    summary="Research completed. 5 stations found."
)

# context_msg is a session_context message with:
# - Session metadata (started_at, ended_at, total_messages)
# - Summary content
# - Agent information
```

## Session Context Message

The `session_context` type is used at session end to persist context:

```json
{
  "type": "session_context",
  "session_id": "S-2025-01-04-observer-abc123",
  "sender": "The Observer",
  "content": "Research completed. 5 stations found, 1 needs review.",
  "keywords": ["research", "complete", "pending:manual-review"],
  "payload": {
    "agent_number": 4,
    "started_at": "2025-01-04T10:00:00Z",
    "ended_at": "2025-01-04T10:30:00Z",
    "total_messages": 12,
    "completed": ["api_query", "address_verification", "notion_export"],
    "pending": ["manual_address_review"],
    "next_session_hints": [
      "Resolve unverified address for Quick Stop #77",
      "Expand search to 73103 zip code"
    ]
  }
}
```

## Keywords for Memory

Use keywords to enable cross-session discovery:

```json
{
  "keywords": [
    "research",           // Topic
    "oklahoma",          // Location
    "73102",             // Identifier
    "complete",          // Status
    "pending:review"     // Action needed
  ]
}
```

**Keyword conventions:**
- Lowercase, normalized
- Status prefixes: `pending:`, `complete:`, `blocked:`
- Entity identifiers: zip codes, IDs, names
- 3-10 keywords per message

## Thread-Safety

The session registry is thread-safe:

```python
# Safe to use from multiple threads
session = registry.start_session("Agent", 1)
seq1 = session.next_seq()  # Thread-safe increment
seq2 = session.next_seq()  # Always seq1 + 1
```

## TypeScript Usage

```typescript
import { AgentSessionRegistry } from '@vigilith/vlp';

const registry = new AgentSessionRegistry();
const session = registry.startSession('The Observer', 4);

// Create claims
const claim = registry.createClaim(session, {
  content: 'Research started',
  confidence: 0.9,
  keywords: ['research', 'start']
});

// End session
const context = registry.endSession(session, 'Research completed');
```

## Best Practices

1. **One session per workflow** - Group related work
2. **End sessions explicitly** - Always emit `session_context`
3. **Include next_session_hints** - Help future sessions resume
4. **Use meaningful keywords** - Enable memory retrieval
5. **Track pending work** - Document incomplete tasks
