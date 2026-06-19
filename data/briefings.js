window.MORNING_BRIEFINGS = [
  {
    date: "2026-06-19",
    displayDate: "2026年6月19日",
    scope: "全球新闻｜科技与财经优先",
    image: "assets/morning-briefing-2026-06-19.png",
    summary: "今日纳入5条，均为近24小时内出现的可核验新进展；为避免重复，未继续追踪Fed会后交易、SpaceX上市后波动、中东和平协议后续、Anthropic模型解禁谈判和Intel 18A-P试产同一主线。",
    focus: [
      "AI算力需求正在从数据中心成本外溢到消费电子价格、半导体供应链和亚洲股市权重。",
      "企业AI落地开始接受利润表检验，咨询、软件与网络安全公司的估值逻辑正在分化。",
      "金融市场基础设施的创新边界继续前移，预测市场和加密衍生品监管会影响传统交易所护城河。"
    ],
    items: [
      {
        title: "特朗普称Apple将与Intel合作在美国设计制造芯片，Intel股价单日大涨约11%",
        region: "美国、Apple、Intel、先进半导体制造",
        sources: ["MarketWatch", "Axios"],
        summary: "特朗普在社交平台称，Apple已同意与Intel合作，在美国设计并制造芯片。MarketWatch和Axios均报道，Intel股价周四上涨约11%，市场把这视为Intel Foundry争取外部大客户的更正式信号；但报道也提示，Apple和Intel尚未披露具体芯片、产量和时间表，分析师认为初期项目可能规模较小。",
        why: "这不同于昨日18A-P进入风险生产的技术节点，而是潜在客户侧的新信号。若Apple真的把部分芯片订单交给Intel，美国本土先进制造叙事会从政策支持进入商业订单验证；若只是低量组件，市场对Intel的重估可能过快。",
        watch: "Apple或Intel是否正式确认合作细节，首批芯片是否采用18A/18A-P节点，以及TSMC、Samsung在美国本土产能竞争中的响应。"
      },
      {
        title: "Tim Cook称Apple产品涨价“不可避免”，AI内存短缺开始传导到消费电子",
        region: "Apple、Micron、Samsung、SK Hynix、全球消费电子",
        sources: ["WSJ", "MarketWatch", "The Verge"],
        summary: "Tim Cook接受WSJ采访时表示，因DRAM和NAND等内存、存储芯片成本暴涨，Apple将不得不提高产品价格。MarketWatch报道称，Micron、Western Digital、Sandisk等存储链公司股价随之走强；The Verge也指出，AI数据中心需求正在挤压手机、电脑和游戏设备的存储供给。",
        why: "AI资本开支不再只是云厂商和芯片股的故事，它正在通过内存价格进入普通消费者账单。Apple这样的采购巨头都无法完全吸收成本，说明AI服务器需求已足以改写消费电子利润率和定价。",
        watch: "9月iPhone 18定价、Mac和iPad是否先涨价，DRAM/NAND供需缺口能否在2027年前缓解，以及Micron下周财报对内存周期的确认程度。"
      },
      {
        title: "Accenture下调全年增长预期并创纪录大跌，AI咨询热潮首次遭遇需求与估值双重压力",
        region: "Accenture、全球IT服务、企业AI落地、工业网络安全",
        sources: ["FT", "MarketWatch", "WSJ"],
        summary: "Accenture公布季度业绩后把全年收入增长预期收窄至3%至4%，新订单降至193亿美元，并称中东冲突造成约1亿美元收入影响。公司股价周四下跌约18%，FT称其跌至2017年以来低位。与此同时，Accenture宣布以约42亿美元收购Dragos多数股权并买下runZero、NetRise，押注工业网络安全。",
        why: "这说明企业AI咨询和传统IT服务不一定同步受益于AI浪潮：客户可能减少人工密集型外包，同时要求更具体的安全和运营结果。资本市场开始区分“讲AI转型故事”和“实际获得可见订单”。",
        watch: "Accenture能否把工业网络安全并购转化为经常性收入，AI工具是否继续压低咨询人力单价，以及Infosys、Capgemini、IBM等同行是否跟随下调展望。"
      },
      {
        title: "CME起诉CFTC阻止Kalshi永续合约，预测市场与传统衍生品交易所正面冲突",
        region: "美国、CME、CFTC、Kalshi、预测市场与加密衍生品",
        sources: ["FT", "WSJ"],
        summary: "CME起诉美国商品期货交易委员会，试图阻止Kalshi上线无到期日的永续合约。FT和WSJ报道称，CME认为CFTC把该类产品归为期货、而非更严格监管的掉期，绕过了Dodd-Frank框架和公开审查；Kalshi和CFTC则把争议描述为竞争与创新问题。",
        why: "预测市场正在从事件合约扩张到更接近主流交易的衍生品结构，直接触碰传统交易所的监管护城河。如果Kalshi胜出，零售化、全天候、低门槛的金融合约可能更快进入主流市场。",
        watch: "法院是否暂停Kalshi产品上线，CFTC是否补充规则制定程序，以及Coinbase、Polymarket等平台是否借此推进更多受监管合约。"
      },
      {
        title: "Noam Shazeer离开Google加入OpenAI，AI顶级人才争夺继续压缩巨头护城河",
        region: "OpenAI、Google DeepMind、Character.AI、AI基础模型竞争",
        sources: ["Axios", "Barron's", "Business Insider"],
        summary: "Axios、Barron's和Business Insider均报道，Gemini关键研究员、Character.AI联合创始人Noam Shazeer将离开Google加入OpenAI。Shazeer曾参与Transformer奠基论文和Gemini项目，Google 2024年曾以约27亿美元交易取得Character.AI技术授权并让其回归。",
        why: "前沿AI竞争的稀缺资源仍是少数核心研究员和工程组织能力。Google用巨额交易换回的人才不到两年后转投OpenAI，说明大公司通过授权或“反向收购式招聘”锁定人才的效果并不稳固。",
        watch: "Shazeer在OpenAI负责模型研究还是产品化，Google是否调整Gemini团队结构，以及OpenAI、Anthropic、Meta是否继续用高额薪酬和股权争夺核心研究员。"
      }
    ],
    sourceLinks: [
      "https://www.marketwatch.com/story/intel-shares-rally-as-trump-says-company-will-build-chips-for-apple-in-the-u-s-c72d8c88",
      "https://www.axios.com/2026/06/18/intel-stock-apple-trump",
      "https://www.wsj.com/tech/apple-price-increases-memory-supply-199845b1",
      "https://www.marketwatch.com/story/microns-stock-is-on-the-rise-even-apple-isnt-safe-from-ballooning-memory-chip-costs-ddd04d74",
      "https://www.theverge.com/tech/951948/apple-tim-cook-price-increases-ram",
      "https://www.ft.com/content/9f063b07-da39-4feb-92ab-ee0f91385c62",
      "https://www.marketwatch.com/story/two-big-reasons-accentures-stock-is-sliding-in-the-wake-of-earnings-9353b184",
      "https://www.wsj.com/pro/cybersecurity/accenture-takes-majority-stake-in-cyber-company-dragos-bb536634",
      "https://www.ft.com/content/5e90353f-cefd-4f3d-aaf9-830244bd5b20",
      "https://www.wsj.com/finance/regulation/cme-sues-u-s-regulator-to-stop-kalshi-from-offering-popular-perp-futures-f96e97fe",
      "https://www.axios.com/2026/06/18/noam-shazeer-google-openai-characterai",
      "https://www.barrons.com/articles/openai-ai-alphabet-stock-shazeer-6f5a9950",
      "https://www.businessinsider.com/google-veteran-founded-characterai-is-jumping-to-openai-talent-war-2026-6"
    ]
  },
  {
    date: "2026-06-18",
    displayDate: "2026年6月18日",
    scope: "全球新闻｜科技与财经优先",
    image: "assets/morning-briefing-2026-06-18.png",
    summary: "本期只纳入4条，原因是避免重复昨日的G7 AI治理、AI发债、SpaceX/Cursor并购和Fed会前交易主线；今日保留Fed实际决议、Intel先进制程节点、Frontier碳移除资金和Snap AR眼镜商业化四个可核验新进展。",
    focus: [
      "美联储从降息预期转向可能加息，科技股估值和长期资本开支折现率会重新承压。",
      "先进制程竞争进入客户验证阶段，Intel能否拿到外部客户将影响AI芯片供应链格局。",
      "AI与硬件、气候科技、企业安全的交叉场景开始接受真实市场检验，价格、需求和治理会比概念更重要。"
    ],
    items: [
      {
        title: "美联储维持利率不变但暗示年内可能加息，Warsh首秀结束降息叙事",
        region: "美国、Fed、全球股债市场、科技股",
        sources: ["Axios", "The Guardian", "Barron's"],
        summary: "Kevin Warsh首次主持FOMC会议，美联储一致决定把联邦基金目标利率维持在3.5%至3.75%，同时最新预测显示多名官员预计年内仍可能加息。会后美股走弱，市场从此前的降息交易切换到更谨慎的通胀与利率路径定价。",
        why: "这不是昨天“等待Fed会议”的延续，而是实际政策结果发生了变化：Warsh用更短声明和弱化前瞻指引开启新沟通风格，也把AI和科技股的高估值重新放回利率约束下。",
        watch: "后续通胀数据是否支持年内加息，Fed是否维持更少前瞻指引的沟通方式，以及纳指和AI硬件股能否消化更高贴现率。"
      },
      {
        title: "Intel 18A-P进入风险生产，先进制程反攻从路线图走向客户验证",
        region: "Intel、TSMC、Apple、Nvidia、先进半导体制造",
        sources: ["Barron's", "Tom's Hardware", "MarketWatch"],
        summary: "Intel披露18A-P制程已进入风险生产阶段，相比18A可在同功耗下提升约9%性能，或在同速度下降低约18%功耗。Barron's和MarketWatch称，这一节点将帮助Intel Foundry争取外部客户，但真正关键仍是良率、产能稳定性和能否获得Apple、Nvidia等大客户订单。",
        why: "AI芯片供应链高度依赖TSMC，Intel如果能把18A-P从试产推进到可靠量产，可能改变先进制程议价格局；如果良率跟不上，Foundry亏损压力会继续拖累估值。",
        watch: "Apple或Nvidia是否确认试产，18A-P良率和热设计数据是否继续改善，以及Intel Foundry下一季亏损是否收窄。"
      },
      {
        title: "Frontier新增9.15亿美元碳移除承诺，Anthropic加入科技巨头气候采购联盟",
        region: "Frontier、Anthropic、Google、Stripe、Salesforce、气候科技",
        sources: ["Frontier", "WSJ"],
        summary: "Frontier宣布新增9.15亿美元碳移除采购承诺，参与买家包括Stripe、Google、Shopify、Salesforce、H&M Group以及新加入的Anthropic，使总承诺规模达到18亿美元。Frontier表示，新资金将更集中投向具备吉吨级潜力且有长期需求路径的技术组合。",
        why: "这说明大型科技公司在AI算力扩张带来能源和排放压力的同时，也在用长期采购合同扶持碳移除供应链。对气候科技创业公司来说，确定性需求比短期补贴更能支撑融资和商业化。",
        watch: "资金实际流向哪些碳移除路径，Anthropic等AI公司是否把碳采购纳入算力扩张披露，以及政府采购或合规市场能否接上企业自愿需求。"
      },
      {
        title: "Snap推出2195美元消费级AR眼镜，投资者质疑高价硬件能否撑起下一代计算入口",
        region: "Snap、Meta、Apple、Google、AR智能眼镜市场",
        sources: ["The Verge", "MarketWatch", "Axios"],
        summary: "Snap在AWE 2026推出消费级AR眼镜Specs，预售价2195美元，计划今年秋季在美国、英国和法国发货。设备主打独立AR体验、约4小时续航和51度视场角，但MarketWatch报道称，Snap股价在发布后连续下跌，投资者担心高价格、重量和持续AR投入会拖累核心广告业务。",
        why: "智能眼镜从AI音频眼镜走向真正AR显示仍面临价格、重量、续航和应用生态四重门槛。Snap选择先做高价早期用户产品，等于把“手机之后的入口”叙事提前交给市场检验。",
        watch: "秋季发货后的退货率和开发者应用数量，Meta与Google是否推出更低价竞品，以及Snap是否继续为AR业务单独融资或缩减投入。"
      }
    ],
    sourceLinks: [
      "https://www.axios.com/2026/06/17/fed-warsh-interest-rates",
      "https://www.theguardian.com/business/2026/jun/17/federal-reserve-interest-rates",
      "https://www.barrons.com/livecoverage/fed-meeting-june-rates-warsh-news/card/read-the-full-fomc-statement-zwigT0BzD319fBDqH9h2",
      "https://www.barrons.com/articles/intel-stock-price-foundry-18ap-chips-2cd104d5",
      "https://www.tomshardware.com/tech-industry/semiconductors/intels-performance-enhanced-18a-p-process-enters-risk-production-enhanced-node-promises-9-percent-performance-improvement-at-iso-power",
      "https://www.marketwatch.com/story/intel-takes-a-major-step-toward-turning-around-a-business-thats-bleeding-cash-ab68cc94",
      "https://frontierclimate.com/writing/growth-amc",
      "https://www.wsj.com/tech/tech-media-telecom-roundup-market-talk-c2c29be4",
      "https://www.theverge.com/tech/950492/snap-specs-ar-glasses-launch-date-preorder",
      "https://www.marketwatch.com/story/snap-breaks-from-the-pack-with-heavy-2-195-smart-glasses-wall-street-is-panning-the-move-99e77ae6",
      "https://www.axios.com/2026/06/16/snaps-ar-glasses-specs"
    ]
  },
  {
    date: "2026-06-17",
    displayDate: "2026年6月17日",
    scope: "全球新闻｜科技与财经优先",
    image: "assets/morning-briefing-2026-06-17.png",
    summary: "今日主线是AI从产业叙事进一步进入外交、资本市场、竞选资金和超级平台并购：G7讨论AI主权，英伟达债券融资放大AI基建杠杆，SpaceX用高估值继续并购AI工具。",
    focus: [
      "AI竞争正在从公司产品竞争升级为国家间基础设施、监管与主权能力竞争。",
      "AI资本开支开始更明显依赖债券和股权市场，现金流、杠杆和回报周期会成为估值核心。",
      "美国利率路径仍会决定AI和科技股反弹能否持续，尤其是在通胀仍高于目标的背景下。"
    ],
    items: [
      {
        title: "G7把AI放到峰会最后一天核心议程，欧洲要求降低对美国AI依赖",
        region: "G7、OpenAI、Google DeepMind、Anthropic、欧洲AI产业",
        sources: ["AP"],
        summary: "G7峰会最后一天安排全球AI部署与治理议题，OpenAI、Google DeepMind、Anthropic以及Mistral、Cohere、Synthesia等公司负责人参会。AP报道称，欧洲在美国前沿模型访问限制之后，更强调技术主权和本土AI基础设施。",
        why: "这说明AI不再只是企业竞争，而是进入盟友关系、产业政策和国家安全层面的基础设施议题。美国模型、云和芯片的可获得性，正在被欧洲当作战略依赖重新评估。",
        watch: "G7是否形成后续AI安全与主权投资机制，欧盟技术主权计划如何落地，以及美国是否放松或扩大前沿模型访问限制。"
      },
      {
        title: "英伟达启动约200亿美元债券融资，AI基建热潮继续推高科技公司杠杆",
        region: "英伟达、美国债券市场、AI数据中心",
        sources: ["Axios", "Investor's Business Daily"],
        summary: "Axios报道，英伟达启动约200亿美元公司债发行，加入大型科技公司通过资本市场支持AI基础设施扩张的行列。高盛估计，2026年超大云厂商资本开支可能达到7700亿美元，接近其经营现金流总额。",
        why: "AI建设正在从“现金流足够覆盖投资”的阶段，进入更多依赖债券、股权和资本市场再融资的阶段。投资者会更关注自由现金流、回购收缩和数据中心回报周期。",
        watch: "英伟达最终发债规模与利率、其他AI链公司是否跟进融资，以及评级机构是否开始更严格审视AI资本开支。"
      },
      {
        title: "SpaceX市值超过亚马逊，并以600亿美元收购Cursor背后的Anysphere",
        region: "SpaceX、Anysphere、Cursor、xAI、全球科技资本市场",
        sources: ["The Guardian", "Business Insider", "Times of India"],
        summary: "The Guardian报道，SpaceX上市后市值升至约2.66万亿美元，超过亚马逊成为全球第五大上市公司，并同意以约600亿美元全股票交易收购AI编程工具Cursor背后的Anysphere，以强化xAI在代码生成领域的能力。",
        why: "这是AI开发工具、商业航天、卫星网络和资本市场估值叙事的一次合流。高估值股票正在成为超级科技公司并购AI资产的“硬通货”。",
        watch: "交易是否按计划在三季度完成，Cursor能否接入更强算力并维持企业客户增长，以及SpaceX股价波动会否影响全股票交易吸引力。"
      },
      {
        title: "美股等待Warsh首次Fed会议，AI硬件股反弹但利率不确定性仍压着估值",
        region: "美国股市、Fed、AI硬件与半导体板块",
        sources: ["AP", "Barron's", "Business Insider"],
        summary: "AP报道，美股在Fed议息决定前窄幅波动，Jabil因AI基础设施需求强劲而上涨，Broadcom、Applied Materials等AI相关股票反弹；市场同时关注新任Fed主席Kevin Warsh首次发布会会否释放更鹰派信号。",
        why: "AI股票仍有很强的风险偏好弹性，但只要通胀和利率路径不清晰，高估值科技股就会对Fed沟通高度敏感。",
        watch: "Warsh是否维持利率不变、点阵图或前瞻指引是否调整，以及AI硬件股反弹能否扩散到软件和云服务。"
      },
      {
        title: "纽约国会初选变成AI监管代理战，OpenAI与Anthropic阵营资金正面交锋",
        region: "美国、纽约、OpenAI投资人、Anthropic阵营、AI监管",
        sources: ["AP"],
        summary: "AP报道，纽约第12选区民主党初选围绕AI监管立场出现高额政治支出。支持放松监管的科技资金投入超过700万美元反对曾推动纽约RAISE Act的Alex Bores，Anthropic相关阵营则投入超过1000万美元支持其竞选。",
        why: "AI公司和投资人正在把监管路线之争推进到地方和国会选举层面。未来AI安全、州级监管和联邦统一规则，可能越来越受政治资金影响。",
        watch: "6月23日初选结果、纽约RAISE Act命运，以及更多州议员是否因科技资金压力调整AI监管立场。"
      }
    ],
    sourceLinks: [
      "https://apnews.com/article/7d783c6de4356962e338b8b8563d48ea",
      "https://apnews.com/article/a7ab28d9b34edfaa2061a67616f610bc",
      "https://www.axios.com/2026/06/16/ai-nvidia-bonds-debt",
      "https://www.investors.com/news/technology/ai-data-centers-suppliers-nvidia-debt/",
      "https://www.theguardian.com/science/2026/jun/16/spacex-ai-coding-anysphere-cursor-amazon-market-valuation-xai",
      "https://www.businessinsider.com/spacex-cursor-spcx-stock-bill-ackman-elon-musk-ai-stocks-2026-6",
      "https://apnews.com/article/stocks-markets-rates-oil-us-iran-02e500f15edc505cedd8a8428197744c",
      "https://apnews.com/article/5753274efbf9c3839fafa78f14e19fdc"
    ]
  },
  {
    date: "2026-06-16",
    displayDate: "2026年6月16日",
    scope: "全球新闻｜科技与财经优先",
    image: "assets/morning-briefing-2026-06-16.png",
    summary: "本期只纳入3条，原因是6月16日可交叉核验、且与近7日不重复的高关注科技财经新增事件有限；排除了Anthropic访问限制后续、OpenAI渠道扩张延伸、AI融资/发债同一主线，以及中东停火与大盘反弹的跟进噪声。",
    focus: [
      "平台开始把公开用户内容直接转成AI搜索答案，分发权与数据使用边界正在重写。",
      "未成年人上网治理继续前移到平台入口层，年龄验证、推荐算法和产品增长模型会一起承压。",
      "媒体与流媒体竞争焦点继续从“谁有内容”转向“谁控制终端入口、广告数据和用户关系”。"
    ],
    items: [
      {
        title: "Meta把Facebook搜索改成AI问答入口，公开帖文开始直接供陌生人检索与生成答案",
        region: "美国、Meta、Facebook、Instagram、Threads",
        sources: ["The Verge", "Meta"],
        summary: "Meta 6月15日发布新的 Facebook AI 功能，其中搜索页新增“AI Mode”，可直接基于 Facebook、Instagram 和 Threads 上的公开内容生成答案，而不再只是返回链接列表。The Verge指出，这意味着用户过去面向关注者或熟人的公开帖文，正被重新放进面向陌生搜索者的AI回答场景里。",
        why: "这不是普通搜索改版，而是平台把社交内容库存直接接入AI分发层。谁能控制公开内容、默认入口和答案呈现方式，谁就更接近下一轮内容发现和广告定价权。",
        watch: "Meta是否补充更明确的引用与退出机制，创作者和普通用户会否对公开内容被AI二次利用提出反弹，以及欧盟等地区是否要求更强的信息来源披露。"
      },
      {
        title: "英国宣布将禁止16岁以下使用TikTok、YouTube和Instagram等平台，社交媒体监管再上一个台阶",
        region: "英国、TikTok、YouTube、Meta、Snap 等社交平台",
        sources: ["The Guardian", "The Verge"],
        summary: "英国政府宣布将推动新规，原则上禁止16岁以下青少年使用 TikTok、YouTube、Instagram、Facebook、X 和 Snapchat，并要求 Ofcom 制定更强的年龄验证方案；部分面向未成年人的直播、陌生人联系和暧昧型AI聊天功能也会被进一步收紧。",
        why: "这不只是儿童保护口号，而是会直接影响平台的未成年用户增长、推荐产品设计和实名/人脸验证成本。若英国先行落地，其他市场复制的概率会明显上升。",
        watch: "法案提交和生效时间表、年龄验证最终采用的人脸或证件方案、YouTube等平台的游说结果，以及欧盟和英联邦国家是否跟进类似门槛。"
      },
      {
        title: "Fox以220亿美元收购Roku，传统媒体开始直接争夺电视操作系统和广告入口",
        region: "美国、Fox、Roku、流媒体广告市场",
        sources: ["Axios", "Business Insider"],
        summary: "Fox 宣布以约220亿美元的现金加股票交易收购 Roku，交易对价约为每股160美元，预计在2027年上半年完成。Axios和Business Insider都指出，Fox希望把Tubi与Roku Channel、Roku电视操作系统和家庭广告数据能力整合，借此把自己从内容提供方进一步推向终端分发平台。",
        why: "对流媒体行业来说，最稀缺的已不只是片库，而是电视首页入口、广告库存和用户行为数据。Fox买下Roku，等于押注“平台控制权”比单纯内容版权更值钱。",
        watch: "监管审批是否顺利，Fox能否把 Tubi 与 Roku Channel 做出规模协同，以及广告主是否愿意为更完整的客厅流量闭环支付更高价格。"
      }
    ],
    sourceLinks: [
      "https://www.theverge.com/tech/950264/meta-ai-mode-search-facebook",
      "https://about.fb.com/news/",
      "https://www.theguardian.com/media/2026/jun/15/social-media-ban-uk-under-16-starmer",
      "https://www.theverge.com/policy/949679/uk-under-16-social-media-ban-announcement",
      "https://www.axios.com/2026/06/15/fox-roku-22-billion",
      "https://www.businessinsider.com/fox-acquire-roku-streaming-deal-2026-6"
    ]
  },
  {
    date: "2026-06-15",
    displayDate: "2026年6月15日",
    scope: "全球新闻｜科技与财经优先",
    image: "assets/morning-briefing-2026-06-15.png",
    summary: "本期只纳入3条，原因是周末到周一之间真正具备新增信息、可交叉核验且不与近几日重复的科技财经事件有限；排除了Apple欧盟落地后续、Anthropic模型访问限制延伸、AI基建资本开支同一主线，以及中东停火与油价的跟进噪声。",
    focus: [
      "反垄断和互操作监管正从浏览器、应用商店延伸到AI分发入口，平台控制权会更直接影响模型商业化。",
      "中国平台经济监管重心正在从单纯促消费转向限制低价内卷，电商利润率与商家生态可能被重新平衡。",
      "AI带来的电力需求开始改写汽车与电池公司的资本开支方向，储能和电网灵活性成为新的产业交叉点。"
    ],
    items: [
      {
        title: "欧盟要求Meta重新向竞争对手开放WhatsApp接口，AI分发入口首次被紧急反垄断措施直接约束",
        region: "欧盟、Meta、WhatsApp、AI聊天机器人平台",
        sources: ["AP"],
        summary: "欧盟委员会依据反垄断调查采取临时措施，要求Meta在五天内恢复竞争对手对WhatsApp Business API的接入，并在调查完成前持续维持。AP报道称，这是欧盟多年少见地动用紧急干预，目标直指Meta把WhatsApp流量入口优先留给自家Meta AI的做法。",
        why: "这意味着AI竞争不再只比模型能力，谁掌握消息入口、分发渠道和默认触点，也会被监管当作市场力量审查。对所有依赖超级App流量的AI公司来说，这都是定价权和获客成本的前瞻信号。",
        watch: "Meta是否上诉或调整接口政策，OpenAI等竞争对手能否真正恢复接入，以及欧盟会否把类似逻辑扩展到更多平台级AI入口。"
      },
      {
        title: "北京在618前警示平台“价格战内卷”，中国电商重新面对监管式利润约束",
        region: "中国、北京监管部门、阿里巴巴、京东、拼多多等电商平台",
        sources: ["SCMP"],
        summary: "在618大促进入冲刺阶段前，北京监管部门约谈主要电商平台，要求停止以极端低价、补贴对冲和算法引导制造恶性竞争。SCMP报道，此举反映出监管希望在刺激消费之外，压制平台与商家之间的价格战内卷，避免对中小商户和供应链利润造成持续挤压。",
        why: "这不是普通节日促销管理，而是中国平台经济政策从“做大GMV”向“稳商家、稳利润、稳秩序”微调的信号。若执行趋严，头部平台的补贴强度、佣金策略和广告变现都会受影响。",
        watch: "平台是否下调补贴和流量倾斜力度，品牌商与白牌商的成交结构是否变化，以及后续是否出现更明确的全国性治理口径。"
      },
      {
        title: "GM联手Peak Energy押注钠离子储能，AI数据中心电力缺口开始把车厂推向能源公司",
        region: "美国、GM、Peak Energy、数据中心与电网储能",
        sources: ["The Verge", "Car and Driver"],
        summary: "GM宣布与Peak Energy合作开发面向固定式储能系统的钠离子电池，并同步推进车网互动能力，核心目标是服务数据中心和电网在AI推动下上升的用电压力。The Verge与Car and Driver都指出，GM并非把钠离子首先用于电动车，而是优先放在更看重寿命、成本和热稳定性的储能场景。",
        why: "这说明AI基础设施的外溢效应已不只是芯片和服务器，连汽车厂商的电池路线和资本配置都在被改写。谁能把车、电池、储能和电网联成一体，谁就可能拿到AI时代新的能源收益。",
        watch: "GM与Peak的量产时间表、钠离子相对LFP的成本曲线，以及更多车厂和公用事业公司是否跟进固定式储能合作。"
      }
    ],
    sourceLinks: [
      "https://apnews.com/article/meta-whatsapp-european-union-antitrust-ai-2f25b0be4c7d6f0734ef1304e8221cbc",
      "https://www.msn.com/en-xl/news/other/as-618-shopping-frenzy-grows-beijing-warns-e-commerce-giants-over-price-war-tactics/ar-AA25nlDB?ocid=BingNewsVerp",
      "https://www.theverge.com/transportation/946820/gm-energy-ev-v2g-storage-sodium-ion",
      "https://www.caranddriver.com/news/a71538744/gm-sodium-ion-battery-cells-plans/"
    ]
  },
  {
    date: "2026-06-14",
    displayDate: "2026年6月14日",
    scope: "全球新闻｜科技与财经优先",
    image: "assets/morning-briefing-2026-06-14.png",
    summary: "本期只纳入4条，原因是周末高关注、可交叉核验且不与近三日重复的科技财经新进展有限；排除了SpaceX IPO后续、Oracle/OpenAI云采购、AI资本市场同一轮估值讨论和中国算力旧主线。",
    focus: [
      "AI监管正在从芯片出口管制外溢到模型访问权限，跨境服务和国际化团队都会受影响。",
      "大模型竞争正从参数和跑分转向企业级执行环境、采购路径与长期运行代理的基础设施。",
      "平台级AI助手与地缘政治仍是市场外部变量，既会影响产品落地，也会影响油价、通胀和风险偏好。"
    ],
    items: [
      {
        title: "美国限制外国人访问Anthropic新模型，前沿AI开始出现“模型出口管制”",
        region: "美国监管、Anthropic、全球AI服务市场",
        sources: ["AP", "MarketWatch"],
        summary: "Anthropic表示，为遵守美国针对外国人访问限制的新指令，已下线最新的Fable 5和Mythos 5模型；限制对象不仅包括海外客户，也波及在美外国员工。MarketWatch认为，这标志着美国AI管制正在从芯片出口进一步推进到模型本身的跨境可得性。",
        why: "这不是单一公司事故，而是AI监管边界的一次上移。如果前沿模型被按国家安全资产管理，全球企业采购、海外研发协作和美国AI公司的国际化增长都会被重估。",
        watch: "限制是否扩展到更多模型提供商，许可机制是否明确，以及海外企业是否加速转向本土或开源替代。"
      },
      {
        title: "OpenAI拟收购Ona，把Codex推向可持续数小时到数天的企业代理工作流",
        region: "OpenAI、Ona、企业级AI代理基础设施",
        sources: ["OpenAI"],
        summary: "OpenAI 6月11日宣布拟收购云端执行与编排公司Ona，称其将把安全、客户可控的持久化云执行能力接入Codex。OpenAI同时披露，Codex周活已超过500万人，较年初增长400%，并强调未来最有价值的代理工作将持续数小时甚至数天。",
        why: "这说明大模型竞争焦点正在从“会不会回答”转到“能不能长期稳定地替企业干活”。持久化执行环境、权限边界和日志治理，正在成为企业级代理落地的核心护城河。",
        watch: "交易审批进度、OpenAI何时把Ona能力产品化，以及企业是否愿意把更多生产流程交给长时运行代理。"
      },
      {
        title: "Apple推出Siri AI，但欧盟iPhone与iPad首发缺席，平台级AI助手先撞上监管边界",
        region: "Apple、欧盟、移动操作系统与AI助手",
        sources: ["The Verge"],
        summary: "Apple在WWDC 2026推出新版Siri AI，并将其作为Apple Intelligence核心入口，但The Verge报道，因与欧盟《数字市场法》互操作要求存在冲突，iPhone和iPad版Siri AI初期不会在欧盟上线。争议焦点在于，Apple认为DMA要求向外部系统开放过深访问权限，可能损害隐私与安全。",
        why: "苹果一旦把AI助手推到系统级入口，监管不再只是抽象风险，而是会直接决定哪些市场能否首发、哪些能力能否开放。这会影响开发者生态、设备换机周期和平台议价权。",
        watch: "Apple与欧盟委员会能否形成折中方案，Mac或Vision设备是否先行放量，以及Siri AI的开发者测试反馈能否改善市场预期。"
      },
      {
        title: "美伊接近签署停火框架，霍尔木兹重开预期成为周末市场新变量",
        region: "美国、伊朗、中东航运与全球能源市场",
        sources: ["AP", "The Guardian"],
        summary: "AP和The Guardian均报道，美伊接近通过电子方式签署结束冲突的框架协议，核心内容包括启动新的核谈判周期并推动霍尔木兹海峡重新开放。不过伊朗方面仍提示协议未最终落定，实际执行与停火范围仍有不确定性。",
        why: "这与6月11日的“冲突升级推高油价”已经不是同一阶段，而是影响油价、航运保险、通胀预期和全球风险偏好的实质性新进展。若海峡真正恢复通航，过去数周的能源风险溢价会被重新定价。",
        watch: "协议是否如期签署、油轮和保险商是否恢复实际通行，以及美国与伊朗在制裁、核设施和黎巴嫩问题上的执行分歧。"
      }
    ],
    sourceLinks: [
      "https://apnews.com/article/d9cc7df5c02e93837d0f0bfb24d5cfd2",
      "https://www.marketwatch.com/story/u-s-restrictions-on-new-anthropic-models-could-trigger-a-global-ai-arms-race-7752afb4",
      "https://openai.com/index/openai-to-acquire-ona/",
      "https://www.theverge.com/tech/942416/apple-siri-ai-update-wwdc",
      "https://www.theverge.com/ai-artificial-intelligence/947051/apple-europe-dma-siri-ai",
      "https://apnews.com/article/949710df39e3f1033cbb6beda3955814",
      "https://www.theguardian.com/world/2026/jun/13/preliminary-peace-deal-could-be-signed-within-days-says-us-iran-and-mediators"
    ]
  },
  {
    date: "2026-06-13",
    displayDate: "2026年6月13日",
    scope: "全球新闻｜科技与财经优先",
    image: "assets/morning-briefing-2026-06-13.png",
    summary: "本期只纳入3条，原因是周末高关注、可核验且不与前两日重复的科技财经新闻有限；重点转向AI资本市场集中度、Adobe软件估值压力和中国AI芯片/基础设施投入。",
    focus: [
      "AI不再只是产品叙事，正在重塑股权、债券和指数配置逻辑。",
      "软件公司承压、芯片与AI基础设施受追捧，科技板块内部正在重新定价。",
      "中国AI投资继续向芯片、算力和基础模型倾斜，国产供应链能力是后续关键。"
    ],
    items: [
      {
        title: "AI投资热潮正在改写股票与债券市场结构",
        region: "全球资本市场、美国科技巨头、AI基础设施",
        sources: ["FT", "WSJ"],
        summary: "FT今日分析称，AI已从行业主题变成资产配置核心变量，大型科技公司加大数据中心和AI资本开支，股权融资、债券发行和指数权重都受到牵引。WSJ同日市场综述也提到，美国科技公司，尤其是Amazon和Alphabet，正积极发行欧元债券，互联网板块成为新发行的重要力量。",
        why: "这说明AI交易已不只是个股行情，而是在改变资金流向、企业融资方式和被动指数投资的风险集中度。",
        watch: "大型科技公司自由现金流、债务融资成本、AI相关IPO供给，以及被动基金对AI权重集中的承受能力。"
      },
      {
        title: "Adobe股价跌至多年低位，CFO转投Marvell凸显软件与芯片分化",
        region: "Adobe、Marvell、软件与半导体板块",
        sources: ["Barron's", "MarketWatch", "Investopedia"],
        summary: "Adobe公布强于预期的季度业绩并上调全年展望，但市场更关注其AI竞争压力、freemium策略和高管流失。CFO Dan Durn将离职加入Marvell，Adobe股价跌至多年低位，而Marvell等AI芯片链公司获得更高估值溢价。",
        why: "这是AI时代科技板块内部轮动的缩影：投资者愿意为算力、芯片和网络基础设施付溢价，却对传统软件公司的定价权更谨慎。",
        watch: "Adobe能否证明AI功能带来付费转化，软件板块是否继续被芯片链挤压估值。"
      },
      {
        title: "百度继续押注AI与芯片，昆仑芯上市预期强化中国算力主线",
        region: "百度、昆仑芯、中国AI基础设施",
        sources: ["WSJ", "Tom's Hardware"],
        summary: "WSJ报道，百度预计未来几个季度收入增长将由AI和芯片业务推动，并计划推进昆仑芯在香港上市，后续也筹备科创板路径。与此同时，中国正在推进大规模AI数据中心和国产芯片替代计划，但本土先进芯片产能与HBM供应仍是约束。",
        why: "中国AI竞争正从模型发布转向算力、芯片和数据中心体系建设，百度等平台公司的AI投入会直接影响国产AI供应链估值。",
        watch: "昆仑芯上市进度、国产AI芯片供给、百度AI云收入，以及政策资金是否推动算力扩张过快。"
      }
    ],
    sourceLinks: [
      "https://www.ft.com/content/b9273a66-f05d-4b28-bf34-be8ab93b89d1",
      "https://www.ft.com/content/b31f1e09-5aae-4cad-af15-97adb15dba70",
      "https://www.wsj.com/tech/tech-media-telecom-roundup-market-talk-f7d28098",
      "https://www.barrons.com/articles/adobe-earnings-stock-price-f259c4e5",
      "https://www.marketwatch.com/story/adobes-cfo-is-departing-for-marvell-and-its-one-more-reason-for-investors-to-choose-chips-over-software-336b9e16",
      "https://www.investopedia.com/why-adobe-stock-just-hit-its-lowest-point-in-8-years-adbe-11996518",
      "https://www.wsj.com/tech/baidu-sees-healthy-ai-driven-revenue-growth-in-next-few-quarters-217fe57a",
      "https://www.tomshardware.com/tech-industry/china-drafts-295-billion-plan-to-build-a-national-ai-data-center-grid-running-on-80-percent-domestic-chips"
    ]
  },
  {
    date: "2026-06-12",
    displayDate: "2026年6月12日",
    scope: "全球新闻｜科技与财经优先",
    image: "assets/morning-briefing-2026-06-12.png",
    summary: "今日不延续昨日油价、Oracle和比亚迪主线，改选可核验且与前一日不同的科技与财经事件：关税、商业航天IPO、AI就业影响、AI广告监管和AI支付代理。",
    focus: [
      "美国关税政策仍处司法拉锯期，进口成本和企业供应链安排继续承压。",
      "AI议题从模型能力扩展到就业冲击、广告合规和支付场景落地。",
      "商业航天与AI叙事结合，SpaceX IPO预期成为资本市场的新估值锚点。"
    ],
    items: [
      {
        title: "美国上诉法院允许政府暂时继续征收10%关税",
        region: "美国、全球贸易、进口企业",
        sources: ["AP"],
        summary: "美国上诉法院裁定，在诉讼继续期间，政府可暂时维持10%基准关税征收。",
        why: "关税不确定性会直接影响企业采购、零售价格、利润率和跨境供应链重新定价。",
        watch: "后续判决是否限制总统关税权限，企业是否提前囤货或转移供应链。"
      },
      {
        title: "SpaceX IPO数字曝光，商业航天估值进入新阶段",
        region: "SpaceX、资本市场、商业航天",
        sources: ["AP"],
        summary: "AP梳理了SpaceX拟上市相关关键数字，市场开始把商业航天、卫星互联网和AI基础设施叙事放在同一张估值表里观察。",
        why: "SpaceX若上市，可能成为继大型AI公司之后又一个重塑科技资本市场权重的超级标的。",
        watch: "IPO时间表、Starlink现金流、发射业务利润率以及监管对估值的影响。"
      },
      {
        title: "Anthropic投入2亿美元研究AI对就业和经济的冲击",
        region: "Anthropic、AI产业、劳动力市场",
        sources: ["AP"],
        summary: "Anthropic宣布设立初始2亿美元资金，用于研究AI对就业、收入和公共政策的影响，其CEO同时提出失业缓冲和基本收入等政策讨论。",
        why: "AI竞争正在从产品能力扩展到社会分配、就业替代和监管责任，这是科技公司估值之外的新压力。",
        watch: "研究资金如何落地、政府是否采纳就业监测机制、AI公司是否承担更多公共责任。"
      },
      {
        title: "纽约AI广告标识法生效，合成演员必须明示",
        region: "纽约、广告行业、生成式AI监管",
        sources: ["AP"],
        summary: "纽约新规要求广告中使用AI生成的“合成表演者”时必须明确标识，进一步把AI内容合规推向商业传播场景。",
        why: "这会影响广告制作、艺人权益、品牌风险控制，也可能成为其他地区AI内容标识规则的样板。",
        watch: "品牌和广告代理商的披露方式、违规处罚案例、其他州或国家是否跟进。"
      },
      {
        title: "Visa把支付网络接入ChatGPT，AI代理可替用户购物付款",
        region: "Visa、OpenAI、金融科技",
        sources: ["AP"],
        summary: "Visa宣布将支付网络接入ChatGPT，使AI代理能够在用户授权下完成购物和付款动作。",
        why: "这把AI从问答工具推进到交易执行层，支付安全、身份验证和责任归属都会成为金融科技新焦点。",
        watch: "用户授权机制、欺诈风控、商户接入规模，以及监管对AI代理支付的态度。"
      }
    ],
    sourceLinks: [
      "https://apnews.com/article/trump-tariffs-court-lawsuit-a95ef7309d89018477a3265ebf93d620",
      "https://apnews.com/article/spacex-ipo-musk-trillionaire-investors-mars-moon-c0ba803b4e98382de2099cc92e547825",
      "https://apnews.com/article/anthropic-dario-amodei-ai-afeb5279eef406980dffa46ff91495e0",
      "https://apnews.com/article/new-york-ai-law-hochul-synthetic-performers-e433625bfb61c8abeab0d619869192ed",
      "https://apnews.com/article/visa-chatgpt-tecnologia-ventas-compras-internet-inteligencia-artificial-852a4c9451c72bfddedf775adf12e85b"
    ]
  },
  {
    date: "2026-06-11",
    displayDate: "2026年6月11日",
    scope: "全球新闻｜科技与财经优先",
    image: "assets/morning-briefing-2026-06-11.png",
    summary: "今日主线是中东冲突推升油价与通胀压力，叠加AI交易降温、AI基建开支审查和中国新能源车出海加速。",
    focus: [
      "油价是否继续冲向100美元，将决定通胀和市场情绪。",
      "AI交易正在从“增长叙事”切换到“现金流和融资压力”审查。",
      "全球科技竞争焦点继续集中在AI基础设施、电动车补能网络和资本市场融资能力。"
    ],
    items: [
      {
        title: "美伊冲突升级，油价与全球市场再受冲击",
        region: "美国、伊朗、中东能源市场",
        sources: ["AP", "Economic Times"],
        summary: "美国对伊朗发动第二轮打击，伊朗反击并波及海湾地区目标；油价因霍尔木兹海峡风险上升而跳涨。",
        why: "这是今天全球市场的第一变量，直接影响能源、通胀、航运和风险资产。",
        watch: "霍尔木兹通行情况、美伊是否重回谈判、亚洲能源进口国的应对。"
      },
      {
        title: "美国5月通胀升至4.2%，美联储压力加大",
        region: "美国、Fed、全球债券和股票市场",
        sources: ["WSJ", "The Guardian"],
        summary: "美国5月CPI同比升至4.2%，能源价格是主要推手，核心通胀约2.9%。",
        why: "高油价正在重新把“通胀-加息”风险推回市场中心。",
        watch: "Fed是否维持利率不动，还是释放更鹰派信号；美债收益率和美元反应。"
      },
      {
        title: "AI股票继续降温，亚洲市场跟随承压",
        region: "美股、亚洲股市、AI和半导体板块",
        sources: ["AP", "Barron's"],
        summary: "美股科技和AI板块再度下跌，纳指跌约2%，半导体相关ETF明显回调；亚洲市场跟随走弱。",
        why: "市场开始重新审视AI估值和资本开支回报，不只是短线获利了结。",
        watch: "英伟达、博通、Micron、台积电、SK海力士等AI链核心资产能否稳住。"
      },
      {
        title: "Oracle云业务强劲，但AI基建开支吓退投资者",
        region: "Oracle、云计算、AI数据中心",
        sources: ["WSJ", "MarketWatch"],
        summary: "Oracle季度收入和利润好于预期，云基础设施收入大增，但市场担心AI数据中心资本开支过高，盘后股价下跌。",
        why: "这是“AI需求很真，但烧钱也很真”的典型案例。",
        watch: "AI云订单能否转化为现金流，资本开支是否继续压低自由现金流。"
      },
      {
        title: "BYD加速欧洲扩张，目标五年内挑战全球最大车企",
        region: "BYD、欧洲新能源车市场、Toyota、Tesla",
        sources: ["The Guardian", "FT"],
        summary: "BYD提出五年内成为全球最大车企的目标，并计划在欧洲投入约20亿欧元建设“5分钟快充”网络。",
        why: "中国新能源车企正在从“卖车”转向“车+电池+补能网络”的系统竞争。",
        watch: "欧盟关税、欧洲本地建厂进度、快充网络能否真正缓解用户补能焦虑。"
      }
    ],
    sourceLinks: [
      "https://apnews.com/article/3c2c6d356a1e25b4d7edf66b2edba57d",
      "https://m.economictimes.com/markets/commodities/news/oil-rises-2-as-iran-announces-closure-of-strait-of-hormuz-following-us-strikes/articleshow/131646731.cms",
      "https://www.theguardian.com/business/live/2026/jun/10/asian-stocks-fall-us-iran-exchange-fire-middle-east-strait-of-hormuz-oil-prices-latest-news-updates",
      "https://apnews.com/article/87c831451197beedb3e29771de1e0a92",
      "https://www.marketwatch.com/story/oracles-stock-slides-after-earnings-as-the-steep-price-of-ai-spooks-investors-0653b309",
      "https://www.theguardian.com/business/2026/jun/10/china-byd-car-firm-ev-maker-toyota"
    ]
  }
];
