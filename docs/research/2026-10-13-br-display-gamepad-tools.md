# 2026-10-13 · 巴西屏幕坏点检测 / 手柄测试的竞品反查

> 所有流量数据来自 Semrush 的公开网站概览，属于第三方对 **全球整站 organic search traffic 的估计**；不是特定工具 URL 的点击、不是巴西单国自然搜索访问量、更不是后台真实收入。所有关键词量为 Brazil 数据库，不能把词的搜索量相加推测工具站真实点击。

## 1. 首选进一步检查：deadpixeltest.org

- 公开来源：https://www.semrush.com/website/deadpixeltest.org/overview/ ，2026年8月。
- 整站全球自然搜索流量估算 **53,460/月**，环比 **+14.16%**；Authority Score **38**。
- Brazil / `dead pixel test`：排名 **2**、Volume **9,900/月**、CPC **USD 0**。
- Brazil / `checking dead pixels`：排名 **2**、Volume **5,400/月**、CPC **USD 0**。
- Brazil / `dead pixel detector`：排名 **3**、Volume **4,400/月**、CPC **USD 0**。
- 真实可用在线工具：https://deadpixeltest.org/ ，通过全屏多色轮换检查坏点；另有 stuck pixel fixer、screen contrast、screen resolution 等工具。没有用户账户或付费 API 的核心必要性。
- 竞争： https://deadpixeltest.com/ 、https://deadpixeltester.com/pt 、https://pixeltest.net/pt/monitor-screen-test 。功能普遍包含坏点/色彩/对比度；不应该认为做出相同基础功能就一定可以取代已有站点。
- 风险：主竞品 Authority Score 38，外链域名公开约946；真正的 Google 前十位中是否有弱站尚未核实，且核心词 CPC USD0，无可靠 AdSense RPM 数据。
- **仅需下一项数据（若用户愿意核实）**：Semrush Keyword Overview **Brazil / `dead pixel test`** 的 **KD**，最好同屏提供 SERP Analysis 前十名域名。如 KD 高或SERP全部高权重，则淘汰，不继续查长尾。

## 2. 超出10万边界、仅作参照：gpadtester.com

- 公开来源：https://www.semrush.com/website/gpadtester.com/overview/ ，2026年8月。
- **全球整站自然搜索流量估算 108,710/月**，环比 +6.23%，高于原定 100,000 上限（不能把 Visits 727,860 混为 SEO 自然流量）。Authority Score 26，约547个 referring domains。
- Brazil / `gamepad tester`：排名3、Volume33,100/月、CPC USD0；`gamepad check` 排名3/Volume9,900；`teste gamepad` 排名2/Volume4,400，意图可能重合，不相加。
- 真实工具：https://gpadtester.com/，Gamepad API 手柄按钮、模拟摇杆漂移、振动及部分校准工具。
- 竞品：https://gamepadtesterr.com/ 、https://controller-test.com/ 、https://www.prodevicetest.com/pt/controller-test/ 均提供无安装的网页测试。
- 现阶段只作“需求真的存在”的参照站而不是严格10k–100k候选；CPC为零，浏览器硬件 API 功能受限，复制 UI 并不能说明可拿到排名。
- **不向用户要求 gamepad tester KD**：先审核更符合流量目标范围的坏点检测方向。

## 3. 本轮排除或无需用户验证

- `gamepadla.com`: Semrush 2026年8月全球自然搜索估算18,280，但公开的主要关键词国家为 Bangladesh， `controller test`/`gamepad tester` 在当地仅第53/61位；不足以支持巴西/墨西哥非品牌工具页自然流量结论。https://www.semrush.com/website/gamepadla.com/overview/。它的独有内容是实测手柄延迟数据库，需持续采集与测试设备，不符合简单独立静态工具站的最低维护成本。
- `vulcanvalues.com`: Semrush 2026年8月全球自然搜索估算22,960（-34.73%）；巴西 `grow a garden stock` 排名3、Volume3,600。属于游戏实时库存查询，维护实时数据的可靠来源与变更频率不明。https://www.semrush.com/website/vulcanvalues.com/overview/。先不要求用户查询搜索量和 KD。

## 研究纪律

1. 依旧先证实竞品真实自然搜索规模、国家非品牌工具词、有操作的功能 URL，再考虑 KD/SERP；当工具词 CPC=$0 时尤其谨慎评估 Ads 收益。
2. 关键词排名不证明某一页面的自然流量；月流量指标来自第三方估算；DR与 Authority Score 是不同平台口径。
3. 主词 Volume 很高也不能跳过竞争审核。若 KD>35 且没有低权重 SERP 的独立证据则先暂停。
4. 此研究与 SaaS 商业收入验证完全分离，不变更用户已运营网站，不复查之前淘汰的 Pix/Placa Pix、树脂、标签、壁纸、找词、数字抽签和 FPS sens converter。
5. 本期依据公开网页人工研究加入两个静态快照；GitHub Actions 每天自动测试、重算报告，但**不能在免费公开 API 无 Semrush 权限时声称自动采集了实时 Semrush 流量**。
