# 2026-10-13 用户 Semrush 实测：巴西元数据清理 vs 美国 Minecraft Ore Finder

> 本文属于**独立 SEO/AdSense 流量站机会研究**；不属于 SaaS 收入筛选。来自用户2026-10-13上传的两张 Semrush Keyword Overview + SERP Analysis 截图，是相应国家/桌面设备/当日快照。公开竞品的 GLOBAL DOMAIN Organic Search estimate（online-metadata.com ~16,170/月；orefinder.gg ~38,550/月）与下面关键词月搜索量、SERP 各URL估算自然搜索流量是**不同指标**，不等同于未来新站访客。截图中的「页面 AS」及引荐域名是针对排名页面，不等于主域名的整体权重。广告关键词 CPC 不是 AdSense 每次点击收入。

## A. Brazil — `remover metadados`（第一优先：建议进入技术可行性验证）

**用户 Semrush 精确数据：** Brazil / desktop，`remover metadados` **月搜索 33,100，KD 21，CPC USD 0**；同一页面显示全球词搜索量33,900（其中 Brazil 33,100）。付款广告竞争密度0.33不等于自然竞争难度。

| 相关巴西词（需查明意图重叠，不能简单相加） | 月搜索量 | KD |
|---|---:|---:|
| `remover metadados de video` | 6,600 | 23 |
| `remover metadados video` | 5,400 | 21 |
| `metadados remover` | 4,400 | 24 |
| `remove metadados` | 1,900 | 25 |

**真实前10 SERP（Semrush 截图）**

| 排名 | 页面/归类 | 页面 AS | 页面引荐域名 | 该URL估算自然搜索流量/月 |
|---:|---|---:|---:|---:|
| 1 | https://www.metadata2go.com/pt/excluir-metadados | 11 | 3 | 27,200 |
| 2 | https://www.adarsus.com/pt/excluir-metadados-on-line-documento-imagem-video/ | 8 | 2 | 14,500 |
| 3 | https://online-metadata.com/pt/remove-metadata | 2 | 3 | 8,400 |
| 4 | https://camaraux.com.br/ferramentas/removedor-metadados-imagens/ | 0 | 0 | 8,300 |
| 5 | https://tools.pdf24.org/pt/remover-metadados-pdf | 17 | 2 | 2,300 |
| 6 | https://exifremover.com/pt/ | 50 | 6 | 3,600 |
| 7 | Google Play metadata cleaner mobile app | 0 | 0 | 1,400 |
| 8 | https://www.adobe.com/br/acrobat/hub/remove-metadata-pdf.html | 0 | 0 | 305 |
| 9 | YouTube explainer video | 0 | 0 | 761 |
| 10 | metadados.jcmaceili.com — metadata utility | 6 | 4 | 6,100 |

**Interpretation:** top 5 tool pages have only 0–3 PAGE-level referring domains and one Brazilian independent tool page appears at #4. This is **multiple-site low-page-link ranking evidence**, more informative than a lone weak #8 page. However several parent brands have authority; site-level domain AS and exact query-contributed clicks remain unverified. *URL overall estimated organic* values are not the clicks caused specifically by `remover metadados`.

**Reality check: competition and monetization**
- https://online-metadata.com/remove-metadata accepts server uploads (up to 2GB on page) and remote URL/Dropbox/Drive source; http page claims server files deleted rapidly. Official pricing page https://online-metadata.com/ explicitly lists **free with ads** and **premium USD2/month, no ads**. This is observed monetization **model**, not verified revenue.
- https://www.metadata2go.com/pt/excluir-metadados admits not every type of metadata is always removable.
- https://www.adarsus.com/pt/excluir-metadados-on-line-documento-imagem-video/ sells enterprise-grade metadata solutions and supports special PDF signatures; replicating signed PDF preservation is not trivial.
- https://washfiles.com/pt/ **already** advertises zero-upload full-browser cleanup of photos, video, Office, PDF; supports batch, before/after, advanced UI. Privacy-first/local processing is **NOT unique**.
- https://github.com/iAnonymous3000/metadata-remover is MIT-licensed browser/WASM reference for JPEG/PNG/WebP/AVIF, with verified fixtures and format limitations; review license/technical limitations before integrating any code.
- https://www.ffmpeg-cookbook.com/en/tools/strip-metadata/ demonstrates local ffmpeg.wasm video stripping and explicitly warns some tags are missed and large media consume RAM.

