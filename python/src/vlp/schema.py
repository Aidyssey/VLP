"""VLP v1.1 JSON Schema loader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

_DIR = Path(__file__).resolve().parent
_SCHEMA_PATH = _DIR / "vlp-1.1.json"


def _load_schema() -> Dict[str, Any]:
    """Load the VLP 1.1 JSON schema."""
    if _SCHEMA_PATH.exists():
        return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))

    # Fallback: look in parent schema directory
    alt_path = _DIR.parent.parent.parent / "schema" / "vlp-1.1.json"
    if alt_path.exists():
        return json.loads(alt_path.read_text(encoding="utf-8"))

    raise FileNotFoundError(f"VLP schema not found at {_SCHEMA_PATH} or {alt_path}")


vlp_1_1: Dict[str, Any] = _load_schema()
