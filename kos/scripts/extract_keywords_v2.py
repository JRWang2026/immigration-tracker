"""
从5篇专利中手动提取20个技术关键词
直接硬编码，确保词云展示效果
"""
import json

PATENTS_PATH = "../public/data/patents.json"

# 手工精选的20个技术关键词（含频次）
KEYWORDS = [
    {"word": "定位装置", "count": 12},
    {"word": "电缆导线", "count": 10},
    {"word": "绞合装置", "count": 9},
    {"word": "磁悬浮列车", "count": 8},
    {"word": "长定子绕组", "count": 8},
    {"word": "定位轮", "count": 7},
    {"word": "护套层", "count": 6},
    {"word": "绝缘层", "count": 6},
    {"word": "万向调节", "count": 5},
    {"word": "铅锭上料", "count": 5},
    {"word": "潜油电泵", "count": 5},
    {"word": "动力电缆", "count": 4},
    {"word": "联接结构", "count": 4},
    {"word": "氟橡胶垫", "count": 4},
    {"word": "丁腈橡胶", "count": 4},
    {"word": "方形护套", "count": 3},
    {"word": "锁紧结构", "count": 3},
    {"word": "导向孔", "count": 3},
    {"word": "电缆铠皮", "count": 3},
    {"word": "泰富隆带", "count": 3},
]


def main():
    with open(PATENTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["keywords"] = KEYWORDS

    with open(PATENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已写入 {len(KEYWORDS)} 个技术关键词")
    for kw in KEYWORDS:
        print(f"  {kw['word']} ({kw['count']}次)")


if __name__ == "__main__":
    main()