**Concrete potential advantage (hypothesis, not proven):** tightly localized pt-BR utility that loads in one clear screen, fast mobile-first photo/EXIF/GPS cleanup, batch without account, clear **before → after → independently reread output tags** evidence, no upload of file bytes, accessible well-explained supported formats, transparent unsupported-tag/size warnings, and measured performance versus current tool UX. Need prove it improves *something that competing sites do poorly*; don't say "local privacy" alone differentiates when WashFiles already covers it.

**Mandatory feasibility checks BEFORE new website build:**
1. Same-device offline/no-upload, no fixed server/API: test JPEG EXIF/GPS, PNG tEXt/iTXt, WebP EXIF/XMP and orientation/ICC preservation; use randomized private test files and verify using independent exiftool/reference fixtures.
2. PDF rewrite needs warning for prior incremental versions, embedded XMP, signatures and redaction: deleting an Info dictionary alone is NOT guaranteed to remove hidden prior metadata; do not claim all metadata gone. Signed files may have their signatures invalidated.
3. Video removal (MP4/MOV/WebM) needs true stream-/container-level metadata verification, e.g. ffmpeg.wasm or byte-level parser; large mobile video and wasm memory are constraints. If unsupported, explicitly label limitations rather than fake "all files supported".
4. Verify 10+ true before/after format fixtures incl GPS, thumbnails, comments, EXIF, copyright/IPTC/XMP, scanned PDFs, Office authors, multiple streams and weird malformed files. Preserve pixels, playback, audio and PDF readability.
5. Ads page must explain privacy accurately; ad/analytics scripts may send network telemetry even when FILE BYTES remain local. Avoid blanket "no tracking/fully offline" with third-party Ads scripts.
6. Do not generate separate SEO pages merely because a keyword variation exists; cluster actual file-type intents only if tool workflows differ materially.
7. No domain, code repo, production site, SaaS repo or AdSense configuration changes until user authorizes; at this stage **STRONG_CANDIDATE_FEASIBILITY_FIRST**.

## B. United States — `minecraft ore finder`（第二优先：搜索环境较易，但准确算法成本较大）

**用户 Semrush 精确数据:** United States / desktop，`minecraft ore finder` **月搜索 4,400，KD 17，CPC USD1.08**；该词全球搜索量约11,400，主词占美国4,400。

| 相关词（意图可能互相覆盖） | 月搜索量 | KD |
|---|---:|---:|
| `ore finder minecraft` | 4,400 | 17 |
| `ore finder minecraft bedrock` | 1,300 | 13 |
| `ore finder for minecraft` | 210 | 17 |
| `where to find iron ore in minecraft` | 210 | 23 |

**真实前10 SERP（用户截图）**

| 排名 | 页面/归类 | 页面 AS | 页面引荐域名 | 该URL估算自然搜索流量/月 |
|---:|---|---:|---:|---:|
| 1 | https://www.orefinder.gg/ | 43 | 65 | 17,300 |
| 2 | https://www.chunkbase.com/apps/ore-vein-finder | 0 | 0 | 1,500 |
| 3 | https://diamondfinder.io/ore-finder | 1 | 1 | 2,800 |
| 4 | https://orefinder.io/ | 41 | 207 | 3,100 |
| 5 | https://www.seeds.gg/ore-finder | 11 | 1 | 1,900 |
| 6 | Reddit discussion | 0 | 0 | 3,000 |
| 7 | Google Play ore/diamonds finder | 0 | 0 | 111 |
| 8 | https://www.seedlander.com/minecraft-diamond-finder | 0 | 0 | 1,200 |
| 9 | YouTube video | 0 | 1 | 197 |
| 10 | CurseForge ore finder addon | 19 | 2 | 0 |

