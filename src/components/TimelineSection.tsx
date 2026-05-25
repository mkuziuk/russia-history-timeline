import type { TimelineItem, TimelinePeriod } from "../types";
import TimelineCard from "./TimelineCard";

interface TimelineSectionProps {
  period: TimelinePeriod;
  index: number;
  onSelectItem: (period: TimelinePeriod, item: TimelineItem) => void;
}

const typeOrder: Record<TimelineItem["type"], number> = {
  событие: 0,
  человек: 1,
  явление: 2,
  идея: 3,
};

export default function TimelineSection({ period, index, onSelectItem }: TimelineSectionProps) {
  const sortedItems = [...period.items].sort((a, b) => {
    const typeDifference = typeOrder[a.type] - typeOrder[b.type];
    return typeDifference || a.sort_year - b.sort_year;
  });

  return (
    <section
      className="period-section"
      id={period.id}
      data-period-id={period.id}
      aria-labelledby={`${period.id}-title`}
    >
      <div className="period-section__number">{String(index + 1).padStart(2, "0")}</div>
      <div className="period-section__intro">
        <p className="period-section__range">{period.date_range}</p>
        <h2 id={`${period.id}-title`}>{period.name}</h2>
        <p className="period-section__theme">{period.visual_theme}</p>
      </div>
      <div className="period-section__cards">
        {sortedItems.map((item, itemIndex) => (
          <TimelineCard
            key={item.id}
            item={item}
            index={itemIndex}
            onSelect={() => onSelectItem(period, item)}
          />
        ))}
      </div>
    </section>
  );
}
