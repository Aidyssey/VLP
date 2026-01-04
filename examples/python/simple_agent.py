#!/usr/bin/env python3
"""
Simple VLP Agent Example

Demonstrates basic VLP message creation and session management.
"""

from vlp import make_message, validate_vlp, to_ndjson
from vlp.sessions import AgentSessionRegistry


def main():
    # Create a session registry
    registry = AgentSessionRegistry()

    # Start a new session
    session = registry.start_session("Example Agent", agent_number=99)
    print(f"Started session: {session.session_id}")

    # Create some claims within the session
    claims = []

    # First claim - starting work
    claim1 = registry.create_claim(
        session,
        content="Starting example workflow.",
        confidence=1.0,
        keywords=["example", "workflow", "start"]
    )
    claims.append(claim1)
    print(f"Created claim: {claim1['id']}")

    # Second claim - with provenance
    claim2 = registry.create_claim(
        session,
        content="Fetched data from external API.",
        confidence=0.9,
        provenance=["https://api.example.com/data"],
        keywords=["example", "api", "data"]
    )
    claims.append(claim2)
    print(f"Created claim: {claim2['id']}")

    # High confidence claim - will auto-escalate without provenance
    claim3 = make_message(
        "claim",
        sender=session.agent_name,
        content="High confidence assertion without provenance.",
        confidence=0.95,
        session_id=session.session_id,
        keywords=["example", "high-confidence"]
    )
    claims.append(claim3)
    print(f"Created claim: {claim3['id']}")
    print(f"  -> Safety level: {claim3['safety']['level']}")  # Will be 'review'

    # Evidence for a prior claim
    evidence = make_message(
        "evidence",
        sender=session.agent_name,
        content="API response verified against schema.",
        confidence=0.95,
        provenance=["schema_validation", "api_response_log"],
        refers_to=claim2["id"],
        session_id=session.session_id,
        keywords=["example", "evidence", "validation"]
    )
    claims.append(evidence)
    print(f"Created evidence: {evidence['id']}")

    # End the session
    context_msg = registry.end_session(
        session,
        summary="Example workflow completed successfully. Created 4 messages."
    )
    claims.append(context_msg)
    print(f"Session ended: {context_msg['id']}")

    # Output as NDJSON
    print("\n--- NDJSON Output ---")
    ndjson = to_ndjson(claims)
    print(ndjson)

    # Validate all messages
    print("\n--- Validation ---")
    for msg in claims:
        ok, err = validate_vlp(msg)
        status = "✓" if ok else f"✗ {err}"
        print(f"{msg['id']}: {status}")


if __name__ == "__main__":
    main()
