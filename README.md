# Traffic Site Opportunity Radar / SEO 流量站机会雷达

> 独立运行的搜索流量站发现与竞争分析项目。**不是 SaaS 收入研究。**

## 项目范围

专门寻找低成本的 SEO 工具站机会：优先巴西（BR）、墨西哥（MX）及其他西葡语国家，也可研究美国及英语市场；不以印度为主要市场。优先寻找估算月自然流量 10,000–100,000 的独立工具站，通过排名功能页、非品牌查询、竞争对手及真实搜索数据筛选，而非猜测流量。

两条机会雷达完全独立：
- `chenmu2024/Traffic-Site-Opportunity-Radar`：自然搜索流量、非品牌关键词、SERP、低 DR 排名、AdSense、免费工具。
- `chenmu2024/SaaS-Opportunity-Intelligence`：真实收费、MRR、付款证据和 SaaS 非品牌获客。

本仓库不读取、不写入 SaaS 仓库、不修改任何已上线网站或既有关键词，不自动建站。

## 已具备能力

1. **GitHub 网站线索发现**：每天最多三次公开 GitHub Search 查询，根据开源仓库提供的独立网站主页收集候选，状态始终是 `DISCOVERY_ONLY`。
2. **SERP 竞品扩散**：导入有出处、有国家和日期的 Google 排名 URL，建立同一关键词前 10 名网站之间的竞争关系，向种子网站外扩至两跳。
3. **弱站排名机会**：用户提供的一致 DR <= 20 且站点已有前 5 名排名时，给出弱站 SERP 证据标记。低 DR **不是**自然流量、KD 或可排名保证。
4. **关键词聚类**：按国家、相同的前 10 URL Jaccard >= 0.6（每词至少三个 URL）识别可能的同一搜索意图；不能直接累加搜索量。
5. **人工数据证据分层**：Volume/KD/CPC/自然搜索流量缺失保持未知。人工 CSV 录入值标为 `USER_SUPPLIED_UNAUDITED`；GitHub 提供的网站主页永远不作为搜索流量证明。

没有第三方 Python 包依赖、付费 SEO API、服务器或数据库。GitHub Actions 每天大约新加坡时间 08:00 运行；GitHub 定时任务可能延迟。

## 运行

```bash
python -m unittest discover -s tests -v
python radar.py                     # 仅导入本地证据，不联网
python radar.py --github-live       # 增加三个有限公共 GitHub Search API 查询
```

运行后生成 `reports/latest.json` 与 `reports/latest.md`。

## 实际 SEO 数据如何进入

先把已知真实竞品域名写入 `inputs/seeds.json`，再按国家将有真实来源的排名结果填写在 `inputs/serp.csv`：

```
country,keyword,rank,url,observed_on,source,domain_dr,volume,kd,cpc
```

`country` 仅允许 BR/MX/ES/PT/CL/US/GB；`rank` 为整数；`observed_on` 为 YYYY-MM-DD；`source` 必须能指向 Semrush/截图/导出的可核实记录。DR、Volume、KD、CPC 如果不知道请留空，不能编造。

可选将有出处的整站分国家月自然搜索流量估计导入 `inputs/sites.csv`：

```
domain,country,monthly_organic,source,observed_on
```

注意：这些指标仍是“用户录入、未被本程序独立审计”。使用 Semrush Organic Research → Pages / Positions，核实功能页、非品牌词占比和国家排名，并由用户决定是否立项。

## GitHub Actions

工作流：`.github/workflows/daily-traffic-radar.yml`。包括 Python 语法和单元测试、公开 GitHub 发现、JSON 验证、结果 artifacts，和在允许时只提交 `reports/latest.*` 到本仓库主分支；从不修改 SaaS 或其他仓库。

- 定时：每天 00:00 UTC（新加坡时间 08:00），调度时间可能延迟。
- 可在 Actions → Independent SEO Traffic Site Radar → Run workflow 手动触发。
- 若无法自动提交，请检查 Settings → Actions → General → Workflow permissions 是否允许 `Read and write permissions`。报告 artifact 仍可用。
- **本仓库当前为 Public**：提交至 `inputs` 和 `reports` 的数据是公开的，不要在公开文件中上传敏感 Semrush 截图、私人账户信息或 API 密钥。

## 约束

本系统不能通过 GitHub Stars、Sitemap、网站收录或 HTTP 成功请求自动推断真实 Google 流量。SEO API 数据没有就保持未知，不输出伪造的数字。每天宁可没有合格候选，也不能把未经验证的主页线索包装成“验证通过的流量站”。


## 国家级 SEO 证据工作单（新增）

雷达新增 triage.py，独立对人工导入的功能页关键词排名和整站自然搜索流量作交叉筛选，**不把 GitHub 主页、Stars 或主页存在当成流量证据**。

数据入口：

