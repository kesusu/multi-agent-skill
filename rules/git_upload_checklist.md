# Git 上传前置检查

上传文件夹到 GitHub 前，必须按顺序执行以下检查，确认方案后才 add/commit/push。

## 检查步骤

1. **目录大小**：`du -sh <目录>` — 判断是否适合直接 push
2. **大文件排查**：`find -size +50M` — GitHub 单文件限 100MB
3. **现有配置**：是否有 `.gitignore`、是否已有 git 仓库（`git status`）、是否已有远程（`git remote -v`）
4. **用户意图确认**：传什么？排除什么？模型文件要不要？（注：git 操作已授权自批，若用户之前已明确意图则直接执行）

## 方案选择

| 场景 | 方案 |
|---|---|
| 总量 < 100MB，无超大文件 | 直接 init/add/commit/push |
| 有 > 100MB 文件 | .gitignore 排除或 Git LFS |
| 已有仓库+远程 | 直接 commit + push |
| 历史含大文件需清理 | orphan branch 重建（需向用户说明会丢历史） |

## 经验

- .gitignore 白名单模式（`*` + `!pattern`）适合"只传代码"场景，但注意 unignore 路径要覆盖模型目录。
- 模型文件 (.pth/.pkl/.joblib) 通常不大，用户倾向作为备份上传，不应默认排除。
- HTTP 500 / 超时：增大 `http.postBuffer 524288000`，或减小推送体积。
- force push 会重写远程历史，需用户确认。
