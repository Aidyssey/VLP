/**
 * VLP v1.1 Agent Session Management
 */

import crypto from 'crypto';
import { makeMessage, nowIso } from './runtime.js';
import type { VlpMessage } from './types.js';

/**
 * Represents an active VLP session for an agent.
 */
export class AgentSession {
  readonly agentName: string;
  readonly agentNumber: number;
  readonly sessionId: string;
  readonly startedAt: string;
  private _seq: number = 0;

  constructor(agentName: string, agentNumber: number = 0) {
    this.agentName = agentName;
    this.agentNumber = agentNumber;
    this.startedAt = nowIso();
    this.sessionId = this.generateSessionId(agentName);
  }

  private generateSessionId(agentName: string): string {
    const date = new Date().toISOString().split('T')[0];
    const slug = agentName
      .toLowerCase()
      .replace(/^the\s+/, '')
      .replace(/\s+/g, '-')
      .slice(0, 12);
    const shortId = crypto.randomBytes(3).toString('hex');
    return `S-${date}-${slug}-${shortId}`;
  }

  /**
   * Get next sequence number.
   */
  nextSeq(): number {
    this._seq += 1;
    return this._seq;
  }

  /**
   * Generate a session-scoped message ID.
   */
  messageId(prefix = 'MSG'): string {
    const suffix = this.sessionId.slice(-6);
    const seq = this.nextSeq().toString().padStart(4, '0');
    return `${prefix}-${suffix}-${seq}`;
  }

  /**
   * Get current sequence number without incrementing.
   */
  get seq(): number {
    return this._seq;
  }
}

/**
 * Registry for managing VLP sessions across agents.
 */
export class AgentSessionRegistry {
  private sessions: Map<string, AgentSession> = new Map();

  /**
   * Start a new VLP session for an agent.
   */
  startSession(agentName: string, agentNumber: number = 0): AgentSession {
    const session = new AgentSession(agentName, agentNumber);
    this.sessions.set(session.sessionId, session);
    return session;
  }

  /**
   * Get an active session by ID.
   */
  getSession(sessionId: string): AgentSession | undefined {
    return this.sessions.get(sessionId);
  }

  /**
   * End a session and create a session_context message.
   */
  endSession(session: AgentSession, summary = ''): VlpMessage {
    const msg = makeMessage({
      type: 'session_context',
      sender: session.agentName,
      content: summary || `Session ended for ${session.agentName}`,
      sessionId: session.sessionId,
      id: session.messageId('CTX'),
      seq: session.nextSeq(),
      confidence: 1.0,
      provenance: ['agent_session', `agent_${session.agentNumber}`],
      payload: {
        agent_number: session.agentNumber,
        started_at: session.startedAt,
        ended_at: nowIso(),
        total_messages: session.seq
      }
    });

    this.sessions.delete(session.sessionId);
    return msg;
  }

  /**
   * Create a claim message within a session context.
   */
  createClaim(
    session: AgentSession,
    options: {
      content: string;
      confidence?: number;
      provenance?: string[];
      keywords?: string[];
      [key: string]: unknown;
    }
  ): VlpMessage {
    const { content, confidence = 0.9, ...rest } = options;

    return makeMessage({
      type: 'claim',
      sender: session.agentName,
      content,
      sessionId: session.sessionId,
      id: session.messageId('CLM'),
      seq: session.nextSeq(),
      confidence,
      ...rest
    });
  }
}

// Global registry instance
let _registry: AgentSessionRegistry | null = null;

/**
 * Get or create the global session registry.
 */
export function getRegistry(): AgentSessionRegistry {
  if (!_registry) {
    _registry = new AgentSessionRegistry();
  }
  return _registry;
}
