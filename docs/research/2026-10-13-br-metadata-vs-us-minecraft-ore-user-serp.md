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
