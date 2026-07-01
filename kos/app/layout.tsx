import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Jirui Wang — Competitive Intelligence & Manufacturing Digitalization | KOS",
    template: "%s | KOS",
  },
  description:
    "Jirui Wang (王吉锐) — ISTIC M.Sc. Candidate in Information Resource Management. Research focus: competitive intelligence systems in manufacturing digital transformation, patent text mining, knowledge organization. Targeting German PhD programs (TU München, RWTH Aachen, TU Berlin, Universität Stuttgart).",
  keywords: [
    "Jirui Wang",
    "王吉锐",
    "competitive intelligence",
    "manufacturing digital transformation",
    "patent text mining",
    "knowledge organization",
    "PhD application",
    "Germany",
    "ISTIC",
    "information science",
    "竞争情报",
    "制造业数字化转型",
    "专利分析",
  ],
  authors: [{ name: "Jirui Wang", url: "https://orcid.org/0009-0006-0528-3961" }],
  creator: "Jirui Wang",
  robots: "index, follow",
  openGraph: {
    type: "website",
    locale: "zh_CN",
    siteName: "KOS — Knowledge Operating System",
    title: "Jirui Wang — Competitive Intelligence & Manufacturing Digitalization",
    description:
      "ISTIC M.Sc. Candidate researching competitive intelligence systems for manufacturing. Targeting German PhD programs.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "KOS — Jirui Wang",
      },
    ],
  },
  alternates: {
    languages: {
      "zh-CN": "/",
      "en": "/en/",
    },
  },
  metadataBase: new URL("https://kos.studio"),
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
