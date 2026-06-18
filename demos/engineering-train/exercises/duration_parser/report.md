# Duration Parser Evaluation Report

## Goal
Train Claude Code on parsing specs, edge cases, and validation-driven fixes.

## Result (2026-05-10)
- claude_attempt: PASS
- codex_attempt: PASS

## Implementation Strategy
- Colon format: regex `^\s*(\d+):(\d+)(?::(\d+))?\s*$` for MM:SS and HH:MM:SS
- Unit format: two-layer regex (_COMPACT_PATTERN for `1h30m`, _LONG_PATTERN for `2 hours`)
- Space policy: short units (h/m/s) no space between digit and unit; long units allow space
- Validation: coverage check, duplicate unit check, decimal check

## Training Lesson
Edge cases drive the value: empty string, negative, decimal, duplicate units, format boundaries. 30 test cases for a single function — the exercise's training value is in how "sharp" the boundaries are, not how big the task is.
