"""External reference fetcher (Unsplash + Brave) with conservative rate limiting."""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List


class ReferenceFetcher:
    def __init__(self):
        self.unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY", "")
        self.brave_key = os.getenv("BRAVE_API_KEY", "")
        self.usage_file = Path(__file__).resolve().parents[1] / "data" / "api_usage.json"
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_usage(self) -> Dict:
        if self.usage_file.exists():
            return json.loads(self.usage_file.read_text(encoding="utf-8"))
        return {"unsplash": []}

    def _save_usage(self, usage: Dict):
        self.usage_file.write_text(json.dumps(usage, ensure_ascii=False, indent=2), encoding="utf-8")

    def _can_use_unsplash(self) -> bool:
        usage = self._load_usage()
        now = int(time.time())
        recent = [t for t in usage.get("unsplash", []) if now - t < 3600]
        usage["unsplash"] = recent
        self._save_usage(usage)
        return len(recent) < 7

    def _mark_unsplash(self):
        usage = self._load_usage()
        usage.setdefault("unsplash", []).append(int(time.time()))
        self._save_usage(usage)

    def get_photo(self, city: str, country: str) -> Dict:
        fallback = {
            "url": f"https://source.unsplash.com/featured/?{urllib.parse.quote(city + ' travel')}",
            "credit": "Unsplash",
        }
        if not self.unsplash_key or not self._can_use_unsplash():
            return fallback

        q = urllib.parse.quote(f"{city} {country} travel landmark")
        req = urllib.request.Request(
            f"https://api.unsplash.com/photos/random?query={q}&orientation=landscape",
            headers={"Authorization": f"Client-ID {self.unsplash_key}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as r:
                data = json.loads(r.read().decode("utf-8"))
            self._mark_unsplash()
            return {
                "url": data.get("urls", {}).get("regular", fallback["url"]),
                "credit": f"Photo by {data.get('user', {}).get('name', 'Unknown')} on Unsplash",
                "page": data.get("links", {}).get("html", ""),
            }
        except Exception:
            return fallback

    def get_blog_links(self, city: str, country: str) -> List[Dict]:
        query = f"{city} {country} travel itinerary blog"
        if not self.brave_key:
            return [
                {"title": f"{city} 여행 검색 결과", "url": f"https://www.google.com/search?q={urllib.parse.quote(query)}"}
            ]
        req = urllib.request.Request(
            f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count=3",
            headers={"X-Subscription-Token": self.brave_key},
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as r:
                data = json.loads(r.read().decode("utf-8"))
            out = []
            for x in data.get("web", {}).get("results", [])[:3]:
                out.append({"title": x.get("title", "참고 링크"), "url": x.get("url", "")})
            return out
        except Exception:
            return [
                {"title": f"{city} 여행 검색 결과", "url": f"https://www.google.com/search?q={urllib.parse.quote(query)}"}
            ]
