import type { TimelineData } from "../types";

export function buildImageSearchPlan(data: TimelineData) {
  return data.periods.flatMap((period) =>
    period.items.map((item) => ({
      period: period.name,
      element: item.title,
      query: item.image_query,
    })),
  );
}
