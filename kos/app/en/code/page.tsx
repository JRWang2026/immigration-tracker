import type { Metadata } from "next";
import { getTranslation } from "@/lib/i18n";
import PageLayout from "@/components/PageLayout";
import CodeLab from "@/components/CodeLab";

export const metadata: Metadata = {
  title: "Code Lab | KOS",
  description: "Run Python in the browser — API data fetching with JSON processing and patent text mining demos",
};

export default function CodeEnPage() {
  const lang = "en";
  const t = getTranslation(lang);

  return (
    <PageLayout lang={lang} t={t}>
      <CodeLab t={t} />
    </PageLayout>
  );
}
