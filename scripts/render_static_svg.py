#!/usr/bin/env python3
from __future__ import annotations

import base64
import html
import json
import mimetypes
import textwrap
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TIMELINE_PATH = ROOT / "data" / "timeline.json"
IMAGE_SOURCES_PATH = ROOT / "data" / "image_sources.json"
OUTPUT_PATH = ROOT / "output" / "timeline.svg"

WIDTH = 2400
MARGIN_X = 150
LINE_X = 205
CONTENT_X = 310
PERIOD_GAP = 120

TYPE_COLORS = {
    "событие": "#d7b46a",
    "человек": "#c98567",
    "явление": "#6f8c7a",
    "идея": "#9d554f",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def wrap(text: str, width: int) -> list[str]:
    return textwrap.wrap(text, width=width, break_long_words=False, replace_whitespace=False)


def image_data_uri(path_value: str) -> str | None:
    path = ROOT / path_value
    if not path.exists():
        return None
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def text_block(lines: list[str], x: int, y: int, size: int, fill: str, line_height: int, family: str = "Arial") -> str:
    if not lines:
        return ""
    tspans = [
        f'<tspan x="{x}" dy="{0 if index == 0 else line_height}">{esc(line)}</tspan>'
        for index, line in enumerate(lines)
    ]
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-family="{family}" letter-spacing="0">{"".join(tspans)}</text>'
    )


def period_image(period: dict[str, Any], x: int, y: int, width: int, height: int, clip_id: str) -> str:
    uri = image_data_uri(period.get("background_image", ""))
    if not uri:
        return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="#2b241b"/>'
    return (
        f'<clipPath id="{clip_id}"><rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8"/></clipPath>'
        f'<image href="{uri}" x="{x}" y="{y}" width="{width}" height="{height}" preserveAspectRatio="xMidYMid slice" clip-path="url(#{clip_id})" opacity="0.8"/>'
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="#11100d" opacity="0.28"/>'
    )


def source_note(image_sources: dict[str, Any]) -> str:
    sources = image_sources.get("sources", [])
    missing = image_sources.get("missing", [])
    parts: list[str] = []
    if sources:
        parts.append("Изображения: Wikimedia Commons и открытые источники.")
    if missing:
        parts.append("Часть фоновых материалов заменена локальными нейтральными панелями.")
    if not parts:
        parts.append("Фоновые панели созданы локально; ссылки на исторические источники сохранены в data/timeline.json.")
    return " ".join(parts)


def main() -> int:
    timeline = load_json(TIMELINE_PATH)
    image_sources = load_json(IMAGE_SOURCES_PATH) if IMAGE_SOURCES_PATH.exists() else {"sources": [], "missing": []}
    output: list[str] = []

    y = 150
    output.append(
        f'<text x="{MARGIN_X}" y="{y}" fill="#f3ead8" font-size="88" font-family="Georgia" letter-spacing="0">{esc(timeline["title"])}</text>'
    )
    y += 70
    output.append(text_block(wrap(timeline["subtitle"], 92), MARGIN_X, y, 34, "#cfc0a4", 48))
    y += 95
    output.append(
        '<rect x="150" y="315" width="2100" height="1" fill="#ead8b5" opacity="0.25"/>'
    )
    output.append(
        '<text x="150" y="380" fill="#d7b46a" font-size="28" font-family="Arial" letter-spacing="0">'
        "5 периодов · 20 элементов · события, люди, явления и идеи · описания 50-150 слов"
        "</text>"
    )
    y = 500

    for period_index, period in enumerate(timeline["periods"]):
        items = sorted(period["items"], key=lambda item: item["sort_year"])
        period_start = y
        image_h = 360
        output.append(period_image(period, CONTENT_X, y, 650, image_h, f"clip-period-{period_index}"))
        output.append(f'<circle cx="{LINE_X}" cy="{y + 34}" r="18" fill="#d7b46a"/>')
        output.append(f'<text x="{CONTENT_X + 720}" y="{y + 52}" fill="#d7b46a" font-size="32" font-family="Arial" letter-spacing="0">{esc(period["date_range"])}</text>')
        output.append(f'<text x="{CONTENT_X + 720}" y="{y + 130}" fill="#f3ead8" font-size="68" font-family="Georgia" letter-spacing="0">{esc(period["name"])}</text>')
        output.append(text_block(wrap(period["visual_theme"], 72), CONTENT_X + 720, y + 188, 30, "#b7aa92", 42))
        y += image_h + 54

        for item in items:
            card_y = y
            description_lines = wrap(item["full_description"], 118)
            source_lines = []
            if item.get("sources"):
                source_lines = ["Источники:"] + [
                    f"{source_index}. {source}"
                    for source_index, source in enumerate(item["sources"], start=1)
                ]
            source_y = card_y + 190 + len(description_lines) * 34
            item_height = max(300, source_y - card_y + 48 + len(source_lines) * 28)
            color = TYPE_COLORS[item["type"]]

            output.append(f'<rect x="{CONTENT_X}" y="{card_y}" width="1940" height="{item_height}" rx="8" fill="#181511" opacity="0.92"/>')
            output.append(f'<rect x="{CONTENT_X}" y="{card_y}" width="8" height="{item_height}" fill="{color}"/>')
            output.append(f'<circle cx="{LINE_X}" cy="{card_y + 42}" r="11" fill="{color}"/>')
            output.append(f'<text x="{CONTENT_X + 38}" y="{card_y + 54}" fill="{color}" font-size="26" font-family="Arial" letter-spacing="0">{esc(item["type"].upper())}</text>')
            output.append(f'<text x="{CONTENT_X + 1720}" y="{card_y + 54}" fill="#cfc0a4" font-size="28" font-family="Arial" text-anchor="end" letter-spacing="0">{esc(item["date"])}</text>')
            output.append(f'<text x="{CONTENT_X + 38}" y="{card_y + 116}" fill="#f3ead8" font-size="44" font-family="Georgia" letter-spacing="0">{esc(item["title"])}</text>')
            output.append(text_block(description_lines, CONTENT_X + 38, card_y + 170, 28, "#ddd1ba", 34))
            if source_lines:
                output.append(text_block(source_lines, CONTENT_X + 38, source_y, 21, "#9f927c", 28))
            y += item_height + 28

        output.append(f'<line x1="{LINE_X}" y1="{period_start + 58}" x2="{LINE_X}" y2="{y - 20}" stroke="#ead8b5" stroke-width="3" opacity="0.24"/>')
        y += PERIOD_GAP

    note_lines = wrap(source_note(image_sources), 132)
    output.append(text_block(note_lines, MARGIN_X, y, 24, "#9f927c", 34))
    y += len(note_lines) * 34 + 120

    height = y
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">'
        "<defs>"
        '<filter id="paper-noise"><feTurbulence type="fractalNoise" baseFrequency="0.72" numOctaves="3"/>'
        '<feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 .08"/></feComponentTransfer></filter>'
        "</defs>"
        '<rect width="100%" height="100%" fill="#11100d"/>'
        '<rect width="100%" height="100%" fill="#ead8b5" filter="url(#paper-noise)" opacity="0.22"/>'
        + "".join(output)
        + "</svg>\n"
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(svg, encoding="utf-8")
    print(f"SVG создан: {OUTPUT_PATH.relative_to(ROOT)} ({WIDTH} x {height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
