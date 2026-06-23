import json
import os
import urllib.error
import urllib.request
from typing import Any


ABSENCE_BASE = os.environ.get("ABSENCE_BASE_URL", "").rstrip("/")
ABSENCE_KEY = os.environ.get("ABSENCE_KEY", "")


def fetch_absence_state(timeout: float = 2.5) -> dict[str, Any] | None:
    """Fetch current absence state from the external absence service.

    Silent failure is intentional: absence awareness should never block breath().
    """
    if not ABSENCE_BASE or not ABSENCE_KEY:
        return None

    url = f"{ABSENCE_BASE}/absence/state"
    req = urllib.request.Request(
        url,
        headers={
            "X-Absence-Key": ABSENCE_KEY,
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            if not raw.strip():
                return None
            return json.loads(raw)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def format_absence_state(state: dict[str, Any] | None) -> str:
    """Format absence state as a lightweight breath block."""
    if not state:
        return ""

    since = (
        state.get("since")
        or state.get("time_since_last_seen")
        or state.get("time_since")
        or state.get("last_seen_delta")
        or ""
    )
    stage = (
        state.get("absence_stage")
        or state.get("stage")
        or state.get("state")
        or ""
    )
    note = (
        state.get("note")
        or state.get("summary")
        or state.get("message")
        or ""
    )

    lines: list[str] = ["=== Absence Awareness ==="]

    if since:
        lines.append(f"距离上次见面：{since}")
    if stage:
        lines.append(f"阶段：{stage}")
    if note:
        lines.append(str(note))

    if len(lines) == 1:
        return ""

    return "\n".join(lines)