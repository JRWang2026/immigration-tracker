import type { Translation } from "@/lib/i18n";

interface TimelineProps {
  t: Translation;
}

export default function Timeline({ t }: TimelineProps) {
  const items = t.profile.timeline;
  const isZh = t.nav.home === "首页";

  return (
    <div className="timeline">
      {items.map((item, i) => (
        <div className="timeline-item" key={i}>
          <div className="timeline-marker">
            <div className="timeline-dot" />
          </div>
          <div className="timeline-card">
            <span className="timeline-period">{item.period}</span>
            <h4 className="timeline-title">{item.title}</h4>
            <p className="timeline-degree">{item.degree}</p>
            {item.note && (
              <p className="timeline-note">{item.note}</p>
            )}
            {item.badges.length > 0 && (
              <div className="timeline-badges">
                {item.badges.map((b) => (
                  <span key={b} className="timeline-badge">
                    {b}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
