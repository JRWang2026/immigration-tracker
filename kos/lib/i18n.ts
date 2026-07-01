export type Lang = "zh" | "en";

export interface Translation {
  nav: {
    home: string;
    patent: string;
    code: string;
    threeD: string;
    research: string;
    intelligence: string;
    knowledge: string;
    draw: string;
    language: string;
  };
  hero: {
    greeting: string;
    title: string;
    subtitle: string;
    tagline: string;
    cta: string;
  };
  profile: {
    title: string;
    bio: string;
    timeline: {
      period: string;
      title: string;
      degree: string;
      badges: string[];
      note?: string;
    }[];
    languages: { language: string; level: string }[];
    identity: { email: string; orcid: string; orcidUrl: string; labelEmail: string; labelOrcid: string; title: string };
  };
  patent: {
    title: string;
    items: { text: string; anchor: string }[];
  };
  research: {
    title: string;
    direction1: { title: string; desc: string };
    direction2: { title: string; desc: string };
    direction3: { title: string; desc: string };
  };
  projects: {
    title: string;
    project1: { title: string; desc: string };
    project2: { title: string; desc: string };
    project3: { title: string; desc: string };
    project4: { title: string; desc: string };
  };
  codeLab: {
    title: string;
    subtitle: string;
    run: string;
    running: string;
    output: string;
    loading: string;
    ready: string;
    demos: { label: string; name: string }[];
    custom: string;
    uploadPy: string;
    clearOutput: string;
    codePlaceholder: string;
  };
  certGallery: {
    view: string;
    close: string;
    of: string;
  };
  cnkiAnalysis: {
    title: string;
    subtitle: string;
    badge: string;
    methodTitle: string;
    methodDesc: string;
  };
  footer: {
    copyright: string;
    built: string;
    github: string;
  };
  researchPage: {
    title: string;
    subtitle: string;
    abstract: string;
    sections: {
      id: string;
      title: string;
      content: string;
    }[];
  };
  patentPage: {
    totalPatents: string;
    totalInventors: string;
    collaborations: string;
    techAreas: string;
    wordCloud: string;
    techDist: string;
    patentType: string;
    yearTrend: string;
    networkTitle: string;
    patentList: string;
    loading: string;
    error: string;
    title: string;
    inventors: string;
    type: string;
    year: string;
    pubno: string;
    certs: string;
    certView: string;
    certClose: string;
    certOf: string;
    inventionPatents: string;
    utilityModels: string;
    invention: string;
    utility: string;
    manageCerts: string;
    manageUnlock: string;
    managePassword: string;
    manageEnter: string;
    manageWrongPassword: string;
    manageUpload: string;
    manageLabel: string;
    manageReset: string;
    manageSave: string;
    manageDone: string;
    manageTitle: string;
    manageHelp: string;
    manageDrag: string;
    manageRemove: string;
  };
  workingPapers: {
    title: string;
    subtitle: string;
    statusLabel: {
      concept: string;
      drafting: string;
      submitted: string;
      published: string;
    };
    papers: {
      id: string;
      title: string;
      desc: string;
      status: "concept" | "drafting" | "submitted" | "published";
      target: string;
    }[];
  };
}

