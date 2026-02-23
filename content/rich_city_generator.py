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
        }
        
        self.language_map = {
            "France": "프랑스어", "Italy": "이탈리아어", "Spain": "스페인어",
            "Germany": "독일어", "Netherlands": "네덜란드어", "UK": "영어",
            "Thailand": "태국어", "Singapore": "영어/중국어", "Japan": "일본어",
            "USA": "영어", "Czech Republic": "체코어",
        }
        
        self._city_data_cache = {}

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
                {"name": f"{city} City Center", "desc": f"{city} 도심 중심부", "duration": "2시간", "fee": "묣료", "time": "오전 10-12시", "reservation_required": False},
                {"name": f"{city} Old Town", "desc": "구시가지", "duration": "3시간", "fee": "묣료", "time": "오후 13-16시", "reservation_required": False},
            ],
            "restaurants": [
                {"name": f"{city} Bistro", "cuisine": "현지식", "price": f"15-25{cur_sym}", "signature": ["파스타", "스테이크"]},
            ],
            "hotels": {
                "budget": [{"name": f"{city} Hotel", "rating": 4.0, "price_per_night": f"{cur_sym}80", "area": "중심가", "pros": "위치 좋음", "cons": "방 작음", "maps_url": f"https://maps.google.com/?q={city}+hotel"}],
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
        
        return {
            "title": f"{city} 여행 완벽 가이드 | {days}일 일정",
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
            "transport": self._generate_transport_section(city, country, cur_sym),
            "total_estimate": self._calculate_total_costs(country, cur_sym, days),
            "emergency": {"contacts": {"general": "112"}, "embassy": {"phone": "+82-2-2100-2100"}},
            "faq": self._generate_faq(city, country, region, days),
            "related_destinations": self._generate_related_destinations(city, country, region),
            "must_reserve": self._generate_must_reserve_list(spots, restaurants),
            "generated_at": datetime.now().isoformat(),
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
            day_restaurants = restaurants[day_num-1:day_num+1] if restaurants else []
            
            # Google Maps URL 추가
            for spot in day_spots:
                if "maps_url" not in spot:
                    spot["maps_url"] = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(spot['name'] + ' ' + city)}"
            for r in day_restaurants:
                if "maps_url" not in r:
                    r["maps_url"] = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(r['name'] + ' ' + city)}"
            
            # 주요 장소 상세 정보
            spots_detail = []
            for i, spot in enumerate(day_spots, 1):
                spots_detail.append({
                    "order": i,
                    "time": spot.get("time", f"오전 {9+i}:00"),
                    "name": spot["name"],
                    "maps_url": spot.get("maps_url", ""),
                    "description": spot.get("desc", ""),
                    "history": spot.get("history", ""),
                    "duration": spot.get("duration", "1-2시간"),
                    "fee": spot.get("fee", "묣료"),
                    "reservation_required": spot.get("reservation_required", False),
                    "reservation_url": spot.get("reservation_url", ""),
                    "tip": spot.get("tip", ""),
                })
            
            # 추천 식당
            restaurants_detail = []
            for r in day_restaurants:
                restaurants_detail.append({
                    "name": r["name"],
                    "maps_url": r.get("maps_url", ""),
                    "cuisine": r.get("cuisine", r.get("type", "현지식")),
                    "price": r.get("price", f"20{cur_sym}"),
                    "signature": r.get("signature", []),
                    "tip": r.get("tip", ""),
                    "reservation_required": r.get("reservation_required", False),
                    "reservation_url": r.get("reservation_url", ""),
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
                "spots": spots_detail,
                "restaurants": restaurants_detail,
                "summary_cost": day_cost,
                "next_day_link": f"day{day_num+1}" if day_num < days else "transport",
            })
        
        return plan

    def _get_day_intro(self, city, country, region, day, total_days, theme):
        """일별 소개 (개인적 톤)"""
        if day == 1:
            return f"첫날은 무리하지 않고 숙소 근처를 둘러보는 것이 좋아요. {city}에 도착하면 일단 숨부터 고르는 것을 추천드려요. 오늘은 {theme.get('theme', '동네 탐험')}을 중심으로 여유롭게 다녀볼 예정이에요."
        elif day == total_days:
            return f"마지막 날이에요. 짐 챙기기 전에 가볍게 마무리하는 날이에요. {city}에서의 추억을 되새기며 여유롭게 마무리하세요."
        else:
            return f"{city}의 {theme.get('theme', '특별한 경험')}을 해보는 날이에요. 현지인들만 아는 멋진 장소와 맛집을 소개해드릴게요."

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
        """일별 비용 계산"""
        food_total = sum([int(re.findall(r'\d+', r.get("price", "0"))[0]) for r in restaurants if re.findall(r'\d+', r.get("price", "0"))])
        activity = len(spots) * 15
        transport = 20 if day in [1, total_days] else 10
        return {
            "transport": f"{transport}{cur_sym}",
            "food": f"{food_total}{cur_sym}",
            "activities": f"{activity}{cur_sym}",
            "total": f"{food_total + activity + transport}{cur_sym}"
        }

    def _calculate_total_costs(self, country, cur_sym, days):
        """총 예상 비용"""
        nights = days - 1
        return {
            "budget": {
                "accommodation": f"80{cur_sym} x {nights}박 = {80*nights}{cur_sym}",
                "food": f"40{cur_sym} x {days}일 = {40*days}{cur_sym}",
                "transport": f"30{cur_sym}",
                "activities": f"50{cur_sym}",
                "total": f"{80*nights + 40*days + 80}{cur_sym}",
            },
            "luxury": {
                "accommodation": f"300{cur_sym} x {nights}박 = {300*nights}{cur_sym}",
                "food": f"100{cur_sym} x {days}일 = {100*days}{cur_sym}",
                "transport": f"100{cur_sym}",
                "activities": f"150{cur_sym}",
                "total": f"{300*nights + 100*days + 250}{cur_sym}",
            }
        }

    def _get_daily_themes(self, city, country, region):
        """일별 테마"""
        return {
            1: {"title": "도착 및 적응", "theme": "느긋한 첫날, 동네 탐험"},
            2: {"title": f"{city} 상징", "theme": "핵심 랜드마크 투어"},
            3: {"title": "문화 체험", "theme": "박물관과 역사 탐방"},
            4: {"title": "특별한 경험", "theme": "숨은 명소와 맛집"},
            5: {"title": "마무리", "theme": "여유로운 마지막 날"},
        }

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
    "London": {
        "spots": [
            {"name": "Big Ben / Elizabeth Tower", "desc": "런던의 상징적인 시계탑. 1859년 완공된 고딕 복건식 건축물로 높이 96미터. 웨스트민스터 궁전과 함께 유네스코 세계문화유산입니다.", "history": "빅벤은 사실 시계탑 안의 종 이름이며, 2012년 엘리자베스 2세의 다이아몬드 주빌리를 기념해 타워 이름이 엘리자베스 타워로 바뀌었어요.", "time": "오전 9:00-10:00", "reservation_required": False, "duration": "30-45분", "fee": "묣료 (외부), 25파운드 (날개 투어)", "address": "London SW1A 0AA", "website": "https://www.parliament.uk/bigben/", "tip": "웨스트민스터 다리에서 빅벤과 템즈강을 함께 담은 사진이 가장 인기 있어요. 일몰 시간대면 금빛으로 물든 타워가 환상적이에요."},
            {"name": "Westminster Abbey", "desc": "영국 왕실의 대성당. 1066년부터 모든 영국 국왕 대관식이 열린 곳으로, 뉴턴, 다윈, 오스틴 등 유명인들이 묻힌 시인의 코너가 유명해요.", "history": "10세기에 건립된 이 성당은 900년 넘는 역사를 지니고 있어요. 윌리엄 셰익스피어를 비롯해 수많은 문인과 과학자들이 기념되고 있어서, 마치 영국 역사의 교과서를 보는 것 같아요.", "time": "오전 10:30-12:30", "reservation_required": True, "reservation_url": "https://www.westminster-abbey.org/visit-us", "duration": "2시간", "fee": "27파운드 (약 5만원)", "address": "20 Deans Yd, London SW1P 3PA", "tip": "오전 9시 30분 오픈런을 하면 여유롭게 볼 수 있어요. 오디오 가이드를 꼭 들으세요."},
            {"name": "Tower of London", "desc": "1078년 윌리엄 1세가 건립한 성. 영국 왕실 볼모인 크라운 주얼을 보관하고 있으며, 900년 역사를 간직한 세계유산이에요.", "history": "한때는 감옥으로도 사용되었던 이곳에서 많은 왕족과 귀족들이 갇혀 지냈어요. 특히 헨리 8세의 두 번째 부인 앤 불린이 처형된 곳으로도 유명하죠. 희생자의 문을 통해 들어가면 그 역사적 무게감이 느껴져요.", "time": "오전 10:00-13:00", "reservation_required": True, "reservation_url": "https://www.hrp.org.uk/tower-of-london/", "duration": "3-4시간", "fee": "33.60파운드 (약 6.2만원)", "address": "London EC3N 4AB", "tip": "요먼 워더(수문장) 투어는 묣료이며 1시간 동안 성의 역사를 재미있게 들려줘요. 10시, 11시 투어를 추천합니다."},
            {"name": "Tower Bridge", "desc": "1894년 완공된 런던의 상징적인 다리. 빅토리아 양식의 타워와 현수교 구조로, 유리바닥 본도에서 42m 높이의 템즈강을 볼 수 있어요.", "history": "산업혁명 시대에 템즈강 하류의 항구 지역과 연결하기 위해 건설되었어요. 당시 최첨단 기술로 만들어진 개황교는 대형 배가 지나갈 때 5분이면 들어 올려질 정도로 신기술이었죠.", "time": "오후 14:00-15:30", "reservation_required": False, "duration": "1시간", "fee": "12.30파운드 (약 2.3만원)", "address": "Tower Bridge Rd, London SE1 2UP", "tip": "일몰 1시간 전에 가면 낮과 밤의 풍경을 모두 볼 수 있어요. 유리바닥 위에서 사진 찍기가 인기예요."},
            {"name": "British Museum", "desc": "세계 최대 규모의 박물관. 이집트 라르손 돌, 로제타 스톤 등 인류 역사의 볼보들을 소장하고 있어요.", "history": "1753년 설립되어 800만 점 이상의 유물을 소장하고 있어요. 대영제국이 전 세계를 누비며 수집한 문화재들을 볼 수 있는 곳이에요. 특히 로제타 스톤은 고대 이집트 상형문자를 핵독하는 열쇠가 된 역사적인 유물이죠.", "time": "오전 10:00-13:00", "reservation_required": True, "reservation_url": "https://www.britishmuseum.org/visit", "duration": "3-4시간", "fee": "묣료 (기부 환영)", "address": "Great Russell St, London WC1B 3DG", "tip": "묣료지만 예약이 필수예요. 이집트관과 그리스관을 우선으로 보세요. 오디오 가이드 대신 공식 앱을 다운로드하세요."},
            {"name": "Borough Market", "desc": "1756년 설립된 런던 최고의 푸드 마켓. 신선한 농산물, 치즈, 해산물, 스트리트 푸드가 100개 이상의 스톨에서 판매돼요.", "history": "런던에서 가장 오래된 야외 시장 중 하나로, 19세기부터 현재 위치에서 운영되고 있어요. 당시 런던의 식재료 유통 중심지였던 이곳은 지금도 영국 최고의 요리사들이 재료를 사러 오는 곳이에요.", "time": "점심 12:00-14:00", "reservation_required": False, "duration": "2-3시간", "fee": "묣료 (음식 별도)", "address": "8 Southwark St, London SE1 1TL", "tip": "목요일 오전이 가장 한적하고 신선해요. 치즈 샌드위치와 오이스터를 꼭 드세요."},
            {"name": "Covent Garden", "desc": "17세기 과일·채소 시장이었던 곳이 현재는 쇼핑 중심지. 거리 공연과 레스토랑이 가득한 곳이에요.", "history": "1630년대에 베드포드 백작이 주택가를 개발하면서 시장으로 번창했어요. 1974년에 현재의 시장 건물이 완공되었고, 지금은 런던의 문화와 쇼핑 중심지가 되었죠. 천장의 유리 돔 아래에서 거리 공연을 보면 시간 가는 줄 몰라요.", "time": "오후 15:00-17:00", "reservation_required": False, "duration": "2-3시간", "fee": "묣료", "address": "Covent Garden, London WC2E 9DD", "tip": "Apple Market은 수공예품을 파는 데 금요일-일요일에만 열려요. 거리 공연은 오후가 피크예요."},
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
            {"name": "나슈마르크트 (Naschmarkt)", "desc": "16세기부터 이어진 빈 최대의 시장. 신선한 농산물, 향신료, 올리브, 치즈 등 120개의 가게와 다양한 레스토랑이 있어요.", "history": "원래 유리병 시장이었던 이곳은 1900년대 초 현재의 위치로 이전했어요. 2차 대전 중 파괴 후 1970년대에 재건축되었죠. 현재는 빈의 다문화 음식 문화를 경험할 수 있는 곳이에요.", "time": "점심 12:00-14:00", "reservation_required": False, "duration": "2시간", "fee": "묣료", "address": "1060 Wien", "tip": "토요일 아침 플리마켓도 함께 열려요. 중동 음식 부스에서 케밥과 팔라펠을 꼭 드세요."},
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
