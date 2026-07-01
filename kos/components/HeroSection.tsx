import type { Translation } from "@/lib/i18n";

interface HeroSectionProps {
  t: Translation;
}

export default function HeroSection({ t }: HeroSectionProps) {
  return (
    <section className="hero">
      <div className="hero-blur hero-blur-1" />
      <div className="hero-blur hero-blur-2" />
      <div className="hero-inner">
        <div className="hero-avatar">
          <img src="/photos/avatar.jpg" alt="Profile" />
        </div>
        <p className="hero-greeting">{t.hero.greeting}</p>
        <h1 className="hero-title">{t.hero.title}</h1>
        <p className="hero-subtitle">{t.hero.subtitle}</p>
        <p className="hero-tagline">{t.hero.tagline}</p>
        <a href="#profile" className="hero-cta">
          {t.hero.cta}
        </a>
      </div>
    </section>
  );
}
