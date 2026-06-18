# Multi-Agent Skill：MiMo 用户指南

> **定位声明**：这是一套 Claude Code 上的多 Agent 协作调度方法论，通过一个 `.md` 文件实现。不是 Python 框架（AutoGen/CrewAI/LangGraph 是引擎，这是驾驶手册），不是独立运行的软件系统，不替代 Claude Code 的 Agent 工具，而是优化其使用方式。

## 为什么 MiMo 用户需要这个

单 Agent 做工程有一个结构性问题：**它不质疑自己的设计选择**。

当你让 MiMo 写一个方案，它会很努力地写出来。但"努力写"和"写对"之间有一道坎——设计决策需要被另一个人挑毛病。单 Agent 模式下，没有那个人。

multi-agent skill 解决的不是"MiMo 能力不够"，而是"多视角交叉验证"这件事，单个 Agent 天然做不到。就像一个人做 code review 不如两个人交叉审——不是水平问题，是结构问题。

## 它能带来什么

skill 提供三层机制：

1. **智能分流**：简单问题直接答，不浪费 token。只有真正复杂的工程任务才启动多 Agent 流程。
2. **多 Agent 协作**：执行者、批评家、验收者各有分工。批评家专门挑毛病，验收者确保方向没偏。两者独立，不会互相跟风。
3. **经验沉淀**：每次任务的教训写入持久存储，下次同类任务自动回顾。你的 skill 会越用越好。

**实测数据**：在一次方案设计任务中，批评家找到了 2 个严重设计漏洞（因果链断裂 + 客户端缓存缺失），对照组（单 Agent）完全没有发现。跨模型验证（MiMo + DeepSeek）确认批评家增量不是模型特有现象——两个模型的审查能力在同一水平（MiMo 9/54 vs DeepSeek 10/54）。对抗审查是这个 skill 最核心的价值。

## 安装方法

skill 是一个 `.md` 文件，零代码零依赖。一步安装：

```bash
git clone https://github.com/kesusu/multi-agent-skill.git
cp multi-agent-skill/commands/multi-agent.md ~/.claude/commands/multi-agent.md
```

然后在 Claude Code 中输入 `/multi-agent <你的任务>` 即可。

## 怎么基于它迭代

skill 是纯 Markdown 文件，你可以直接编辑：

- **加角色模板**：在"角色设计"章节追加你常用的角色（如"性能分析员"、"部署审查员"）
- **改分流器条件**：调整 0 秒分流器的三个判断条件，适配你的工作模式
- **调反模式清单**：根据你的踩坑经验，增删禁止行为
- **鼓励 fork**：每个团队的工作流不同，把它当成起点，改成你的版本

每次修改 skill 后，框架会自动记录变更日志，方便回溯。

## 诚实声明

这个 skill 有明确的边界：

- **强绑定 Claude Code**：依赖 Claude Code 的 Agent spawn 机制，不能在其他平台直接使用。
- **不能消除 AI 固有局限**：幻觉、上下文丢失、长程遗忘——这些是 LLM 的底层约束，skill 无法突破。
- **但能提高敷衍成本**：自检 + 独立审计 + 对抗审查，让产出必须经过多轮验证才能通过。不是"保证不出错"，而是"出错的成本更高、被发现的概率更大"。

## 与其他方案的关系

AutoGen、CrewAI、LangGraph 是**引擎**——你需要写代码来定义 Agent 行为和编排逻辑。

multi-agent skill 是**驾驶手册**——一个 Markdown 文件，粘贴到 Claude Code 就能用。

两者不冲突。如果你已经在用 AutoGen 写 Agent 系统，这个 skill 提供的是协作模式的经验沉淀，不是替代。

**选型建议**：
- 需要自定义 Agent 行为和工具调用 → 用 AutoGen/CrewAI
- 需要在 Claude Code 里直接用、零配置 → 用这个 skill
- 两者可以并存——用 Claude Code 做快速原型和探索，用框架做正式部署
