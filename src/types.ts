export type TimelineItemType = "событие" | "человек" | "явление" | "идея";

export interface TimelineItem {
  id: string;
  type: TimelineItemType;
  title: string;
  date: string;
  sort_year: number;
  short_description: string;
  full_description: string;
  image_query: string;
  image_attribution: string;
  sources: string[];
}

export interface TimelinePeriod {
  id: string;
  name: string;
  date_range: string;
  visual_theme: string;
  background_image: string;
  items: TimelineItem[];
}

export interface TimelineData {
  title: string;
  subtitle: string;
  language: "ru";
  periods: TimelinePeriod[];
}
