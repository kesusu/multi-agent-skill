import importlib
import sys


VALID_CASES = [
    ("00:00", 0),
    ("02:03", 123),
    (" 10:05 ", 605),
    ("1:02:03", 3723),
    ("0:00:59", 59),
    ("1h", 3600),
    ("2 hours", 7200),
    ("1h 30m", 5400),
    ("1h30m", 5400),
    ("2 minutes 10 seconds", 130),
    ("45s", 45),
    ("5m 2h", 7500),
]

INVALID_CASES = [
    "",
    "   ",
    "10",
    "-1m",
    "1.5h",
    "1:2:3:4",
    "1:60",
    "1:00:60",
    "1:60:00",
    "1h 2h",
    "1m 30 minutes",
    "1d",
    "abc",
    "1 h",
    "h1",
    "1hour30",
    "2hours",
    "10seconds",
]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python run_eval.py <attempt_dir>")
        return 2

    sys.path.insert(0, sys.argv[1])
    parse_duration = importlib.import_module("duration_parser").parse_duration

    failures = []
    for text, expected in VALID_CASES:
        try:
            actual = parse_duration(text)
        except Exception as exc:
            failures.append(f"{text!r}: raised {type(exc).__name__}, expected {expected}")
            continue
        if actual != expected:
            failures.append(f"{text!r}: got {actual}, expected {expected}")

    for text in INVALID_CASES:
        try:
            actual = parse_duration(text)
        except ValueError:
            continue
        except Exception as exc:
            failures.append(f"{text!r}: raised {type(exc).__name__}, expected ValueError")
        else:
            failures.append(f"{text!r}: returned {actual}, expected ValueError")

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
