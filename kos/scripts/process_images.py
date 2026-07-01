#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process personal photos and certificates:
1. Desensitize: blur ID numbers and certificate numbers
2. Add diagonal watermark overlay
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

BASE = r"C:\Users\Mr_Wang\WorkBuddy\2026-06-03-14-49-17\kos"
INPUT_DIR = r"D:\Downloads"
OUTPUT_BASE = os.path.join(BASE, "public")

# Image definitions with blur regions (as % of width, height) and output paths
IMAGES = {
    # Certificate: 汽车修理证 - blur 身份证号 + 证书编号（范围扩大10%）
    "cert-auto-repair.jpg": {
        "type": "cert",
        "src": "certs/cert-auto-repair.jpg",   # already processed, re-process from original
        "output": "certs/cert-auto-repair.jpg",
        "blur": [
            # 身份证号 — 扩大范围
            {"name": "id_card", "x1": 0.10, "y1": 0.75, "x2": 0.50, "y2": 0.91},
            # 证书编号 — 扩大范围
            {"name": "cert_no", "x1": 0.10, "y1": 0.62, "x2": 0.52, "y2": 0.76},
        ],
        "label": "汽车维修工（中级）",
        "desc": "2003年6月获劳动和社会保障部职业技能鉴定中心认证",
    },
    # Certificate: 三好学生 - no sensitive numbers
    "cert-honor-student.jpg": {
        "type": "cert",
        "src": "certs/cert-honor-student.jpg",
        "output": "certs/cert-honor-student.jpg",
        "blur": [],
        "label": "三好学生荣誉证书",
        "desc": "2001-2002学年，中国石油大学（华东）",
    },
    # Certificate: 制图员资格证 - blur 身份证号 + 证书编号（范围扩大）
    "cert-drafting.jpg": {
        "type": "cert",
        "src": "certs/cert-drafting.jpg",
        "output": "certs/cert-drafting.jpg",
        "blur": [
            {"name": "id_card", "x1": 0.08, "y1": 0.75, "x2": 0.50, "y2": 0.91},
            {"name": "cert_no", "x1": 0.10, "y1": 0.62, "x2": 0.52, "y2": 0.76},
        ],
        "label": "制图员（中级）",
        "desc": "2001年7月获劳动和社会保障部职业技能鉴定中心认证",
    },
    # Certificate: 学士学位证书 - blur 证书编号（范围扩大）
    "cert-bachelor-degree.jpg": {
        "type": "cert",
        "src": "certs/cert-bachelor-degree.jpg",
        "output": "certs/cert-bachelor-degree.jpg",
        "blur": [
            # 证书编号在底部，扩大范围
            {"name": "cert_no", "x1": 0.50, "y1": 0.88, "x2": 0.95, "y2": 0.99},
            # 也可能在右上角有编号
            {"name": "cert_no_2", "x1": 0.60, "y1": 0.02, "x2": 0.98, "y2": 0.12},
        ],
        "label": "工学学士学位证书",
        "desc": "中国石油大学（华东）机电工程学院，机械设计制造及其自动化专业，2005年",
    },
    # Personal photo
    "profile-lake.jpg": {
        "type": "photo",
        "src": "photos/profile-lake.jpg",
        "output": "photos/profile-lake.jpg",
        "blur": [],
        "label": "个人照",
        "desc": "东营",
    },
    # Certificate: CET-6 - blur 证书编号（范围扩大）
    "cert-cet6.jpg": {
        "type": "cert",
        "src": "certs/cert-cet6.jpg",
        "output": "certs/cert-cet6.jpg",
        "blur": [
            {"name": "cert_no", "x1": 0.0, "y1": 0.79, "x2": 0.48, "y2": 0.96},
        ],
        "label": "CET-6 大学英语六级",
        "desc": "2004年3月，成绩合格",
    },
    # Certificate: CET-4 - blur 证书编号（范围扩大）
    "cert-cet4.jpg": {
        "type": "cert",
        "src": "certs/cert-cet4.jpg",
        "output": "certs/cert-cet4.jpg",
        "blur": [
            {"name": "cert_no", "x1": 0.0, "y1": 0.79, "x2": 0.48, "y2": 0.96},
        ],
        "label": "CET-4 大学英语四级",
        "desc": "2003年3月，成绩合格",
    },
    # Work photo: Troester - 不需要脱敏，但可能需要缩放
    "troester-team.jpg": {
        "type": "experience",
        "src": "experience/troester-team.jpg",
        "output": "experience/troester-team.jpg",
        "blur": [],
        "label": "Troester 连续硫化生产线调试",
        "desc": "与德国Troester公司工程师合影，连续硫化生产线安装调试项目",
    },
}

