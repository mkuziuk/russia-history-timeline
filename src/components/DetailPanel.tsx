import { useEffect, useRef } from "react";
import type { TimelineItem, TimelinePeriod } from "../types";

interface DetailPanelProps {
  item: TimelineItem;
  period: TimelinePeriod;
  onClose: () => void;
}

const typeLabels: Record<TimelineItem["type"], string> = {
  событие: "Событие",
  человек: "Человек",
  явление: "Явление",
  идея: "Идея",
};

const hasSpecificAttribution = (value: string) =>
  value && !value.startsWith("Отдельная иллюстрация не используется");

export default function DetailPanel({ item, period, onClose }: DetailPanelProps) {
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    closeButtonRef.current?.focus();
    document.addEventListener("keydown", handleKeyDown);

    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  return (
    <div className="detail-layer" role="presentation">
      <button className="detail-layer__scrim" type="button" aria-label="Закрыть описание" onClick={onClose} />
      <aside
        className="detail-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="detail-panel-title"
      >
        <div className="detail-panel__topline">
          <span className={`detail-panel__type detail-panel__type--${item.type}`}>
            {typeLabels[item.type]}
          </span>
          <button
            className="detail-panel__close"
            type="button"
            onClick={onClose}
            ref={closeButtonRef}
            aria-label="Закрыть"
          >
            ×
          </button>
        </div>
        <p className="detail-panel__period">{period.name}</p>
        <time className="detail-panel__date">{item.date}</time>
        <h2 id="detail-panel-title">{item.title}</h2>
        <p className="detail-panel__description">{item.full_description}</p>

        {hasSpecificAttribution(item.image_attribution) ? (
          <div className="detail-panel__note">
            <span>Изображение</span>
            <p>{item.image_attribution}</p>
          </div>
        ) : null}

        {item.sources.length > 0 ? (
          <div className="detail-panel__sources">
            <span>Источники</span>
            {item.sources.map((source, index) => (
              <a key={source} href={source} target="_blank" rel="noreferrer">
                Источник {index + 1}
              </a>
            ))}
          </div>
        ) : null}
      </aside>
    </div>
  );
}
