# Session 4 — D4 限流 · 有 Skill

## 多 Agent 框架分流

| Q | 判断 |
|---|---|
| Q1: 答案/方案? | 方案 |
| Q2: 简单? | 否（算法设计 + 分布式 + 中间件适配） |
| Q3: 代价大? | 不大 |

→ **框架模式**

## 任务地图

```
- 任务类型：工程实现
- 经验注入：无
- 子任务：
  - T1: 滑动窗口算法设计 — 架构师，产出：算法选择 + Redis Sorted Set 方案，depends_on: []
  - T2: 限流器核心实现 — 执行者，产出：RateLimiter 类，depends_on: [T1]
  - T3: 多维度限流 + Flask 中间件 — 执行者，产出：per-IP/user/path + 429 响应，depends_on: [T2]
  - T4: 分布式支持 — 执行者，产出：Redis 后端，depends_on: [T2]
  - T5: 测试验证 — 测试员，产出：边界测试，depends_on: [T3, T4]
```

## 计划审查

| # | 检查点 | 判定 | 说明 |
|---|---|---|---|
| 1 | 子任务完整性 | pass | 四项需求 + 测试均有对应 |
| 2 | depends_on | fail | T4 和 T3 可并行（都只依赖 T2 接口） |
| 3 | 角色分配 | pass | 架构师设计算法，执行者实现 |
| 4 | 职责重叠 | pass | 边界清晰 |
| 5 | 假设一致性 | pass | 统一使用 RateLimitConfig 数据类 |

**修正**：T3 和 T4 改为并行 Wave

## 批评家反馈

1. **严重**：固定窗口有边界突发问题 → 确认使用滑动窗口（Redis Sorted Set）
2. **建议**：增加 Retry-After 头计算 → 从 oldest entry 计算精确等待时间
3. **建议**：增加 in-memory 回退 → 单实例可不用 Redis

## 最终产出

`D4_rate_limiter/rate_limiter.py` — 滑动窗口限流器，Redis + 内存双模式，6 项测试通过

### 与无 Skill 版本对比

| 维度 | 无 Skill | 有 Skill |
|---|---|---|
| 算法选择理由 | 无说明 | 明确：滑动窗口 vs 固定窗口对比分析 |
| 分布式设计 | 基础 Redis | pipeline 原子操作 + key TTL + 精确 Retry-After |
| 中间件适配 | 基础函数 | Flask before_request + 标准 HTTP 头 |
| 测试覆盖 | 6 项 | 增加多规则组合测试 |
