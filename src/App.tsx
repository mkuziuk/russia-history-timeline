import { useEffect, useMemo, useState } from "react";
import timelineData from "../data/timeline.json";
import DetailPanel from "./components/DetailPanel";
import Legend from "./components/Legend";
import ScrollBackground from "./components/ScrollBackground";
import TimelineSection from "./components/TimelineSection";
import type { TimelineData, TimelineItem, TimelinePeriod } from "./types";
import { validateTimeline } from "./utils/validateTimeline";

const data = timelineData as TimelineData;

export default function App() {
  const [activePeriodId, setActivePeriodId] = useState(data.periods[0].id);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [selectedDetail, setSelectedDetail] = useState<{
    period: TimelinePeriod;
    item: TimelineItem;
  } | null>(null);
  const validationErrors = useMemo(() => validateTimeline(data), []);

  const handleSelectItem = (period: TimelinePeriod, item: TimelineItem) => {
    setSelectedDetail({ period, item });
  };

  const handleCloseDetail = () => {
    setSelectedDetail(null);
  };

  useEffect(() => {
    const sections = Array.from(document.querySelectorAll<HTMLElement>("[data-period-id]"));
    let frameId: number | null = null;

    const updateActivePeriod = () => {
      frameId = null;
      const markerY = window.innerHeight * 0.45;
      let closestPeriodId = data.periods[0].id;
      let closestDistance = Number.POSITIVE_INFINITY;

      for (const section of sections) {
        const rect = section.getBoundingClientRect();
        const periodId = section.dataset.periodId || data.periods[0].id;

        if (rect.top <= markerY && rect.bottom >= markerY) {
          closestPeriodId = periodId;
          break;
        }

        const distance = Math.min(Math.abs(rect.top - markerY), Math.abs(rect.bottom - markerY));
        if (distance < closestDistance) {
          closestDistance = distance;
          closestPeriodId = periodId;
        }
      }

      setActivePeriodId((currentPeriodId) =>
        currentPeriodId === closestPeriodId ? currentPeriodId : closestPeriodId,
      );
    };

    const scheduleUpdate = () => {
      if (frameId !== null) {
        return;
      }
      frameId = window.requestAnimationFrame(updateActivePeriod);
    };

    scheduleUpdate();
    window.addEventListener("scroll", scheduleUpdate, { passive: true });
    window.addEventListener("resize", scheduleUpdate);

    return () => {
      if (frameId !== null) {
        window.cancelAnimationFrame(frameId);
      }
      window.removeEventListener("scroll", scheduleUpdate);
      window.removeEventListener("resize", scheduleUpdate);
    };
  }, []);

  useEffect(() => {
    const cards = Array.from(document.querySelectorAll<HTMLElement>(".timeline-card"));
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("timeline-card--visible");
          }
        });
      },
      { threshold: 0.28 },
    );

    cards.forEach((card) => observer.observe(card));
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const updateProgress = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      setScrollProgress(max <= 0 ? 0 : window.scrollY / max);
    };

    updateProgress();
    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("resize", updateProgress);

    return () => {
      window.removeEventListener("scroll", updateProgress);
      window.removeEventListener("resize", updateProgress);
    };
  }, []);

  useEffect(() => {
    document.body.classList.toggle("detail-open", selectedDetail !== null);
    return () => document.body.classList.remove("detail-open");
  }, [selectedDetail]);

  if (validationErrors.length > 0) {
    return (
      <main className="validation-screen">
        <h1>Таймлайн требует исправления</h1>
        <ul>
          {validationErrors.map((error) => (
            <li key={error}>{error}</li>
          ))}
        </ul>
      </main>
    );
  }

  return (
    <>
      <ScrollBackground periods={data.periods} activePeriodId={activePeriodId} />
      <div className="timeline-progress" aria-hidden="true">
        <span style={{ transform: `scaleY(${scrollProgress})` }} />
      </div>
      <header className="site-header">
        <a href="#timeline" className="site-header__brand">
          Музейная лента
        </a>
        <Legend />
      </header>
      <main>
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero__content">
            <p className="hero__kicker">История России</p>
            <h1 id="hero-title">{data.title}</h1>
            <p>{data.subtitle}</p>
          </div>
        </section>
        <div id="timeline" className="timeline-shell">
          {data.periods.map((period, index) => (
            <TimelineSection
              key={period.id}
              period={period}
              index={index}
              onSelectItem={handleSelectItem}
            />
          ))}
        </div>
      </main>
      <footer className="site-footer">
        <p>Создано: Mikhail Kuziuk</p>
      </footer>
      {selectedDetail ? (
        <DetailPanel
          period={selectedDetail.period}
          item={selectedDetail.item}
          onClose={handleCloseDetail}
        />
      ) : null}
    </>
  );
}
