import type { Metadata } from "next";
import { getTranslation } from "@/lib/i18n";
import PageLayout from "@/components/PageLayout";
import CodeLab from "@/components/CodeLab";

export const metadata: Metadata = {
  title: "代码实验室 | KOS",
  description: "浏览器内运行 Python 代码 — API数据获取与JSON处理、专利文本挖掘演示",
};

export default function CodePage() {
  const lang = "zh";
  const t = getTranslation(lang);

  return (
    <PageLayout lang={lang} t={t}>
      <CodeLab t={t} />
    </PageLayout>
  );
}
