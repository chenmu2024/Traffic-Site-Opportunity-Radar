# 2026-10-13 巴西元数据清理：独立技术可行性验证

> 属于独立 SEO/AdSense 流量站研究；不是 SaaS 收入研究、未批准公开网站上线。第三方源码测试结果不等于新产品已经通过所有设备的验收。

## 1. 可重复的实际验证

- 上游 MIT 源代码：https://github.com/iAnonymous3000/metadata-remover；固定版本 SHA：2524864b3135d6a77fdbb635c571d6948f8b2b3d（2026-07-06）。复用时必须保留版权和MIT许可。
- 我们的独立审核运行：https://github.com/chenmu2024/Traffic-Site-Opportunity-Radar/actions/runs/38369440198 —— **GitHub Actions SUCCESS**。
- 独立可重跑工作流只在审核分支：https://github.com/chenmu2024/Traffic-Site-Opportunity-Radar/blob/audit/metadata-remover-wasm-feasibility-20261013/.github/workflows/metadata-feasibility-oneoff.yml 。没有把测试工作流合并到流量雷达 main，也没有更改生产网站。
- 上游 Rust cargo fmt --check 通过；cargo test --locked 结果 **119项模块测试+2项真实编码器测试通过，0失败**。 npm run check:js 的JS源代码语法检查通过。
- 另写独立 Rust 测试并调用公开库函数：对9份真实编码器样本——JPEG、HEIC、MOV、MP4、MP3、FLAC、WAV、OGG Vorbis、OGG Opus——独立验证原文件类型/合法性、清理、输出合法性、敏感标记消除和对输出重新扫描，**9/9通过**。
- 通过 ffprobe 与 FFmpeg 对7份音视频样本比对主要编解码轨道及解码后的MD5，**7/7一致**：MOV(H264)、MP4(H264)、MP3、FLAC、WAV PCM、OGG Vorbis、OGG Opus。FLAC中嵌入的封面附属轨可被移除，不能要求媒体所有附属封面字节不变。
- **重要限制**：公开 fixture 文件非常小，甚至 MOV/MP4 仅约1–2KB；本次不能当成30MB或80MB视频在手机上可靠运行的证据。Rust native测试不是实际 Android/iOS Safari 测试。

## 2. 支持范围的证据等级

| 类型 | 上游源码能力 | 本次独立证明 | 尚待验收 |
|---|---|---|---|
| JPEG / HEIC | 图片元数据清理 | 两份真实小文件通过 | GPS/EXIF、方向/ICC、手机真图及视觉正确性 |
| MP4 / MOV | 视频元数据清理 | 两份小样本通过，H264解码后MD5一致 | 大文件、时间戳、拍摄手机真实MP4/MOV、浏览器内存 |
| MP3 / WAV / FLAC / OGG | 音频标签和附属封面清理 | 五份小样本通过，解码后内容一致 | 更多私有tag、封面与播放器兼容性 |
| PNG / WebP / AVIF / GIF / TIFF / SVG | 上游Rust单元测试/README支持 | 未用独立大型真实样本验证 | 格式各10份以上真实测试，动画/颜色/外部资源边界 |
| PDF | 上游Rust单元测试/README支持 | 未独立测试复杂真实PDF | 增量更新历史、签名、附件、XMP、文档可读性 |
| DOCX / PPTX / XLSX / ODF / EPUB | 上游Rust单元测试/README支持 | 未独立验证Office文件 | 作者、批注、修订、嵌入图和办公软件正常打开 |
| 旧Office DOC/XLS/PPT、BigTIFF | 上游README明确不支持或部分拒绝 | 未做独立验证 | 不承诺支持，不建立虚假的格式内页 |

- 现有浏览器 UI **单文件限100MB**，批量内存预算依设备调整；不能宣传无限视频大小。
- 上游清理工序确实有检测、二次扫描和“Limited verification”类别，但这不构成所有未知私有元数据均彻底清除的证明。
- 源码基于 Rust+WebAssembly 可以纯静态部署，零文件服务器计算费用具有可行性。引入Ads/Analytics后，不能笼统宣传网站无任何网络请求；应准确区别“文件本身不上传”和“第三方广告网络通信”。

## 3. 巴西 SEO 已验证，可规划页面（并非现在直接索引）

| URL | 主要关键词 / BR Volume / KD | 条件 |
|---|---|---|
| / | remover metadados 33,100 / 21；limpar metadados 9,900 /16；removedor de metadados 5,400 /21 | 通用功能能真实使用 |
| /remover-metadados-video | remover metadados de video 6,600 /23；remover metadados video 5,400 /21 | MP4/MOV等真实手机文件及内存测试通过后才index |
| /remover-metadados-imagem | remover metadados imagem 720 /17；limpar metadados de imagem 590 /14 | 完整EXIF/GPS/图片一致性验证 |
| /remover-metadados-pdf | remover metadados pdf 590 /21 | PDF复杂样本/签名/历史风险验证后才index |
| /ver-metadados-imagem | ver metadados de uma imagem 1,600 /23 | 读取和清理是不同用户意图，可独立真实工具 |

已由用户提供核心词及前10名SERP，前4工具页面引荐域名数量仅3、2、3、0，是低页面级外链竞争证据，但不能将页面AS视为根域名AS。相近变体不能累加成独立潜在流量；巴西 Metadados RH品牌/导航词全部排除。

## 4. 真实差异化与验收条件

竞争者 https://washfiles.com/pt/ 已提供本地处理、批量、多格式和前后验证，因此“无上传”不是独家优势。我们需要争取的优点必须可实测：巴西 pt-BR 手机首屏快速可用、图片/视频处理成功率、前后字段对比、清理后再扫描、诚实反馈无法移除/无法验证的项目、符合隐私的广告布置。

建议后续用真实文件矩阵（至少每类10份独立样本）验证：GPS、EXIF、XMP、QuickTime位置/时间、iPhone/Android 30MB与80MB视频、PDF签名和增量历史、Office修订和嵌入图；同时分别用桌面Chrome/Firefox和安卓/iPhone Safari跑真实浏览器流程，核对输出可打开且内容未损坏。外部 ExifTool/FFmpeg用于独立检查，不只依赖同一个引擎自己声称清理成功。

产品流程：选择本地文件 → 读取元数据 → 显示项目与风险 → 点击清理 → 独立复核已清理/保留/未知 → 下载。针对不支持格式给出明确失败，不要编造“100%匿名”；PDF签名可能失效、附属封面可能被移除。

## 5. 商业性与决策

- 巴西几乎全部非品牌清理工具词用户截图 CPC USD0，不能承诺AdSense高收益或依靠 Metadados RH 导航词有较高 CPC。
- 竞品广告免费版+USD2/月高级版是存在商业模式的证据，但不是经过核实的收入数字。实际AdSense RPM和未来新域名SEO流量仍未知。
- **SEO/市场：通过需求初验；技术引擎：可继续采用；复杂PDF/Office与大手机视频：未通过完整验收；新站发布/Ads上线：尚未批准。**
- 下一步为非生产独立 pt-BR 工具原型+真实文件/浏览器兼容测试；确定可靠支持的格式后再一次性完整PRD/SEO/GEO/UI并免费托管。正式域名尚未确定，不能擅自改用户已有网站。
