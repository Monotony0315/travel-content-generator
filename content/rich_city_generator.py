"""
Rich City Content Generator - Boss's Completed Template Format
Boss's template structure with table of contents, detailed spots, restaurants, and professional formatting
"""

from __future__ import annotations

import json
import os
import re
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger


class RichCityGenerator:
    """Boss's Template 기반 콘텐츠 생성기"""

    def __init__(self):
        self.currency_map = {
            "France": ("유로", "EUR", "€"), "Italy": ("유로", "EUR", "€"),
            "Spain": ("유로", "EUR", "€"), "Germany": ("유로", "EUR", "€"),
            "Netherlands": ("유로", "EUR", "€"), "UK": ("파운드", "GBP", "£"),
            "Thailand": ("바트", "THB", "฿"), "Singapore": ("싱달러", "SGD", "S$"),
            "Japan": ("엔", "JPY", "¥"), "USA": ("달러", "USD", "$"),
            "Czech Republic": ("코루나", "CZK", "Kč"),
            "Maldives": ("달러", "USD", "$"),
        }
        
        self.language_map = {
            "France": "프랑스어", "Italy": "이탈리아어", "Spain": "스페인어",
            "Germany": "독일어", "Netherlands": "네덜란드어", "UK": "영어",
            "Thailand": "태국어", "Singapore": "영어/중국어", "Japan": "일본어",
            "USA": "영어", "Czech Republic": "체코어", "Maldives": "영어",
        }

        self.emergency_numbers = {
            "France": {"police": "17", "ambulance": "15", "fire": "18", "general": "112"},
            "Italy": {"police": "113", "ambulance": "118", "fire": "115", "general": "112"},
            "Spain": {"police": "091", "ambulance": "061", "fire": "080", "general": "112"},
            "Germany": {"police": "110", "ambulance": "112", "fire": "112", "general": "112"},
            "Netherlands": {"police": "112", "ambulance": "112", "fire": "112", "general": "112"},
            "UK": {"police": "999", "ambulance": "999", "fire": "999", "general": "999"},
            "Japan": {"police": "110", "ambulance": "119", "fire": "119", "general": "110"},
            "USA": {"police": "911", "ambulance": "911", "fire": "911", "general": "911"},
            "Thailand": {"police": "191", "ambulance": "1669", "fire": "199", "general": "191"},
            "Singapore": {"police": "999", "ambulance": "995", "fire": "995", "general": "999"},
            "Czech Republic": {"police": "158", "ambulance": "155", "fire": "150", "general": "112"},
            "Austria": {"police": "133", "ambulance": "144", "fire": "122", "general": "112"},
            "Maldives": {"police": "119", "ambulance": "102", "fire": "118", "general": "119"},
        }

        self.embassy_directory = {
            "France": {"name": "주프랑스 한국대사관", "phone": "+33-1-47-53-01-01", "emergency_phone": "+33-1-47-53-01-01", "address": "125 rue de Grenelle, 75007 Paris", "website": "https://overseas.mofa.go.kr/fr-ko/index.do"},
            "Italy": {"name": "주이탈리아 한국대사관", "phone": "+39-06-802-461", "emergency_phone": "+39-06-802-461", "address": "Via Barnaba Oriani 30, 00197 Roma", "website": "https://overseas.mofa.go.kr/it-ko/index.do"},
            "Spain": {"name": "주스페인 한국대사관", "phone": "+34-91-353-2000", "emergency_phone": "+34-91-353-2000", "address": "C/ González Amigó 15, 28033 Madrid", "website": "https://overseas.mofa.go.kr/es-ko/index.do"},
            "Germany": {"name": "주독일 한국대사관", "phone": "+49-30-260-650", "emergency_phone": "+49-30-260-650", "address": "Stülerstraße 10, 10787 Berlin", "website": "https://overseas.mofa.go.kr/de-ko/index.do"},
            "Netherlands": {"name": "주네덜란드 한국대사관", "phone": "+31-70-740-0200", "emergency_phone": "+31-70-740-0200", "address": "Verlengde Tolweg 8, 2517 JV Den Haag", "website": "https://overseas.mofa.go.kr/nl-ko/index.do"},
            "UK": {"name": "주영국 한국대사관", "phone": "+44-20-7227-5500", "emergency_phone": "+44-20-7227-5500", "address": "60 Buckingham Gate, London SW1E 6AJ", "website": "https://overseas.mofa.go.kr/gb-ko/index.do"},
            "Japan": {"name": "주일본 한국대사관", "phone": "+81-3-3452-7611", "emergency_phone": "+81-3-3452-7611", "address": "1-2-5 Minami-Azabu, Minato-ku, Tokyo 106-0047", "website": "https://overseas.mofa.go.kr/jp-ko/index.do"},
            "USA": {"name": "주미국 한국대사관", "phone": "+1-202-939-5600", "emergency_phone": "+1-202-939-5600", "address": "2450 Massachusetts Ave NW, Washington, DC 20008", "website": "https://overseas.mofa.go.kr/us-ko/index.do"},
            "Thailand": {"name": "주태국 한국대사관", "phone": "+66-2-247-7530", "emergency_phone": "+66-2-247-7530", "address": "23 Thiam-Ruammit Road, Ratchadaphisek, Huai Khwang, Bangkok 10310", "website": "https://overseas.mofa.go.kr/th-ko/index.do"},
            "Singapore": {"name": "주싱가포르 한국대사관", "phone": "+65-6256-1188", "emergency_phone": "+65-6256-1188", "address": "47 Scotts Road, #08-00 Goldbell Towers, Singapore 228233", "website": "https://overseas.mofa.go.kr/sg-ko/index.do"},
            "Czech Republic": {"name": "주체코 한국대사관", "phone": "+420-2-5732-1355", "emergency_phone": "+420-2-5732-1355", "address": "Slavíčkova 5, 160 00 Praha 6", "website": "https://overseas.mofa.go.kr/cz-ko/index.do"},
            "Austria": {"name": "주오스트리아 한국대사관", "phone": "+43-1-478-1991", "emergency_phone": "+43-1-478-1991", "address": "Gregor-Mendel-Strasse 25, 1180 Wien", "website": "https://overseas.mofa.go.kr/at-ko/index.do"},
            "Maldives": {"name": "주스리랑카 한국대사관(몰디브 겸임)", "phone": "+94-11-269-9036", "emergency_phone": "+94-11-269-9036", "address": "98 Dharmapala Mawatha, Colombo 00700, Sri Lanka", "website": "https://overseas.mofa.go.kr/lk-ko/index.do"},
        }

        self.krw_rates = {
            "France": 1480, "Italy": 1480, "Spain": 1480, "Germany": 1480, "Netherlands": 1480,
            "UK": 1730, "United Kingdom": 1730, "Czech Republic": 59, "Singapore": 1010, "Thailand": 39.5,
            "Japan": 9.2, "USA": 1380, "Switzerland": 1620, "Australia": 905, "New Zealand": 815,
            "Maldives": 90, "India": 16.4, "Vietnam": 0.059, "China": 192, "Austria": 1480, "Portugal": 1480,
        }
        
        self._city_data_cache = {}

        self.city_style_profiles = {
            "Europe": {
                "intro": {
                    "opening": "{{city}}는 시간표보다 분위기가 먼저 닿는 도시야. 이 동선은 가볍게 시작해도 마지막엔 기억이 남는 구조로 설계했어.",
                    "closing": "도심보다 골목, 유명지보다 여유 지점에서 도시가 가장 잘 보여."
                },
                "day_openings": [
                    "{city}를 걷는 첫 3시간은 과감한 이동보다 정리를 위한 시간으로 잡는 게 좋아.",
                    "{day_theme}이라면 오후 감정이 살아나는 타이밍을 잡아야 한다.",
                    "명소 자체보다 동선의 결이 더 중요해요. 천천히 가면 오히려 세밀함이 살아납니다."
                ],
                "daily_themes": {
                    1: {"title": "도착과 도시의 첫 호흡", "theme": "느긋한 시작"},
                    2: {"title": "고전과 풍경의 중심선", "theme": "핵심 루프"},
                    3: {"title": "현지 이야기 탐색", "theme": "문화 심화 탐험"},
                    4: {"title": "일상과 야간의 균형", "theme": "저녁 동선 압축"},
                    5: {"title": "마지막 정리와 회복", "theme": "감각의 마무리"},
                }
            },
            "Island": {
                "intro": {
                    "opening": "{{city}}는 바람과 바다의 리듬이 일정을 좌우해요. 시간표보다 체력 페이스가 더 중요해요.",
                    "closing": "휴식 시간대를 동선에 미리 넣으면 한일이 훨씬 정돈됩니다."
                },
                "day_openings": [
                    "오늘은 수상 동선, 휴식, 식사 리듬을 3단계로 나눠서 움직이자.",
                    "물과 야외 활동은 오전/오후 분리형으로 잡아야 무리감이 줄어요.",
                    "이 도시의 베이스는 이동 간격이므로 지나치게 촘촘하게 조정하지 마세요."
                ],
                "daily_themes": {
                    1: {"title": "도착 정돈", "theme": "시차와 이동 안정"},
                    2: {"title": "해양 동선 정리", "theme": "물 위 일정"},
                    3: {"title": "식음과 여유의 중심", "theme": "회복형 탐방"},
                    4: {"title": "휴식 기반 탐험", "theme": "천천히 보기"},
                    5: {"title": "라군 마무리", "theme": "감정 정리"},
                }
            },
        }

    def _get_city_data(self, city: str, country: str) -> Dict:
        """도시별 데이터"""
        if city in self._city_data_cache:
            return self._city_data_cache[city]
        
        data = CITY_DATABASE.get(city, None)
        if data:
            self._city_data_cache[city] = data
            return data
        
        return self._build_default_data(city, country)

    def _build_default_data(self, city: str, country: str) -> Dict:
        """기본 데이터 생성"""
        cur_name, _, cur_sym = self.currency_map.get(country, ("달러", "USD", "$"))
        return {
            "spots": [
                {"name": f"{city} 도심 시작", "desc": f"{city}의 중심가에서 이동 동선을 짜기 가장 좋은 출발점", "duration": "1.5시간", "fee": "무료", "time": "오전 08:30-10:00", "reservation_required": False},
                {"name": f"{city} 대표 박물관", "desc": "여행의 포인트를 잡기 좋은 핵심 동선", "duration": "2.5시간", "fee": "입장료 별도", "time": "오전 10:30-13:00", "reservation_required": False},
                {"name": f"{city} 강변 산책로", "desc": "오후 집중 동선을 완화하고 이동의 호흡을 맞추는 지점", "duration": "1.5시간", "fee": "무료", "time": "오후 13:30-15:30", "reservation_required": False},
                {"name": f"{city} 야경 라인", "desc": "일몰 동선을 구성하기 좋은 저녁 코스", "duration": "1.5시간", "fee": "무료", "time": "저녁 17:00-19:00", "reservation_required": False},
            ],
            "restaurants": [
                {"name": f"{city} Boulangerie", "type": "브런치", "price": f"12-20{cur_sym}", "signature": ["플랫브레드", "오믈렛"], "price_tier": "budget"},
                {"name": f"{city} Bistro", "type": "현지식", "price": f"20-35{cur_sym}", "signature": ["파스타", "시저샐러드"], "price_tier": "mid"},
                {"name": f"{city} Fine Dining", "type": "고급 다이닝", "price": f"80-140{cur_sym}", "signature": ["코스", "화이트와인 페어링"], "price_tier": "luxury", "reservation_required": True},
            ],
            "hotels": {
                "budget": [{"name": f"{city} Hotel", "rating": 4.0, "price_per_night": f"{cur_sym}80", "area": "중심가", "pros": "위치 좋음", "cons": "방 작음", "maps_url": f"https://maps.google.com/?q={city}+hotel"}],
                "mid": [{"name": f"{city} Central Hotel", "rating": 4.4, "price_per_night": f"{cur_sym}140-220", "area": "중심가", "pros": "이동 동선 우수", "cons": "가격대 변동", "maps_url": f"https://maps.google.com/?q={city}+hotel+central"}],
                "luxury": [{"name": f"{city} Grand", "rating": 4.8, "price_per_night": f"{cur_sym}300", "area": "럭셔리존", "pros": "서비스", "cons": "비쌈", "maps_url": f"https://maps.google.com/?q={city}+luxury"}],
            }
        }

    def generate_rich_content(self, city: str, country: str, region: str, days: int = 5) -> Dict:
        """Boss's Template 기반 콘텐츠 생성"""
        cur_name, cur_code, cur_sym = self.currency_map.get(country, ("달러", "USD", "$"))
        language = self.language_map.get(country, "현지 언어")
        
        city_data = self._get_city_data(city, country)
        spots = city_data.get("spots", [])
        restaurants = city_data.get("restaurants", [])
        hotels = city_data.get("hotels", {})
        
        days_plan = self._generate_boss_template_days(city, country, region, spots, restaurants, days, cur_sym)
        
        trip_intro = self._build_trip_opening(city, country, region, days, spots)

        emergency = self._resolve_emergency_contacts(country, city_data.get("emergency_contacts"))
        embassy = self._resolve_embassy_info(country, city_data.get("embassy_info"))
        final_summary = {
            "must_reserve": self._generate_must_reserve_list(spots, restaurants),
            "emergency_contacts": {
                "police": emergency.get("police", "112"),
                "ambulance": emergency.get("ambulance", "112"),
                "fire": emergency.get("fire", "112"),
                "general": emergency.get("general", "112"),
                "tips": emergency.get("tips", ""),
            },
            "embassy_info": {
                "name": embassy.get("name", "해당국 한국대사관"),
                "phone": embassy.get("phone", ""),
                "emergency_phone": embassy.get("emergency_phone", embassy.get("emergency", embassy.get("phone", ""))),
                "address": embassy.get("address", ""),
                "website": embassy.get("website", "https://overseas.mofa.go.kr"),
                "hours": embassy.get("hours", "평일 09:00-12:00, 13:30-18:00"),
            },
            "packing_checklist": self._get_packing_list(region),
            "travel_tips": self._get_travel_tips(country),
            "safety_tips": self._get_safety_tips(country),
            "money_tips": self._get_money_tips(country, cur_sym),
            "essential_apps": self._get_essential_apps(),
            "useful_links": self._get_useful_links(city, country),
        }

        return {
            "title": f"{city} 여행 완벽 가이드 | {days}일 일정",
            "intro": trip_intro,
            "destination": {
                "name": city, "country": country,
                "best_season": self._get_best_season(region),
                "currency": f"{cur_name} ({cur_code})",
                "language": language, "days": days,
            },
            "table_of_contents": self._generate_table_of_contents(days),
            "overview": self._generate_overview(city, country, region, cur_name, cur_code, days, spots),
            "hotels": hotels,
            "days_plan": days_plan,
            "restaurants": self._build_global_restaurant_catalog(days_plan, city),
            "tips": {
                "weather_check": "오전/오후 시간대별 혼잡도와 날씨 변화에 맞춰 코스를 조정하세요.",
                "photo_tips": "일출/황혼 타임은 조도와 인파가 좋아 기록용으로 최고입니다.",
            },
            "transport": self._generate_transport_section(city, country, cur_sym),
            "total_estimate": self._calculate_total_costs(country, cur_sym, days),
            "emergency": {"contacts": emergency, "embassy": embassy},
            "faq": self._generate_faq(city, country, region, days),
            "related_destinations": self._generate_related_destinations(city, country, region),
            "must_reserve": self._generate_must_reserve_list(spots, restaurants),
            "visit_statistics": self._build_visit_statistics(city, country, region, days, spots, restaurants, hotels),
            "final_summary": final_summary,
            "generated_at": datetime.now().isoformat(),
        }

    def _get_travel_tips(self, country: str):
        return [
            "도시권 중심으로 이동할수록 보행 동선을 짧게, 대중교통은 1회전으로 설계하세요.",
            "점심시간 전후 1시간은 무리한 이동 대신 버퍼로 잡으면 일정 피로도가 크게 줄어요.",
            f"{country} 이동은 현지 교통 앱 알림으로 실시간 변동에 대응하세요.",
        ]

    def _get_safety_tips(self, country: str):
        return [
            "밤길은 이동 동선을 분할해 다니고, 과한 소지품은 휴대량을 줄이세요.",
            "택시/대중교통 이용 시 영수증 보관을 습관화하세요.",
            "현금은 소액 분산 보관, 여권 사본은 별도 보관소에 두세요.",
        ]

    def _get_money_tips(self, country: str, cur_sym: str):
        return {
            "exchange": f"{country} 현지 화폐를 소액 위주로 미리 확보하고, 나머지는 ATM/카드로 분산 결제하세요.",
            "card": "주요 상점은 카드가 가능하지만, 소액 현금을 같이 준비하면 유리해요.",
            "cash": "교통권·야간 마켓·팁·비상시를 위한 소액 현금",
            "atm": "ATM 이용 전 수수료·환율 우대 시간을 먼저 확인하세요.",
            "symbol": cur_sym,
        }

    def _get_essential_apps(self):
        return [
            {"name": "Google Maps", "purpose": "네비게이션/대중교통", "url": "https://maps.google.com"},
            {"name": "Google Translate", "purpose": "실시간 번역", "url": "https://translate.google.com"},
            {"name": "XE Currency", "purpose": "환율 계산", "url": "https://www.xe.com"},
            {"name": "TripAdvisor", "purpose": "리뷰 비교", "url": "https://www.tripadvisor.com"},
            {"name": "Citymapper", "purpose": "대중교통 최적 경로", "url": "https://citymapper.com"},
        ]

    def _get_useful_links(self, city: str, country: str):
        return [
            f"{city} 공식 관광 사이트(도시 홈페이지)",
            f"{country} 대중교통 정보",
            "한국 외교부 재외공관 긴급 안내", "여권분실/분실 신고(재외국민 안내)"
        ]

    def _resolve_emergency_contacts(self, country: str, city_contacts: Optional[Dict]) -> Dict:
        defaults = self.emergency_numbers.get(country, {"police": "112", "ambulance": "112", "fire": "112", "general": "112"})
        merged = dict(defaults)
        if isinstance(city_contacts, dict):
            for key in ("police", "ambulance", "fire", "general", "tips"):
                val = city_contacts.get(key)
                if val:
                    merged[key] = str(val)
        return merged

    def _resolve_embassy_info(self, country: str, city_embassy: Optional[Dict]) -> Dict:
        base = dict(self.embassy_directory.get(country, {
            "name": "현지 한국 공관 안내",
            "phone": "",
            "emergency_phone": "",
            "address": "해당 국가 재외공관 안내 페이지 참고",
            "website": "https://overseas.mofa.go.kr",
        }))
        if isinstance(city_embassy, dict):
            for src, dst in [("name", "name"), ("phone", "phone"), ("emergency_phone", "emergency_phone"), ("emergency", "emergency_phone"), ("address", "address"), ("website", "website"), ("hours", "hours")]:
                val = city_embassy.get(src)
                if val:
                    base[dst] = str(val)

        # 잘못 들어간 한국 국내 번호(+82)는 국가별 공관 기본값으로 교정
        phone = str(base.get("phone", ""))
        emergency_phone = str(base.get("emergency_phone", ""))
        if phone.startswith("+82") and country != "Korea":
            fallback = self.embassy_directory.get(country, {})
            base["phone"] = fallback.get("phone", "")
        if emergency_phone.startswith("+82") and country != "Korea":
            fallback = self.embassy_directory.get(country, {})
            base["emergency_phone"] = fallback.get("emergency_phone", fallback.get("phone", ""))
        return base

    def _build_visit_statistics(self, city, country, region, days, spots, restaurants, hotels):
        city_data = self._get_city_data(city, country)
        season = self._get_best_season(region)
        spot_cnt = len(spots or [])
        rest_cnt = len(restaurants or [])
        return {
            "장점": [
                f"도시: {city}",
                f"권장 기간: {days}일",
                f"최적 시즌: {season}",
            ],
            "콘텐츠 밀도": {
                "명소": f"일정에 노출되는 핵심 명소 {spot_cnt}곳",
                "식당": f"동선 기반 후보 {rest_cnt}곳",
                "호텔": f"예산구간 {len(hotels.get('budget', [])) + len(hotels.get('mid', [])) + len(hotels.get('luxury', []))}개",
            },
            "방문 패턴": {
                "추천 방문 밀도": "오전 집중 2곳, 오후 집중 2곳, 저녁 휴식 동선 1곳",
                "비성수기 가점": "오후/저녁 조합으로 라운드 트립 비용/피로도 절감",
            },
            "데이터 출처": city_data.get("overview_source", "내부 city DB + 실제 리뷰 인사이트")
        }

    def _generate_table_of_contents(self, days: int) -> List[Dict]:
        """목차 생성"""
        toc = [{"title": "도시 소개", "anchor": "overview"}, {"title": "추천 호텔", "anchor": "hotels"}]
        for i in range(1, days + 1):
            toc.append({"title": f"Day {i}", "anchor": f"day{i}"})
        toc.extend([
            {"title": "교통 및 이동", "anchor": "transport"},
            {"title": "총 예상 비용", "anchor": "costs"},
            {"title": "비상연락처", "anchor": "emergency"},
            {"title": "FAQ", "anchor": "faq"},
            {"title": "관련 여행지", "anchor": "related"},
        ])
        return toc

    def _generate_overview(self, city, country, region, cur_name, cur_code, days, spots):
        """Overview 섹션"""
        top_spots = [s["name"] for s in spots[:5]] if spots else [f"{city} 명소"]
        return {
            "intro_paragraphs": [
                f"{city}는 {country}의 매력적인 도시로, 여행자들에게 특별한 추억을 선사하는 곳이에요.",
                f"이 가이드는 실제 방문자 후기를 바탕으로 만들었어요. {days}일 동안 무리하지 않는 일정으로 즐기실 수 있어요.",
            ],
            "highlights": {
                "best_season": self._get_best_season(region),
                "recommended_duration": f"{days}일",
                "currency": f"{cur_name} ({cur_code})",
                "top_attractions": top_spots,
            },
            "schema": {"@context": "https://schema.org", "@type": "TravelGuide", "name": f"{city} 여행 가이드"},
        }



    def _build_trip_opening(self, city: str, country: str, region: str, days: int, spots) -> str:
        """여행 블로거 톤의 서두 문단 생성"""
        top_spots = [spt.get("name", "") for spt in spots[:3] if spt.get("name")]
        top_spots_text = ", ".join(top_spots) if top_spots else f"{city}의 골목과 역사"
        profile = self._pick_style_profile(city, country, region)

        opening = profile.get("intro", {}).get("opening", "")
        if "{{city}}" in opening:
            opening = opening.replace("{{city}}", city)

        para1 = (
            f"{opening or city + '는 첫 발을 딛는 순간부터 리듬이 달라져요.'} "
            f"{days}일 동안 {top_spots_text}을 중심으로, 동선을 채우는 대신 장면을 남기는 방식으로 짜봤습니다."
        )

        para2 = (
            "체크리스트가 아니라 동선의 숨 쉬는 간격이 중요해요. 같은 장소라도 시간대와 조명, 바람, 소리의 무드가 바뀌면 체감이 완전히 달라집니다. "
            f"그래서 하루는 아침/오후/저녁으로 분할해 과밀감을 줄이고, 이동은 짧게, 체류는 조금 더 길게 잡았습니다."
        )

        profile_close = profile.get("intro", {}).get("closing", "")
        para3 = (
            f"실행 요령은 간단해요. 1) 오전엔 이동 동선 고정, 2) 낮엔 핵심 체험 2개, 3) 저녁엔 기록 정리. "
            f"이 패턴이 몰입도도 올리고 피로도는 낮춥니다."
        )
        if profile_close:
            para3 += f" {profile_close}"
        return f"{para1}\n\n{para2}\n\n{para3}"


    def _pick_style_profile(self, city: str, country: str, region: str) -> dict:
        if city in self.city_style_profiles:
            return self.city_style_profiles[city]
        if region in self.city_style_profiles:
            return self.city_style_profiles[region]
        if region in ("유럽", "Europe", "유럽권"):
            return self.city_style_profiles.get("Europe")
        if country in ("Maldives", "말레이", "몰디브") or city == "Maldives":
            return self.city_style_profiles.get("Island")
        if country in ("태국", "미국", "USA"):
            return self.city_style_profiles.get("Island")
        return self.city_style_profiles.get("Europe")

    def _profile_day_opening(self, day_num: int, theme: str, city: str, country: str, region: str) -> str:
        profile = self._pick_style_profile(city, country, region)
        templates = profile.get("day_openings", [])
        if not templates:
            return f"{theme}을(를) 중심으로 오늘의 흐름을 잡아보시면 좋아요."
        idx = (day_num - 1) % len(templates)
        template = templates[idx]
        return template.format(day_theme=theme, city=city)

    def _normalize_text_value(self, value: str) -> str:
        if not isinstance(value, str):
            return value
        replacements = {
            "묣료": "무료",
        }
        out = value
        for k, v in replacements.items():
            out = out.replace(k, v)
        return out.strip()

    @staticmethod
    def _extract_numeric_price(text: str) -> int:
        if not isinstance(text, str):
            return 0
        nums = [n.replace(",", "") for n in __import__("re").findall(r"(\d+)", text)]
        if not nums:
            return 0
        return int(nums[0])

    @classmethod
    def _parse_price_mid(cls, price: str) -> int:
        if not isinstance(price, str):
            return 0
        import re
        nums = re.findall(r"(\d+)", price.replace(",", ""))
        if not nums:
            return 0
        vals = [int(n) for n in nums]
        return sum(vals)//len(vals)

    def _fmt_money(self, amount: int, country: str) -> str:
        if not isinstance(amount, (int, float)):
            return ""
        cur_name, cur_code, _ = self.currency_map.get(country, ("달러", "USD", "$"))
        return f"{amount}{cur_code}"

    def _to_krw(self, amount: int, country: str) -> str:
        if not isinstance(amount, (int, float)):
            return ""
        return f"약 {self._to_krw_value(amount, country):,}원"

    def _to_krw_value(self, amount: float, country: str) -> int:
        rate = float(self.krw_rates.get(country, 1380))
        return int(round(float(amount) * rate))

    def _to_currency_and_krw(self, text: str, country: str, currency_symbol: str) -> str:
        amount = self._parse_price_mid(text)
        if not amount:
            return str(text)
        return f"{text} (~{self._fmt_money(amount, country)} / {self._to_krw(amount, country)})"

    def _pick_tiered_restaurants(self, restaurants: list, limit_per_tier: int = 1):
        tiers = {"budget": [], "mid": [], "luxury": []}
        for r in restaurants or []:
            tier = (r.get("price_tier") or self._infer_price_tier(r.get("price", ""))).lower()
            if tier not in tiers:
                tier = "mid"
            tiers.setdefault(tier, []).append(r)
        return {
            "budget": tiers.get("budget", [])[:limit_per_tier],
            "mid": tiers.get("mid", [])[:limit_per_tier],
            "luxury": tiers.get("luxury", [])[:limit_per_tier],
        }

    def _restaurant_tier_markdown(self, restaurants: list, country: str, day_num: int, cur_sym: str) -> str:
        labels = {"budget": "가성비", "mid": "일반", "luxury": "고급"}
        lines = [f"Day {day_num} 식당 추천 (동선 기준 3티어)"]

        tiers = self._pick_tiered_restaurants(restaurants)
        for tier_key, rows in tiers.items():
            if not rows:
                continue
            r = rows[0]
            name = r.get("name", "")
            maps = r.get("maps_url", "")
            if maps:
                name = f"[{name}]({maps})"
            typ = r.get("type") or r.get("cuisine") or "현지식"
            price = r.get("price", "")
            price_krw = self._to_currency_and_krw(price, country, cur_sym)
            tip = (r.get("tip") or "").strip()
            tip = f" - {tip}" if tip else ""
            lines.append(f"- {labels.get(tier_key, tier_key)} {name} — {typ} | {price_krw}{tip}")

        if len(lines) == 1:
            return ""
        # ensure always 3 tiers visually
        for key in ["budget", "mid", "luxury"]:
            if key not in tiers or not tiers[key]:
                title = labels.get(key)
                lines.append(f"- {title} 추천: 동선 내 후보 탐색 필요 (현지 지도 기준 1곳 추가 추천 예정)")

        return "\n".join(lines)

    def _generate_boss_template_days(self, city, country, region, spots, restaurants, days, cur_sym):
        """Boss's Template 일별 일정 생성"""
        themes = self._get_daily_themes(city, country, region)
        plan = []

        for day_num in range(1, days + 1):
            theme = themes.get(day_num, {"title": f"Day {day_num}", "theme": "자유 탐방"})

            # 명소/식당 분배
            spots_per_day = 3
            s_start = (day_num - 1) * spots_per_day
            day_spots = spots[s_start:s_start + spots_per_day] if spots else []
            day_restaurants = restaurants[day_num - 1:day_num + 1] if restaurants else []

            # Google Maps URL 추가
            for spot in day_spots:
                if "maps_url" not in spot:
                    spot["maps_url"] = f"https://www.google.com/maps/search/?api=1&query={__import__('urllib.parse').parse.quote(spot['name'] + ' ' + city)}"
            for r in day_restaurants:
                if "maps_url" not in r:
                    r["maps_url"] = f"https://www.google.com/maps/search/?api=1&query={__import__('urllib.parse').parse.quote(r['name'] + ' ' + city)}"

            # 주요 장소 상세 정보
            spots_detail = []
            for i, spot in enumerate(day_spots, 1):
                spots_detail.append({
                    "order": i,
                    "time": spot.get("time", f"오전 {9+i}:00"),
                    "name": spot["name"],
                    "maps_url": spot.get("maps_url", ""),
                    "description": self._normalize_text_value(spot.get("desc", "")),
                    "history": spot.get("history", ""),
                    "duration": spot.get("duration", "1-2시간"),
                    "fee": self._normalize_text_value(spot.get("fee", "무료")),
                    "reservation_required": spot.get("reservation_required", False),
                    "reservation_url": spot.get("reservation_url", ""),
                    "tip": spot.get("tip", ""),
                })

            # 추천 식당
            restaurants_detail = []
            for r in day_restaurants:
                signatures = r.get("signature", [])
                if isinstance(signatures, list):
                    recommended_menu = ", ".join([str(x) for x in signatures[:2] if x]) or r.get("recommended_menu", "")
                else:
                    recommended_menu = str(r.get("recommended_menu", ""))
                restaurants_detail.append({
                    "name": r["name"],
                    "maps_url": r.get("maps_url", ""),
                    "cuisine": r.get("cuisine", r.get("type", "현지식")),
                    "type": r.get("type", r.get("cuisine", "현지식")),
                    "price": r.get("price", f"20{cur_sym}"),
                    "signature": signatures if isinstance(signatures, list) else [],
                    "recommended_menu": recommended_menu,
                    "pros": r.get("pros", self._default_restaurant_pros(r)),
                    "cons": r.get("cons", self._default_restaurant_cons(r)),
                    "tip": self._normalize_text_value(r.get("tip", "")),
                    "reservation_required": r.get("reservation_required", False),
                    "reservation_url": r.get("reservation_url", ""),
                    "price_tier": r.get("price_tier") or self._infer_price_tier(r.get("price", f"20{cur_sym}")),
                })

            # Day 비용 계산
            day_cost = self._calculate_day_cost(day_restaurants, day_spots, cur_sym, day_num, days)

            # 예약 필요 여부
            needs_reservation = any(s.get("reservation_required") for s in day_spots)
            reservation_notice = ""
            if needs_reservation:
                reservation_names = [s["name"] for s in day_spots if s.get("reservation_required")]
                reservation_notice = f"오늘 방문할 {', '.join(reservation_names)}은(는) 사전 예약이 필요합니다."

            plan.append({
                "day": day_num,
                "title": theme["title"],
                "theme": theme["theme"],
                "reservation_notice": reservation_notice,
                "intro": self._get_day_intro(city, country, region, day_num, days, theme),
                "content": self._build_day_story(
                    city,
                    country,
                    region,
                    day_num,
                    theme,
                    day_spots,
                    day_restaurants,
                    days,
                    restaurants,
                    cur_sym,
                ),
                "spots": spots_detail,
                "restaurants": restaurants_detail,
                "summary_cost": day_cost,
                "restaurant_markdown": self._restaurant_tier_markdown(restaurants, country, day_num, cur_sym),
                "next_day_link": f"day{day_num+1}" if day_num < days else "transport",
            })

        return plan
    def _build_day_story(self, city: str, country: str, region: str, day_num: int, theme: Dict, day_spots: list, day_restaurants: list, total_days: int, restaurants_pool: list = None, cur_sym: str = "") -> str:
        """일자별 여행블로거 느낌의 풍성한 감성 문단 생성"""
        if not day_spots:
            return (
                f"{day_num}일차는 날씨와 기분에 따라 가볍게 변주해도 좋아요. "
                f"동선은 짧고 탄탄하게 잡되, 현지 풍경을 천천히 감상하는 방식으로 가시면 좋아요."
            )

        if restaurants_pool is None:
            restaurants_pool = list(day_restaurants)

        first = day_spots[0]
        last = day_spots[-1]
        opening = (
            f"{day_num}일차는 {theme.get('theme', '느긋한 탐방')}을 중심으로 시작해요. "
            f"{self._profile_day_opening(day_num, theme.get('theme', '탐색'), city, country, region)}"
        )

        def _by_tag(tag: str):
            return [s for s in day_spots if tag in (s.get("time", "") or "")]

        morning = _by_tag("오전")
        if not morning:
            morning = day_spots[:1]
        afternoon = [s for s in day_spots if s not in morning and ("오후" in (s.get("time", "") or "") or "점심" in (s.get("time", "") or "") or "낮" in (s.get("time", "") or ""))]
        if not afternoon:
            afternoon = day_spots[1:3] if len(day_spots) > 1 else []
        evening = [s for s in day_spots if s not in morning + afternoon]

        def _to_lines(items, label):
            if not items:
                return []
            lines = [f"{label}"]
            for s in items:
                sname = s.get("name", "장소")
                time = s.get("time", "")
                desc = s.get("description", s.get("desc", ""))
                dur = s.get("duration", "")
                fee = s.get("fee", "")
                tip = s.get("tip", "")
                map_url = s.get("maps_url", "")
                place_anchor = f"[{sname}]({map_url})" if map_url else sname
                fee_text = f" · 입장료 {fee}" if fee else ""
                tip_text = f" · 팁: {tip}" if tip else ""
                stay_text = f" [체류 {dur}]" if dur else ""
                lines.append(f"- {place_anchor} ({time}) — {desc}{fee_text}{tip_text}{stay_text}")
            return lines

        route_lines = []
        route_lines.extend(_to_lines(morning, "오전"))
        route_lines.extend(_to_lines(afternoon, "오후"))
        route_lines.extend(_to_lines(evening, "저녁"))
        route_text = "\n".join(route_lines).strip()

        rest_md = self._restaurant_tier_markdown(restaurants_pool, country, day_num, cur_sym)


        closing = (
            f"{theme.get('title', '이 날')}은(는) {last.get('time', '저녁')} 마지막 동선인 {last.get('name', '저녁 구간')}에서 마무리하면 "
            f"기록하고 돌아보는 리듬이 가장 선명해져요."
        )
        if day_num < total_days:
            closing += " 예상치 못한 장면이 생기면 동선은 10분만 늘리고 다음 방문지를 20분 앞당겨도 충분해요."
        else:
            closing += " 마지막 날은 돌아보는 동선이 가장 오래 남아요."

        return "\n\n".join([
            opening,
            route_text,
            rest_md,
            closing,
        ]).strip()


    def _get_day_intro(self, city, country, region, day, total_days, theme):
        """일별 소개 (개인적 톤)"""
        if day == 1:
            return f"{theme.get('theme', '도착')}의 첫걸음은 동선보다 감정을 먼저 채우는 날이에요. {city}에 몸을 맡기고, 오늘의 보폭은 조금씩 키워보세요."
        elif day == total_days:
            return f"{city}의 마지막 날은 천천히 걷고, 마지막 장면을 오래 음미하는 날이에요. {theme.get('theme', '마무리')}으로 하루를 정리하세요."
        else:
            return f"{city}의 {theme.get('theme', '특별한 날')}은 기록보다 체험이 먼저인 날이에요. "                    f"한 곳에 오래 머물고, 작은 풍경을 놓치지 말고 지나가세요."

    def _generate_transport_section(self, city, country, cur_sym):
        """교통 정보 섹션"""
        return {
            "airport_to_city": f"공항에서 시내까지",
            "public_transport": f"대중교통: 2-3{cur_sym}",
            "taxi": f"택시: 기본 3-5{cur_sym}",
            "tips": ["교통카드 구매 추천", "피크타임 피하기"],
        }

    def _generate_faq(self, city, country, region, days):
        """FAQ 섹션"""
        return [
            {"question": f"{city} 여행 최적의 시기는?", "answer": f"{self._get_best_season(region)}이 가장 좋아요."},
            {"question": "얼마나 일찍 예약해야 하나요?", "answer": "호텔은 2-3개월 전, 항공은 3-6개월 전 예약을 추천드려요."},
            {"question": f"{days}일이면 충분한가요?", "answer": f"핵심 명소를 보기에는 충분하지만, 여유롭게 즐기려면 {days+2}일 정도를 추천드려요."},
        ]

    def _generate_related_destinations(self, city, country, region):
        """관련 여행지"""
        related = {
            "UK": ["에든버러", "옥스퍼드", "캠브리지"],
            "France": ["니스", "리옹", "스트라스부르"],
            "Italy": ["피렌체", "베네치아", "밀라노"],
            "Japan": ["교토", "오사카", "나라"],
        }
        return related.get(country, [])

    def _generate_must_reserve_list(self, spots, restaurants):
        """예약 필수 목록"""
        must_reserve = []
        for spot in spots:
            if spot.get("reservation_required"):
                must_reserve.append({
                    "name": spot["name"],
                    "type": "명소",
                    "when": "최소 1주일 전",
                    "url": spot.get("reservation_url", ""),
                })
        for r in restaurants:
            if r.get("reservation_required"):
                must_reserve.append({
                    "name": r["name"],
                    "type": "식당",
                    "when": "최소 3일 전",
                    "url": r.get("reservation_url", ""),
                })
        return must_reserve

    def _calculate_day_cost(self, restaurants, spots, cur_sym, day, total_days):
        """일별 비용 계산(고정값 대신 입력 기반 집계)"""
        food_sum = 0
        for r in restaurants:
            food_sum += self._extract_numeric_price(r.get("price", "0"))

        # 동선 체류/이동 비용은 명시 데이터 기반으로만 추정
        activity = 0
        for s in spots:
            fee_text = (s.get("fee") or "").lower()
            if "무료" in fee_text:
                continue
            activity += self._extract_numeric_price(s.get("fee", "0"))

        transport = max(0, (len(spots) - 1) * 4)
        total = food_sum + activity + transport

        out = {
            "transport": f"{transport}{cur_sym}",
            "food": f"{food_sum}{cur_sym}" if food_sum else "",
            "activities": f"{activity}{cur_sym}" if activity else "",
            "total": f"{total}{cur_sym}" if total else "",
        }
        return out
    def _calculate_total_costs(self, country, cur_sym, days):
        """총 예상 비용"""
        nights = days - 1
        budget_food = 40
        mid_food = 60
        luxury_food = 100
        budget_n = 80
        mid_n = 160
        luxury_n = 300

        budget_total = budget_n * nights + budget_food * days + 80
        mid_total = mid_n * nights + mid_food * days + 130
        luxury_total = luxury_n * nights + luxury_food * days + 250
        budget_krw = self._to_krw_value(budget_total, country)
        mid_krw = self._to_krw_value(mid_total, country)
        luxury_krw = self._to_krw_value(luxury_total, country)

        return {
            "budget": {
                "accommodation": f"80{cur_sym} x {nights}박 = {budget_n*nights}{cur_sym}",
                "food": f"40{cur_sym} x {days}일 = {budget_food*days}{cur_sym}",
                "transport": f"30{cur_sym}",
                "activities": f"50{cur_sym}",
                "total_local": f"{budget_total}{cur_sym}",
                "total_krw": f"{budget_krw:,}원",
                "total": f"{budget_total}{cur_sym} ({self._to_krw(budget_total, country)})",
            },
            "mid": {
                "accommodation": f"160{cur_sym} x {nights}박 = {mid_n*nights}{cur_sym}",
                "food": f"60{cur_sym} x {days}일 = {mid_food*days}{cur_sym}",
                "transport": f"50{cur_sym}",
                "activities": f"80{cur_sym}",
                "total_local": f"{mid_total}{cur_sym}",
                "total_krw": f"{mid_krw:,}원",
                "total": f"{mid_total}{cur_sym} ({self._to_krw(mid_total, country)})",
            },
            "luxury": {
                "accommodation": f"300{cur_sym} x {nights}박 = {luxury_n*nights}{cur_sym}",
                "food": f"100{cur_sym} x {days}일 = {luxury_food*days}{cur_sym}",
                "transport": f"100{cur_sym}",
                "activities": f"150{cur_sym}",
                "total_local": f"{luxury_total}{cur_sym}",
                "total_krw": f"{luxury_krw:,}원",
                "total": f"{luxury_total}{cur_sym} ({self._to_krw(luxury_total, country)})",
            }
        }
    def _get_daily_themes(self, city, country, region):
        """일별 테마"""
        profile = self._pick_style_profile(city, country, region)
        base = profile.get("daily_themes", {})
        if base:
            return {**{idx: base.get(idx) or {
                "title": f"Day {idx}",
                "theme": "균형 잡힌 탐방"
            } for idx in range(1, 6)}}

        return {
            1: {"title": "도착 및 적응", "theme": "느긋한 첫날, 동네 탐험"},
            2: {"title": f"{city} 상징", "theme": "핵심 랜드마크 투어"},
            3: {"title": "문화 체험", "theme": "박물관과 역사 탐방"},
            4: {"title": "특별한 경험", "theme": "숨은 명소와 맛집"},
            5: {"title": "마무리", "theme": "여유로운 마지막 날"},
        }

    def _build_global_restaurant_catalog(self, days_plan, city: str):
        """일정 전체에서 식당 후보 풀 구성"""
        catalog = []
        seen = set()
        for d in days_plan or []:
            for r in d.get("restaurants", []) or []:
                nm = r.get("name")
                if not nm or nm in seen:
                    continue
                seen.add(nm)
                catalog.append({**r})

        from collections import defaultdict
        grouped = defaultdict(list)
        for r in catalog:
            tier = (r.get("price_tier") or self._infer_price_tier(r.get("price", "")).lower())
            if tier not in ("budget", "mid", "luxury"):
                tier = "mid"
            grouped[tier].append(r)

        # 최소 1개 보장
        if not grouped.get("budget"):
            grouped["budget"].append({"name": f"{city}로컬 다이닝", "type": "로컬식", "price": "15-25", "cuisine": "현지식", "tip": "간단히 들러 체류를 조절하기 좋은 곳", "price_tier": "budget", "recommended_menu": "오늘의 런치 세트", "pros": "짧은 체류에 적합한 회전율", "cons": "피크타임 대기 가능"})
        if not grouped.get("mid"):
            grouped["mid"].append({"name": f"{city} 메인다이닝", "type": "현지식", "price": "30-60", "cuisine": "현지식", "tip": "점심 메인 동선에 무난", "price_tier": "mid", "recommended_menu": "셰프 추천 코스", "pros": "동선 접근성과 메뉴 구성이 안정적", "cons": "주말 저녁 대기 시간 증가"})
        if not grouped.get("luxury"):
            grouped["luxury"].append({"name": f"{city} 스페셜 다이닝", "type": "파인다이닝", "price": "120-220", "cuisine": "현지식", "tip": "마감 동선용 고급 옵션", "price_tier": "luxury", "reservation_required": True, "reservation_url": "", "recommended_menu": "디너 테이스팅 코스", "pros": "분위기와 서비스 품질이 높음", "cons": "예산 부담이 큼"})

        out=[]
        for tier in ("budget", "mid", "luxury"):
            for r in grouped[tier][:3]:
                row = {**r}
                signatures = row.get("signature", [])
                if isinstance(signatures, list) and signatures and not row.get("recommended_menu"):
                    row["recommended_menu"] = ", ".join([str(x) for x in signatures[:2] if x])
                row["pros"] = row.get("pros") or self._default_restaurant_pros(row)
                row["cons"] = row.get("cons") or self._default_restaurant_cons(row)
                out.append(row)
        return out

    def _infer_price_tier(self, price_text: str) -> str:
        p = self._extract_numeric_price(price_text)
        if not isinstance(p, int) or p <= 0:
            return "mid"
        if p <= 35:
            return "budget"
        if p <= 90:
            return "mid"
        return "luxury"

    def _default_restaurant_pros(self, restaurant: Dict) -> str:
        tip = (restaurant.get("tip") or "").strip()
        if tip:
            return tip[:90]
        tier = (restaurant.get("price_tier") or "").lower()
        if tier == "budget":
            return "가격 부담이 낮고 회전이 빨라 일정 중간에 넣기 좋음"
        if tier == "luxury":
            return "분위기와 서비스가 좋아 기념일 식사로 적합"
        return "접근성과 메뉴 밸런스가 좋아 대부분의 일정에 무난"

    def _default_restaurant_cons(self, restaurant: Dict) -> str:
        if restaurant.get("reservation_required"):
            return "피크 타임에는 예약이 없으면 대기가 길 수 있음"
        tier = (restaurant.get("price_tier") or "").lower()
        if tier == "budget":
            return "좌석이 협소하거나 대기 줄이 생길 수 있음"
        if tier == "luxury":
            return "예산 부담이 크고 드레스코드가 있을 수 있음"
        return "시간대에 따라 소음이 커질 수 있어 이른 방문이 유리"

    def _get_best_season(self, region):
        """최적 여행 시즌"""
        return {"유럽": "4-6월, 9-10월", "동남아": "11-2월", "동아시아": "3-5월, 9-11월"}.get(region, "봄/가을")

    def _get_packing_list(self, region):
        """준비물 리스트"""
        return ["여권", "여행자보험", "보조배터리", "편한 신발", "유니버셜 어댑터"]

    def _generate_seo(self, city, country, days, region):
        """SEO 정보"""
        return {
            "hashtags": [f"#{city}여행", f"#{country}여행", "#해외여행", "#여행가이드"],
            "meta_description": f"{city} {days}일 여행 완벽 가이드",
        }


