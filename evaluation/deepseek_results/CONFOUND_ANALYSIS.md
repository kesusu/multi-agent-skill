# DeepSeek vs MiMo 差异：混淆变量分析

## 核心问题

MiMo 有 Skill = 34/54（63%），DeepSeek 有 Skill = 10/54（18.5%）。差距 24 分。
单用"模型智商"解释不完整——需要拆出所有混淆变量。

---

## 变量 1：子 Agent 的模型与思考预算（影响：极高）

**这是最可疑的变量。**

Multi-Agent Skill 的核心机制是 spawn 子 Agent（批评家、架构师、测试员等）。在 Claude Code 中，`Agent` 工具 spawn 的子 Agent 默认使用**更小的模型**（如 Haiku/Sonnet），不一定继承主对话的模型配置。

**关键问题**：当主对话跑 DeepSeek + max effort + deep thinking 时：
- 子 Agent（尤其是批评家）是否也跑在同样的 DeepSeek + deep thinking 上？
- 还是跑在一个轻量版 DeepSeek 且**没有 deep thinking**？

如果批评家没有 deep thinking，它的分析必然是"建议"级别，永远到不了 MiMo 批评家的"致命/严重"深度。这能直接解释为什么 DeepSeek 的批评家产出全是"建议"，而 MiMo 的批评家产出是"致命×4 + 严重×N"。

**验证方法**：跑一个有 Skill 任务时观察 Agent 调用的 model 参数（如果 CC 暴露的话），或对比批评家产出的思考深度。

---

## 变量 2：System Prompt 的模型适配（影响：中高）

Claude Code 的 system prompt 为 Claude 模型深度优化。在 DeepSeek 上运行时：

- **Tool use 指令格式**：CC 的 tool calling 格式是 Claude-native 的。DeepSeek 是否有等效的 tool-use 训练？格式不匹配可能导致工具调用质量下降。
- **Agent 工具的行为**：`Agent` 是 CC 最复杂的工具，它内部有角色定义、上下文隔离、输出格式等机制。这些可能依赖 Claude 特定的 prompt-following 能力。
- **"对抗性思考"的 prompt 敏感度**：Skill 要求批评家"对抗性审查，按致命/严重/轻微分级"。Claude 被训练为对这类角色扮演 prompt 高度敏感。DeepSeek 可能理解为"给一些改进建议"。

---

## 变量 3：思考预算的继承与分配（影响：中高）

DeepSeek 有独立的 "effort" 和 "deep thinking" 开关。但 CC 内部也有 thinking 机制：

| 层级 | 设置 |
|------|------|
| 用户设置 | DeepSeek effort = max, deep thinking = on |
| CC 设置 | `thinking_mode`（可能在 settings.json 中） |
| 子 Agent | **未知**——是否继承？是否降级？ |

如果 CC 的子 Agent 默认 thinking = off（即使主对话 thinking = on），批评家就废了。

**MiMo 实验的隐含优势**：MiMo 是 Claude 原生模型，CC 的 thinking 和 Agent 机制对它做了深度适配。同一套 Skill prompt 在 Claude 上能触发深度对抗审查，在 DeepSeek 上可能只触发表层检查。

---

## 变量 4：长 Prompt 的结构化遵循能力（影响：中）

Multi-Agent Skill 主文件 520 行，包含：
- 分流器（3 个问题 → 3 种模式）
- 任务拆解（依赖分析规则）
- 计划审查（5 个检查点）
- Wave 调度
- 审计员（8 项审计）
- 验收闭环（7 项检查）
- 全局审视 + 复盘 + 经验闭环
- 质量红线 + 反模式

不同模型对"长指令中的细粒度要求"遵循程度不同。Claude 在遵循复杂结构化 prompt 方面通常表现更好。DeepSeek 可能：
- 正确执行了流程框架（任务地图、Wave 调度都正常）
- 但在**精神层面**打了折扣——批评家走了形式但没深入

证据：DeepSeek 的批评家反馈格式正确（有编号、有严重度标注），但内容深度不够——"做得像"但不"做得到位"。

---

## 变量 5：上下文窗口的注意力分布（影响：中）

Multi-Agent 框架产生大量上下文：
- 任务地图 + 计划审查报告 + Wave 调度声明 + Agent 产出 + 审计报告

不同模型的长上下文注意力分布不同。如果 DeepSeek 对中间段的注意力衰减更快，批评家在读架构师产出时可能已经"丢失"了原始需求的关键细节——导致审查变浅。

---

## 变量 6：D5 支付任务触发了 Q3 代价门禁（影响：已证实）

这是**唯一一个受控的变量**——在 6 个任务中，只有 D5（支付）触发了 Q3="代价大"→ 探针模式 → 深层需求分析。D5 也是 DeepSeek 最高分(4/9)。

其他 5 个任务被判 Q3="代价不大"→ 批评家走快速通道 → 审查更浅。这个分流决策本身就是个变量：**同样的任务，不同模型可能给出不同的 Q3 判断**，从而进入不同的审查深度。

---

## 变量 7：模型的知识边界不同（影响：低-中）

MiMo 批评家在 ETL 拿满分(9/9)——"每个写过数据管道的人都踩过的坑"。DeepSeek 批评家在 ETL 只拿 1/9。

这不是"智商"问题，是训练数据中**工程实践案例的覆盖密度**不同。Claude 的训练数据可能包含更多 StackOverflow/GitHub 上的"ETL 踩坑"讨论。DeepSeek 可能在这些领域的实战知识密度较低。

---

## 变量 8：CC 版本/配置差异（影响：未知）

MiMo 实验和 DeepSeek 实验可能使用不同版本的 Claude Code CLI。不同版本对 Agent 工具的实现、模型路由、thinking 分配可能有差异。

---

## 可控变量 vs 不可控变量

| 变量 | 可控 | 建议 |
|------|:--:|------|
| 子 Agent 模型/thinking | ✅ | 检查 CC 配置，确认子 Agent 是否继承 deep thinking |
| System prompt 适配 | ❌ | CC 内部机制，改不了 |
| 思考预算继承 | ✅ | 检查 settings.json 中 Agent 相关配置 |
| 长 prompt 遵循 | ❌ | 模型固有特性 |
| 上下文注意力分布 | ❌ | 模型固有特性 |
| Q3 代价判断 | ✅ | 可以手动调整为"代价大"触发探针模式 |
| 知识边界 | ❌ | 模型固有特性 |
| CC 版本 | ✅ | 确保同版本 |

---

## 最可能的主因（按影响力排序）

1. **子 Agent 没有 deep thinking**（影响力最大，可验证）
2. **System prompt 对 DeepSeek 的 Agent 工具适配不足**（影响力大，不可控）
3. **DeepSeek 对"对抗性批评家"角色的 prompt 敏感度低于 Claude**（影响力中，不可控）
4. **Q3 代价判断导致大部分任务走快速通道**（影响力中，可控——手动调）
