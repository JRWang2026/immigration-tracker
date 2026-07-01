import type { Metadata } from "next";
import { getTranslation } from "@/lib/i18n";
import PageLayout from "@/components/PageLayout";
import IntelligenceDashboard from "@/components/IntelligenceDashboard";

export const metadata: Metadata = {
  title: "情报台 | SEEK NZ 绿名单岗位追踪",
  description:
    "由私人本地 Agent 驱动的 SEEK NZ 绿名单 Tier1 ICT 岗位实时追踪面板。每日自动扫描邮件，匹配 Database Administrator、Software Engineer 等绿名单职业，为新西兰技术移民提供数据支持。",
  openGraph: {
    title: "Intelligence Dashboard — SEEK NZ Green List Job Tracker",
    description:
      "Automated SEEK NZ Green List Tier 1 ICT job monitoring powered by a self-hosted Python agent.",
  },
};

export default function IntelligencePage() {
  const lang = "zh";
  const t = getTranslation(lang);

  return (
    <PageLayout lang={lang} t={t}>
      <IntelligenceDashboard />
    </PageLayout>
  );
}
