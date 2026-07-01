#!/usr/bin/env python3
"""从万方数据提取专利JSON（无需jieba/wordcloud/matplotlib等依赖）"""

import re, json, os
from collections import Counter, defaultdict

INPUT = r"D:/Downloads/2026-06-02上午9-21-35@WanFangdata.txt"
OUTPUT = r"C:\Users\Mr_Wang\WorkBuddy\2026-06-03-14-49-17\kos\public\data\patents.json"

def parse_patents(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    blocks = re.split(r'\n\n+', content.strip())
    patents = []
    for block in blocks:
        record = {}
        current_authors = []
        for line in block.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            for field in ['Reference Type', 'Title', 'Applicant Name',
                          'Application Number', 'Pub.No.', 'Type of Work',
                          'Date', 'Year', 'Abstract', 'URL',
                          'Database Provider']:
                m = re.match(r'\{' + field + r'\}: (.+)', line)
                if m:
                    record[field] = m.group(1)
                    break
            m = re.match(r'\{Author\}: (.+)', line)
            if m:
                current_authors.append(m.group(1))
        if current_authors:
            record['Authors'] = list(dict.fromkeys(current_authors))
        if 'Title' in record:
            patents.append(record)
    return patents

def deduplicate(patents):
    groups = defaultdict(list)
    for p in patents:
        groups[p.get('Title', '')].append(p)
    unique = []
    for title, group in groups.items():
        best = None
        for p in group:
            if p.get('Pub.No.', '').endswith('B'):
                best = p; break
        if best is None:
            for p in group:
                if p.get('Pub.No.', '').endswith('A'):
                    best = p; break
        if best is None:
            best = group[0]
        best['AllPubNos'] = [p.get('Pub.No.', '') for p in group]
        unique.append(best)
    return unique

def extract_keywords(patents):
    text = ' '.join([p.get('Title', '') + ' ' + p.get('Abstract', '') for p in patents])
    raw_words = re.findall(r'[\u4e00-\u9fa5a-zA-Z]{2,}', text)
    stopwords = {'本发明','实用新型','涉及','一种','包括','设置','用于','所述','具有',
                 '可以','使得','通过','进行','使用','能够','从而','并且','或者','其中',
                 '该','上','下','中','内','外','其','与','及','等','在','为','被','将',
                 '第一','第二','第三','部分','结构','装置','系统','方法','连接','安装',
                 '实现','有效','便于','提高','确保','之间','相互','形成','设有','还要',
                 '进而','本申请','本','用于','限定','该定位','定位孔','定位本体','从',
                 '包括','还','利','所','地'}
    words = [w for w in raw_words if w not in stopwords]
    counter = Counter(words)
    return [{"word": w, "count": c} for w, c in counter.most_common(60)]

def build_network(patents):
    author_count = Counter()
    cooccur = Counter()
    for p in patents:
        authors = p.get('Authors', [])
        for a in authors:
            author_count[a] += 1
        for i in range(len(authors)):
            for j in range(i+1, len(authors)):
                cooccur[tuple(sorted([authors[i], authors[j]]))] += 1
    nodes = [{"id": a, "count": c} for a, c in author_count.items()]
    links = [{"source": a1, "target": a2, "weight": w}
             for (a1, a2), w in cooccur.items()]
    return {"nodes": nodes, "links": links}

def tech_distribution(patents):
    tech_map = defaultdict(int)
    for p in patents:
        title = p.get('Title', '')
        if '磁悬浮' in title: tech_map['磁悬浮列车电缆'] += 1
        elif '潜油' in title or '电泵' in title: tech_map['潜油电泵电缆'] += 1
        elif '油井' in title or '方形护套' in title: tech_map['油井护套电缆'] += 1
        elif '铅锭' in title: tech_map['电缆护套/铅锭'] += 1
        else: tech_map['其他电缆技术'] += 1
    return [{"name": k, "count": v} for k, v in tech_map.items()]

def type_stats(patents):
    c = Counter(p.get('Type of Work', '未分类') for p in patents)
    return [{"name": k, "count": v} for k, v in c.items()]

def year_stats(patents):
    c = Counter()
    for p in patents:
        y = p.get('Year', '')
        if y: c[int(y)] += 1
    return [{"year": y, "count": c[y]} for y in sorted(c.keys())]

def main():
    raw = parse_patents(INPUT)
    patents = deduplicate(raw)
    
    data = {
        "total": len(patents),
        "patents": [{
            "title": p.get("Title", ""),
            "authors": ", ".join(p.get("Authors", [])),
            "type": p.get("Type of Work", ""),
            "year": p.get("Year", ""),
            "pubno": p.get("Pub.No", ""),
            "abstract": p.get("Abstract", "")[:200],
        } for p in patents],
        "keywords": extract_keywords(patents),
        "network": build_network(patents),
        "techDistribution": tech_distribution(patents),
        "typeStats": type_stats(patents),
        "yearStats": year_stats(patents),
    }
    
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] patents.json written: {len(patents)} patents, {os.path.getsize(OUTPUT)} bytes")

if __name__ == '__main__':
    main()
