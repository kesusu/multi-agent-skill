# Session 6 — D6 ETL · 有 Skill

## 多 Agent 框架分流

| Q | 判断 |
|---|---|
| Q1: 答案/方案? | 方案 |
| Q2: 简单? | 否（多源+多阶段+错误处理，架构复杂） |
| Q3: 代价大? | 不大 |

→ **框架模式**

## 任务地图

```
- 任务类型：工程实现
- 经验注入：无
- 子任务：
  - T1: 数据源适配层设计 — 架构师，产出：DataSource 抽象接口，depends_on: []
  - T2: 转换管道设计 — 架构师，产出：Transformer + 类型映射，depends_on: []
  - T3: 加载 + 重试机制 — 执行者，产出：Loader + 指数退避，depends_on: [T1, T2]
  - T4: 死信队列 + 告警 — 执行者，产出：DLQ + AlertNotifier，depends_on: [T3]
  - T5: 端到端测试 — 测试员，产出：使用真实 CSV/API schema 验证，depends_on: [T3, T4]
```

## 计划审查

| # | 检查点 | 判定 | 说明 |
|---|---|---|---|
| 1 | 子任务完整性 | pass | 四需求全覆盖 |
| 2 | depends_on | pass | T1/T2 可并行，T3 依赖两者接口 |
| 3 | 角色分配 | pass | 架构师设计接口，执行者实现 |
| 4 | 职责重叠 | pass | 各阶段职责清晰 |
| 5 | 假设一致性 | pass | 统一 ETLRecord 数据类流通全管道 |

## 批评家反馈

1. **严重**：单一源失败不应阻塞整个管道 → extract 阶段 try/except per-source
2. **建议**：重试应使用指数退避而非固定间隔 → `delay = base * attempt`
3. **建议**：DLQ 应持久化到文件而非只在内存 → JSONL 文件存储
4. **建议**：增加 PipelineStats 汇总 → 提取/转换/加载/失败/死信 计数

## 最终产出

`D6_etl_pipeline/etl_pipeline.py` — 三源 ETL 管道，12 条记录全流程无错误

### 与无 Skill 版本对比

| 维度 | 无 Skill | 有 Skill |
|---|---|---|
| 源适配层 | CSV + API | 抽象 DataSource + 可扩展 |
| 重试策略 | 固定间隔 | 指数退避 1s→2s→3s |
| DLQ 格式 | JSON 字符串 | JSONL 结构化 + 时间戳 |
| 统计 | 日志 | PipelineStats 数据类 |
| 错误隔离 | 未处理 | per-source try/except，单源失败不阻塞 |
