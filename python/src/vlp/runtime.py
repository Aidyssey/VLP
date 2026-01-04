"""
VLP v1.1 Runtime - Message creation and validation.
"""

from __future__ import annotations

import datetime
import json
import uuid
from typing import Any, Dict, List, Optional, Tuple

from jsonschema import ValidationError, validate

from .schema import vlp_1_1


def new_id(prefix: str = "MSG") -> str:
    """Generate a unique message ID."""
    return f"{prefix}{uuid.uuid4().hex[:8]}"


def now_iso() -> str:
    """Generate current UTC timestamp in ISO 8601 format."""
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_list(v: Any) -> List[Any]:
    """Normalize value to list."""
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def _semantic_validate(msg: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate VLP semantic rules ("Truth Serum").

    Returns (ok, error_message).
    """
    t = str(msg.get("type") or "").strip()
    if t != t.lower():
        return False, "type must be lowercase"

    conf = msg.get("confidence", None)
    if conf is None:
        return False, "confidence is required"

    try:
        conf_f = float(conf)
    except Exception:
        return False, "confidence must be a number"

    prov = msg.get("provenance", [])
    prov_list = prov if isinstance(prov, list) else []
    safety = msg.get("safety") if isinstance(msg.get("safety"), dict) else {"level": "safe", "issues": []}
    safety_level = str((safety or {}).get("level") or "safe")

    refers_to = msg.get("refers_to")

    # Evidence rules: must have refers_to and provenance
    if t == "evidence":
        if not refers_to:
            return False, "evidence messages must include refers_to"
        if not prov_list:
            return False, "evidence messages must include non-empty provenance"

    # Response/correction rules: must have refers_to
    if t in ("response", "correction"):
        if not refers_to:
            return False, f"{t} messages must include refers_to"

    # High confidence must be earned (provenance) or explicitly flagged for review
    if conf_f >= 0.9 and not prov_list and safety_level != "review":
        return False, "confidence >= 0.9 requires provenance or safety.level=review"

    return True, None


def validate_vlp(msg: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate a VLP message against schema and semantic rules.

    Returns (ok, error_message).
    """
    try:
        validate(instance=msg, schema=vlp_1_1)
    except ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

    ok, err = _semantic_validate(msg)
    return ok, err


def make_message(
    type_: str,
    sender: str,
    content: Any,
    **kw: Any,
) -> Dict[str, Any]:
    """
    Create a validated VLP message.

    Args:
        type_: Message type (claim, evidence, query, response, correction, notice, session_context)
        sender: Agent identifier
        content: Message content (string or dict)
        **kw: Optional fields (confidence, provenance, keywords, receiver, topic, etc.)

    Returns:
        Validated VLP message dict

    Raises:
        ValueError: If message fails validation
    """
    t = str(type_).strip().lower()
    confidence = float(kw.get("confidence", 1.0))
    provenance = kw.get("provenance", [])
    provenance_list = provenance if isinstance(provenance, list) else _as_list(provenance)
    constraints = kw.get("constraints", [])
    constraints_list = constraints if isinstance(constraints, list) else _as_list(constraints)

    safety = kw.get("safety", {"level": "safe", "issues": []})
    if not isinstance(safety, dict):
        safety = {"level": "safe", "issues": []}
    if "issues" not in safety or not isinstance(safety.get("issues"), list):
        safety["issues"] = []
    if "level" not in safety:
        safety["level"] = "safe"

    # v1.1 behavior: if sender claims high confidence without provenance, auto-escalate to review
    if confidence >= 0.9 and not provenance_list and str(safety.get("level")) != "review":
        safety["level"] = "review"
        safety["issues"].append({
            "code": "missing_provenance_high_confidence",
            "detail": "confidence >= 0.9 without provenance"
        })

    # Keywords for searchable agent memory
    keywords = kw.get("keywords", [])
    keywords_list = keywords if isinstance(keywords, list) else _as_list(keywords)
    # Normalize keywords: lowercase, strip whitespace, dedupe
    keywords_list = list(dict.fromkeys(
        k.lower().strip() for k in keywords_list if isinstance(k, str) and k.strip()
    ))

    msg: Dict[str, Any] = {
        "id": kw.get("id") or new_id(),
        "protocol": "VLP/1.1",
        "type": t,
        "timestamp": kw.get("timestamp") or now_iso(),
        "session_id": kw.get("session_id"),
        "seq": kw.get("seq"),
        "sender": sender,
        "receiver": kw.get("receiver"),
        "topic": kw.get("topic"),
        "content": content,
        "confidence": confidence,
        "provenance": provenance_list,
        "constraints": constraints_list,
        "safety": safety,
        "refers_to": kw.get("refers_to"),
        "keywords": keywords_list,
        "payload": kw.get("payload"),
        "_extras": kw.get("_extras", {}),
    }

    ok, err = validate_vlp(msg)
    if not ok:
        raise ValueError(f"VLP validation failed: {err}")
    return msg


def to_ndjson(messages: List[Dict[str, Any]]) -> str:
    """Convert list of messages to NDJSON format."""
    return "\n".join(json.dumps(m, ensure_ascii=False) for m in messages)


def from_ndjson(text: str) -> List[Dict[str, Any]]:
    """Parse NDJSON text to list of messages."""
    out: List[Dict[str, Any]] = []
    for line in (text or "").splitlines():
        if not line.strip():
            continue
        out.append(json.loads(line))
    return out
