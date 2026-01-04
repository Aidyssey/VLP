# VLP TypeScript Package

TypeScript/Node implementation of the Vigilith Language Protocol (VLP) v1.1.

## Installation

```bash
npm install @vigilith/vlp
```

## Quick Start

```typescript
import { makeMessage, validateVlp } from '@vigilith/vlp';

// Create a claim message
const msg = makeMessage({
  type: 'claim',
  sender: 'ResearchAgent',
  content: 'Found 5 gas stations in zip 73102',
  confidence: 0.85,
  provenance: ['google_places_api'],
  keywords: ['research', 'stations', 'oklahoma']
});

console.log(msg);
// {
//   id: 'MSGabc12345',
//   protocol: 'VLP/1.1',
//   type: 'claim',
//   timestamp: '2025-01-04T10:30:00Z',
//   sender: 'ResearchAgent',
//   content: 'Found 5 gas stations in zip 73102',
//   confidence: 0.85,
//   provenance: ['google_places_api'],
//   keywords: ['research', 'stations', 'oklahoma'],
//   safety: { level: 'safe', issues: [] },
//   ...
// }

// Validate any VLP message
const result = validateVlp(msg);
if (!result.valid) {
  console.error('Validation failed:', result.errors);
}
```

## Session Management

```typescript
import { AgentSessionRegistry } from '@vigilith/vlp';

// Create a registry
const registry = new AgentSessionRegistry();

// Start a session
const session = registry.startSession('The Observer', 4);
console.log(session.sessionId); // S-2025-01-04-observer-abc123

// Create messages within the session
const claim = registry.createClaim(session, {
  content: 'Research completed',
  confidence: 0.9,
  provenance: ['api_source']
});

// End the session
const contextMsg = registry.endSession(session, 'Completed research phase');
```

## API Reference

### `makeMessage(options)`

Create a validated VLP message.

```typescript
interface MessageOptions {
  type: VlpType;
  sender: string;
  content: string | Record<string, unknown>;
  confidence?: number;
  provenance?: (string | ProvenanceRef)[];
  keywords?: string[];
  receiver?: string;
  topic?: string;
  sessionId?: string;
  seq?: number;
  refersTo?: string | string[];
  payload?: Record<string, unknown>;
}
```

### `validateVlp(msg)`

Validate a VLP message against schema and semantic rules.

```typescript
interface ValidationResult {
  valid: boolean;
  errors: string[];
}
```

### Types

```typescript
type VlpType = 'claim' | 'evidence' | 'query' | 'response' | 'correction' | 'notice' | 'session_context';
type SafetyLevel = 'safe' | 'review' | 'block';

interface VlpMessage {
  id: string;
  protocol: string;
  type: VlpType;
  timestamp: string;
  sender: string;
  content: string | Record<string, unknown>;
  confidence: number;
  safety: Safety;
  // ... see types.ts for full definition
}
```

## License

MIT
