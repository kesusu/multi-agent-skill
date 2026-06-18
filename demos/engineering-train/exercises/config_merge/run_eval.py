import copy
import importlib
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python run_eval.py <attempt_dir>")
        return 2

    sys.path.insert(0, sys.argv[1])
    merge_config = importlib.import_module("config_merge").merge_config

    failures = []

    def check(name, base, override, expected):
        original_base = copy.deepcopy(base)
        original_override = copy.deepcopy(override)
        try:
            actual = merge_config(base, override)
        except Exception as exc:
            failures.append(f"{name}: raised {type(exc).__name__}: {exc}")
            return
        if actual != expected:
            failures.append(f"{name}: got {actual!r}, expected {expected!r}")
        if base != original_base:
            failures.append(f"{name}: mutated base")
        if override != original_override:
            failures.append(f"{name}: mutated override")

        actual_mutables = _mutable_ids(actual)
        shared_base = actual_mutables & _mutable_ids(base)
        shared_override = actual_mutables & _mutable_ids(override)
        if shared_base:
            failures.append(f"{name}: result shares mutable objects with base")
        if shared_override:
            failures.append(f"{name}: result shares mutable objects with override")

    check(
        "flat replace and add",
        {"debug": False, "port": 8000},
        {"debug": True, "host": "localhost"},
        {"debug": True, "port": 8000, "host": "localhost"},
    )
    check(
        "recursive merge",
        {"db": {"host": "old", "port": 5432}, "cache": True},
        {"db": {"host": "new"}},
        {"db": {"host": "new", "port": 5432}, "cache": True},
    )
    check(
        "nested delete",
        {"a": {"b": 1, "c": 2}, "x": 3},
        {"a": {"b": None}},
        {"a": {"c": 2}, "x": 3},
    )
    check(
        "top delete and missing delete",
        {"a": 1, "b": 2},
        {"a": None, "missing": None},
        {"b": 2},
    )
    check(
        "list replace",
        {"items": [1, 2], "meta": {"tags": ["a"]}},
        {"items": [3], "meta": {"tags": ["b", "c"]}},
        {"items": [3], "meta": {"tags": ["b", "c"]}},
    )
    check(
        "dict scalar replacement",
        {"a": {"nested": True}, "b": 1},
        {"a": "value", "b": {"nested": False}},
        {"a": "value", "b": {"nested": False}},
    )

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS")
    return 0


def _mutable_ids(value):
    ids = set()
    if isinstance(value, dict):
        ids.add(id(value))
        for item in value.values():
            ids.update(_mutable_ids(item))
    elif isinstance(value, list):
        ids.add(id(value))
        for item in value:
            ids.update(_mutable_ids(item))
    return ids


if __name__ == "__main__":
    raise SystemExit(main())

