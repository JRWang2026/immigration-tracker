"""
KOS 学术网站桥接器

把本地 Agent 的运行结果转换成 KOS 网站可直接读取的 JSON 数据源。
KOS 网站可以通过 fetch('/data/seek_nz_latest.json') 方式读取，
也可以用 GitHub Actions 自动把 local_agent_output/kos/ 同步到 KOS 仓库的 public/data 目录。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


KOS_SECTIONS = {
    "seek-nz": {
        "title": "SEEK NZ 绿名单岗位追踪",
        "description": "每日自动扫描 SEEK NZ 邮件中的绿名单 Tier1 ICT 岗位",
        "icon": "briefcase",
    },
    "policy-tracker": {
        "title": "全球移民政策追踪",
        "description": "监控 OECD 主要国家技术移民政策变化",
        "icon": "globe",
    },
    "german-phd": {
        "title": "德国博士岗位扫描",
        "description": "EURAXESS / academics.de 德国及欧洲博士岗位聚合",
        "icon": "graduation-cap",
    },
}


def write_kos_feed(
    kos_dir: Path,
    section_id: str,
    data: Dict[str, Any],
    timestamp: datetime = None,
) -> Path:
    """
    写入 KOS 数据 feed。
    返回写入的文件路径。
    """
    if section_id not in KOS_SECTIONS:
        raise ValueError(f"Unknown KOS section: {section_id}")

    kos_dir.mkdir(parents=True, exist_ok=True)

    meta = KOS_SECTIONS[section_id].copy()
    meta["section_id"] = section_id
    meta["last_updated"] = (timestamp or datetime.now()).isoformat()

    feed = {
        "meta": meta,
        "data": data,
    }

    # KOS 网站统一读取 latest.json；每个 section 独占一个子目录
    output_path = kos_dir / "latest.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)

    # 同时写入一份以日期命名的历史快照
    date_str = (timestamp or datetime.now()).strftime("%Y-%m-%d")
    snapshot_path = kos_dir / f"{section_id}_{date_str}.json"
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)

    return output_path


def generate_kos_index(kos_dir: Path, feeds: Dict[str, Path]) -> Path:
    """
    生成 KOS 数据目录索引，供 KOS 网站一次性拉取所有可用 feed。
    """
    index = {
        "updated_at": datetime.now().isoformat(),
        "feeds": {},
    }
    for section_id, path in feeds.items():
        index["feeds"][section_id] = {
            "url": f"data/{section_id}/latest.json",
            "meta": KOS_SECTIONS.get(section_id, {}),
        }

    index_path = kos_dir / "index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    return index_path
