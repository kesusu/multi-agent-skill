# Session 6 — D6 ETL (有 Skill)

## 任务

设计一个 ETL 数据管道的错误处理机制。

## 流程：/multi-agent 框架模式

### 0秒分流器
- Q1: 方案 → Q2: 否（ETL 多数据源+死信队列）→ Q3: 不大 → **框架模式**

### 任务地图
- T1: ETL 管道核心 — 架构师+执行者（合并）
- T2: 批评家审查
- 角色：架构师+执行者、批评家

### 批评家审查

第一轮 Agent 偏离目标（审查了无关文件），重新派发后完成。

## 实现

### etl_pipeline.py 核心结构

```
1. 数据源抽取器
   - CsvExtractor: 读取 CSV 文件
   - ApiExtractor: 模拟 API 调用（基于 api_schema.json）
   - DbExtractor: 模拟数据库查询

2. 转换器
   - 字段映射（name→full_name, id→user_id 等）
   - 类型转换（str→int/float/date）
   - 去重（基于 record_id）

3. 加载器
   - InMemoryLoader: 模拟数据库写入

4. 错误处理
   - RetryPolicy: 可配置重试次数 + 指数退避
   - DeadLetterQueue: 失败记录持久化
   - AlertManager: 回调告警通知

5. 管道编排
   - Pipeline: 串联 E→T→L，逐记录重试 + DLQ

6. 自测
   - 干净运行：15 条全通，DLQ=0
   - 故障注入：偶数用户失败 → 2 条进 DLQ，3 条成功，告警触发 2 次
```

## 测试结果

```
===== SELF-TEST RESULTS =====
[extract]  records extracted: 15
[transform] records after transform: 15
[load]     records loaded: 15
[check]    user_id type: int
[check]    order amount type: float
[dlq]      dead letters: 0
[timing]   duration: 0.016s

----- DLQ / retry injection test -----
[dlq-test] dead letters: 2
[dlq-test] loaded: 3
[dlq-test] alerts fired: 2

===== ALL SELF-TESTS PASSED =====
```

## 功能覆盖

- [x] 从多个数据源（API、数据库、CSV）抽取数据
- [x] 转换（字段映射、类型转换、去重）
- [x] 加载到目标数据库
- [x] 支持失败重试（指数退避）
- [x] 死信队列（处理失败记录持久化）
- [x] 告警通知（回调机制）
