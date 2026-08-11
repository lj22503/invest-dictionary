---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 1c835e55ba3b06878e6538b2edadf703_26f98d348d8611f1bfea525400e6dd8f
    ReservedCode1: moyq4uaE1OK1egSoBHulprg3fYiFh9htHUcKLNdmw1R0wJoPPmumybF+LzZ049HGRd7tQ58pKy7YEd0mNAkmRgeZrIi+mDOdkM/x6YdzTXM9uEF+lWIoJRubX2k7ld00WkIHxN/bYOpmNvvZVl6uZdn4p0NjF4p72xY6oV+tzp3AAbikIzFkDo4fMtk=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 1c835e55ba3b06878e6538b2edadf703_26f98d348d8611f1bfea525400e6dd8f
    ReservedCode2: moyq4uaE1OK1egSoBHulprg3fYiFh9htHUcKLNdmw1R0wJoPPmumybF+LzZ049HGRd7tQ58pKy7YEd0mNAkmRgeZrIi+mDOdkM/x6YdzTXM9uEF+lWIoJRubX2k7ld00WkIHxN/bYOpmNvvZVl6uZdn4p0NjF4p72xY6oV+tzp3AAbikIzFkDo4fMtk=
---

# Invest Dictionary · 已知坑点（PITFALLS）

> 开发与发布过程中踩过的坑，供后续维护者和 AI Agent 排雷。
> 每条均标注：现象 → 根因 → 修复 → 预防。
> 创建日期：2026-08-01

## 1. 词条 slug 特殊字符导致文件名/链接断链（最高频）

- **现象**：词条名含 `/`（如 `M0 / M1 / M2`）、`*`（如 `新股（IPO / 打新）`）、`>`（如 `股票（普通股 / 优先股）`）时，相关词条链接 308 处断链、首页卡片约 30+ 张点击报错。
- **根因**：文件名必须把 `/`、`*`、`>` 替换为 `_`（Windows 文件系统不允许），但链接生成仍直接使用原始标题/slug。
- **修复**：建立 id → 真实文件名映射表（`entry_file_map.json`），所有链接（相关词条、首页卡片、pager）统一用映射后的文件名。
- **预防**：新增词条时必须用归一化 slug 命名（`/`、`*`、`>` → `_`），相关词条 href 禁止直接用标题。

## 2. encodeURIComponent(slug) 产生 %2F 导致 ERR_INVALID_URL

- **现象**：首页卡片点击含斜杠词条报 `ERR_INVALID_URL`（file:// 协议下）。
- **根因**：JS 用 `encodeURIComponent(e.slug)` 生成 href，`/` 被编码为 `%2F`，而磁盘上文件名是 `_` 版本，两者不一致。
- **修复**：改为 `encodeURIComponent(e.file)`（真实文件名映射字段）。
- **预防**：链接生成永远以磁盘文件名为准，不要用 slug 直接拼 URL。

## 3. 旧域名残留（investbuddy.com → dictionary.mangofolio.com）

- **现象**：213 个详情页 canonical、sitemap.xml 214 条 URL、robots.txt 的 Sitemap 声明全部指向 investbuddy.com。
- **根因**：词条页由 InvestBuddy 历史项目继承而来，域名未同步替换。
- **修复**：全量批量替换 + 终验（残留文件数 = 0）。
- **预防**：任何项目独立发布前，先扫 canonical/og:url/sitemap/robots 的域名残留。

## 4. 页面声称条目数与实际数据不一致

- **现象**：首页副标题写"217 个投资术语"，实际数据源只有 213 条。
- **根因**：文案与数据源脱节，未同步校验。
- **修复**：统一改为 213。
- **预防**：条目数等硬数字必须从数据源（dictionary.json）读取或校验，禁止手写。

## 5. body display:flex 布局塌陷

- **现象**：详情页新增区块被挤成单行（卡片并排而非纵向堆叠）。
- **根因**：ianneo 原始样式 `body { display: flex }` 假设只有一个 `.paper` 子元素，新增元素后被横向排列。
- **修复**：`flex-direction: column`。
- **预防**：改造继承样式时，先确认 flex 方向假设。

## 6. 微信分享"假二维码"

- **现象**：426 处微信分享按钮使用占位灰色方块冒充二维码。
- **根因**：历史模板遗留占位图，无真实二维码生成。
- **修复**：替换为真实分享降级方案（复制链接引导）。
- **预防**：上线前扫描所有图片占位；无真实素材就不放二维码。

## 7. git 分支名不一致（master vs main）

- **现象**：本地 `git init` 默认 master，远程默认分支 main，push 报 `src refspec main does not match any`。
- **根因**：git 默认分支名与 GitHub 新建仓库默认分支不一致。
- **修复**：`git branch -m main` 后重新 push。
- **预防**：`git init -b main` 或在 init 后立即改名。

