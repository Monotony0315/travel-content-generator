"""
SEO-Enhanced Notion Publisher
SEO 최적화된 제목, 메타 설명, 계층적 헤딩 구조, FAQ, 스키마 마크업 포함
Extends FixedNotionPublisher with full SEO capabilities
"""

from __future__ import annotations

import json
import os
import random
import urllib.parse
import urllib.error
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

from notion.fixed_publisher import FixedNotionPublisher


class SEOEnhancedPublisher(FixedNotionPublisher):
    """SEO 최적화 버전 - FixedNotionPublisher를 확장하여 SEO 요소 추가"""

    def __init__(self):
        super().__init__()
        self.base_canonical_url = os.getenv("BLOG_CANONICAL_URL", "https://travel-blog.example.com")

    # ─── SEO Title ───
    def _generate_seo_title(self, content: Dict) -> str:
        """[YYYY-MM-DD] City, Country | N-Day Complete Travel Guide"""
        dest = content["destination"]
        city = dest["name"]
        country = dest.get("country", "")
        days = dest.get("days", 5)
        date_str = datetime.now().strftime('%Y-%m-%d')
        suffix = random.randint(1000, 9999)
        return f"[{date_str}] {city}, {country} | {days}-Day Complete Travel Guide #{suffix}"

    # ─── URL Slug ───
    def _generate_slug(self, city: str, country: str) -> str:
        date_prefix = datetime.now().strftime('%Y-%m-%d')
        city_slug = city.lower().replace(' ', '-').replace("'", "")
        country_slug = country.lower().replace(' ', '-').replace("'", "") if country else ''
        return f"{date_prefix}-{city_slug}-{country_slug}-travel-guide".strip('-')

    # ─── Meta Description ───
    def _generate_meta_description(self, content: Dict) -> str:
        dest = content["destination"]
        city = dest["name"]
        country = dest.get("country", "")
        days = dest.get("days", 5)
        intro = (content.get("intro", "") or "")[:120]
        return (
            f"{city}, {country} {days}일 완벽 여행 가이드. {intro}… "
            f"최적의 동선, 호텔 추천, 예상 비용, 현지 팁까지 한눈에 확인하세요."
        )

    # ─── Keywords ───
    def _generate_keywords(self, content: Dict) -> List[str]:
        dest = content["destination"]
        city = dest["name"]
        country = dest.get("country", "")
        days = dest.get("days", 5)
        season = self._season_kr()
        return [
            f"{city} travel guide", f"{city} 여행", f"{city} {days}일",
            f"{country} travel", f"{city} 여행코스",
            f"{city} 호텔 추천", f"{city} 맛집", f"{city} 관광지",
            f"{city} 가볼만한 곳", f"{country} 여행",
            f"{city} 자유여행", f"{city} 배낭여행",
            f"{city} 가족여행", f"{city} 커플여행",
            f"{city} {season}", f"{city} best time to visit",
            f"{city} 여행 비용", f"{city} 물가",
            f"{city} 교통", f"{city} 여행 준비물",
        ]

    def _season_kr(self) -> str:
        m = datetime.now().month
        return {m in range(3,6): "봄", m in range(6,9): "여름",
                m in range(9,12): "가을"}.get(True, "겨울")

    # ─── Schema Markup (JSON-LD) ───
    def _generate_schema_markup(self, content: Dict, page_url: str) -> Dict:
        dest = content["destination"]
        city = dest["name"]
        country = dest.get("country", "")
        days = dest.get("days", 5)
        return {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": f"{city}, {country} {days}-Day Complete Travel Guide",
            "description": self._generate_meta_description(content),
            "author": {"@type": "Organization", "name": "Travel Content Generator"},
            "datePublished": datetime.now().isoformat(),
            "dateModified": datetime.now().isoformat(),
            "image": content.get("hero_image_url", ""),
            "articleSection": "Travel Guide",
            "keywords": ", ".join(self._generate_keywords(content)[:10]),
            "about": {
                "@type": "Place",
                "name": city,
                "address": {"@type": "PostalAddress", "addressCountry": country}
            },
            "mainEntityOfPage": {"@type": "WebPage", "@id": page_url}
        }

    # ─── FAQ ───
    def _generate_faq(self, content: Dict, city: str, country: str) -> List[Dict]:
        dest = content.get("destination", {})
        days = dest.get("days", 5)
        return [
            {"q": f"{city} 여행 최적의 시기는 언제인가요?",
             "a": f"{city} 여행은 {dest.get('best_season','4-6월, 9-10월')}이 가장 좋습니다. 날씨가 온화하고 관광객이 상대적으로 적어 여행하기 좋습니다."},
            {"q": f"{city} 여행은 며칠이 적당한가요?",
             "a": f"최소 {days}일을 추천합니다. 주요 명소를 여유롭게 둘러보기 적당합니다."},
            {"q": f"{city}에서 사용하는 통화는 무엇인가요?",
             "a": f"{dest.get('currency','유로 (EUR)')}를 사용합니다. 카드 결제가 가능하지만 소액용 현금을 준비하세요."},
            {"q": f"{city}에서 한국어가 통하나요?",
             "a": "주요 관광지에서 영어가 통합니다. 번역 앱(Google Translate, Papago)을 준비하세요."},
            {"q": f"{city}는 자유여행하기에 안전한가요?",
             "a": f"네, {city}는 안전한 도시입니다. 다만 소매치기에 주의하고 야간에는 주요 거리를 이용하세요."},
            {"q": f"{city} 여행 예상 비용은 얼마인가요?",
             "a": f"가성비 여행 기준 {days}일에 약 50-80만원, 럭셔리 기준 150-250만원 정도입니다."},
        ]

    # ─── Related Destinations ───
    def _get_related_destinations(self, country: str, current_city: str) -> List[Dict]:
        related_map = {
            "France": [
                {"name": "Lyon", "country": "France", "desc": "프랑스의 미식 수도"},
                {"name": "Nice", "country": "France", "desc": "코트다쥐르의 해변 도시"},
                {"name": "Strasbourg", "country": "France", "desc": "크리스마스 마켓의 성지"},
            ],
            "Italy": [
                {"name": "Florence", "country": "Italy", "desc": "르네상스의 발상지"},
                {"name": "Venice", "country": "Italy", "desc": "물 위의 도시"},
                {"name": "Milan", "country": "Italy", "desc": "패션과 디자인의 중심"},
            ],
            "Spain": [
                {"name": "Madrid", "country": "Spain", "desc": "활기찬 수도"},
                {"name": "Seville", "country": "Spain", "desc": "플라멩코의 본고장"},
                {"name": "Valencia", "country": "Spain", "desc": "파에야의 고향"},
            ],
            "UK": [
                {"name": "Edinburgh", "country": "Scotland", "desc": "축제와 역사의 도시"},
                {"name": "Bath", "country": "UK", "desc": "로마 시대 온천 도시"},
            ],
            "Czech Republic": [
                {"name": "Cesky Krumlov", "country": "Czech Republic", "desc": "동화 같은 마을"},
                {"name": "Brno", "country": "Czech Republic", "desc": "체코 제2의 도시"},
            ],
            "Netherlands": [
                {"name": "Rotterdam", "country": "Netherlands", "desc": "현대 건축의 도시"},
                {"name": "Utrecht", "country": "Netherlands", "desc": "운하와 대학의 도시"},
            ],
            "Germany": [
                {"name": "Munich", "country": "Germany", "desc": "맥주와 알프스의 도시"},
                {"name": "Hamburg", "country": "Germany", "desc": "항구와 문화의 도시"},
            ],
            "Austria": [
                {"name": "Salzburg", "country": "Austria", "desc": "모차르트의 고향"},
                {"name": "Hallstatt", "country": "Austria", "desc": "세계에서 가장 아름다운 호숫가 마을"},
            ],
            "Greece": [
                {"name": "Santorini", "country": "Greece", "desc": "하얀 집과 파란 돔의 섬"},
                {"name": "Mykonos", "country": "Greece", "desc": "에게해의 파티 섬"},
            ],
            "Thailand": [
                {"name": "Chiang Mai", "country": "Thailand", "desc": "북부 산악 문화의 중심"},
                {"name": "Phuket", "country": "Thailand", "desc": "안다만해의 해변 천국"},
            ],
            "Japan": [
                {"name": "Kyoto", "country": "Japan", "desc": "천년 고도"},
                {"name": "Osaka", "country": "Japan", "desc": "일본의 주방"},
            ],
        }
        results = related_map.get(country, [
            {"name": "Paris", "country": "France", "desc": "빛의 도시"},
            {"name": "Tokyo", "country": "Japan", "desc": "전통과 현대의 조화"},
            {"name": "New York", "country": "USA", "desc": "세계의 수도"},
        ])
        return [r for r in results if r["name"] != current_city][:3]

    # ─── Highlights ───
    def _extract_highlights(self, content: Dict) -> List[str]:
        dest = content.get("destination", {})
        hl = [
            f"최적 여행 시즌: {dest.get('best_season', 'N/A')}",
            f"추천 여행 기간: {dest.get('days', 5)}일",
            f"현지 통화: {dest.get('currency', 'N/A')}",
        ]
        days_plan = content.get("days_plan", [])
        if days_plan:
            spots = days_plan[0].get("spots", [])
            if spots:
                names = [s.get('name', '') for s in spots[:3]]
                hl.append(f"핵심 명소: {', '.join(names)}")
        return hl

    # ─── Helper block builders ───
    def _bulleted_list_item(self, text: str, bold: bool = False) -> Dict:
        return {"object": "block", "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": self._rt(text, bold)}}

    def _numbered_list_item(self, text: str, bold: bool = False) -> Dict:
        return {"object": "block", "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": self._rt(text, bold)}}

    # ─── SEO Image Caption ───
    def _seo_image_caption(self, city: str, country: str, context: str, photographer: str = "", source: str = "") -> str:
        """Generate descriptive alt text / caption for images"""
        caption = f"{city}, {country} - {context}"
        if photographer and photographer != "Unknown" and photographer != "Pexels":
            caption += f" | 📷 {photographer}"
            if source:
                caption += f" on {source}"
        return caption

    # ═══════════════════════════════════════════════
    #  MAIN PUBLISH (override parent)
    # ═══════════════════════════════════════════════
    async def publish_blog(self, content: Dict, images: List[Dict]) -> str:
        dest = content["destination"]
        city = dest["name"]
        country = dest.get("country", "")

        title = self._generate_seo_title(content)
        slug = self._generate_slug(city, country)
        canonical_url = f"{self.base_canonical_url}/{slug}"

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

        content["canonical_url"] = canonical_url
        if images:
            content["hero_image_url"] = images[0].get("url", "")

        blocks = self._build_seo_blocks(content, images, city, canonical_url)
        total = len(blocks)
        logger.info(f"SEO blocks to publish: {total}")

        batch_size = 95
        for i in range(0, total, batch_size):
            batch = blocks[i:i + batch_size]
            self._request("PATCH", f"/blocks/{page_id}/children", {"children": batch})
            logger.info(f"Added {i+1}-{min(i+len(batch), total)} / {total}")

        return page_url

    # ═══════════════════════════════════════════════
    #  BUILD SEO BLOCKS
    # ═══════════════════════════════════════════════
    def _build_seo_blocks(self, content: Dict, images: List[Dict], city: str, canonical_url: str) -> List[Dict]:
        dest = content["destination"]
        country = dest.get("country", "")
        blocks = []
        days_plan = content.get("days_plan", [])

        meta_desc = self._generate_meta_description(content)
        keywords = self._generate_keywords(content)

        # ── SEO Meta Block ──
        blocks.append(self._callout(f"🔗 Canonical: {canonical_url}", "", "gray_background"))
        blocks.append(self._callout(f"🔍 Keywords: {', '.join(keywords[:12])}", "", "gray_background"))
        blocks.append(self._divider())

        # ── Table of Contents ──
        blocks.append(self._heading(2, "📋 목차 (Table of Contents)"))
        toc_items = ["여행 개요", "추천 호텔"]
        for idx, day in enumerate(days_plan):
            day_num = day.get("day", idx + 1)
            toc_items.append(f"Day {day_num}: {day.get('title','')}")
        toc_items += ["교통 및 이동", "총 예상 비용", "비상연락망", "FAQ", "관련 여행지", "Schema"]
        for item in toc_items:
            blocks.append(self._numbered_list_item(item))
        blocks.append(self._divider())

        # ── Hero Image (SEO caption) ──
        if images:
            hero_caption = self._seo_image_caption(
                city, country, "랜드마크와 명소 풍경",
                images[0].get("photographer", ""), images[0].get("source", "")
            )
            blocks.append(self._image_external(images[0]["url"], hero_caption))

        # ── H1 Title ──
        blocks.append(self._heading(1, f"{city}, {country} {dest['days']}일 완벽 여행 가이드"))
        blocks.append(self._callout(meta_desc, "📝", "blue_background"))
        blocks.append(self._paragraph(
            f"⏱️ {dest['days']}일 | 🌤️ {dest['best_season']} | 💰 {dest['currency']}", bold=True
        ))
        blocks.append(self._divider())

        # ── Intro + Highlights ──
        blocks.append(self._heading(2, "🌍 여행 개요"))
        blocks.append(self._quote(content.get("intro", "")))
        blocks.append(self._heading(3, "✨ 여행 하이라이트"))
        for hl in self._extract_highlights(content):
            blocks.append(self._bulleted_list_item(hl))
        blocks.append(self._divider())

        # ── Hotels ──
        blocks.append(self._heading(2, "🏨 추천 호텔"))
        hotels = content.get("hotels", {})
        for cat, label, color in [("budget", "💰 가성비", "green"), ("luxury", "✨ 럭셔리", "purple")]:
            for h in hotels.get(cat, []):
                blocks.append(self._callout(label, "", f"{color}_background"))
                maps_url = h.get('maps_url', '')
                if maps_url and maps_url.startswith('http'):
                    name_text = f"[{h['name']}]({maps_url}) ★{h['rating']} | {h['price_per_night']} | {h['area']}"
                else:
                    name_text = f"{h['name']} ★{h['rating']} | {h['price_per_night']} | {h['area']}"
                blocks.append(self._paragraph(name_text))
                blocks.append(self._paragraph(f"✅ {h['pros']} | ⚠️ {h['cons']}"))
        blocks.append(self._divider())

        # ── Daily Itinerary (inherits parent logic, adds SEO) ──
        blocks.append(self._heading(2, "📅 일정 상세"))
        for idx, day in enumerate(days_plan):
            day_num = day.get("day", idx + 1)

            # Day image with SEO caption
            img_idx = idx + 1
            if len(images) > img_idx and images[img_idx].get("url"):
                img = images[img_idx]
                caption = self._seo_image_caption(
                    city, country,
                    f"Day {day_num} {day.get('title', '')} 여행 코스",
                    img.get("photographer", ""), img.get("source", "")
                )
                blocks.append(self._image_external(img["url"], caption))

            blocks.append(self._callout(f"📌 Day {day_num}: {day['title']}", "", "blue_background"))
            blocks.append(self._paragraph(f"🎯 테마: {day['theme']}", bold=True))

            # Content paragraphs
            content_text = day.get("content", "").strip()
            for para in content_text.split('\n\n'):
                if para.strip():
                    blocks.append(self._paragraph(para.strip()))

            # Spots (H3)
            spots = day.get("spots", [])
            if spots:
                blocks.append(self._heading(3, f"🗺️ Day {day_num} 주요 장소"))
                for i, spot in enumerate(spots, 1):
                    name = spot['name']
                    maps_url = self._maps_url(f"{name} {city}")
                    res_url = spot.get('reservation_url', '')
                    res_req = spot.get('reservation_required', False)
                    time_str = spot.get('time', '')

                    title_line = f"{i}. [{name}]({maps_url})"
                    if time_str:
                        title_line += f"  ⏰ {time_str}"
                    blocks.append(self._paragraph(title_line))
                    detail = spot.get('desc', '')
                    if spot.get('tip'):
                        detail += f" 💡 {spot['tip']}"
                    if res_req and res_url and res_url.startswith('http'):
                        detail += f" 🎫 [예약하기]({res_url})"
                    blocks.append(self._paragraph(detail))

            # Restaurants (H3)
            restaurants = day.get("restaurants", [])
            if restaurants:
                blocks.append(self._heading(3, f"🍽️ Day {day_num} 추천 식당"))
                for r in restaurants:
                    r_maps = self._maps_url(f"{r['name']} {city}")
                    r_line = f"[{r['name']}]({r_maps}) {r.get('type','')} · {r.get('price','')}"
                    blocks.append(self._paragraph(r_line))
                    if r.get('tip'):
                        blocks.append(self._paragraph(f"→ {r['tip']}"))

            # Day cost
            cost = day.get("estimated_cost", {})
            if cost:
                blocks.append(self._callout(f"💰 합계: {cost.get('total', '')}", "", "yellow_background"))

            # Internal nav to next day
            if idx < len(days_plan) - 1:
                next_title = days_plan[idx+1].get("title", "")
                blocks.append(self._paragraph(f"➡️ 다음: Day {day_num+1} - {next_title}", bold=True))

            blocks.append(self._divider())

        # ── Transport ──
        blocks.append(self._heading(2, "🚗 교통 및 이동"))
        transport = content.get("transport_summary", {})
        for mode, price in transport.items():
            blocks.append(self._bulleted_list_item(f"{mode}: {price}"))
        if dest.get("car_rental_available"):
            parking = content.get("parking_info", {})
            if parking:
                blocks.append(self._heading(3, "🅿️ 주차 정보"))
                blocks.append(self._paragraph(f"난이도: {parking.get('difficulty','')} | 요금: {parking.get('city_center_rate','')}"))
        blocks.append(self._divider())

        # ── Cost Summary ──
        blocks.append(self._heading(2, "💰 총 예상 비용"))
        estimates = content.get("total_estimate", {})
        for level, label, color in [("budget","💚 가성비","green"),("luxury","💜 럭셔리","purple")]:
            est = estimates.get(level, {})
            if not est:
                continue
            blocks.append(self._callout(label, "", f"{color}_background"))
            for k, v in est.items():
                if k != "total":
                    blocks.append(self._bulleted_list_item(f"{k}: {v}"))
            if est.get("total"):
                blocks.append(self._paragraph(f"**총계: {est['total']}**", bold=True))
        blocks.append(self._divider())

        # ── Emergency ──
        blocks.append(self._heading(2, "🚨 비상연락망 & 대사관"))
        final_summary = content.get("final_summary", {})
        emergency = final_summary.get("emergency_contacts", {})
        embassy = final_summary.get("embassy_info", {})
        if emergency:
            blocks.append(self._callout("긴급 신고번호", "🚨", "red_background"))
            label_map = {"police":"👮 경찰","ambulance":"🚑 구급차","fire":"🚒 소방","general":"📞 통합신고"}
            for k, v in emergency.items():
                blocks.append(self._bulleted_list_item(f"{label_map.get(k,k)}: {v}"))
        if embassy:
            blocks.append(self._callout("한국대사관", "🏛️", "blue_background"))
            for field, icon in [("name",""), ("phone","📞"), ("address","📍"), ("emergency_phone","🆘")]:
                if embassy.get(field):
                    blocks.append(self._paragraph(f"{icon} {embassy[field]}"))
            if embassy.get("website"):
                blocks.append(self._paragraph(f"🌐 [대사관 웹사이트]({embassy['website']})"))
        blocks.append(self._divider())

        # ── FAQ (Featured Snippets) ──
        blocks.append(self._heading(2, "❓ 자주 묻는 질문 (FAQ)"))
        faqs = self._generate_faq(content, city, country)
        for faq in faqs:
            blocks.append(self._heading(3, f"Q: {faq['q']}"))
            blocks.append(self._paragraph(f"A: {faq['a']}"))
        blocks.append(self._divider())

        # ── Related Destinations ──
        blocks.append(self._heading(2, "🌎 관련 여행지 추천"))
        for rd in self._get_related_destinations(country, city):
            blocks.append(self._bulleted_list_item(f"{rd['name']}, {rd['country']} - {rd['desc']}"))
        blocks.append(self._divider())

        # ── Hashtags & Keywords ──
        blocks.append(self._heading(2, "🏷️ SEO & 해시태그"))
        seo = content.get("seo", {})
        hashtags = seo.get("hashtags", [])
        if hashtags:
            blocks.append(self._callout("해시태그", "#️⃣", "yellow_background"))
            for i in range(0, len(hashtags), 5):
                blocks.append(self._paragraph(" ".join(hashtags[i:i+5])))
        blocks.append(self._callout("Keywords", "🔍", "gray_background"))
        blocks.append(self._paragraph(", ".join(keywords[:20])))
        blocks.append(self._divider())

        # ── Schema Markup (JSON-LD) ──
        blocks.append(self._heading(2, "📊 Schema Markup (JSON-LD)"))
        blocks.append(self._callout("구조화된 데이터 - 검색엔진용", "🤖", "purple_background"))
        schema = self._generate_schema_markup(content, canonical_url)
        # Notion can't render code blocks via API easily, store as paragraph
        schema_str = json.dumps(schema, ensure_ascii=False, indent=2)
        # Split long schema text
        for chunk in [schema_str[i:i+1800] for i in range(0, len(schema_str), 1800)]:
            blocks.append(self._paragraph(chunk))
        blocks.append(self._divider())

        # ── Image Attributions ──
        if images:
            blocks.append(self._heading(2, "📷 이미지 출처"))
            for i, img in enumerate(images, 1):
                attr = self._get_image_attribution(img)
                blocks.append(self._paragraph(f"[{i}] {attr}"))

        # ── Footer ──
        blocks.append(self._divider())
        blocks.append(self._paragraph(
            f"작성일: {datetime.now().strftime('%Y-%m-%d')} | "
            f"마지막 수정: {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
            f"Canonical: {canonical_url}"
        ))

        logger.info(f"Total SEO blocks: {len(blocks)}")
        return blocks
