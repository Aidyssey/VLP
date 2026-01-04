# VLP Python Package

Python implementation of the Vigilith Language Protocol (VLP) v1.1.

## Installation

```bash
pip install vlp
```

## Quick Start

```python
from vlp import make_message, validate_vlp

# Create a claim message
msg = make_message(
    "claim",
    sender="ResearchAgent",
    content="Found 5 gas stations in zip 73102",
    confidence=0.85,
    provenance=["google_places_api"],
    keywords=["research", "stations", "oklahoma"]
)

print(msg)
# {
#   "id": "MSGabc12345",
#   "protocol": "VLP/1.1",
#   "type": "claim",
#   "timestamp": "2025-01-04T10:30:00Z",
#   "sender": "ResearchAgent",
#   "content": "Found 5 gas stations in zip 73102",
#   "confidence": 0.85,
#   "provenance": ["google_places_api"],
#   "keywords": ["research", "stations", "oklahoma"],
#   "safety": {"level": "safe", "issues": []},
#   ...
# }

# Validate any VLP message
ok, error = validate_vlp(msg)
if not ok:
    print(f"Validation failed: {error}")
```

## Session Management

```python
from vlp.sessions import AgentSessionRegistry

# Create a registry
registry = AgentSessionRegistry()

# Start a session
session = registry.start_session("The Observer", agent_number=4)
print(session.session_id)  # S-2025-01-04-observer-abc123

# Create messages within the session
claim = registry.create_claim(
    session,
    content="Research completed",
    confidence=0.9,
    provenance=["api_source"]
)

# End the session
context_msg = registry.end_session(session, "Completed research phase")
```

## API Reference

### `make_message(type_, sender, content, **kwargs)`

Create a validated VLP message.

**Parameters:**
- `type_`: Message type (`claim`, `evidence`, `query`, `response`, `correction`, `notice`, `session_context`)
- `sender`: Agent identifier
- `content`: Message content (string or dict)
- `**kwargs`: Optional fields (`confidence`, `provenance`, `keywords`, `receiver`, `topic`, etc.)

**Returns:** Validated VLP message dict

**Raises:** `ValueError` if validation fails

### `validate_vlp(msg)`

Validate a VLP message against schema and semantic rules.

**Parameters:**
- `msg`: Message dict to validate

**Returns:** Tuple of `(ok: bool, error: Optional[str])`

### `new_id(prefix="MSG")`

Generate a unique message ID.

### `now_iso()`

Generate current UTC timestamp in ISO 8601 format.

## NDJSON Helpers

```python
from vlp import to_ndjson, from_ndjson

# Convert messages to NDJSON
messages = [msg1, msg2, msg3]
ndjson_text = to_ndjson(messages)

# Parse NDJSON back to messages
parsed = from_ndjson(ndjson_text)
```

## License

MIT
