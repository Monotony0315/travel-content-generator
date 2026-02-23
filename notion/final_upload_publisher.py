"""
Final Notion Publisher with Direct Image Upload
Optimizes images (resize 1920x1080 max, compress 200-500KB) and uploads to Notion with attribution
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.error
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger
from pathlib import Path

# Import our upload publisher
from notion.upload_publisher import upload_publisher


class FinalUploadPublisher:
    """
    Final publisher that:
    1. Downloads images from APIs
    2. Optimizes them (resize to max 1920x1080, compress to 200-500KB)
    3. Creates Notion page with image blocks
    4. Adds proper attribution captions (required for copyright)
    """

    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"

    def __init__(self):
        self.api_key = os.getenv("NOTION_API_KEY", "")
        self.parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID", "30a20a81-386f-8092-80dc-f6639dbccbf1")
        self.enabled = bool(self.api_key and self.parent_page_id)

    def _maps_url(self, query: str) -> str:
        return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query)}"

    def _request(self, method: str, path: str, payload: Optional[Dict] = None) -> Dict:
        url = f"{self.BASE_URL}{path}"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload else None

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
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Notion API error {e.code}: {body}") from e

    async def publish_blog(self, content: Dict, images: List[Dict]) -> str:
        """Publish blog with optimized images and attribution"""
        import random

        dest = content["destination"]
        city = dest["name"]
        country = dest.get("country", "")

        # Create unique title
        unique_suffix = random.randint(1000, 9999)
        title = f"{datetime.now().strftime('%Y-%m-%d')} | {city}, {country} | {dest['days']}일 가이드 #{unique_suffix}"

        logger.info(f"\n{'='*70}")
        logger.info(f"CREATING NOTION PAGE: {title}")
        logger.info(f"{'='*70}")

        # Step 1: Process images (download, optimize)
        logger.info("\n[1/4] Processing images (download + optimize)...")
        processed_images = upload_publisher.process_and_upload_images(images, city)

        if not processed_images:
            logger.error("No images were successfully processed")
            raise RuntimeError("Image processing failed")

        logger.info(f"✅ Processed {len(processed_images)} images")
        for img in processed_images:
            logger.info(f"   - {img['size_kb']:.1f}KB | {img['attribution']}")

        # Step 2: Create Notion page
        logger.info("\n[2/4] Creating Notion page...")
        payload = {
            "parent": {"page_id": self.parent_page_id},
            "properties": {
                "title": {"title": [{"type": "text", "text": {"content": title}}]}
            },
        }

        page = self._request("POST", "/pages", payload)
        page_id = page.get("id", "")
        page_url = page.get("url", "")

        if not page_id:
            raise RuntimeError("Failed to create Notion page")

        logger.info(f"✅ Page created: {page_url}")

        # Step 3: Build blocks with optimized images
        logger.info("\n[3/4] Building content blocks with images...")
        blocks = self._build_blocks(content, processed_images, city)

        # Step 4: Add blocks in batches
        logger.info("\n[4/4] Adding blocks to page...")
        batch_size = 90
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]
            self._request("PATCH", f"/blocks/{page_id}/children", {"children": batch})
            logger.info(f"   Added blocks {i+1} to {min(i+len(batch), len(blocks))} of {len(blocks)}")

        # Cleanup temp files
        upload_publisher.cleanup_temp_files(city)

        logger.info(f"\n{'='*70}")
        logger.info(f"✅ PUBLISHED SUCCESSFULLY!")
        logger.info(f"{'='*70}")
        logger.info(f"URL: {page_url}")

        return page_url

    def _rt(self, text: str, bold: bool = False, link: Optional[str] = None, color: Optional[str] = None) -> List[Dict]:
        item = {"type": "text", "text": {"content": str(text)[:1900]}}
        if bold:
            item["annotations"] = {"bold": True}
        if link:
            item["text"]["link"] = {"url": link}
        if color:
            item.setdefault("annotations", {})["color"] = color
        return [item]

    def _heading(self, level: int, text: str) -> Dict:
        t = f"heading_{level}"
        return {"object": "block", "type": t, t: {"rich_text": self._rt(text)}}

    def _paragraph(self, text: str, bold: bool = False, link: Optional[str] = None) -> Dict:
        return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": self._rt(text, bold, link)}}

    def _quote(self, text: str) -> Dict:
        return {"object": "block", "type": "quote", "quote": {"rich_text": self._rt(text)}}

    def _callout(self, text: str, icon: str = "", color: str = "default") -> Dict:
        block = {
            "object": "block",
            "type": "callout",
            "callout": {"rich_text": self._rt(text), "color": color},
        }
        if icon:
            block["callout"]["icon"] = {"type": "emoji", "emoji": icon}
        return block

    def _divider(self) -> Dict:
        return {"object": "block", "type": "divider", "divider": {}}

    def _image_block(self, image_data: Dict, caption_override: str = "") -> Dict:
        """Create image block with attribution caption"""
        original_url = image_data.get("original_url", "")
        attribution = caption_override or image_data.get("attribution", "")

        block = {
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {"url": original_url},
            },
        }

        if attribution:
            block["image"]["caption"] = [
                {"type": "text", "text": {"content": attribution}}
            ]

        return block

    def _build_blocks(self, content: Dict, images: List[Dict], city: str) -> List[Dict]:
        """Build all blocks for the Notion page"""
        dest = content["destination"]
        blocks = []

        days_plan = content.get("days_plan", [])
        logger.info(f"[DEBUG] Building blocks: {len(images)} images, {len(days_plan)} days")

        # Hero Image (first image)
        if images:
            blocks.append(self._image_block(images[0], f"{city} - {images[0].get('attribution', '')}"))
            logger.info(f"[DEBUG] Added Hero image with attribution")

        # Title Section
        blocks.append(self._heading(1, f"{city} 여행 완벽 가이드"))
        blocks.append(self._paragraph(f"{dest['days']}일 일정 | {dest['best_season']} 추천 | 통화: {dest['currency']}", bold=True))
        blocks.append(self._divider())

        # Introduction
        blocks.append(self._quote(content.get("intro", "")))
        blocks.append(self._divider())

        # Hotels Section
        blocks.append(self._heading(2, "🏨 추천 호텔"))
        hotels = content.get("hotels", {})

        for cat, label, color in [
            ("budget", "💰 가성비 호텔", "green"),
            ("luxury", "👑 고급 호텔", "purple")
        ]:
            hotel_list = hotels.get(cat, [])
            if not hotel_list:
                continue
            blocks.append(self._callout(label, "", f"{color}_background"))
            for h in hotel_list[:3]:  # Limit to 3 hotels per category
                blocks.append(self._heading(3, f"{h['name']} (★{h['rating']})"))
                blocks.append(self._paragraph(f"💵 {h['price_per_night']} | 📍 {h['area']}"))
                blocks.append(self._paragraph(f"✅ {h['pros']}"))
                blocks.append(self._paragraph(f"⚠️ {h['cons']}"))
                maps_url = self._maps_url(f"{h['name']} {city}")
                blocks.append(self._paragraph(f"📍 지도에서 보기", link=maps_url))

        blocks.append(self._divider())

        # Daily Itinerary with Images
        blocks.append(self._heading(2, "📅 일정 상세"))

        for idx, day in enumerate(days_plan):
            day_num = day.get("day", idx + 1)
            image_idx = idx + 1  # Hero is 0, Day 1 is 1, etc.

            # Day Image (if available)
            if len(images) > image_idx:
                img = images[image_idx]
                caption = f"Day {day_num} - {img.get('attribution', '')}"
                blocks.append(self._image_block(img, caption))
                logger.info(f"[DEBUG] Added Day {day_num} image with attribution")

            # Day Header
            blocks.append(self._callout(f"Day {day_num}: {day['title']}", "📍", "blue_background"))
            blocks.append(self._paragraph(f"🎯 테마: {day['theme']}", bold=True))

            # Day Content
            content_text = day.get("content", "").strip()
            for para in content_text.split('\n\n'):
                if para.strip():
                    blocks.append(self._paragraph(para.strip()))

            # Spots with inline links
            spots = day.get("spots", [])
            if spots:
                blocks.append(self._heading(3, "🎯 주요 장소"))
                for spot in spots[:5]:  # Limit to 5 spots
                    name = spot['name']
                    desc = spot['desc']
                    tip = spot.get('tip', '')
                    maps_url = self._maps_url(f"{name} {city}")
                    reservation_url = spot.get('reservation_url', '')
                    reservation_required = spot.get('reservation_required', False)

                    para = {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"type": "text", "text": {"content": "• "}},
                                {"type": "text", "text": {"content": name, "link": {"url": maps_url}}, "annotations": {"bold": True}},
                                {"type": "text", "text": {"content": f": {desc}"}},
                            ]
                        }
                    }
                    blocks.append(para)

                    if tip:
                        blocks.append(self._paragraph(f"   💡 {tip}"))

                    if reservation_required and reservation_url:
                        res_para = {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {"type": "text", "text": {"content": "   🎫 예약 필요: "}},
                                    {"type": "text", "text": {"content": "예약하러 가기", "link": {"url": reservation_url}}, "annotations": {"bold": True, "color": "red"}},
                                ]
                            }
                        }
                        blocks.append(res_para)

            # Restaurants
            restaurants = day.get("restaurants", [])
            if restaurants:
                blocks.append(self._heading(3, "🍽️ 추천 식당"))
                for r in restaurants[:3]:  # Limit to 3 restaurants
                    name = r['name']
                    price = r.get('price', '')
                    tip = r.get('tip', '')
                    maps_url = self._maps_url(f"{name} {city}")
                    reservation_url = r.get('reservation_url', '')
                    reservation_required = r.get('reservation_required', False)

                    para = {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"type": "text", "text": {"content": "• "}},
                                {"type": "text", "text": {"content": name, "link": {"url": maps_url}}, "annotations": {"bold": True}},
                                {"type": "text", "text": {"content": f" ({price}) - {tip}"}},
                            ]
                        }
                    }
                    blocks.append(para)

                    if reservation_required and reservation_url:
                        res_para = {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {"type": "text", "text": {"content": "   🎫 예약: "}},
                                    {"type": "text", "text": {"content": "예약하러 가기", "link": {"url": reservation_url}}, "annotations": {"bold": True, "color": "orange"}},
                                ]
                            }
                        }
                        blocks.append(res_para)

            # Daily Cost
            cost = day.get("estimated_cost", {})
            if cost and cost.get("total"):
                blocks.append(self._callout(f"💰 예상 비용: {cost['total']}", "", "yellow_background"))

            blocks.append(self._divider())

        # Transport Section
        blocks.append(self._heading(2, "🚇 교통 및 이동"))
        transport = content.get("transport_summary", {})
        for mode, price in transport.items():
            emoji = {"metro": "🚇", "bus": "🚌", "taxi": "🚕", "airport": "✈️", "car": "🚗"}.get(mode, "🚊")
            blocks.append(self._paragraph(f"{emoji} {mode}: {price}"))

        # Parking info
        if dest.get("car_rental_available"):
            parking = content.get("parking_info", {})
            if parking:
                blocks.append(self._heading(3, "🅿️ 주차 정보"))
                blocks.append(self._paragraph(f"주차 난이도: {parking.get('difficulty', '')}"))
                blocks.append(self._paragraph(f"도심 요금: {parking.get('city_center_rate', '')}"))

                pr_locations = parking.get("pr_locations", [])
                if pr_locations:
                    blocks.append(self._paragraph("추천 P+R 주차장:", bold=True))
                    for pr in pr_locations[:2]:
                        maps_url = self._maps_url(f"{pr['name']} {city}")
                        para = {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {"type": "text", "text": {"content": "• "}},
                                    {"type": "text", "text": {"content": pr['name'], "link": {"url": maps_url}}},
                                    {"type": "text", "text": {"content": f": {pr['rate']} ({pr['metro']})"}},
                                ]
                            }
                        }
                        blocks.append(para)

        blocks.append(self._divider())

        # Total Cost Summary
        blocks.append(self._heading(2, "💵 총 예상 비용"))
        estimates = content.get("total_estimate", {})

        for level in ["budget", "luxury"]:
            est = estimates.get(level, {})
            if not est:
                continue
            label = "💰 가성비 여행" if level == "budget" else "👑 럭셔리 여행"
            color = "green" if level == "budget" else "purple"

            blocks.append(self._callout(label, "", f"{color}_background"))
            for key, val in est.items():
                if key != "total":
                    blocks.append(self._paragraph(f"• {key}: {val}"))
            if est.get("total"):
                blocks.append(self._paragraph(f"**총계: {est['total']}**", bold=True))

        blocks.append(self._divider())

        # Emergency Contacts
        blocks.append(self._heading(2, "🚨 비상연락망 & 대사관 정보"))
        final_summary = content.get("final_summary", {})
        emergency = final_summary.get("emergency_contacts", {})
        embassy = final_summary.get("embassy_info", {})

        if emergency:
            blocks.append(self._callout("긴급 신고번호", "🚨", "red_background"))
            emergency_labels = {
                "police": "👮 경찰",
                "ambulance": "🚑 구급차",
                "fire": "🚒 소방",
                "general": "📞 유럽 통합신고"
            }
            for key, val in emergency.items():
                label = emergency_labels.get(key, key)
                blocks.append(self._paragraph(f"{label}: {val}"))

        if embassy:
            blocks.append(self._callout("주재국 한국대사관", "🏛️", "blue_background"))

            if embassy.get("name"):
                blocks.append(self._paragraph(f"{embassy['name']}", bold=True))
            if embassy.get("phone"):
                blocks.append(self._paragraph(f"📞 전화: {embassy['phone']}"))
            if embassy.get("address"):
                blocks.append(self._paragraph(f"📍 주소: {embassy['address']}"))
            if embassy.get("hours"):
                blocks.append(self._paragraph(f"🕐 영업시간: {embassy['hours']}"))
            if embassy.get("email"):
                blocks.append(self._paragraph(f"✉️ 이메일: {embassy['email']}"))
            if embassy.get("website"):
                para = {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "🌐 웹사이트: "}},
                            {"type": "text", "text": {"content": "대사관 홈페이지 방문", "link": {"url": embassy['website']}}, "annotations": {"bold": True, "color": "blue"}},
                        ]
                    }
                }
                blocks.append(para)
            if embassy.get("emergency_phone"):
                blocks.append(self._paragraph(f"🆘 24시간 긴급연락처: {embassy['emergency_phone']}", bold=True))

        # Tips
        blocks.append(self._callout("💡 위급 시 참고사항", "", "yellow_background"))
        blocks.append(self._paragraph("• 여권 분실 시 즉시 대사관에 신고하세요"))
        blocks.append(self._paragraph("• 신용카드 분실 시 즉시 카드사에 정지 요청하세요"))
        blocks.append(self._paragraph("• 유럽 통합신고번호 112는 영어로도 응대합니다"))
        blocks.append(self._paragraph("• 한국 외교부 24시간 영사콜센터: +82-2-3210-0404"))

        blocks.append(self._divider())

        # SEO Section
        blocks.append(self._heading(2, "🏷️ 해시태그 & SEO"))
        seo = content.get("seo", {})

        if seo.get("hashtags"):
            hashtags = seo["hashtags"]
            blocks.append(self._callout("추천 해시태그", "#️⃣", "yellow_background"))
            for i in range(0, min(len(hashtags), 15), 5):
                group = hashtags[i:i+5]
                blocks.append(self._paragraph(" ".join(group)))

        if seo.get("keywords"):
            blocks.append(self._callout("SEO 키워드", "🔍", "gray_background"))
            blocks.append(self._paragraph(", ".join(seo["keywords"][:15])))

        if seo.get("meta_description"):
            blocks.append(self._callout("메타 설명", "📝", "purple_background"))
            blocks.append(self._paragraph(seo["meta_description"]))

        blocks.append(self._divider())

        # Image Attribution Summary
        blocks.append(self._heading(2, "📸 이미지 출처"))
        blocks.append(self._paragraph("본 페이지의 모든 이미지는 다음과 같은 출처에서 제공되었습니다:"))
        for i, img in enumerate(images, 1):
            attr = img.get("attribution", "Unknown source")
            blocks.append(self._paragraph(f"{i}. {attr}"))

        blocks.append(self._divider())

        # Footer
        blocks.append(self._paragraph(f"📝 작성일: {content.get('generated_at', datetime.now().isoformat())[:10]}"))
        blocks.append(self._paragraph("✈️ 안전하고 즐거운 여행 되세요!"))

        return blocks


# Singleton instance
final_upload_publisher = FinalUploadPublisher()