**Interpretation:** several low-page-link indie sites rank (#3, #5, #8), so entry is not blocked entirely by links. But #1/#4 have substantial page strengths; Chunkbase is strong brand even with 0 page-level AS. The two 4,400 variant terms are overlapping search intents, do **not** sum them as independent demand. The website https://www.orefinder.gg/ itself says it is not 100% accurate and publishes updates for Bedrock ore accuracy and version support (2026 Sep). Accurate exact-coordinate tools require Minecraft-specific seed RNG/chunk/world generation algorithms and version parity; browser-only technology is not equivalent to an easy implementable calculator.

**Comparison and decision:** 
- A metadata remover can be validated quickly against file fixtures entirely in browser, whereas a truly accurate Minecraft ore-seed-location tool needs generated-world ground-truth comparisons across Java/Bedrock versions. A static generic Y-level chart does not satisfy `minecraft ore finder` intent.
- New Minecraft site may be viable if developer can validate deterministic placement algorithm with ≥20 controlled worlds/chunks/editions and version handling, but cannot claim such support in advance. Existing https://voxelcurve.com/ is a DIFFERENT Minecraft geometry product; no production change approved.
- This idea is **SECONDARY_PROTOTYPE_ONLY**, not immediately approved standalone site. No further Semrush requests for either current phrase.

## Decision, user action and next step

**#1 Brazil `remover metadados`: conditional GO for engineering feasibility proof** (not unconditional public website launch). Search demand KD21 and multiple independently weak PAGE-level tool SERP results have been verified by the user's screenshots. File support, privacy, safety, usability and ad RPM still need proof; avoid overpromising metadata sanitization.

**#2 USA `minecraft ore finder`: hold candidate, prioritize only if a correct, maintainable ore placement calculation engine is available.** KD17 with several weak linked independent ranking pages but smaller country monthly demand and higher version algorithm maintenance.

**No further Semrush query needed now.** Ask user for go-ahead before creating a website/repository or modifying any existing site. A single research document records this batch; do not modify radar scripts/workflows or open unnecessary PRs.


## 2026-10-13 用户补充两份巴西 Semrush 相关关键词数据

数据源：用户直接提供的两组 Semrush Brazil 关键词列表，记录于2026-10-13。每个 Volume 是该精确词在巴西的估算月搜索量；KD 是 SEO 难度，CPC 为美元广告主出价指标。两组相同词重复，不可以按行累加，也不能把表示词关联度的独立百分数写成 KD。

### 可用于 SEO 定位的准确关键词

| 功能簇 | 精确关键词 | BR Volume/月 | KD | CPC USD | 页面建议 |
|---|---|---:|---:|---:|---|
| 通用 | remover metadados | 33,100 | 21 | 0 | `/` 首页主工具 |
| 通用 | limpar metadados | 9,900 | 16 | 0 | 首页同义词，不单独复制一页 |
| 通用 | removedor de metadados | 5,400 | 21 | 0 | 首页同义词 |
| 通用 | metadados remover | 4,400 | 24 | 0 | 首页 |
| 通用 | removedor metadados | 4,400 | 20 | 0 | 首页 |
| 通用 | tirar metadados | 2,900 | 28 | 0 | 首页 |
| 通用 | remove metadados | 1,900 | 25 | 0 | 首页 |
| 通用 | limpa metadados | 1,300 | 16 | 0 | 首页 |
| 视频 | remover metadados de video | 6,600 | 23 | 0 | `/remover-metadados-video` |
| 视频 | remover metadados video | 5,400 | 21 | 0 | 同一个视频工具页 |
| 视频 | limpar metadados video | 2,900 | 23 | 0 | 同一个视频工具页 |
| 视频 | tirar metadados de video | 1,900 | 21 | 0 | 同一个视频工具页 |
| 视频 | remover metadados vídeo online | 1,600 | 21 | 0 | 同一个视频工具页 |
| 视频 | limpar metadados vídeo | 1,000 | 24 | 0 | 同一个视频工具页 |
| 视频 | remover metadados de um video | 720 | 18 | 0 | 同一个视频工具页 |
| 视频 | remover metadados vídeo grátis | 590 | 23 | 0 | 同一个视频工具页 |
| 图片 | remover metadados imagem | 720 | 17 | 0 | `/remover-metadados-imagem` |
| 图片 | limpar metadados de imagem | 590 | 14 | 0 | 同一个图片工具页 |
| 图片 | tirar metadados imagem | 260 | 12 | 0 | 同一个图片工具页 |
| 图片 | limpar metadados imagem | 210 | 12 | 0 | 同一个图片工具页 |
| 图片 | remover metadados foto | 110 | 13 | 0 | 同一个图片工具页 |
| PDF | remover metadados pdf | 590 | 21 | 0 | `/remover-metadados-pdf`，仅支持可靠清理与复核时 index |
| 图片信息查看 | ver metadados de uma imagem | 1,600 | 23 | 0 | `/ver-metadados-imagem`，查看意图不同于删除 |
| 图片信息查看 | como ver metadados de uma foto | 880 | 22 | 0 | 同一个查看工具页 |
| 不同意图 | editar metadados pdf | 260 | 17 | 0.35 | 是“编辑”不是“删除”，不混页 |

视频上方多个 de video、video、vídeo、online 等近义/拼写变体，不能求和当作独立流量；不要为这些变体生成独立相似网页。不能把 Semrush 前两份关键词列表当作两个独立样本量。

### 必须排除的关键词污染

- 巴西企业 Metadados RH / Portal RH 相关导航词并非文件清理：portal rh metadados (2,400/KD28/CPC0.58)、metadados rh (1,000/KD23/CPC1.09)、rh metadados (480/KD21/CPC0.57)、suporte metadados (210/KD32/CPC1.70)、portal metadados (390/KD16/CPC0.63)。**禁止借助这些CPC证明清理工具的广告收入**。
- 品牌/导航：jc metadados (1,900/KD21)、metadados jc maciel (590/KD19)、remover metadados jc maciel (170/KD24)、remover metadados adarsus (50/未知KD) 等，不纳入非品牌需求。
- 泛义 metadados (8,100/KD43/CPC0.59) 是元数据概念或同名品牌混合词，不能视为独立删除工具的商业流量。
- 零搜索量且可能有实际用户价值的：remover metadados docx、remover metadados excel、remover metadados em lote 等。**可以作为工具功能但不是创建可索引独立网页的理由**。
- malformed 词如 remover metadados video] (140/未知 KD) 直接不作为目标。

