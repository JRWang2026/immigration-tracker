import { translations } from "@/lib/i18n";
import PageLayout from "@/components/PageLayout";
import HeroSection from "@/components/HeroSection";
import ProfileSection from "@/components/ProfileSection";
import PatentSnapshot from "@/components/PatentSnapshot";
import ResearchDirections from "@/components/ResearchDirections";
import CNKIAnalysis from "@/components/CNKIAnalysis";
import ProjectShowcase from "@/components/ProjectShowcase";
import WorkingPapers from "@/components/WorkingPapers";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: {
    template: "%s | KOS",
    default: "KOS — Knowledge Operating System",
  },
  description: "面向申博的个人研究交互平台——专利分析、代码实验室、3D展示、知识管理",
};

export default function ZhPage() {
  const t = translations.zh;

  return (
    <PageLayout lang="zh" t={t}>
      <HeroSection t={t} />
      <ProfileSection t={t} />
      <PatentSnapshot t={t} lang="zh" />
      <ResearchDirections t={t} />
      <CNKIAnalysis t={t} lang="zh" />
      <WorkingPapers t={t} />
      <ProjectShowcase t={t} />
    </PageLayout>
  );
}
