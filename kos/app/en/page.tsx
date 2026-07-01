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
  description:
    "Personal research platform for PhD applications — patent analysis, code lab, 3D viewer, knowledge management",
};

export default function EnPage() {
  const t = translations.en;

  return (
    <PageLayout lang="en" t={t}>
      <HeroSection t={t} />
      <ProfileSection t={t} />
      <PatentSnapshot t={t} lang="en" />
      <ResearchDirections t={t} />
      <CNKIAnalysis t={t} lang="en" />
      <WorkingPapers t={t} />
      <ProjectShowcase t={t} />
    </PageLayout>
  );
}
