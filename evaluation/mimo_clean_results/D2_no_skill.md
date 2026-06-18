# Session 8 — D2 分页 (无 Skill)

## 任务

设计一个通用的 REST API 分页方案。

## 实现

### paginator.py

代码与 Session 2（有 Skill）相同。Skill 版本经过了批评家审查并修复了 3 个严重问题：
1. 模块级 sys.stdout 替换 → 移至 __main__ 守卫
2. _default_encode_cursor 使用 str() → 改为 NotImplementedError
3. limit or 吞零 → limit if limit is not None

无 Skill 版本使用的是已修复后的最终代码。

### 核心结构

```
1. 数据结构
   - PageParams / CursorParams: 分页请求参数（含校验）
   - PageResult / CursorResult: 分页结果（含 to_dict() 序列化）

2. offset/limit 分页
   - paginate(): 内存序列分页
   - paginate_query(): 数据库回调分页

3. cursor 分页
   - paginate_cursor(): 内存序列 cursor 分页
   - paginate_cursor_query(): 数据库回调 cursor 分页

4. SDK 封装
   - Paginator[T]: 统一入口，支持 .page() 和 .cursor_page()
   - from_query() / from_cursor_query() 工厂方法

5. 边界处理
   - 空数据、越界页码、非法参数（ValueError）
   - cursor 到末尾返回 next_cursor=None
```

## 测试结果

```
offset/limit: page=1/5/10/999 全部正确
cursor: 3 轮迭代，next_cursor 链式传递正确
边界: 空数据、越界、负数参数、limit 超限全部抛 ValueError
to_dict: 序列化格式正确
全部演示通过
```

## 功能覆盖

- [x] 支持 offset/limit 和 cursor 两种模式
- [x] 返回总条数、当前页、是否有下一页
- [x] 处理空结果、越界页码
- [x] 提供 SDK 封装（Python）
