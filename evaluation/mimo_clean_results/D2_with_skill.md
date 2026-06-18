# Session 2 — D2 分页 (有 Skill)

## 任务

设计一个通用的 REST API 分页方案。

## 流程：/multi-agent 框架模式

### 0秒分流器
- Q1: 方案 → Q2: 是 → Q3: 不大 → **框架模式**

### 任务地图
- 子任务：T1 核心分页逻辑 → T2 SDK 封装 → T3 代码审查 → T4 验收
- 角色：架构师、执行者、批评家、验收者

### 调度
- Wave 1: 架构师设计核心逻辑 + SDK（合并执行）
- Wave 2: 批评家审查

### 批评家审查结果

| 级别 | 数量 | 关键项 |
|---|---|---|
| 致命 | 0 | — |
| 严重 | 3 | 模块级 stdout 劫持、默认游标编码不可逆、cursor items 长度无断言 |
| 轻微 | 4 | 游标缺 decode、query_fn 灵活性足够、类型擦除、limit falsy 吞零 |

### 修复

1. **删除模块级 sys.stdout/stderr 替换** — SDK 库不应有 import 副作用，UTF-8 处理移至 `__main__` 守卫
2. **`_default_encode_cursor` 改为抛 NotImplementedError** — 强制调用方提供游标编码，避免 str() 不稳定
3. **`paginate_cursor` 增加 `__debug__` 断言** — 传入 items 不足 limit 时发出 warnings.warn
4. **`limit or` 改为 `limit if limit is not None`** — 避免 limit=0 被 falsy 吞掉

## 实现

### paginator.py

```python
"""
通用 REST API 分页方案 — SDK 核心

支持 offset/limit 与 cursor 两种模式。
兼容 Python 3.8+
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Generic, List, Optional, Sequence, TypeVar

T = TypeVar("T")

# ──────────────────────────────────────────────
# 1. 数据结构
# ──────────────────────────────────────────────


@dataclass(frozen=True)
class PageParams:
    """offset/limit 分页请求参数"""

    page: int = 1       # 页码，从 1 开始
    limit: int = 20     # 每页条数

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError(f"page 必须 >= 1，收到 {self.page}")
        if self.limit < 1:
            raise ValueError(f"limit 必须 >= 1，收到 {self.limit}")
        if self.limit > 1000:
            raise ValueError(f"limit 上限 1000，收到 {self.limit}")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


@dataclass(frozen=True)
class CursorParams:
    """cursor 分页请求参数"""

    cursor: Optional[str] = None   # 游标值，None 表示从头开始
    limit: int = 20                # 每页条数

    def __post_init__(self) -> None:
        if self.limit < 1:
            raise ValueError(f"limit 必须 >= 1，收到 {self.limit}")
        if self.limit > 1000:
            raise ValueError(f"limit 上限 1000，收到 {self.limit}")


@dataclass(frozen=True)
class PageResult(Generic[T]):
    """offset/limit 分页结果"""

    items: List[T]
    total: int          # 总条数
    page: int           # 当前页码
    limit: int          # 每页条数
    total_pages: int    # 总页数
    has_next: bool      # 是否有下一页
    has_prev: bool      # 是否有上一页

    def to_dict(self) -> dict[str, Any]:
        """序列化为 API 响应字典"""
        return {
            "items": self.items,
            "pagination": {
                "total": self.total,
                "page": self.page,
                "limit": self.limit,
                "total_pages": self.total_pages,
                "has_next": self.has_next,
                "has_prev": self.has_prev,
            },
        }


@dataclass(frozen=True)
class CursorResult(Generic[T]):
    """cursor 分页结果"""

    items: List[T]
    next_cursor: Optional[str]   # 下一页游标，None 表示已到末尾
    has_next: bool
    limit: int
    count: int                   # 当前页实际返回条数

    def to_dict(self) -> dict[str, Any]:
        """序列化为 API 响应字典"""
        return {
            "items": self.items,
            "pagination": {
                "next_cursor": self.next_cursor,
                "has_next": self.has_next,
                "limit": self.limit,
                "count": self.count,
            },
        }


# ──────────────────────────────────────────────
# 2. offset/limit 分页
# ──────────────────────────────────────────────


def paginate(
    items: Sequence[T],
    params: PageParams,
) -> PageResult[T]:
    total = len(items)
    total_pages = max(1, (total + params.limit - 1) // params.limit)

    if params.page > total_pages:
        return PageResult(
            items=[], total=total, page=params.page,
            limit=params.limit, total_pages=total_pages,
            has_next=False, has_prev=params.page > 1,
        )

    start = params.offset
    end = start + params.limit
    page_items = list(items[start:end])

    return PageResult(
        items=page_items, total=total, page=params.page,
        limit=params.limit, total_pages=total_pages,
        has_next=params.page < total_pages, has_prev=params.page > 1,
    )


def paginate_query(
    query_fn: Callable[[int, int], Sequence[T]],
    count_fn: Callable[[], int],
    params: PageParams,
) -> PageResult[T]:
    total = count_fn()
    total_pages = max(1, (total + params.limit - 1) // params.limit)

    if params.page > total_pages:
        return PageResult(
            items=[], total=total, page=params.page,
            limit=params.limit, total_pages=total_pages,
            has_next=False, has_prev=params.page > 1,
        )

    items = list(query_fn(params.offset, params.limit))
    return PageResult(
        items=items, total=total, page=params.page,
        limit=params.limit, total_pages=total_pages,
        has_next=params.page < total_pages, has_prev=params.page > 1,
    )


# ──────────────────────────────────────────────
# 3. cursor 分页
# ──────────────────────────────────────────────


def paginate_cursor(
    items: Sequence[T],
    params: CursorParams,
    *,
    encode_cursor: Callable[[T], str],
) -> CursorResult[T]:
    if __debug__ and len(items) < params.limit:
        import warnings
        warnings.warn(
            f"paginate_cursor 收到 {len(items)} 条数据但 limit={params.limit}，"
            f"期望至少 {params.limit} 条（建议传入 limit+1）。可能丢失最后一页。",
            stacklevel=2,
        )
    limit = params.limit
    has_next = len(items) > limit
    page_items = list(items[:limit])
    next_cursor = encode_cursor(page_items[-1]) if has_next and page_items else None

    return CursorResult(
        items=page_items, next_cursor=next_cursor,
        has_next=has_next, limit=limit, count=len(page_items),
    )


def paginate_cursor_query(
    query_fn: Callable[[Optional[str], int], Sequence[T]],
    params: CursorParams,
    *,
    encode_cursor: Callable[[T], str],
) -> CursorResult[T]:
    limit = params.limit
    items = list(query_fn(params.cursor, limit + 1))
    has_next = len(items) > limit
    page_items = items[:limit]
    next_cursor = encode_cursor(page_items[-1]) if has_next and page_items else None

    return CursorResult(
        items=page_items, next_cursor=next_cursor,
        has_next=has_next, limit=limit, count=len(page_items),
    )


# ──────────────────────────────────────────────
# 4. SDK 封装 — Paginator 类
# ──────────────────────────────────────────────


class Paginator(Generic[T]):
    def __init__(
        self,
        data: Optional[Sequence[T]] = None,
        *,
        default_limit: int = 20,
        encode_cursor: Optional[Callable[[T], str]] = None,
    ) -> None:
        self._data: Sequence[T] = data if data is not None else []
        self._default_limit = default_limit
        self._encode_cursor = encode_cursor or self._default_encode_cursor
        self._query_fn: Optional[Callable[[int, int], Sequence[T]]] = None
        self._count_fn: Optional[Callable[[], int]] = None
        self._cursor_query_fn: Optional[Callable[[Optional[str], int], Sequence[T]]] = None

    @classmethod
    def from_query(
        cls, *, query_fn, count_fn, default_limit=20, encode_cursor=None,
    ) -> Paginator[T]:
        p = cls(default_limit=default_limit, encode_cursor=encode_cursor)
        p._query_fn = query_fn
        p._count_fn = count_fn
        return p

    @classmethod
    def from_cursor_query(
        cls, *, query_fn, default_limit=20, encode_cursor,
    ) -> Paginator[T]:
        p = cls(default_limit=default_limit, encode_cursor=encode_cursor)
        p._cursor_query_fn = query_fn
        return p

    def page(self, page: int = 1, limit: Optional[int] = None) -> PageResult[T]:
        params = PageParams(page=page, limit=limit if limit is not None else self._default_limit)
        if self._query_fn and self._count_fn:
            return paginate_query(self._query_fn, self._count_fn, params)
        return paginate(self._data, params)

    def cursor_page(
        self, cursor: Optional[str] = None, limit: Optional[int] = None,
    ) -> CursorResult[T]:
        params = CursorParams(cursor=cursor, limit=limit if limit is not None else self._default_limit)
        if self._cursor_query_fn:
            return paginate_cursor_query(
                self._cursor_query_fn, params, encode_cursor=self._encode_cursor
            )
        return paginate_cursor(self._data, params, encode_cursor=self._encode_cursor)

    @staticmethod
    def _default_encode_cursor(item: T) -> str:
        raise NotImplementedError(
            "cursor 分页必须提供 encode_cursor 参数。"
            "示例：Paginator(data, encode_cursor=lambda item: base64.urlsafe_b64encode(str(item.id).encode()).decode())"
        )
```

