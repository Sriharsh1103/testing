"""Decides active vs idle polling frequency — pure function, no I/O.

Gold's highest volume/volatility window is the London-NY session overlap
(~12:00-16:00 UTC). Outside that window we poll less often to save API calls.
"""

from datetime import datetime, timezone
from typing import Optional

ACTIVE_SESSION_START_UTC = 12
ACTIVE_SESSION_END_UTC = 16


def is_active_session(now: Optional[datetime] = None) -> bool:
    now = now or datetime.now(timezone.utc)
    return ACTIVE_SESSION_START_UTC <= now.hour < ACTIVE_SESSION_END_UTC
