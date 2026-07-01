"use client";

import type { Translation } from "@/lib/i18n";

interface WorkingPapersProps {
  t: Translation;
}

const STATUS_COLORS: Record<string, string> = {
  concept: "#f59e0b",
  drafting: "#3b82f6",
  submitted: "#8b5cf6",
  published: "#10b981",
};

const STATUS_BG: Record<string, string> = {
  concept: "rgba(245,158,11,0.1)",
  drafting: "rgba(59,130,246,0.1)",
  submitted: "rgba(139,92,246,0.1)",
  published: "rgba(16,185,129,0.1)",
};

export default function WorkingPapers({ t }: WorkingPapersProps) {
  const { papers, statusLabel } = t.workingPapers;

  return (
    <section className="workingpapers-section">
      <div className="workingpapers-container">
        <h2 className="workingpapers-title">{t.workingPapers.title}</h2>
        <p className="workingpapers-subtitle">{t.workingPapers.subtitle}</p>

        <div className="workingpapers-grid">
          {papers.map((paper) => (
            <div key={paper.id} className="workingpapers-card">
              <div className="workingpapers-card-header">
                <span
                  className="workingpapers-badge"
                  style={{
                    color: STATUS_COLORS[paper.status],
                    background: STATUS_BG[paper.status],
                  }}
                >
                  {statusLabel[paper.status]}
                </span>
              </div>
              <h3 className="workingpapers-card-title">{paper.title}</h3>
              <p className="workingpapers-card-desc">{paper.desc}</p>
              <div className="workingpapers-card-footer">
                <span className="workingpapers-card-target">{paper.target}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
