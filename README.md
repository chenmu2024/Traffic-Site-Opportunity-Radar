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