## 测试结果

```
============================================================
offset/limit 分页演示
============================================================
  page=1: items=[1, 2, 3]... total=100 total_pages=10 has_next=True has_prev=False
  page=5: items=[41, 42, 43]... total=100 total_pages=10 has_next=True has_prev=True
  page=10: items=[91, 92, 93]... total=100 total_pages=10 has_next=False has_prev=True
  page=999 (越界): items=[] total=100 has_next=False
  空数据: items=[] total=0 total_pages=1
  page=0, limit=10: ValueError(page 必须 >= 1，收到 0)
  page=-1, limit=10: ValueError(page 必须 >= 1，收到 -1)
  page=1, limit=0: ValueError(limit 必须 >= 1，收到 0)
  page=1, limit=-5: ValueError(limit 必须 >= 1，收到 -5)
  page=1, limit=2000: ValueError(limit 上限 1000，收到 2000)

============================================================
cursor 分页演示
============================================================
  iter=0: cursor=None items=[1, 2, 3]... count=10 has_next=True next_cursor=MTA=...
  iter=1: cursor=MTA= items=[11, 12, 13]... count=10 has_next=True next_cursor=MjA=...
  iter=2: cursor=MjA= items=[21, 22, 23]... count=10 has_next=True next_cursor=MzA=...

============================================================
to_dict 序列化演示
============================================================
  keys: ['items', 'pagination']
  pagination: {'total': 100, 'page': 1, 'limit': 10, 'total_pages': 10, 'has_next': True, 'has_prev': False}
  items 长度: 10

全部演示通过
```

## 功能覆盖

- [x] 支持 offset/limit 和 cursor 两种模式
- [x] 返回总条数、当前页、是否有下一页
- [x] 处理空结果、越界页码
- [x] 提供 SDK 封装（Python）
- [x] 参数校验（非法值抛 ValueError）
- [x] to_dict() 序列化为 API 响应
- [x] 数据库友好（query_fn/count_fn 回调模式）
