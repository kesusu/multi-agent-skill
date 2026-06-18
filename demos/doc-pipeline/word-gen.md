---
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: 用 python-docx 生成排版规范的 Word 文档
---

# Word 文档生成技能

用 python-docx 生成可直接打印的规范 Word 文档。以下是经过实战验证的完整流程和排版策略。

## 用户需求

$ARGUMENTS

## 基础流程

1. 确认用户需求：文档内容、结构、表格、格式要求
2. 写 Python 脚本，用 python-docx 生成 .docx
3. 运行脚本，自动自查，输出结果

## 必须实现的排版规范

以下规则来自反复踩坑后的最终方案，必须全部实现。

### 1. 全局格式

```python
import sys
sys.stdout.reconfigure(encoding='utf-8')  # 防止中文乱码
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from lxml import etree

doc = Document()

style = doc.styles['Normal']
font = style.font
font.name = '宋体'
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
font.size = Pt(10.5)
pf = style.paragraph_format
pf.line_spacing = 1.5
pf.space_before = Pt(0)
pf.space_after = Pt(4)
```

### 2. 三个核心工具函数（必须有）

```python
def set_widow_control(paragraph):
    """禁止段落孤行/寡行"""
    pPr = paragraph._p.get_or_add_pPr()
    if pPr.find(qn('w:widowControl')) is None:
        etree.SubElement(pPr, qn('w:widowControl'))

def keep_with_next(paragraph):
    """标题与下段同页"""
    pPr = paragraph._p.get_or_add_pPr()
    if pPr.find(qn('w:keepNext')) is None:
        pPr.append(etree.Element(qn('w:keepNext')))

def prevent_row_split(table):
    """表格行不跨页拆行"""
    for row in table.rows:
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        if trPr.find(qn('w:cantSplit')) is None:
            trPr.append(etree.Element(qn('w:cantSplit')))
```

- 所有标题调用 `keep_with_next()`
- 所有表格调用 `prevent_row_split()`
- 正文段落调用 `set_widow_control()`

### 3. 分页策略（关键！踩坑总结）

**核心原则：用空段落做软换页，不用硬分页。**

错误做法（反复踩坑）：
- 不加分页 → keepNext 保证不了标题+表头+1行不卡在页底
- 全加 `doc.add_page_break()` → 每个表格独占一页，大片空白
- 按行数判断（≤4行加分页）→ 依然顾此失彼

正确做法：
- 内容多的前几个模块：不加任何分页，靠 keepNext + cantSplit 自然流动
- 需要"跳到下一页"的模块：在标题前加 **1-2 个空段落**
- 空段落填掉当前页剩余空间，Word 自然把后续标题推到新页面
- 配合 keepNext + cantSplit，后续表格不被拆散

```python
# 软换页示例：在某个模块标题前加空段落
doc.add_paragraph('')
doc.add_paragraph('')
# 然后正常添加标题和表格
add_table(doc, '模块标题', data_rows)
```

**判断标准：** 打开生成的 docx 目视检查——
- 标题不能孤零零在页面底部
- 表格不能被分页从中间截断
- 不要有大片空白页

### 4. 表格格式化

```python
def format_table(table, headers, widths):
    """表头加粗居中，数据字号统一，列宽固定，防跨页"""
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = h
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(9)
    for row in table.rows[1:]:
        for cell in row.cells:
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9)
    for row in table.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = w
    prevent_row_split(table)
```

### 5. 生成后自动自查（必须有）

```python
# 保存后重新打开检查
check_doc = Document(output_path)
issues = []

# 检查所有表格行有 cantSplit
for t_idx, table in enumerate(check_doc.tables):
    for r_idx, row in enumerate(table.rows):
        trPr = row._tr.trPr
        if trPr is None or trPr.find(qn('w:cantSplit')) is None:
            issues.append(f'表格{t_idx} 第{r_idx}行 缺少 cantSplit')

# 检查所有标题有 keepNext
for p in check_doc.paragraphs:
    if 'Heading' in p.style.name and p.text.strip():
        pPr = p._p.get_or_add_pPr()
        if pPr.find(qn('w:keepNext')) is None:
            issues.append(f'标题 "{p.text[:20]}" 缺少 keepNext')

if issues:
    print(f'发现 {len(issues)} 个问题:')
    for issue in issues:
        print(f'  x {issue}')
else:
    print('全部通过')
```

## 工具函数清单

| 工具 | 用途 |
|---|---|
| `sys.stdout.reconfigure(encoding='utf-8')` | 防止中文输出乱码 |
| `keep_with_next(p)` | 标题与下段同页 |
| `prevent_row_split(table)` | 表格行不跨页 |
| `set_widow_control(p)` | 段落孤行控制 |
| `format_table(table, headers, widths)` | 统一表格格式 |
| 空段落 `doc.add_paragraph('')` | 软换页（替代硬分页） |
| 自查脚本 | 生成后自动检查 XML 属性 |

## 环境

- Python: `C:\Users\ke\AppData\Local\Programs\Python\Python311\python.exe`
- 依赖: `python-docx`, `lxml`
- 排版规范详见: `C:\Users\ke\.claude\rules\word_format.md`
