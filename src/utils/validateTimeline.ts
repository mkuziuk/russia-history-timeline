import type { TimelineData, TimelineItemType } from "../types";

const requiredTypes: TimelineItemType[] = ["событие", "человек", "явление", "идея"];

const countWords = (value: string) =>
  value
    .trim()
    .split(/\s+/)
    .filter(Boolean).length;

export function validateTimeline(data: TimelineData): string[] {
  const errors: string[] = [];

  if (data.language !== "ru") {
    errors.push("Язык данных должен быть ru.");
  }

  if (data.periods.length !== 5) {
    errors.push("В таймлайне должно быть ровно 5 исторических периодов.");
  }

  data.periods.forEach((period) => {
    if (period.items.length < 4) {
      errors.push(`В периоде «${period.name}» меньше четырех элементов.`);
    }

    const types = new Set(period.items.map((item) => item.type));
    requiredTypes.forEach((type) => {
      if (!types.has(type)) {
        errors.push(`В периоде «${period.name}» нет типа «${type}».`);
      }
    });

    period.items.forEach((item) => {
      const missing = [
        item.title,
        item.date,
        item.type,
        item.short_description,
        item.full_description,
      ].some((value) => !value);

      if (missing) {
        errors.push(`В элементе «${item.title || item.id}» не заполнены обязательные поля.`);
      }

      const words = countWords(item.full_description);
      if (words < 50 || words > 150) {
        errors.push(`Описание «${item.title}» содержит ${words} слов, требуется 50-150.`);
      }
    });
  });

  return errors;
}
