# Session 10 — D4 限流 · 无 Skill

## 任务

设计一个 Web API 限流中间件。要求：
1. 支持按 IP、按用户、按 API 路径限流
2. 滑动窗口算法（不是固定窗口）
3. 返回标准 HTTP 429 + Retry-After 头
4. 支持分布式部署（多实例共享限流状态）

## 实现

创建了 `D4_rate_limiter/rate_limiter.py`。

### 滑动窗口算法

使用 Redis Sorted Set 实现：
```
zremrangebyscore(key, 0, now - window)  # 移除过期条目
zcard(key)                               # 计数
if count < max: zadd(key, now, now)      # 允许
else: reject + Retry-After               # 拒绝
```

每个请求以毫秒时间戳作为 score 加入 sorted set。每次检查时先清理窗口外的条目。

### 双模式存储

- **Redis**：`SlidingWindowStore` — 原子 pipeline 操作，支持多实例共享
- **内存**：`InMemorySlidingWindow` — 单进程，列表存储时间戳

### 限流键设计

```python
ratelimit:{key_type}:{key_value}
# e.g. ratelimit:ip:192.168.1.1
# e.g. ratelimit:user_id:user_42
# e.g. ratelimit:api_path:/api/payments
```

### Flask 中间件适配

```python
from rate_limiter import RateLimiter, flask_middleware

limiter = RateLimiter(redis_client)
app.before_request(flask_middleware(limiter))
```

返回标准 HTTP 429：
```json
{"error": {"code": 429, "message": "Too Many Requests", "retry_after": 30.5}}
```
+ `Retry-After: 31` 头
+ `X-RateLimit-Remaining: 0` 头

### 验证结果

6 项测试全部通过：
```
[PASS] First 10 allowed
[PASS] 11th blocked, retry_after=60.0s
[PASS] Different IPs independent
[PASS] Per-user limiting works
[PASS] Per-API-path limiting works
[PASS] Multi-rule first-block works
[PASS] InMemorySlidingWindow works
```

### 代码位置
- `D4_rate_limiter/rate_limiter.py` — 核心实现
- `D4_rate_limiter/test_rate_limiter.py` — 测试
