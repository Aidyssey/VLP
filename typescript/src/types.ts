/**
 * VLP v1.1 Type Definitions
 */

export type VlpType = 'claim' | 'evidence' | 'query' | 'response' | 'correction' | 'notice' | 'session_context';
export type SafetyLevel = 'safe' | 'review' | 'block';
export type Gate = 'pass' | 'review' | 'fail';

export interface Issue {
  code: string;
  detail?: string;
}

export interface Safety {
  level: SafetyLevel;
  issues: Issue[];
  requires_human?: boolean;
}

export interface ProvenanceRef {
  ref: string;
  kind?: 'url' | 'hash' | 'document' | 'api' | 'snapshot' | 'log' | 'excerpt' | 'other';
  hash?: string;
  excerpt?: string;
  fetched_at?: string;
}

export interface VlpMessage {
  id: string;
  protocol: string;
  type: VlpType;
  timestamp: string;
  session_id?: string | null;
  seq?: number | null;
  sender: string;
  receiver?: string | null;
  topic?: string | null;
  content: string | Record<string, unknown>;
  confidence: number;
  provenance?: (string | ProvenanceRef)[] | null;
  constraints?: string[] | null;
  safety: Safety;
  refers_to?: string | string[] | null;
  keywords?: string[] | null;
  payload?: Record<string, unknown> | null;
  _extras?: Record<string, unknown> | null;

  // Validator-computed fields (read-only)
  context_integrity?: number | null;
  context_depth?: number | null;
  context_debt?: number | null;
  gate?: Gate | null;

  [key: string]: unknown;
}

export interface MessageOptions {
  type: VlpType;
  sender: string;
  content: string | Record<string, unknown>;
  confidence?: number;
  provenance?: (string | ProvenanceRef)[];
  keywords?: string[];
  constraints?: string[];
  receiver?: string;
  topic?: string;
  sessionId?: string;
  seq?: number;
  refersTo?: string | string[];
  payload?: Record<string, unknown>;
  safety?: Safety;
  id?: string;
  timestamp?: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}
