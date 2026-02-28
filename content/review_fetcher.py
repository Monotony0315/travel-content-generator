"""Travel review intelligence fetcher.

- Brave Search: uses local rate-limited wrapper to avoid API quota/rate bursts.
- Fallback: Wikipedia summary (API) for destination context.
- Cache: writes short-lived JSON cache to avoid repeated calls.

Purpose: add a deterministic, non-blocking review layer used by travel blog generation.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger

from content.rate_limited_search import search_brave_rate_limited

CACHE_DIR = Path(__file__).parent.parent / "data" / "review_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_CACHE_TTL_SECONDS = 60 * 60 * 12  # 12h


def _cache_key(city: str, country: str, provider: str) -> str:
    import hashlib

    key = f"{provider}::{city.strip().lower()}::{country.strip().lower()}"
    return hashlib.md5(key.encode("utf-8")).hexdigest()


def _cache_path(city: str, country: str, provider: str) -> Path:
    return CACHE_DIR / f"{_cache_key(city, country, provider)}.json"


def _read_cache(city: str, country: str, provider: str) -> Optional[List[Dict]]:
    path = _cache_path(city, country, provider)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        age = time.time() - float(payload.get("timestamp", 0))
        if age <= _CACHE_TTL_SECONDS:
            rows = payload.get("results", [])
            if isinstance(rows, list) and rows:
                return rows
        return None
    except Exception as e:
        logger.warning(f"[review_fetcher] cache read failed: {e}")
        return None
    return None


def _write_cache(city: str, country: str, provider: str, rows: List[Dict]) -> None:
    if not rows:
        return
    path = _cache_path(city, country, provider)
    try:
        path.write_text(
            json.dumps({"timestamp": time.time(), "results": rows}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        logger.warning(f"[review_fetcher] cache write failed: {e}")


def _fetch_wikipedia_summary(city: str) -> Optional[Dict]:
    import urllib.error
    import urllib.parse
    import urllib.request

    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(city)}"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; travel-content-generator/1.0; +https://openclaw.ai)"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            summary = (data.get("extract") or "").strip()
            if not summary:
                return None
            return {
                "title": data.get("title") or f"{city} - Wikipedia",
                "source": "wikipedia",
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "snippet": summary[:1200],
            }
    except urllib.error.URLError as e:
        logger.warning(f"[review_fetcher] wikipedia failed (URL error): {e}")
    except Exception as e:
        logger.warning(f"[review_fetcher] wikipedia failed: {e}")
    return None


def _build_provider_rows(city: str, country: str, sources: List[str], limit: int) -> List[Dict]:
    rows: List[Dict] = []
    queries = [
        f"{city} 여행 후기 {country} 맛집 추천",
        f"{city} {country} 여행가이드 추천 포인트 후기",
        f"{country} {city} 여행 일정 블로그 리뷰",
    ]

    if "brave" in sources:
        brave_cached = _read_cache(city, country, "brave")
        if brave_cached:
            logger.info("[review_fetcher] using cached brave results")
            rows.extend(brave_cached)
        else:
            for q in queries:
                try:
                    results = search_brave_rate_limited(q, count=5)
                    for item in results[:3]:
                        title = (item.get("title") or "").strip()
                        url = (item.get("url") or "").strip()
                        desc = (item.get("description") or "").strip()
                        if not title and not desc:
                            continue
                        rows.append({
                            "source": "brave",
                            "query": q,
                            "title": title,
                            "url": url,
                            "snippet": desc[:500],
                            "provider": "search",
                        })
                    if len(rows) >= limit:
                        break
                except Exception as e:
                    logger.warning(f"[review_fetcher] brave search error for '{q}': {e}")
                    continue
            # Cache for next run if we got anything.
            if rows:
                _write_cache(city, country, "brave", rows)

    # De-duplicate by URL
    seen = set()
    deduped: List[Dict] = []
    for r in rows:
        key = r.get("url") or r.get("title")
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)

    # Fill remaining with fallback sources
    if len(deduped) < limit and "wikipedia" in sources:
        wiki = _fetch_wikipedia_summary(city)
        if wiki:
            deduped.append(wiki)

    if len(deduped) < limit:
        fallback = {
            "source": "fallback",
            "title": f"{city} 공식/여행 가이드 추천",
            "url": f"https://www.google.com/search?q={city}+{country}+travel+guide",
            "snippet": "검색 API 할당량 제한으로 검색 결과를 바로 받아오지 못했습니다. 지도/여행 가이드 공식 페이지를 대체 참고로 사용합니다.",
            "provider": "search",
        }
        deduped.append(fallback)

    return deduped[:limit]


def collect_travel_reviews(city: str, country: str, region: str = "", limit: int = 3) -> Dict:
    """Collect lightweight review intelligence for a city.

    Returns:
        {
            "source": "brave|fallback",
            "updated_at": timestamp,
            "items": [...]
        }
    """

    city = (city or "").strip()
    country = (country or "").strip()
    if not city:
        return {"source": "empty", "updated_at": time.time(), "items": []}

    # provider order: Brave -> Wikipedia -> fallback
    items = _build_provider_rows(city, country, ["brave", "wikipedia"], limit)
    source = "fallback"
    if any(item.get("source") == "brave" for item in items):
        source = "brave"
    elif any(item.get("source") == "wikipedia" for item in items):
        source = "wikipedia"
    elif items:
        source = "fallback"

    return {
        "source": source,
        "updated_at": time.time(),
        "region": region,
        "items": items,
    }
