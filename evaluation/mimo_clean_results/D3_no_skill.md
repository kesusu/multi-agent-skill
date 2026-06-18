# Session 3 — D3 配置热更新 (无 Skill)

## 任务

实现一个配置热更新机制。

## 实现

### hotreload.py

```python
#!/usr/bin/env python3
"""配置热更新机制 — 监听 JSON 配置文件变更，自动重载 + 校验 + 回调通知。"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


@dataclass
class FieldRule:
    """单个字段的校验规则"""
    field_path: str
    expected_type: type = None
    required: bool = False
    min_value: Any = None
    max_value: Any = None
    allowed_values: list = None


class ConfigValidator:
    """配置校验器"""
    def __init__(self, rules=None):
        self.rules = rules or []

    def add_rule(self, rule):
        self.rules.append(rule)
        return self

    def validate(self, config):
        errors = []
        for rule in self.rules:
            value = _get_nested(config, rule.field_path)
            exists = value is not None
            if rule.required and not exists:
                errors.append(f"必填字段缺失: {rule.field_path}")
                continue
            if not exists:
                continue
            if rule.expected_type and not isinstance(value, rule.expected_type):
                errors.append(f"{rule.field_path}: 期望 {rule.expected_type.__name__}，收到 {type(value).__name__}")
                continue
            if rule.min_value is not None and isinstance(value, (int, float)):
                if value < rule.min_value:
                    errors.append(f"{rule.field_path}: {value} < 最小值 {rule.min_value}")
            if rule.max_value is not None and isinstance(value, (int, float)):
                if value > rule.max_value:
                    errors.append(f"{rule.field_path}: {value} > 最大值 {rule.max_value}")
            if rule.allowed_values is not None:
                if value not in rule.allowed_values:
                    errors.append(f"{rule.field_path}: {value} 不在允许值 {rule.allowed_values} 中")
        return len(errors) == 0, errors


def _get_nested(data, path):
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


ConfigChangeCallback = Callable[[dict, dict], None]


class ConfigWatcher:
    """配置文件热更新器"""
    def __init__(self, filepath, validator=None, poll_interval=1.0):
        self.filepath = os.path.abspath(filepath)
        self.validator = validator
        self.poll_interval = poll_interval
        self._config = None
        self._last_mtime = 0
        self._callbacks = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None
        self._load()

    def get(self):
        with self._lock:
            return dict(self._config) if self._config else {}

    def on_change(self, callback):
        self._callbacks.append(callback)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=3)

    def _load(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                new_config = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            print(f"配置加载失败：{e}")
            return False
        if self.validator:
            ok, errors = self.validator.validate(new_config)
            if not ok:
                print(f"配置校验失败：{'；'.join(errors)}")
                return False
        with self._lock:
            old_config = self._config
            self._config = new_config
            self._last_mtime = os.path.getmtime(self.filepath)
        if old_config is not None:
            for cb in self._callbacks:
                try:
                    cb(new_config, old_config)
                except Exception as e:
                    print(f"配置变更回调异常：{e}")
        return True

    def _watch_loop(self):
        while not self._stop_event.is_set():
            try:
                current_mtime = os.path.getmtime(self.filepath)
                if current_mtime != self._last_mtime:
                    success = self._load()
                    if success:
                        print("配置重新加载成功")
                    else:
                        print("配置重新加载失败，保留上一版配置")
            except FileNotFoundError:
                print(f"配置文件不存在，保留上一版配置")
            self._stop_event.wait(self.poll_interval)
```

## 测试结果

```
============================================================
配置热更新演示
============================================================

1. 初始配置加载成功:
   server.host = 0.0.0.0
   server.port = 8080
   database.url = postgresql://localhost:5432/mydb

2. 校验正确配置:
   结果: 通过 []

3. 校验错误配置:
   结果: 失败
   - server.host: 期望 str，收到 int
   - server.port: 99999 > 最大值 65535
   - database.pool_size: 200 > 最大值 100
   - logging.level: VERBOSE 不在允许值 ['DEBUG', 'INFO', 'WARNING', 'ERROR'] 中

4. 模拟配置文件变更:
   新配置 port = 9090

5. 模拟配置文件损坏（回退测试）:
   加载结果: 失败（预期行为）
   配置保留: 是

6. 启动/停止监听线程:
   线程存活: True → 停止后 False

全部演示通过
```

## 功能覆盖

- [x] 配置文件（JSON）变更时自动重新加载（轮询 + mtime 检测）
- [x] 支持配置校验（类型、范围、必填项、枚举值）
- [x] 配置变更通知（回调机制，支持多个回调）
- [x] 加载失败时回退到上一版配置
- [x] 线程安全（threading.Lock）
- [x] 启动/停止后台监听线程
