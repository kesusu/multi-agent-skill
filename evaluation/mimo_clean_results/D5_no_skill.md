# Session 5 — D5 支付幂等 (无 Skill)

## 任务

设计一个支付 API 的幂等性方案。

## 实现

### idempotent.py 核心结构

```
1. 数据结构
   - RequestStatus: PROCESSING / COMPLETED / FAILED
   - IdempotencyRecord: 幂等键记录（状态、时间、结果）
   - PaymentRequest: 支付请求（金额、幂等键等）
   - PaymentResult: 支付结果（含 is_duplicate 标记）

2. 幂等键存储
   - IdempotencyStore: 基类接口
   - MemoryIdempotencyStore: 线程安全内存存储（threading.Lock）

3. 支付处理器
   - IdempotentPaymentProcessor:
     - try_lock(): 原子获取锁（新键 or 过期键）
     - 重复请求 → 等待完成 → 返回缓存结果
     - 并发安全：多个线程同时到达只有一个能执行支付

4. 自测（6 组全部通过）
   - 首次请求 → 正常支付
   - 重复请求 → 返回首次结果，不重复扣款
   - 不同幂等键 → 新交易
   - 10 线程并发 → 只扣款 1 次
   - 幂等键过期 → 允许新请求
   - 参数校验
```

## 测试结果

```
1. 首次支付请求:
   transaction_id=TXN-0001 is_duplicate=False 支付次数=1

2. 重复支付请求（相同幂等键）:
   transaction_id=TXN-0001 is_duplicate=True 支付次数=1

3. 不同幂等键 → 新交易:
   transaction_id=TXN-0002 is_duplicate=False 支付次数=2

4. 并发重复请求测试（10 线程同时发起）:
   完成数: 10 错误数: 0 实际支付次数: 1
   首次请求: 1  重复请求: 9  总计: 10

5. 幂等键过期测试:
   首次: tx=TXN-0001 payments=1
   过期后: tx=TXN-0002 is_dup=False payments=2

6. 参数校验:
   空幂等键: ValueError
   负金额: ValueError

全部演示通过
```

## 功能覆盖

- [x] 客户端生成幂等键，服务端去重
- [x] 相同幂等键的重复请求返回首次结果，不重复扣款
- [x] 幂等键有效期 24 小时（可配置 ttl_seconds）
- [x] 处理并发重复请求（threading.Lock + try_lock 原子操作）
- [x] PROCESSING 状态等待机制（轮询 + 超时）
- [x] 过期键自动清理（cleanup_expired）
