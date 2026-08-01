# 贡献指南 · Contributing to Invest Dictionary

感谢你愿意为投资词典贡献词条。本项目的核心使命是：**用大白话讲清楚每一个投资术语**。

## 词条质量标准（4 条红线）

1. **说人话**：第一句定义必须让外行听懂，禁止"术语套术语"。
   - ❌ "货币是充当一般等价物的特殊商品"
   - ✅ "货币就是你手里攥着的 100 块"
2. **有场景**：必须讲清楚"关我什么事"，给真实生活/投资场景。
3. **讲坑点**：必须包含"常见坑 / 误区"，帮读者避雷。
4. **能搜索**：标题、description、正文覆盖用户会搜的关键词。

## 新增词条流程

### 第一步：查重

在 [web/dictionary.json](web/dictionary.json) 搜索是否已有同义词条（含别名）。已存在则改为补充/修正，不要重复新增。

### 第二步：写 Markdown 词条

按 [skill/invest-dictionary-generator/templates/term-card.md](skill/invest-dictionary-generator/templates/term-card.md) 模板撰写，包含 4 个部分：

```
# 词条名（别名）
> 一句话定义
## 1. 这是什么
## 2. 为什么重要
## 3. 怎么用 / 怎么看
## 4. 常见坑 / 误区
相关词条：xxx、yyy
```

### 第三步：命名与登记（重要）

- **slug 归一化**：词条名含 `/`、`*`、`>` 时，一律替换为 `_`（下划线）。
  - 例：`M0 / M1 / M2` → 文件名 `M0 _ M1 _ M2（货币供应量）.html`
- 在 `web/dictionary.json` 登记：
  ```json
  {
    "id": 214,
    "title": "词条名",
    "slug": "归一化后的 slug",
    "chapter": "所属篇章",
    "description": "一句话定义",
    "related": [1, 2, 3]
  }
  ```

### 第四步：生成 HTML 页面

- 复用 [templates/term-page.html](skill/invest-dictionary-generator/templates/term-page.html)
- canonical / og:url 使用正式域名 `https://dictionary.mangofolio.com/terms/{文件名}.html`
- 相关词条链接 href 必须用**归一化文件名**，否则含特殊字符的词条会断链

### 第五步：提交 PR

PR 内容应包含：
- 词条 Markdown（`.md`）
- 词条 HTML 页面（放 `web/terms/`）
- `dictionary.json` 登记更新
- 若为新增篇章，同步更新首页章节结构

## 评审标准

维护者会用以下清单检查你的 PR：

- [ ] 第一句是大白话定义
- [ ] 正文 ≥2 张故事卡（这是什么 / 为什么重要 必含）
- [ ] 有真实场景或数字例子
- [ ] 有"常见坑 / 误区"
- [ ] 相关词条链接全部可跳转
- [ ] canonical / og:url 域名正确
- [ ] 无假二维码、无 HTML 残留
- [ ] dictionary.json 登记正确

## 开发环境

无需构建工具，纯静态站点：

```bash
cd web && python -m http.server 8080
```

## 其他贡献方式

- **提 Issue**：发现词条错误、过期数据、或者想要某个词条
- **翻译**：帮助把词条翻译成英文（路线图中）
- **设计**：视觉优化、可访问性改进
