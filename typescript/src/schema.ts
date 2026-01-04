/**
 * VLP v1.1 JSON Schema loader
 */

import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let _schema: Record<string, unknown> | null = null;

export function loadVlpSchema(): Record<string, unknown> {
  if (_schema) {
    return _schema;
  }

  // Try loading from package directory
  const schemaPath = join(__dirname, '..', '..', 'schema', 'vlp-1.1.json');

  try {
    const content = readFileSync(schemaPath, 'utf-8');
    _schema = JSON.parse(content);
    return _schema!;
  } catch {
    // Fallback: return inline schema
    return getInlineSchema();
  }
}

function getInlineSchema(): Record<string, unknown> {
  return {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Vigilith Language Protocol (VLP) v1.1",
    "type": "object",
    "additionalProperties": true,
    "required": ["id", "protocol", "type", "timestamp", "sender", "content", "confidence"],
    "properties": {
      "id": { "type": "string", "minLength": 3 },
      "protocol": { "type": "string", "const": "VLP/1.1" },
      "type": {
        "type": "string",
        "enum": ["claim", "evidence", "query", "response", "correction", "notice", "session_context"]
      },
      "timestamp": { "type": "string", "minLength": 10 },
      "session_id": { "type": ["string", "null"] },
      "seq": { "type": ["integer", "null"], "minimum": 0 },
      "sender": { "type": "string", "minLength": 1 },
      "receiver": { "type": ["string", "null"] },
      "topic": { "type": ["string", "null"] },
      "content": { "type": ["string", "object"] },
      "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
      "provenance": { "type": "array", "default": [] },
      "constraints": { "type": "array", "items": { "type": "string" }, "default": [] },
      "safety": {
        "type": "object",
        "properties": {
          "level": { "type": "string", "enum": ["safe", "review", "block"] },
          "issues": { "type": "array", "default": [] },
          "requires_human": { "type": "boolean" }
        },
        "required": ["level", "issues"]
      },
      "refers_to": {
        "oneOf": [
          { "type": "string" },
          { "type": "array", "items": { "type": "string" } },
          { "type": "null" }
        ]
      },
      "keywords": { "type": "array", "items": { "type": "string" }, "default": [] },
      "payload": { "type": ["object", "null"] },
      "_extras": { "type": "object" }
    }
  };
}
