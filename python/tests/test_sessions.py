"""Tests for VLP session management."""

import pytest
from vlp.sessions import AgentSession, AgentSessionRegistry, get_registry


class TestAgentSession:
    def test_session_id_format(self):
        session = AgentSession("The Observer", 4)
        assert session.session_id.startswith("S-")
        assert "observer" in session.session_id
        assert len(session.session_id.split("-")) == 4

    def test_seq_increments(self):
        session = AgentSession("Test", 1)
        assert session.next_seq() == 1
        assert session.next_seq() == 2
        assert session.next_seq() == 3

    def test_message_id_format(self):
        session = AgentSession("Test", 1)
        msg_id = session.message_id("CLM")
        assert msg_id.startswith("CLM-")
        assert len(msg_id.split("-")) == 3

    def test_message_id_increments_seq(self):
        session = AgentSession("Test", 1)
        id1 = session.message_id("MSG")
        id2 = session.message_id("MSG")
        # Extract sequence numbers
        seq1 = int(id1.split("-")[-1])
        seq2 = int(id2.split("-")[-1])
        assert seq2 == seq1 + 1


class TestAgentSessionRegistry:
    def test_start_session(self):
        registry = AgentSessionRegistry()
        session = registry.start_session("The Observer", 4)
        assert session.agent_name == "The Observer"
        assert session.agent_number == 4

    def test_get_session(self):
        registry = AgentSessionRegistry()
        session = registry.start_session("Test", 1)
        retrieved = registry.get_session(session.session_id)
        assert retrieved is session

    def test_get_unknown_session(self):
        registry = AgentSessionRegistry()
        result = registry.get_session("nonexistent")
        assert result is None

    def test_end_session(self):
        registry = AgentSessionRegistry()
        session = registry.start_session("Test", 1)
        session_id = session.session_id

        msg = registry.end_session(session, "Completed successfully")

        assert msg["type"] == "session_context"
        assert msg["sender"] == "Test"
        assert msg["content"] == "Completed successfully"
        assert msg["payload"]["agent_number"] == 1

        # Session should be removed
        assert registry.get_session(session_id) is None

    def test_create_claim(self):
        registry = AgentSessionRegistry()
        session = registry.start_session("Test", 1)

        claim = registry.create_claim(
            session,
            content="Test claim",
            confidence=0.85,
            provenance=["source"]
        )

        assert claim["type"] == "claim"
        assert claim["sender"] == "Test"
        assert claim["content"] == "Test claim"
        assert claim["confidence"] == 0.85
        assert claim["session_id"] == session.session_id


class TestGlobalRegistry:
    def test_get_registry_singleton(self):
        reg1 = get_registry()
        reg2 = get_registry()
        assert reg1 is reg2
