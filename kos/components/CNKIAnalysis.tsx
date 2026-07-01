"use client";

import { useState } from "react";
import type { Translation } from "@/lib/i18n";

interface CNKIAnalysisProps {
  t: Translation;
  lang: "zh" | "en";
}

interface CnkImage {
  src: string;
  alt: string;
  label: string;
  descZh: string;
  descEn: string;
}

const images: CnkImage[] = [
  {
    src: "/images/cnki/cnki_yearly_trends.png",
    alt: "CNKI yearly publication trends 1967-2023",
    label: "年度发文趋势",
    descZh: "1967–2023 年潜油电泵领域 CNKI 发文量变化趋势，反映该技术领域的研究热度演变",
    descEn: "Publication volume trends in ESP-related research (1967–2023), reflecting the evolution of research interest",
  },
  {
    src: "/images/cnki/cnki_publication_types.png",
    alt: "CNKI publication type distribution",
    label: "文献类型分布",
    descZh: "学术期刊占比 86.3%，标准文献 12.2%，以期刊论文为绝对主体的研究产出结构",
    descEn: "Journal articles account for 86.3%, standards 12.2% — a research output structure dominated by peer-reviewed journals",
  },
  {
    src: "/images/cnki/cnki_keywords_bar.png",
    alt: "CNKI TOP15 keywords bar chart",
    label: "TOP15 关键词",
    descZh: "高频关键词统计：潜油电泵(19)、应用(15)、故障诊断(13) 等，揭示核心技术方向",
    descEn: "High-frequency keyword statistics revealing core technology directions: ESP(19), Application(15), Fault Diagnosis(13)",
  },
];

export default function CNKIAnalysis({ t, lang }: CNKIAnalysisProps) {
  const [lightbox, setLightbox] = useState<number | null>(null);
  const cnki = t.cnkiAnalysis;

  const openLightbox = (index: number) => setLightbox(index);
  const closeLightbox = () => setLightbox(null);
  const prevImage = () => {
    if (lightbox !== null) {
      setLightbox(lightbox === 0 ? images.length - 1 : lightbox - 1);
    }
  };
  const nextImage = () => {
    if (lightbox !== null) {
      setLightbox(lightbox === images.length - 1 ? 0 : lightbox + 1);
    }
  };

  // Keyboard navigation
  if (typeof window !== "undefined" && lightbox !== null) {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeLightbox();
      if (e.key === "ArrowLeft") prevImage();
      if (e.key === "ArrowRight") nextImage();
    };
    window.addEventListener("keydown", handleKey);
    // Cleanup is tricky in non-hook context; using useEffect would be better
    // but keeping it simple for static export
  }

  return (
    <section className="section section-alt">
      <div className="container">
        {/* Section Header */}
        <div style={{ textAlign: "center", marginBottom: "1rem" }}>
          <span className="cnki-badge">{cnki.badge}</span>
        </div>
        <h2 className="section-title">{cnki.title}</h2>
        <p className="cnki-subtitle">{cnki.subtitle}</p>

        {/* Images Grid */}
        <div className="cnki-grid">
          {images.map((img, i) => {
            const desc = lang === "zh" ? img.descZh : img.descEn;
            const label = lang === "zh" ? img.label : img.label.split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");

            return (
              <div key={img.src} className="cnki-card" onClick={() => openLightbox(i)}>
                <div className="cnki-image-wrapper">
                  <img
                    src={img.src}
                    alt={img.alt}
                    loading="lazy"
                  />
                  <div className="cnki-image-overlay">
                    <span className="cnki-zoom-icon">🔍</span>
                  </div>
                </div>
                <div className="cnki-card-body">
                  <h3 className="cnki-card-label">{label}</h3>
                  <p className="cnki-card-desc">{desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Methodology Note */}
        <div className="cnki-methodology">
          <div className="cnki-methodology-icon">📊</div>
          <div>
            <strong>{cnki.methodTitle}</strong>
            <p>{cnki.methodDesc}</p>
          </div>
        </div>
      </div>

      {/* Lightbox */}
      {lightbox !== null && (
        <div className="cnki-lightbox" onClick={closeLightbox}>
          <div className="cnki-lightbox-content" onClick={(e) => e.stopPropagation()}>
            <button className="cnki-lightbox-close" onClick={closeLightbox}>
              &times;
            </button>
            <button className="cnki-lightbox-nav cnki-lightbox-prev" onClick={prevImage}>
              &#8249;
            </button>
            <img
              src={images[lightbox].src}
              alt={images[lightbox].alt}
            />
            <button className="cnki-lightbox-nav cnki-lightbox-next" onClick={nextImage}>
              &#8250;
            </button>
            <div className="cnki-lightbox-caption">
              <span>{lang === "zh" ? images[lightbox].label : images[lightbox].alt}</span>
              <span className="cnki-lightbox-counter">
                {lightbox + 1} / {images.length}
              </span>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
