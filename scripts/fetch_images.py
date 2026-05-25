#!/usr/bin/env python3
from __future__ import annotations

import json
import mimetypes
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TIMELINE_PATH = ROOT / "data" / "timeline.json"
IMAGE_SOURCES_PATH = ROOT / "data" / "image_sources.json"
IMAGES_DIR = ROOT / "public" / "images"

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "russia-history-timeline/1.0 (educational project; Wikimedia Commons image cache)"

PERIOD_QUERIES = {
    "ancient-rus": "Varangian routes map",
    "muscovite-state": "Sergius of Radonezh icon",
    "russian-empire": "Decembrist revolt 1825 painting",
    "ussr": "Yuri Gagarin 1961 public domain",
    "contemporary-russia": "Moscow International Business Center skyline",
}

PERIOD_FILES = {
    "ancient-rus": "File:Kievan Rus and trade routes in 10th century (ru).svg",
    "muscovite-state": "File:Sergius of Radonezh vita icon (17 c., Yaroslavl museum).jpg",
    "russian-empire": "File:Volkonsky-4 S G.jpg",
    "ussr": "File:Yuri Gagarin (1961) - Restoration.jpg",
    "contemporary-russia": "File:Moscow Skyline.jpg",
}

PERIOD_IMAGE_TITLES = {
    "ancient-rus": "Карта Киевской Руси и торговых путей X века",
    "muscovite-state": "Житийная икона Сергия Радонежского, XVII век",
    "russian-empire": "Портрет Сергея Григорьевича Волконского",
    "ussr": "Портрет Юрия Гагарина, 1961 год",
    "contemporary-russia": "Панорама современной Москвы",
}

KNOWN_CACHED_METADATA = {
    "russian-empire": {
        "local_filename": "public/images/russian-empire.jpg",
        "original_url": "https://commons.wikimedia.org/wiki/File:Volkonsky-4_S_G.jpg",
        "title": "Портрет Сергея Григорьевича Волконского",
        "author": "George Dawe",
        "license": "Public domain",
        "source_website": "Wikimedia Commons",
        "supports_period": "Российская империя",
        "supports_element": "Восстание декабристов",
        "query": "Decembrist revolt 1825 painting",
    },
    "ussr": {
        "local_filename": "public/images/ussr.jpg",
        "original_url": "https://commons.wikimedia.org/wiki/File:Yuri_Gagarin_(1961)_-_Restoration.jpg",
        "title": "Yuri Gagarin (1961) - Restoration",
        "author": "Arto Jousi; Suomen valokuvataiteen museo; Alma Media; restored by Adam Cuerden",
        "license": "Public domain",
        "source_website": "Wikimedia Commons",
        "supports_period": "СССР",
        "supports_element": "Первый полёт человека в космос",
        "query": "Yuri Gagarin 1961 public domain",
    },
}

SUPPORT_ITEM_IDS = {
    "ancient-rus": "varangians-greeks-route",
    "muscovite-state": "sergius-of-radonezh",
    "russian-empire": "decembrist-revolt",
    "ussr": "first-human-spaceflight",
    "contemporary-russia": "digital-everyday-platforms",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def request_json(url: str, params: dict[str, str]) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{query}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def clean_metadata(value: dict[str, Any] | None, fallback: str = "Не указано") -> str:
    if not value:
        return fallback
    text = value.get("value") or fallback
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if text.lower() in {"anonimous", "anonymous"}:
        return "анонимный автор"
    return text or fallback


def clean_title(metadata: dict[str, Any], fallback: str) -> str:
    title = clean_metadata(metadata.get("ObjectName"), fallback.replace("File:", ""))
    if "QS:" in title or len(title) > 140:
        title = fallback.replace("File:", "")
    return title


def support_item(period: dict[str, Any], period_id: str) -> dict[str, Any]:
    support_id = SUPPORT_ITEM_IDS.get(period_id)
    for item in period["items"]:
        if item["id"] == support_id:
            return item
    return period["items"][0]


def extension_from_url(url: str, mime: str | None) -> str:
    parsed = urllib.parse.urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".svg"}:
        return ".jpg" if suffix == ".jpeg" else suffix

    guessed = mimetypes.guess_extension(mime or "")
    if guessed in {".jpg", ".jpeg", ".png", ".webp", ".svg"}:
        return ".jpg" if guessed == ".jpeg" else guessed
    return ".jpg"


