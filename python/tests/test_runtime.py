"""Tests for VLP runtime."""

import pytest
from vlp import make_message, validate_vlp, new_id, now_iso, to_ndjson, from_ndjson


class TestNewId:
    def test_default_prefix(self):
        id_ = new_id()
        assert id_.startswith("MSG")
        assert len(id_) == 11  # MSG + 8 hex chars

    def test_custom_prefix(self):
        id_ = new_id("CLM")
        assert id_.startswith("CLM")


class TestNowIso:
    def test_format(self):
        ts = now_iso()
        assert ts.endswith("Z")
        assert "T" in ts
        assert len(ts) == 20  # YYYY-MM-DDTHH:MM:SSZ


class TestMakeMessage:
    def test_basic_claim(self):
        msg = make_message(
            "claim",
            sender="TestAgent",
            content="Test content",
            confidence=0.8
        )
        assert msg["type"] == "claim"
        assert msg["sender"] == "TestAgent"
        assert msg["content"] == "Test content"
        assert msg["confidence"] == 0.8
        assert msg["protocol"] == "VLP/1.1"

    def test_high_confidence_without_provenance_escalates(self):
        msg = make_message(
            "claim",
            sender="TestAgent",
            content="High confidence claim",
            confidence=0.95
        )
        assert msg["safety"]["level"] == "review"
        assert any(i["code"] == "missing_provenance_high_confidence" for i in msg["safety"]["issues"])

    def test_high_confidence_with_provenance_stays_safe(self):
        msg = make_message(
            "claim",
            sender="TestAgent",
            content="Proven claim",
            confidence=0.95,
            provenance=["source1", "source2"]
        )
        assert msg["safety"]["level"] == "safe"

    def test_keywords_normalized(self):
        msg = make_message(
            "claim",
            sender="TestAgent",
            content="Test",
            confidence=0.5,
            keywords=["Research", "  OKLAHOMA  ", "test", "test"]  # Duplicates + mixed case
        )
        assert msg["keywords"] == ["research", "oklahoma", "test"]

    def test_session_fields(self):
        msg = make_message(
            "claim",
            sender="TestAgent",
            content="Session test",
            confidence=0.5,
            session_id="S-2025-01-04-test-abc123",
            seq=5
        )
        assert msg["session_id"] == "S-2025-01-04-test-abc123"
        assert msg["seq"] == 5


class TestValidateVlp:
    def test_valid_message(self):
        msg = make_message("claim", "Test", "Content", confidence=0.5)
        ok, err = validate_vlp(msg)
        assert ok is True
        assert err is None

    def test_missing_confidence(self):
        msg = {
            "id": "MSG001",
            "protocol": "VLP/1.1",
            "type": "claim",
            "timestamp": "2025-01-04T10:00:00Z",
            "sender": "Test",
            "content": "Test"
        }
        ok, err = validate_vlp(msg)
        assert ok is False
        assert "confidence" in err.lower()

    def test_evidence_requires_refers_to(self):
        with pytest.raises(ValueError, match="refers_to"):
            make_message(
                "evidence",
                sender="Test",
                content="Evidence without ref",
                confidence=0.8,
                provenance=["source"]
            )

    def test_evidence_requires_provenance(self):
        with pytest.raises(ValueError, match="provenance"):
            make_message(
                "evidence",
                sender="Test",
                content="Evidence without provenance",
                confidence=0.8,
                refers_to="MSG001"
            )


class TestNdjson:
    def test_to_ndjson(self):
        msgs = [
            {"id": "MSG001", "content": "First"},
            {"id": "MSG002", "content": "Second"}
        ]
        result = to_ndjson(msgs)
        lines = result.strip().split("\n")
        assert len(lines) == 2

    def test_from_ndjson(self):
        text = '{"id": "MSG001"}\n{"id": "MSG002"}\n'
        msgs = from_ndjson(text)
        assert len(msgs) == 2
        assert msgs[0]["id"] == "MSG001"
        assert msgs[1]["id"] == "MSG002"

    def test_roundtrip(self):
        original = [
            make_message("claim", "Agent1", "Test1", confidence=0.5),
            make_message("claim", "Agent2", "Test2", confidence=0.6)
        ]
        ndjson = to_ndjson(original)
        parsed = from_ndjson(ndjson)
        assert len(parsed) == 2
        assert parsed[0]["sender"] == "Agent1"
        assert parsed[1]["sender"] == "Agent2"
