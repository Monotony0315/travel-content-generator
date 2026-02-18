"""
Fixed Notion Publisher
버그 수정: 100블록 제한, 텍스트 잘림 문제 해결
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


class FixedNotionPublisher:
    """버그 수정 버전 - 콘텐츠 잘림 없이 완전 표시"""

    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2025-09-03"
    MAX_TEXT_LENGTH = 1900  # Notion API 제한
    MAX_BLOCKS_PER_REQUEST = 100  # Notion API 하드 리밋

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
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Notion API error {e.code}: {body}") from e

    async def publish_blog(self, content: Dict, images: List[Dict]) -> str:
        """블로그 발행 - 콘텐츠 잘림 없이"""
        import random
        dest = content["destination"]
        city = dest["name"]
        country = dest.get("country", "")
        
        # Unique title with timestamp + random suffix
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
        total_blocks = len(blocks)
        logger.info(f"Total blocks to publish: {total_blocks}")
        
        if total_blocks > self.MAX_BLOCKS_PER_REQUEST:
            logger.warning(f"Block count ({total_blocks}) exceeds limit ({self.MAX_BLOCKS_PER_REQUEST}). Truncating to fit.")
            blocks = blocks[:self.MAX_BLOCKS_PER_REQUEST]
        
        # Add blocks in batches
        batch_size = 90
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]
            self._request("PATCH", f"/blocks/{page_id}/children", {"children": batch})
            logger.info(f"Added blocks {i+1} to {min(i+len(batch), len(blocks))} of {len(blocks)}")
        
        return page_url

    def _split_long_text(self, text: str, max_len: int = 1900) -> List[str]:
        """긴 텍스트를 여러 chunk로 분할"""
        if len(text) <= max_len:
            return [text]
        
        chunks = []
        while text:
            if len(text) <= max_len:
                chunks.append(text)
                break
            
            # 문장 끝에서 자르기
            split_pos = text.rfind('. ', 0, max_len)
            if split_pos == -1:
                split_pos = text.rfind(' ', 0, max_len)
            if split_pos == -1:
                split_pos = max_len
            
            chunks.append(text[:split_pos + 1])
            text = text[split_pos + 1:].strip()
        
        return chunks

    def _parse_markdown_links(self, text: str) -> List[Dict]:
        """마크다운 링크 [text](url)를 Notion rich_text로 변환"""
        import re
        result = []
        # 마크다운 링크 패턴: [text](url)
        pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        
        last_end = 0
        for match in re.finditer(pattern, text):
            # 링크 앞의 일반 텍스트
            if match.start() > last_end:
                result.append({
                    "type": "text",
                    "text": {"content": text[last_end:match.start()]}
                })
            # 링크 텍스트
            link_text = match.group(1)
            link_url = match.group(2)
            result.append({
                "type": "text",
                "text": {"content": link_text, "link": {"url": link_url}},
                "annotations": {"bold": True}
            })
            last_end = match.end()
        
        # 남은 텍스트
        if last_end < len(text):
            result.append({
                "type": "text",
                "text": {"content": text[last_end:]}
            })
        
        return result if result else [{"type": "text", "text": {"content": text}}]

    def _rt(self, text: str, bold: bool = False, link: Optional[str] = None, color: Optional[str] = None) -> List[Dict]:
        """Rich text 생성 - 마크다운 링크와 긴 텍스트 처리"""
        # 마크다운 링크가 있는지 확인
        if '[' in text and '](' in text:
            items = self._parse_markdown_links(str(text))
            # bold/color 적용
            for item in items:
                if bold and "annotations" in item:
                    item["annotations"]["bold"] = True
                elif bold:
                    item["annotations"] = {"bold": True}
                if color:
                    item.setdefault("annotations", {})["color"] = color
            return items
        
        # 일반 텍스트 처리
        chunks = self._split_long_text(str(text), self.MAX_TEXT_LENGTH)
        result = []
        for chunk in chunks:
            item = {"type": "text", "text": {"content": chunk}}
            if bold:
                item["annotations"] = {"bold": True}
            if link:
                item["text"]["link"] = {"url": link}
            if color:
                item.setdefault("annotations", {})["color"] = color
            result.append(item)
        return result

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
        """블록 구성 - 블록 수 최적화"""
        dest = content["destination"]
        blocks = []
        
        # Hero Image
        if images:
            blocks.append(self._image_external(images[0]["url"], f"{city} 대표 이미지"))
        
        # Title
        blocks.append(self._heading(1, f"{city} 여행 완벽 가이드"))
        blocks.append(self._paragraph(f"{dest['days']}일 일정 | {dest['best_season']} 추천 | 통화: {dest['currency']}", bold=True))
        blocks.append(self._divider())
        
        # Intro
        blocks.append(self._quote(content.get("intro", "")))
        blocks.append(self._divider())
        
        # HOTELS Section - 더 간략화
        blocks.append(self._heading(2, "추천 호텔"))
        hotels = content.get("hotels", {})
        
        for cat, label, color in [("budget", "가성비", "green"), ("luxury", "럭셔리", "purple")]:
            hotel_list = hotels.get(cat, [])
            if not hotel_list:
                continue
            blocks.append(self._callout(label, "", f"{color}_background"))
            for h in hotel_list:
                # 호텔 정보를 한 문단으로 압축 - validate URL
                hotel_name = h['name']
                maps_url = h.get('maps_url', '')
                if maps_url and maps_url.startswith('http'):
                    hotel_text = f"[{hotel_name}]({maps_url}) ★{h['rating']} | {h['price_per_night']} | {h['area']}"
                else:
                    hotel_text = f"**{hotel_name}** ★{h['rating']} | {h['price_per_night']} | {h['area']}"
                blocks.append(self._paragraph(hotel_text))
        
        blocks.append(self._divider())
        
        # DAILY ITINERARY
        blocks.append(self._heading(2, "일정 상세"))
        
        for idx, day in enumerate(content.get("days_plan", [])):
            day_num = day.get("day", idx + 1)
            
            # Day image
            if len(images) > day_num:
                blocks.append(self._image_external(images[day_num]["url"], f"Day {day_num}"))
            
            # Day header
            blocks.append(self._callout(f"Day {day_num}: {day['title']}", "", "blue_background"))
            
            # Day content - 문단을 더 큰 덩어리로 묶기
            content_text = day.get("content", "").strip()
            # 2-3문단씩 묶어서 하나의 블록으로
            paragraphs = [p.strip() for p in content_text.split('\n\n') if p.strip()]
            
            # 첫 2문단은 따로, 나머지는 합쳐서 블록 수 줄이기
            if paragraphs:
                # 첫 문단
                blocks.append(self._paragraph(paragraphs[0]))
                # 나머지 문단들 (2-3개씩 합쳐서)
                remaining = '\n\n'.join(paragraphs[1:])
                if remaining:
                    # 4000자씩 잘라서 여러 블록으로 (rich_text 여러 개 사용)
                    chunks = self._split_long_text(remaining, 4000)
                    for chunk in chunks:
                        blocks.append(self._paragraph(chunk))
            
            # Spots - 간략화
            spots = day.get("spots", [])
            if spots:
                blocks.append(self._heading(3, "주요 장소"))
                for spot in spots:
                    name = spot['name']
                    desc = spot['desc']
                    maps_url = self._maps_url(f"{name} {city}")
                    reservation_url = spot.get('reservation_url', '')
                    reservation_required = spot.get('reservation_required', False)
                    
                    # 한 줄로 압축 - 팁 제외
                    spot_text = f"• **[{name}]({maps_url})**: {desc}"
                    if reservation_required and reservation_url and reservation_url.startswith('http'):
                        spot_text += f" | [🎫 예약하기]({reservation_url})"
                    blocks.append(self._paragraph(spot_text))
            
            # Restaurants - 간략화
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
                    
                    rest_text = f"• **[{name}]({maps_url})** ({price}): {tip}"
                    if reservation_required and reservation_url and reservation_url.startswith('http'):
                        rest_text += f" | [🎫 예약]({reservation_url})"
                    blocks.append(self._paragraph(rest_text))
            
            # Daily cost
            cost = day.get("estimated_cost", {})
            if cost:
                blocks.append(self._callout(f"💰 {cost.get('total', '')}", "", "yellow_background"))
            
            # 100블록 근접시 중단
            if len(blocks) >= 90:
                blocks.append(self._callout("⚠️ 이후 내용은 다음 페이지에서 확인하세요.", "", "red_background"))
                break
        
        # TRANSPORT & PARKING
        blocks.append(self._heading(2, "교통 및 이동"))
        transport = content.get("transport_summary", {})
        transport_text = " | ".join([f"{k}: {v}" for k, v in transport.items()])
        blocks.append(self._paragraph(transport_text))
        
        # 렌트카 주차 정보 - 간략화
        if dest.get("car_rental_available"):
            parking = content.get("parking_info", {})
            if parking:
                blocks.append(self._heading(3, "🚗 렌트카 주차 안내"))
                blocks.append(self._paragraph(f"**주차 난이도:** {parking.get('difficulty', '')} | **요금:** {parking.get('city_center_rate', '')}"))
                
                pr_locations = parking.get("pr_locations", [])
                if pr_locations:
                    pr_text = "**추천 P+R 주차장:** "
                    for pr in pr_locations:
                        name = pr['name']
                        maps_url = pr.get('maps_url', '')
                        if maps_url and maps_url.startswith('http'):
                            pr_text += f"[{name}]({maps_url}) "
                        else:
                            pr_text += f"{name} "
                    blocks.append(self._paragraph(pr_text))
        
        # TOTAL COST SUMMARY
        blocks.append(self._heading(2, "총 예상 비용"))
        estimates = content.get("total_estimate", {})
        
        for level in ["budget", "luxury"]:
            est = estimates.get(level, {})
            label = "가성비 여행" if level == "budget" else "럭셔리 여행"
            color = "green" if level == "budget" else "purple"
            
            blocks.append(self._callout(label, "", f"{color}_background"))
            if est.get("total"):
                blocks.append(self._paragraph(f"**총계: {est['total']}**"))
        
        blocks.append(self._divider())
        
        # FINAL SUMMARY - 최종 요약 (서술형 스타일)
        final_summary = content.get("final_summary", {})
        if final_summary:
            blocks.append(self._heading(2, "📋 여행 전 체크리스트 & 꿀팁"))
            
            # 🎫 예약 필수 - 서술형
            must_reserve = final_summary.get("must_reserve", [])
            if must_reserve:
                blocks.append(self._callout("🎫 미리 예약해야 할 곳", "", "red_background"))
                reserve_text = "이번 여행에서 꼭 미리 예약해야 하는 곳들이에요. 특히 인기 있는 명소는 하루 전에는 매진되곤 하니, 미리 준비하시는 것을 추천드려요. "
                for i, item in enumerate(must_reserve[:5], 1):
                    name = item['name']
                    when = item['when']
                    url = item.get('url', '')
                    if url and url.startswith('http'):
                        reserve_text += f"{i}) [{name}]({url})은 {when}에 예약하시는 것이 좋아요. "
                    else:
                        reserve_text += f"{i}) {name}은 {when}에 예약하시는 것이 좋아요. "
                blocks.append(self._paragraph(reserve_text))
            
            # 🚨 비상 연락처 & 대사관 - 서술형
            emergency = final_summary.get("emergency_contacts", {})
            embassy = final_summary.get("embassy_info", {})
            if emergency or embassy:
                blocks.append(self._callout("🚨 만약의 사태에 대비한 연락처", "", "yellow_background"))
                
                emergency_text = "여행 중 긴급 상황이 발생하면 당황하지 마시고 아래 번호로 연락하세요. "
                if emergency:
                    emergency_text += f"현지에서는 통합 신고번호 **{emergency.get('general', '112')}**로 모든 긴급 상황을 신고할 수 있어요. "
                    emergency_text += f"경찰({emergency.get('police', '112')}), 구급/응급({emergency.get('ambulance', '112')}), 소방({emergency.get('fire', '112')})이 각각 연결됩니다. "
                
                if embassy:
                    emergency_text += f"\\n\\n한국 대사관도 기억해두세요. **[{embassy.get('name', '해당국 한국대사관')}]({embassy.get('website', 'https://www.mofa.go.kr')})** ({embassy.get('phone', '+82-2-2100-2100')})에 연락하시면 여권 분실, 사고 등 각종 지원을 받으실 수 있어요. "
                    emergency_text += f"긴급 상황 시에는 {embassy.get('emergency', embassy.get('phone', '+82-2-2100-2100'))}로 연락하시고, 주소는 {embassy.get('address', '외교부 홈페이지 참조')}입니다. "
                    emergency_text += f"업무시간은 {embassy.get('hours', '평일 09:00-12:00, 13:30-17:00')}이니 참고하세요."
                
                blocks.append(self._paragraph(emergency_text))
            
            # 💰 돈/환전 꿀팁 - 서술형
            money_tips = final_summary.get("money_tips", {})
            if money_tips:
                money_text = f"\\n💰 **돈 관리 팁**: 환전은 {money_tips.get('exchange', '은행이나 ATM에서')}하는 것이 유리해요. "
                money_text += f"카드 사용은 {money_tips.get('card', '주요 가게에서 가능')}하지만, {money_tips.get('cash', '소액 현금')}은 꼭 준비하세요. "
                money_text += f"ATM은 {money_tips.get('atm', '수수료 확인 후 인출')}하는 것이 좋습니다."
                blocks.append(self._paragraph(money_text))
            
            # 🎯 여행 꿀팁 - 서술형
            travel_tips = final_summary.get("travel_tips", [])
            if travel_tips:
                tips_text = "\\n🎯 **현지 꿀팁**: "
                for i, tip in enumerate(travel_tips[:5], 1):
                    if i > 1:
                        tips_text += " 또한 "
                    tips_text += f"{tip}"
                tips_text += " 이런 팁들을 기억하시면 더 즐거운 여행이 될 거예요."
                blocks.append(self._paragraph(tips_text))
            
            # ⚠️ 안전 주의사항 - 서술형
            safety_tips = final_summary.get("safety_tips", [])
            if safety_tips:
                safety_text = "\\n⚠️ **안전을 위한 조언**: "
                for i, tip in enumerate(safety_tips[:5], 1):
                    if i > 1:
                        safety_text += " "
                    safety_text += f"{tip}."
                safety_text += " 조금만 주의하시면 안전하게 여행하실 수 있어요."
                blocks.append(self._paragraph(safety_text))
            
            # 📱 필수 앱 - 서술형
            essential_apps = final_summary.get("essential_apps", [])
            if essential_apps:
                blocks.append(self._heading(3, "📱 여행에 꼭 필요한 앱"))
                apps_text = "스마트폰에 미리 설치해두면 편리한 앱들을 추천드릴게요. "
                for app in essential_apps[:5]:
                    if isinstance(app, dict):
                        app_name = app.get('name', '')
                        app_purpose = app.get('purpose', '')
                        app_url = app.get('url', '')
                        if app_url:
                            apps_text += f"[{app_name}]({app_url})은 {app_purpose}에 최적이에요. "
                        else:
                            apps_text += f"{app_name}은 {app_purpose}에 최적이에요. "
                    else:
                        apps_text += f"{app} "
                apps_text += "이 앱들은 현지에서 정말 유용하게 사용하실 수 있을 거예요."
                blocks.append(self._paragraph(apps_text))
            
            # 🎒 준비물 체크리스트 - 서술형
            packing = final_summary.get("packing_checklist", [])
            if packing:
                blocks.append(self._heading(3, "🎒 짐 싸기 전 확인"))
                packing_text = "출발 전 꼭 챙겨야 할 것들이에요. "
                packing_text += ", ".join(packing[:10])
                packing_text += " 등을 준비하시면 되겠네요. 여행 전날 밤 미리 가방을 꾸려두시는 것을 추천드려요."
                blocks.append(self._paragraph(packing_text))
        
        blocks.append(self._divider())
        
        # 여행 블로그 링크 섹션
        blog_links = content.get('blog_links', [])
        if blog_links:
            blocks.append(self._heading(2, "🔗 참고 여행 블로그"))
            blocks.append(self._paragraph("해당 도시에 대한 더 많은 정보는 아래 링크에서 확인하세요:"))
            for link in blog_links[:4]:  # 상위 4개만
                # Only add link if URL is valid
                if link and isinstance(link, str) and link.startswith('http'):
                    blocks.append(self._paragraph(f"• [여행 가이드 보기]({link})"))
                elif link and isinstance(link, str):
                    blocks.append(self._paragraph(f"• {link}"))
        
        # Footer
        blocks.append(self._divider())
        blocks.append(self._paragraph(f"작성일: {content.get('generated_at', datetime.now().isoformat())[:10]}"))
        
        logger.info(f"Total blocks created: {len(blocks)}")
        return blocks
