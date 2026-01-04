/**
 * VLP v1.1 Runtime - Message creation and validation
 */

import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import crypto from 'crypto';
import { loadVlpSchema } from './schema.js';
import type { VlpMessage, MessageOptions, ValidationResult, Safety } from './types.js';

const ajv = new Ajv({ allErrors: true, strict: false });
addFormats(ajv);

const schema = loadVlpSchema();
const validateSchema = ajv.compile(schema);

/**
 * Generate a unique message ID.
 */
export function newId(prefix = 'MSG'): string {
  return `${prefix}${crypto.randomBytes(4).toString('hex')}`;
}

/**
 * Generate current UTC timestamp in ISO 8601 format.
 */
export function nowIso(): string {
  return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

/**
 * Normalize value to array.
 */
function asList<T>(v: T | T[] | null | undefined): T[] {
  if (v === null || v === undefined) return [];
  if (Array.isArray(v)) return v;
  return [v];
}

/**
 * Validate VLP semantic rules ("Truth Serum").
 */
function semanticValidate(msg: VlpMessage): ValidationResult {
  const errors: string[] = [];

  const t = msg.type?.toLowerCase() ?? '';
  if (t !== msg.type) {
    errors.push('type must be lowercase');
  }

  if (msg.confidence === undefined || msg.confidence === null) {
    errors.push('confidence is required');
  }

  const conf = msg.confidence ?? 0;
  const prov = asList(msg.provenance);
  const safetyLevel = msg.safety?.level ?? 'safe';
  const refersTo = msg.refers_to;

  // Evidence rules
  if (t === 'evidence') {
    if (!refersTo) {
      errors.push('evidence messages must include refers_to');
    }
    if (prov.length === 0) {
      errors.push('evidence messages must include non-empty provenance');
    }
  }

  // Response/correction rules
  if (t === 'response' || t === 'correction') {
    if (!refersTo) {
      errors.push(`${t} messages must include refers_to`);
    }
  }

  // High confidence must be earned
  if (conf >= 0.9 && prov.length === 0 && safetyLevel !== 'review') {
    errors.push('confidence >= 0.9 requires provenance or safety.level=review');
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Validate a VLP message against schema and semantic rules.
 */
export function validateVlp(msg: Record<string, unknown>): ValidationResult {
  const schemaValid = validateSchema(msg);

  if (!schemaValid) {
    const errors = (validateSchema.errors ?? []).map(e =>
      `${e.instancePath || '/'}: ${e.message}`
    );
    return { valid: false, errors };
  }

  return semanticValidate(msg as VlpMessage);
}

/**
 * Create a validated VLP message.
 */
export function makeMessage(options: MessageOptions): VlpMessage {
  const {
    type,
    sender,
    content,
    confidence = 1.0,
    provenance = [],
    keywords = [],
    constraints = [],
    receiver,
    topic,
    sessionId,
    seq,
    refersTo,
    payload,
    safety: inputSafety,
    id,
    timestamp
  } = options;

  const t = type.toLowerCase() as VlpMessage['type'];
  const provList = asList(provenance);
  const constraintsList = asList(constraints);

  // Normalize keywords
  const keywordsList = asList(keywords)
    .filter((k): k is string => typeof k === 'string' && k.trim() !== '')
    .map(k => k.toLowerCase().trim())
    .filter((k, i, arr) => arr.indexOf(k) === i); // dedupe

  // Initialize safety
  let safety: Safety = inputSafety ?? { level: 'safe', issues: [] };
  if (!safety.issues) {
    safety.issues = [];
  }

  // Auto-escalate high confidence without provenance
  if (confidence >= 0.9 && provList.length === 0 && safety.level !== 'review') {
    safety = {
      ...safety,
      level: 'review',
      issues: [
        ...safety.issues,
        {
          code: 'missing_provenance_high_confidence',
          detail: 'confidence >= 0.9 without provenance'
        }
      ]
    };
  }

  const msg: VlpMessage = {
    id: id ?? newId(),
    protocol: 'VLP/1.1',
    type: t,
    timestamp: timestamp ?? nowIso(),
    session_id: sessionId ?? null,
    seq: seq ?? null,
    sender,
    receiver: receiver ?? null,
    topic: topic ?? null,
    content,
    confidence,
    provenance: provList,
    constraints: constraintsList,
    safety,
    refers_to: refersTo ?? null,
    keywords: keywordsList,
    payload: payload ?? null,
    _extras: {}
  };

  const result = validateVlp(msg);
  if (!result.valid) {
    throw new Error(`VLP validation failed: ${result.errors.join(', ')}`);
  }

  return msg;
}

/**
 * Convert messages to NDJSON format.
 */
export function toNdjson(messages: VlpMessage[]): string {
  return messages.map(m => JSON.stringify(m)).join('\n');
}

/**
 * Parse NDJSON text to messages.
 */
export function fromNdjson(text: string): VlpMessage[] {
  return text
    .split('\n')
    .filter(line => line.trim())
    .map(line => JSON.parse(line) as VlpMessage);
}
