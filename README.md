# Multi-Agent Skill: Relay — Claude Code 多 Agent 协作框架

> 一个 `.md` 文件，让你的 AI 从"一个人干"变成"一个团队干"。
>
> 分流器是教练选人（简单任务不上场），Wave 调度是棒次安排（同一棒多人并行跑，不同棒按交接规则顺序来），依赖分析是交接棒规则，验收者是终点裁判，批评家是赛前质疑队友状态的人。
>
> **完整多 Agent 协作调度（Wave 并行、独立审计、经验沉淀）需要 Claude Code 环境。** 核心方法论思想（分流器、对抗审查、需求锚定）可迁移到任何支持 system prompt 的平台（Codex、GLM、Kimi、DeepSeek 等）。已在 MiMo (Claude) + DeepSeek 上完成双模型验证。
>
> 5 分钟上手，看到差别。你可以基于它搭自己的多 Agent 团队，做自己的项目，改自己的框架。

## 目录

- [它是什么](#它是什么)
- [它不是什么](#它不是什么)
- [用它做过什么](#用它做过什么)
- [为什么有用](#为什么有用)
- [拿它能做什么](#拿它能做什么)
- [快速上手（5分钟）](#快速上手5分钟)
- [想深入？](#想深入)
- [适合谁](#适合谁)
- [不适合谁](#不适合谁)
- [项目结构](#项目结构)
- [诚实声明](#诚实声明)
- [参与共创](#参与共创)
- [致谢](#致谢)
- [License](#license)

---

## 它是什么

一套多 Agent 协作调度方法论，打包成一个 `.md` 文件。把 AI 任务变成一场接力赛——每个角色只跑自己那一棒，交接棒有规则，终点有裁判。

**两层能力，迁移程度不同**：

| 层 | 内容 | 平台要求 |
|:---|:---|:---|
| **方法论层**（可迁移） | 分流器（3 问题判断复杂度）、对抗审查思想、需求锚定、经验沉淀理念 | 任何支持 system prompt 的平台 |
| **调度层**（需 Claude Code） | Wave 并行调度、子 Agent spawn、独立审计员、自动复盘 | 依赖 Claude Code 的 Agent 工具 |

Claude Code 用户用 slash command 调用，获得完整体验。其他平台用户可以将方法论层的内容迁移到自己的 system prompt 中——分流器逻辑和对抗审查思想仍然有效，但无法实现并行 Agent 调度。

- **教练选人**（分流器）：3 个问题判断任务该走哪条路，简单任务不上场，不浪费资源
- **赛前审查**（计划审查 Agent）：任务执行前独立 Agent 按 5 维度审查计划，有问题在起跑前修正
- **队友质疑**（批评家）：对设计方案做对抗性审查，挑不出毛病就引入第二个批评家交叉验证
- **按棒次跑**（Wave 调度）：同一 Wave 内的 Agent 并行工作，不同 Wave 之间按依赖顺序串行
- **终点裁判**（验收者）：每轮对照原始需求逐项验收，不是最后才查一次
- **赛后复盘**（经验沉淀）：教训自动记住，下次同类任务直接注入决策检查点

## 它不是什么

- 不是 Python 框架（AutoGen/CrewAI/LangGraph 是引擎，这是驾驶手册）
- 不是独立运行的软件系统
- 不替代 Claude Code 的 Agent 工具，而是优化其使用方式（完整调度需 Claude Code）
- 不让 AI 更聪明，而是让 AI 不敢敷衍——强制交叉审查，错误必须付出返工代价
- **没有做到模型层**——改不了模型权重、训不了专属参数。说白了就是一套提示词工程方法论。但这恰恰是大多数人的现状：没有能力修改模型，只能站在强大 AI 的风口上，用 skill 层的创新武装自己。不是什么颠覆行业的东西，是在能力范围内做到最好
- **和豆包之类的区别**：豆包很会说话——"最正确最直接最有效最不绕弯子地告诉你"，犯了错说"下次一定不错"然后继续错。这个框架里的批评家不跟你客气，问题就是问题，不分级不安慰。你不一定每次都爱听，但它说的是真话

## 用它做过什么

多 Agent 的分工让不同视角的任务协作更靠谱——架构师设计、批评家审查、测试员验证，各司其职，不会一个人又做又查。

| 场景     | 一句话                                        | 分工怎么帮了忙                                                                       |
|:---------|:----------------------------------------------|:-------------------------------------------------------------------------------------|
| 开源打包 | 这份 README、12 个文档、A/B 实验设计，全部由多 Agent 团队完成 | 架构师定叙事、研究员对齐数据、批评家抓自我否定的措辞、验收者守住核心主题               |
| 文档处理 | 扫描 PDF 转可编辑 Word，LaTeX 公式双击可改，已独立开源       | 执行者写 pipeline、批评家抓出 5 个"规则对但没执行"的隐性缺陷                          |
| 游戏开发 | 纯 HTML+JS 愤怒的小鸟，910 行，2D 物理+关卡+音频            | 架构师搭引擎、测试员踩边界、批评家发现物理参数没联动校准 → [`demos/angry_birds.html`](demos/angry_birds.html) |
| 理论研究 | "AI 时代你真正的活儿是什么"——从焦虑到行动的定位框架 | 4 轮迭代：理论家写框架 → 场景测试员发现初版对文科生不可读 → 重写通用入口 → 产出 CS/EE 专属版 [`推荐：CS/EE版`](demos/theory_v3.3_CS%20OR%20EE.md) [`通用版`](demos/theory_v3.3建议看另外一个更好的版本.md) |
| 自学习   | 自主学习教材→出题→批改→反思→做笔记，用于开卷考试（框架内验证）  | "学"和"查"分离，避免自己出题自己答的盲区                                             |
| 工程训练 | 自动出题+评分+对比基线的能力训练系统（框架内验证）             | 批评家对标基线找差距，不是自己觉得自己行                                               |
| A/B 实验 | 3 组对照实验验证分流器准确性+对抗审查价值                   | Task C 对照组漏 2 个严重漏洞，批评家是唯一的增量价值                                   |
| 跨模型验证 | MiMo + DeepSeek 双模型 × 6 任务 × 2 条件 = 24 个独立对话   | 无 Skill 基线 0/54（跨模型一致），批评家增量 MiMo +9、DeepSeek +10                   |
| 自审查   | 用多 Agent 框架审查框架自身                              | 审计员 catch 到调度员不会自认的违规                                                   |

详见 [`examples/cases.md`](examples/cases.md)。

## 为什么有用

单 Agent 做复杂决策时会自己做决定，但不会质疑自己的选择。

跑了 3 组 A/B 对照实验（pilot study，1 人 1 次执行，不能做统计推断）：

| 任务                         | 复杂度 | 分流器行为                 | 核心差异                                         |
|:-----------------------------|:-------|:---------------------------|:-------------------------------------------------|
| Python *args/**kwargs 区别   | 极简   | 正确判极简模式，跳过全部流程 | 产出等价，分流器通过极限测试                       |
| 代码解释+找问题              | 中等   | 正确判极简模式             | 两者产出接近，skill 核心能力未被触发               |
| 多人协作文档冲突方案         | 复杂   | 正确判框架模式，启动多 Agent | 批评家找到 2 个严重问题，对照组未发现              |

Task C 具体发现：批评家发现 Lamport 时钟在网络分区重连后因果链会断裂，改为 HLC；还发现方案缺少客户端缓存层，离线用户每次操作都要全量请求。对照组方案自洽，但没人质疑自己的设计选择。

> 3 个任务的样本量都很小，不能做统计推断。分流器 3/3 正确分类，批评家在复杂任务中找到了对照组遗漏的问题——这些是可复现的因果发现，不是统计结论。

### 跨模型验证（MiMo + DeepSeek）

用预埋 bug 法在 MiMo (Claude) 和 DeepSeek-v4-pro 上跑了 6 个任务（3 中等 + 3 复杂），每任务预埋 3 个 bug，满分 54 分。每个条件使用全新空白对话，零上下文污染。

| | MiMo (Claude) | DeepSeek |
|---|:---:|:---:|
| 无 Skill（代码生成基线） | 0/54 | 0/54 |
| 有 Skill（框架模式） | **9/54** | **10/54** |
| 增量 | +9 | +10 |

核心发现：
1. **无 Skill 基线跨模型一致为 0**：LLM 在"写代码"模式下默认不质疑设计，这是通用现象
2. **批评家增量集中在特定 bug 类型**：竞态条件、状态机漏洞、攻击面推演——偏代码正确性
3. **两个模型的审查能力在同一水平**：MiMo 9 vs DeepSeek 10，差距在误差范围内

详见 [`evaluation/FINAL_REPORT.md`](evaluation/FINAL_REPORT.md) 和 [`evaluation/SCORING_SHEET.md`](evaluation/SCORING_SHEET.md)。

## 拿它能做什么

- **如果你是 Claude Code 用户**：装上即获得完整多 Agent 协作能力——Wave 并行调度、对抗审查、独立审计、经验沉淀，工程任务从"能跑"变"跑得稳"。MiMo 用户详见 [`docs/mimo_guide.md`](docs/mimo_guide.md)
- **如果你在用其他 AI 平台**（Codex、GLM、Kimi、DeepSeek 等）：方法论层（分流器逻辑、对抗审查思想、核心原则）可以迁移到你的 system prompt 中，提升任务拆解和审查质量
- **如果你想 5 分钟看到差别**：装上跑一个复杂任务，重点看批评家挑出了什么你没注意到的问题
- **如果你想做二次开发**：基于这个框架搭你自己的多 Agent 团队——改分流器判据、加角色、适配你的领域，3 个点就能出你自己的版本。已有 12 个版本的踩坑记录可供参考。详见 [`docs/fork_guide.md`](docs/fork_guide.md)
- **如果你想构建新项目**：这不是一个用完就扔的工具，是一套可复用的多 Agent 协作框架。用它做过的项目包括游戏、文档处理、自学习、理论研究——你也可以在你的领域上做。详见 [`examples/cases.md`](examples/cases.md)

## 快速上手（5分钟）

### 前置条件

- [Claude Code](https://claude.ai/code)（完整多 Agent 调度需要）；其他平台可迁移方法论层

### 安装

```bash
git clone https://github.com/kesusu/multi-agent-skill.git
```

核心就一个文件：`commands/multi-agent.md`。根据你的平台选择安装方式：

#### Claude Code（slash command 方式）

```bash
# macOS / Linux
cp multi-agent-skill/commands/multi-agent.md ~/.claude/commands/multi-agent.md

# Windows (PowerShell)
Copy-Item multi-agent-skill\commands\multi-agent.md $env:USERPROFILE\.claude\commands\multi-agent.md
```

重启 Claude Code，输入 `/multi-agent` 验证命令已注册。

**可选增强**（CLAUDE.md + rules，提升整体工程质量）：

> CLAUDE.md 包含项目特定的工程规则（Python 版本、Word 排版规范等）。**复制前建议审阅一遍**，把不适合你的规则删掉或改成你的。

```bash
# macOS / Linux
cp multi-agent-skill/CLAUDE.md ~/.claude/CLAUDE.md
cp -r multi-agent-skill/rules ~/.claude/rules

# Windows (PowerShell)
Copy-Item multi-agent-skill\CLAUDE.md $env:USERPROFILE\.claude\CLAUDE.md
Copy-Item -Recurse multi-agent-skill\rules $env:USERPROFILE\.claude\rules
```

#### 其他平台（方法论迁移）

> **注意**：以下方式仅支持方法论层的迁移（分流器逻辑、对抗审查思想、核心原则）。完整多 Agent 协作调度（Wave 并行、子 Agent spawn、独立审计员）需要 Claude Code 环境。

| 平台 | 粘贴位置 | 能获得什么 |
|:---|:---|:---|
| OpenAI Codex | 项目根目录的 `codex.md` 或 system prompt | 分流器 + 对抗审查思想 |
| Cursor | 项目根目录的 `.cursorrules` | 分流器 + 对抗审查思想 |
| Windsurf | 项目根目录的 `.windsurfrules` | 分流器 + 对抗审查思想 |
| GLM / Kimi / DeepSeek | 对话的系统提示词 | 分流器 + 核心原则 |

分流器的 3 个问题（判断任务复杂度）和对抗审查思想（执行者和审查者分离）在任何平台都有效——它们是方法论，不依赖特定工具。

### 试一个简单任务看分流器（1 分钟）

```
/multi-agent Python 的 *args 和 **kwargs 有什么区别？
```

分流器判断：要答案 / 简单 / 代价不大 → 极简模式，直接回答，不派 Agent。和不用 skill 几乎一样——这是对的，简单任务不应该走流程。

### 试一个复杂任务看对抗审查（3 分钟）

```
/multi-agent 设计一个多人协作文档的冲突解决方案。约束：10人同时编辑、离线5-30分钟、版本历史+回滚、自动合并。
```

观察：分流器判框架模式 → 多个 Agent 并行工作 → 批评家逐条审查设计选择。重点看批评家怎么质疑"你为什么这样选"。

### 理解分流器怎么改（1 分钟）

Skill 文件开头的 3 个问题决定分流逻辑。想适配你的场景？直接编辑判据。详见 [Fork 引导指南](docs/fork_guide.md)。

## 想深入？

| 你想做什么           | 看哪份文档                                                                                   |
|:---------------------|:---------------------------------------------------------------------------------------------|
| 了解完整机制设计     | `commands/multi-agent.md`（skill 主文件，约 500 行）                                             |
| 把它改成你的版本     | [`docs/fork_guide.md`](docs/fork_guide.md) — 模块解剖 + 定制区 + 入门修改                     |
| 学习框架构建方法论   | [`docs/framework_methodology.md`](docs/framework_methodology.md) — 从 v1 到 v12.5 的踩坑实录 |
| 看 A/B 实验完整数据  | [`evaluation/AB_TEST.md`](evaluation/AB_TEST.md)                                              |
| 看跨模型验证报告     | [`evaluation/FINAL_REPORT.md`](evaluation/FINAL_REPORT.md) + [`evaluation/SCORING_SHEET.md`](evaluation/SCORING_SHEET.md) |
| 看实际使用案例       | [`examples/cases.md`](examples/cases.md) — 5 个样例覆盖工程/文档/理论/自审查                  |
| 把它写进简历         | [`docs/resume_guide.md`](docs/resume_guide.md) — 简历模板 + 面试问答                          |
| 其他平台怎么用 | 方法论层可迁移（分流器+对抗审查），参见上方「其他平台（方法论迁移）」                      |
| MiMo 用户专属指南    | [`docs/mimo_guide.md`](docs/mimo_guide.md)                                                   |
| 提升整体工程质量     | [`CLAUDE.md`](CLAUDE.md) + [`rules/`](rules/) — 复杂度分级、交付标准、专项规则（仅 Claude Code）|

## 适合谁

- **想入门多 Agent 协作的初学者**：没用过多 Agent 框架？这是一个好的起点——一个 .md 文件，零依赖，5 分钟看到效果，然后自己改改看。不需要会写代码，不需要懂框架原理
- **想用 AI 做项目但不知道从哪开始的人**：Claude Code 用户装上即用；其他平台用户可以迁移方法论思想。已有游戏、文档处理、理论研究等现成案例可以参考
- **想在 AI 浪潮里武装自己的人**：改不了模型没关系，大多数人都改不了。但你可以在应用层做创新——用提示词工程让 AI 团队替你干活，这不是程序员的专利
- **想搭建自己的多 Agent 团队的人**：这个 skill 给你一套现成的调度逻辑和审查机制，你可以在上面加角色、改分流器、适配你的领域——搭出属于你自己的 AI 协作团队
- **想做出东西讲给别人听的学生/工程师**：基于它搭了什么、改了什么、验证了什么——这才是你讲得出故事的东西

## 不适合谁

- **想跟大厂代码工具（Codex、Claude 原生）比写代码性能的人**：定位不同——人家是重型引擎，这是轻量方法论。装上能看到项目能力和开发体验的提升，但不是去跟大厂比肩
- **想跑一堆简单任务的人**：分流器会把简单任务判入极简模式，跳过全部流程，装了和没装差不多
- **需要在非 Claude Code 平台上跑完整多 Agent 调度的人**：Wave 并行、子 Agent spawn、独立审计依赖 Claude Code 的 Agent 工具。其他平台可以迁移方法论层（分流器+对抗审查），但完整调度跑不起来

## 项目结构

### 复制到 `~/.claude/`（Claude Code 用户）

```
~/.claude/
├── commands/
│   └── multi-agent.md          # ★ 核心：skill 主文件（约 500 行），完整多 Agent 调度
├── CLAUDE.md                   # [可选] 全局工程规范（复杂度分级、交付标准、权限管理）
└── rules/                      # [可选] 专项规则
    ├── coding_cycle.md         # 编程执行循环：定位→判断→修改→验证→收尾
    ├── engineering_scorecard.md # 6 维工程能力自评
    ├── multi_agent_improvements.md # Multi-Agent 速查卡
    ├── single_file_html_rules.md   # 单文件 HTML 修改规范
    ├── permission_summary.md   # 自动批准摘要格式
    ├── git_upload_checklist.md # Git 上传前置检查
    ├── python_env.md           # Python 项目默认配置
    └── word_format.md          # Word 文档排版规范
```

**只有 `commands/multi-agent.md` 是必须的。** CLAUDE.md 和 rules/ 是可选增强——即使不装，skill 也能独立运行。

**其他平台**：`commands/multi-agent.md` 中的方法论层（分流器、对抗审查思想、核心原则）可以迁移到你的 system prompt 中，详见上方「其他平台（方法论迁移）」。

### 给人看的（不需要复制，直接在仓库里读）

```
multi-agent-skill/
├── README.md                   # ← 你正在读的这个
├── CHANGELOG.md                # 版本演进（v1→v12.5）
├── LICENSE                     # MIT
├── docs/
│   ├── quickstart.md           # 5 分钟快速上手
│   ├── fork_guide.md           # 怎么改成你的版本
│   ├── framework_methodology.md # 从 v1 到 v12.5 的构建方法论
│   ├── mimo_guide.md           # MiMo 用户指南 + 定位声明
│   ├── resume_guide.md         # 简历模板 + 面试问答
│   ├── failure_cases.md        # 5 个失败案例 + 根因分析
│   ├── tech_summary.md         # 技术摘要（给不想读 500 行全文的人）
│   └── GLOSSARY.md             # 术语表
├── evaluation/
│   ├── AB_TEST.md              # A/B 实验完整数据（pilot study + MiMo/DeepSeek 深度评估）
│   ├── FINAL_REPORT.md         # 跨模型验证最终报告（MiMo 9/54 vs DeepSeek 10/54）
│   ├── SCORING_SHEET.md        # 逐 bug 评分表（18 个预埋 bug × 2 模型）
│   ├── mimo_clean_results/     # MiMo 12 个干净会话输出
│   └── deepseek_results/       # DeepSeek 12 个干净会话输出 + 汇总
├── examples/
│   └── cases.md                # 5 个实际使用样例（含可复现命令）
└── demos/
    ├── angry_birds.html        # 愤怒的小鸟（架构师+执行者+测试员+批评家）
    ├── doc-pipeline/           # PDF→Word（已独立开源，执行者+批评家）
    ├── theory_v3.3_CS OR EE.md # ★ 理论文档 CS/EE 版（推荐，更完整）
    └── theory_v3.3建议看另外一个更好的版本.md  # 理论文档通用版（4轮迭代，文科生友好入口）
```

**最有价值的 3 个文件**：`commands/multi-agent.md`（产品核心）、`docs/fork_guide.md`（定制入口）、`docs/failure_cases.md`（教学价值最高）。

## 诚实声明

**关于验证数据**：
- **A/B 实验**（pilot study）：3 个任务、1 个用户、1 次执行。不能做统计推断。核心发现（批评家找到 2 个严重漏洞）是可复现的因果发现，但不是统计结论。
- **跨模型验证**（预埋 bug 法）：MiMo (Claude) + DeepSeek-v4-pro，6 任务 × 2 条件，每条件全新空白对话。无 Skill 基线 0/54（跨模型一致），有 Skill 增量 MiMo +9、DeepSeek +10。批评家擅长代码正确性和攻击面分析，弱于分布式系统和文件系统语义。

**关于规则执行**：多条规则中硬机制 3 条。v12 审计发现"全部规则在实际任务中没被执行"。后来硬化了审计机制（自检 + 元检查 + 独立审计员），但验证数据仍然不足。

**关于经验沉淀**："经验写了不用"是最普遍的问题。v11 加了强制转化机制，但实际效果依赖调度员（Claude 模型）的判断力，不是真正的自动化学习。

**关于篇幅**：skill 主文件约 500 行，读完 15-20 分钟，理解需要 1 小时以上。对大多数用户偏重。如果批评家机制对你没用，这个 skill 的大部分内容就不值得。

## 参与共创

这个框架本身就是一个多 Agent 团队的产出——从 README 到文档到实验设计，都由它自己调度完成。如果你用这个 skill 做出了自己的项目、改出了自己的版本、或者跑出了有意思的实验结果，欢迎分享：

- **分享你的成果**：在 GitHub Issues 里贴出你用这个 skill 做了什么、改了什么、发现了什么——你的案例会成为后来者的参考
- **成为共创者**：如果你基于这个框架做了深度定制（改分流器、加角色、适配新领域），欢迎提交 PR 或联系作者，优秀的贡献者将作为共创者署名
- **反馈问题**：发现 bug、流程漏洞、或者有更好的设计思路，直接开 Issue——批评家精神适用于开源本身

> 这个框架的目标不是做一个完美的工具，而是让每个人都能在自己的领域上搭出适合自己的多 Agent 团队。你的版本比我的版本更有价值——因为它是为你的场景设计的。

作者：[kesusu](https://github.com/kesusu)

## 致谢

致敬 AI 浪潮下的每一位开发者。

我们可能改不了模型、训不了参数，但我们可以用双手在应用层搭建属于自己的东西——一个 skill、一个项目、一个团队。每一行提示词、每一次版本迭代、每一个跑通的 demo，都是这个时代留下的印记。

不必等到完美才开始。风已经起了，出发就好。

## License

MIT