### 新证据对产品立项判断的影响

1. 核心工具 BR 33,100 / KD21，及比较大的视频簇 6,600 / 5,400 等，提供了更坚实的 SEO 结构依据。多个独立低页面外链工具在主词 SERP 排名前5；该证据来自用户前一轮提供的完整截图。
2. 近乎所有**真正相关**非品牌工具词 CPC 均为 USD0；不能依赖高广告单价假设立项，不得虚构 AdSense RPM/月收入。
3. 既有 https://washfiles.com/pt/ 宣称可本地清理照片/视频/音频/PDF/Office、批量清理、输出元数据 JSON 与 SHA256；**无上传、浏览器本地处理并不是新项目的独家卖点**。必须用葡语移动体验、清理准确性、可验证的前后对比和视频操作成功率取得真实产品优势。
4. 新查 https://github.com/iAnonymous3000/metadata-remover 的 README：开源 Rust+WebAssembly 项目声称已实现 JPEG/PNG/WebP/HEIC/AVIF/GIF、MP4/MOV、MP3/FLAC/WAV/OGG、PDF、DOCX/PPTX/XLSX、ODF/EPUB 清理与二次验证；LICENSE 是 MIT。README 同时明确浏览器单文件100MB限制、BigTIFF/旧二进制 Office 等格式限制。**作者声明不等于本项目独立通过验收**，需审计依赖与对真实文件的正确性，遵守 MIT 版权许可通知。
5. 视频大文件不宜仅凭 ffmpeg.wasm 方案就假设快且稳定；官方性能文档显示 WASM 通常低于原生 FFmpeg，应优先评估上述已存在、目标为 metadata box 修改而无需重编码的视频方案。
6. 文件上传/下载必须是真实可交互的完整流程：选择文件 → 本地预览元数据 → 清理 → 独立重新检测输出 → 下载；对不能识别的字段显示“未确认/可能保留”，不作“100%匿名”承诺。PDF 增量历史版本/签名、包含嵌入内容的 Office、MP4/MOV 的复杂结构需单独验收。
7. 若未来接入 AdSense，要准确说明“**文件字节不上传**”与“广告/分析脚本可能发出网络请求”是两件事。避免工具页低价值内容、广告过度干扰。官方政策：https://support.google.com/adsense/answer/48182 及 https://support.google.com/adsense/answer/10502938 。

**明确状态**：STRONG_CANDIDATE_FEASIBILITY_FIRST。下一步优先做完整格式和性能验证，再决定独立站开发，不改用户任何现有站点/SEO/AdSense设置；无需再查已提供的巴西相关词 Volume/KD，Minecraft Ore Finder 是完全单独的第二候选。
