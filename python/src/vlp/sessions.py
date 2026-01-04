"""
VLP v1.1 Agent Session Management.

Provides session tracking for grouping related VLP messages.
"""

from __future__ import annotations

import datetime
import threading
import uuid
from typing import Any, Dict, Optional

from .runtime import make_message


class AgentSession:
    """
    Represents an active VLP session for an agent.

    Sessions group related messages with:
    - Unique session_id
    - Sequential message numbering
    - Session-scoped message IDs
    """

    def __init__(self, agent_name: str, agent_number: int = 0):
        """
        Initialize a new agent session.

        Args:
            agent_name: Human-readable agent name
            agent_number: Optional numeric identifier
        """
        self.agent_name = agent_name
        self.agent_number = agent_number
        self.session_id = self._generate_session_id(agent_name)
        self.started_at = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        self.seq = 0
        self._lock = threading.Lock()

    def _generate_session_id(self, agent_name: str) -> str:
        """Generate a unique session ID with agent prefix."""
        # Format: S-{date}-{agent_slug}-{short_uuid}
        date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        slug = agent_name.lower().replace("the ", "").replace(" ", "-")[:12]
        short_id = uuid.uuid4().hex[:6]
        return f"S-{date}-{slug}-{short_id}"

    def next_seq(self) -> int:
        """Get next sequence number (thread-safe)."""
        with self._lock:
            self.seq += 1
            return self.seq

    def message_id(self, prefix: str = "MSG") -> str:
        """Generate a session-scoped message ID."""
        return f"{prefix}-{self.session_id[-6:]}-{self.next_seq():04d}"


class AgentSessionRegistry:
    """
    Registry for managing VLP sessions across agents.

    Usage:
        registry = AgentSessionRegistry()
        session = registry.start_session("The Observer", 4)

        # Create claims within session
        claim = registry.create_claim(session, "Research completed", confidence=0.9)

        # End session with context
        registry.end_session(session, "Completed successfully")
    """

    def __init__(self):
        self._sessions: Dict[str, AgentSession] = {}
        self._lock = threading.Lock()

    def start_session(self, agent_name: str, agent_number: int = 0) -> AgentSession:
        """
        Start a new VLP session for an agent.

        Returns the session object with a unique session_id.
        """
        session = AgentSession(agent_name, agent_number)

        with self._lock:
            self._sessions[session.session_id] = session

        return session

    def get_session(self, session_id: str) -> Optional[AgentSession]:
        """Get an active session by ID."""
        with self._lock:
            return self._sessions.get(session_id)

    def end_session(self, session: AgentSession, summary: str = "") -> Dict[str, Any]:
        """
        End a session and create a session_context message.

        Returns the session_context VLP message.
        """
        msg = make_message(
            "session_context",
            sender=session.agent_name,
            content=summary or f"Session ended for {session.agent_name}",
            session_id=session.session_id,
            id=session.message_id("CTX"),
            seq=session.next_seq(),
            confidence=1.0,
            provenance=["agent_session", f"agent_{session.agent_number}"],
            payload={
                "agent_number": session.agent_number,
                "started_at": session.started_at,
                "ended_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
                "total_messages": session.seq,
            },
        )

        with self._lock:
            self._sessions.pop(session.session_id, None)

        return msg

    def create_claim(
        self,
        session: AgentSession,
        content: str,
        confidence: float = 0.9,
        **kw: Any,
    ) -> Dict[str, Any]:
        """Create a claim message within a session context."""
        return make_message(
            "claim",
            sender=session.agent_name,
            content=content,
            session_id=session.session_id,
            id=session.message_id("CLM"),
            seq=session.next_seq(),
            confidence=confidence,
            **kw,
        )


# Global registry instance
_registry: Optional[AgentSessionRegistry] = None


def get_registry() -> AgentSessionRegistry:
    """Get or create the global session registry."""
    global _registry
    if _registry is None:
        _registry = AgentSessionRegistry()
    return _registry
