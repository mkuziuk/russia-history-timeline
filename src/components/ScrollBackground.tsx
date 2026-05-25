import type { TimelinePeriod } from "../types";

interface ScrollBackgroundProps {
  periods: TimelinePeriod[];
  activePeriodId: string;
}

const publicPath = (value: string) => {
  const relativePath = value.replace(/^public\//, "");
  const basePath = import.meta.env.BASE_URL.endsWith("/")
    ? import.meta.env.BASE_URL
    : `${import.meta.env.BASE_URL}/`;
  return `${basePath}${relativePath}`;
};

export default function ScrollBackground({ periods, activePeriodId }: ScrollBackgroundProps) {
  return (
    <div className="scroll-background" aria-hidden="true">
      {periods.map((period) => (
        <div
          key={period.id}
          className={`scroll-background__image ${
            period.id === activePeriodId ? "scroll-background__image--active" : ""
          }`}
          style={{ backgroundImage: `url("${publicPath(period.background_image)}")` }}
        />
      ))}
      <div className="scroll-background__grain" />
      <div className="scroll-background__shade" />
    </div>
  );
}
