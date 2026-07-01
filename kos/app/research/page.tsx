import type { Metadata } from "next";
import { getTranslation } from "@/lib/i18n";
import PageLayout from "@/components/PageLayout";
import ResearchProposal from "@/components/ResearchProposal";

export const metadata: Metadata = {
  title: "Research Proposal | KOS",
  description:
    "面向德国博士申请的预研究报告：制造业数字化转型中的竞争情报系统（Competitive Intelligence Systems in Manufacturing Digital Transformation）——专利文本挖掘、知识图谱与 Python 数据分析",
  openGraph: {
    title: "Research Proposal — Competitive Intelligence Systems | KOS",
    description:
      "面向德国博士申请的预研究报告：制造业数字化转型中的竞争情报系统框架",
  },
};

export default function ResearchPage() {
  const lang = "zh";
  const t = getTranslation(lang);

  return (
    <PageLayout lang={lang} t={t}>
      <ResearchProposal t={t} lang="zh" />
    </PageLayout>
  );
}
