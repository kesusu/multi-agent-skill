# Config Merge Evaluation Report

## Goal
Train Claude Code on nested data handling, deletion semantics, and immutability.

## Result (2026-05-10)
- claude_attempt: PASS
- codex_attempt: PASS

## Implementation Strategy
- `merge_config(base, override)`: deepcopy base, then recursive merge
- Recursive rules: both dict → recurse; override=None → delete key; otherwise replace with deepcopy

## Evaluator Checks
- Recursive merge, nested deletion, top-level deletion
- List replacement, scalar/dict replacement in both directions
- No mutation of inputs
- No shared mutable dict/list objects in returned result (via `_mutable_ids()` id() intersection)

## Training Lesson
Nested data tasks should test both value equality AND object aliasing, because a solution can return the right shape while still leaking mutable references from the inputs.
