"""The only shared file. Everything else is standalone.

Replaces a test framework: run a session file and read the PASS/FAIL lines.
"""


def check(label, actual, expected):
    if actual == expected:
        print(f"  PASS  {label}")
        return True
    print(f"  FAIL  {label}")
    print(f"        expected {expected!r}")
    print(f"        got      {actual!r}")
    return False


def check_raises(label, exception_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exception_type:
        print(f"  PASS  {label}")
        return True
    except Exception as exc:                      # noqa: BLE001
        print(f"  FAIL  {label} (raised {type(exc).__name__})")
        return False
    print(f"  FAIL  {label} (nothing raised)")
    return False
