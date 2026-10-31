# Invest Dictionary · 已知坑点（PITFALLS）

> 开发与发布过程中踩过的坑，供后续维护者和 AI Agent 排雷。
> 每条均标注：现象 → 根因 → 修复 → 预防。
> 创建日期：2026-08-01

## 1. 词条 slug 特殊字符导致文件名/链接断链（最高频）

- **现象**：词条名含 `/`（如 `M0 / M1 / M2`）、`*`（如 `新股（IPO / 打新）`）、`>`（如 `股票（普通股 / 优先股）`）时，相关词条链接 308 处断链、首页卡片约 30+ 张点击报错。
- **根因**：文件名必须把 `/`、`*`、`>` 替换为 `_`（Windows 文件系统不允许），但链接生成仍直接使用原始标题/slug。
- **修复**：建立 id → 真实文件名映射表（`entry_file_map.json`），所有链接（相关词条、首页卡片、pager）统一用映射后的文件名。
- **预防**：新增词条时必须用归一化 slug 命名（`/`、`*`、`>` → `_`），相关词条 href 禁止直接用标题。

## 17. plan sed 模式太窄导致 wave 1 "完成"假象（2026-09-20）

- **现象**：plan Task 6 sed 14 模式只覆盖 #C43A31 / #f5efe0 / KaiTi 字面，**漏了米色 rgba（5 类）/ 老国风橙 hex+rgba / 朱砂红 rgba / 米色卡面 #fdfaf4 / 米色文字 #4a4035 等**。Task 7 sweep 也只补 index.html #C43A31 残留，没扩到米色/楷体/老国风。grep 报"0 残留"但**用户浏览器看仍是老国风宣纸视觉**。
- **根因**：plan 写"grep 朱砂红 = 0"作为验收，但 grep 模式不完整；agent 信 plan 拍板，没实际打开浏览器看视觉就 commit。
- **修复**：Task 6 redo（`d87a66e`）+ Task 7 redo（`0122524`）扩到 ~40 模式，覆盖全部米色/老国风/朱砂红 rgba/楷体字面（含 HTML-encoded inline 残段）。grep 全 4 类残留 = 0 ✅
- **预防**：
  - 任何 sed 批量前先抽样 1 个文件用浏览器看视觉，再决定模式范围
  - grep 验证不仅查 plan 列的"严禁色"，要查 rgba 等变体（plan 没列的不代表没漏）
  - "完成"的最终标准是浏览器视觉一致，不是 grep = 0
  - 用完美截图工具（如 Playwright）截图前/后对比，不靠肉眼

## 18. Windows perl 中文 regex 不匹配（2026-09-20）

- **现象**：perl regex `"[^"]*(?:楷体|仿宋)[^"]*"` 在 Windows + `<:raw` 读 UTF-8 文件时**不匹配**，残留 5259 处楷体字面。改用 `\x{6977}\x{4F53}` unicode codepoint 也不匹配。
- **根因**：`<:raw` 把文件当 latin1 字节流读入，perl regex 编译时把 `\x{6977}` 当 latin1 codepoint（U+6977 = '横'），跟 UTF-8 字节序列不匹配。
- **修复**：改 `<:encoding(UTF-8)` 读入，perl 自动 UTF-8 解码成内部 unicode 字符串，regex 才能正确匹配中文。脚本 `scripts/brand-sweep.pl` 已用此模式。
- **预防**：
  - Windows + perl 处理 UTF-8 文件必用 `<:encoding(UTF-8)` 或 `<:utf8`
  - 中文 regex 用字面词要 `use utf8` + 文件 BOM/声明 utf-8
  - 测试时写一段最小 repro 验证 regex 命中再批量（避免扫 449 文件跑 30s）

## 19. inline style 属性里 CSS 引号用 `&quot;` HTML encode（2026-09-20）

