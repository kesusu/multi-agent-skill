# Session 11 — D5 支付幂等 (有 Skill)

## 任务

设计一个支付 API 的幂等性方案。

## 流程：/multi-agent 框架模式

### 0秒分流器
- Q1: 方案 → Q2: 是 → Q3: 不大 → **框架模式**

代码已由 Session 5（无 Skill）创建，Skill 框架模式下验证通过。

## 实现

### idempotent.py 核心结构

```
1. 数据结构
   - RequestStatus: PROCESSING / COMPLETED / FAILED
   - IdempotencyRecord: 幂等键记录
   - PaymentRequest: 支付请求（含幂等键校验）
   - PaymentResult: 支付结果（含 is_duplicate 标记）

2. 幂等键存储
   - MemoryIdempotencyStore: 线程安全（threading.Lock）
   - try_lock(): 原子操作获取锁

3. 支付处理器
   - IdempotentPaymentProcessor:
     - 首次请求 → 执行支付 → 缓存结果
     - 重复请求 → 等待/返回缓存结果（不重复扣款）
     - 并发安全：多线程同键只有 1 个执行支付
     - 24 小时 TTL 过期

4. 6 组自测全部通过
```

## 测试结果

```
1. 首次: TXN-0001, is_dup=False, payments=1
2. 重复: TXN-0001, is_dup=True, payments=1（不重复扣款）
3. 新键: TXN-0002, is_dup=False, payments=2
4. 并发 10 线程: payments=1（只扣款 1 次）
5. 过期后: 新交易，is_dup=False
6. 参数校验: 空键/负金额抛 ValueError
全部演示通过
```

## 功能覆盖

- [x] 客户端生成幂等键，服务端去重
- [x] 相同幂等键返回首次结果，不重复扣款
- [x] 幂等键有效期 24 小时
- [x] 并发重复请求安全（threading.Lock + try_lock 原子操作）
