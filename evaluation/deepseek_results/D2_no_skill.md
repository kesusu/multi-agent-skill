# Session 8 — D2 分页 · 无 Skill

## 任务

设计一个通用的 REST API 分页方案。要求：
1. 支持 offset/limit 和 cursor 两种模式
2. 返回总条数、当前页、是否有下一页
3. 处理空结果、越界页码
4. 提供 SDK 封装（Python）

## 实现

创建了 `D2_pagination/pagination_sdk.py`。

### 协议设计

**统一响应格式**：
```json
{
  "items": [...],
  "pagination": {
    "mode": "offset|cursor",
    "total_count": 100,
    "page": 1,
    "has_next": true,
    "next_cursor": null
  }
}
```

**两种模式**：
- `offset/limit`：传 `offset` + `limit`，返回 `total_count`、`total_pages`
- `cursor`：传 `cursor`（base64url 编码锚点），返回 `next_cursor`

### 边界情况覆盖

| 场景 | 处理 |
|---|---|
| 空数据集 | items=[], total_count=0, has_next=false |
| offset 越界 | 自动 clamp 到合法范围，不返回 4xx |
| offset 负数 | 自动 clamp 到 0 |
| cursor 到尾 | has_next=false, next_cursor=null |
| 无效 cursor | 容错回退到首页 |
| limit 越界 | 参数校验 1-100 |

### SDK API

```python
from pagination_sdk import OffsetPaginator, CursorPaginator

# Offset-based
p = OffsetPaginator(total_count=100)
page = p.paginate(offset=0, limit=20)

# Cursor-based
p = CursorPaginator(items, cursor_field="id")
page = p.paginate(cursor=None, limit=20)
```

### 验证结果

13 项测试全部通过：
```
[PASS] offset_empty
[PASS] offset_normal
[PASS] offset_last_page
[PASS] offset_beyond_bounds
[PASS] offset_negative
[PASS] cursor_first_page
[PASS] cursor_second_page
[PASS] cursor_last_page
[PASS] cursor_empty
[PASS] cursor_at_end
[PASS] response_format
[PASS] error_response
[PASS] cursor_invalid_graceful
```

### 代码位置
- `D2_pagination/pagination_sdk.py` — SDK 实现
- `D2_pagination/test_pagination.py` — 测试
