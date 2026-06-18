# Session 3 — D3 配置热更新 · 无 Skill

## 任务

实现一个配置热更新机制。要求：
1. 配置文件（JSON）变更时自动重新加载
2. 支持配置校验（类型、范围、必填项）
3. 配置变更通知（回调机制）
4. 加载失败时回退到上一版配置

## 实现

创建了 `D3_config_hotreload/config_hotreload.py`。

### 核心架构

```
ConfigSchema  →  校验层（类型/范围/必填/嵌套）
ConfigManager →  核心管理者（加载/监控/回调/回退）
watch_loop    →  后台轮询线程（跨平台兼容）
```

### 关键设计决策

1. **轮询而非 inotify**：跨平台兼容（Windows/Linux/macOS），1秒轮询间隔足够实时
2. **自动 Schema 推断**：从初始配置自动生成校验规则，无需手写 schema
3. **deepcopy 隔离**：`config` 属性返回深拷贝，外部修改不影响内部状态
4. **回调在锁外执行**：防止回调死锁
5. **失败计数**：`_load_error_count` 追踪连续失败次数，便于监控告警

### 验证结果

6 项测试全部通过：

```
[PASS] Initial load works
[PASS] Nested get works
[PASS] Callback fires on change
[PASS] Invalid config rejected, fallback works
[PASS] Schema auto-generation works
[PASS] Config deep copy isolation works
```

### 用法示例

```python
from config_hotreload import ConfigManager

mgr = ConfigManager("config.json")
mgr.on_change(lambda new, old: print(f"Config changed!"))

mgr.start_watching()  # background thread
# ... edit config.json ...
mgr.stop_watching()
```

### 代码位置
- `D3_config_hotreload/config_hotreload.py` — 核心实现
- `D3_config_hotreload/test_hotreload.py` — 测试
- `D3_config_hotreload/config.json` — 示例配置
