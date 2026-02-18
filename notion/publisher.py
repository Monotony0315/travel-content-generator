"""
Notion Publisher - Blog Style
Notion 발행 모듈 (블로그 스타일 고급 포맷)
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger


class NotionPublisher:
    """Notion 블로그 스타일 발행기"""

    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2025-09-03"

    def __init__(self):
        self.api_key = os.getenv("NOTION_API_KEY", "")
        self.database_id = os.getenv("NOTION_DATABASE_ID", "")
        self.parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID", "")
        self.enabled = bool(self.api_key and (self.database_id or self.parent_page_id))

        if not self.api_key:
            logger.warning("Notion API Key not configured")
        if self.api_key and not (self.database_id or self.parent_page_id):
            logger.warning("NOTION_DATABASE_ID or NOTION_PARENT_PAGE_ID is required for real publishing")

    def _request(self, method: str, path: str, payload: Optional[Dict] = None) -> Dict:
        url = f"{self.BASE_URL}{path}"
        data = None
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        req = urllib.request.Request(
            url=url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": self.NOTION_VERSION,
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Notion API error {e.code}: {body}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Notion API connection error: {e}") from e

    def validate_connection(self) -> Dict:
        """토큰 유효성 + 접근 가능한 리소스 확인"""
        if not self.api_key:
            return {"ok": False, "reason": "NOTION_API_KEY missing"}

        result = self._request("POST", "/search", {"page_size": 3})
        return {
            "ok": True,
            "result_count": len(result.get("results", [])),
            "has_more": result.get("has_more", False),
        }

    async def publish_travel_guide(self, content: Dict) -> str:
        """여행 가이드를 Notion에 블로그 스타일로 발행"""
        destination = content["destination"]
        city = destination["name"]
        country = destination["country"]

        logger.info(f"Publishing {city} guide to Notion (blog style)...")

        if not self.enabled:
            mock_url = f"https://notion.so/travel-guide-{city.lower().replace(' ', '-')}"
            logger.warning("Notion real publish disabled, returning mock URL")
            return mock_url

        days = content.get('itinerary', {}).get('days', destination.get('recommended_days', 5))
        title = f"{datetime.now().strftime('%Y-%m-%d')} | {city}, {country} | {days}일"
        
        # Create page first
        if self.database_id:
            payload = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Name": {"title": [{"type": "text", "text": {"content": title}}]}
                },
            }
        else:
            payload = {
                "parent": {"page_id": self.parent_page_id},
                "properties": {
                    "title": {"title": [{"type": "text", "text": {"content": title}}]}
                },
            }

        page = self._request("POST", "/pages", payload)
        page_url = page.get("url", "")
        page_id = page.get("id", "")
        
        if not page_url or not page_id:
            raise RuntimeError("Notion page created but URL/ID missing")

        # Add content blocks
        children = self._build_blog_blocks(content)
        self._request("PATCH", f"/blocks/{page_id}/children", {"children": children})

        return page_url

    def _rt(self, text: str, link: Optional[str] = None) -> List[Dict]:
        text = str(text)
        if len(text) <= 1900:
            item = {"type": "text", "text": {"content": text}}
            if link:
                item["text"]["link"] = {"url": link}
            return [item]
        chunks = [text[i:i + 1900] for i in range(0, len(text), 1900)]
        return [{"type": "text", "text": {"content": c}} for c in chunks]

    def _paragraph(self, text: str, link: Optional[str] = None) -> Dict:
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": self._rt(text, link)},
        }

    def _heading(self, level: int, text: str) -> Dict:
        t = f"heading_{level}"
        return {
            "object": "block",
            "type": t,
            t: {"rich_text": self._rt(text)},
        }

    def _quote(self, text: str) -> Dict:
        return {
            "object": "block",
            "type": "quote",
            "quote": {"rich_text": self._rt(text)},
        }

    def _callout(self, text: str, icon: str = "💡") -> Dict:
        return {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": self._rt(text),
                "icon": {"type": "emoji", "emoji": icon},
            },
        }

    def _divider(self) -> Dict:
        return {"object": "block", "type": "divider", "divider": {}}

    def _toggle(self, title: str, children: List[Dict]) -> Dict:
        return {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": self._rt(title),
                "children": children[:10],  # Toggle children limit
            },
        }

    def _image_external(self, url: str, caption: str = "") -> Dict:
        block = {
            "object": "block",
            "type": "image",
            "image": {"type": "external", "external": {"url": url}},
        }
        if caption:
            block["image"]["caption"] = [{"type": "text", "text": {"content": caption}}]
        return block

    def _bookmark(self, url: str) -> Dict:
        return {
            "object": "block",
            "type": "bookmark",
            "bookmark": {"url": url},
        }

    def _bullets(self, items: List[str]) -> List[Dict]:
        out = []
        for item in items:
            out.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": self._rt(item)},
            })
        return out

    def _build_blog_blocks(self, content: Dict) -> List[Dict]:
        d = content["destination"]
        itinerary = content["itinerary"]
        restaurants = content["restaurants"]
        tips = content["tips"]
        refs = content.get("references", {})

        blocks: List[Dict] = []

        # Cover Image
        photo = refs.get("photo", {})
        if photo.get("url"):
            blocks.append(self._image_external(
                photo["url"], 
                f"{d['name']} 대표 이미지 - {photo.get('credit', 'Unsplash')}"
            ))
            blocks.append(self._divider())

        # Title & Intro
        blocks.append(self._heading(1, f"{d['name']}, {d['country']} 여행 가이드"))
        blocks.append(self._quote(itinerary.get("intro", "")))
        blocks.append(self._paragraph(f"📅 {content['generated_at'][:10]} · {itinerary['days']}일 일정"))
        blocks.append(self._divider())

        # Daily Itinerary
        blocks.append(self._heading(2, "여행 일정"))
        for day in itinerary.get("days_plan", []):
            # Day header with toggle
            day_children = [
                self._callout(day.get("narrative", ""), "📝"),
                self._heading(3, "오전"),
                self._paragraph(day["morning"]["activity"]),
                self._bookmark(day["morning"]["google_maps"]),
                self._heading(3, "오후"),
                self._paragraph(day["afternoon"]["activity"]),
                self._bookmark(day["afternoon"]["google_maps"]),
                self._heading(3, "저녁"),
                self._paragraph(day["evening"]["activity"]),
                self._bookmark(day["evening"]["google_maps"]),
                self._callout(day["parking"]["tip"], "🚗"),
                self._bookmark(day["parking"]["google_maps"]),
            ]
            blocks.append(self._toggle(f"Day {day['day']}: {day['theme']}", day_children))
        
        blocks.append(self._divider())

        # Restaurants
        blocks.append(self._heading(2, "맛집 추천 10선"))
        
        for grade, icon, title in [("budget", "💰", "가성비 맛집"), 
                                    ("standard", "⭐", "일반 맛집"), 
                                    ("premium", "👑", "고급 맛집")]:
            blocks.append(self._heading(3, f"{icon} {title}"))
            for p in restaurants.get(grade, []):
                rest_children = [
                    self._paragraph(f"타입: {p.get('type', '레스토랑')}"),
                    self._paragraph(f"시그니처: {p.get('signature', '')}"),
                    self._callout(p["description"], "💡"),
                    self._bookmark(p["google_maps"]),
                    self._callout(f"주차: {p['parking']['guide']}", "🅿️"),
                    self._bookmark(p["parking"]["google_maps"]),
                ]
                blocks.append(self._toggle(f"{p['name']} ({p['price']})", rest_children))
        
        blocks.append(self._divider())

        # Tips
        blocks.append(self._heading(2, "여행 꿀팁"))
        blocks.append(self._callout(tips.get("voice", ""), "✈️"))
        
        tips_data = [
            ("🚇 이동 전략", tips.get('transportation', {}).get('city_transport', '')),
            ("🚗 렌트카 팁", tips.get('transportation', {}).get('car_rental', '')),
            ("🅿️ 주차 전략", tips.get('driving_and_parking', {}).get('parking_strategy', '')),
            ("💰 예산", tips.get('money', {}).get('budget', '')),
        ]
        
        for tip_title, tip_content in tips_data:
            if tip_content:
                blocks.append(self._callout(f"{tip_title}: {tip_content}", "💡"))
        
        # Safety tips
        for s in tips.get("safety", {}).get("tips", []):
            blocks.append(self._callout(s, "⚠️"))
        
        # Parking/Rental links
        blocks.append(self._heading(3, "주차/렌트카 링크"))
        blocks.append(self._bookmark(tips.get('driving_and_parking', {}).get('maps_parking', '')))
        blocks.append(self._bookmark(tips.get('driving_and_parking', {}).get('maps_rental', '')))
        
        blocks.append(self._divider())

        # Reference Links
        links = refs.get("blog_links", [])
        if links:
            blocks.append(self._heading(2, "참고 링크"))
            for l in links:
                blocks.append(self._bookmark(l.get('url', '')))

        return blocks[:95]
