# 工程训练 — 让 Claude Code 做编程题，自动跑测试打分

> 一个零依赖的 benchmark 框架：给 AI 一道编程题，看它能不能跑通。

## 这是什么

给 Claude Code 一个有明确规格的任务（比如"解析时间字符串"），让它写代码，用标准库评分脚本自动跑 30 个测试用例，输出 PASS 或 FAIL。

**不是**：让 AI "听起来聪明"的评测。**是**：让 AI 产出的代码能不能跑通的评测。

## 前置条件

- **Python 3.6+**（用了 f-string 和 pathlib，标准库即可，不需要 pip install 任何东西）
- **Claude Code CLI**（可选，仅"完整训练流程"需要）：安装见 [claude.ai/code](https://claude.ai/code)

**没有 Claude CLI？** 直接用 `run_eval.py` 评分——手动写代码放进 `claude_attempt/` 文件夹，然后 `python run_eval.py claude_attempt` 即可。评分脚本不依赖 Claude。

## 文件结构

```
engineering-train/
├── README.md               ← 你在读的这个
├── train_round.py          ← 训练 harness（调用 Claude CLI 写代码+评分）
├── run_all.py              ← 批量跑所有练习
└── exercises/
    ├── duration_parser/    ← 练习 1：时间字符串解析
    │   ├── task.md         ← 需求规格（给 AI 看的）
    │   ├── run_eval.py     ← 评分脚本（30 个测试用例）
    │   ├── report.md       ← 运行报告
    │   ├── claude_attempt/ ← AI 要在这里写代码
    │   │   └── duration_parser.py  ← 空壳，raise NotImplementedError
    │   └── codex_attempt/  ← 人工 baseline 对照
    │       └── duration_parser.py  ← 能通过所有测试的参考实现
    └── config_merge/       ← 练习 2：嵌套配置合并
        ├── task.md
        ├── run_eval.py     ← 6 类场景 + 对象别名检查
        ├── report.md
        ├── claude_attempt/
        │   └── config_merge.py
        └── codex_attempt/
            └── config_merge.py
```

**文件关系**：`task.md` 定义需求 → `claude_attempt/*.py` 是 AI 的实现 → `run_eval.py` 读取实现并跑测试 → `report.md` 记录结果和教训。

## 快速上手（2 分钟）

```bash
# 1. 看评分脚本怎么工作（baseline 应该 PASS）
cd exercises/duration_parser
python run_eval.py codex_attempt    # → PASS

# 2. 看空壳实现怎么 FAIL
python run_eval.py claude_attempt   # → FAIL（NotImplementedError）

# 3. 读需求规格
cat task.md                         # 30 个边界用例的完整规格
```

这三步不需要 Claude CLI，不需要任何依赖，clone 下来就能跑。

## 完整训练流程（需要 Claude CLI）

```bash
# 单个练习：生成 prompt → 调 Claude 写代码 → 自动评分
python train_round.py exercises/duration_parser --run-claude

# 全部练习
python run_all.py
```

`train_round.py` 做了什么：
1. 读 `exercises/<name>/task.md`，拼成约束 prompt
2. 通过 `claude -p --permission-mode acceptEdits` 调 Claude Code 写代码
3. 自动跑 `run_eval.py` 评分
4. 输出 PASS/FAIL 和失败用例列表

不加 `--run-claude` 时只生成 prompt 文件和打印手动命令，不调用 Claude。

## 六维能力记分卡

PASS/FAIL 只告诉你"代码跑通没有"。六维记分卡告诉你"工程能力在哪"：

| 维度 | 评估什么 | 具体怎么看 |
|:---|:---|:---|
| 目标理解 | task.md 的规格和约束是否被准确理解 | 需求里写的边界用例是否都覆盖了 |
| 上下文把握 | 文件结构、输入输出格式是否注意到 | 有没有改错文件、漏看依赖 |
| 根因判断 | 测试失败后能否定位根因 | 是改了真正出错的地方，还是在表面打补丁 |
| 方案质量 | 实现是否简洁、健壮 | 有没有过度设计或遗漏边界 |
| 实现安全性 | 是否避免输入突变、共享可变引用 | config_merge 的 `id()` 检查就是测这个 |
| 验证循环 | 是否运行评估脚本、失败后是否迭代修复 | 只写代码不跑测试 = 验证循环 0 分 |

**当前状态**：记分卡是人工评估维度，`run_eval.py` 只自动输出 PASS/FAIL。六维打分需要人工或用 multi-agent skill 的批评家角色完成。

## 现有练习

| 练习 | 训练重点 | 测试用例 |
|:---|:---|:---|
| `duration_parser` | 解析规格、边界用例、验证驱动修复 | 12 个有效 + 18 个无效 = 30 个 |
| `config_merge` | 嵌套数据处理、不可变性、删除语义 | 6 类场景 + 对象别名检查（`_mutable_ids()`） |

**config_merge 的独特设计**：不只检查返回值对不对，还检查返回值有没有和输入共享可变对象引用（通过 `id()` 交集检查）。一个实现可以返回正确形状，但仍泄漏可变引用——这种隐性 bug 只有别名检查能抓到。

## 怎么加自己的练习

```bash
# 1. 创建目录结构
mkdir -p exercises/my_exercise/claude_attempt exercises/my_exercise/codex_attempt

# 2. 写需求规格
#    文件：exercises/my_exercise/task.md
#    内容：函数签名 + 输入输出格式 + 边界用例（越"尖锐"越好）
#    参考：exercises/duration_parser/task.md 的格式

# 3. 写评分脚本
#    文件：exercises/my_exercise/run_eval.py
#    规范：
#      - 只用标准库（importlib + sys）
#      - 接收 1 个参数：attempt 目录路径
#      - 用 sys.path.insert + importlib.import_module 加载实现
#      - 打印 PASS 或 FAIL + 失败用例列表
#      - 退出码 0=PASS，1=FAIL
#    参考：exercises/duration_parser/run_eval.py（最简单的模板）

# 4. 写空壳实现
#    文件：exercises/my_exercise/claude_attempt/my_exercise.py
#    注意：文件名必须和 importlib.import_module 的参数一致
echo 'def my_func(): raise NotImplementedError("Implement this")' > exercises/my_exercise/claude_attempt/my_exercise.py

# 5. 写 baseline（可选但推荐）
#    人工写一个能通过所有测试的实现，验证你的评分脚本和难度设置
```

**关键约束**：`run_eval.py` 用 `importlib.import_module("模块名")` 加载实现，所以 `claude_attempt/` 下的 `.py` 文件名必须和模块名一致（如 `duration_parser.py`、`config_merge.py`）。

## 关键洞察

### 1. 先让评估 harness 可靠，再谈模型改进

> "First make the evaluation harness reliable; a model cannot improve against an unstable scoreboard."

我们最初用 pytest 做评分，发现 pytest 的 import 机制和 `sys.path.insert` 冲突，导致测试结果不稳定。改用零依赖的 `importlib` + `sys` 后，评分脚本本身不再出问题。**如果你的评分工具有 bug，你优化模型时看到的所有"改进"都可能是幻觉。**

### 2. 小任务 + 尖锐边界 > 大任务 + 模糊需求

`duration_parser` 只是一个函数，但 30 个测试用例覆盖了：
- 空串、纯空格、纯数字（无单位）
- 负数、小数、重复单位（`1h 2h`）
- 冒号格式的边界（`1:60`、`1:00:60`）
- 短单位不允许空格（`1 h` → ValueError）、长单位允许空格（`2 hours` → OK）

**训练价值不在任务大小，在边界是否足够"尖锐"。** 一个大任务 + 模糊需求的练习，不如一个小任务 + 30 个边界用例的练习。

### 3. 基线对照组防止"过了就觉得好"

每个练习都有 `codex_attempt/`（人工实现），和 Claude 的实现跑同一套测试。作用：
- baseline 能 PASS → 说明评分脚本和难度设置合理
- Claude 也能 PASS → 说明 AI 能处理这个难度
- 如果 Claude PASS 但 baseline FAIL → 评分脚本可能有 bug
- 如果 Claude FAIL 但 baseline PASS → AI 确实有改进空间

### 4. 每轮只提取 1-2 条教训

从 `config_merge` 提取的教训："嵌套数据任务应同时测值相等和对象别名，因为方案可以返回正确形状但仍泄漏可变引用。" 这条教训可以直接复制到其他团队——它不依赖特定框架，是通用的工程验证模式。

## 运行报告（2026-05-10）

| 练习 | Claude | Baseline |
|:---|:---:|:---:|
| duration_parser | PASS | PASS |
| config_merge | PASS | PASS |

详见 `exercises/*/report.md`。

## 与 multi-agent skill 的关系

| 维度 | 工程训练 | multi-agent skill |
|:---|:---|:---|
| 目标 | 训练单个 AI 的编码能力 | 多 Agent 协作调度复杂任务 |
| 评估 | 量化（PASS/FAIL + 六维记分卡） | 流程合规（8 项审计检查） |
| 粒度 | 单文件函数级别 | 跨模块方案级别 |
| 比喻 | 单兵作战训练 | 团队协作训练 |

两者互补：一个连单函数都写不对的 AI，派再多 Agent 也没用。
