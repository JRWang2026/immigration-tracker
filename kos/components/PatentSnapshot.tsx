import type { Translation } from "@/lib/i18n";
import Link from "next/link";

interface PatentSnapshotProps {
  t: Translation;
  lang: "zh" | "en";
}

const icons = [
  <svg key="0" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="3" width="6" height="18" rx="1" />
    <rect x="16" y="8" width="6" height="13" rx="1" />
    <rect x="9" y="13" width="6" height="8" rx="1" />
  </svg>,
  <svg key="1" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z" />
    <line x1="7" y1="7" x2="7.01" y2="7" />
  </svg>,
  <svg key="2" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
    <polyline points="17 6 23 6 23 12" />
  </svg>,
];

export default function PatentSnapshot({ t, lang }: PatentSnapshotProps) {
  const basePath = lang === "en" ? "/en/patent/" : "/patent/";
  return (
    <section className="section section-alt">
      <div className="container">
        <h2 className="section-title">{t.patent.title}</h2>
        <div className="snapshot-grid">
          {t.patent.items.map((item, i) => {
            const href = item.anchor
              ? `${basePath}?anchor=${item.anchor}`
              : basePath;
            return (
              <Link key={i} href={href} className="snapshot-card snapshot-link">
                <div className="snapshot-icon">{icons[i]}</div>
                <p className="snapshot-text">{item.text}</p>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
}
