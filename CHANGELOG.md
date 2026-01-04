# Changelog

All notable changes to the Vigilith Language Protocol (VLP) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-04

### Added

- **Session Management**: New `session_id` and `seq` fields for grouping related messages
- **Agent Memory**: `session_context` message type for persisting context across sessions
- **Keywords**: `keywords` array field for searchable agent memory retrieval
- **Python Package**: Full runtime implementation with `make_message`, `validate_vlp`
- **TypeScript Package**: Complete TypeScript/Node implementation with types
- **Session Registry**: `AgentSessionRegistry` class for managing agent sessions
- **Context Metrics**: Validator-computed `context_integrity`, `context_depth`, `gate` fields

### Changed

- Enhanced provenance to support both simple strings and structured reference objects
- Improved validation rules documentation ("Truth Serum")
- Updated JSON schema with new fields and `session_context` type

### Fixed

- Schema now properly validates `refers_to` as string, array, or null
- Confidence auto-escalation now correctly adds issue codes

## [1.0.0] - 2025-12-01

### Added

- Initial VLP specification release
- Six core message types: `claim`, `evidence`, `query`, `response`, `correction`, `notice`
- Required fields: `id`, `protocol`, `type`, `timestamp`, `sender`, `content`, `confidence`
- Safety classification system with `safe`, `review`, `block` levels
- Provenance tracking for evidence chains
- NDJSON transport format specification
- JSON Schema for validation (Draft-07)
- Basic validation rules for message integrity

---

## Migration Guide

### From 1.0 to 1.1

VLP 1.1 is backwards compatible with 1.0. Existing messages will validate, but to use new features:

1. **Add session tracking** (optional but recommended):
   ```json
   {
     "session_id": "S-2025-01-04-agent-abc123",
     "seq": 1
   }
   ```

2. **Add keywords for memory** (optional):
   ```json
   {
     "keywords": ["topic", "entity", "action"]
   }
   ```

3. **Use session_context at session end** (optional):
   ```json
   {
     "type": "session_context",
     "content": "Session summary...",
     "keywords": ["completed:task1", "pending:task2"]
   }
   ```

### Breaking Changes

None. VLP 1.1 is fully backwards compatible with 1.0.
