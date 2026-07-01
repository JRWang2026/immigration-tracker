import type { Translation } from "@/lib/i18n";

interface ResearchProposalProps {
  t: Translation;
  lang: "zh" | "en";
}

export default function ResearchProposal({ t, lang }: ResearchProposalProps) {
  const page = t.researchPage;

  return (
    <section className="section">
      <div className="container">
        {/* Header */}
        <div className="rprop-header">
          <h1 className="rprop-title">{page.title}</h1>
          <p className="rprop-subtitle">{page.subtitle}</p>
          <div className="rprop-abstract">
            <p>{page.abstract}</p>
          </div>
        </div>

        {/* Target Universities */}
        <div className="rprop-targets">
          <span className="rprop-targets-label">
            {lang === "zh" ? "目标院校" : "Target Universities"}
          </span>
          <div className="rprop-targets-list">
            <span className="rprop-target-badge">TU Muenchen</span>
            <span className="rprop-target-badge">RWTH Aachen</span>
            <span className="rprop-target-badge">TU Berlin</span>
            <span className="rprop-target-badge">Uni Stuttgart</span>
          </div>
        </div>

        {/* Sections */}
        <div className="rprop-sections">
          {page.sections.map((section) => (
            <section key={section.id} id={section.id} className="rprop-section">
              <h2 className="rprop-section-title">{section.title}</h2>
              <div className="rprop-section-content">
                {section.content.split("\n\n").map((para, i) => (
                  <p key={i}>{para}</p>
                ))}
              </div>
            </section>
          ))}
        </div>

        {/* Download CTA */}
        <div className="rprop-cta">
          <p>
            {lang === "zh"
              ? "本页面为在线浏览版。如需完整 PDF 版本（含格式化引用与目录），请联系学术邮箱。"
              : "This page is the online version. For a complete PDF with formatted references and table of contents, please contact via academic email."}
          </p>
          <a href={`mailto:${t.profile.identity.email}`} className="hero-cta">
            {lang === "zh" ? "获取 PDF 版本" : "Request PDF"}
          </a>
        </div>
      </div>
    </section>
  );
}