def search_commons(query: str) -> dict[str, Any] | None:
    payload = request_json(
        COMMONS_API,
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": "6",
            "gsrlimit": "8",
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|mime",
            "iiurlwidth": "1800",
            "format": "json",
        },
    )
    pages = payload.get("query", {}).get("pages", {})
    candidates = sorted(pages.values(), key=lambda page: page.get("index", 999))

    for page in candidates:
      image_info = (page.get("imageinfo") or [{}])[0]
      mime = image_info.get("mime", "")
      if not mime.startswith("image/"):
          continue
      if "thumburl" in image_info or "url" in image_info:
          return {
              "title": page.get("title", "Wikimedia Commons image"),
              "image_info": image_info,
          }
    return None


def fetch_commons_title(title: str) -> dict[str, Any] | None:
    payload = request_json(
        COMMONS_API,
        {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|mime",
            "iiurlwidth": "1800",
            "format": "json",
        },
    )
    pages = payload.get("query", {}).get("pages", {})
    page = next(iter(pages.values()), None)
    if not page or "missing" in page:
        return None
    image_info = (page.get("imageinfo") or [{}])[0]
    mime = image_info.get("mime", "")
    if not mime.startswith("image/"):
        return None
    return {
        "title": page.get("title", title),
        "image_info": image_info,
    }


def download(url: str, destination: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=35) as response:
        destination.write_bytes(response.read())


def main() -> int:
    timeline = load_json(TIMELINE_PATH)
    existing_sources = []
    if IMAGE_SOURCES_PATH.exists():
        existing_sources = load_json(IMAGE_SOURCES_PATH).get("sources", [])
    existing_by_period = {
        record.get("supports_period"): record
        for record in existing_sources
        if record.get("supports_period")
    }
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    source_records: list[dict[str, Any]] = []
    missing: list[str] = []

    for period in timeline["periods"]:
        period_id = period["id"]
        query = PERIOD_QUERIES.get(period_id) or period["items"][0]["image_query"]
        supported_item_id = SUPPORT_ITEM_IDS.get(period_id)
        for item in period["items"]:
            if item["id"] != supported_item_id:
                item["image_attribution"] = "Отдельная иллюстрация не используется; см. фон периода и ссылки на источники."
        print(f"Ищу изображение: {period['name']} — {query}")

        try:
            exact_title = PERIOD_FILES.get(period_id)
            result = fetch_commons_title(exact_title) if exact_title else None
            if not result:
                result = search_commons(query)
            if not result:
                missing.append(f"{period['name']}: подходящее изображение на Wikimedia Commons не найдено")
                continue

            info = result["image_info"]
            image_url = info.get("thumburl") or info.get("url")
            original_url = info.get("descriptionurl") or info.get("url")
            extension = extension_from_url(image_url, info.get("mime"))
            filename = f"{period_id}{extension}"
            destination = IMAGES_DIR / filename
            download(image_url, destination)

            period["background_image"] = f"public/images/{filename}"
            metadata = info.get("extmetadata", {})
            attribution = clean_metadata(metadata.get("Artist"))
            license_name = clean_metadata(metadata.get("LicenseShortName"), "Уточнить лицензию")
            supported_item = support_item(period, period_id)
            supported_item["image_attribution"] = f"{attribution}; {license_name}"

            source_records.append(
                {
                    "local_filename": f"public/images/{filename}",
                    "original_url": original_url,
                    "title": PERIOD_IMAGE_TITLES.get(period_id) or clean_title(metadata, result["title"]),
                    "author": attribution,
                    "license": license_name,
                    "source_website": "Wikimedia Commons",
                    "supports_period": period["name"],
                    "supports_element": supported_item["title"],
                    "query": query,
                }
            )
            print(f"Сохранено: public/images/{filename}")
        except Exception as exc:
            missing.append(f"{period['name']}: {exc}")
            print(f"Не удалось загрузить изображение для периода «{period['name']}»: {exc}", file=sys.stderr)

            existing_record = existing_by_period.get(period["name"])
            background_path = ROOT / period.get("background_image", "")
            known_record = KNOWN_CACHED_METADATA.get(period_id)
            if existing_record and background_path.exists():
                source_records.append(existing_record)
            elif known_record and (ROOT / known_record["local_filename"]).exists():
                source_records.append(known_record)

    write_json(TIMELINE_PATH, timeline)
    write_json(
        IMAGE_SOURCES_PATH,
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sources": source_records,
            "missing": missing,
        },
    )

    print(f"Готово. Источников сохранено: {len(source_records)}. Пропусков: {len(missing)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
