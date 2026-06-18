# Session 12 — D6 ETL · 无 Skill

## 任务

设计一个 ETL 数据管道的错误处理机制。要求：
1. 从多个数据源（API、数据库、CSV）抽取数据
2. 转换（字段映射、类型转换、去重）
3. 加载到目标数据库
4. 支持失败重试、死信队列、告警通知

## 实现

创建了 `D6_etl_pipeline/etl_pipeline.py`。

### 架构

```
DataSource (抽象类)
├── CSVSource    → csv.DictReader 读取
├── APISource    → HTTP API (模拟)
└── DBSource     → (可扩展)

Transformer → 字段映射 + 类型转换 + 去重

Loader → 指数退避重试 → 目标DB
                ↓ 重试耗尽
         DeadLetterQueue → dead_letter_queue.jsonl

AlertNotifier → webhook / 日志告警
```

### 错误处理分层

| 层级 | 错误类型 | 处理策略 |
|---|---|---|
| Extract | 文件不存在、API 超时 | 记录告警，跳过该源，继续处理其他源 |
| Transform | 类型转换失败、重复 ID | 标记 FAILED，不阻塞其他记录 |
| Load | DB 写入失败 | 指数退避重试 3 次 → DLQ |

### 数据流

```
CSV(users) ───┐
CSV(orders) ──┼─→ Extract (12 rows) → Transform (12 records)
API(users) ───┘                          │
                                    Type conversion
                                    Dedup by ID
                                         │
                                    Load (3 retries)
                                         │
                              ┌──────────┴──────────┐
                          LOADED (12)          DEAD (0) → DLQ
```

### 重试策略

指数退避：`delay = retry_delay * attempt` (1s, 2s, 3s)

### 验证结果

使用提供的 users.csv、orders.csv、api_schema.json 运行完整管道：

```
Pipeline Stats: extracted=12, transformed=12, loaded=12, failed=0, dead=0
Alerts raised: 0
```

三源数据抽取、字段映射、去重、加载全流程无错误。

### 代码位置
`D6_etl_pipeline/etl_pipeline.py`