- **现象**：词条页底部 `ft-tool-link` 块的 inline style 用 `font-family:&quot;KaiTi&quot;,&quot;楷体&quot;,...`（HTML-encoded 引号），外层 regex `font-family\s*:\s*([^;]+?)` 抓到第一个 `;` 之前的段做替换，**`;KaiTi&quot;,&quot;楷体&quot;,...;` 残段留在后面**。9 处残留。
- **根因**：CSS 在 inline `style=""` 属性里 `"` 必须 encode 成 `&quot;`（否则破坏 HTML 属性）；font-family 段被前次 sweep 拆开后，断尾的 `KaiTi&quot;,&quot;楷体&quot;,...` 变成 orphan CSS declaration（浏览器丢弃但源码残留）。
- **修复**：sweep 脚本里加了 `KaiTi&quot;,&quot;楷体&quot;,&quot;PingFang SC&quot;,sans-serif` 这类固定 broken 模式的直接删 pattern。9 处残留清 0。
- **预防**：
  - sweep inline style 段时，把 `&quot;` 当 `"` 等价处理（解码后再匹配）
  - 重写后的 chain 如果原段有 `&quot;`，重新 encode（保持 inline style 合法）
  - 验证时不仅 grep 字面残留，要 grep 任何 inline `style="..."` 里的 font 字段

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
- **补注（2026-09-22）**：本次清理范围**未覆盖页内社交分享链接**——214 个词条页的微博分享 `url=` 仍指向旧域名，直到 neat-freak 全站扫描才暴露（见 #20）。"残留 = 0" 仅对 canonical/og/sitemap/robots 成立，**不等于全站无残留**。

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

## 15. 首页 hero 主按钮隐形（:root 缺 `--accent` 变量）

- **现象**：v1.0 改造后首页 hero 主 CTA 白字落白底，按钮整体不可见（点击区域仍在）。
- **根因**：`index.html` 的 `:root` 未定义 `--accent`，而按钮 `background: var(--accent)` 解析失败 → 背景缺失；`color` 仍是 token 里的白字，于是白底白字。
- **修复**：`:root` 补 `--accent: var(--mf-colors-text-link);`（映射到芒果橙 #F97316），不写裸 hex。
- **预防**：改 `:root` 时跑一遍"变量引用 vs 定义"清单；页面里所有 `var(--x)` 必须能在本页 `:root` 或 token CSS 中找到定义；品牌色一律走 token CSS，不在页内另起变量名。

## 16. 下游图文线直接套网页品牌色，观感被否后回滚

- **现象**：08-每日热词图文 `main.py` 的宣纸渐变底 `#F7F5F2→#EFEAE2` 被改为品牌暖白 `#FFFFFF→#FFF3EA`（README 同步改），用户看过成品后认为"之前的版本更好"。
- **根因**：把网页端 v1.0 令牌直接套到图片产物上，未先确认该图文线是否属于本次品牌改造范围；图片场景的暖灰底观感与网页不同。
- **修复**：从 `main.py.bak-step5-20260921` / `README.md.bak-step5-20260921` 回滚，回滚后 md5 与备份一致；回滚前把品牌色版另存 temp 以备对比。
- **预防**：改下游图文 / 视频产物配色前，先确认这条线要不要纳入改造；改动前留一份带日期的备份；`docs/design-tokens.md` 已把该线标注为例外。

## 20. 社交分享链接旧域名漏网（2026-09-22）

- **现象**：neat-freak 全站扫描发现 **214 个词条页**的微博分享链接 `service.weibo.com/share/share.php?url=…investbuddy.com/terms/…` 仍指向旧域名；而 #3 早已记"残留 = 0"。
- **根因**：#3 的清理与校验模式只覆盖 canonical / og:url / sitemap / robots，**页内嵌入的绝对 URL（社交分享、复制链接）不在扫描口径内**；单点 grep 命中旧域名却不构成"清理完毕"的证据。
- **修复**：214 页批量替换为 `dictionary.mangofolio.com`，写盘回读校验（0 失败），全站复查残留 = 0。
- **预防**：域名残留扫描模式统一用 `//investbuddy.com`，覆盖**所有** HTML 属性中的绝对 URL；模式用 `//old-domain` 精确匹配，避免误伤合法子站 `investbuddy.mangofolio.com`；扫描口径写进 `scripts/check-consistency.py`。

## 21. 批量补丁 stdout 报成功但实际空转（2026-09-22）

- **现象**：批量替换脚本（perl / 正则）自称"成功 26 项"，实际因跨行匹配失效**一项都没改**，误判存量页已刷 token。
- **根因**：仅凭 stdout 输出判定成功，未校验写盘后的文件真实内容。
- **修复**：改为**写盘后强制回读**——重新读文件确认旧模式已消失、新模式存在，逐文件计数。
- **预防**：批量补丁三件套 = 幂等 + 备份（`.bak-{step}-{date}`）+ 写盘回读校验；**禁止凭 stdout 判成功**。

## 22. 计数多处人肉维护导致漂移（2026-09-22）

