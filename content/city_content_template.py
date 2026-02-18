"""
Rich Content Template System for All Cities
모든 도시에 적용 가능한 풍부한 콘텐츠 생성 템플릿 - Paris 스타일
"""

from typing import Dict, List
from datetime import datetime
import re

class CityContentTemplate:
    """도시별 풍부한 콘텐츠 생성 템플릿 - Paris 스타일 적용"""
    
    def __init__(self):
        self.currency_map = {
            "France": "유로 (EUR)", "Italy": "유로 (EUR)", "Spain": "유로 (EUR)", 
            "Germany": "유로 (EUR)", "Netherlands": "유로 (EUR)", "Austria": "유로 (EUR)",
            "Greece": "유로 (EUR)", "Portugal": "유로 (EUR)", "Czech Republic": "체코 코루나 (CZK)",
            "UK": "파운드 (GBP)", "Scotland": "파운드 (GBP)",
            "Thailand": "태국 바트 (THB)", "Singapore": "싱가포르 달러 (SGD)",
            "Malaysia": "말레이시아 링깃 (MYR)", "Indonesia": "인도네시아 루피아 (IDR)",
            "Vietnam": "베트남 동 (VND)", "Philippines": "필리핀 페소 (PHP)",
            "Japan": "일본 엔 (JPY)", "Taiwan": "대만 달러 (TWD)",
            "Hong Kong": "홍콩 달러 (HKD)", "Maldives": "몰디브 루피야 (MVR)",
            "USA": "달러 (USD)", "Canada": "캐나다 달러 (CAD)", "Australia": "호주 달러 (AUD)",
            "UAE": "디르함 (AED)", "Turkey": "터키 리라 (TRY)",
        }
    
    def generate_rich_content(self, city: str, country: str, region: str, days: int = 5) -> Dict:
        """Paris 스타일의 풍부한 콘텐츠 생성"""
        
        currency = self.currency_map.get(country, "현지 통화")
        
        # 도시별 특성에 따른 컨텐츠 생성
        spots = self._get_city_spots(city)
        restaurants = self._get_city_restaurants(city)
        hotels = self._get_city_hotels(city, currency)
        
        # 일별 일정 생성 (Paris 스타일의 상세 설명)
        days_plan = self._generate_days_plan(city, country, spots, restaurants, days, currency)
        
        # 예상 비용 계산
        total_estimate = self._calculate_costs(city, country, currency, days)
        
        # 주차 및 교통 정보
        parking_info = self._get_parking_info(city, country)
        transport_summary = self._get_transport_info(country, currency)
        
        # 대사관 정보
        embassy_info = self._get_embassy_info(country)
        emergency_numbers = self._get_emergency_numbers(country)
        
        # SEO 메타정보
        seo_meta = self._generate_seo_meta(city, country, days, region)
        
        return {
            "title": f"{city} 여행 완벽 가이드 | {days}일 상세 일정 + 호텔/비용 총정리",
            "destination": {
                "name": city,
                "country": country,
                "nickname": self._get_city_nickname(city),
                "best_season": self._get_best_season(region),
                "currency": currency,
                "language": self._get_language(country),
                "flight_time": self._get_flight_time(region),
                "days": days,
                "car_rental_available": country not in ["Japan", "Singapore", "Hong Kong"],
                "parking_difficulty": "어려움" if country in ["France", "Italy", "Spain", "UK", "Netherlands"] else "보통",
            },
            "intro": self._generate_intro(city, country, region),
            "hotels": hotels,
            "days_plan": days_plan,
            "parking_info": parking_info,
            "transport_summary": transport_summary,
            "total_estimate": total_estimate,
            "embassy_info": embassy_info,
            "emergency_numbers": emergency_numbers,
            "seo": seo_meta,
            "final_summary": {
                "must_reserve": self._get_reservation_list(city, spots),
                "essential_apps": ["Google Maps", "Google Translate", "Citymapper"],
                "emergency_contacts": emergency_numbers,
                "embassy_info": embassy_info,
                "packing_checklist": self._get_packing_list(region)
            },
            "brave_search_queries": [
                f"{city} travel itinerary",
                f"best restaurants {city}",
                f"{city} hotel recommendations",
                f"{city} transportation guide",
            ],
            "generated_at": datetime.now().isoformat(),
        }
    
    def _generate_days_plan(self, city: str, country: str, spots: List[Dict], restaurants: List[Dict], days: int, currency: str) -> List[Dict]:
        """상세 일별 일정 생성 (Paris 스타일)"""
        themes = self._get_daily_themes(city, country)
        
        days_plan = []
        for day_num in range(1, days + 1):
            theme = themes.get(day_num, {})
            day_spots = self._select_spots_for_day(day, spots)
            day_restaurants = self._select_restaurants_for_day(day, restaurants)
            
            content = self._generate_day_content(city, country, day_num, theme, day_spots, day_restaurants)
            estimated_cost = self._calculate_day_cost(day_restaurants, day_spots, currency)
            
            days_plan.append({
                "day": day_num,
                "title": theme.get("title", f"Day {day_num} 탐험"),
                "theme": theme.get("theme", "도시 탐방"),
                "content": content,
                "spots": day_spots,
                "restaurants": day_restaurants,
                "transport": theme.get("transport", "도보/대중교통"),
                "estimated_cost": estimated_cost
            })
        
        return days_plan
    
    def _generate_day_content(self, city: str, country: str, day: int, theme: Dict, spots: List[Dict], restaurants: List[Dict]) -> str:
        """일별 상세 설명 생성 (Paris 스타일의 풍부한 서술)"""
        
        title = theme.get("title", f"{city} 탐험 Day {day}")
        theme_desc = theme.get("theme", "")
        
        lines = [f"📍 {title}", f"테마: {theme_desc}", ""]
        
        # 예약 필요 여부
        needs_reservation = any(s.get("reservation_required") for s in spots)
        if needs_reservation:
            lines.append("🎫 예약 필요: 일부 명소는 미리 예약이 필요합니다 (아래 링크 참조)")
        else:
            lines.append("📍 예약 필요: 없음 (자유롭게 방문 가능)")
        lines.append("")
        
        # Day별 소개 문단
        intro = self._generate_day_intro(city, day, theme)
        lines.append(intro)
        lines.append("")
        
        # 장소별 상세 설명
        for i, spot in enumerate(spots, 1):
            spot_text = self._generate_spot_description(spot, i)
            lines.append(spot_text)
            lines.append("")
        
        # 식당 추천
        if restaurants:
            lines.append("🍽️ 오늘의 추천 식당:")
            for r in restaurants:
                res_tag = " (예약 필수)" if r.get("reservation_required") else ""
                res_link = f" [예약]({r.get('reservation_url')})" if r.get("reservation_url") else ""
                price = r.get("price", "가격 문의")
                lines.append(f"- **[{r['name']}]({r.get('maps_url', '#')})** ({r.get('type', '식당')}){res_tag}{res_link}")
                lines.append(f"  가격: {price} | {r.get('tip', '')}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_spot_description(self, spot: Dict, index: int) -> str:
        """장소별 상세 설명"""
        name = spot["name"]
        desc = spot.get("desc", "")
        time = spot.get("time", "")
        tip = spot.get("tip", "")
        maps_url = spot.get("maps_url", "#")
        
        lines = [f"{index}. **[{name}]({maps_url})**"]
        lines.append(f"   {desc}")
        if time:
            lines.append(f"   ⏰ 추천 시간: {time}")
        if tip:
            lines.append(f"   💡 팁: {tip}")
        
        return "\n".join(lines)
    
    def _generate_day_intro(self, city: str, day: int, theme: Dict) -> str:
        """일별 소개 문단"""
        intros = {
            1: f"첫날은 무리하지 않고 숙소 근처를 둘러보는 것이 좋아요. 비행기 피로도 풀면서 동네 감을 잡는 것이 중요하더라구요. {city}에 도착하면 일단 숨부터 고르는 것을 추천드려요. 오늘은 {theme.get('theme', '동네 탐험')}을 중심으로 여유롭게 다녀볼 예정이에요.",
            2: f"오늘은 {city}의 상징적인 명소들을 볼 예정이에요. 하지만 무턱대고 가면 줄 때문에 시간을 날릴 수 있어서, 미리 예약하고 아침 일찍 가는 것이 필수랍니다. 현지인들이 추천하는 숨은 명소도 함께 둘러보실 거예요.",
            3: f"오늘은 {city}의 문화와 예술을 느껴보는 날이에요. {theme.get('theme', '문화 탐방')}을 중심으로 현지의 분위기를 제대로 경험해보세요. 사전 예약이 필요한 곳이 있으니 아래 내용을 꼭 확인해주세요.",
            4: f"{city}에서 가장 {theme.get('theme', '특별한 경험')}을 해보는 날이에요. 현지인들만 아는 멋진 장소와 맛집을 소개해드릴게요. 오늘은 평소보다 여유롭게 다녀오시는 것을 추천드려요.",
            5: f"마지막 날이에요. 짐 챙기기 전에 가볍게 마무리하는 날이에요. 빠진 곳이 있다면 채우고, 쇼핑할 거라면 오늘이 마지막 기회예요. {city}에서의 추억을 되새기며 여유롭게 마무리하세요.",
        }
        return intros.get(day, f"Day {day}: {city}의 매력을 느껴보는 날이에요.")
    
    def _get_city_spots(self, city: str) -> List[Dict]:
        """도시별 주요 명소"""
        from content.city_templates import get_city_spots
        spots = get_city_spots(city)
        
        # Google Maps 링크 추가
        for spot in spots:
            if "maps_url" not in spot:
                query = f"{spot['name']} {city}".replace(" ", "+")
                spot["maps_url"] = f"https://www.google.com/maps/search/?api=1&query={query}"
        
        return spots
    
    def _get_city_restaurants(self, city: str) -> List[Dict]:
        """도시별 추천 식당"""
        from content.city_templates import get_city_restaurants
        restaurants = get_city_restaurants(city)
        
        # Google Maps 링크 추가
        for r in restaurants:
            if "maps_url" not in r:
                query = f"{r['name']} {city}".replace(" ", "+")
                r["maps_url"] = f"https://www.google.com/maps/search/?api=1&query={query}"
        
        return restaurants
    
    def _get_city_hotels(self, city: str, currency: str) -> Dict:
        """도시별 호텔 정보"""
        return {
            "budget": [
                {
                    "name": f"{city} Central Hotel",
                    "rating": 4.0,
                    "price_per_night": f"60-90{currency[:3]}",
                    "area": "시내 중심",
                    "pros": "교통 편리, 청결",
                    "cons": "객실이 작은 편",
                    "maps_url": f"https://www.google.com/maps/search/hotel+{city}+budget"
                }
            ],
            "luxury": [
                {
                    "name": f"The {city} Palace",
                    "rating": 4.8,
                    "price_per_night": f"300-500{currency[:3]}",
                    "area": "최고급 지역",
                    "pros": "럭셔리 서비스, 중심 위치",
                    "cons": "가격대가 높음",
                    "maps_url": f"https://www.google.com/maps/search/luxury+hotel+{city}"
                }
            ],
        }
    
    def _select_spots_for_day(self, day: int, all_spots: List[Dict]) -> List[Dict]:
        """해당 일자에 맞는 명소 선택"""
        if not all_spots:
            return []
        
        per_day = 3
        start = (day - 1) * per_day
        selected = all_spots[start:start + per_day]
        
        # 부족하면 순환
        while len(selected) < per_day and all_spots:
            selected.extend(all_spots[:per_day - len(selected)])
        
        return selected[:per_day]
    
    def _select_restaurants_for_day(self, day: int, all_restaurants: List[Dict]) -> List[Dict]:
        """해당 일자에 맞는 식당 선택"""
        if not all_restaurants:
            return []
        
        per_day = 2
        start = (day - 1) * per_day
        selected = all_restaurants[start:start + per_day]
        
        while len(selected) < per_day and all_restaurants:
            selected.extend(all_restaurants[:per_day - len(selected)])
        
        return selected[:per_day]
    
    def _get_daily_themes(self, city: str, country: str) -> Dict:
        """일별 테마"""
        return {
            1: {"title": "도착 & 동네 적응하기", "theme": "느긋한 첫날, 동네 탐험", "transport": "공항 리무진 + 도보"},
            2: {"title": f"{city}의 상징", "theme": "핵심 랜드마크 투어", "transport": "Metro/대중교통"},
            3: {"title": "문화 & 예술", "theme": "박물관과 역사", "transport": "Metro/대중교통"},
            4: {"title": "특별한 경험", "theme": "숨은 명소와 맛집", "transport": "Metro + 도보"},
            5: {"title": "마무리 & 쇼핑", "theme": "여유로운 마지막 날", "transport": "Metro + 공항 리무진"},
        }
    
    def _get_city_nickname(self, city: str) -> str:
        """도시 별칭"""
        nicknames = {
            "Paris": "빛의 도시", "Rome": "영원한 도시", "London": "대영제국의 심장",
            "Barcelona": "가우디의 도시", "Amsterdam": "운하의 도시", "Prague": "천의 도시",
            "Vienna": "음악의 도시", "Lisbon": "일곱 개의 언덱 위 도시", "Berlin": "역사와 현대의 도시",
            "Tokyo": "전통과 미래의 교차로", "Kyoto": "천 개의 신사가 있는 도시", "Bangkok": "천사의 도시",
            "Singapore": "정원 도시", "Bali": "신들의 섬", "Maldives": "낙원 on Earth",
            "New York": "세계의 수도", "Sydney": "하버 시티", "Dubai": "사막의 보석",
        }
        return nicknames.get(city, f"매력적인 {city}")
    
    def _get_best_season(self, region: str) -> str:
        """지역별 최적 여행 시즌"""
        seasons = {
            "유럽": "4-6월, 9-10월 (봄/가을)",
            "동남아": "11-2월 (건기)",
            "휴양지": "11-4월 (건기)",
            "동아시아": "3-5월, 9-11월 (봄/가을)",
            "미주": "4-6월, 9-11월",
            "중동": "11-3월 (서늘한 계절)",
            "오세아니아": "9-11월, 3-5월",
        }
        return seasons.get(region, "봄/가을")
    
    def _get_language(self, country: str) -> str:
        """국가별 언어"""
        languages = {
            "France": "프랑스어", "Italy": "이탈리아어", "Spain": "스페인어",
            "Germany": "독일어", "Netherlands": "네덜란드어",
            "Thailand": "태국어", "Singapore": "영어/중국어/말레이어",
            "Japan": "일본어", "Maldives": "디베히어/영어",
            "USA": "영어", "Australia": "영어", "Dubai": "아랍어/영어",
        }
        return languages.get(country, "현지 언어")
    
    def _get_flight_time(self, region: str) -> str:
        """지역별 비행 시간"""
        times = {
            "유럽": "직항 약 12-14시간",
            "동남아": "직항 약 5-7시간",
            "휴양지": "직항 약 6-12시간",
            "동아시아": "직항 약 2-3시간",
            "미주": "직항 약 13-15시간",
            "중동": "직항 약 10-12시간",
            "오세아니아": "직항 약 10-12시간",
        }
        return times.get(region, "약 10-14시간")
    
    def _generate_intro(self, city: str, country: str, region: str) -> str:
        """도시 소개"""
        intros = {
            "유럽": f"{city}는 역사와 현대가 공존하는 매력적인 도시예요. 골목골목 숨은 명소들이 가득하고, 현지인들의 여유로운 라이프스타일도 느껴볼 수 있어요.",
            "동남아": f"{city}는 저렴한 물가와 친절한 사람들, 그리고 멋진 자연이 어우러진 곳이에요. 길거리 음식부터 고급 레스토랑까지 다양한 먹거리가 가득해요.",
            "휴양지": f"{city}는 일상에서 벗어나 완벽한 휴식을 취하기 좋은 곳이에요. 아름다운 해변과 고급스러운 리조트에서 특별한 시간을 보내실 수 있어요.",
            "동아시아": f"{city}는 전통과 현대가 독특하게 조화된 도시예요. 고즈넉한 사원부터 하이테크 빌딩까지 다양한 모습을 볼 수 있어요.",
        }
        return intros.get(region, f"{city}는 {country}의 매력적인 도시로, 특별한 추억을 만들기 좋은 곳이에요.")
    
    def _calculate_costs(self, city: str, country: str, currency: str, days: int) -> Dict:
        """예상 비용 계산"""
        base = {
            "France": (85, 400, 40, 120), "Italy": (80, 350, 35, 100),
            "Spain": (70, 300, 30, 90), "Netherlands": (90, 380, 40, 110),
            "Thailand": (25, 150, 15, 60), "Japan": (70, 300, 35, 100),
            "USA": (100, 400, 50, 150),
        }
        
        hb, hl, fb, fl = base.get(country, (60, 250, 30, 90))
        nights = days - 1
        
        cur = currency.split()[0] if " " in currency else currency
        
        return {
            "budget": {
                "accommodation": f"{hb}{cur} x {nights}박 = {hb * nights}{cur}",
                "food": f"{fb}{cur} x {days}일 = {fb * days}{cur}",
                "transport": f"50{cur}",
                "activities": f"100{cur}",
                "total": f"{hb * nights + fb * days + 150}{cur}"
            },
            "luxury": {
                "accommodation": f"{hl}{cur} x {nights}박 = {hl * nights}{cur}",
                "food": f"{fl}{cur} x {days}일 = {fl * days}{cur}",
                "transport": f"150{cur}",
                "activities": f"300{cur}",
                "total": f"{hl * nights + fl * days + 450}{cur}"
            }
        }
    
    def _calculate_day_cost(self, restaurants: List[Dict], spots: List[Dict], currency: str) -> Dict:
        """일별 비용"""
        food = sum(int(re.findall(r'\d+', r.get("price", "0"))[0]) for r in restaurants if re.findall(r'\d+', r.get("price", "0")))
        activity = len(spots) * 10
        transport = 10
        cur = currency.split()[0] if " " in currency else currency
        
        return {
            "transport": f"{transport}{cur}",
            "food": f"{food}{cur}",
            "activities": f"{activity}{cur}",
            "total": f"{food + activity + transport}{cur}"
        }
    
    def _get_parking_info(self, city: str, country: str) -> Dict:
        """주차 정보"""
        return {
            "difficulty": "어려움" if country in ["France", "Italy", "Spain", "UK", "Netherlands"] else "보통",
            "city_center_rate": "시간당 3-6유로/달러",
            "recommendation": "도심은 대중교통 이용 권장",
            "pr_locations": [{"name": f"{city} P+R", "rate": "하루 10-15", "metro": "Line 1", "maps_url": f"https://maps.google.com/?q={city}+parking"}],
            "apps": ["Parkopedia"],
            "tips": ["대중교통 이용 권장", "P+R 주차장 활용"]
        }
    
    def _get_transport_info(self, country: str, currency: str) -> Dict:
        """교통 정보"""
        cur = currency.split()[0] if " " in currency else currency
        return {
            "metro": f"1회 2-3{cur}",
            "uber": f"도심 10-20{cur}",
            "taxi": f"기본 3-5{cur} + km당 1-2{cur}",
            "rental_car": f"하루 50-80{cur}",
        }
    
    def _get_embassy_info(self, country: str) -> Dict:
        """대사관 정보"""
        embassies = {
            "France": {"name": "주프랑스 한국대사관", "phone": "+33-1-47-53-01-01", "address": "125 rue de Grenelle, 75007 Paris", "hours": "월-금 09:00-12:00, 14:00-17:00", "website": "https://overseas.mofa.go.kr/fr-ko/index.do"},
            "Netherlands": {"name": "주네덜란드 한국대사관", "phone": "+31-70-416-4646", "address": "Verlengde Tolweg 10, 2517 JV Den Haag", "hours": "월-금 09:00-12:00, 13:30-16:30", "website": "https://overseas.mofa.go.kr/nl-ko/index.do"},
            "Italy": {"name": "주이탈리아 한국대사관", "phone": "+39-06-802-461", "address": "Via Barnaba Oriani 30, 00197 Roma", "hours": "월-금 09:00-12:30, 14:00-17:00", "website": "https://overseas.mofa.go.kr/it-ko/index.do"},
        }
        return embassies.get(country, {"name": "해당국 대사관", "phone": "외교부 확인", "website": "https://www.mofa.go.kr"})
    
    def _get_emergency_numbers(self, country: str) -> Dict:
        """긴급 연락처"""
        numbers = {
            "France": {"police": "17", "fire": "18", "ambulance": "15", "general": "112"},
            "Netherlands": {"police": "112", "fire": "112", "ambulance": "112", "general": "112"},
            "Italy": {"police": "113", "fire": "115", "ambulance": "118", "general": "112"},
        }
        return numbers.get(country, {"general": "112", "police": "112", "fire": "112", "ambulance": "112"})
    
    def _get_reservation_list(self, city: str, spots: List[Dict]) -> List[Dict]:
        """예약 필수 목록"""
        must_reserve = []
        for spot in spots:
            if spot.get("reservation_required"):
                must_reserve.append({
                    "name": spot["name"],
                    "when": "사전 예약",
                    "url": spot.get("reservation_url", spot.get("maps_url", "#"))
                })
        return must_reserve
    
    def _get_packing_list(self, region: str) -> List[str]:
        """준비물 목록"""
        base = ["여권/비자", "여행자보험", "보조배터리", "편한 신발"]
        extras = {
            "유럽": ["유니버셜 어댑터", "우산", "보온용품"],
            "동남아": ["선크림", "모기약", "여름옷"],
            "휴양지": ["수영복", "선글라스", "비치타월"],
            "동아시아": ["보온용품", "우산", "편한 신발"],
        }
        return base + extras.get(region, [])
    
    def _generate_seo_meta(self, city: str, country: str, days: int, region: str) -> Dict:
        """SEO 메타정보"""
        return {
            "keywords": [f"{city} 여행", f"{country} 여행", "해외여행", "여행 가이드"],
            "hashtags": [f"#{city}여행", f"#{country}여행", "#해외여행", "#여행가이드"],
            "meta_description": f"{city} {days}일 여행 완벽 가이드. {country}의 매력적인 관광지, 맛집, 호텔 추천.",
            "title_tag": f"{city} 여행 {days}일 완벽 가이드 | {country} 관광 코스 추천",
        }


# 인스턴스 생성
city_template = CityContentTemplate()
