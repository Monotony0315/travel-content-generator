"""
Final Enhanced Notion Publisher
인라인 링크 + 일자별 이미지 + 호텔/비용 정보 포함
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


class FinalNotionPublisher:
    """최종 버전 - 인라인 링크 + 일자별 이미지 + 모든 정보 펼쳐서 표시"""

    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2025-09-03"

    def __init__(self):
        self.api_key = os.getenv("NOTION_API_KEY", "")
        # Use new parent page ID (updated 2026-02-18 - permissions granted)
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
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Notion API error {e.code}: {body}") from e

    async def publish_blog(self, content: Dict, images: List[Dict]) -> str:
        """최종 블로그 발행"""
        import random
        dest = content["destination"]
        city = dest["name"]
        country = dest.get("country", "")
        
        # Unique title with timestamp + random suffix to avoid conflicts
        unique_suffix = random.randint(1000, 9999)
        title = f"{datetime.now().strftime('%Y-%m-%d')} | {city}, {country} | {dest['days']}일 가이드 #{unique_suffix}"

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

        blocks = self._build_final_blocks(content, images, city)
        
        # Add blocks in batches (Notion API limit: 100 blocks per request)
        batch_size = 90  # 90개씩 나눠서 전송 (안전마진)
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]
            self._request("PATCH", f"/blocks/{page_id}/children", {"children": batch})
            logger.info(f"Added blocks {i+1} to {min(i+len(batch), len(blocks))} of {len(blocks)}")
        
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

    def _image_external(self, url: str, caption: str = "") -> Dict:
        block = {
            "object": "block",
            "type": "image",
            "image": {"type": "external", "external": {"url": url}},
        }
        if caption:
            block["image"]["caption"] = [{"type": "text", "text": {"content": caption}}]
        return block

    def _build_final_blocks(self, content: Dict, images: List[Dict], city: str) -> List[Dict]:
        """최종 블록 구성 - 인라인 링크 + 일자별 이미지"""
        dest = content["destination"]
        blocks = []
        
        # 디버깅: 이미지 개수와 일정 개수 확인
        days_plan = content.get("days_plan", [])
        logger.info(f"[DEBUG] 총 이미지 수: {len(images)}, 총 일정 수: {len(days_plan)}")
        
        # Hero Image
        if images:
            blocks.append(self._image_external(images[0]["url"], f"{city} 대표 이미지"))
            logger.info(f"[DEBUG] Hero 이미지 추가: idx=0")
        
        # Title
        blocks.append(self._heading(1, f"{city} 여행 완벽 가이드"))
        blocks.append(self._paragraph(f"{dest['days']}일 일정 | {dest['best_season']} 추천 | 통화: {dest['currency']}", bold=True))
        blocks.append(self._divider())
        
        # Intro
        blocks.append(self._quote(content.get("intro", "")))
        blocks.append(self._divider())
        
        # HOTELS Section
        blocks.append(self._heading(2, "추천 호텔"))
        hotels = content.get("hotels", {})
        
        for cat, label, color in [("budget", "가성비 호텔", "green"), ("luxury", "고급 호텔", "purple")]:
            hotel_list = hotels.get(cat, [])
            if not hotel_list:
                continue
            blocks.append(self._callout(label, "", f"{color}_background"))
            for h in hotel_list:
                blocks.append(self._heading(3, f"{h['name']} (★{h['rating']})"))
                blocks.append(self._paragraph(f"가격: {h['price_per_night']} | 위치: {h['area']}"))
                blocks.append(self._paragraph(f"장점: {h['pros']}"))
                blocks.append(self._paragraph(f"단점: {h['cons']}"))
                # 인라인 링크
                blocks.append(self._paragraph(f"📍 지도 보기: ", link=h['maps_url']))
        
        blocks.append(self._divider())
        
        # DAILY ITINERARY - with inline links
        blocks.append(self._heading(2, "일정 상세"))
        
        for idx, day in enumerate(content.get("days_plan", [])):
            day_num = day.get("day", idx + 1)
            
            # Day image (if available) - 이미지 인덱스: Hero(0), Day1(1), Day2(2), Day3(3), Day4(4), Day5(5)
            image_idx = idx + 1  # idx 0 → Day 1 uses images[1], idx 1 → Day 2 uses images[2], etc.
            logger.info(f"[DEBUG] Day {day_num} 처리 중: idx={idx}, image_idx={image_idx}, images_len={len(images)}")
            
            if len(images) > image_idx and images[image_idx].get("url"):
                img_url = images[image_idx]["url"]
                # URL 검증 및 디버그 로깅
                logger.info(f"[DEBUG] ✅ Day {day_num} 이미지 추가: idx={image_idx}, url={img_url[:60]}...")
                blocks.append(self._image_external(img_url, f"Day {day_num} - {city}"))
            else:
                logger.warning(f"[DEBUG] ❌ Day {day_num} 이미지 없음: idx={image_idx}, len(images)={len(images)}")
            
            # Day header
            blocks.append(self._callout(f"Day {day_num}: {day['title']}", "", "blue_background"))
            blocks.append(self._paragraph(f"테마: {day['theme']}", bold=True))
            
            # Day content - clean paragraphs (ALL content, not limited)
            content_text = day.get("content", "").strip()
            for para in content_text.split('\n\n'):
                if para.strip():
                    blocks.append(self._paragraph(para.strip()))
            
            # Spots with inline links
            spots = day.get("spots", [])
            if spots:
                blocks.append(self._heading(3, "주요 장소"))
                for spot in spots:
                    name = spot['name']
                    desc = spot['desc']
                    tip = spot.get('tip', '')
                    maps_url = self._maps_url(f"{name} {city}")
                    reservation_url = spot.get('reservation_url', '')
                    reservation_required = spot.get('reservation_required', False)
                    reservation_note = spot.get('reservation_note', '')
                    
                    # 인라인 링크: 장소명을 클릭하면 구글맵
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
                    
                    # 예약 링크 추가
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
                        if reservation_note:
                            blocks.append(self._paragraph(f"   📌 {reservation_note}"))
            
            # Restaurants with inline links
            restaurants = day.get("restaurants", [])
            if restaurants:
                blocks.append(self._heading(3, "추천 식당"))
                for r in restaurants:
                    name = r['name']
                    price = r.get('price', '')
                    tip = r.get('tip', '')
                    maps_url = self._maps_url(f"{name} {city}")
                    reservation_url = r.get('reservation_url', '')
                    reservation_required = r.get('reservation_required', False)
                    reservation_note = r.get('reservation_note', '')
                    
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
                    
                    # 예약 링크 추가
                    if reservation_required:
                        if reservation_url:
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
                        if reservation_note:
                            blocks.append(self._paragraph(f"   📌 {reservation_note}"))
            
            # Daily cost
            cost = day.get("estimated_cost", {})
            if cost:
                blocks.append(self._callout(f"예상 비용: {cost.get('total', '')}", "", "yellow_background"))
            
            blocks.append(self._divider())
        
        # TRANSPORT & PARKING
        blocks.append(self._heading(2, "교통 및 이동"))
        transport = content.get("transport_summary", {})
        for mode, price in transport.items():
            blocks.append(self._paragraph(f"{mode}: {price}"))
        
        # Parking info (if car rental available)
        if dest.get("car_rental_available"):
            parking = content.get("parking_info", {})
            if parking:
                blocks.append(self._heading(3, "주차 정보"))
                blocks.append(self._paragraph(f"주차 난이도: {parking.get('difficulty', '')}"))
                blocks.append(self._paragraph(f"도심 요금: {parking.get('city_center_rate', '')}"))
                
                pr_locations = parking.get("pr_locations", [])
                if pr_locations:
                    blocks.append(self._paragraph("추천 P+R 주차장:", bold=True))
                    for pr in pr_locations:
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
        
        # TOTAL COST SUMMARY
        blocks.append(self._heading(2, "총 예상 비용"))
        estimates = content.get("total_estimate", {})
        
        for level in ["budget", "luxury"]:
            est = estimates.get(level, {})
            label = "가성비 여행" if level == "budget" else "럭셔리 여행"
            color = "green" if level == "budget" else "purple"
            
            blocks.append(self._callout(label, "", f"{color}_background"))
            for key, val in est.items():
                if key != "total":
                    blocks.append(self._paragraph(f"• {key}: {val}"))
            if est.get("total"):
                blocks.append(self._paragraph(f"총계: {est['total']}", bold=True))
        
        blocks.append(self._divider())
        
        # EMERGENCY CONTACTS - Enhanced Section
        blocks.append(self._heading(2, "🚨 비상연락망 & 대사관 정보"))
        
        final_summary = content.get("final_summary", {})
        emergency = final_summary.get("emergency_contacts", {})
        embassy = final_summary.get("embassy_info", {})
        
        if emergency:
            blocks.append(self._callout("긴급 신고번호", "🚨", "red_background"))
            for key, val in emergency.items():
                label = {
                    "police": "👮 경찰",
                    "ambulance": "🚑 구급차", 
                    "fire": "🚒 소방",
                    "general": "📞 유럽 통합신고"
                }.get(key, key)
                blocks.append(self._paragraph(f"{label}: {val}"))
        
        if embassy:
            blocks.append(self._callout("주재국 한국대사관", "🏛️", "blue_background"))
            
            # 대사관 기본 정보
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
            
            # 긴급 연락처
            if embassy.get("emergency_phone"):
                blocks.append(self._paragraph(f"🆘 24시간 긴급연락처: {embassy['emergency_phone']}", bold=True))
            
            # 주요 업무
            if embassy.get("services"):
                blocks.append(self._heading(3, "주요 업무"))
                for svc in embassy["services"]:
                    blocks.append(self._paragraph(f"• {svc}"))
        
        # 추가 팁
        blocks.append(self._callout("💡 위급 시 참고사항", "", "yellow_background"))
        blocks.append(self._paragraph("• 여권 분실 시 즉시 대사관에 신고하세요"))
        blocks.append(self._paragraph("• 신용카드 분실 시 즉시 카드사에 정지 요청하세요"))
        blocks.append(self._paragraph("• 유럽 통합신고번호 112는 영어로도 응대합니다"))
        blocks.append(self._paragraph("• 한국 외교부 24시간 영사콜센터: +82-2-3210-0404"))
        
        blocks.append(self._divider())
        
        # SEO & HASHTAGS Section
        blocks.append(self._divider())
        blocks.append(self._heading(2, "🏷️ 해시태그 & SEO"))
        
        seo = content.get("seo", {})
        if seo:
            # 해시태그
            hashtags = seo.get("hashtags", [])
            if hashtags:
                blocks.append(self._callout("추천 해시태그", "#️⃣", "yellow_background"))
                # 5개씩 그룹화하여 표시
                for i in range(0, len(hashtags), 5):
                    group = hashtags[i:i+5]
                    blocks.append(self._paragraph(" ".join(group)))
            
            # SEO 키워드
            keywords = seo.get("keywords", [])
            if keywords:
                blocks.append(self._callout("SEO 키워드", "🔍", "gray_background"))
                blocks.append(self._paragraph(", ".join(keywords[:15])))  # 상위 15개만
            
            # 메타 설명
            meta_desc = seo.get("meta_description", "")
            if meta_desc:
                blocks.append(self._callout("메타 설명", "📝", "purple_background"))
                blocks.append(self._paragraph(meta_desc))
        
        blocks.append(self._divider())
        
        # Reference links
        queries = content.get("brave_search_queries", [])
        if queries:
            blocks.append(self._heading(2, "참고 자료"))
            blocks.append(self._paragraph("아래 링크에서 더 많은 정보를 확인할 수 있어:"))
            for q in queries:
                search_url = f"https://www.google.com/search?q={urllib.parse.quote(q)}"
                blocks.append(self._paragraph(f"🔍 {q}", link=search_url))
        
        # Footer
        blocks.append(self._divider())
        blocks.append(self._paragraph(f"작성일: {content.get('generated_at', datetime.now().isoformat())[:10]}"))
        
        return blocks
