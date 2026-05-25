#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_PATH = ROOT / "output" / "timeline.svg"
PDF_PATH = ROOT / "output" / "timeline.pdf"
PNG_PATH = ROOT / "output" / "timeline.png"


def ensure_svg() -> None:
    if SVG_PATH.exists() and SVG_PATH.stat().st_size > 0:
        return
    subprocess.run([sys.executable, str(ROOT / "scripts" / "render_static_svg.py")], check=True)


def main() -> int:
    ensure_svg()
    try:
        import cairosvg
    except ImportError:
        print(
            "Не установлен cairosvg. Создайте виртуальное окружение в проекте и установите зависимости:\n"
            "python3 -m venv .venv\n"
            "source .venv/bin/activate\n"
            "pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    cairosvg.svg2pdf(url=str(SVG_PATH), write_to=str(PDF_PATH))
    cairosvg.svg2png(url=str(SVG_PATH), write_to=str(PNG_PATH), output_width=3200)
    print(f"PDF создан: {PDF_PATH.relative_to(ROOT)}")
    print(f"PNG создан: {PNG_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
