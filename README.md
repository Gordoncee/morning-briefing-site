# AI法智前沿 · 每日资讯

每日资讯由本仓库独立采集、归档、生成和发布。案例库保留在 `Gordoncee/AI-Case`，两个仓库不合并。公开资讯页面使用与案例库一致的品牌、导航、背景和阅读样式。

- 正式网站：https://fazhi.cc/news/
- 案例库：https://fazhi.cc/
- 运行位置：GitHub Actions 临时运行器；网站托管在 GitHub Pages。
- 不需要个人电脑开机，不向 ECS 安装采集程序、数据库、模型或定时任务。

2026-10-26：所有公开导航、资讯归档／详情、资源和 canonical URL 均使用 `https://fazhi.cc`。GitHub Pages 仍是构建产物源站，由现有 ECS 在 `/news/` 安全代理；源站访问不携带用户 Cookie 或认证头。旧 GitHub Pages 收藏会跳转对应的正式资讯页，查询参数和段内锚点保留；外部媒体原文链接保留原始出处。来源、模型、密钥与每天的定时采集保持原配置，所有资讯仍独立从 Markdown 构建，不需要 ECS 运行采集或模型。

## Markdown 是资料的唯一维护来源

| 路径 | 内容 |
| --- | --- |
| `archive/sources/config.md` | 原有 8 个媒体 RSS 入口、5 组 Google News 查询、候选数量 |
| `archive/sources/YYYY/MM/YYYY-MM-DD.md` | 当日全部成功取得的 RSS 条目、原描述/未截断摘要、标题、链接、原始发布时间、每个入口成功或失败状态；另记录送模型的候选链接 |
| `archive/briefings/YYYY/MM/YYYY-MM-DD.md` | 完整中文简报、关注点、逐条摘要/观察和原文链接 |
| `archive/runs/YYYY/MM/YYYY-MM-DD.md`（失败时） | 生成失败状态；已保存的 RSS 和此前有效简报保持不变 |

MD 使用可读标题和紧凑 JSON 数据块，避免同一正文再存一份，不执行 JavaScript。最初迁移的 127 期简报（2026-06-11 至 2026-10-15）无损保存，总计约 737 KiB。当时程序没有保存历史 RSS 原始输入，这些期数明确标记 `historical-input-unavailable`，不会把后补材料伪称为当时原文。

“原始采集记录”是 RSS 实际返回的条目与摘要，不等于媒体网页全文。不能获取的入口记录 HTTP 状态及错误类型，不编造正文。模型看到的摘要仍最多 220 字符、候选仍最多 30 条；归档保留完整 RSS 摘要及未选入模型的已取得条目。

`data/briefings.js` 仅是从 MD 派生的兼容输出，不作为人工编辑入口。`dist/` 是临时构建产物，Git 忽略，由 Pages artifact 发布，不在主分支重复保存整站 HTML。后续不再每日生成或提交分享 PNG；既有历史图片不重写或强制清除 Git 历史。

## 自动更新

`.github/workflows/morning-briefing.yml` 每天北京时间 07:30 开始，07:45、08:05、08:20、08:35 为早间补跑；另在 **13:15、16:15** 各安排一次下午补跑。以上为计划时间，GitHub 调度仍可能延迟。当天已有简报时，补跑复用仓库中的 Markdown，跳过重复采集和模型调用；缺少当天简报时继续尝试采集、生成、归档和发布。来源配置及生成器、模板变更后，也会自动检查并发布。

流程：读取 MD 信息源配置 → 访问全部 13 个现有入口/查询 → 先归档原始 RSS → 为缺失日期调用千问 → 校验并保存简报 MD → 提交资料回本仓库 → 从 MD 构建静态页面 → 在同一工作流显式部署 GitHub Pages。

