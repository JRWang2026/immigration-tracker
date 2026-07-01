import Link from "next/link";
import type { Lang, Translation } from "@/lib/i18n";
import { NAV_ITEMS } from "@/lib/site-config";

interface NavbarProps {
  lang: Lang;
  t: Translation;
}

function l(href: string, lang: Lang): string {
  const base = lang === "en" ? "/en" : "";
  if (href === "") return base || "/";
  return `${base}${href}/`;
}

export default function Navbar({ lang, t }: NavbarProps) {
  const otherLang: Lang = lang === "zh" ? "en" : "zh";
  // CloudStudio static server needs explicit index.html for subdirectories
  const otherUrl = otherLang === "en" ? "/en/index.html" : "/";

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <a href="/" className="navbar-brand">
          KOS
        </a>
        <nav className="navbar-links">
          {NAV_ITEMS.map((item) => (
            <Link key={item.key} href={l(item.href, lang)}>
              {t.nav[item.labelKey as keyof typeof t.nav]}
            </Link>
          ))}
        </nav>
        <Link href={otherUrl} className="navbar-lang">
          {t.nav.language}
        </Link>
      </div>
    </header>
  );
}
