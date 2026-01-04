"""
Vigilith Language Protocol (VLP) v1.1

A structured protocol for accountable AI agent communication.
"""

from .runtime import (
    make_message,
    validate_vlp,
    new_id,
    now_iso,
    to_ndjson,
    from_ndjson,
)
from .sessions import (
    AgentSession,
    AgentSessionRegistry,
    get_registry,
)

__version__ = "1.1.0"
__all__ = [
    "make_message",
    "validate_vlp",
    "new_id",
    "now_iso",
    "to_ndjson",
    "from_ndjson",
    "AgentSession",
    "AgentSessionRegistry",
    "get_registry",
]
