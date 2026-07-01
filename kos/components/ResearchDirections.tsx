import type { Translation } from "@/lib/i18n";

interface ResearchDirectionsProps {
  t: Translation;
}

const dirKeys = ["direction1", "direction2", "direction3"] as const;
const dirNumbers = ["01", "02", "03"];

export default function ResearchDirections({ t }: ResearchDirectionsProps) {
  return (
    <section className="section">
      <div className="container">
        <h2 className="section-title">{t.research.title}</h2>
        <div className="research-grid">
          {dirKeys.map((key, i) => {
            const dir = t.research[key];
            return (
              <div key={key} className="research-card">
                <span className="research-number">{dirNumbers[i]}</span>
                <h3 className="research-title">{dir.title}</h3>
                <p className="research-desc">{dir.desc}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
