import type { Metadata } from "next";
import { getTranslation } from "@/lib/i18n";
import PageLayout from "@/components/PageLayout";
import ResearchProposal from "@/components/ResearchProposal";

export const metadata: Metadata = {
  title: "Research Proposal | KOS",
  description:
    "Pre-study for German PhD Application: Competitive Intelligence Systems in the Digital Transformation of Manufacturing — patent text mining, knowledge graphs, and Python data analytics",
  openGraph: {
    title: "Research Proposal — Competitive Intelligence Systems | KOS",
    description:
      "Pre-study for German PhD Application: A framework for Competitive Intelligence Systems in manufacturing digital transformation",
  },
};

export default function ResearchPage() {
  const lang = "en";
  const t = getTranslation(lang);

  return (
    <PageLayout lang={lang} t={t}>
      <ResearchProposal t={t} lang="en" />
    </PageLayout>
  );
}
