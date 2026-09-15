from dataclasses import dataclass, field
from typing import Any, Optional

from .severity import Severity


@dataclass(frozen=True)
class ErrorDef:
    """A single catalog entry. Immutable once registered — severity is
    overridden separately in the registry, not mutated here, so the
    original definition (as shipped by a plugin) stays intact."""

    code: str
    message: str
    default_severity: Severity
    tags: tuple[str, ...] = field(default_factory=tuple)
    source: Optional[str] = None  # which package/plugin registered this

    def format(self, **ctx: Any) -> str:
        try:
            return self.message.format(**ctx)
        except (KeyError, IndexError):
            # Missing context shouldn't blow up the error path itself.
            return self.message
