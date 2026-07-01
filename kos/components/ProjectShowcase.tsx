import type { Translation } from "@/lib/i18n";

interface ProjectShowcaseProps {
  t: Translation;
}

const projKeys = ["project1", "project2", "project3", "project4"] as const;

const projImages: Record<string, string> = {};

export default function ProjectShowcase({ t }: ProjectShowcaseProps) {
  return (
    <section className="section section-alt">
      <div className="container">
        <h2 className="section-title">{t.projects.title}</h2>
        <div className="projects-list">
          {projKeys.map((key) => {
            const proj = t.projects[key];
            const img = projImages[key];
            return (
              <div key={key} className="project-card">
                {img && (
                  <div className="project-image">
                    <img src={img} alt={proj.title} loading="lazy" />
                  </div>
                )}
                <h3 className="project-title">{proj.title}</h3>
                <p className="project-desc">{proj.desc}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
