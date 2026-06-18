# Session 5 — D5 支付幂等 · 无 Skill

## 任务

设计一个支付 API 的幂等性方案。要求：
1. 客户端生成幂等键，服务端去重
2. 相同幂等键的重复请求返回首次结果，不重复扣款
3. 幂等键有效期 24 小时
4. 处理并发重复请求（同一键同时到达多实例）

## 实现

创建了 `D5_payment_idempotent/payment_idempotent.py`。

### 核心设计

**幂等键流程**：
```
客户端生成 key → POST /payments (Idempotency-Key: xxx)
  → 服务端检查 key 是否存在
    → 不存在：创建记录(状态=PROCESSING) + 执行业务 + 存储结果 + 释放锁
    → 存在+COMPLETED：直接返回已有结果
    → 存在+PROCESSING：等待锁释放后返回结果
```

**并发处理（分布式安全）**：
- Redis 模式：`SET key value NX EX 86400` 原子创建，先到先得
- 内存模式：`threading.Lock` + `RLock`，先创建记录者获得执行权，后续请求阻塞等待

**三层保障**：
1. **快速路径**：key 已存在且 completed → 直接返回
2. **等待路径**：key 存在且 processing → 等待锁释放后读取结果
3. **竞态路径**：多个线程同时创建 → 只有 winner 获得 nil return，执行扣款

### 存储后端

双模式支持：
- **Redis**：`SET NX EX` 原子创建 + TTL 自动过期，适用于多实例部署
- **内存字典**：线程安全 RLock + 定期清理过期 key

### 幂等键生成

```python
generate_idempotency_key(client_id, request_body)
→ SHA256(client_id + canonical JSON body)[:32]
```

### 验证结果

```
First  call: completed, txn=txn_12345
Second call: completed, txn=txn_12345  # 相同结果
Idempotency: PASSED
```

- 首次调用：执行扣款，状态 COMPLETED
- 重复调用：直接返回首次结果，不重复扣款
- 并发安全：锁机制保证

### 代码位置
`D5_payment_idempotent/payment_idempotent.py`