2026-10-29 修复模型输出与网页构建格式不一致：两阶段共用 `scripts/briefing_schema.py`。摘要、影响、后续观察若返回纯文字列表，逐项以分号连接，保留全部文字；对象、数字、混合列表仍拒绝发布。已归档的可修复格式在补跑时自动修复，无需重新采集或调用模型；无法修复的当天归档会重新生成，避免后续补跑永远跳过坏数据。新模型输出必须通过同一格式检查才保存为简报，格式不合格最多追加一次生成尝试，仍失败保留 RSS 与原线上页面。来源、模型、API 地址和密钥不变。

2026-10-28 起，每次发布后用 `scripts/verify_news_sync.py` 核对 **GitHub Pages 源站与正式 `https://fazhi.cc/news/`** 的首页、当前导航参数入口和最新一期详情。构建器从 Markdown 计算完整简报集合的 SHA-256，将同一内容版本写入每页元数据及 `data/news-status.json`；核查同时要求当天日期和内容版本一致，可发现同一天修订尚未同步的情况。版本信息不包含密钥或内部资料。

自动核查最多尝试 8 次、间隔 45 秒，覆盖正式域名原有的 5 分钟代理缓存窗口。第一次核查失败会复用当前工作流已上传的 Pages 成品补发一次，再次验收；仍失败则工作流明确失败，保留检查报告 `news-sync-check-运行编号` 7 天，由下一次早间或下午任务继续尝试。不会为了网页同步重新调用模型，不向服务器增加采集进程或定时任务，也不清除现有缓存或更改其他站点。

手动核查（先运行构建器；默认要求仓库与网页均包含北京时间当天简报）：

```sh
python3 scripts/build_news_site.py
python3 scripts/verify_news_sync.py --report sync-report.json
```

模型或输出校验失败时，原始 RSS 仍提交 Git，网页保留最近有效简报，工作流报告失败。Git 提交或静态构建失败时不部署新页面；恢复 artifact 保留 7 天。Pages 使用 Actions 发布，避免 `GITHUB_TOKEN` 提交不能触发传统分支 Pages 构建的问题。

## 模型与密钥

- `MODEL_PROVIDER=qwen`
- `QWEN_MODEL=qwen3.8-max`
- `LLM_BASE_URL=https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1`，沿用原地址。
- 密钥继续引用 GitHub Secrets 的 `DASHSCOPE_API_KEY`；密钥值、请求头和环境文件不写入 MD、Git 或 Pages。
- `MODEL_NAME` 如有值会覆盖 `QWEN_MODEL`，日常保持为空；手动工作流可以显式覆盖。

来源列表、Google News 关键词、输出条数和编辑要求沿用原配置，不把资讯写进案例首页。

## 换电脑或交给其他维护者

只需有该仓库权限即可在 GitHub 修改 MD 来源配置、运行工作流或查看失败记录，不依赖原电脑目录、SQLite、坚果云或本地 Python 环境。历史简报和实际采集输入都在仓库里。

本地核查可用标准 Python（不需要密钥、数据库或联网）：

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_news_site.py --output /tmp/daily-news-site
```

仅归档、无需模型时：`python3 scripts/generate_morning_briefing.py --collect-only`。正常生成默认不覆盖已有日期；只有明确传 `--force` 才会再次调用模型重做该日。

## 页面同步（2026-10-23）

资讯站导航已与案例站统一为首页、国内典型案例、全球典型案例、法律法规、团队评析、关于团队。国内与全球栏目分别链接 `/cases/` 和 `/global-cases/` 独立页面；不再使用旧的 `/#explore` 入口。共享样式、导航脚本及页底建议与补充提示同步自案例站；资讯归档、采集来源、模型、密钥和定时计划保持原配置。后续调整案例站公共导航时，应同步 `site/templates/base.html` 与 `site/assets/` 并运行本仓库测试和构建，避免两个独立站点的页面版本脱节。

2026-10-23 补充：首页以外六个栏目顶部背景使用公共 `--page-hero-height`，当前为 340px；横向通栏，桌面与手机保持一致。资讯导航版本为 `20261023-headers`，公共尺寸修改也应同步该入口版本和案例站的对应缓存标记。