WATERMARK_TEXT = "KOS | WANG JIRUI (Jerry) | 学术展示"

def get_font(size):
    """Try to find a suitable Chinese font."""
    fonts = [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for f in fonts:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                continue
    return ImageFont.load_default()

def add_watermark(img, text=WATERMARK_TEXT, opacity=30):
    """Add diagonal watermark overlay."""
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_size = max(12, min(w, h) // 35)
    font = get_font(font_size)

    # Draw diagonal repeated text
    spacing_x = w // 4
    spacing_y = h // 5
    angle = -25

    for row in range(-3, 8):
        for col in range(-2, 6):
            x = col * spacing_x
            y = row * spacing_y + (col % 2) * (spacing_y // 2)
            draw.text((x, y), text, font=font, fill=(255, 255, 255, opacity))

    # Also add thin diagonal lines
    for i in range(-5, 15):
        x0 = i * (w // 6)
        y0 = -h
        x1 = x0 + h
        y1 = h * 2
        draw.line([(x0, y0), (x1, y1)], fill=(255, 255, 255, opacity // 3), width=1)

    # Composite
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    result = Image.alpha_composite(img, overlay)
    return result.convert("RGB")

def blur_region(img, region):
    """Apply strong Gaussian blur to a region defined by percentages.
    Uses radius=25 for full desensitization — text becomes completely unreadable.
    """
    w, h = img.size
    x1 = int(region["x1"] * w)
    y1 = int(region["y1"] * h)
    x2 = int(region["x2"] * w)
    y2 = int(region["y2"] * h)

    # Expand region by 5% on all sides for safety margin
    expand_x = int(0.05 * (x2 - x1))
    expand_y = int(0.05 * (y2 - y1))
    x1 = max(0, x1 - expand_x)
    y1 = max(0, y1 - expand_y)
    x2 = min(w, x2 + expand_x)
    y2 = min(h, y2 + expand_y)

    if x2 <= x1 or y2 <= y1:
        return img

    # Crop, apply STRONG blur (radius=25), paste back
    crop = img.crop((x1, y1, x2, y2))
    blurred = crop.filter(ImageFilter.GaussianBlur(radius=25))
    img.paste(blurred, (x1, y1))
    return img

def process_image(filename, config):
    """Process a single image: load, blur, watermark, save."""
    src = os.path.join(INPUT_DIR, filename)
    dst = os.path.join(OUTPUT_BASE, config["output"])

    if not os.path.exists(src):
        print(f"  SKIP: source not found: {src}")
        return None

    # Load
    img = Image.open(src)
    if img.mode == "P":
        img = img.convert("RGB")
    elif img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    print(f"  Processing: {filename} ({img.size[0]}x{img.size[1]})")

    # Desensitize: blur sensitive regions
    for region in config.get("blur", []):
        img = blur_region(img, region)
        print(f"    -> Blurred: {region['name']}")

    # Watermark
    img = add_watermark(img)
    print(f"    -> Watermark added")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(dst), exist_ok=True)

    # Save (optimize for web)
    img.save(dst, quality=85, optimize=True)
    print(f"    -> Saved: {dst}")

    return {
        "src": config["output"],
        "label": config["label"],
        "desc": config["desc"],
        "type": config["type"],
        "size": img.size,
    }

def main():
    print("=" * 60)
    print("KOS 图片处理: 脱敏 + 水印")
    print("=" * 60)

    results = {}
    for filename, config in IMAGES.items():
        print(f"\n[{config['type'].upper()}] {config['label']}")
        info = process_image(filename, config)
        if info:
            results[filename] = info

    # Save metadata JSON
    import json
    meta_path = os.path.join(OUTPUT_BASE, "data", "images.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nMetadata saved: {meta_path}")

    print("\n" + "=" * 60)
    print(f"Done. Processed {len(results)}/{len(IMAGES)} images.")
    print("=" * 60)

if __name__ == "__main__":
    main()
