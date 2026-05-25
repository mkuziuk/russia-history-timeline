#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TIMELINE_PATH = ROOT / "data" / "timeline.json"
IMAGE_SOURCES_PATH = ROOT / "data" / "image_sources.json"
OUTPUTS = [
    ROOT / "output" / "timeline.svg",
    ROOT / "output" / "timeline.pdf",
    ROOT / "output" / "timeline.png",
]

REQUIRED_TYPES = {"событие", "человек", "явление", "идея"}
BANNED_MAIN_TITLES = {
    "Крещение Руси",
    "Революция 1917 года",
    "Ленин",
    "Владимир Ленин",
    "Распад СССР",
    "Образование Российской Федерации",
    "Борис Ельцин",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-zА-Яа-яЁё0-9]+(?:[-–][A-Za-zА-Яа-яЁё0-9]+)?", text))


def validate(require_outputs: bool = False) -> list[str]:
    errors: list[str] = []
    timeline = load_json(TIMELINE_PATH)

    if timeline.get("language") != "ru":
        errors.append("Поле language должно быть ru.")

    periods = timeline.get("periods", [])
    if len(periods) != 5:
        errors.append(f"Ожидалось 5 периодов, найдено: {len(periods)}.")

    for period in periods:
        period_name = period.get("name", "Без названия")
        items = period.get("items", [])

        if len(items) < 4:
            errors.append(f"В периоде «{period_name}» меньше 4 элементов.")

        types = {item.get("type") for item in items}
        missing_types = REQUIRED_TYPES - types
        if missing_types:
            errors.append(f"В периоде «{period_name}» нет типов: {', '.join(sorted(missing_types))}.")

        sort_years = [item.get("sort_year") for item in items]
        if sort_years != sorted(sort_years):
            errors.append(f"В периоде «{period_name}» элементы не упорядочены по sort_year.")

        background = period.get("background_image", "")
        if not background:
            errors.append(f"У периода «{period_name}» не указан background_image.")
        elif not (ROOT / background).exists():
            errors.append(f"Файл изображения не найден: {background}.")

        for item in items:
            title = item.get("title", "")
            for field in ["id", "type", "title", "date", "short_description", "full_description", "image_query"]:
                if not item.get(field):
                    errors.append(f"В элементе «{title or item.get('id', 'без id')}» не заполнено поле {field}.")

            if title in BANNED_MAIN_TITLES:
                errors.append(f"Запрещенный очевидный элемент выбран как основной: «{title}».")

            if item.get("type") not in REQUIRED_TYPES:
                errors.append(f"Неизвестный тип элемента «{title}»: {item.get('type')}.")

            words = word_count(item.get("full_description", ""))
            if words < 50 or words > 150:
                errors.append(f"Описание «{title}» содержит {words} слов, требуется 50-150.")

            sources = item.get("sources", [])
            if not isinstance(sources, list) or not sources:
                errors.append(f"У элемента «{title}» нет ссылок на источники.")

    if IMAGE_SOURCES_PATH.exists():
        image_sources = load_json(IMAGE_SOURCES_PATH)
        if "sources" not in image_sources or "missing" not in image_sources:
            errors.append("data/image_sources.json должен содержать поля sources и missing.")
    else:
        errors.append("Не найден data/image_sources.json.")

    if require_outputs:
        for output in OUTPUTS:
            if not output.exists() or output.stat().st_size == 0:
                errors.append(f"Не создан выходной файл: {output.relative_to(ROOT)}.")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Проверка данных музейного таймлайна.")
    parser.add_argument("--require-outputs", action="store_true", help="Проверять SVG/PDF/PNG в output/.")
    args = parser.parse_args()

    errors = validate(require_outputs=args.require_outputs)
    if errors:
        print("Проверка не пройдена:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Проверка пройдена: структура, баланс типов, описания, изображения и источники соответствуют требованиям.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
