import type { Metadata } from "next";
import { getTranslation } from "@/lib/i18n";
import PageLayout from "@/components/PageLayout";
import IntelligenceDashboard from "@/components/IntelligenceDashboard";

export const metadata: Metadata = {
  title: "Intelligence | SEEK NZ Green List Job Tracker",
  description:
    "Real-time SEEK NZ Green List Tier 1 ICT job tracker powered by a self-hosted Python agent. Daily email scanning for Green List occupations including Database Administrator, Software Engineer, and Systems Administrator.",
  openGraph: {
    title: "Intelligence Dashboard — SEEK NZ Green List Job Tracker",
    description:
      "Automated SEEK NZ Green List Tier 1 ICT job monitoring powered by a self-hosted Python agent.",
  },
};

export default function EnIntelligencePage() {
  const lang = "en";
  const t = getTranslation(lang);

  return (
    <PageLayout lang={lang} t={t}>
      <IntelligenceDashboard />
    </PageLayout>
  );
}
