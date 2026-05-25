import type { TimelineItem } from "../types";
import type { CSSProperties } from "react";

interface TimelineCardProps {
  item: TimelineItem;
  index: number;
  onSelect: () => void;
}

const typeLabels: Record<TimelineItem["type"], string> = {
  событие: "Событие",
  человек: "Человек",
  явление: "Явление",
  идея: "Идея",
};

export default function TimelineCard({ item, index, onSelect }: TimelineCardProps) {
  return (
    <button
      className="timeline-card"
      type="button"
      onClick={onSelect}
      aria-label={`Открыть полное описание: ${item.title}`}
      style={{ "--delay": `${index * 90}ms` } as CSSProperties}
    >
      <div className="timeline-card__meta">
        <span className={`timeline-card__type timeline-card__type--${item.type}`}>
          {typeLabels[item.type]}
        </span>
        <time>{item.date}</time>
      </div>
      <h3>{item.title}</h3>
      <p>{item.short_description}</p>
      <span className="timeline-card__source">Открыть полное описание</span>
    </button>
  );
}
