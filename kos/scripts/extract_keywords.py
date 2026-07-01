"""
从专利标题和摘要中提取真正的技术关键词（2-6字）
替代之前的整句提取逻辑
"""
import json
import re
from collections import Counter

# 专利数据路径
PATENTS_PATH = "../public/data/patents.json"

# 停用词/噪声词（专利文本中高频但无技术含义的词）
STOP_WORDS = {
    "包括", "所述", "一种", "设置", "用于", "通过", "具有", "该",
    "本发明", "本申请", "实用新型", "涉及", "其中", "包括有",
    "且该", "进而", "无需", "便于", "同时也", "在工作时",
    "使得", "相互", "通过", "然后", "以及", "还包括",
    "其特征在于", "本发明涉及", "本发明的", "在此",
    "之间的", "在此基础", "公开了一种",
    "与此同时", "所述的", "较佳地", "特别的", "进一步",
    "相互配合", "地", "中", "并", "或", "和", "为", "及",
    "与", "以", "在", "不", "其", "可", "的",
}

def load_patents():
    with open(PATENTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_meaningful_words(text):
    """
    从中文文本中提取2-6字的技术关键词
    使用正则 + 启发式规则，不依赖jieba分词
    """
    results = []

    # 移除标点和数字
    text = re.sub(r"[，。；：、！？（）【】《》\"\"''\[\]{}（）\d]", " ", text)

    # 切分短语（按常见分隔模式）
    # 专利文本常见模式：XX装置、XX系统、XX结构、XX方法
    phrases = re.split(r"[\s,，;；、]", text)

    for phrase in phrases:
        phrase = phrase.strip()
        if len(phrase) < 2:
            continue

        # 识别2-6字的技术术语
        # 技术术语通常以这些后缀结尾
        tech_suffixes = [
            "装置", "系统", "结构", "方法", "机构", "设备", "组件",
            "模块", "单元", "电缆", "导线", "护套", "绝缘", "导体",
            "定位", "绞合", "绕组", "定子", "转子", "磁悬浮",
            "上料", "调节", "固定", "连接", "驱动", "传动",
            "密封", "保护", "支撑", "滑动", "转动", "移动",
            "传感", "控制", "检测", "测量", "信号", "电源",
            "油井", "电泵", "铅锭", "氟橡胶", "铠装", "护层",
        ]

        # 方法1：按后缀匹配
        for suffix in tech_suffixes:
            idx = phrase.find(suffix)
            if idx >= 0:
                # 取后缀及之前2-4字
                start = max(0, idx - 3)
                term = phrase[start:idx + len(suffix)]
                if 2 <= len(term) <= 8:
                    results.append(term)

        # 方法2：2-3字的短词直接保留（过滤停用词）
        if 2 <= len(phrase) <= 3 and phrase not in STOP_WORDS:
            results.append(phrase)

        # 方法3：滑动窗口提取2-4字词组
        if len(phrase) >= 4:
            for i in range(len(phrase) - 1):
                for wlen in [2, 3, 4]:
                    if i + wlen <= len(phrase):
                        sub = phrase[i:i + wlen]
                        if sub not in STOP_WORDS and len(sub) >= 2:
                            results.append(sub)

    return results


def extract_all_keywords(patents):
    """从所有专利的标题和摘要中提取关键词"""
    all_words = []

    for p in patents:
        text = p["title"] + "。" + p["abstract"]
        words = extract_meaningful_words(text)
        all_words.extend(words)

    # 统计频率
    counter = Counter(all_words)

    # 过滤：至少出现1次，词长2-8字
    filtered = [
        {"word": w, "count": c}
        for w, c in counter.most_common(50)
        if 2 <= len(w) <= 8 and c >= 1
    ]

    # 去重：移除相似短词（如果短词是长词的一部分）
    deduped = []
    for i, item in enumerate(filtered):
        is_sub = False
        for j, other in enumerate(filtered):
            if i != j and item["word"] in other["word"] and item["count"] <= other["count"]:
                is_sub = True
                break
        if not is_sub:
            deduped.append(item)

    return deduped[:40]  # 最多40个关键词


def main():
    data = load_patents()
    keywords = extract_all_keywords(data["patents"])

    print(f"提取到 {len(keywords)} 个关键词:")
    for kw in keywords[:30]:
        print(f"  {kw['word']} ({kw['count']}次)")

    # 更新数据
    data["keywords"] = keywords
    with open(PATENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n已更新 {PATENTS_PATH}")


if __name__ == "__main__":
    main()
