"""
Demo: plugin discovery, a user-settable severity override, a
severity-wide action, and an error-specific action.

Setup (one-time), assuming errorkit-plugin-example lives in a sibling
directory (its own repo in real usage; installable from PyPI too):

    pip install -e .
    pip install -e ../errorkit-plugin-example

Run:
    python examples_demo.py
"""
from errorkit import ErrorRegistry, Severity


def page_oncall(err, severity, ctx):
    print(f"  -> paging on-call for {err.code} ({severity.name}): {ctx}")


def block_checkout(err, severity, ctx):
    print(f"  -> checkout blocked due to {err.code}: {ctx}")


def main() -> None:
    reg = ErrorRegistry()

    # 1. Extend: pull in every error definition contributed by installed
    #    plugins, without the host app knowing they exist in advance.
    loaded = reg.load_plugins()
    print(f"Loaded plugins: {loaded}")
    print(f"Known error codes: {reg.all_codes()}\n")

    # 2. Wire baseline actions: log everything, hard-exit on CRITICAL.
    reg.use_default_actions()

    # 3. Severity-wide action: anything that becomes CRITICAL pages on-call,
    #    regardless of which error code it was.
    reg.on_severity(Severity.CRITICAL, page_oncall)

    # 4. Error-specific action: independent of severity, always block
    #    checkout on a declined payment.
    reg.on_code("PAYMENT_DECLINED", block_checkout)

    # 5. User-settable severity override (could equally come from
    #    errorkit.config.load_config(reg, "config.yaml")).
    print("Default CACHE_MISS severity:", reg.effective_severity("CACHE_MISS").name)
    reg.set_severity("CACHE_MISS", Severity.WARNING)
    print("Overridden CACHE_MISS severity:", reg.effective_severity("CACHE_MISS").name)

    print("\n--- firing errors ---")
    reg.trigger("CACHE_MISS", key="user:42")
    reg.trigger("PAYMENT_DECLINED", order_id="A1002", reason="insufficient_funds")
    print("\n(DB_CONN_LOST is wired to exit_action - uncomment to see it end the process)")
    # reg.trigger("DB_CONN_LOST", host="db.internal", port=5432)


if __name__ == "__main__":
    main()