- inputs/positions.csv：必须有 country,domain,keyword,position,url,volume,kd,cpc,observed_on,source,nonbrand_review,tool_intent_review。
- inputs/sites.csv：已有 domain,country,monthly_organic,source,observed_on。
- country 支持 BR、MX、ES、PT、CL、US、GB；不使用印度市场数据立项。
- position 必须是实际记录的 1–100 整数，观察时间不应在未来；90 天以上的排名/流量观测会要求重新检查。
- nonbrand_review 和 tool_intent_review 只允许 YES、NO、UNKNOWN。只有研究者确实人工核对非品牌 + 需要使用工具的意图后，才能填 YES；留空会被当作 UNKNOWN。
- Volume、KD、CPC 缺失留空，系统不会猜测，导入字段只标记 USER_SUPPLIED_UNAUDITED。
- 只考虑同一国家的自然搜索流量估计 10,000–100,000/月，且至少两个已人工确认的非品牌工具关键词同时满足排名前20、Volume ≥500 和 KD ≤30，才列入 READY_FOR_FINAL_SERP_REVIEW。此状态仍不等于建站批准。
- 按功能 URL 分组和人工 SERP 重合分析，防止简单相加同义词搜索量。

单独运行：

    python triage.py
    python triage.py --positions /your/local/positions.csv --sites /your/local/sites.csv --output-dir /your/local/reports

输出报告为 reports/triage.md 和 reports/triage.json。日常 GitHub Actions 会刷新这两个文件，并将它们与最新的公开发现线索一起作为 artifact 保存。

**隐私提醒：仓库是 Public。不要将购买或受授权限制的 Semrush 原始 CSV、截图、私人账户数据及密钥直接提交到 inputs/ 或 GitHub Actions 日志。** 推荐在本地或本对话中提供用于研究的必要指标，再决定是否只向仓库提交你愿意公开的汇总字段。GitHub 自动运行的公开模板仍可能没有任何符合证据门槛的候选；这是正确输出，不是系统故障。

研究必须严格区分：
1. GitHub DISCOVERY_ONLY：只证明某个项目提供了一个主页线索。
2. USER_SUPPLIED_UNAUDITED：有用户记录的关键词/国家/来源/日期，但尚未独立审计。
3. READY_FOR_FINAL_SERP_REVIEW：满足人工意图审查、需求与流量阈值，可核查 Google SERP 的候选。
4. BUILD：仅在独立检查 SERP、竞争对手、可获客优势、AdSense 收益和成本，并经用户批准后才可能进入。系统不会自动提升到 BUILD。

## GitHub 上游发现质量与历史去重

新增 discovery_quality.py，将技术线索与真正经过数据核实的 SEO 机会严格分开：

- 每天公开 GitHub API 搜索三个技术方向，按葡语/西语/英语词根轮换，并记录实际查询语句。查询词语言不等于目标国家，更不代表目标国家有自然流量。
- 保存公开仓库名称、description、源码 URL、Star 快照；排除归档和 fork，识别 awesome 目录、课程、挑战、练习代码和非独立托管主页。
- 用 TECH_LEAD_TO_INSPECT / LOW_PRIORITY_TECH_LEAD / SKIP_GITHUB_SOURCE 分层。技术适配得分只是核对产品页面的优先级，并非 SEO 流量、关键词排名或商业收入评分。
- data/site-history.json 记录站点首次出现日期和采集次数（不是访问量）。所有数据源都失败时保留历史，不把抓取失败包装成 0 流量。
- 新报告 reports/discovery-quality.md / reports/discovery-quality.json，每天只展示最多五个技术线索供公开页面核查。
- GitHub 线索不会自动产生 Semrush 查询要求。只有确定具体国家、非品牌关键词、真实功能 URL、竞争页面并找到公开来源后，才提出精确的人工数据查询清单。
- python discovery_quality.py 可从已有 reports/latest.json 构建研究工作单，Python 标准库无需新依赖。

该发现通道不访问私人竞争对手数据，不绕过搜索引擎爬虫限制，不会把 Github Stars 误当作真实流量。

## 2026-10-13：防止桌面软件、教程和收费平台污染流量站机会

- 浏览器工具机会优先考虑独立注册域名上的真实在线交互工具页面；站点 homepage 指向下载页面、教程、源码展示页或个人站内页时会自动降级或拒绝。
- 识别常见桌面专用技术标签（如 PySide、Tkinter、Windows 离线安装器）并排除，避免把桌面产品仓库的 GitHub Stars 当成在线工具站流量。
- 代码库 data/manual-site-decisions.json 保存研究者明确排除的网站、具体原因、证据 URL 和复查日期；审计记录不是黑箱算法规则。
- 目前已核对 File Converter Pro、XL Converter、Codante React IMC 教程、favr.dev 的开源页面与 Fichas de Nimb 订阅型 RPG 平台，对当前以低成本在线工具和 AdSense 为主的选题不进行 Semrush 查询。
- 被排除的项目仍保留在历史研究记录中，并不表示其真实搜索流量为零、产品质量差或完全没有商业价值。
- 只有独立核对真实在线工具功能、非品牌搜索入口和国家市场后，才请求用户查询具体的 Semrush Volume、KD、CPC 和竞争页面。