## 8. pull 后 commit 未执行（staged 但未提交）

- **现象**：`git pull --allow-unrelated-histories` 后执行 commit，看似成功，实际只完成了 staged，log 仍停留在远程 Initial commit。
- **根因**：pull 的 merge 状态 + 多行输出导致 commit 未真正提交（工作区处于 staged 状态）。
- **修复**：重新执行 `git commit` + `git push`。
- **预防**：推送前用 `git log` / `git status` 确认 commit 真实生成。

## 9. Vercel CLI 未登录（部署阻塞）

- **现象**：`vercel whoami` 为空，无 auth.json、无 VERCEL_TOKEN 环境变量。
- **根因**：CLI 已安装但从未登录授权。
- **修复**：需用户执行 `vercel login`（浏览器授权）或提供 VERCEL_TOKEN。
- **预防**：部署前先确认 `vercel whoami` 通过。

## 10. market skill 未注册导致 use_skill 不可用

- **现象**：neat-freak 位于 skills/market 目录，但 `use_skill` 报"对当前 Agent 不可用"。
- **根因**：market 目录 skill 未注册进当前 Agent 的可用 skill 列表。
- **修复**：直接读取 `skills/market/neat-freak/SKILL.md` 按其方法论手动执行。
- **预防**：引用外部 skill 前先确认在可用列表，否则降级为读取方法论执行。

## 11. Vercel Git 集成必须设置 Root Directory

- **现象**：仓库根目录无 index.html（站点在 web/ 子目录），直接导入部署会失败或部署出空壳。
- **根因**：Vercel 默认以仓库根为项目根；本项目静态站点在 `web/`。
- **修复**：导入时在 Project Settings → Root Directory 设为 `web/`。
- **预防**：Git 集成部署前确认站点根目录与仓库结构关系。

## 12. 自定义域名需先配置 DNS（Cloudflare 托管场景）

- **现象**：Vercel Domains 添加 dictionary.mangofolio.com 后状态为 Invalid Configuration。
- **根因**：mangofolio.com 由 Cloudflare 托管，Vercel 无法自动接管 DNS。
- **修复**：在 Cloudflare 添加 CNAME `dictionary` → `8f73e94d8020e067.vercel-dns-017.com`，等待生效后 Vercel 自动变 Valid。
- **预防**：第三方 DNS 托管的域名绑定前，先准备 DNS 记录。

## 13. Cloudflare 代理（橙云）导致 Vercel 提示 Proxy Detected + 可能 525

- **现象**：CNAME 走 Cloudflare Proxied 后，Vercel Domains 显示 Proxy Detected 警告；域名刚生效初期访问偶发 `525 SSL handshake failed`。
- **根因**：① Cloudflare 橙云代理使 Vercel 的 DDoS 防护/性能优化失效，Vercel 显示功能警告；② 域名生效初 Vercel 侧证书签发/握手未就绪，Cloudflare 转发时出现临时 525。
- **修复**：525 为临时状态，等待证书签发完成即可；如要消除 Proxy Detected 警告，将 Cloudflare 记录改为 DNS only（灰云）。
- **预防**：绑定第三方代理时预知 Vercel 会提示 Proxy Detected；域名生效后先等 1-3 分钟再验证，避免误判 525 为失败。

## 14. 热词词条页 pager/related 链接使用斜杠版 URL 导致 404

- **现象**：主页热词「期限错配」「中签率」词条页内，pager-prev 与 related-links 第一个词条点击报 404（如 `%E6%96%B0%E8%82%A1%EF%BC%88IPO%20/%20%E6%89%93%E6%96%B0%EF%BC%89.html`），用户反馈"所有热词的第一个词都点不开"。
- **根因**：词条页内链接（pager/related）用词条名直接编码生成，含 `/` 的词条名生成斜杠版 URL（`%20/%20`），而磁盘文件名是下划线版（`%20_%20`）；线上 308 重定向去 .html 后缀后无法匹配任何文件，最终 404。全站 234 处 terms 链接仅这 4 处断链，均集中在热词新词条页。
- **修复**：将 `中签率.html`、`期限错配.html` 的 pager-prev 与 related-links 首词 href 从斜杠版改为下划线版；同时修正 `index.html` renderFallback 用 `e.title` 拼链接的隐患（改 `e.file`），避免兜底热词再踩同样的坑。
- **预防**：新增含 `/`、`*`、`>` 词条时，页内所有链接（pager、related、canonical、og:url）必须以真实文件名（下划线版）编码；热词写入 KV 前用线上请求验证 url 返回 200；全量校验脚本（扫描 terms/ 链接与本地文件名一致性）在每次提交前运行。

---
*本文档与 docs/PROJECT_GOALS.md 一同维护，同步副本见 Obsidian `D:\ObsidianVault\02-Projects\`。*
*（内容由AI生成，仅供参考）*
