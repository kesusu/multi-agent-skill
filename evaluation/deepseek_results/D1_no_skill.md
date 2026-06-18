# Session 1 — D1 文件去重 · 无 Skill

## 任务

写一个 Python CLI 工具，扫描指定目录下的重复文件并处理。要求：
1. 用 MD5 哈希判断文件是否重复
2. 重复文件保留一个，其余移到 .duplicates/ 文件夹
3. 支持 --dry-run 模式只报告不移动
4. 输出统计：扫描文件数、重复组数、节省空间

## 实现

创建了 `D1_file_dedup/dedup.py`，完整实现：

### 核心设计
- **MD5 分块哈希**：8192 字节分块读取，避免大文件 OOM
- **重复分组**：`{hash: [filepaths]}` 字典，过滤掉只有一个文件的组
- **安全移动**：保留每组第一个文件为 [KEEP]，其余为 [DUP]，处理 .duplicates/ 内的文件名冲突（自动加后缀 `_1`, `_2`）
- **统计输出**：扫描文件数、重复组数、重复文件数、节省字节数/KB

### 用法

```bash
# 预览模式
python dedup.py test_files --dry-run

# 执行去重
python dedup.py test_files
```

### 验证结果

测试 `test_files/` 目录（8 个文件）：

```
--- DRY RUN ---
Files scanned:    8
Duplicate groups: 2
Duplicate files:  3
Space saved:      114 bytes (0.1 KB)
```

**重复组 1** (MD5: d99e2d693807):
- [KEEP] file_a.txt
- [DUP]  file_b.txt, file_e.txt

**重复组 2** (MD5: f5c1fb10c081):
- [KEEP] report_2024.csv
- [DUP]  report_backup.csv

执行后 3 个重复文件正确移入 .duplicates/。恢复后目录保留原始文件。

### 代码位置

`D1_file_dedup/dedup.py`
