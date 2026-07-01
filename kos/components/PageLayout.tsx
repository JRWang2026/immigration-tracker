import type { Lang, Translation } from "@/lib/i18n";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

interface PageLayoutProps {
  lang: Lang;
  t: Translation;
  children: React.ReactNode;
}

export default function PageLayout({ lang, t, children }: PageLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar lang={lang} t={t} />
      <main className="flex-1">{children}</main>
      <Footer t={t} />
    </div>
  );
}
