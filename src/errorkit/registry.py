from __future__ import annotations

from collections import defaultdict
from importlib.metadata import entry_points
from typing import Any, Callable

from . import actions as default_actions
from .models import ErrorDef
from .severity import Severity

Action = Callable[[ErrorDef, Severity, dict], None]

PLUGIN_GROUP = "errorkit.errors"


class ErrorRegistry:
    """Central, extendable catalog of error definitions with
    severity-based and error-specific actions.

    Three independent axes:
      1. Catalog    -- what error codes exist, and their message/default severity.
                       Extended by any installed package via entry points.
      2. Severity   -- user-settable per code, overriding the shipped default.
      3. Actions    -- what happens when an error fires: wired per severity
                       level (broad) and/or per error code (specific,
                       runs first).
    """

    def __init__(self) -> None:
        self._catalog: dict[str, ErrorDef] = {}
        self._severity_overrides: dict[str, Severity] = {}
        self._severity_actions: dict[Severity, list[Action]] = defaultdict(list)
        self._code_actions: dict[str, list[Action]] = defaultdict(list)

    # ---- registration ---------------------------------------------------

    def register(self, err: ErrorDef) -> None:
        if err.code in self._catalog:
            raise ValueError(f"Duplicate error code: {err.code}")
        self._catalog[err.code] = err

    def register_many(self, errs: list[ErrorDef]) -> None:
        for e in errs:
            self.register(e)

    def load_plugins(self, group: str = PLUGIN_GROUP) -> list[str]:
        """Discover error definitions contributed by other installed
        packages via Python entry points.

        Each plugin exposes a callable under the entry point group with
        signature `register(registry: ErrorRegistry) -> None`. Returns
        the names of the plugins that were loaded.
        """
        loaded = []
        for ep in entry_points(group=group):
            register_fn = ep.load()
            register_fn(self)
            loaded.append(ep.name)
        return loaded

    # ---- severity configuration ------------------------------------------

    def set_severity(self, code: str, severity: Severity) -> None:
        """User-settable override for one error code, without touching
        the original definition (which may live in a third-party plugin)."""
        if code not in self._catalog:
            raise KeyError(f"Unknown error code: {code}")
        self._severity_overrides[code] = severity

    def configure_severities(self, overrides: dict[str, str]) -> None:
        """Bulk apply overrides, e.g. loaded from a config file:
        {"DB_CONN_LOST": "CRITICAL", "CACHE_MISS": "DEBUG"}"""
        for code, level_name in overrides.items():
            self.set_severity(code, Severity.from_name(level_name))

    def effective_severity(self, code: str) -> Severity:
        return self._severity_overrides.get(code, self._catalog[code].default_severity)

    # ---- actions ----------------------------------------------------------

    def on_severity(self, level: Severity, action: Action) -> None:
        """Run `action` whenever an error's *effective* severity equals
        this level."""
        self._severity_actions[level].append(action)

    def on_code(self, code: str, action: Action) -> None:
        """Run `action` whenever this specific error code fires. Code
        actions run before that error's severity-level actions."""
        self._code_actions[code].append(action)

    def use_default_actions(self) -> None:
        """Convenience wiring: log everything, hard-exit on CRITICAL."""
        for level in Severity:
            self.on_severity(level, default_actions.log_action)
        self.on_severity(Severity.CRITICAL, default_actions.exit_action)

    # ---- firing -------------------------------------------------------------

    def get(self, code: str) -> ErrorDef:
        return self._catalog[code]

    def trigger(self, code: str, **ctx: Any) -> None:
        err = self._catalog[code]
        severity = self.effective_severity(code)
        for action in self._code_actions.get(code, []):
            action(err, severity, ctx)
        for action in self._severity_actions.get(severity, []):
            action(err, severity, ctx)

    def all_codes(self) -> list[str]:
        return sorted(self._catalog)


# Shared instance so multiple modules/plugins can register into the same
# catalog without passing the object around explicitly.
registry = ErrorRegistry()
