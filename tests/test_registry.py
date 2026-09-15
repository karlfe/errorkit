import pytest

from errorkit import ErrorDef, ErrorRegistry, Severity


def make_registry() -> ErrorRegistry:
    reg = ErrorRegistry()
    reg.register(
        ErrorDef(
            code="CACHE_MISS",
            message="Cache miss for key {key}",
            default_severity=Severity.DEBUG,
        )
    )
    reg.register(
        ErrorDef(
            code="DB_CONN_LOST",
            message="Lost connection to {host}",
            default_severity=Severity.CRITICAL,
        )
    )
    return reg


def test_severity_from_name():
    assert Severity.from_name("critical") is Severity.CRITICAL
    with pytest.raises(ValueError):
        Severity.from_name("not_a_level")


def test_register_rejects_duplicates():
    reg = make_registry()
    with pytest.raises(ValueError):
        reg.register(
            ErrorDef(code="CACHE_MISS", message="dup", default_severity=Severity.INFO)
        )


def test_default_severity_before_override():
    reg = make_registry()
    assert reg.effective_severity("CACHE_MISS") is Severity.DEBUG


def test_severity_override():
    reg = make_registry()
    reg.set_severity("CACHE_MISS", Severity.WARNING)
    assert reg.effective_severity("CACHE_MISS") is Severity.WARNING
    # original definition is untouched
    assert reg.get("CACHE_MISS").default_severity is Severity.DEBUG


def test_override_unknown_code_raises():
    reg = make_registry()
    with pytest.raises(KeyError):
        reg.set_severity("NOPE", Severity.WARNING)


def test_configure_severities_bulk():
    reg = make_registry()
    reg.configure_severities({"CACHE_MISS": "ERROR", "DB_CONN_LOST": "WARNING"})
    assert reg.effective_severity("CACHE_MISS") is Severity.ERROR
    assert reg.effective_severity("DB_CONN_LOST") is Severity.WARNING
