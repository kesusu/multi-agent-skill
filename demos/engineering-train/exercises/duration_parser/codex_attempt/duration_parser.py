import re


def parse_duration(text: str) -> int:
    text = text.strip()
    if not text:
        raise ValueError("empty input")

    # Colon format: MM:SS or HH:MM:SS
    m = re.fullmatch(r'(\d+):(\d+)(?::(\d+))?', text)
    if m:
        a = int(m.group(1))
        b = int(m.group(2))
        c = int(m.group(3)) if m.group(3) else None
        if c is not None:
            # HH:MM:SS
            if b >= 60 or c >= 60:
                raise ValueError("minutes/seconds must be 0-59")
            return a * 3600 + b * 60 + c
        else:
            # MM:SS
            if b >= 60:
                raise ValueError("seconds must be 0-59")
            return a * 60 + b

    # Unit format
    # Short units (h/m/s): no space between digit and unit
    # Long units (hour/hours/minute/minutes/second/seconds): space allowed
    _COMPACT = re.compile(r'(\d+)([hms])')
    _LONG = re.compile(r'(\d+)\s+(hours?|minutes?|seconds?)')

    total = 0
    units_seen = []
    matched_spans = []

    # Try long forms first (they have priority due to space handling)
    for m in _LONG.finditer(text):
        val = int(m.group(1))
        unit = m.group(2).lower()
        matched_spans.append(m.span())
        if unit.startswith('h'):
            total += val * 3600
            units_seen.append('h')
        elif unit.startswith('m'):
            total += val * 60
            units_seen.append('m')
        elif unit.startswith('s'):
            total += val
            units_seen.append('s')

    # Mark matched regions
    covered = set()
    for start, end in matched_spans:
        for i in range(start, end):
            covered.add(i)

    # Try compact forms in non-covered regions
    remaining = ''.join(c for i, c in enumerate(text) if i not in covered)
    for m in _COMPACT.finditer(remaining):
        val = int(m.group(1))
        unit = m.group(2)
        if unit == 'h':
            total += val * 3600
        elif unit == 'm':
            total += val * 60
        elif unit == 's':
            total += val
        units_seen.append(unit)
        # Mark these chars as covered too
        orig_start = remaining.index(m.group(0))
        for i in range(orig_start, orig_start + len(m.group(0))):
            covered.add(i)

    # Check all non-whitespace chars are covered
    uncovered = ''.join(c for i, c in enumerate(text) if i not in covered and c.strip())
    if uncovered:
        raise ValueError(f"invalid input: {text!r}")

    if not total and total != 0:
        raise ValueError(f"invalid input: {text!r}")
    if not units_seen:
        raise ValueError(f"invalid input: {text!r}")

    # Duplicate units
    if len(units_seen) != len(set(units_seen)):
        raise ValueError(f"duplicate units in: {text!r}")

    return total
