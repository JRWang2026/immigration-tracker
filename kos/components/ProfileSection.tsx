import type { Translation } from "@/lib/i18n";
import Timeline from "./Timeline";

interface ProfileSectionProps {
  t: Translation;
}

export default function ProfileSection({ t }: ProfileSectionProps) {
  const p = t.profile;

  return (
    <section id="profile" className="section">
      <div className="container">
        <h2 className="section-title">{p.title}</h2>

        <div className="profile-bio">
          <p>{p.bio}</p>
        </div>

        <div className="profile-grid">
          <div className="profile-card profile-card-wide">
            <h3 className="profile-card-title">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              {t.nav.home === "首页" ? "学术与职业历程" : "Career & Education"}
            </h3>
            <Timeline t={t} />
          </div>

          <div className="profile-card">
            <h3 className="profile-card-title">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="2" y1="12" x2="22" y2="12"/>
                <path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>
              </svg>
              {t.nav.home === "首页" ? "语言能力" : "Languages"}
            </h3>
            <ul className="profile-lang-list">
              {p.languages.map((lang) => (
                <li key={lang.language} className="profile-lang-item">
                  <span className="profile-lang-name">{lang.language}</span>
                  <span className="profile-lang-level">{lang.level}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="profile-card">
            <h3 className="profile-card-title">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
              {p.identity.title}
            </h3>
            <ul className="profile-lang-list">
              <li className="profile-lang-item">
                <span className="profile-lang-name">{p.identity.labelEmail}</span>
                <a href={`mailto:${p.identity.email}`} className="profile-identity-link">{p.identity.email}</a>
              </li>
              <li className="profile-lang-item">
                <span className="profile-lang-name">{p.identity.labelOrcid}</span>
                <a href={p.identity.orcidUrl} target="_blank" rel="noopener noreferrer" className="profile-identity-link profile-orcid-link">
                  {p.identity.orcid}
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
