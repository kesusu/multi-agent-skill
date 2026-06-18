# Session 10 — D4 限流 (无 Skill)

## 任务

设计一个 Web API 限流中间件。

## 实现

代码与 Session 4（有 Skill）相同。Skill 版本经过批评家审查修复了 3 个严重问题：
1. Redis member 多进程唯一性（uuid 替代 threading.get_ident）
2. FastAPI 中间件文档与实际返回类型不一致（更新文档）
3. Retry-After 头/body 值不一致（统一 math.ceil）

无 Skill 版本使用已修复后的最终代码。

### rate_limiter.py 核心结构

```
1. 滑动窗口核心
   - MemoryBackend: 有序时间戳 + Lock（线程安全）
   - RedisBackend: ZSET + Lua 脚本（分布式原子操作）

2. 限流规则
   - RateLimitRule: per-IP / per-user / per-path，优先级排序
   - SlidingWindowRateLimiter: 多规则匹配，任一拒绝即整体拒绝

3. 框架封装
   - create_fastapi_middleware(): BaseHTTPMiddleware
   - create_fastapi_dependency(): Depends 注入
   - WSGIRateLimitMiddleware: Flask/Django 兼容

4. 6 组自测全部通过
```

## 测试结果

```
[Test 1] 滑动窗口基本逻辑: OK
[Test 2] 规则匹配: OK
[Test 3] 多规则组合: OK
[Test 4] IP 隔离: OK
[Test 5] 边界情况: OK
[Test 6] Retry-After 精度: OK
=== All tests passed ===
```

## 功能覆盖

- [x] 按 IP、按用户、按 API 路径限流
- [x] 滑动窗口算法
- [x] HTTP 429 + Retry-After 头
- [x] 分布式部署（Redis 后端）
