# 2026-10-13：浏览器本地工具流量反查（配色、大小写、阅读时长）

> 仅适用于独立 SEO / AdSense 流量站。以下 Semrush 指标是具备来源的**整站全球自然搜索估算**和单独列示的国家级关键词 Volume、排名、CPC。不是 GA4、不是工具页自然流量、不是关键词点击量或 Adsense 收入。无关印度市场，不得用印度数据库主导的竞品校验用户机会。

## 研究结论速览

| 竞品 | 时间与全球自然搜索月估算 | 国别词 / Volume / Position / CPC | 排除或暂缓理由 |
|---|---:|---|---|
| [caseconverter.com](https://www.semrush.com/website/caseconverter.com/overview/) | Aug 2026 / 34,570 (-15.40%) | US `case converter` / 22,200 / #2 / $0 | AS31，576 引荐域名、成熟同类 Convertcase.net；普通大小写切换缺少差异化，广告价值未验证 |
| [titlecaseconverter.com](https://www.semrush.com/website/titlecaseconverter.com/overview/) | Sep 2026 / 37,270 (-8.37%) | US `title case converter` / 6,600 / #1 / $0 | AS41，约1.1k引荐域名，工具已支持 AP/APA/Chicago/MLA/Bluebook 等语法规则和大批量转换 |
| [paletton.com](https://www.semrush.com/website/paletton.com/overview/) | Sep 2026 / 78,490 (+4.93%) | US `color palette generator` / 60,500 / #9 / $1.26 | AS51，**13.5k 引荐域名**；真实复杂工具，显示广告可变现但利润未披露 |
| [colormagic.app](https://www.semrush.com/website/colormagic.app/overview/) | Sep 2026 / 26,750 (-10.89%) | US `color palette generator from name` / 1,000 / #1 / $2.22 | 部分最高排名词是 colormagic 品牌；特定功能核心词搜索需求低，通用 color palette generator 排名仅#11 |
| [gradients.app](https://www.semrush.com/website/gradients.app/overview/) | Aug 2026 / 158,930 (+6.13%) | BR `mistura de cores` / 12,100 / #1 / $0.41 | 全站自然搜索超10万目标上限；主页公开工具页面被反爬拦截，不能宣称已亲自验证该URL交互 |
| [wordstotime.com](https://www.semrush.com/website/wordstotime.com/overview/) | Aug 2026 / 41,470 (+2.81%) | US `words to time` / 4,400 / #1 / $0 | 词组与站名吻合，可能含品牌/导航；更明确的 `reading time calculator` 只有2,400搜索量，CPC$0 |

### 真正核实过的浏览器功能

- https://www.caseconverter.com/ 支持 uppercase/lowercase/proper/sentence case、复制文本和文本文件导出；与大型 https://convertcase.net/ 直接竞争。
- https://titlecaseconverter.com/ 有高级编辑规范和标题大小写解释，工具与内容互相支撑，而不只是一个 JS 公式。
- https://paletton.com/ 提供 RYB 色轮、单色/互补/三色/四色方案、WCAG 对比度、色觉模拟和 CSS/PNG/ACO/GPL 导出；官网原文称显示广告为唯一盈利来源，但公开站点没有披露月 AdSense 收入。
- https://colormagic.app/ 提供色板、图片提色、颜色混合、WCAG 颜色对比等工具；特色 AI 输入可能有运行模型成本，未证明纯静态零成本可复刻全部效果。
- https://wordstotime.com/ 是阅读/演讲时间简单估算器，用户输入字数和速度即可计算；官网注明部分链接有推广佣金，不能推断为 AdSense 收入。

### 本轮顺带核实、但不纳入目标市场候选

- [unzip-online.com](https://www.semrush.com/website/unzip-online.com/overview/)：Aug 全球自然搜索约23,790，公开排名表显示印度为首要国家，主要词 `unzip files online` 印度 6,600、排名#4。虽然目标站体量合适、可浏览器本地做压缩包解压，但用户明确不按印度主导流量寻找项目；不请求印度 Semrush。
- [textcompare.org](https://www.semrush.com/website/textcompare.org/overview/)：Aug全球自然搜索约45,410，公开榜单优先孟加拉 `text compare` 1,000、排名#6；没有对应巴西、墨西哥或美国的具体非品牌工具词流量证据。
- [base64-image.de](https://www.semrush.com/website/base64-image.de/overview/)：Aug全球自然搜索约43,150，但总访问量主要来自孟加拉，也没有经核实的 BR/MX/US 目标大词；不把整站自然流量错误当成该市场规模。
- [passwordsgenerator.net](https://www.semrush.com/website/passwordsgenerator.net/overview/)：Aug全球自然搜索约11,040，US `password generator` 1,220,000搜索量但自身排名#13，AS35约4,340引荐域名；高 Volume 无法推断新站可切入。

## 结论及改进

1. 这批的 **6 个结构化新候选全部不进入用户下轮 Semrush 查询队列**：3项成熟功能竞争、多站高外链、1项只有1k真实细分词、1项超10万上限、1项词义近品牌且明确非品牌工具词低于3k。
2. `paletton.com` 提供了**网站公开自述的展示广告商业化证据**，但没有可核实收入数字；记录商业模式而不是编造 AdSense RPM。
3. 网站即便靠功能做到 3万—8万自然搜索访问，也可能背后有 5百—1.35万引荐域名和长年工具迭代；不要把“JS 计算很容易”误当作“SEO获客很容易”。
4. 如果一个词搜索量高但 CPC 为0，优先核对实际广告表现再研究；CPC为0并不意味着AdSense绝无收入。
5. 已排除的 Pix/Placa Pix、树脂、标签、壁纸、找词、数字抽签、FPS灵敏度、GIF去背景、BR坏点等关键词继续禁止重复查询。
6. 只有出现新竞品 **实际自然搜索在目标区间 + 国家级有效非品牌核心工具词 + 真实可用功能页 + 可复制竞争弱点**，才请用户提供该具体核心词的 KD 或 SERP。不存在就如实交付0推荐。

整个研究过程仅使用公开网页证据、人工编录、免费 GitHub Actions；不需要付费 SEO API，也没有更改 SaaS 仓库、现有生产网站或 AdSense 配置。
