# Demos — 多 Agent 协作框架的实际产出

这些是用 multi-agent skill 做出来的项目，不是 skill 本身。

**第一次来？** 建议先看 [主 README](../README.md) 了解框架，然后从 [`engineering-train/`](engineering-train/) 或 [`self-learning/`](self-learning/) 开始——这两个最容易理解和复现。

每个 demo 的协作过程详见 [examples/cases.md](../examples/cases.md)。

## 目录

| Demo | 一句话 | 文件位置 | 运行方式 |
|:---|:---|:---|:---|
| 工程训练 | 让 Claude Code 做编程题，自动跑测试打分 | [`engineering-train/`](engineering-train/) | `python run_eval.py`（零依赖） |
| 自学习 | "学查分离"的 AI 辅助学习，激光原理考试案例 | [`self-learning/`](self-learning/) | 需要 Claude Code + multi-agent skill |
| 自审查 | 用客观痕迹代替主观声明，8 项审计检查清单 | [`self-audit/`](self-audit/) | 检查清单可直接复制使用 |
| 愤怒的小鸟 | 纯 HTML+JS，910 行，2D 物理+关卡+音频 | [`angry_birds/`](angry_birds/) | 浏览器直接打开 |
| PDF→Word | 扫描 PDF 转可编辑 Word，LaTeX 公式双击可改 | [`doc-pipeline/`](doc-pipeline/) | Python + pandoc |
| 理论文档 | "AI 时代你真正的活儿是什么"，含 CS/EE 版和通用版 | [`theory/`](theory/) | 4 轮迭代产出的文档 |

## 快速指引

- **想跑代码看效果？** → [`engineering-train/`](engineering-train/)，clone 下来 `python run_eval.py codex_attempt` 直接看 PASS/FAIL
- **想学怎么让 AI 不敢偷懒？** → [`self-audit/`](self-audit/)，`audit_checklist.md` 有 8 项检查（4 项通用 + 4 项需多 Agent 环境）
- **想用 AI 辅助学习？** → [`self-learning/`](self-learning/)，先看 [`答题诊断报告`](self-learning/sample_output/答题诊断报告.md) 理解"查"的价值
- **想看游戏 demo？** → [`angry_birds/`](angry_birds/)，下载 `angry_birds.html` 用浏览器打开即可玩
- **想看文档处理？** → [`doc-pipeline/`](doc-pipeline/)，已独立开源的完整项目（有独立 README 和 LICENSE）
- **想看理论写作？** → [`theory/`](theory/)，推荐先看 CS/EE 版（更完整）

