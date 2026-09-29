"""Small reusable helper functions shared across CLI, config, and UI code.

Anything used in 2+ places belongs here instead of being duplicated inline.
"""


def mask_secret(value: str, visible: int = 4) -> str:
    """Show only the first `visible` chars of a secret, for safe display."""
    if not value:
        return ""
    return f"{value[:visible]}••••"


def key_status(value: str) -> str:
    """Human-readable SET/MISSING status for a config value."""
    return "SET" if value else "MISSING"