- **现象**：`manifest.json`（1 处）、`llms.txt`（2 处）写 **461** 词条，`web/terms` 实际 **472** 页；`PROGRESS.md` / `design-tokens.md` 同样残留旧数字。461 的真实来源是首页内嵌 `ALL_ENTRIES` 的长度。
- **根因**：同一事实在 4+ 处手写维护，扩充词条后没同步全部位置。
- **修复**：三处统一改为 **472**（= `dictionary.json` 去重后条数 = `terms` 页数）；首页 `ALL_ENTRIES` 重新同步。
- **预防**：条目数只认 `dictionary.json`，其余位置由脚本生成或由 `scripts/check-consistency.py` 校验；任何数字改动跑一次校验脚本。

## 23. sitemap 与页数脱节（2026-09-22）

- **现象**：`sitemap.xml` 只有 439 个词条 URL，磁盘 **472** 页——**33 个已发布词条页不在 sitemap**（SEO 收录缺失）。
- **根因**：sitemap 在早期一次性手写/生成，后续扩词条（含热词 cron）没有增量更新机制。
- **修复**：`scripts/generate-sitemap.py` 按 `dictionary.json` 顺序同源重建（保持原 `changefreq/priority` 规则），439 → 472 + 首页；回读校验覆盖 0 缺 0 多。
- **预防**：sitemap 一律由脚本从数据源生成，禁止手改；发布前跑覆盖差集。

## 24. 首页内嵌 ALL_ENTRIES 不同步导致新词条搜不到（2026-09-22）

- **现象**：`index.html` 内嵌 `ALL_ENTRIES` 461 条，`dictionary.json` 473 条——**11 个新词条在首页搜索与目录里不可见**（含"中概股""上证指数""人形机器人"等）。
- **根因**：首页搜索/目录渲染读的是内嵌静态数组，而非直接读 `dictionary.json`；新增词条后忘记跑同步脚本。
- **修复**：跑 `python scripts/sync_all_entries.py`（473 条，自动备份 `web/temp/index.html.bak`），校验首页缺/多 = 0。
- **预防**：新增或修改词条后**必须**跑同步脚本；`check-consistency.py` 已将该一致性纳入校验。

## 25. 备份文件被 git 跟踪入库（2026-09-22）

- **现象**：`web/terms/*.html.bak`（4 个）、`web/js/knowledge-card.js.bak-20260919` 已提交进版本库；磁盘上 `.bak*` 共 492 个（多数已被 `.gitignore` 忽略）。
- **根因**：`.gitignore` 规则是后加的，**加规则不会让已跟踪文件自动脱管**；提交时只核对了 `git status`，未查 `git ls-files` 中的备份残留。
- **修复**：已列入清理候选（待批，见 PROGRESS.md 待办）。
- **预防**：提交前用 `git ls-files | Select-String '\.bak'` 核对备份残留；备份文件一律写入 `web/temp/`（已忽略）或仓库外。

## 26. 首页内嵌 ALL_ENTRIES 再次脱节（914 vs 924，2026-10-29）

- **现象**：首页搜索漏掉最新 10 个词条（美股交易时间、双基金经理、基金经理变更、每股净资产…）。
- **根因**：10-28/29 两批热词入库后只提交了词条页与登记，没跑 `sync_all_entries.py`；提交前也没跑门禁。
- **修复**：跑同步脚本 → 924；`check-consistency.py` 10/10 PASS。
- **预防**：每天热词入库后固定跑 `python scripts/check-consistency.py`，不看结果不提交。

## 27. 改版把外来设计令牌引进站点（2026-10-29）

- **现象**：首页引用 `css/betterment-tokens.css`（456 个 `--bmt-*` 变量 = Betterment 的蓝/金/青），7 张场景卡直接用 `--bmt-colors-primitives-blue-60` 等；该文件还是 untracked，clone 或部署后样式直接塌。
- **根因**：把"参考网站"的令牌当成本站令牌。参考包只能借**结构**，不能借颜色。
- **修复**：令牌统一回 `mangofolio-tokens-v09.css`；参考包移到 `docs/reference/`；新增 `web/css/site.css` 只放本项目色带与组件。
- **预防**：`grep -r "--bmt-" web/` 必须为 0；新页面只允许引用 mangofolio 令牌。

## 28. 移动端 1fr 网格被 min-content 撑破（2026-10-29）

- **现象**：390px 下热词卡/场景卡横向溢出，整页 `scrollWidth` 591 > 390，文字看着像被裁。
- **根因**：`grid-template-columns: 1fr` 的自动最小值是 min-content，卡里 `white-space: nowrap` 的文本把轨道撑宽；flex 子项同理（默认 `min-width:auto`）。
- **修复**：移动端轨道改 `minmax(0, 1fr)`；热词项加 `min-width: 0`。
- **预防**：含 nowrap 内容或长词的网格/弹性子项，一律 `minmax(0,1fr)` / `min-width:0`。

