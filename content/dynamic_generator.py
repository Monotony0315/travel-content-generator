"""
Dynamic City Content Generator - Rich Blogger Style with Detailed Content
도시별 상세 콘텐츠 생성기
"""

from typing import Dict, List, Optional
from datetime import datetime
from content.city_templates import get_city_spots
from content.detailed_cities import CITY_DATABASE, COUNTRY_EMERGENCY, RESERVATION_REQUIRED

# 국가별 상세 대사관 정보
EMBASSY_DETAILS = {
    "France": {
        "name": "주프랑스 한국대사관",
        "phone": "+33-1-47-53-01-01",
        "emergency_phone": "+33-1-47-53-01-01 (업무시간 후 긴급건)",
        "address": "125 rue de Grenelle, 75007 Paris, France",
        "hours": "월-금 09:00-12:00, 14:00-17:00",
        "email": "koreanembassy@mofa.go.kr",
        "website": "https://overseas.mofa.go.kr/fr-ko/index.do",
        "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무"]
    },
    "Italy": {
        "name": "주이탈리아 한국대사관",
        "phone": "+39-06-802-461",
        "emergency_phone": "+39-06-802-461 (업무시간 후 긴급건)",
        "address": "Via Barnaba Oriani 30, 00197 Roma, Italy",
        "hours": "월-금 09:00-12:30, 14:00-17:00",
        "email": "koreaembassy@mofa.go.kr",
        "website": "https://overseas.mofa.go.kr/it-ko/index.do",
        "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무"]
    },
    "Spain": {
        "name": "주스페인 한국대사관",
        "phone": "+34-91-353-2000",
        "emergency_phone": "+34-91-353-2000 (업무시간 후 긴급건)",
        "address": "Calle González Amigó 15, 28036 Madrid, Spain",
        "hours": "월-금 09:00-13:00, 14:00-17:00",
        "email": "koremb@mofa.go.kr",
        "website": "https://overseas.mofa.go.kr/es-ko/index.do",
        "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무"]
    },
    "Germany": {
        "name": "주독일 한국대사관",
        "phone": "+49-30-203-610",
        "emergency_phone": "+49-30-203-610 (업무시간 후 긴급건)",
        "address": "Leipziger Platz 3, 10117 Berlin, Germany",
        "hours": "월-금 09:00-12:00, 14:00-17:00",
        "email": "info@koreanembassy.de",
        "website": "https://overseas.mofa.go.kr/de-ko/index.do",
        "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무"]
    },
    "UK": {
        "name": "주영국 한국대사관",
        "phone": "+44-20-7227-5500",
        "emergency_phone": "+44-20-7227-5500 (업무시간 후 긴급건)",
        "address": "60 Buckingham Gate, London SW1E 6AJ, UK",
        "hours": "월-금 09:30-12:30, 14:00-17:00",
        "email": "info@koreanembassy.org.uk",
        "website": "https://overseas.mofa.go.kr/gb-ko/index.do",
        "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무"]
    },
    "Japan": {
        "name": "주일본 한국대사관",
        "phone": "+81-3-3452-7611",
        "emergency_phone": "+81-90-3320-3111 (재외국민 긴급전화)",
        "address": "1-2-5 Minami-Azabu, Minato-ku, Tokyo 106-0047, Japan",
        "hours": "월-금 09:30-12:00, 13:30-16:30",
        "email": "info@koreaembassy.jp",
        "website": "https://overseas.mofa.go.kr/jp-ko/index.do",
        "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무"]
    },
    "Thailand": {
        "name": "주태국 한국대사관",
        "phone": "+66-2-247-7530",
        "emergency_phone": "+66-81-826-5666 (재외국민 긴급전화)",
        "address": "23 Thiam-Ruammit Road, Ratchadapisek, Huai Khwang, Bangkok 10320, Thailand",
        "hours": "월-금 09:00-12:00, 13:30-16:00",
        "email": "korembassy@mofa.go.kr",
        "website": "https://overseas.mofa.go.kr/th-ko/index.do",
        "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무"]
    },
    "Singapore": {
        "name": "주싱가포르 한국대사관",
        "phone": "+65-6256-1188",
        "emergency_phone": "+65-9236-5413 (재외국민 긴급전화)",
        "address": "47 Scotts Road, #08-00 Goldbell Towers, Singapore 228233",
        "hours": "월-금 09:00-12:00, 14:00-17:00",
        "email": "koreanembassy@mofa.go.kr",
        "website": "https://overseas.mofa.go.kr/sg-ko/index.do",
        "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무"]
    },
    "USA": {
        "name": "주미국 한국대사관",
        "phone": "+1-202-939-5600",
        "emergency_phone": "+1-202-939-5600 (24시간 긴급)",
        "address": "2450 Massachusetts Avenue NW, Washington, DC 20008, USA",
        "hours": "월-금 09:00-12:00, 13:30-17:00",
        "email": "washington@mofa.go.kr",
        "website": "https://overseas.mofa.go.kr/us-ko/index.do",
        "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무"]
    },
    "Vietnam": {
        "name": "주베트남 한국대사관",
        "phone": "+84-24-3831-5116",
        "emergency_phone": "+84-24-3831-5116 (업무시간 후 긴급건)",
        "address": "63-65 Ly Thai To, Hoan Kiem, Hanoi, Vietnam",
        "hours": "월-금 09:00-12:00, 14:00-17:00",
        "email": "koremb@mofa.go.kr",
        "website": "https://overseas.mofa.go.kr/vn-ko/index.do",
        "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무"]
    },
}

