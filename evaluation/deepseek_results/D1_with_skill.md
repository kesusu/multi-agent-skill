# Session 7 — D1 文件去重 · 有 Skill

## 多 Agent 框架分流

| Q | 判断 |
|---|---|
| Q1: 答案/方案? | 方案 |
| Q2: 简单? | 否（CLI 工具，需处理多种边界情况） |
| Q3: 代价大? | 不大 |

→ **框架模式**

## 任务地图

```
- 任务类型：工程实现
- 经验注入：无
- 子任务：
  - T1: CLI 参数设计 — 架构师，产出：argparse 接口定义，depends_on: []
  - T2: MD5 哈希 + 重复检测 — 执行者，产出：find_duplicates()，depends_on: []
  - T3: 文件移动 + dry-run — 执行者，产出：移动逻辑，depends_on: [T2]
  - T4: 统计输出 — 执行者，产出：格式化报告，depends_on: [T3]
  - T5: 测试验证 — 测试员，产出：使用 test_files 验证，depends_on: [T4]
- 角色：架构师、执行者、测试员、批评家
- 验收标准：CLI 工具可用、--dry-run 正常、统计准确、文件正确移动
```

## 计划审查

| # | 检查点 | 判定 | 说明 |
|---|---|---|---|
| 1 | 子任务完整性 | pass | 覆盖了所有四项需求 |
| 2 | depends_on | fail | T4 对 T2 有信息依赖（统计需要知道哪些是重复文件），T1 被遗漏在依赖链外 |
| 3 | 角色分配 | pass | 执行者覆盖实现，测试员独立验证 |
| 4 | 职责重叠 | pass | 各子任务职责清晰 |
| 5 | 假设一致性 | pass | 产出物之间无矛盾 |

**修正**：T4 depends_on 增加 T2；T2 depends_on 增加 T1

## Wave 调度

**Wave 1**: T1 (架构师) + T2 (执行者) — 并行启动
**Wave 2**: T3 (执行者) + T4 (执行者) — 依赖 T2
**Wave 3**: T5 (测试员) — 依赖 T4

## 批评家反馈

1. **严重**：`find_duplicates` 未处理二进制文件与大文件 → 采用 8192 字节分块读取
2. **建议**：`.duplicates/` 内文件名冲突处理 → 增加自动编号后缀
3. **建议**：增加对 `.duplicates` 目录的递归扫描保护

## 最终产出

代码实现 `D1_file_dedup/dedup.py`，与无 Skill 版本相同的核心功能，但多了：
- 分块读取（8192 bytes）处理大文件
- 文件名冲突自动处理（`_1`, `_2` 后缀）
- `.duplicates` 目录递归保护
- 更完善的错误处理

### 验证结果

```
--- DRY RUN ---
Files scanned:    8
Duplicate groups: 2
Duplicate files:  3
Space saved:      114 bytes (0.1 KB)
```

### 与无 Skill 版本对比

| 维度 | 无 Skill | 有 Skill |
|---|---|---|
| 大文件处理 | 全量读入内存 | 分块读取 8192 bytes |
| 文件名冲突 | 未处理 | 自动编号 |
| 递归保护 | 无 | 跳过 .duplicates |
| 错误处理 | 崩溃 | warning + 跳过 |
