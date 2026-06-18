# Config Merge Exercise

Implement `merge_config(base: dict, override: dict) -> dict` in `config_merge.py`.

Return a new dictionary that merges `override` into `base`.

Rules:

- Do not mutate `base` or `override`.
- If both values are dictionaries, merge them recursively.
- If the override value is `None`, delete that key from the result if present.
- Lists are replaced, not merged.
- Scalar values are replaced.
- New keys from `override` are added.
- If a `None` override targets a missing key, ignore it.

Important edge cases:

- Nested delete: `{"a": {"b": None}}` removes `b` from nested `a`.
- A dictionary in `base` replaced by scalar in `override` should become the scalar.
- A scalar in `base` replaced by dictionary in `override` should become the dictionary.
- Returned nested structures must not share mutable dict/list objects with either input.

