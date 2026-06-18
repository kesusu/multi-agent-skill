import copy


def merge_config(base: dict, override: dict) -> dict:
    result = copy.deepcopy(base)
    _merge(result, override)
    return result


def _merge(target: dict, source: dict):
    for key, val in source.items():
        if val is None:
            target.pop(key, None)
        elif isinstance(val, dict) and isinstance(target.get(key), dict):
            _merge(target[key], val)
        else:
            target[key] = copy.deepcopy(val)
