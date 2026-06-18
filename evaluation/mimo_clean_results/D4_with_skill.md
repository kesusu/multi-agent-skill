# Session 4 — D4 限流 (有 Skill)

## 任务

设计一个 Web API 限流中间件。

## 流程：/multi-agent 框架模式

### 0秒分流器
- Q1: 方案 → Q2: 否（分布式限流有复杂度）→ Q3: 不大 → **框架模式**

### 任务地图
- T1: 滑动窗口核心 → T2: HTTP 中间件 → T3: 批评家审查
- 角色：架构师+执行者（合并）、批评家

### 批评家审查结果

| 级别 | 编号 | 问题 | 修复 |
|---|---|---|---|
| 严重 | S1 | Redis member 多进程不唯一 | `uuid.uuid4()` 替代 `threading.get_ident()` |
| 严重 | S2 | FastAPI 中间件返回类型与文档不符 | 更新文档为 `app.add_middleware()` 用法 |
| 严重 | S3 | Retry-After 头/body 值不一致 | 统一用 `math.ceil()`，移除 +1 偏移 |
| 轻微 | M6 | WSGI headers 可能不可变 | `headers = list(headers)` 防御 |

### 修复摘要

1. **S1**: Redis member 改用 `uuid.uuid4().hex[:8]`，保证多进程部署下唯一
2. **S2**: 文档从 `app.middleware("http")(...)` 改为 `app.add_middleware()` 正确用法
3. **S3**: 所有 Retry-After 统一 `math.ceil(retry_after)`，body 和 header 一致
4. **M6**: WSGI `_start_response` 中 `headers = list(headers)` 防御不可变序列

## 实现

### rate_limiter.py 核心结构

```
1. 数据结构
   - RateLimitRule: 限流规则（维度、阈值、窗口、路径模式）
   - RateLimitResult: 检查结果（是否允许、剩余、重试时间）

2. 后端
   - MemoryBackend: 线程安全滑动窗口（有序时间戳 + Lock）
   - RedisBackend: 分布式滑动窗口（ZSET + Lua 脚本原子操作）

3. 限流器核心
   - SlidingWindowRateLimiter: 多规则匹配（优先级排序，任一拒绝即整体拒绝）

4. 框架封装
   - create_fastapi_middleware(): BaseHTTPMiddleware 方式
   - create_fastapi_dependency(): Depends 注入方式
   - WSGIRateLimitMiddleware: Flask/Django 兼容

5. 自测（6 组全部通过）
   - 滑动窗口基本逻辑
   - 规则匹配
   - 多规则组合
   - IP 隔离
   - 边界情况（max_requests=0、无规则匹配、时钟回退）
   - Retry-After 精度
```

## 测试结果

```
=== Rate Limiter Self-Test ===

[Test 1] Sliding window basics
  3 requests allowed, remaining=0
  4th request rejected, retry_after=9.00s
  Request after window expiry: allowed

[Test 2] Rule matching
  Path matching: OK
  Empty path list matches all: OK

[Test 3] Multi-rule limiter
  /api/data: 10 allowed, 11th rejected by rule 'ip'
  /api/login: 3 allowed, 4th rejected by rule 'login'

[Test 4] IP isolation
  Different IPs have independent limits: OK

[Test 5] Edge cases
  max_requests=0: rejects all
  No matching rules: allows by default
  Clock skew (timestamp regression): handled gracefully

[Test 6] Retry-After precision
  Retry-After = 2.00s (expected ~2.0s): OK

=== All tests passed ===
```

## 功能覆盖

- [x] 支持按 IP、按用户、按 API 路径限流
- [x] 滑动窗口算法（有序时间戳 + 二分裁剪，非固定窗口近似）
- [x] 返回标准 HTTP 429 + Retry-After 头
- [x] 支持分布式部署（Redis ZSET + Lua 原子操作）
- [x] 多规则组合（优先级排序，任一拒绝即整体拒绝）
- [x] IP 隔离
- [x] FastAPI + WSGI 双框架支持
