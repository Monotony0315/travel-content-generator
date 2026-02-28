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
        
        # Notion API 는 한 번에 100블록 제한 → batch 로 나눠서 전부 추가
        batch_size = 95
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]
            self._request("PATCH", f"/blocks/{page_id}/children", {"children": batch})
            logger.info(f"Added blocks {i+1} to {min(i+len(batch), total_blocks)} of {total_blocks}")
        
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

    def _clean_text(self, text: str) -> str:
        """텍스트 정제: \\n 제거, 공백 정리"""
        import re
        
        # \\n 문자열 제거
        text = text.replace('\\n', ' ')
        
        # 실제 개행문자도 공백으로
        text = text.replace('\n', ' ')
        
        # 연속된 공백 정리
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _rt(self, text: str, bold: bool = False, link: Optional[str] = None, color: Optional[str] = None) -> List[Dict]:
        """Rich text 생성 - 마크다운 링크와 긴 텍스트 처리"""
        # 텍스트 정제
        text = self._clean_text(str(text))
        
        # 마크다운 링크가 있는지 확인
        if '[' in text and '](' in text:
            items = self._parse_markdown_links(text)
            # bold/color 적용
            for item in items:
                if bold and "annotations" in item:
                    item["annotations"]["bold"] = True
                elif bold:
                    item["annotations"] = {"bold": True}
                if color:
                    item.setdefault("annotations", {})["color"] = color
            return items
        
        # 일반 텍스트 처리 - 문장 단위로 분리
        sentences = []
        import re
        parts = re.split(r'([.!?]+\s+)', text)
        
        current = ""
        for part in parts:
            if not part.strip():
                continue
            if len(current) + len(part) < 120:
                current += part
            else:
                if current.strip():
                    sentences.append(current.strip())
                current = part
        
        if current.strip():
            sentences.append(current.strip())
        
        if not sentences:
            sentences = [text]
        
        result = []
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
            item = {"type": "text", "text": {"content": sentence}}
            if bold:
                item["annotations"] = {"bold": True}
            if link and i == 0:
                item["text"]["link"] = {"url": link}
            if color:
                item.setdefault("annotations", {})["color"] = color
            result.append(item)
            
            if i < len(sentences) - 1:
                result.append({"type": "text", "text": {"content": " "}})
        
        return result if result else [{"type": "text", "text": {"content": text}}]

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

    def _table(self, rows: List[List[str]], has_header: bool = True) -> Dict:
        width = max(len(r) for r in rows)
        norm_rows = []
        for row in rows:
            cells = list(row[:width])
            if len(cells) < width:
                cells.extend([""] * (width - len(cells)))
            norm_rows.append({
                "object": "block",
                "type": "table_row",
                "table_row": {"cells": [self._rt(str(cell)) for cell in cells]},
            })
        return {
            "object": "block",
            "type": "table",
            "table": {
                "table_width": width,
                "has_column_header": has_header,
                "has_row_header": False,
                "children": norm_rows,
            },
        }

    def _split_total_amounts(self, est: Dict) -> tuple[str, str]:
        local = str(est.get("total_local", "")).strip()
        krw = str(est.get("total_krw", "")).strip()
        if local and krw:
            return local, krw
        total_text = str(est.get("total", "")).strip()
        if total_text and "(" in total_text and ")" in total_text:
            local_part, _, tail = total_text.partition("(")
            krw_part = tail.rsplit(")", 1)[0]
            return local_part.strip(), krw_part.strip()
        return total_text, ""

    def _build_cost_table_rows(self, estimates: Dict) -> List[List[str]]:
        rows = [["구분", "숙박", "식비", "교통", "액티비티", "총액(현지)", "총액(원화)"]]
        for level, label in [("budget", "가성비"), ("mid", "일반"), ("luxury", "고급")]:
            est = estimates.get(level, {})
            if not isinstance(est, dict) or not est:
                continue
            total_local, total_krw = self._split_total_amounts(est)
            rows.append([
                label,
                str(est.get("accommodation", "-")),
                str(est.get("food", "-")),
                str(est.get("transport", "-")),
                str(est.get("activities", "-")),
                total_local or "-",
                total_krw or "-",
            ])
        return rows if len(rows) > 1 else []

    def _get_image_attribution(self, image: Dict) -> str:
        """이미지 출처 생성"""
        source = image.get("source", "unknown")
        photographer = image.get("photographer", "Unknown")
        
        if source == "unsplash":
            return f"📷 {photographer} on Unsplash"
        elif source == "pexels":
            return f"📷 {photographer} on Pexels"
        elif source == "pixabay":
            return f"📷 {photographer} on Pixabay"
        else:
            return f"📷 {photographer}"

    def _image_external(self, url: str, caption: str = "", attribution: str = "") -> Dict:
        block = {
            "object": "block",
            "type": "image",
            "image": {"type": "external", "external": {"url": url}},
        }
        # caption + attribution 함께 표시
        caption_text = caption
        if attribution:
            if caption_text:
                caption_text += f" | {attribution}"
            else:
                caption_text = attribution
        if caption_text:
            block["image"]["caption"] = [{"type": "text", "text": {"content": caption_text}}]
        return block

    def _build_final_blocks(self, content: Dict, images: List[Dict], city: str) -> List[Dict]:
        """블록 구성 - 블록 수 최적화"""
        dest = content["destination"]
        blocks = []
        minimal_mode = os.getenv("TRAVEL_PUBLISHER_MINIMAL", "0") == "1"

        # Minimal mode: keep only core narrative flow.
        if minimal_mode:
            # Hero image
            if images:
                hero_attr = self._get_image_attribution(images[0])
                blocks.append(self._image_external(images[0]["url"], f"{city} 대표 이미지", hero_attr))
            blocks.append(self._heading(1, f"{city} 여행 가이드"))
            blocks.append(self._paragraph(content.get("intro", "")))

            # scenario + season + 통계 + 호텔 + 비용
            scenario_section = content.get("scenario_section")
            if scenario_section:
                blocks.append(self._heading(2, "🎯 3가지 방문 시나리오"))
                blocks.append(self._paragraph(scenario_section))

            season = content.get("season_section")
            if season:
                blocks.append(self._heading(2, "📊 통계적 방문 시기"))
                blocks.append(self._paragraph(season))

            visit_stats = content.get("visit_statistics")
            if isinstance(visit_stats, dict):
                blocks.append(self._heading(3, "📈 방문 데이터 요약"))
                top = visit_stats.get("장점")
                if isinstance(top, list):
                    for row in top[:3]:
                        blocks.append(self._paragraph(f"• {row}"))
                density = visit_stats.get("콘텐츠 밀도")
                if isinstance(density, dict):
                    for k, v in density.items():
                        blocks.append(self._paragraph(f"• {k}: {v}"))
                patterns = visit_stats.get("방문 패턴")
                if isinstance(patterns, dict):
                    for k, v in patterns.items():
                        blocks.append(self._paragraph(f"• {k}: {v}"))

            hotels = content.get("hotels", {})
            blocks.append(self._heading(2, "🏨 숙소 3티어 추천"))
            for cat, label in [("budget", "가성비"), ("mid", "일반"), ("luxury", "고급")]:
                hotel_list = (hotels.get(cat) or [])
                if not hotel_list:
                    continue
                blocks.append(self._paragraph(f"[{label}]"))
                for h in hotel_list[:2]:
                    h_name = h.get("name", "숙소")
                    h_url = h.get("maps_url", "")
                    h_area = h.get("area", "")
                    h_price = h.get("price_per_night", "")
                    h_rating = h.get("rating", "")
                    h_pros = h.get("pros", "-")
                    h_cons = h.get("cons", "-")
                    h_for = h.get("recommended_for", "가성비/동선형 추천")
                    if h_url and str(h_url).startswith("http"):
                        h_line = f"[{h_name}]({h_url})"
                    else:
                        h_line = h_name
                    blocks.append(self._paragraph(f"{h_line} | 평점 {h_rating} | 1박 {h_price} | {h_area}"))
                    blocks.append(self._paragraph(f"장단점: {h_pros} / {h_cons}"))
                    blocks.append(self._paragraph(f"추천 대상: {h_for}"))

            total_estimate = content.get("total_estimate", {})
            if total_estimate:
                blocks.append(self._heading(2, "💰 여행비용 분석"))
                cost_rows = self._build_cost_table_rows(total_estimate if isinstance(total_estimate, dict) else {})
                if cost_rows:
                    blocks.append(self._table(cost_rows, has_header=True))

            blocks.append(self._divider())

            # 핵심 일정 + 일자 대표 이미지 + 3티어 맛집 + 예약 동선 + 일일 비용
            for idx, day in enumerate(content.get("days_plan", [])):
                day_num = day.get("day", idx + 1)
                title = day.get("title", "")
                blocks.append(self._heading(2, f"Day {day_num}: {title}"))

                if len(images) > day_num:
                    day_attr = self._get_image_attribution(images[day_num])
                    blocks.append(self._image_external(images[day_num]["url"], f"Day {day_num}", day_attr))

                content_text = day.get("content", "").strip()
                if content_text:
                    for p in [x.strip() for x in content_text.split('\n\n') if x.strip()][:6]:
                        blocks.append(self._paragraph(p))

                rest_md = day.get("restaurant_markdown", "")
                if rest_md:
                    for p in [x.strip() for x in rest_md.split('\n') if x.strip()][:8]:
                        blocks.append(self._paragraph(p))

                reserve_spots = []
                for s in (day.get("spots") or []):
                    if s.get("reservation_required") and s.get("reservation_url"):
                        reserve_spots.append(s)
                if reserve_spots:
                    blocks.append(self._paragraph("🔔 예약이 필요한 주요 방문지"))
                    for s in reserve_spots[:4]:
                        name = s.get("name", "")
                        when = s.get("time", "")
                        url = s.get("reservation_url", "")
                        if url and str(url).startswith("http"):
                            blocks.append(self._paragraph(f"• {name} ({when}) — [예약하기]({url})"))

                blocks.append(self._divider())

            final_summary = content.get("final_summary", {})
            if isinstance(final_summary, dict):
                blocks.append(self._heading(2, "🚨 비상연락망"))
                emergency = final_summary.get("emergency_contacts", {})
                if isinstance(emergency, dict):
                    blocks.append(self._paragraph(f"현지 긴급번호: 경찰 {emergency.get('police', '-')}, 구급/응급 {emergency.get('ambulance', '-')}, 소방 {emergency.get('fire', '-')}, 통합 {emergency.get('general', '-')}"))
                    if emergency.get("tips"):
                        blocks.append(self._paragraph(f"안전 팁: {emergency.get('tips')}"))

                embassy = final_summary.get("embassy_info", {})
                if isinstance(embassy, dict):
                    emb = f"{embassy.get('name', '')} / 전화 {embassy.get('phone', '')} / 긴급 {embassy.get('emergency_phone', embassy.get('emergency', ''))} / 주소 {embassy.get('address', '')} / 영업시간 {embassy.get('hours', '')}"
                    emb_url = embassy.get("website")
                    if emb_url and str(emb_url).startswith("http"):
                        blocks.append(self._paragraph(f"[{emb}]({emb_url})"))
                    else:
                        blocks.append(self._paragraph(emb))

                useful_links = final_summary.get("useful_links", [])
                if useful_links:
                    blocks.append(self._heading(3, "📌 유용정보"))
                    for u in useful_links[:6]:
                        blocks.append(self._paragraph(f"• {u}"))

            if content.get("closing"):
                blocks.append(self._heading(2, "📝 마무리"))
                blocks.append(self._paragraph(content.get("closing", "")))

            blocks.append(self._paragraph(f"작성일: {content.get('generated_at', datetime.now().isoformat())[:10]}"))
            logger.info(f"Total blocks created: {len(blocks)} (minimal mode)")
            return blocks

        # Hero Image with attribution
        if images:
            hero_attr = self._get_image_attribution(images[0])
            blocks.append(self._image_external(images[0]["url"], f"{city} 대표 이미지", hero_attr))
        
        # Title
        blocks.append(self._heading(1, f"{city} 여행 완벽 가이드"))
        blocks.append(self._paragraph(f"{dest['days']}일 일정 | {dest['best_season']} 추천 | 통화: {dest['currency']}", bold=True))
        blocks.append(self._divider())
        
        # Intro
        blocks.append(self._quote(content.get("intro", "")))
        blocks.append(self._divider())
        
        # HOTELS Section - 추천 이유까지 표시
        blocks.append(self._heading(2, "추천 호텔"))
        hotels = content.get("hotels", {})

        for cat, label, color in [("budget", "가성비", "green"), ("mid", "일반", "blue"), ("luxury", "고급", "purple")]:
            hotel_list = hotels.get(cat, [])
            if not hotel_list:
                continue
            blocks.append(self._callout(label, "", f"{color}_background"))
            for h in hotel_list[:2]:
                hotel_name = h.get("name", "")
                maps_url = h.get('maps_url', '')
                pros = h.get('pros', '') or '강점 정보 없음'
                cons = h.get('cons', '') or '주의 포인트 없음'
                rec = h.get('recommended_for', '')
                area = h.get('area', '')
                price = h.get('price_per_night', '')
                rating = h.get('rating', '')
                if maps_url and maps_url.startswith('http'):
                    hotel_text = f"[{hotel_name}]({maps_url}) ★{rating} | {price} | {area}"
                else:
                    hotel_text = f"{hotel_name} ★{rating} | {price} | {area}"
                blocks.append(self._paragraph(hotel_text))
                detail = f"{hotel_name}은(는) {area or '주요 구역'} 중심으로 이동 동선이 편하고, 하루를 마무리하기 좋은 숙소입니다."
                if rec:
                    detail += f" 특히 {rec} 여행자에게 잘 맞아요."
                blocks.append(self._paragraph(detail))
                blocks.append(self._paragraph(f"장점: {pros}"))
                blocks.append(self._paragraph(f"단점: {cons}"))
                if rec:
                    blocks.append(self._paragraph(f"추천 대상: {rec}"))
        
        blocks.append(self._divider())
        
        # REVIEW INSIGHTS (real usage signals)
        review_bundle = content.get("review_insights", {}) if isinstance(content, dict) else {}
        if isinstance(review_bundle, dict):
            items = review_bundle.get("items", []) or []
            if items:
                blocks.append(self._heading(2, "실사용 리뷰 인사이트"))
                for idx, row in enumerate(items[:5], 1):
                    title = row.get("title", "리뷰 인사이트")
                    snippet = row.get("snippet", "")
                    source = row.get("source", "source")
                    url = row.get("url", "")
                    if url and str(url).startswith("http"):
                        heading = f"{idx}. [{title}]({url})"
                    else:
                        heading = f"{idx}. {title}"
                    blocks.append(self._paragraph(f"{heading} ({source})"))
                    if snippet:
                        blocks.append(self._paragraph(snippet[:340]))
                blocks.append(self._divider())

        # DAILY ITINERARY — 여행 블로그 스타일
        blocks.append(self._heading(2, "일정 상세"))
        
        for idx, day in enumerate(content.get("days_plan", [])):
            day_num = day.get("day", idx + 1)
            
            # Day image with attribution
            if len(images) > day_num:
                day_attr = self._get_image_attribution(images[day_num])
                blocks.append(self._image_external(images[day_num]["url"], f"Day {day_num}", day_attr))
            
            # Day header
            blocks.append(self._callout(f"📌 Day {day_num}: {day['title']}", "", "blue_background"))
            blocks.append(self._paragraph(f"티켓/예약 필요: {'있음' if day.get('reservation_notice') else '없음'}"))
            if day.get('reservation_notice'):
                blocks.append(self._paragraph(f"🔔 예약 안내: {day.get('reservation_notice')}"))

            # Day content — 서술형 소개 (전체 문단)
            content_text = day.get("content", "").strip()
            paragraphs = [p.strip() for p in content_text.split('\n\n') if p.strip()]
            for paragraph in paragraphs:
                blocks.append(self._paragraph(paragraph))
            
            # ─── 🗺️ 오늘의 코스 ───
            spots = day.get("spots", [])
            if spots:
                blocks.append(self._heading(3, "오늘의 코스"))
                for i, spot in enumerate(spots, 1):
                    name = spot['name']
                    desc = spot.get('desc', spot.get('description', ""))
                    tip = spot.get('tip', '')
                    time_str = spot.get('time', '')
                    maps_url = self._maps_url(f"{name} {city}")
                    res_url = spot.get('reservation_url', '')
                    res_req = spot.get('reservation_required', False)
                    
                    # 장소명 + 시간 (1줄) - bold 제거
                    title_line = f"{i}. [{name}]({maps_url})"
                    if time_str:
                        title_line += f"  ⏰ {time_str}"
                    blocks.append(self._paragraph(title_line))
                    
                    # 설명 + 요약 정보 + 팁 + 예약 (1줄로 합침)
                    detail_parts = []
                    if desc:
                        detail_parts.append(desc)
                    if spot.get("history"):
                        detail_parts.append(f"{spot.get('history')}" )
                    if spot.get("duration"):
                        detail_parts.append(f"소요시간: {spot.get('duration')}")
                    if spot.get("fee"):
                        detail_parts.append(f"입장료: {spot.get('fee')}")
                    if tip:
                        detail_parts.append(f"💡 {tip}")
                    if res_req and res_url and res_url.startswith('http'):
                        detail_parts.append(f"[예약하기]({res_url})")
                    detail = " | ".join(detail_parts)
                    blocks.append(self._paragraph(detail if detail else tip or name))
            
            # ─── 🍽️ 오늘의 맛집 (하루 2-3개 추천) ───
            restaurants = day.get("restaurants", [])
            if restaurants:
                blocks.append(self._heading(3, "오늘의 맛집"))
                
                # price_tier 기반 분류
                budget_r = [r for r in restaurants if r.get('price_tier') == 'budget']
                mid_r = [r for r in restaurants if r.get('price_tier') == 'mid']
                luxury_r = [r for r in restaurants if r.get('price_tier') == 'luxury']
                no_tier = [r for r in restaurants if 'price_tier' not in r]
                if no_tier and not budget_r and not mid_r and not luxury_r:
                    mid_r = no_tier
                
                # 각 tier에서 day_num 기준으로 돌아가며 1개씩 선택
                day_picks = []
                if budget_r:
                    day_picks.append(("", budget_r[(day_num - 1) % len(budget_r)]))
                if mid_r:
                    day_picks.append(("", mid_r[(day_num - 1) % len(mid_r)]))
                if luxury_r:
                    day_picks.append(("", luxury_r[(day_num - 1) % len(luxury_r)]))
                
                for emoji, r in day_picks:
                    r_name = r['name']
                    r_price = r.get('price', '')
                    r_type = r.get('type', '')
                    r_tip = r.get('tip', '')
                    signatures = r.get('signature', []) if isinstance(r.get('signature', []), list) else []
                    r_menu = r.get('recommended_menu', '') or (", ".join([str(x) for x in signatures[:2] if x]))
                    r_pros = r.get('pros', '') or "동선상 접근성이 좋아 일정 중간에 넣기 편함"
                    r_cons = r.get('cons', '') or "피크 타임에는 대기가 생길 수 있음"
                    r_maps = self._maps_url(f"{r_name} {city}")
                    r_res_url = r.get('reservation_url', '')
                    r_res_req = r.get('reservation_required', False)
                    
                    r_line = f"{emoji} [{r_name}]({r_maps})  {r_type} · {r_price}"
                    blocks.append(self._paragraph(r_line))

                    if r_menu:
                        blocks.append(self._paragraph(f"추천 메뉴: {r_menu}"))
                    blocks.append(self._paragraph(f"장점: {r_pros}"))
                    blocks.append(self._paragraph(f"단점: {r_cons}"))

                    r_detail = ""
                    if r_tip:
                        r_detail = f"→ {r_tip}"
                    if r_res_req and r_res_url and r_res_url.startswith('http'):
                        r_detail += f"  [예약하기]({r_res_url})"
                    if r_detail:
                        blocks.append(self._paragraph(r_detail))
            
            # ─── 💰 오늘의 예상 비용 ───
            
            blocks.append(self._divider())
        
        # ─── 🍽️ 전체 맛집 가이드 (가성비 / 일반 / 고급) ───
        all_restaurants = content.get("restaurants", [])
        if all_restaurants:
            blocks.append(self._heading(2, "전체 맛집 가이드"))
            
            budget_all = [r for r in all_restaurants if r.get('price_tier') == 'budget']
            mid_all = [r for r in all_restaurants if r.get('price_tier') == 'mid']
            luxury_all = [r for r in all_restaurants if r.get('price_tier') == 'luxury']
            no_tier_all = [r for r in all_restaurants if 'price_tier' not in r]
            if no_tier_all and not budget_all and not mid_all and not luxury_all:
                mid_all = no_tier_all
            
            for tier_label, tier_list, tier_color in [
                ("가성비 맛집", budget_all, "green_background"),
                ("일반 맛집", mid_all, "orange_background"),
                ("고급 식당", luxury_all, "purple_background"),
            ]:
                if not tier_list:
                    continue
                blocks.append(self._callout(tier_label, "", tier_color))
                for r in tier_list:
                    r_name = r['name']
                    r_price = r.get('price', '')
                    r_type = r.get('type', '')
                    r_tip = r.get('tip', '')
                    signatures = r.get('signature', []) if isinstance(r.get('signature', []), list) else []
                    r_menu = r.get('recommended_menu', '') or (", ".join([str(x) for x in signatures[:2] if x]))
                    r_pros = r.get('pros', '') or "접근성이 좋아 동선 손실이 적음"
                    r_cons = r.get('cons', '') or "인기 시간대 대기 가능"
                    r_maps = self._maps_url(f"{r_name} {city}")
                    r_res_url = r.get('reservation_url', '')
                    r_res_req = r.get('reservation_required', False)
                    
                    r_line = f"[{r_name}]({r_maps})  {r_type} · {r_price}"
                    if r_res_req and r_res_url and r_res_url.startswith('http'):
                        r_line += f"  [예약]({r_res_url})"
                    blocks.append(self._paragraph(r_line))
                    if r_menu:
                        blocks.append(self._paragraph(f"추천 메뉴: {r_menu}"))
                    blocks.append(self._paragraph(f"장점: {r_pros}"))
                    blocks.append(self._paragraph(f"단점: {r_cons}"))
                    if r_tip:
                        blocks.append(self._paragraph(f"→ {r_tip}"))
            
            blocks.append(self._divider())
        
        # TRANSPORT & PARKING
        blocks.append(self._heading(2, "교통 및 이동"))
        transport = content.get("transport_summary", content.get("transport", {}))
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
        cost_rows = self._build_cost_table_rows(estimates if isinstance(estimates, dict) else {})
        if cost_rows:
            blocks.append(self._table(cost_rows, has_header=True))
        else:
            blocks.append(self._paragraph("비용 데이터를 아직 계산하지 못했습니다."))
        
        blocks.append(self._divider())
        
        # FINAL SUMMARY - 최종 요약 (서술형 스타일)
        final_summary = content.get("final_summary", {})
        if final_summary:
            blocks.append(self._heading(2, "📋 여행 전 체크리스트 & 꿀팁"))
            
            #  예약 필수 - 서술형
            must_reserve = final_summary.get("must_reserve", [])
            if must_reserve:
                blocks.append(self._callout("예약이 필요한 곳", "", "red_background"))
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
                blocks.append(self._callout("비상 연락처", "", "yellow_background"))
                
                emergency_text = "여행 중 긴급 상황이 생기면 아래 현지 번호로 바로 연락하세요. "
                if emergency:
                    emergency_text += (
                        f"통합 신고번호는 **{emergency.get('general', '112')}**, "
                        f"경찰 {emergency.get('police', '112')}, "
                        f"구급/응급 {emergency.get('ambulance', '112')}, "
                        f"소방 {emergency.get('fire', '112')}입니다. "
                    )
                    if emergency.get("tips"):
                        emergency_text += f"현지 안전 메모: {emergency.get('tips')} "
                
                if embassy:
                    emergency_text += (
                        f"\\n\\n영사 지원이 필요하면 **[{embassy.get('name', '현지 한국 공관')}]({embassy.get('website', 'https://overseas.mofa.go.kr')})**에 연락하세요. "
                        f"대표전화 {embassy.get('phone', '-')}, 긴급전화 {embassy.get('emergency_phone', embassy.get('emergency', '-'))}, "
                        f"주소 {embassy.get('address', '재외공관 홈페이지 참고')}."
                    )
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
            blocks.append(self._heading(2, "참고 여행 블로그"))
            blocks.append(self._paragraph("해당 도시에 대한 더 많은 정보는 아래 링크에서 확인하세요:"))
            for link in blog_links[:4]:  # 상위 4개만
                # Only add link if URL is valid
                if link and isinstance(link, str) and link.startswith('http'):
                    blocks.append(self._paragraph(f"• [여행 가이드 보기]({link})"))
                elif link and isinstance(link, str):
                    blocks.append(self._paragraph(f"• {link}"))
        
        # Image Attributions
        blocks.append(self._divider())
        blocks.append(self._heading(2, "이미지 출처"))
        blocks.append(self._paragraph("본 여행 가이드에 사용된 이미지는 다음 출처에서 제공되었습니다. 각 이미지는 해당 플랫폼의 라이선스에 따라 사용되었습니다."))
        
        # 이미지 출처 정보 추가
        if images:
            for i, img in enumerate(images, 1):
                source = img.get("source", "unknown")
                photographer = img.get("photographer", "Unknown")
                
                if source == "unsplash":
                    photographer_url = img.get("photographer_url", "")
                    unsplash_url = img.get("unsplash_url", "")
                    if photographer_url and unsplash_url:
                        attr_text = f"[{i}] Photo by [{photographer}]({photographer_url}) on [Unsplash]({unsplash_url})"
                    else:
                        attr_text = f"[{i}] Photo by {photographer} on Unsplash"
                elif source == "pexels":
                    photographer_url = img.get("photographer_url", "")
                    if photographer_url:
                        attr_text = f"[{i}] Photo by [{photographer}]({photographer_url}) on [Pexels](https://www.pexels.com)"
                    else:
                        attr_text = f"[{i}] Photo by {photographer} on Pexels"
                elif source == "pixabay":
                    attr_text = f"[{i}] Photo by {photographer} on [Pixabay](https://pixabay.com)"
                elif source in ["pexels_static", "static"]:
                    attr_text = f"[{i}] Photo from Pexels (CC0 License)"
                else:
                    attr_text = f"[{i}] Photo source: {source}"
                
                blocks.append(self._paragraph(attr_text, link=img.get("url", "")))
        
        blocks.append(self._paragraph(""))
        blocks.append(self._paragraph("**라이선스 안내:**\n• Unsplash: Unsplash License (Free to use, attribution appreciated)\n• Pexels: Pexels License (Free to use, no attribution required)\n• Pixabay: Pixabay License (Free to use, no attribution required)"))
        
        # Footer
        blocks.append(self._divider())
        blocks.append(self._paragraph(f"작성일: {content.get('generated_at', datetime.now().isoformat())[:10]}"))
        
        logger.info(f"Total blocks created: {len(blocks)}")
        return blocks
