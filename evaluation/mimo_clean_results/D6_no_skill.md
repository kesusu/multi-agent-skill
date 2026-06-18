# Session 12 — D6 ETL (无 Skill)

## 任务

设计一个 ETL 数据管道的错误处理机制。

## 实现

代码与 Session 6（有 Skill）相同。

### etl_pipeline.py 核心结构

```
1. 数据源抽取器
   - CsvExtractor: users.csv, orders.csv
   - ApiExtractor: 模拟 API（基于 api_schema.json）
   - DbExtractor: 模拟数据库查询

2. 转换器
   - 字段映射（name→full_name 等）
   - 类型转换（str→int/float/date）
   - 去重（基于 record_id）

3. 加载器
   - InMemoryLoader: 模拟数据库写入

4. 错误处理
   - RetryPolicy: 可配置重试 + 指数退避
   - DeadLetterQueue: 失败记录持久化
   - AlertManager: 回调告警

5. 管道编排
   - Pipeline: 串联 E→T→L，逐记录重试 + DLQ

6. 自测（全部通过）
```

## 测试结果

```
正常路径: extracted=15, transformed=15, loaded=15, dlq=0
故障注入: dead_letters=2, loaded=3, alerts=2
===== ALL SELF-TESTS PASSED =====
```

## 功能覆盖

- [x] 从多个数据源（API、数据库、CSV）抽取数据
- [x] 转换（字段映射、类型转换、去重）
- [x] 加载到目标数据库
- [x] 支持失败重试、死信队列、告警通知
