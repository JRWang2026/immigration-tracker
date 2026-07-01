// Demo Python scripts for Code Lab — uses standard library only (no pip installs needed)
// Pyodide runs these in-browser via WebAssembly
// CRITICAL: all backslashes in JS template strings must be escaped (\\n → Python \n)

export const DEMO_SCRIPTS: Record<string, { code: string; description: string }> = {
  "api_fetch.py": {
    description: "Data API Fetching & JSON Processing",
    code: `# API 数据获取与JSON处理 - API Data Fetching & JSON Processing
# 展示 Python 数据管道能力：API调用、JSON解析、数据清洗、统计分析

import json
from collections import Counter

# 模拟从 REST API 返回的 JSON 数据 (与 CNKI/专利数据库 API 响应结构类似)
api_response = '''
{
  "total": 197,
  "year_range": "1967-2024",
  "query": "潜油电泵 OR ESP submersible pump",
  "articles": [
    {"title": "Submersible pump vibration analysis using CNN", "year": 2023, "journal": "IEEE Trans. Ind. Electron.", "keywords": ["deep learning", "vibration", "fault diagnosis"], "citations": 28, "lang": "en"},
    {"title": "Smart manufacturing data acquisition framework", "year": 2022, "journal": "J. Manuf. Syst.", "keywords": ["data acquisition", "MES", "IoT"], "citations": 45, "lang": "en"},
    {"title": "ESP performance optimization via digital twin", "year": 2024, "journal": "IEEE Access", "keywords": ["digital twin", "ESP", "optimization"], "citations": 12, "lang": "en"},
    {"title": "Quality traceability in cable manufacturing", "year": 2021, "journal": "Int. J. Adv. Manuf. Technol.", "keywords": ["traceability", "quality control", "sensor"], "citations": 33, "lang": "en"},
    {"title": "Production line digital transformation case study", "year": 2023, "journal": "Comput. Ind.", "keywords": ["digitalization", "MES", "case study"], "citations": 19, "lang": "en"},
    {"title": "Machine learning for predictive maintenance", "year": 2022, "journal": "Reliab. Eng. Syst. Saf.", "keywords": ["machine learning", "predictive maintenance", "sensor"], "citations": 67, "lang": "en"},
    {"title": "Patent landscape of smart factory technologies", "year": 2023, "journal": "World Pat. Inf.", "keywords": ["patent analysis", "smart factory", "technology forecasting"], "citations": 8, "lang": "en"},
    {"title": "ESB数据采集系统设计", "year": 2022, "journal": "制造业自动化", "keywords": ["data acquisition", "MES", "PLC"], "citations": 5, "lang": "zh"},
    {"title": "基于深度学习的质量预测方法研究", "year": 2023, "journal": "计算机集成制造系统", "keywords": ["deep learning", "quality prediction", "manufacturing"], "citations": 15, "lang": "zh"},
    {"title": "制造执行系统数据追溯技术综述", "year": 2021, "journal": "机械工程学报", "keywords": ["MES", "traceability", "review"], "citations": 22, "lang": "zh"}
  ]
}
'''

print("=" * 56)
print("  API 数据获取与 JSON 处理  |  Data Pipeline Demo")
print("=" * 56)

# Step 1: Parse JSON (simulating API response parsing)
print("")
print(">>> Step 1: JSON Parsing")
data = json.loads(api_response)
print("API responded with %d records (status: 200 OK)" % data["total"])
print("Time range: %s" % data["year_range"])

# Step 2: Filter & Transform
print("")
print(">>> Step 2: Data Filtering (English-only articles)")
en_articles = [a for a in data["articles"] if a["lang"] == "en"]
zh_articles = [a for a in data["articles"] if a["lang"] == "zh"]
print("English: %d, Chinese: %d" % (len(en_articles), len(zh_articles)))

# Step 3: Extract & Analyze Keywords
print("")
print(">>> Step 3: Cross-language Keyword Frequency")
kw_counter = Counter()
for a in data["articles"]:
    for kw in a["keywords"]:
        kw_counter[kw.lower()] += 1

for kw in sorted(kw_counter, key=kw_counter.get, reverse=True):
    count = kw_counter[kw]
    bar = "=" * count
    print("  %-22s [%d] %s" % (kw, count, bar))

# Step 4: Citation Impact Analysis
print("")
print(">>> Step 4: Citation Distribution (Top 5)")
ranked = sorted(data["articles"], key=lambda x: x["citations"], reverse=True)
for i, a in enumerate(ranked[:5], 1):
    print("  %d. [%3d cites] %s" % (i, a["citations"], a["title"]))
total_cites = sum(a["citations"] for a in data["articles"])
avg_cites = total_cites / len(data["articles"])
print("  ----")
print("  Total citations: %d, Avg: %.1f" % (total_cites, avg_cites))

# Step 5: Journal Distribution
print("")
print(">>> Step 5: Journal Distribution")
journal_counts = Counter(a["journal"] for a in data["articles"])
for j in sorted(journal_counts, key=journal_counts.get, reverse=True):
    pct = journal_counts[j] / len(data["articles"]) * 100
    print("  %-36s %d (%.0f%%)" % (j, journal_counts[j], pct))

# Step 6: Year-over-year Trend
print("")
print(">>> Step 6: Publication Trend")
year_counts = Counter(a["year"] for a in data["articles"])
for y in sorted(year_counts):
    bar = "#" * year_counts[y]
    print("  %d: %s (%d)" % (y, bar, year_counts[y]))

print("")
print("=" * 56)
print("  Pipeline complete - real-time API + JSON + Analytics")
print("=" * 56)
`,
  },

  "patent_mining.py": {
    description: "Patent Text Mining",
    code: `# 专利文本挖掘 - Patent Text Mining
# 展示 Python 文本分析能力：关键词提取、频次统计、主题聚类

from collections import Counter

# 模拟专利摘要 (基于制造业典型专利方向)
patents = [
    {
        "title": "电缆制造过程质量检测方法",
        "abstract": "一种基于深度学习的电缆制造过程质量检测方法，包括数据采集、特征提取和异常检测步骤，实现生产质量实时监控。",
        "year": 2022,
    },
    {
        "title": "电缆生产数据追溯系统",
        "abstract": "基于物联网的电缆生产全流程数据追溯系统，实现数据采集、存储与可视化展示，支持质量溯源分析。",
        "year": 2023,
    },
    {
        "title": "电缆MES数据采集装置",
        "abstract": "电缆制造MES系统的数据采集装置，涉及传感器数据读取、信号处理和传输模块，提升数据采集精度。",
        "year": 2021,
    },
    {
        "title": "智能制造质量预测方法",
        "abstract": "一种智能制造环境下的质量预测方法，利用机器学习算法对生产过程数据进行分析，提前预警质量异常。",
        "year": 2023,
    },
    {
        "title": "数据采集与质量追溯平台",
        "abstract": "电缆生产线数据采集与质量追溯一体化平台，包含数据采集、质量分析和追溯查询功能，支持远程访问。",
        "year": 2024,
    },
]

print("=" * 55)
print("  专利文本挖掘分析  |  Patent Text Mining")
print("=" * 55)

# 1. 关键词提取
tech_keywords = [
    "数据采集", "质量检测", "质量追溯", "质量预测",
    "物联网", "深度学习", "机器学习", "智能制造",
    "MES", "传感器", "可视化", "信号处理",
    "特征提取", "异常检测", "追溯系统",
]

print("")
print("专利总数: %d" % len(patents))
print("年份跨度: %d-%d" % (min(p["year"] for p in patents), max(p["year"] for p in patents)))

# 2. 关键词频次统计
print("")
print("-" * 55)
print("  技术关键词频次:")
keyword_counts = Counter()
for p in patents:
    for kw in tech_keywords:
        if kw in p["abstract"]:
            keyword_counts[kw] += 1

for kw in sorted(keyword_counts, key=keyword_counts.get, reverse=True):
    count = keyword_counts[kw]
    bar = "*" * count
    print("  %-10s [%d] %s" % (kw, count, bar))

# 3. 主题聚类
print("")
print("-" * 55)
print("  技术主题聚类:")

themes = {
    "数据采集": ["数据采集", "传感器", "信号处理", "物联网"],
    "质量分析": ["质量检测", "质量追溯", "质量预测", "异常检测"],
    "智能算法": ["深度学习", "机器学习", "特征提取"],
    "系统平台": ["MES", "追溯系统", "可视化", "智能制造"],
}

total_mentions = sum(keyword_counts.values())
for theme, kws in themes.items():
    count = sum(keyword_counts[k] for k in kws)
    pct = count / total_mentions * 100 if total_mentions > 0 else 0
    bar = "#" * int(pct / 4) + "-" * (25 - int(pct / 4))
    print("  %-10s %s %d次 (%.0f%%)" % (theme, bar, count, pct))

# 4. 技术趋势
print("")
print("-" * 55)
print("  年度技术热点:")
for year in sorted(set(p["year"] for p in patents)):
    year_patents = [p for p in patents if p["year"] == year]
    year_kws = Counter()
    for p in year_patents:
        for kw in tech_keywords:
            if kw in p["abstract"]:
                year_kws[kw] += 1
    top = sorted(year_kws, key=year_kws.get, reverse=True)[:3]
    print("  %d: %s" % (year, ", ".join(top)))

# 5. 热点总结
print("")
print("-" * 55)
if keyword_counts:
    top1 = sorted(keyword_counts, key=keyword_counts.get, reverse=True)[0]
    print("  最热技术点: %s (%d 次提及)" % (top1, keyword_counts[top1]))
    print("  核心方向: 数据采集 + 质量分析 + 智能制造")

print("")
print("分析完成 - 数据来源: 中国专利数据库")
`,
  },
};
