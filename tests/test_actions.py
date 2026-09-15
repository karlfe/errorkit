from errorkit import ErrorDef, ErrorRegistry, Severity


def make_registry() -> ErrorRegistry:
    reg = ErrorRegistry()
    reg.register(
        ErrorDef(
            code="PAYMENT_DECLINED",
            message="Payment declined for {order_id}",
            default_severity=Severity.ERROR,
        )
    )
    return reg


def test_severity_action_fires():
    reg = make_registry()
    calls = []
    reg.on_severity(Severity.ERROR, lambda err, sev, ctx: calls.append((err.code, sev)))
    reg.trigger("PAYMENT_DECLINED", order_id="A1")
    assert calls == [("PAYMENT_DECLINED", Severity.ERROR)]


def test_code_action_fires_independent_of_severity():
    reg = make_registry()
    calls = []
    reg.on_code("PAYMENT_DECLINED", lambda err, sev, ctx: calls.append(ctx))
    reg.set_severity("PAYMENT_DECLINED", Severity.CRITICAL)  # severity changes...
    reg.trigger("PAYMENT_DECLINED", order_id="A1")
    assert calls == [{"order_id": "A1"}]  # ...code action still fires


def test_code_actions_run_before_severity_actions():
    reg = make_registry()
    order = []
    reg.on_severity(Severity.ERROR, lambda err, sev, ctx: order.append("severity"))
    reg.on_code("PAYMENT_DECLINED", lambda err, sev, ctx: order.append("code"))
    reg.trigger("PAYMENT_DECLINED", order_id="A1")
    assert order == ["code", "severity"]


def test_message_formatting_missing_context_is_safe():
    reg = make_registry()
    err = reg.get("PAYMENT_DECLINED")
    assert err.format() == "Payment declined for {order_id}"
    assert err.format(order_id="A1") == "Payment declined for A1"