const zh: Translation = {
  nav: {
    home: "首页",
    patent: "专利分析",
    code: "代码实验室",
    threeD: "3D展示",
    research: "研究",
    intelligence: "情报台",
    knowledge: "知识图谱",
    draw: "绘图",
    language: "EN",
  },
  hero: {
    greeting: "王吉锐",
    title: "竞争情报与制造业数字化转型",
    subtitle:
      "ISTIC 信息资源管理硕士在读 · 中国石油大学工学学士",
    tagline: "AI 工具协同：Codex + WorkBuddy · Python 数据挖掘 · 专利分析",
    cta: "了解更多",
  },
  profile: {
    title: "个人简介",
    bio: "从汽车技术到机械制造，再到信息资源管理——三个专业的跨越。2005-2021 年从事电缆行业质量检验与技术工作，2021 年至今负责党务与 HSE 体系综合管理（胜利油田胜利泵业有限责任公司）。目前聚焦于制造业数字化转型中的竞争情报分析，运用 Python 数据挖掘技术从专利文本中提取技术竞争态势。目标是将工程实践转化为学术研究，为智能制造中的知识管理提供方法论支撑。",
    timeline: [
      {
        period: "2000 — 2003",
        title: "石油大学（华东）",
        degree: "专科 · 汽车技术专业",
        badges: ["CET-4", "三好学生", "制图员资格证（中级）", "汽车修理证（中级）"],
      },
      {
        period: "2003 — 2005",
        title: "中国石油大学（华东）机电工程学院",
        degree: "工学学士 · 机械设计制造及其自动化",
        badges: ["CET-6"],
      },
      {
        period: "2005 — 至今",
        title: "胜利油田胜利泵业有限责任公司",
        degree: "质量检验/技术管理 (2005-2021) · 党务与HSE体系综合管理 (2021-至今)",
        badges: ["质量工程师（中级）", "HSE 内审员", "MES", "质量追溯", "电缆生产", "HSE 管理"],
        note: "三体系内审员（ISO 9001 质量 / 14001 环境 / 45001 职业健康安全）",
      },
      {
        period: "2025 — 至今",
        title: "中国科学技术信息研究所",
        degree: "硕士在读（在职攻读）· 信息资源管理（均分 86+）",
        badges: [
          "Python", "数据挖掘", "专利分析",
          "竞争情报", "D3.js", "Next.js", "知识组织",
        ],
        note: "在职攻读，与 SLP 全职工作并行",
      },
    ],
    languages: [
      { language: "中文", level: "母语" },
      { language: "English", level: "CET-6 · 雅思备考中" },
    ],
    identity: {
      title: "学术身份",
      labelEmail: "学术邮箱",
      labelOrcid: "ORCID",
      email: "WJR2026@hotmail.com",
      orcid: "0009-0006-0528-3961",
      orcidUrl: "https://orcid.org/0009-0006-0528-3961",
    },
  },
  patent: {
    title: "专利成果快照",
    items: [
      { text: "我的 5 项专利全景分析", anchor: "stats" },
      { text: "技术词云：数据采集、追溯系统、智能制造", anchor: "wordcloud" },
      { text: "发明人合作网络可视化", anchor: "network" },
    ],
  },
  research: {
    title: "研究方向",
    direction1: {
      title: "企业技术竞争情报",
      desc: "基于专利文本挖掘的企业技术竞争情报分析方法研究，结合 Python 数据处理与可视化。",
    },
    direction2: {
      title: "制造执行系统 (MES)",
      desc: "面向特种电缆制造过程的数据采集与质量追溯系统架构设计。",
    },
    direction3: {
      title: "知识组织系统 (KOS)",
      desc: "AI 驱动的知识组织方法，构建制造领域知识图谱，探索语义检索技术。",
    },
  },
  projects: {
    title: "项目展示",
    project1: {
      title: "制造企业专利竞争态势分析",
      desc: "基于万方数据的企业专利文本挖掘，包含词云、合作网络、技术趋势可视化，为竞争情报分析提供方法论支撑。",
    },
    project2: {
      title: "Python 数据分析平台",
      desc: "基于 Python 开发的企业数据统计分析与可视化工具，支持多源数据接入、自动计算与报表生成，为管理决策提供数据支撑。",
    },
    project3: {
      title: "潜油特种电缆数据追溯",
      desc: "面向连续硫化生产线的数据采集与质量追溯系统原型，探索制造过程数字化转型。",
    },
    project4: {
      title: "Troester 连续硫化生产线调试",
      desc: "参与德国 Troester 公司连续硫化生产线安装调试，与德方工程师协作完成设备验收。具备国际化项目协作经验。",
    },
  },
  codeLab: {
    title: "代码实验室",
    subtitle: "浏览器内运行 Python — 查看我的数据分析工作流，无需安装任何软件",
    run: "运行",
    running: "执行中…",
    output: "输出",
    loading: "正在加载 Python 运行环境…",
    ready: "环境就绪，点击「运行」执行代码",
    demos: [
      { label: "API数据获取与JSON处理", name: "api_fetch.py" },
      { label: "专利文本挖掘", name: "patent_mining.py" },
    ],
    custom: "自定义",
    uploadPy: "上传 .py 文件",
    clearOutput: "清空",
    codePlaceholder: "# 在此输入或粘贴 Python 代码\n# 支持标准库 (statistics, collections, json, math, re...)\n# 也支持 print() 输出\n\nprint(\"Hello, KOS!\")",
  },
  certGallery: {
    view: "查看大图",
    close: "关闭",
    of: "/",
  },
  cnkiAnalysis: {
    title: "CNKI 文献计量分析",
    subtitle:
      "基于中国知网（CNKI）数据库的潜油电泵领域文献计量研究，展示文献检索、数据清洗、关键词提取与可视化分析的系统方法论。此项工作为 ISTIC 信息资源管理硕士课程作业，体现信息组织与计量分析的核心能力。",
    badge: "文献计量 · Bibliometrics",
    methodTitle: "方法论说明",
    methodDesc:
      "数据来源：CNKI 学术期刊库（检索日期：2026年1月31日）。采用文献计量学方法，对 197 篇目标文献进行年度分布、类型构成、关键词频次统计，使用 Python (jieba + wordcloud + matplotlib) 完成数据处理与可视化。本页面展示 3 项核心分析：年度发文趋势、文献类型分布、TOP15 高频关键词。",
  },
  footer: {
    copyright: "© 2026 KOS — Knowledge Operating System",
    built: "Built with Next.js · Deployed on CloudStudio",
    github: "GitHub",
  },
  researchPage: {
    title: "Research Proposal",
    subtitle: "面向德国博士申请的预研究报告 —— 制造业数字化转型中的竞争情报系统",
    abstract: "本研究计划提出一个面向制造业数字化转型的竞争情报系统（Competitive Intelligence System, CIS）框架。传统竞争情报方法依赖人工文献检索与静态报告，难以应对全球供应链重构与产业政策快速演进的双重压力。本研究旨在利用专利文本挖掘、组织知识图谱与 Python 数据分析技术，构建一个半自动化的技术竞争态势感知系统，为特种电缆等行业的中型制造企业提供可操作的情报决策支持。该研究位于信息科学、制造工程与战略管理的交叉领域，目标申请方向为 TU München、RWTH Aachen、TU Berlin 或 Universität Stuttgart 的博士项目。",
    sections: [
      {
        id: "background",
        title: "1. 研究背景与动机",
        content: "制造业正处于第四次工业革命（Industrie 4.0）的核心转型期。全球供应链的区域化重组、技术脱钩风险的加剧，以及各国产业政策的战略性回归，使得技术竞争情报（Competitive Technical Intelligence, CTI）从可选工具演变为企业生存的必需品。\n\n然而，传统 CTI 实践面临三重瓶颈：（1）数据源孤岛化——专利数据库、学术文献、行业报告、企业公告彼此割裂；（2）分析手段滞后——以人工阅读与 Excel 统计为主，难以应对海量非结构化文本；（3）方法论缺位——缺乏将自然语言处理（NLP）技术系统化整合到制造企业情报工作流中的理论框架。\n\n本研究以中国特种电缆制造企业为场景，该行业具有典型的中型制造特征：对德国设备（如 Troester 连续硫化生产线）高度依赖、专利竞争国际化、数字化转型需求迫切但情报能力薄弱。研究者的二十年行业经验（2005—2021 质量与技术管理，2021 至今 HSE 体系与党务综合管理）为深度理解企业情报需求提供了独特视角。"
      },
      {
        id: "problem",
        title: "2. 研究问题",
        content: "本研究围绕一个核心问题展开：如何设计和评估一个数据驱动的竞争情报系统，使其能够从专利文献中自动提取技术竞争态势，并服务于中型制造企业的战略决策？\n\n该核心问题分解为三个子问题：\n\nRQ1（情报获取）：如何从中文专利数据库中高效采集、清洗和结构化多维度技术情报数据（技术分类、发明人网络、权利要求演变、地理分布）？\n\nRQ2（情报分析）：哪些自然语言处理与网络分析方法能够从专利文本中提取有意义的技术竞争信号（新兴技术主题识别、竞争对手技术路线追踪、技术空白区域发现）？\n\nRQ3（情报呈现）：如何将分析结果以可行动的知识表示形式（交互式知识图谱、自动情报简报）传递给非技术背景的企业决策者？"
      },
      {
        id: "literature",
        title: "3. 文献综述与研究空白",
        content: "技术竞争情报的研究可追溯至 Porter (1980) 的竞争战略框架，其后经 Ashton & Klavans (1997)、Lichtenthaler (2003) 等人的发展，逐步形成以专利分析为核心的方法体系。近年来，随着 NLP 技术的突破，基于 Transformer 架构的专利文本挖掘（如 Lee et al., 2020; Arts et al., 2021）显著提升了技术主题识别的精度。\n\n然而，现有文献存在三个显著空白：\n\n空白 1：多数研究聚焦于技术密集型大型企业（制药、半导体），对中型制造企业的适用性缺乏验证。中型企业的专利数量少、技术领域集中、分析资源有限，需要不同的方法论设计。\n\n空白 2：专利分析与组织知识管理脱节。现有研究将专利视为独立数据源，忽视了它与企业内部知识（工艺文档、设备参数、质量问题记录）的关联价值。\n\n空白 3：缺乏面向行动的情报呈现研究。大量工作停留在可视化展示层面，未探讨如何将分析结果转化为企业管理者的决策输入。\n\n本研究通过将专利分析嵌入企业知识组织系统（KOS）框架，并设计面向决策者的情报呈现界面，填补上述空白。"
      },
      {
        id: "methodology",
        title: "4. 研究方法",
        content: "本研究采用设计科学（Design Science Research）方法论，分四个阶段推进：\n\n阶段一：数据基础设施构建\n- 数据源：中国国家知识产权局（CNIPA）专利数据库、万方数据、CNKI 学术期刊\n- 技术栈：Python（AKShare / requests 数据采集 + pandas / jieba 数据处理 + scikit-learn / networkx 分析）\n- 数据管道设计：半自动化 ETL 流程，支持增量更新与数据版本管理\n\n阶段二：竞争情报分析引擎开发\n- 专利文本预处理：分词（jieba）、去停用词、TF-IDF 向量化\n- 技术主题建模：LDA 主题模型 + BERTopic 对比验证\n- 发明人合作网络：基于 networkx 的中心性分析与社区检测\n- 技术路线追踪：时间序列上的技术主题演变分析\n\n阶段三：情报呈现界面设计\n- 交互式知识图谱：D3.js 力导向图展示技术—发明人—专利三元关系\n- 自动情报简报生成：基于模板的 NLP 摘要生成\n- 决策仪表盘：关键竞争指标（KCI）实时监控\n\n阶段四：实证验证\n- 案例研究：以潜油特种电缆行业为场景，验证系统的情报价值\n- 专家评估：邀请企业技术管理人员与竞争情报学者进行效用评估\n- 可复现性：所有代码与数据集通过 KOS CodeLab（Pyodide WASM）开源发布"
      },
      {
        id: "significance",
        title: "5. 预期贡献与意义",
        content: "理论贡献：\n1. 提出「嵌入型竞争情报系统」（Embedded CIS）概念，将专利分析锚定在企业知识组织框架中，填补 CTI 与知识管理之间的理论空白。\n2. 为中型制造企业场景定制 NLP 方法论，验证轻量级文本挖掘技术在该场景下的适用边界。\n\n实践贡献：\n1. 开发一套开源、可复现的竞争情报分析工具链，降低中型企业的 CTI 应用门槛。\n2. 通过 KOS 平台提供交互式情报展示界面，为产学研合作提供展示与交流载体。\n\n学术路径规划：\n- 短期（2026—2027）：完成中文 CSSCI 论文（《情报理论与实践》），确立国内学术地位\n- 中期（2027—2028）：将方法论扩展至国际语境，投稿 SSCI 期刊（Online Information Review）\n- 长期（博士阶段）：在德国导师指导下深化理论框架，将研究场景从中国制造扩展至中德制造比较研究"
      },
      {
        id: "references",
        title: "6. 核心参考文献",
        content: "Ashton, W. B., & Klavans, R. A. (1997). Keeping abreast of science and technology. Battelle Press.\n\nArts, S., Hou, J., & Gomez, J. C. (2021). Natural language processing to identify the creation and impact of new technologies in patent text. Research Policy, 50(2), 104144.\n\nLee, C., Jeon, D., Ahn, J., & Kwon, O. (2020). A deep learning-based approach for patent landscaping. Technological Forecasting and Social Change, 155, 119968.\n\nLichtenthaler, E. (2003). Third generation management of technology intelligence processes. R&D Management, 33(4), 361–375.\n\nPorter, M. E. (1980). Competitive strategy. Free Press.\n\nYoon, B., & Park, Y. (2004). A text-mining-based patent network. Technovation, 24(11), 897–906."
      }
    ],
  },
  patentPage: {
    totalPatents: "有效专利",
    totalInventors: "发明人",
    collaborations: "合作关系",
    techAreas: "技术领域",
    wordCloud: "技术关键词云",
    techDist: "技术领域分布",
    patentType: "专利类型统计",
    yearTrend: "年度申请趋势",
    networkTitle: "发明人合作网络",
    patentList: "专利明细列表",
    loading: "正在加载数据...",
    error: "数据加载失败，请刷新重试",
    title: "专利名称",
    inventors: "发明人",
    type: "类型",
    year: "年份",
    pubno: "公开号",
    certs: "专利证书",
    certView: "查看大图",
    certClose: "关闭",
    certOf: "/",
    inventionPatents: "发明专利 Invention Patents",
    utilityModels: "实用新型 Utility Models",
    invention: "发明",
    utility: "实用新型",
    manageCerts: "管理证书",
    manageUnlock: "点击解锁管理面板",
    managePassword: "请输入管理密码",
    manageEnter: "进入",
    manageWrongPassword: "密码错误，请重试",
    manageUpload: "点击上传证书图片",
    manageLabel: "标签类型",
    manageReset: "恢复默认",
    manageSave: "保存设置",
    manageDone: "退出管理",
    manageTitle: "证书管理面板",
    manageHelp: "点击图片区域上传新图片 · 选择标签类型 · 点击保存生效",
    manageDrag: "拖拽调整顺序",
    manageRemove: "清除此证书",
  },
  workingPapers: {
    title: "工作论文",
    subtitle: "进行中的学术写作项目。这是一个活的列表，随着研究推进逐步更新。",
    statusLabel: {
      concept: "构思",
      drafting: "写作中",
      submitted: "审稿中",
      published: "已发表",
    },
    papers: [
      {
        id: "patent-ci",
        title: "基于专利文本挖掘的制造业企业技术竞争情报分析",
        desc: "以专利数据库为数据源，运用 Python 文本挖掘与可视化技术，构建制造业技术竞争态势分析方法。目标期刊：SSCI（Online Information Review）或 CSSCI（情报理论与实践）。此为申博核心论文。",
        status: "concept",
        target: "目标：SSCI Q3 / CSSCI",
      },
      {
        id: "gdp-stock",
        title: "宏观经济指标与资本市场联动效应分析：多国比较视角",
        desc: "基于课程作业的技术框架（World Bank API + AKShare 多源数据管道 + Streamlit 交互应用），需完全替换真实股市数据、扩展时间序列至20+年、升级方法论（Granger 因果 + VAR 模型）。待核心论文完成后启动。",
        status: "concept",
        target: "目标：CSSCI / 省级CN",
      },
      {
        id: "softwarex",
        title: "KOS: A Browser-Based Python Code Lab for Research Reproducibility in Competitive Intelligence",
        desc: "介绍 KOS 平台的 CodeLab 模块——基于 Pyodide WASM 技术的浏览器端 Python 执行环境，支持科研脚本的即时复现。目标期刊：SoftwareX（SCI JCR Q2, IF~3）。",
        status: "concept",
        target: "目标：SoftwareX (SCI Q2)",
      },
      {
        id: "mes-trace",
        title: "面向特种电缆连续硫化生产线的数据追溯系统架构设计",
        desc: "以 Troester 生产线调试经验为基础，设计制造执行系统（MES）中的数据采集与质量追溯方案，结合工业4.0框架讨论中小型制造企业的数字化转型路径。",
        status: "concept",
        target: "目标：中文核心 / 国际会议",
      },
    ],
  },
};

