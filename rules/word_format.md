# Word 文档排版规范（详细）

## 一、核心分页与标题绑定规则

### 禁止标题孤行
- 所有层级标题绝不允许单独留在页面底部
- 不允许标题后仅跟随 1-2 行正文就被分页
- 当前页剩余空间无法容纳「标题 + 至少 3 行正文」时，标题连带后续正文整体移至下一页

### 标题与正文强制同页
- 任意层级标题必须与紧跟的第一段正文在同一页
- 禁止 "标题在本页末尾、正文在跨页开头"

### 标题层级不跨页割裂
- 连续多个同级小标题，优先保持整块内容在同一页
- 禁止将一个标题拆成两页

### 章节与分页规则
- 一级标题（章节标题）默认从新页面开始
- 二级/三级标题禁止作为页面最后一行

## 二、正文段落排版规则

### 禁止段落孤行/寡行
- 段落禁止 "最后1行单独留在下一页" 或 "开头1行单独留在本页底部"
- 分页必须保证段落至少有 2 行内容在同一页

### 段落格式全局统一
- 全篇正文统一字体、字号、行间距（1.5倍）、段前段后间距
- 所有正文段落首行缩进 2 字符
- 文字严禁上下重叠、行间距挤压、自动乱换行

### 特殊段落处理
- 长段落超过1页时，优先在句子间合理分页，禁止将单个句子拆成两页

## 三、图表/表格与标题绑定规则

### 表格禁止跨页割裂
- 单张表格必须完整放在同一页，禁止被分页拆成两部分
- 若内容过长无法单页放下：拆分为逻辑块，或调整字号/列宽
- **实现策略：前几个大模块自然流动（靠 keepNext + cantSplit），需要"跳页"的小模块前加 1-2 个空段落做软换页，不加硬分页。**

> **踩坑总结：**
> - 纯靠 keepNext + cantSplit 不够：Word 虽然不会拆行，但标题+表头+1行数据在页底、剩下全在下页，一样难看。
> - 所有表格都加分页也不行：第一页空、中间页也空，浪费严重。
> - **最终正确方案：软换页。** 在需要跳页的位置前加 `doc.add_paragraph('')`（1-2 个空段落），填掉当前页剩余空间，Word 自然把后续标题推到新页面。配合 keepNext + cantSplit，后续表格不拆散。不浪费空间，排版自然。

### 表格与说明文字绑定
- 表格标题、说明文字必须与表格主体在同一页
- 表头必须与第一行数据同页

### 续表处理
- 若必须跨页，在续页添加重复表头，标注 "续表" 字样

## 四、格式与样式全局规范

- 标题层级格式全程统一
- 编号严格按逻辑顺序，禁止跳号/重号/乱号
- 全篇页边距统一（上下 2.54cm、左右 3.17cm）
- 页码从正文第一页开始，格式统一

## 五、自查清单

- [ ] 无标题孤行、标题与正文跨页割裂
- [ ] 无段落孤行/寡行
- [ ] 无文字重叠、格式混乱
- [ ] 表格完整不跨页，与说明文字同页
- [ ] 编号连续不跳号

## 六、python-docx 代码实现

```python
# 标题与下段同页
def keep_with_next(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    if pPr.find(qn('w:keepNext')) is None:
        pPr.append(etree.Element(qn('w:keepNext')))

# 表格行不跨页拆行
def prevent_row_split(table):
    for row in table.rows:
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        if trPr.find(qn('w:cantSplit')) is None:
            trPr.append(etree.Element(qn('w:cantSplit')))

# 段落孤行控制
def set_widow_control(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    if pPr.find(qn('w:widowControl')) is None:
        etree.SubElement(pPr, qn('w:widowControl'))

# 全局行间距
style = doc.styles['Normal']
style.paragraph_format.line_spacing = 1.5

# 软换页：在需要跳页的位置前加空段落（不加硬分页）
doc.add_paragraph('')  # 填掉当前页剩余空间
doc.add_paragraph('')  # Word 自然把后续标题推到新页面
```
