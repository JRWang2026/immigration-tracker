import type { Metadata } from "next";
import { getTranslation } from "@/lib/i18n";
import PageLayout from "@/components/PageLayout";
import PatentVisualization from "@/components/PatentVisualization";

export const metadata: Metadata = {
  title: "专利全景分析 | KOS",
  description: "制造企业专利文本挖掘全景分析 — 技术词云、发明人合作网络、技术领域分布",
};

export default function PatentPage() {
  const lang = "zh";
  const t = getTranslation(lang);

  return (
    <PageLayout lang={lang} t={t}>
      <div className="container" style={{ paddingTop: "3rem", paddingBottom: "3rem" }}>
        <div style={{ textAlign: "center", marginBottom: "2.5rem" }}>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, color: "var(--slate-800)", marginBottom: "0.5rem" }}>
            {t.patent.title}
          </h1>
          <p style={{ color: "var(--slate-500)", fontSize: "1.05rem" }}>
            数据来源：万方数据 · 中国专利数据库 · 自动化文本分析
          </p>
        </div>
        <PatentVisualization lang={lang} t={t.patentPage} />
      </div>
    </PageLayout>
  );
}
