import type { TimelineItemType } from "../types";

const entries: { type: TimelineItemType; label: string }[] = [
  { type: "событие", label: "События" },
  { type: "человек", label: "Люди" },
  { type: "явление", label: "Явления" },
  { type: "идея", label: "Идеи" },
];

export default function Legend() {
  return (
    <nav className="legend" aria-label="Типы элементов">
      {entries.map((entry) => (
        <span key={entry.type} className="legend__item">
          <span className={`legend__dot legend__dot--${entry.type}`} />
          {entry.label}
        </span>
      ))}
    </nav>
  );
}
