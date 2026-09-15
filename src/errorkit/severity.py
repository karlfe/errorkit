from enum import IntEnum


class Severity(IntEnum):
    """Severity levels, deliberately aligned with stdlib `logging` levels
    so they interoperate with existing logging config/handlers."""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    @classmethod
    def from_name(cls, name: str) -> "Severity":
        try:
            return cls[name.upper()]
        except KeyError as exc:
            valid = ", ".join(s.name for s in cls)
            raise ValueError(f"Unknown severity {name!r}. Valid: {valid}") from exc