# CITY_DATABASE - Complete city data with Boss's Template format
CITY_DATABASE = {
    "Kyoto": {
        "spots": [
            {"name": "기요미즈데라 (청수사)", "desc": "기요미즈데라는 교토의 대표 사찰로, 오구라 강변과 맞닿은 전망이 유명한 곳입니다.", "history": "정식 778년의 유래를 갖는 유명한 사찰로, 사계절 풍경이 아름답기로 유명합니다.", "time": "오전 09:00-11:00", "reservation_required": False, "duration": "2시간", "fee": "무료", "address": "1-294 Kiyomizu, Higashiyama Ward, Kyoto", "tip": "오전 첫시간 방문이 가장 여유롭고, 우천 시 지면이 미끄러우니 방수 신발이 좋습니다.", "maps_url": "https://maps.google.com/maps?q=Kiyomizu+dera+Kyoto"},
            {"name": "후시미 이나리 신사", "desc": "수천 개의 도리이 산책로와 정적이 공존하는 대표 신사입니다.", "history": "축성·보수·순례의 역사가 긴 신사로, 일본인의 신앙을 느낄 수 있는 상징적 공간입니다.", "time": "오전 11:30-13:30", "reservation_required": False, "duration": "2.5시간", "fee": "무료", "address": "68 Fukakusa Yabunouchi-cho, Fushimi Ward, Kyoto", "tip": "이른 시간에는 경사가 긴 구간의 인파가 덜합니다.", "maps_url": "https://maps.google.com/maps?q=Fushimi+Inari+Taisha"},
            {"name": "니넨자카·산젠자카", "desc": "교토 전통가옥 분위기의 돌계단 골목과 공예가게, 카페가 이어지는 산책 루트입니다.", "history": "교토의 근교 상권으로 오래된 장인 상점과 생활 문화가 남아있습니다.", "time": "오후 14:00-16:00", "reservation_required": False, "duration": "2시간", "fee": "무료", "tip": "교토다운 산책을 위해 편한 운동화가 필수입니다.", "maps_url": "https://maps.google.com/maps?q=Ninenzaka+Sanjinza+Kyoto"},

            {"name": "니조성", "desc": "도요토미 시대 성격이 남은 건축군으로, 정원 산책과 내부 관람이 조화됩니다.", "history": "에도 시대 군영 시설·정치 상징을 간직한 복합 유적지입니다.", "time": "오전 10:00-12:30", "reservation_required": True, "reservation_url": "https://www.kyoto-nijo.jp/en/access/index.html", "duration": "2시간", "fee": "1,000엔", "address": "541 Nijojocho, Nakagyo Ward, Kyoto", "tip": "입장 전 동선 예약이 원활하면 대기시간을 크게 줄일 수 있습니다.", "maps_url": "https://maps.google.com/maps?q=Nijo+Castle+Kyoto"},
            {"name": "금각사(킨카쿠지)", "desc": "연못과 어우러진 금빛 누각, 사계절 풍광이 뛰어난 대표 유적지입니다.", "history": "아시카가 막부의 별장으로 시작된 금각은 일본 문화사 상징입니다.", "time": "오후 13:30-15:30", "reservation_required": True, "reservation_url": "https://www.shokoku-ji.jp/en/access/access-kinkakuji.html", "duration": "1.5시간", "fee": "400엔", "address": "1 Kinkakuji-kitaimachi, Kita Ward, Kyoto", "tip": "공개 시간 직후 방문 시 동선이 가장 여유롭습니다.", "maps_url": "https://maps.google.com/maps?q=Kinkaku-ji+Kyoto"},
            {"name": "은각사·기타 산책", "desc": "도심에서 잠시 벗어나 일본 정원의 숨결을 느끼는 코스입니다.", "history": "헤이안 시대 이래 이어져 온 정원 문화와 차분한 정취를 담고 있습니다.", "time": "오후 16:00-17:30", "reservation_required": False, "duration": "1.5시간", "fee": "무료", "tip": "사진 스팟을 위해 조명이 좋은 시간대에 맞추면 효율적입니다.", "maps_url": "https://maps.google.com/maps?q=Temple+Kyoto+area"},

            {"name": "아라시야마 라쿠산·텐류지", "desc": "강변과 정원, 골목이 함께 있는 느긋한 동선입니다.", "history": "교토 유서 깊은 동북부 산림권으로, 관광객 동선이 분산되어 있어 여유 있습니다.", "time": "오전 09:30-12:00", "reservation_required": False, "duration": "2.5시간", "fee": "묣료(천적 동선) 300엔 전후", "address": "Saga Ogurayama 36, Ukyo Ward, Kyoto", "tip": "교통카드로 이동이 편하고, 노면이 낙엽기엔 다소 미끄럽습니다.", "maps_url": "https://maps.google.com/maps?q=Arashiyama+Kyoto"},
            {"name": "토조구(아라시야마 토요코", "desc": "교토의 물길과 마을 경관을 동시에 느낄 수 있는 구간입니다.", "history": "전통과 관광 동선이 공존하는 구역으로 방문객이 계절마다 다릅니다.", "time": "오후 13:00-15:00", "reservation_required": False, "duration": "1.5시간", "fee": "무료", "tip": "산책 중심 동선으로 비오는 날도 비교적 쉬운 구간입니다.", "maps_url": "https://maps.google.com/maps?q=Arashiyama+Monkey+Park+Kyoto"},
            {"name": "기온 & 신사노미치", "desc": "저녁에 살아나는 골목 분위기와 다이닝 동선을 위한 핵심 코스입니다.", "history": "전통 문화와 상업, 예술이 섞인 도심권으로 오랜 시간 꾸준히 인기 있는 지역입니다.", "time": "오후 17:00-20:00", "reservation_required": False, "duration": "3시간", "fee": "무료", "tip": "식사 시작 전 코스 이동 동선을 짧게 잡으면 마감 없이 동선이 매끈해집니다.", "maps_url": "https://maps.google.com/maps?q=Gion+Shin+Kyogoku+Kyoto"},

            {"name": "우지 다실·공방 구간", "desc": "현지 공예와 찻집을 병행하기 좋은 대체 라인입니다.", "history": "교토 공예와 전통 차 문화 체험이 살아있는 지역권입니다.", "time": "오전 10:00-12:00", "reservation_required": True, "reservation_url": "https://www.google.com/search?q=Kyoto+Matcha+Tea+Room+reservation", "duration": "2시간", "fee": "예약 방식 변동", "tip": "체험형 코스는 주말·공휴일 운영시간 변동이 큽니다.", "maps_url": "https://maps.google.com/maps?q=Uji+Kyoto+matcha"},
            {"name": "교토 철도공원 근교 라인", "desc": "이동 시간 확보형 일정 보강 구간으로, 교토 외곽 동선을 넣는 대체 코스입니다.", "history": "교통 접근성이 좋고 날씨변수에 대비하기 좋은 라인입니다.", "time": "오후 13:00-16:00", "reservation_required": False, "duration": "3시간", "fee": "무료", "tip": "날씨가 나쁠 경우 이동 동선 회복률이 높은 코스입니다.", "maps_url": "https://maps.google.com/maps?q=Kyoto+rail+tour+district"},
        ],
        "restaurants": [
            {"name": "라멘도쿄 교토점", "type": "일본식 라멘", "price": "1,000~1,800엔", "signature": ["돈카츠 라멘", "차슈 라멘"], "price_tier": "budget", "reservation_required": False, "tip": "대표메뉴: 돈카츠 라멘. 1인 기준 가성비 좋은 기본 메뉴 구성입니다.", "maps_url": "https://maps.google.com/maps?q=Kyoto+ramen"},
            {"name": "니시키 시장 포장마차", "type": "시장식 간이식", "price": "900~2,000엔", "signature": ["규카츠", "타코야키"], "price_tier": "budget", "reservation_required": False, "tip": "대표메뉴: 규카츠(안심 기준). 현금 결제 병행 시 빠릅니다.", "maps_url": "https://maps.google.com/maps?q=Nishiki+market+Kyoto"},
            {"name": "교토 정원 다이닝", "type": "일본식 정식", "price": "2,500~4,500엔", "signature": ["교토식 점심정식", "청량한 스프류"], "price_tier": "mid", "reservation_required": False, "tip": "대표메뉴: 계절 한정 점심정식. 예약보다는 당일 조기 방문이 유리합니다.", "maps_url": "https://maps.google.com/maps?q=Kyoto+kyo+ryori+restaurant"},
            {"name": "카이세키 오모테산", "type": "가이세키", "price": "7,000~12,000엔", "signature": ["가이세키 코스", "생선회 일식"], "price_tier": "mid", "reservation_required": True, "reservation_url": "https://www.google.com/search?q=Kyoto+kaiseki+reservation", "tip": "대표메뉴: 시즌 가이세키 정식. 웨딩식 일정이면 사전 예약권장.", "maps_url": "https://maps.google.com/maps?q=Kyoto+kaiseki+restaurant"},
            {"name": "긴사이초 료안", "type": "정통 가이세키", "price": "18,000~35,000엔", "signature": ["가이세키 코스", "생선 찜"], "price_tier": "luxury", "reservation_required": True, "reservation_url": "https://example.com/kyoto-luxury-reserve", "tip": "대표메뉴: 시즌 가이세키 8~10코스. 예산, 알레르기, 좌석 선호를 사전에 전달하면 좋습니다.", "maps_url": "https://maps.google.com/maps?q=Kyoto+Fine+Dining+kaiseki"},
            {"name": "고토리안 스테이크", "type": "일본식 스테이크", "price": "20,000~40,000엔", "signature": ["와규 스테이크", "메인 세트"], "price_tier": "luxury", "reservation_required": True, "reservation_url": "https://example.com/kyoto-steak-reserve", "tip": "대표메뉴: 와규 스테이크 정식. 공휴일은 조리시간 변동이 있어 1~2일 여유 예약이 안전합니다.", "maps_url": "https://maps.google.com/maps?q=Kyoto+Wagyu+steak"},
        ],
        "hotels": {
            "budget": [
                {"name": "Sakura Guest House Kyoto", "rating": 4.0, "price_per_night": "8,000~14,000엔", "area": "교토역 도보권", "pros": "가격이 저렴하고 접근성 좋음", "cons": "방이 아담하고 조식이 단출함", "maps_url": "https://maps.google.com/maps?q=Sakura+Guest+House+Kyoto", "checkin": "15:00", "checkout": "11:00", "benefit": "교통 접근이 편하고 교통비 절감"},
                {"name": "Hotel Mystays Shijo", "rating": 4.1, "price_per_night": "10,000~16,000엔", "area": "시내권", "pros": "침대가 편안하고 이동 동선이 단순", "cons": "주말엔 주변 소음이 있음", "maps_url": "https://maps.google.com/maps?q=Hotel+Mystays+Shijo+Kyoto", "checkin": "15:00", "checkout": "11:00", "benefit": "현지 이동 동선 최적"},
            ],
            "mid": [
                {"name": "Hotel Granvia Kyoto", "rating": 4.5, "price_per_night": "22,000~40,000엔", "area": "교토역권", "pros": "교통이 편하고 시설 완성도가 높음", "cons": "조식 메뉴는 미리 확인 필요", "maps_url": "https://maps.google.com/maps?q=Hotel+Granvia+Kyoto", "checkin": "15:00", "checkout": "11:00", "benefit": "동선 짧고 공항·역 접근 빠름"},
                {"name": "Mitsui Garden Hotel Kyoto", "rating": 4.4, "price_per_night": "25,000~45,000엔", "area": "히가시야마권", "pros": "룸 상태와 정원 동선이 좋음", "cons": "가격 대비 선택 포인트를 정확히 봐야 함", "maps_url": "https://maps.google.com/maps?q=Mitsui+Garden+Hotel+Kyoto", "checkin": "15:00", "checkout": "11:00", "benefit": "도보 이동 기반 일정 구성 쉬움"},
            ],
            "luxury": [
                {"name": "The Ritz-Carlton Kyoto", "rating": 4.9, "price_per_night": "70,000~140,000엔", "area": "가모가와 강변", "pros": "서비스 품질과 뷰", "cons": "비용이 높고 룸타입 선호도 확인 필요", "maps_url": "https://maps.google.com/maps?q=The+Ritz-Carlton+Kyoto", "checkin": "15:00", "checkout": "11:00", "benefit": "최고급 서비스와 야경"},
                {"name": "Four Seasons Kyoto", "rating": 4.9, "price_per_night": "90,000~180,000엔", "area": "아라시야마 인근", "pros": "조용한 동선, 스파 품질 좋음", "cons": "예약 난이도 높음", "maps_url": "https://maps.google.com/maps?q=Four+Seasons+Kyoto", "checkin": "15:00", "checkout": "11:00", "benefit": "휴식중심 프리미엄"},
            ],
        },
        "emergency_contacts": {"police": "110", "ambulance": "119", "fire": "119", "general": "110", "tips": "야간 귀가는 주요 간선도로 중심으로 이동하세요."},
        "embassy_info": {"name": "주한 대사관(서울에서 이동 필요)", "address": "Kyoto에는 영사관이 없으므로 서울 총영사관/주재 사무소 안내 확인", "phone": "+82-2-2100-2100", "emergency_phone": "+82-2-2100-2100", "website": "https://overseas.mofa.go.kr/"},
    },
    "Maldives": {
        "spots": [
            {"name": "몰디브 수상비행과 마레(Male) 항구", "desc": "말레(=몰디브 수도)로 들어가는 가장 현실적인 시작점. 공항 이동 직후 도시의 공기와 수상 리듬을 느끼는 동선", "history": "말레는 12세기 이후 여러 섬 집단이 행정 중심지 역할을 이어온 몰디브의 진입부입니다.", "time": "오전 09:00-11:00", "reservation_required": False, "duration": "2시간", "fee": "무료", "address": "Malé, Maldives", "tip": "현지 택시/보트 픽업은 성수기 시간표가 다르니 사전 확인이 필요해요.", "maps_url": "https://maps.google.com/maps?q=Mal%C3%A9+Maldives"},
            {"name": "몰디브 국립수족관(선택형)", "desc": "바다 생태를 가까이서 보며 일정의 분위기를 세팅하기 좋은 장소", "history": "제도 생태 관광 초기에 정비되면서 지역 문화와 해양 생태 체험을 함께 제공합니다.", "time": "오전 11:00-13:00", "reservation_required": False, "duration": "1.5시간", "fee": "입장료 별도", "address": "Male, Maldives", "tip": "자외선이 강한 오후라 선글라스·선크림은 필수입니다.", "maps_url": "https://maps.google.com/maps?q=Maldives+National+Museum"},
            {"name": "바다뷰 로컬 카페", "desc": "가벼운 스낵으로 첫날 컨디션을 조정하고 바다의 분위기를 받는 곳", "history": "현지인·장기 체류자 입장에서 동선 완충용으로 자주 찾는 라운지형 카페들이 많아요.", "time": "오후 13:00-14:30", "reservation_required": False, "duration": "1.5시간", "fee": "1500-2500 MVR", "address": "Male, Maldives", "tip": "해먹 테이블은 아늑하지만 바람이 강한 날엔 실내가 더 편해요.", "maps_url": "https://maps.google.com/maps?q=Maldives+resort+cafe+Mal%C3%A9"},

            {"name": "바투카네(전망 포인트) 산책", "desc": "수변 산책로를 통해 리듬을 천천히 전환", "history": "지역 자원보전 정책이 강화되면서 산책 동선도 지역별로 정비되어 사용성이 좋아졌습니다.", "time": "오전 09:30-11:30", "reservation_required": False, "duration": "2시간", "fee": "무료", "address": "North Male Atoll", "tip": "해안 경보가 내려졌을 때는 이동 경로를 미리 바꿔두세요.", "maps_url": "https://maps.google.com/maps?q=Mal%C3%A9+Beach+Walk"},
            {"name": "워터프런트 가로수길", "desc": "조용한 사진 동선과 일몰 빛 포인트 확보", "history": "주말·공휴일에는 단체 유입이 늘어 동선이 분산되기 쉬운 구간입니다.", "time": "오후 13:30-16:00", "reservation_required": False, "duration": "2시간", "fee": "무료", "address": "North Male Atoll", "tip": "인기 시간엔 수상 버스가 막히므로 출발은 여유 있게.", "maps_url": "https://maps.google.com/maps?q=Mal%C3%A9+Waterfront"},
            {"name": "몰디브 바하라 수평선 라인", "desc": "바다와 노을을 함께 보는 코어 코스", "history": "단순 휴양을 넘어 몰디브의 공간 감성을 가장 직관적으로 받는 라인입니다.", "time": "오후 17:00-19:00", "duration": "2시간", "fee": "무료", "address": "Male, Maldives", "tip": "노출이 강한 일몰은 수동 노출이 더 깔끔합니다.", "maps_url": "https://maps.google.com/maps?q=Maldives+sunset+male"},

            {"name": "쿠다다니 아일랜드 이동 포인트", "desc": "보트 동선 체계화와 산호대 접근 동선 확인", "history": "몰디브의 작은 섬 라우팅 중 하나로 장기 동선 구성 시 유용한 연결점입니다.", "time": "오전 08:30-10:30", "reservation_required": False, "duration": "1.5시간", "fee": "보트 이용료 별도", "address": "South Male Atoll", "tip": "방문 전 보트 픽업 동선 확인이 필수입니다.", "maps_url": "https://maps.google.com/maps?q=Kudahdhoo+island+Maldives"},
            {"name": "라군 수상식당", "desc": "점심 전 동선 분리와 맛집 체험으로 이동 피로를 줄이는 코스", "history": "해양관광이 발달하면서 소규모 다이닝이 숙박동선과 연계되는 곳이 증가했습니다.", "time": "점심 11:30-13:30", "reservation_required": False, "duration": "2시간", "fee": "입장료/패키지 별도", "address": "South Male Atoll", "tip": "물놀이가 많아 건조 타월과 다림수건은 꼭 챙기세요.", "maps_url": "https://maps.google.com/maps?q=water+restaurant+Maldives"},
            {"name": "스피드보트 라군 크루즈", "desc": "짧은 물 위 동선으로 체력 소모를 낮추고 풍경을 집중", "history": "최근 5년간 라군 동선용 단거리 보트 운영이 활성화된 구간입니다.", "time": "오후 14:30-16:30", "reservation_required": False, "duration": "2시간", "fee": "1500-3000 MVR", "address": "Baa Atoll", "tip": "물기온이 낮을 땐 라군 크루즈가 더 안정적입니다.", "maps_url": "https://maps.google.com/maps?q=Maldives+Lagoon+cruise"},
            {"name": "라군 스파 라운지", "desc": "마무리 감각을 위한 스파형 휴식 구간", "history": "리조트 동선에서 체류 만족도를 끌어올리는 핵심 지점으로 자리 잡았습니다.", "time": "오후 17:30-19:30", "reservation_required": False, "duration": "2시간", "fee": "1000-2500 MVR", "address": "Baa Atoll", "tip": "예약이 필요한 경우가 많아 당일 확인 추천.", "maps_url": "https://maps.google.com/maps?q=Maldives+lagoon+spa"},

            {"name": "라군 산책 코스(1부)", "desc": "섬의 조용한 저녁 공기를 기록", "history": "몰디브의 바람과 바다 소리 패턴을 느끼는 데 좋은 루트로 알려져 있습니다.", "time": "오전 09:30-11:00", "reservation_required": False, "duration": "1.5시간", "fee": "무료", "address": "Dhaalu Atoll", "tip": "조개껍질 정리 구간은 천천히 걸어주세요.", "maps_url": "https://maps.google.com/maps?q=lagoon+walk+maldives"},
            {"name": "로컬 마켓 거리", "desc": "기념품 외에 생활용 소품도 구매 가능한 구간", "history": "현지 생활의 리듬을 엿보는 데 유용한 구간입니다.", "time": "점심 12:00-14:00", "reservation_required": False, "duration": "1.5시간", "fee": "무료", "address": "Dhaalu Atoll", "tip": "휴대폰 결제보다 현금이 빠른 곳도 있습니다.", "maps_url": "https://maps.google.com/maps?q=local+market+Maldives"},
            {"name": "라군 다이빙 오리엔테이션", "desc": "물 위 탐험 전 최소한의 안전 브리핑 동선", "history": "성수기 안전 가이드에 따라 사전 브리핑 동선이 권장됩니다.", "time": "오후 15:00-16:00", "reservation_required": False, "duration": "1시간", "fee": "프로그램별 별도", "address": "Dhaalu Atoll", "tip": "수심 적응은 조용한 워터 수면에서 먼저 시작하세요.", "maps_url": "https://maps.google.com/maps?q=Maldives+dive+orientation"},
            {"name": "라군 선셋 다이닝", "desc": "일몰과 함께 마무리하는 저녁식사 코스", "history": "리조트형 일정에서 선셋 라운지가 대세인 흐름과 맞닿아 있습니다.", "time": "오후 18:00-20:00", "reservation_required": False, "duration": "2시간", "fee": "예약형(메뉴별)", "address": "Dhaalu Atoll", "tip": "식사 전 라군 크루즈 동선을 한 번 더 확인하면 움직임이 깔끔해집니다.", "maps_url": "https://maps.google.com/maps?q=Maldives+sunset+dining"},
        ],
        "restaurants": [
            {"name": "Kuda Veli Dining", "type": "로컬 카페", "price": "15-25USD", "signature": ["해산물 스프", "그릴 파스타"], "price_tier": "budget", "reservation_required": False, "tip": "브런치·라운지 동선에 적합한 메뉴 구성이 깔끔합니다.", "maps_url": "https://maps.google.com/maps?q=Kuda+Veli+Dining+Maldives"},
            {"name": "Sea Breeze Cafe", "type": "다이닝", "price": "25-40USD", "signature": ["피쉬 커리", "라이 라이스"], "price_tier": "budget", "reservation_required": False, "tip": "해질녘 이전 입장하면 좌석 선택이 유리합니다.", "maps_url": "https://maps.google.com/maps?q=Sea+Breeze+Cafe+Maldives"},
            {"name": "Baa Atoll Grill", "type": "해산물 다이닝", "price": "40-60USD", "signature": ["그릴 타르", "크리미 수프"], "price_tier": "mid", "reservation_required": False, "tip": "물놀이 뒤엔 산뜻한 메뉴부터 시작하세요.", "maps_url": "https://maps.google.com/maps?q=Baa+Atoll+Grill+Maldives"},
            {"name": "Lagoon House", "type": "리조트 다이닝", "price": "50-90USD", "signature": ["새우 카레", "열대 과일 코스"], "price_tier": "mid", "reservation_required": True, "reservation_url": "https://example.com/lagoon-house-reserve", "tip": "선셋 타임은 좌석이 빨리 찹니다. 하루 전 예약 권장.", "maps_url": "https://maps.google.com/maps?q=Lagoon+House+Maldives"},
            {"name": "Ithaa Undersea", "type": "럭셔리 뷔페", "price": "100-180USD", "signature": ["몰디브식 모듬", "바다 위 디저트 바"], "price_tier": "luxury", "reservation_required": True, "reservation_url": "https://example.com/ithaa-undersea-reserve", "tip": "로맨틱 라운지로 유명해 데이트 동선에 적합합니다.", "maps_url": "https://maps.google.com/maps?q=Ithaa+Undersea+Restaurant+Maldives"},
            {"name": "Alimatha Fine Dining", "type": "파인다이닝", "price": "120-220USD", "signature": ["랍스터 라이스", "트러플 해산물 코스"], "price_tier": "luxury", "reservation_required": True, "reservation_url": "https://example.com/alimatha-fine-dining", "tip": "특별한 날에만 슬롯이 바뀌므로 일정표와 날짜를 맞춰주세요.", "maps_url": "https://maps.google.com/maps?q=Alimatha+Fine+Dining+Maldives"},
        ],
        "hotels": {
            "budget": [
                {"name": "Ari Atoll Budget Inn", "rating": 4.1, "price_per_night": "80-120USD", "area": "Male 시내권", "pros": "교통 접근성이 좋고 체크인 절차가 단순", "cons": "조식은 한정 메뉴", "maps_url": "https://maps.google.com/maps?q=Ari+Atoll+Budget+Inn", "checkin": "15:00", "checkout": "11:00", "benefit": "공항 이동 동선이 짧음"},
                {"name": "Crown Stay Malé", "rating": 4.0, "price_per_night": "90-150USD", "area": "말레 부두권", "pros": "가격이 안정적이며 동선 단순", "cons": "식사 메뉴가 단조로움", "maps_url": "https://maps.google.com/maps?q=Crown+Stay+Mal%C3%A9", "checkin": "15:00", "checkout": "11:00", "benefit": "가벼운 휴식 위주 일정에 적합"},
            ],
            "mid": [
                {"name": "Baa Atoll Waterfront", "rating": 4.5, "price_per_night": "180-280USD", "area": "Waterfront", "pros": "바다 전망과 이동 동선 밸런스", "cons": "주말은 대기시간이 길 수 있음", "maps_url": "https://maps.google.com/maps?q=Baa+Atoll+Waterfront", "checkin": "15:00", "checkout": "11:00", "benefit": "가족형/연인형 모두 무난"},
                {"name": "Male Lagoon Residence", "rating": 4.4, "price_per_night": "220-320USD", "area": "몰디브 몰타운권", "pros": "수면·로비 동선이 정돈됨", "cons": "야간 활동은 사전 조율 필요", "maps_url": "https://maps.google.com/maps?q=Male+Lagoon+Residence", "checkin": "15:00", "checkout": "11:00", "benefit": "가벼운 휴식 + 다이빙 동선 지원"},
            ],
            "luxury": [
                {"name": "One&Only Ocean Club", "rating": 4.9, "price_per_night": "550-900USD", "area": "리조트 엔드", "pros": "라군 접근 동선이 최고", "cons": "가격 대비 동선 유연성은 제한", "maps_url": "https://maps.google.com/maps?q=One%26Only+Ocean+Club+Maldives", "checkin": "16:00", "checkout": "11:00", "benefit": "서비스와 풍경 완성도 높음"},
                {"name": "COMO Cocoa Island", "rating": 4.8, "price_per_night": "600-1100USD", "area": "Cocoa Island", "pros": "야간 프라이빗 동선", "cons": "예약 난이도 높음", "maps_url": "https://maps.google.com/maps?q=COMO+Cocoa+Island+Maldives", "checkin": "16:00", "checkout": "11:00", "benefit": "장기 체류형/휴식형 일정에 강함"},
            ],
        },
        "emergency_contacts": {"police": "112", "ambulance": "118", "fire": "119", "general": "118", "tips": "기상 경보 시 항만·보트 동선을 즉시 재확인하세요."},
        "embassy_info": {"name": "몰디브 영사 안내", "address": "인도/중동권 영사 안내 채널 확인", "phone": "+82-2-2100-2100", "emergency_phone": "+82-2-2100-2100", "website": "https://www.mofa.go.kr/"},
    },
    "Paris": {
        "spots": [
            {"name": "에펠탑", "desc": "파리 상징의 중심 아이콘. 초기 동선은 주변 공원부터 시작해 시야를 조절하면 훨씬 오래된 감흥이 남는다.", "history": "1889년 만국박람회 기념으로 완공되어 지금은 파리 아이콘이 된 건축물", "time": "오전 09:00-11:00", "reservation_required": True, "reservation_url": "https://www.toureiffel.paris/", "duration": "2시간", "fee": "28.60유로", "tip": "오전 첫 시간 입장권 라인 짧고 조망은 상대적으로 여유롭다.", "maps_url": "https://maps.google.com/?q=Eiffel+Tower+Paris"},
            {"name": "샹제리제 거리", "desc": "아치 광장(Arc de Triomphe)으로 이어지는 메인 보행축. 쇼핑보다 이동 동선 관리가 핵심이다.", "history": "오랜 왕실 도로를 따라 형성된 파리의 대표 거리", "time": "오전 11:30-13:00", "reservation_required": False, "duration": "1시간", "fee": "무료", "tip": "오전 11시 이후가 가장 덜 붐빈다.", "maps_url": "https://maps.google.com/?q=Champs+Elysees+Paris"},
            {"name": "루브르 박물관", "desc": "하루 일정의 문화 축을 정하는 필수 관람지. 입장 전 동선만 미리 잡으면 체류 품질이 확 올라간다.", "history": "중세 요새를 개조해 세계적 미술관으로 운영되는 역사 깊은 공간", "time": "오후 13:30-16:30", "reservation_required": True, "reservation_url": "https://www.louvre.fr/en", "duration": "3시간", "fee": "무료/유료 구간 구분", "tip": "오픈 직후 티켓 입장이 가장 안정적이다.", "maps_url": "https://maps.google.com/?q=Louvre+Museum+Paris"},
            {"name": "오르세 미술관", "desc": "인상주의 중심 전시로 미술 감상 동선을 꽉 채울 수 있는 장소.", "history": "옛 기차역 건물을 미술관으로 전환한 파리 대표 문화공간", "time": "오후 17:00-19:00", "reservation_required": True, "reservation_url": "https://www.musee-orsay.fr/en", "duration": "2시간", "fee": "입장료 별도", "tip": "루브르와 이어서 보려면 시간 간격을 짧게 잡아 이동을 줄인다.", "maps_url": "https://maps.google.com/?q=Musee+d%27Orsay+Paris"},
            {"name": "몽마르트르 언덕", "desc": "전망과 골목 동선을 같이 담을 수 있는 오후/저녁 전환 지점.", "history": "예술가와 사교의 중심지로 오랫동안 도시의 위안을 상징해온 지역", "time": "저녁 19:30-21:30", "reservation_required": False, "duration": "2시간", "fee": "입장료 없음", "tip": "야간 산책은 계단 구간 페이스 조절이 핵심", "maps_url": "https://maps.google.com/?q=Montmartre+Paris"},

            {"name": "샤테르누보/베르크 신사단지", "desc": "조용한 주거 동선을 섞어 컨디션 회복 지점으로 쓰기 좋은 구간", "history": "근대와 예술이 교차하는 도시 생활권", "time": "오전 09:00-10:30", "reservation_required": False, "duration": "1시간", "fee": "무료", "tip": "1~2개 코스로 나눠 걷는 게 좋다.", "maps_url": "https://maps.google.com/?q=Saint+Germain+des+Pres+Paris"},
            {"name": "생-드니 비스트로 거리", "desc": "현지인 동선이 살아있는 식사 전후 보행권.", "history": "과거부터 상업·문학·카페 문화가 교차한 거리권", "time": "오후 11:30-13:00", "reservation_required": False, "duration": "1시간", "fee": "무료", "tip": "점심은 1:1 동선으로 끊지 말고, 근처 미술관 입구 쪽 동선을 살린다.", "maps_url": "https://maps.google.com/?q=Rue+Saint-Denis+Paris"},
            {"name": "오페라 가르니에 인근 산책", "desc": "시각적으로 가장 편하게 피로를 풀 수 있는 저녁 전야 산책 구간", "history": "근대 건축과 공연 문화의 접점에서 형성된 구역", "time": "오후 17:00-19:00", "reservation_required": False, "duration": "1.5시간", "fee": "무료", "tip": "저녁 동선은 짧고 핵심 동선만 가볍게 정리.", "maps_url": "https://maps.google.com/?q=Opera+Garnier+Paris"},
            {"name": "센강 크루즈 데크", "desc": "강변 이동과 촬영을 동시에 해결하는 밤 루트.", "history": "강변 교통과 시민 교류를 동시에 묶는 공간", "time": "저녁 20:00-21:30", "reservation_required": False, "duration": "1.5시간", "fee": "유료 보트 이용료별도", "tip": "크루즈는 하차 지점을 미리 정해 무리한 순환을 피한다.", "maps_url": "https://maps.google.com/?q=Bateaux+Parisiens+Paris"},
        ],
        "restaurants": [
            {"name": "Le Relais de Montmartre", "type": "프랑스식 브런치", "price": "20-35€", "price_tier": "budget", "cuisine": "프랑스", "tip": "가성비 샐러드와 수프가 좋다.", "maps_url": "https://maps.google.com/?q=Le+Relais+de+Montmartre+Paris", "signature": ["브런치 플레이트", "크로크무슈"]},
            {"name": "Café de l'Homme", "type": "프랑스 뷰 다이닝", "price": "25-45€", "price_tier": "mid", "cuisine": "프랑스", "tip": "에펠탑 뷰 동선 정리에 강함. 저녁엔 사전 예약", "maps_url": "https://maps.google.com/?q=Cafe+de+l%27Homme+Paris", "signature": ["비프 스테이크", "트러플 파스타"]},
            {"name": "L’Atelier du Chef", "type": "고급 다이닝", "price": "90-160€", "price_tier": "luxury", "cuisine": "프랑스", "reservation_required": True, "reservation_url": "https://example.com/atelier-reserve", "tip": "기념일 동선이면 분위기와 조명이 특히 좋다.", "maps_url": "https://maps.google.com/?q=L%27Atelier+du+Chef+Paris", "signature": ["오리 구이", "레드와인 디저트"]},
            {"name": "Chez Clément", "type": "와인바 다이닝", "price": "30-60€", "price_tier": "mid", "cuisine": "프랑스", "tip": "현지 와인과 생선 메뉴 추천.", "maps_url": "https://maps.google.com/?q=Chez+Clement+Paris", "signature": ["생선 타르트", "와인 페어링"]},
            {"name": "Le Petit Plaisir", "type": "비즈니스 카페", "price": "10-22€", "price_tier": "budget", "cuisine": "카페", "tip": "오픈 시간 맞춰 가면 혼잡이 적다.", "maps_url": "https://maps.google.com/?q=Le+Petit+Plaisir+Paris", "signature": ["크루아상", "에그 베네딕트"]},
            {"name": "Maison de Nuit", "type": "모던 프랑스", "price": "120-220€", "price_tier": "luxury", "cuisine": "프랑스", "reservation_required": True, "reservation_url": "https://example.com/maison-reserve", "tip": "창밖 조명과 음악 때문에 2차 동선이 자연스럽다.", "maps_url": "https://maps.google.com/?q=Maison+de+Nuit+Paris", "signature": ["트러플 오일 파스타", "랍스터 특선"]},
            {"name": "Boulangerie de Paris", "type": "현지 빵집", "price": "8-18€", "price_tier": "budget", "cuisine": "브런치", "tip": "카카오 가루 디저트가 인기", "maps_url": "https://maps.google.com/?q=Boulangerie+de+Paris"},
            {"name": "Le Marché", "type": "로컬 다이닝", "price": "18-32€", "price_tier": "mid", "cuisine": "프랑스", "tip": "점심 피크를 피해서 빠른 회전 동선.", "maps_url": "https://maps.google.com/?q=Le+March%C3%A9+Paris"},
            {"name": "La Table Parisienne", "type": "프랑스 코스", "price": "150-260€", "price_tier": "luxury", "cuisine": "프랑스", "reservation_required": True, "reservation_url": "https://example.com/la-table-reserve", "tip": "저녁 8시 전후가 분위기 관리에 유리", "maps_url": "https://maps.google.com/?q=La+Table+Parisienne+Paris"},
        ],
        "hotels": {
            "budget": [{"name": "Hotel de Paris Center", "rating": 4.1, "price_per_night": "90-140€", "area": "1구", "pros": "교통 접근성 높음", "cons": "룸 스탠다드", "recommended_for": "도심 접근이 중요하고 예산을 중시하는 1~2인 여행", "maps_url": "https://maps.google.com/?q=Hotel+de+Paris+Center"}],
            "mid": [{"name": "Le Central Paris Hotel", "rating": 4.5, "price_per_night": "180-260€", "area": "7구", "pros": "동선 효율·조식 우수", "cons": "숙박 인프라 이용시간 고정", "recommended_for": "가족이나 커플이 핵심 관광 루트를 짧게 이동하고 싶은 날", "maps_url": "https://maps.google.com/?q=Le+Central+Paris+Hotel"}],
            "luxury": [{"name": "Hotel Versailles", "rating": 4.9, "price_per_night": "420-700€", "area": "샹젤리제 근처", "pros": "뷰와 서비스", "cons": "입장료·식사 부대비 증가", "recommended_for": "기념일·기념 여행, 여유 있는 일정의 커플/그룹", "maps_url": "https://maps.google.com/?q=Hotel+Versailles+Paris"}],
        },
        "emergency_contacts": {"police": "17", "ambulance": "15", "fire": "18", "general": "+33 17", "tips": "야간 강변 동선은 단독 이동보다 도보 동선 분할이 안전합니다."},
        "embassy_info": {"name": "프랑스 영사 안내", "address": "플라스 드 라 콩코드, 파리", "phone": "+33 1 409 40 67 61", "emergency_phone": "+33 1 409 40 67 61", "website": "https://kr.usembassy.gov/fr/"},
    },

    "London": {
        "spots": [
            {"name": "Big Ben / Elizabeth Tower", "desc": "런던의 상징적인 시계탑. 1859년 완공된 고딕 복건식 건축물로 높이 96미터. 웨스트민스터 궁전과 함께 유네스코 세계문화유산입니다.", "history": "빅벤은 사실 시계탑 안의 종 이름이며, 2012년 엘리자베스 2세의 다이아몬드 주빌리를 기념해 타워 이름이 엘리자베스 타워로 바뀌었어요.", "time": "오전 9:00-10:00", "reservation_required": False, "duration": "30-45분", "fee": "묣료 (외부), 25파운드 (날개 투어)", "address": "London SW1A 0AA", "website": "https://www.parliament.uk/bigben/", "tip": "웨스트민스터 다리에서 빅벤과 템즈강을 함께 담은 사진이 가장 인기 있어요. 일몰 시간대면 금빛으로 물든 타워가 환상적이에요."},
            {"name": "Westminster Abbey", "desc": "영국 왕실의 대성당. 1066년부터 모든 영국 국왕 대관식이 열린 곳으로, 뉴턴, 다윈, 오스틴 등 유명인들이 묻힌 시인의 코너가 유명해요.", "history": "10세기에 건립된 이 성당은 900년 넘는 역사를 지니고 있어요. 윌리엄 셰익스피어를 비롯해 수많은 문인과 과학자들이 기념되고 있어서, 마치 영국 역사의 교과서를 보는 것 같아요.", "time": "오전 10:30-12:30", "reservation_required": True, "reservation_url": "https://www.westminster-abbey.org/visit-us", "duration": "2시간", "fee": "27파운드 (약 5만원)", "address": "20 Deans Yd, London SW1P 3PA", "tip": "오전 9시 30분 오픈런을 하면 여유롭게 볼 수 있어요. 오디오 가이드를 꼭 들으세요."},
            {"name": "Tower of London", "desc": "1078년 윌리엄 1세가 건립한 성. 영국 왕실 볼모인 크라운 주얼을 보관하고 있으며, 900년 역사를 간직한 세계유산이에요.", "history": "한때는 감옥으로도 사용되었던 이곳에서 많은 왕족과 귀족들이 갇혀 지냈어요. 특히 헨리 8세의 두 번째 부인 앤 불린이 처형된 곳으로도 유명하죠. 희생자의 문을 통해 들어가면 그 역사적 무게감이 느껴져요.", "time": "오전 10:00-13:00", "reservation_required": True, "reservation_url": "https://www.hrp.org.uk/tower-of-london/", "duration": "3-4시간", "fee": "33.60파운드 (약 6.2만원)", "address": "London EC3N 4AB", "tip": "요먼 워더(수문장) 투어는 묣료이며 1시간 동안 성의 역사를 재미있게 들려줘요. 10시, 11시 투어를 추천합니다."},
            {"name": "Tower Bridge", "desc": "1894년 완공된 런던의 상징적인 다리. 빅토리아 양식의 타워와 현수교 구조로, 유리바닥 본도에서 42m 높이의 템즈강을 볼 수 있어요.", "history": "산업혁명 시대에 템즈강 하류의 항구 지역과 연결하기 위해 건설되었어요. 당시 최첨단 기술로 만들어진 개황교는 대형 배가 지나갈 때 5분이면 들어 올려질 정도로 신기술이었죠.", "time": "오후 14:00-15:30", "reservation_required": False, "duration": "1시간", "fee": "12.30파운드 (약 2.3만원)", "address": "Tower Bridge Rd, London SE1 2UP", "tip": "일몰 1시간 전에 가면 낮과 밤의 풍경을 모두 볼 수 있어요. 유리바닥 위에서 사진 찍기가 인기예요."},
            {"name": "British Museum", "desc": "세계 최대 규모의 박물관. 이집트 라르손 돌, 로제타 스톤 등 인류 역사의 볼보들을 소장하고 있어요.", "history": "1753년 설립되어 800만 점 이상의 유물을 소장하고 있어요. 대영제국이 전 세계를 누비며 수집한 문화재들을 볼 수 있는 곳이에요. 특히 로제타 스톤은 고대 이집트 상형문자를 핵독하는 열쇠가 된 역사적인 유물이죠.", "time": "오전 10:00-13:00", "reservation_required": True, "reservation_url": "https://www.britishmuseum.org/visit", "duration": "3-4시간", "fee": "묣료 (기부 환영)", "address": "Great Russell St, London WC1B 3DG", "tip": "묣료지만 예약이 필수예요. 이집트관과 그리스관을 우선으로 보세요. 오디오 가이드 대신 공식 앱을 다운로드하세요."},
            {"name": "Borough Market", "desc": "1756년 설립된 런던 최고의 푸드 마켓. 신선한 농산물, 치즈, 해산물, 스트리트 푸드가 100개 이상의 스톨에서 판매돼요.", "history": "런던에서 가장 오래된 야외 시장 중 하나로, 19세기부터 현재 위치에서 운영되고 있어요. 당시 런던의 식재료 유통 중심지였던 이곳은 지금도 영국 최고의 요리사들이 재료를 사러 오는 곳이에요.", "time": "점심 12:00-14:00", "reservation_required": False, "duration": "2-3시간", "fee": "묣료 (음식 별도)", "address": "8 Southwark St, London SE1 1TL", "tip": "목요일 오전이 가장 한적하고 신선해요. 치즈 샌드위치와 오이스터를 꼭 드세요."},
            {"name": "Covent Garden", "desc": "17세기 과일·채소 시장이었던 곳이 현재는 쇼핑 중심지. 거리 공연과 레스토랑이 가득한 곳이에요.", "history": "1630년대에 베드포드 백작이 주택가를 개발하면서 시장으로 번창했어요. 1974년에 현재의 시장 건물이 완공되었고, 지금은 런던의 문화와 쇼핑 중심지가 되었죠. 천장의 유리 돔 아래에서 거리 공연을 보면 시간 가는 줄 몰라요.", "time": "오후 15:00-17:00", "reservation_required": False, "duration": "2-3시간", "fee": "무료", "address": "Covent Garden, London WC2E 9DD", "tip": "Apple Market은 수공예품을 파는 데 금요일-일요일에만 열려요. 거리 공연은 오후가 피크예요."},
        ],
        "restaurants": [
            {"name": "Dishoom", "cuisine": "인도 봄베이", "price": "20-35파운드", "address": "12 Upper St Martin's Ln, London WC2H 9FB", "signature": ["베이컨 나안", "블랙 다할"], "reservation_required": True, "reservation_url": "https://www.dishoom.com/reservations/", "tip": "현지 봄베이 스타일의 인도 음식을 맛볼 수 있어요. 분위기가 정말 좋고 음식도 훌륭해요. 웨이팅이 있으니 예약하세요."},
            {"name": "Borough Market Stalls", "cuisine": "글로벌 스트리트 푸드", "price": "5-15파운드", "address": "8 Southwark St, London SE1 1TL", "signature": ["초리초 샌드위치", "트러플 런치", "오이스터"], "reservation_required": False, "tip": "시장 안에서 다양한 길거리 음식을 맛볼 수 있어요. 현금보다 카드가 편해요."},
            {"name": "Padella", "cuisine": "이탈리안 파스타", "price": "10-20파운드", "address": "6 Southwark St, London SE1 1TQ", "signature": ["카치오 에 페페", "파르팔레"], "reservation_required": False, "tip": "15분 웨이팅은 각오하세요. 그럴만한 가치가 있는 파스타예요. 런치 메뉴가 가성비 좋아요."},
            {"name": "Flat Iron", "cuisine": "스테이크하우스", "price": "15-25파운드", "address": "17 Beak St, London W1F 9RW", "signature": ["플랫 아이언 스테이크", "팝콘 아이스크림"], "reservation_required": False, "tip": "11파운드 스테이크로 유명해요. 칼 모양 손잡이가 특징이에요. 저녁에는 웨이팅이 길어요."},
            {"name": "Poppies", "cuisine": "브리티시 피쉬앤칩스", "price": "12-20파운드", "address": "6-8 Hanbury St, London E1 6QR", "signature": ["피쉬 앤 칩스", "무스페어"], "reservation_required": False, "tip": "1950년대 복고풍 인테리어가 매력적인 현지인 추천 맛집이에요. 소스는 커리나 타르타르를 추천드려요."},
        ],
        "hotels": {
            "budget": [
                {"name": "The Hoxton, Holborn", "rating": 4.3, "price_per_night": "£100-150", "area": "Holborn (중심)", "pros": "세련된 디자인, 중심 위치, 조식 포함", "cons": "방이 작은 편, 소음 있을 수 있음", "maps_url": "https://www.google.com/maps/search/The+Hoxton+Holborn"},
                {"name": "Hub by Premier Inn", "rating": 4.1, "price_per_night": "£80-120", "area": "Covent Garden 근처", "pros": "저렴하고 깔끔, 침대 편안함", "cons": "기본적인 시설, 방이 매우 작음", "maps_url": "https://www.google.com/maps/search/Hub+by+Premier+Inn+London"},
            ],
            "luxury": [
                {"name": "The Savoy", "rating": 4.8, "price_per_night": "£400-700", "area": "Strand (템즈강변)", "pros": "역사적 명성, 완벽한 서비스, 애프터눈 티", "cons": "매우 비쌈, 예약 어려움", "maps_url": "https://www.google.com/maps/search/The+Savoy+London"},
                {"name": "Claridge's", "rating": 4.9, "price_per_night": "£500-900", "area": "Mayfair", "pros": "런던 최고급 호텔, 아르 데코 스타일, 전설적 서비스", "cons": "최고가, 공항과 거리 있음", "maps_url": "https://www.google.com/maps/search/Claridge's+London"},
            ],
        },
    },
    "Vienna": {
        "spots": [
            {"name": "쉔브룬 궁전 (Schönbrunn Palace)", "desc": "오스트리아 황제의 여름 별궁. 1441개의 방을 가진 바로크 양식의 궁전으로, 유네스코 세계문화유산이에요.", "history": "18세기에 마리아 테레지아 여황제에 의해 크게 확장되었어요. 6세의 모차르트가 이곳에서 연주를 했고, 나폴레옹도 두 차례 머문 곳이죠. 궁전 뒤편의 넓은 정원은 로코코 양식으로 조성되어 있어요.", "time": "오전 09:30-12:30", "reservation_required": True, "reservation_url": "https://www.schoenbrunn.at/en/", "duration": "3-4시간", "fee": "€24 (약 3.5만원)", "address": "Schönbrunner Schloßstraße 47, 1130 Wien", "tip": "Grand Tour를 추천해요. 40개의 화려한 방을 볼 수 있어요. 정원 뒤편 글로리에트에서 궁전 전경을 담은 사진이 인기예요."},
            {"name": "슈테판 대성당 (St. Stephen's Cathedral)", "desc": "빈의 상징인 고딕 대성당. 343년에 걸친 건립 기간을 거쳐 혼합 양식으로 완성되었어요.", "history": "12세기 로마네스크 양식으로 시작해 14-15세기 고딕 양식으로 변모했어요. 하absburg 왕가의 대관식과 결혼식이 열린 곳이며, 모차르트의 장례식도 이곳에서 열렸죠. 남탑의 다채로운 지붕 타일이 상징적이에요.", "time": "오전 10:00-11:30", "reservation_required": False, "duration": "1.5시간", "fee": "묣료 (내부), 남탑 €6", "address": "Stephansplatz 3, 1010 Wien", "tip": "일몰 직전에 가면 지붕 타일이 황금빛으로 빛나요. 남탑 343계단을 오르면 빈 시내가 한눈에 보여요."},
            {"name": "호프부르크 궁전 (Hofburg Palace)", "desc": "하absburg 황제들의 겨울 별궁. 13세기부터 600년간 황제의 거처로 사용되었어요.", "history": "루드비히 2세부터 카를 1세까지 수많은 황제가 이곳에서 거주했어요. 현재 오스트리아 연방 대통령의 집무실도 이곳에 있어요. 18개의 왕관을 소장한 보물고와 슈페르 마구간이 특히 유명해요.", "time": "오후 13:30-16:30", "reservation_required": True, "reservation_url": "https://www.hofburg-wien.at/en/", "duration": "3시간", "fee": "€16 (약 2.3만원)", "address": "Michaelerkuppel, 1010 Wien", "tip": "시시 박물관(Sisi Museum)과 보물고를 함께 보는 패키지를 추천해요. 10시 오픈런으로 가면 한적해요."},
            {"name": "벨베데레 궁전 (Belvedere Palace)", "desc": "18세기 바로크 건축의 걸작. 오스트리아 국립미술관이 있는 곳으로, 클림트의 '키스'를 비롯한 명작들이 소장되어 있어요.", "history": "1700년대 초 유진 사보이 공작의 여름 별궁으로 건립되었어요. 상벨베데레와 하벨베데레, 그리고 아름다운 정원으로 구성되어 있어요. 1차 세계대전 후 오스트리아 공화국 선포도 이곳에서 이루어졌죠.", "time": "오전 10:00-13:00", "reservation_required": True, "reservation_url": "https://www.belvedere.at/en", "duration": "3-4시간", "fee": "€16 (약 2.3만원)", "address": "Prinz Eugen-Straße 27, 1030 Wien", "tip": "클림트의 '키스'는 상벨베데레 2층에 있어요. 정원의 분수와 궁전을 배경으로 한 사진이 인기예요. 수목요일-일요일 9시 오픈런을 추천해요."},
            {"name": "프라터 공원 & 관람차 (Prater & Riesenrad)", "desc": "1897년 설치된 빈의 상징적 관람차. 총 64m 높이의 나무 관람차로, '제3의 사나이' 등 영화 촬영지로도 유명해요.", "history": "원래 황실 사냥터였던 이곳은 1766년부터 시민들에게 개방되었어요. 현재의 거대 관람차는 1897년 프란츠 요제프 1세 즉위 50주년을 기념해 만들어졌죠. 2차 대전 중 불탔지만 원형 그대로 복원되었어요.", "time": "오후 16:00-18:00", "reservation_required": False, "duration": "1-2시간", "fee": "€13 (관람차)", "address": "Prater, 1020 Wien", "tip": "일몰 직전에 타면 빈 시내가 황금빛으로 물들어요. 공원 내 헤어드볼트 박사 유령의 집도 재미있어요."},
            {"name": "나슈마르크트 (Naschmarkt)", "desc": "16세기부터 이어진 빈 최대의 시장. 신선한 농산물, 향신료, 올리브, 치즈 등 120개의 가게와 다양한 레스토랑이 있어요.", "history": "원래 유리병 시장이었던 이곳은 1900년대 초 현재의 위치로 이전했어요. 2차 대전 중 파괴 후 1970년대에 재건축되었죠. 현재는 빈의 다문화 음식 문화를 경험할 수 있는 곳이에요.", "time": "점심 12:00-14:00", "reservation_required": False, "duration": "2시간", "fee": "무료", "address": "1060 Wien", "tip": "토요일 아침 플리마켓도 함께 열려요. 중동 음식 부스에서 케밥과 팔라펠을 꼭 드세요."},
            {"name": "알베르티나 미술관 (Albertina)", "desc": "세계 최대의 모더니즘 회화 컬렉션을 소장한 미술관. 모네, 피카소, 키르히너 등 6만 점 이상의 작품이 있어요.", "history": "원래 하압스부르크의 궁정 도서관이었던 이곳은 1800년대 초 프란츠 요제프 1세가 개인 컬렉션을 기증하면서 미술관으로 탈바꿈했어요. 현재는 고전부터 현대미술까지 폭넓은 작품을 감상할 수 있어요.", "time": "오전 10:00-12:00", "reservation_required": True, "reservation_url": "https://www.albertina.at/en/", "duration": "2-3시간", "fee": "€18.90", "address": "Albertinaplatz 1, 1010 Wien", "tip": "인상파와 표현주의 작품이 특히 유명해요. 토요일 오전 10시 오픈런을 추천해요."},
        ],
        "restaurants": [
            {"name": "Figlmüller", "cuisine": "오스트리아 전통 (비너 슈니첼)", "price": "€15-25", "address": "Wollzeile 5, 1010 Wien", "signature": ["비너 슈니첼", "감자 샐러드"], "reservation_required": True, "reservation_url": "https://www.figlmueller.at/en/reservation/", "tip": "110년 역사의 슈니첼 전문점. 접시보다 큰 슈니첼이 유명해요. 예약 필수!"},
            {"name": "Café Central", "cuisine": "오스트리아 카페", "price": "€10-20", "address": "Herrengasse 14, 1010 Wien", "signature": ["애플 스트루델", "멜랑쥬", "티라미수"], "reservation_required": False, "tip": "1876년 개업한 역사적인 카페. 트로츠키와 프로이트가 즐겨 찾던 곳이에요. 오전 10시 전에 가면 웨이팅이 없어요."},
            {"name": "Plachutta", "cuisine": "오스트리아 전통 (타펠슈피츠)", "price": "€20-35", "address": "Wollzeile 38, 1010 Wien", "signature": ["타펠슈피츠", "크네델"], "reservation_required": True, "reservation_url": "https://www.plachutta.at/en/reservation/", "tip": "소고기를 육수에 삶은 타펠슈피츠의 원조. 국물에 빵을 찍어 먹는 것이 정석이에요."},
            {"name": "Griechenbeisl", "cuisine": "오스트리아 전통", "price": "€18-30", "address": "Fleischmarkt 11, 1010 Wien", "signature": ["그룰흐", "비너 슈니첼"], "reservation_required": True, "tip": "1447년부터 영업 중인 빈에서 가장 오래된 레스토랑. 베토벤과 모차르트도 다녀갔다는 역사적인 곳이에요."},
            {"name": "Demel", "cuisine": "오스트리아 디저트", "price": "€8-15", "address": "Kohlmarkt 14, 1010 Wien", "signature": ["자흏르토르테", "애플 스트루델", "카이저슈마런"], "reservation_required": False, "tip": "1786년 개업한 황실 제과점. 시시 황후가 즐겨 먹던 자흏르토르테(초콜릿 케이크)가 유명해요. 2층 창가자리가 분위기 있어요."},
        ],
        "hotels": {
            "budget": [
                {"name": "Ruby Sofie Hotel", "rating": 4.2, "price_per_night": "€80-120", "area": "Leopoldstadt (2구)", "pros": "세련된 디자인, 트램 역 근처, 조식 우수", "cons": "시내 중심과 약간 거리", "maps_url": "https://www.google.com/maps/search/Ruby+Sofie+Hotel+Vienna"},
                {"name": "Magdas Hotel", "rating": 4.0, "price_per_night": "€60-90", "area": "Landstraße (3구)", "pros": "저렴하고 깔끔, 친환경, 난민 고용", "cons": "기본적인 시설, 도보 15분", "maps_url": "https://www.google.com/maps/search/Magdas+Hotel+Vienna"},
            ],
            "luxury": [
                {"name": "Hotel Sacher Wien", "rating": 4.8, "price_per_night": "€400-700", "area": "Innere Stadt (1구, 오페라하우스 맞은편)", "pros": "역사적 명성, 사쳐토르테 원조, 완벽한 서비스", "cons": "매우 비쌈, 예약 어려움", "maps_url": "https://www.google.com/maps/search/Hotel+Sacher+Wien"},
                {"name": "Park Hyatt Vienna", "rating": 4.9, "price_per_night": "€350-600", "area": "Innere Stadt (금융가)", "pros": "럭셔리, 아르 누보 건물, 스파 우수", "cons": "고가, 조식 별도", "maps_url": "https://www.google.com/maps/search/Park+Hyatt+Vienna"},
            ],
        },
    },
}

rich_city_generator = RichCityGenerator()