# 기본 대사관 정보 (국가가 목록에 없을 경우)
DEFAULT_EMBASSY = {
    "name": "주재국 한국대사관 정보",
    "phone": "해당 국가 대사관 전화번호 확인 필요",
    "emergency_phone": "외교부 영사콜센터 +82-2-3210-0404 (24시간)",
    "address": "외교부 홈페이지에서 확인",
    "hours": "해당 대사관 홈페이지 확인",
    "email": "홈페이지 참조",
    "website": "https://www.mofa.go.kr",
    "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록"]
}

class DynamicCityContentGenerator:
    """동적 도시 콘텐츠 생성기 - 상세 버전"""
    
    def _generate_seo_meta(self, city: str, country: str, days: int, region: str = "유럽") -> Dict:
        """SEO 메타정보 및 해시태그 생성"""
        # 기본 키워드
        base_keywords = [
            f"{city} 여행", f"{country} 여행", "해외여행", "여행 가이드",
            f"{city} 여행 코스", f"{city} 여행 일정", f"{city} 맛집",
            f"{city} 호텔", f"{city} 관광", f"{city} 가볼만한 곳"
        ]
        
        # 지역별 키워드
        region_keywords = {
            "유럽": ["유럽여행", "유럽 자유여행", "유럽 배낭여행", "유럽 루트"],
            "동남아": ["동남아 여행", "동남아시아", "베트남 여행", "태국 여행", "발리 여행"],
            "휴양지": ["휴양지 추천", "리조트", "필리핀 여행", "몰디브", "푸켓", "허니문", "신혼여행"],
            "동아시아": ["일본 여행", "대만 여행", "홍콩 여행", "도쿄 여행", "오키나와"],
            "미주": ["미국 여행", "캐나다 여행", "LA 여행", "뉴욕 여행", "하와이"],
            "중동": ["두바이 여행", "터키 여행", "이스탄불"],
            "오세아니아": ["호주 여행", "시드니 여행", "뉴질랜드"],
            "중남미": ["멕시코 여행", "칸쿤", "페루", "마추픽추"],
            "남아시아": ["인도 여행", "네팔", "스리랑카"],
            "아프리카": ["남아공 여행", "이집트", "모로코", "케냐"]
        }
        
        keywords = base_keywords + region_keywords.get(region, [])
        
        # 해시태그 생성 (25-30개)
        hashtags = [
            f"#{city.replace(' ', '')}여행", f"#{country.replace(' ', '')}여행",
            "#해외여행", "#여행가이드", "#여행코스", "#여행일정",
            f"#{city.replace(' ', '')}맛집", f"#{city.replace(' ', '')}호텔",
            "#배낭여행", "#자유여행", "#혼자여행", "#커플여행", "#가족여행",
            f"#{region}여행" if region != "휴양지" else "#휴양지여행",
            "#여행블로거", "#여행스타그램", "#여행에미치다", "#세계여행",
            "#맛집탐방", "#카페투어", "#인생샷", "#여행사진",
            "#호캉스" if region == "휴양지" else "#관광",
            f"#{days}박{days+1}일", "#여행준비", "#여행꿀팁",
            "#해외여행준비", "#여행추천", "#여행기록"
        ]
        
        # 중복 제거
        unique_hashtags = list(set(hashtags))
        
        # SEO 메타 설명 (150자 이내)
        meta_description = f"{city} {days}일 여행 완벽 가이드. {country}의 매력적인 관광지, 맛집, 호텔 추천과 함께 최적의 여행 코스를 확인하세요."
        if len(meta_description) > 150:
            meta_description = meta_description[:147] + "..."
        
        return {
            "keywords": keywords,
            "hashtags": unique_hashtags,
            "meta_description": meta_description,
            "title_tag": f"{city} 여행 {days}일 완벽 가이드 | {country} 관광 코스 추천",
            "og_title": f"{city} {days}일 여행 가이드 - {country}",
            "og_description": f"{city}의 숨은 명소부터 인기 맛집까지! {days}일 일정으로 떠나는 완벽한 {country} 여행"
        }
    
    def __init__(self):
        self.currency_map = {
            "France": "유로 (EUR)", "Italy": "유로 (EUR)", "Spain": "유로 (EUR)", 
            "Germany": "유로 (EUR)", "Netherlands": "유로 (EUR)", "Austria": "유로 (EUR)",
            "Greece": "유로 (EUR)", "Portugal": "유로 (EUR)", "Czech Republic": "체코 코루나 (CZK)",
            "Hungary": "헝가리 포린트 (HUF)", "Croatia": "유로 (EUR)", "UK": "파운드 (GBP)",
            "Scotland": "파운드 (GBP)", "Denmark": "덴ish 크로네 (DKK)", "Sweden": "스웨덴 크로나 (SEK)",
            "Thailand": "태국 바트 (THB)", "Singapore": "싱가포르 달러 (SGD)", "Malaysia": "말레이시아 링깃 (MYR)",
            "Indonesia": "인도네시아 루피아 (IDR)", "Vietnam": "베트남 동 (VND)", "Philippines": "필리핀 페소 (PHP)",
            "Cambodia": "캄볼디아 리엘 (KHR)", "Myanmar": "미얀마 차트 (MMK)", "Laos": "라오스 킵 (LAK)",
            "Japan": "일본 엔 (JPY)", "Taiwan": "대만 달러 (TWD)", "Hong Kong": "홍콩 달러 (HKD)",
            "South Korea": "원 (KRW)", "Maldives": "몰디브 루피야 (MVR)", "Fiji": "피지 달러 (FJD)",
            "Seychelles": "세이셸 루피 (SCR)", "Mauritius": "모리셔스 루피 (MUR)",
            "USA": "달러 (USD)", "Canada": "캐나다 달러 (CAD)", "Australia": "호주 달러 (AUD)",
            "UAE": "디르함 (AED)", "Turkey": "터키 리라 (TRY)",
        }
        
        self.flight_time_map = {
            "France": "직항 약 12시간", "Italy": "직항 약 13시간", "Spain": "직항 약 14시간",
            "Germany": "직항 약 11시간", "Netherlands": "직항 약 11시간", "Austria": "직항 약 11시간",
            "Greece": "직항 약 13시간", "Portugal": "직항 약 14시간", "Czech Republic": "직항 약 11시간",
            "Hungary": "직항 약 11시간", "Croatia": "직항 약 12시간", "UK": "직항 약 12시간",
            "Scotland": "직항 약 12시간", "Denmark": "직항 약 10시간", "Sweden": "직항 약 10시간",
            "Thailand": "직항 약 6시간", "Singapore": "직항 약 6.5시간", "Malaysia": "직항 약 7시간",
            "Indonesia": "직항 약 7시간", "Vietnam": "직항 약 5시간", "Philippines": "직항 약 4시간",
            "Cambodia": "경유 약 6시간", "Myanmar": "경유 약 6시간", "Laos": "경유 약 6시간",
            "Japan": "직항 약 2시간", "Taiwan": "직항 약 2.5시간", "Hong Kong": "직항 약 3.5시간",
            "South Korea": "직항 약 1시간", "Maldives": "경유 약 9시간", "Fiji": "경유 약 12시간",
            "Seychelles": "경유 약 11시간", "Mauritius": "경유 약 12시간",
            "USA": "직항 약 13시간", "Canada": "직항 약 10시간", "Australia": "직항 약 10시간",
            "UAE": "직항 약 9시간", "Turkey": "직항 약 11시간",
        }
    
    def generate_basic_content(self, city_name: str, country: str, region: str) -> Optional[Dict]:
        """도시 기본 정보로 콘텐츠 생성"""
        
        # 상세 데이터베이스에 있으면 사용
        if city_name in CITY_DATABASE:
            return self._generate_from_detailed(city_name, country, region)
        
        # 없으면 기본 템플릿 사용
        return self._generate_basic_template(city_name, country, region)
    
    def _generate_from_detailed(self, city_name: str, country: str, region: str) -> Dict:
        """상세 데이터베이스에서 콘텐츠 생성"""
        
        currency = self.currency_map.get(country, "현지 통화")
        flight_time = self.flight_time_map.get(country, "약 10-12시간")
        
        detailed = CITY_DATABASE[city_name]
        
        # 일정 구성
        days_plan = []
        for day_num in range(1, 6):
            day_key = f"day{day_num}"
            if day_key in detailed:
                day_data = detailed[day_key]
                day_plan = {
                    "day": day_num,
                    "title": day_data["title"],
                    "theme": day_data["theme"],
                    "content": day_data["content"],
                    "spots": day_data.get("spots", []),
                    "restaurants": day_data.get("restaurants", []),
                    "transport": "도보 및 대중교통",
                    "estimated_cost": {"transport": "€20", "food": "€60", "activities": "€30", "total": "€110"},
                }
                days_plan.append(day_plan)
        
        # 예약 필수 목록
        must_reserve = RESERVATION_REQUIRED.get(city_name, [
            {"name": "주요 관광지", "when": "사전 확인", "url": f"https://www.google.com/search?q={city_name}+tickets", "note": "온라인 예매 권장"},
        ])
        
        # 정확한 비상 연락처 및 대사관 정보
        emergency = COUNTRY_EMERGENCY.get(country, {
            "police": "112", "ambulance": "112", "fire": "112", "general": "112"
        })
        embassy_info = EMBASSY_DETAILS.get(country, DEFAULT_EMBASSY)
        
        # SEO 메타정보 생성
        seo_meta = self._generate_seo_meta(city_name, country, 5, region)
        
        return {
            "title": f"{city_name} 여행 완벽 가이드 | 5일 상세 일정 + 예약/비용 총정리",
            "destination": {
                "name": city_name,
                "country": country,
                "nickname": f"{city_name} 여행",
                "best_season": self._get_best_season(region),
                "currency": currency,
                "flight_time": flight_time,
                "days": 5,
                "car_rental_available": region != "유럽",
                "parking_difficulty": "어려움" if region == "유럽" else "보통",
            },
            "intro": self._get_intro(city_name, country),
            "seo": seo_meta,
            "hotels": {
                "budget": [
                    {
                        "name": f"{city_name} Boutique Hotel",
                        "rating": 4.2,
                        "price_per_night": "€85-110" if country in ["France", "Italy", "Spain"] else "$60-80",
                        "area": "시내 중심, 지하철 근처",
                        "pros": "교통 편리, 조식 포함, 친절한 직원",
                        "cons": "객실이 다소 작음",
                        "maps_url": f"https://www.google.com/maps/search/{city_name}+boutique+hotel"
                    },
                ],
                "luxury": [
                    {
                        "name": f"{city_name} Palace Hotel",
                        "rating": 4.8,
                        "price_per_night": "€400-600" if country in ["France", "Italy", "Spain"] else "$300-500",
                        "area": "역사적 중심지",
                        "pros": "최고급 시설, 레스토랑, 스파",
                        "cons": "가격대가 높음",
                        "maps_url": f"https://www.google.com/maps/search/{city_name}+palace+hotel"
                    },
                ],
            },
            "days_plan": days_plan,
            "parking_info": {
                "difficulty": "어려움" if region == "유럽" else "보통",
                "city_center_rate": "시간당 €4-6" if region == "유럽" else "시간당 $2-4",
                "recommendation": "대중교통 이용 권장" if region == "유럽" else "택시 또는 지하철 이용",
                "pr_locations": [],
                "apps": ["Google Maps", "Citymapper"],
                "tips": ["도심은 지하철이 가장 편리해요", "택시는 미터기 확인 필수"]
            },
            "transport_summary": {
                "metro": "1회 €1.9" if country in ["France", "Italy", "Spain"] else "1회 $1-2",
                "taxi": "시작 €7" if country in ["France", "Italy", "Spain"] else "시작 $3",
                "uber": "도심 €10-20" if country in ["France", "Italy", "Spain"] else "도심 $5-15",
                "rental_car": "비추천" if region == "유럽" else "하루 $40-60",
            },
            "total_estimate": {
                "budget": {
                    "accommodation": "€90 x 4박 = 360유로" if country in ["France", "Italy", "Spain"] else "$70 x 4박 = $280",
                    "food": "€50 x 5일 = 250유로" if country in ["France", "Italy", "Spain"] else "$40 x 5일 = $200",
                    "transport": "€70" if country in ["France", "Italy", "Spain"] else "$60",
                    "activities": "€100" if country in ["France", "Italy", "Spain"] else "$80",
                    "total": f"€780 (약 114만원)" if country in ["France", "Italy", "Spain"] else "$620 (약 91만원)"
                },
                "luxury": {
                    "accommodation": "€500 x 4박 = 2,000유로" if country in ["France", "Italy", "Spain"] else "$400 x 4박 = $1,600",
                    "food": "€120 x 5일 = 600유로" if country in ["France", "Italy", "Spain"] else "$100 x 5일 = $500",
                    "transport": "€150" if country in ["France", "Italy", "Spain"] else "$150",
                    "activities": "€200" if country in ["France", "Italy", "Spain"] else "$150",
                    "total": f"€2,950 (약 431만원)" if country in ["France", "Italy", "Spain"] else "$2,400 (약 351만원)"
                }
            },
            "brave_search_queries": [
                f"{city_name} travel guide 2024",
                f"{city_name} best restaurants local",
                f"{city_name} things to do itinerary",
                f"{city_name} transportation tips",
            ],
            "final_summary": {
                "must_reserve": must_reserve,
                "essential_apps": ["Google Maps", "Google Translate", "Citymapper", "TripAdvisor"],
                "emergency_contacts": emergency,
                "embassy_info": embassy_info,
                "packing_checklist": ["여권", "여행자 보험", "현금/카드", "유니버셜 어댑터", "편한 신발", "우산"]
            },
            "generated_at": datetime.now().isoformat(),
        }
    
    def _generate_basic_template(self, city_name: str, country: str, region: str) -> Dict:
        """기본 템플릿으로 콘텐츠 생성 (상세 데이터 없는 도시용)"""
        # ... (기존 코드 유지)
        currency = self.currency_map.get(country, "현지 통화")
        flight_time = self.flight_time_map.get(country, "약 10-12시간")
        
        # 정확한 비상 연락처 및 대사관 정보
        emergency = COUNTRY_EMERGENCY.get(country, {
            "police": "112", "ambulance": "112", "fire": "112", "general": "112"
        })
        embassy_info = EMBASSY_DETAILS.get(country, DEFAULT_EMBASSY)
        
        # 기본 5일 일정
        days_plan = []
        for day_num in range(1, 6):
            day_plan = {
                "day": day_num,
                "title": f"Day {day_num}: {city_name} 탐방",
                "theme": "도시 탐방" if day_num <= 3 else "휴식 및 귀국",
                "content": f"{city_name}의 {day_num}일차 일정입니다.",
                "spots": [{"name": f"{city_name} 주요 명소", "desc": "대표 관광지", "reservation": False}],
                "restaurants": [{"name": "현지 식당", "type": "점심/저녁", "price": "$20-40"}],
                "transport": "대중교통",
                "estimated_cost": {"transport": "$20", "food": "$50", "activities": "$30", "total": "$100"},
            }
            days_plan.append(day_plan)
        
        # SEO 메타정보 생성
        seo_meta = self._generate_seo_meta(city_name, country, 5, region)
        
        return {
            "title": f"{city_name} 여행 가이드 | 5일 일정",
            "destination": {
                "name": city_name,
                "country": country,
                "nickname": city_name,
                "best_season": self._get_best_season(region),
                "currency": currency,
                "flight_time": flight_time,
                "days": 5,
                "car_rental_available": region != "유럽",
                "parking_difficulty": "보통",
            },
            "intro": f"{city_name}는 {country}의 매력적인 여행지입니다.",
            "seo": seo_meta,
            "hotels": {
                "budget": [{"name": "Budget Hotel", "rating": 4.0, "price_per_night": "$60-80", "area": "시내", "pros": "가성비", "cons": "시설 간단", "maps_url": "#"}],
                "luxury": [{"name": "Luxury Hotel", "rating": 4.7, "price_per_night": "$300-500", "area": "중심지", "pros": "최고급", "cons": "비쌈", "maps_url": "#"}],
            },
            "days_plan": days_plan,
            "parking_info": {"difficulty": "보통", "city_center_rate": "$3-5", "recommendation": "대중교통 이용", "pr_locations": [], "apps": ["Google Maps"], "tips": []},
            "transport_summary": {"metro": "$2", "taxi": "$10", "uber": "$15", "rental_car": "$50"},
            "total_estimate": {
                "budget": {"accommodation": "$280", "food": "$200", "transport": "$60", "activities": "$80", "total": "$620"},
                "luxury": {"accommodation": "$1,600", "food": "$500", "transport": "$150", "activities": "$150", "total": "$2,400"},
            },
            "brave_search_queries": [f"{city_name} travel guide"],
            "final_summary": {
                "must_reserve": [{"name": "주요 관광지", "when": "사전 확인", "url": "#"}],
                "essential_apps": ["Google Maps"],
                "emergency_contacts": emergency,
                "embassy_info": embassy_info,
                "packing_checklist": ["여권", "현금"]
            },
            "generated_at": datetime.now().isoformat(),
        }
    
    def _get_best_season(self, region: str) -> str:
        """지역별 최적 여행 시기"""
        seasons = {
            "유럽": "봄(4-5월)과 가을(9-10월)이 가장 좋아요",
            "동남아": "건기(11-2월)가 여행하기 좋아요",
            "동아시아": "봄(3-5월)과 가을(9-11월)이 적해요",
            "미주": "봄(4-6월)과 가을(9-10월)이 좋아요",
            "중동": "11월-3월이 선선하고 좋아요",
            "휴양지": "건기(11-4월)가 해변 즐기기 좋아요",
        }
        return seasons.get(region, "봄과 가을이 가장 좋아요")
    
    def _get_intro(self, city: str, country: str) -> str:
        """도시 소개 문구"""
        return f"""{city}는 {country}의 대표적인 여행지로, 독특한 매력과 맛있는 음식, 아름다운 경으로 사랑받는 곳이에요. 

이 일정은 실제 여행자들의 경험을 바탕으로 작성한 상세 가이드예요. 예약이 필요한 곳은 미리 표시해두었으니 꼭 확인하세요. 각 장소마다 이동 방법과 꿀팁도 함께 소개해드릴게요.

즐거운 여행 되세요!"""

# 인스턴스 생성
dynamic_generator = DynamicCityContentGenerator()