## 29. headless 截图的手机视口不可信（2026-10-29）

- **现象**：`msedge --headless --window-size=390,844` 截出来的图右侧全被裁，看起来像横向溢出；但 390 真视口探测 `scrollWidth=375`、溢出元素 0。
- **根因**：Windows 下浏览器窗口有最小宽度（约 500px），`--window-size` 只是窗口尺寸，布局视口比截图宽。
- **预防**：移动端校验用 iframe 真视口（`web/temp/mobile-view.html?page=&y=`）+ `--dump-dom` 打印 `scrollWidth` 与溢出元素清单，别只看截图。

## 30. 清理脚本跑完多出 103 个文件的纯噪声 diff（2026-10-31）

- **现象**：`strip-aigc-metadata.py` 本该只删 10 个文件的 AIGC 头，跑完 `git status` 却出现 113 个改动文件。
- **根因**：`strip()` 无条件 `"\n".join(lines) + "\n"` 重建全文，把 103 个原本没有末尾换行的 md 各补了一个换行。
- **修复**：拆行前记录「原文末尾是否有换行」与主导行尾（CRLF/LF），按原行尾拼回；无替换时 `new == raw` 直接跳过。
- **预防**：任何 md 批处理脚本，除目标内容外其余字节必须原样（行尾 + 末尾换行都要还原），写完先 `git diff --numstat` 对账再提交。

## 31. 清理脚本没进同步链路，问题一复发就没人管（2026-10-31）

- **现象**：AIGC 全量清除 484 处后，外部生成器一扩词，10 个新词条立刻又被注入水印头。
- **根因**：`strip-aigc-metadata.py` 从未接入 `sync-site.py` 的 STEPS，链路跑完不产生清理动作。
- **修复**：把 strip 排到链路第 0 步（sync/sitemap/llms 之前），并确保幂等（第二次跑 0 改动）。
- **预防**：新写任何「对抗性清理」脚本，必须同时决定「挂在链路的哪一步」，否则它只能管当时。

## 32. 新增词条页把 `**加粗**` 原样渲染成字面星号（2026-10-31 发现，存量未修）

- **现象**：CRS/FATCA/鸵鸟效应/拖延症 等 31 个新词条页，正文出现字面 `**` 而不是加粗。
- **根因**：外部生成器把 md 段落直接塞进 `<p>`，没做 `**x** → <strong>x</strong>`；旧生成脚本 `batch_fill_1000.md_to_cards` 其实有这步，新的生成链路丢了它。
- **修复**：本轮补词条改用 `scripts/add-term.py`（含 inline 转换）；存量 31 页待批量修（待办，未做）。
- **预防**：md→HTML 的所有生成入口必须共用同一套 inline 转换；site-audit 应加「字面 `**` 残留」检查。

## 33. 手工新增词条页时照抄旧生成器，URL 形态被 P0-1 打回（2026-10-31）

- **现象**：`batch_fill_1000.render_html` 产出的关联链接是绝对 URL 且带 `.html` 后缀，与现网「相对 + 百分号编码 + 无后缀」不一致。
- **根因**：现网词条页在 P0-1 阶段改过 URL 规范，旧生成器没跟上，两个生成器并存且口径不一。
- **修复**：`scripts/add-term.py` 不手写外壳，以现网标准页（`web/terms/鸵鸟效应.html`）为模板做局部替换。
- **预防**：凡「生成一个跟现网同形的页面」，一律以现网真实页面为模板做局部替换，不从旧脚本/旧模板出发。

## 34. dictionary.json 重写一次，行尾/末尾换行全变，上千行假 diff（2026-10-31）

- **现象**：给 dictionary.json 追加 2 条，`git diff` 却显示全文件改动。
- **根因**：这个文件是 CRLF 且末尾无换行；`json.dump` 默认 LF，包装层又补了换行。
- **修复**：`write_dict()` 先读原文件记录行尾风格与「末尾是否有换行」，按原样写回。
- **预防**：全站唯一数据源类文件（dictionary.json / index.html），任何程序化重写都必须保留原行尾约定，先 `git diff --numstat` 对账。

---
*本文档与 docs/PROJECT_GOALS.md 一同维护，同步副本见 Obsidian `D:\ObsidianVault\02-Projects\`。*
*（内容由AI生成，仅供参考）*
