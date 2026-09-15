"""Optional YAML-based severity configuration loader.

Lets ops/users override severities at deploy time without touching code:

    # config.yaml
    severity_overrides:
      DB_CONN_LOST: CRITICAL
      CACHE_MISS: WARNING

Requires PyYAML (`pip install errorkit[yaml]`); only imported when this
loader is actually used, so the core package stays dependency-light.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .registry import ErrorRegistry


def load_config(registry: ErrorRegistry, path: str | Path) -> None:
    import yaml

    data: dict[str, Any] = yaml.safe_load(Path(path).read_text()) or {}
    overrides = data.get("severity_overrides", {})
    registry.configure_severities(overrides)