const en: Translation = {
  nav: {
    home: "Home",
    patent: "Patent Lab",
    code: "Code Lab",
    threeD: "3D Viewer",
    research: "Research",
    intelligence: "Intelligence",
    knowledge: "Knowledge",
    draw: "Draw",
    language: "中文",
  },
  hero: {
    greeting: "Jirui Wang",
    title:
      "Competitive Intelligence & Manufacturing Digitalization",
    subtitle:
      "M.Sc Candidate, ISTIC · B.Eng, China University of Petroleum",
    tagline: "AI Tools: Codex + WorkBuddy · Python Data Mining · Patent Analytics",
    cta: "Learn More",
  },
  profile: {
    title: "Profile",
    bio: "From automotive technology to mechanical engineering to information science — spanning three disciplines. From 2005 to 2021: quality inspection and technical work in the specialty cable industry at Shengli Oilfield Shengli Pump Co., Ltd. Since 2021: Corporate administration & HSE compliance management (Three-system internal auditor: ISO 9001/14001/45001). Currently focused on competitive intelligence analysis in manufacturing digital transformation, using Python-based patent text mining to extract technology competition landscapes. Aiming to bridge engineering practice with academic research, contributing methodological frameworks for knowledge management in smart manufacturing.",
    timeline: [
      {
        period: "2000 — 2003",
        title: "University of Petroleum (East China)",
        degree: "Diploma · Automotive Technology",
        badges: ["CET-4", "Three Good Student", "Drafting Cert. (Int.)", "Auto Repair Cert. (Int.)"],
      },
      {
        period: "2003 — 2005",
        title: "China University of Petroleum (East China)",
        degree: "B.Eng · Mechanical Design, Manufacturing & Automation",
        badges: ["CET-6"],
      },
      {
        period: "2005 — Present",
        title: "Shengli Oilfield Shengli Pump Co., Ltd.",
        degree: "Quality Inspection / Technical Mgmt (2005-2021) · Corp. Admin & HSE Compliance (2021-Present)",
        badges: ["Certified Quality Eng. (Int.)", "HSE Auditor", "MES", "Quality Traceability", "Cable Mfg", "Project Mgmt"],
        note: "Three-system internal auditor: ISO 9001 Quality / 14001 Environment / 45001 Occupational Health & Safety",
      },
      {
        period: "2025 — Present",
        title: "Institute of Scientific and Technical Information of China (ISTIC)",
        degree: "M.Sc (part-time) · Information Resource Management (GPA 86+/100)",
        badges: [
          "Python", "Data Mining", "Patent Analysis",
          "Competitive Intelligence", "D3.js", "Next.js", "Knowledge Organization",
        ],
        note: "Part-time study alongside full-time employment at SLP",
      },
    ],
    languages: [
      { language: "Chinese", level: "Native" },
      { language: "English", level: "CET-6 · Preparing for IELTS" },
    ],
    identity: {
      title: "Academic Identity",
      labelEmail: "Email",
      labelOrcid: "ORCID",
      email: "WJR2026@hotmail.com",
      orcid: "0009-0006-0528-3961",
      orcidUrl: "https://orcid.org/0009-0006-0528-3961",
    },
  },
  patent: {
    title: "Patent Snapshot",
    items: [
      { text: "Panoramic analysis of 5 patents", anchor: "stats" },
      { text: "Keyword cloud: data acquisition, traceability, intelligent manufacturing", anchor: "wordcloud" },
      { text: "Inventor collaboration network visualization", anchor: "network" },
    ],
  },
  research: {
    title: "Research Directions",
    direction1: {
      title: "Enterprise Technology CI",
      desc: "Patent text mining-based competitive intelligence analysis for enterprises, leveraging Python data processing and visualization.",
    },
    direction2: {
      title: "Manufacturing Execution System",
      desc: "Data acquisition and quality traceability system architecture for specialty cable manufacturing processes.",
    },
    direction3: {
      title: "Knowledge Organization System",
      desc: "AI-driven knowledge organization methods for manufacturing domain knowledge graphs and semantic retrieval.",
    },
  },
  projects: {
    title: "Projects",
    project1: {
      title: "Manufacturing Patent Landscape Analysis",
      desc: "Enterprise patent text mining based on Wanfang data, featuring word clouds, collaboration networks, and technology trend visualizations.",
    },
    project2: {
      title: "Python Data Analysis Platform",
      desc: "Enterprise data analytics and visualization tool built with Python, supporting multi-source data integration, automated computation, and report generation.",
    },
    project3: {
      title: "Submersible Cable Data Traceability",
      desc: "Prototype data acquisition and quality traceability system for continuous vulcanization production lines.",
    },
    project4: {
      title: "Troester Continuous Vulcanization Line Commissioning",
      desc: "Participated in installation and commissioning of a Troester (Germany) continuous vulcanization production line, collaborating with German engineers on equipment acceptance.",
    },
  },
  codeLab: {
    title: "Code Lab",
    subtitle: "Run Python in your browser — explore my data analysis workflows, no installation required",
    run: "Run",
    running: "Running…",
    output: "Output",
    loading: "Loading Python environment…",
    ready: "Environment ready. Click Run to execute.",
    demos: [
      { label: "API Data Fetching & JSON", name: "api_fetch.py" },
      { label: "Patent Text Mining", name: "patent_mining.py" },
    ],
    custom: "Custom",
    uploadPy: "Upload .py File",
    clearOutput: "Clear",
    codePlaceholder: "# Type or paste Python code here\n# Standard library supported (statistics, collections, json, math, re...)\n# print() works as expected\n\nprint(\"Hello, KOS!\")",
  },
  certGallery: {
    view: "View Full",
    close: "Close",
    of: " of ",
  },
  cnkiAnalysis: {
    title: "CNKI Bibliometric Analysis",
    subtitle:
      "A bibliometric study of the ESP (Electrical Submersible Pump) domain based on the CNKI database, demonstrating systematic methodology in literature retrieval, data cleaning, keyword extraction, and visualization analysis. Completed as coursework for the ISTIC M.Sc. in Information Resource Management, showcasing core competencies in information organization and bibliometrics.",
    badge: "Bibliometrics",
    methodTitle: "Methodology Note",
    methodDesc:
      "Data source: CNKI academic journal database (retrieved January 31, 2026). Applied bibliometric methods to analyze 197 target publications across dimensions of annual distribution, publication type composition, and keyword frequency. Data processing and visualization performed with Python (jieba + wordcloud + matplotlib). This showcase presents 3 core analyses: yearly publication trends, publication type distribution, and TOP15 high-frequency keywords.",
  },
  footer: {
    copyright: "© 2026 KOS — Knowledge Operating System",
    built: "Built with Next.js · Deployed on CloudStudio",
    github: "GitHub",
  },
  researchPage: {
    title: "Research Proposal",
    subtitle: "Pre-study for German PhD Application — Competitive Intelligence Systems in the Digital Transformation of Manufacturing",
    abstract: "This research proposal presents a framework for a Competitive Intelligence System (CIS) tailored to the digital transformation of manufacturing. Traditional competitive intelligence methods rely on manual literature searches and static reports, struggling to cope with the dual pressures of global supply chain restructuring and rapidly evolving industrial policies. This study aims to leverage patent text mining, organizational knowledge graphs, and Python-based data analytics to construct a semi-automated technology competitive landscape awareness system, providing actionable intelligence support for medium-sized manufacturers in industries such as specialty cables. Positioned at the intersection of information science, manufacturing engineering, and strategic management, this research targets doctoral programs at TU München, RWTH Aachen, TU Berlin, or Universität Stuttgart.",
    sections: [
      {
        id: "background",
        title: "1. Research Background & Motivation",
        content: "Manufacturing is at the core of the Fourth Industrial Revolution (Industrie 4.0). The regional restructuring of global supply chains, heightened risks of technological decoupling, and the strategic resurgence of national industrial policies have transformed Competitive Technical Intelligence (CTI) from an optional tool into a business necessity.\n\nHowever, traditional CTI practice faces three bottlenecks: (1) Data silos — patent databases, academic literature, industry reports, and corporate announcements remain disconnected; (2) Lagging analytical methods — dominated by manual reading and Excel-based statistics, inadequate for massive unstructured text; (3) Missing methodology — no theoretical framework exists for systematically integrating NLP techniques into the intelligence workflows of manufacturing enterprises.\n\nThis study focuses on China's specialty cable manufacturing sector, which exemplifies medium-sized manufacturing: heavy dependence on German equipment (e.g., Troester continuous vulcanization lines), international patent competition, urgent digital transformation needs, yet weak intelligence capabilities. The researcher's twenty years of industry experience (2005–2021 quality & technical management; 2021–present HSE systems & corporate administration) provides a unique vantage point for understanding enterprise intelligence requirements."
      },
      {
        id: "problem",
        title: "2. Research Problem & Questions",
        content: "This research centers on one core question: How can we design and evaluate a data-driven competitive intelligence system that automatically extracts technology competition landscapes from patent literature and serves the strategic decision-making of medium-sized manufacturers?\n\nThis core question decomposes into three sub-questions:\n\nRQ1 (Intelligence Acquisition): How can multi-dimensional technology intelligence data (technology classification, inventor networks, claim evolution, geographic distribution) be efficiently collected, cleaned, and structured from Chinese-language patent databases?\n\nRQ2 (Intelligence Analysis): Which NLP and network analysis methods can extract meaningful technology competition signals from patent texts (emerging technology topic identification, competitor technology trajectory tracking, technology white space discovery)?\n\nRQ3 (Intelligence Presentation): How can analytical results be translated into actionable knowledge representations (interactive knowledge graphs, automated intelligence briefings) for decision-makers without technical backgrounds?"
      },
      {
        id: "literature",
        title: "3. Literature Review & Research Gap",
        content: "Research on technology competitive intelligence traces back to Porter's (1980) competitive strategy framework, subsequently developed by Ashton & Klavans (1997) and Lichtenthaler (2003) into patent-centric methodologies. In recent years, NLP breakthroughs — particularly Transformer-based patent text mining (e.g., Lee et al., 2020; Arts et al., 2021) — have significantly improved the precision of technology topic identification.\n\nHowever, three notable gaps persist in the existing literature:\n\nGap 1: Most studies focus on technology-intensive large enterprises (pharmaceuticals, semiconductors), leaving the applicability to medium-sized manufacturers unvalidated. These enterprises have fewer patents, more concentrated technology domains, and limited analytical resources, requiring different methodological designs.\n\nGap 2: Patent analysis remains disconnected from organizational knowledge management. Existing studies treat patents as isolated data sources, neglecting their relational value with internal enterprise knowledge (process documentation, equipment parameters, quality issue records).\n\nGap 3: Action-oriented intelligence presentation is under-researched. Much work stops at visualization display, without exploring how to transform analytical findings into decision inputs for enterprise managers.\n\nThis study fills these gaps by embedding patent analysis within an enterprise Knowledge Organization System (KOS) framework and designing a decision-oriented intelligence presentation interface."
      },
      {
        id: "methodology",
        title: "4. Proposed Methodology",
        content: "This study adopts Design Science Research (DSR) methodology, proceeding in four phases:\n\nPhase I: Data Infrastructure Construction\n- Data sources: CNIPA patent database, Wanfang Data, CNKI academic journals\n- Technology stack: Python (AKShare/requests for data acquisition + pandas/jieba for data processing + scikit-learn/networkx for analysis)\n- Data pipeline: Semi-automated ETL workflows supporting incremental updates and data versioning\n\nPhase II: Competitive Intelligence Analysis Engine\n- Patent text preprocessing: Chinese word segmentation (jieba), stop-word removal, TF-IDF vectorization\n- Technology topic modeling: LDA topic model with BERTopic cross-validation\n- Inventor collaboration network: centrality analysis and community detection using networkx\n- Technology trajectory tracking: temporal evolution analysis of technology topics\n\nPhase III: Intelligence Presentation Interface\n- Interactive knowledge graph: D3.js force-directed graph displaying technology-inventor-patent triadic relationships\n- Automated intelligence briefing: template-based NLP summary generation\n- Decision dashboard: real-time monitoring of Key Competitive Indicators (KCI)\n\nPhase IV: Empirical Validation\n- Case study: Validate the system's intelligence value using the submersible specialty cable industry as the scenario\n- Expert evaluation: Utility assessment by enterprise technical managers and competitive intelligence scholars\n- Reproducibility: All code and datasets published as open source through KOS CodeLab (Pyodide WASM)"
      },
      {
        id: "significance",
        title: "5. Expected Contributions & Significance",
        content: "Theoretical Contributions:\n1. Propose the \"Embedded Competitive Intelligence System\" (Embedded CIS) concept, anchoring patent analysis within an enterprise knowledge organization framework, bridging the theoretical gap between CTI and knowledge management.\n2. Customize NLP methodology for the medium-sized manufacturing enterprise context, validating the applicability boundaries of lightweight text mining techniques in this setting.\n\nPractical Contributions:\n1. Develop an open-source, reproducible competitive intelligence analysis toolchain, lowering the CTI adoption threshold for medium-sized enterprises.\n2. Provide an interactive intelligence presentation interface through the KOS platform, serving as a showcase and communication vehicle for industry-academia collaboration.\n\nAcademic Pathway:\n- Short-term (2026–2027): Complete a Chinese-language CSSCI paper (Journal of Intelligence Theory and Practice), establishing domestic academic standing\n- Medium-term (2027–2028): Extend the methodology to international contexts, submit to an SSCI journal (Online Information Review)\n- Long-term (doctoral phase): Deepen the theoretical framework under German supervision, expanding the research scope from Chinese manufacturing to Sino-German manufacturing comparative studies"
      },
      {
        id: "references",
        title: "6. Key References",
        content: "Ashton, W. B., & Klavans, R. A. (1997). Keeping abreast of science and technology. Battelle Press.\n\nArts, S., Hou, J., & Gomez, J. C. (2021). Natural language processing to identify the creation and impact of new technologies in patent text. Research Policy, 50(2), 104144.\n\nLee, C., Jeon, D., Ahn, J., & Kwon, O. (2020). A deep learning-based approach for patent landscaping. Technological Forecasting and Social Change, 155, 119968.\n\nLichtenthaler, E. (2003). Third generation management of technology intelligence processes. R&D Management, 33(4), 361–375.\n\nPorter, M. E. (1980). Competitive strategy. Free Press.\n\nYoon, B., & Park, Y. (2004). A text-mining-based patent network. Technovation, 24(11), 897–906."
      }
    ],
  },
  patentPage: {
    totalPatents: "Active Patents",
    totalInventors: "Inventors",
    collaborations: "Collaborations",
    techAreas: "Tech Areas",
    wordCloud: "Technology Keyword Cloud",
    techDist: "Technology Distribution",
    patentType: "Patent Type Statistics",
    yearTrend: "Annual Filing Trend",
    networkTitle: "Inventor Collaboration Network",
    patentList: "Patent Details",
    loading: "Loading data...",
    error: "Failed to load data. Please refresh.",
    title: "Title",
    inventors: "Inventors",
    type: "Type",
    year: "Year",
    pubno: "Pub. No.",
    certs: "Patent Certificates",
    certView: "View Full",
    certClose: "Close",
    certOf: " of ",
    inventionPatents: "Invention Patents",
    utilityModels: "Utility Models",
    invention: "Invention",
    utility: "Utility",
    manageCerts: "Manage Certs",
    manageUnlock: "Click to unlock management",
    managePassword: "Enter management password",
    manageEnter: "Enter",
    manageWrongPassword: "Wrong password, try again",
    manageUpload: "Click to upload certificate image",
    manageLabel: "Label Type",
    manageReset: "Reset Default",
    manageSave: "Save Settings",
    manageDone: "Exit Management",
    manageTitle: "Certificate Manager",
    manageHelp: "Click image area to upload · Select label type · Click Save to apply",
    manageDrag: "Drag to reorder",
    manageRemove: "Remove this cert",
  },
  workingPapers: {
    title: "Working Papers",
    subtitle: "Ongoing academic writing projects. This is a living list, updated as research progresses.",
    statusLabel: {
      concept: "Concept",
      drafting: "Drafting",
      submitted: "Under Review",
      published: "Published",
    },
    papers: [
      {
        id: "patent-ci",
        title: "Patent Text Mining-Based Competitive Technology Intelligence Analysis for Manufacturing Enterprises",
        desc: "Building a manufacturing technology competition landscape analysis method using patent databases, Python text mining, and visualization. Target: SSCI (Online Information Review) or CSSCI. This is the core paper for PhD applications.",
        status: "concept",
        target: "Target: SSCI Q3 / CSSCI",
      },
      {
        id: "gdp-stock",
        title: "Macroeconomic Indicators and Capital Market Co-Movement: A Multi-Country Comparative Analysis",
        desc: "Based on the technical architecture from coursework (World Bank API + AKShare multi-source data pipeline + Streamlit app), requiring complete replacement with real stock data, extension to 20+ years of time series, and methodological upgrade (Granger causality + VAR). To be initiated after the core paper.",
        status: "concept",
        target: "Target: CSSCI / Chinese CN journal",
      },
      {
        id: "softwarex",
        title: "KOS: A Browser-Based Python Code Lab for Research Reproducibility in Competitive Intelligence",
        desc: "Presenting the CodeLab module of the KOS platform — a Pyodide WASM-based in-browser Python execution environment supporting instant reproducibility of research scripts. Target: SoftwareX (SCI JCR Q2, IF~3).",
        status: "concept",
        target: "Target: SoftwareX (SCI Q2)",
      },
      {
        id: "mes-trace",
        title: "Data Traceability System Architecture Design for Specialty Cable Continuous Vulcanization Production Lines",
        desc: "Based on Troester production line commissioning experience, designing a data acquisition and quality traceability solution within a Manufacturing Execution System (MES), discussing digital transformation pathways for SMEs through an Industry 4.0 lens.",
        status: "concept",
        target: "Target: Chinese core journal / International conference",
      },
    ],
  },
};

export const translations: Record<Lang, Translation> = { zh, en };

export function getTranslation(lang: Lang): Translation {
  return translations[lang] || translations.zh;
}
