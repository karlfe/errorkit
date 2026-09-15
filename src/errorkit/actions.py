import logging
import sys
from typing import Any

from .models import ErrorDef
from .severity import Severity

logger = logging.getLogger("errorkit")


def log_action(err: ErrorDef, severity: Severity, ctx: dict[str, Any]) -> None:
    logger.log(int(severity), "[%s] %s", err.code, err.format(**ctx))


def print_action(err: ErrorDef, severity: Severity, ctx: dict[str, Any]) -> None:
    print(f"[{severity.name}] {err.code}: {err.format(**ctx)}", file=sys.stderr)


def raise_action(err: ErrorDef, severity: Severity, ctx: dict[str, Any]) -> None:
    raise RuntimeError(f"{err.code}: {err.format(**ctx)}")


def exit_action(err: ErrorDef, severity: Severity, ctx: dict[str, Any]) -> None:
    print_action(err, severity, ctx)
    sys.exit(1)
