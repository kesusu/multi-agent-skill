# Session 1 — D1 文件去重 (无 Skill)

## 任务

写一个 Python CLI 工具，扫描指定目录下的重复文件并处理。

## 实现

### dedup.py

```python
#!/usr/bin/env python3
"""文件去重 CLI 工具 — 扫描指定目录下的重复文件并处理。"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from collections import defaultdict
from pathlib import Path

# Windows 终端 UTF-8 支持
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def md5_of(filepath: str, chunk_size: int = 8192) -> str:
    """计算文件的 MD5 哈希值。"""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def scan_directory(directory: str) -> dict[str, list[str]]:
    """扫描目录，返回 {md5: [file_paths]} 的字典。"""
    groups: dict[str, list[str]] = defaultdict(list)
    for root, _, files in os.walk(directory):
        for name in files:
            fp = os.path.join(root, name)
            file_hash = md5_of(fp)
            groups[file_hash].append(fp)
    return dict(groups)


def find_duplicates(groups: dict[str, list[str]]) -> list[tuple[str, list[str]]]:
    """筛选出有重复的组。"""
    return [(h, paths) for h, paths in groups.items() if len(paths) > 1]


def format_size(size_bytes: int) -> str:
    """人类可读的文件大小。"""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main():
    parser = argparse.ArgumentParser(description="扫描并处理重复文件")
    parser.add_argument("directory", help="要扫描的目录路径")
    parser.add_argument("--dry-run", action="store_true", help="只报告不移动文件")
    args = parser.parse_args()

    target = os.path.abspath(args.directory)
    if not os.path.isdir(target):
        print(f"错误：{target} 不是有效目录")
        return 1

    print(f"扫描目录：{target}\n")
    groups = scan_directory(target)
    dup_groups = find_duplicates(groups)

    total_files = sum(len(v) for v in groups.values())
    total_saved = 0

    print(f"扫描文件数：{total_files}")
    print(f"重复组数：{len(dup_groups)}\n")

    if not dup_groups:
        print("未发现重复文件。")
        return 0

    dup_dir = os.path.join(target, ".duplicates")
    if not args.dry_run:
        os.makedirs(dup_dir, exist_ok=True)

    for i, (file_hash, paths) in enumerate(dup_groups, 1):
        paths_sorted = sorted(paths)
        keep = paths_sorted[0]
        duplicates = paths_sorted[1:]

        file_size = os.path.getsize(keep)
        saved = file_size * len(duplicates)
        total_saved += saved

        print(f"组 {i} (MD5: {file_hash[:12]}...):")
        print(f"  保留：{os.path.relpath(keep, target)}")
        for dup in duplicates:
            rel = os.path.relpath(dup, target)
            if args.dry_run:
                print(f"  [dry-run] 将移动：{rel}")
            else:
                dest = os.path.join(dup_dir, os.path.basename(dup))
                counter = 1
                base, ext = os.path.splitext(dest)
                while os.path.exists(dest):
                    dest = f"{base}_{counter}{ext}"
                    counter += 1
                shutil.move(dup, dest)
                print(f"  已移动：{rel} → .duplicates/")
        print()

    print("--- 统计 ---")
    print(f"扫描文件数：{total_files}")
    print(f"重复组数：{len(dup_groups)}")
    print(f"节省空间：{format_size(total_saved)}")
    if args.dry_run:
        print("(dry-run 模式，未实际移动文件)")

    return 0


if __name__ == "__main__":
    exit(main())
```

## 测试结果

### dry-run 模式

```
扫描目录：C:\Users\ke\Desktop\玩\multi_agent\evaluation\mimo_test\D1_file_dedup\test_files

扫描文件数：8
重复组数：2

组 1 (MD5: d99e2d693807...):
  保留：file_a.txt
  [dry-run] 将移动：file_b.txt
  [dry-run] 将移动：file_e.txt

组 2 (MD5: f5c1fb10c081...):
  保留：report_2024.csv
  [dry-run] 将移动：report_backup.csv

--- 统计 ---
扫描文件数：8
重复组数：2
节省空间：114.0 B
(dry-run 模式，未实际移动文件)
```

### 实际执行

```
扫描目录：C:\Users\ke\Desktop\玩\multi_agent\evaluation\mimo_test\D1_file_dedup\test_files

扫描文件数：8
重复组数：2

组 1 (MD5: d99e2d693807...):
  保留：file_a.txt
  已移动：file_b.txt → .duplicates/
  已移动：file_e.txt → .duplicates/

组 2 (MD5: f5c1fb10c081...):
  保留：report_2024.csv
  已移动：report_backup.csv → .duplicates/

--- 统计 ---
扫描文件数：8
重复组数：2
节省空间：114.0 B
```

## 功能覆盖

- [x] MD5 哈希判断重复
- [x] 重复文件保留一个，其余移到 .duplicates/
- [x] --dry-run 模式只报告不移动
- [x] 输出统计：扫描文件数、重复组数、节省空间
