import type { Metadata } from "next";
import { getTranslation } from "@/lib/i18n";
import PageLayout from "@/components/PageLayout";
import PatentVisualization from "@/components/PatentVisualization";

export const metadata: Metadata = {
  title: "Patent Landscape Analysis | KOS",
  description: "Manufacturing firm patent text mining — keyword cloud, inventor network, technology mapping",
};

export default function PatentEnPage() {
  const lang = "en";
  const t = getTranslation(lang);

  return (
    <PageLayout lang={lang} t={t}>
      <div className="container" style={{ paddingTop: "3rem", paddingBottom: "3rem" }}>
        <div style={{ textAlign: "center", marginBottom: "2.5rem" }}>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, color: "var(--slate-800)", marginBottom: "0.5rem" }}>
            {t.patent.title}
          </h1>
          <p style={{ color: "var(--slate-500)", fontSize: "1.05rem" }}>
            Data Source: Wanfang Data · China Patent Database · Automated Text Analysis
          </p>
        </div>
        <PatentVisualization lang={lang} t={t.patentPage} />
      </div>
    </PageLayout>
  );
}
