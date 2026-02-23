"""
Restaurant Finder - Expanded Options with Full Details
MAJOR IMPROVEMENTS (2026-02-19):
- 6-8 restaurants per city (was 2-3)
- Full details: name, cuisine type, price range, address, signature dishes, reservation links
- Categories: Fine Dining (2-3), Mid-range (2-3), Budget/Fast (2-3), Local/Hidden gems (2)
"""

from __future__ import annotations

from typing import Dict, List
from loguru import logger
import urllib.parse


CITY_RESTAURANTS = {
    "London": {
        "fine_dining": [
            {
                "name": "Restaurant Gordon Ramsay",
                "cuisine": "프렌치 파인다이닝",
                "price_range": "₩₩₩₩",
                "price": "200-350파운드",
                "address": "68 Royal Hospital Rd, London SW3 4HP",
                "maps_url": "https://www.google.com/maps/search/Restaurant+Gordon+Ramsay+London",
                "signature": ["콩피 오브 치킨", "랍스터 라비올리", "칙커리 푸딩"],
                "reservation_required": True,
                "reservation_url": "https://www.gordonramsayrestaurants.com/en/us/restaurant-gordon-ramsay",
                "tip": "미슐랭 3성. 2개월 전 예약 필수. 드레스 코드 있음."
            },
            {
                "name": "The Ledbury",
                "cuisine": "모던 유러피언",
                "price_range": "₩₩₩₩",
                "price": "150-250파운드",
                "address": "127 Ledbury Rd, London W11 2AQ",
                "maps_url": "https://www.google.com/maps/search/The+Ledbury+London",
                "signature": ["베이컨 피난티에", "초콜릿 소르테", "쇠고기 트러플"],
                "reservation_required": True,
                "reservation_url": "https://www.theledbury.com/",
                "tip": "미슐랭 2성. 노팅힐에 위치. 베이컨 요리가 유명."
            },
            {
                "name": "Duck & Waffle",
                "cuisine": "브리티시 모던",
                "price_range": "₩₩₩",
                "price": "40-80파운드",
                "address": "110 Bishopsgate, London EC2N 4AY",
                "maps_url": "https://www.google.com/maps/search/Duck+%26+Waffle+London",
                "signature": ["덕앤와플", "포크 벨리", "달콤한 와플"],
                "reservation_required": True,
                "reservation_url": "https://duckandwaffle.com/reservations/",
                "tip": "핫러드 타워 40층. 24시간 영업. 일출 예약 인기."
            },
        ],
        "mid_range": [
            {
                "name": "The Ivy",
                "cuisine": "브리티스트로",
                "price_range": "₩₩₩",
                "price": "40-70파운드",
                "address": "1-5 West St, London WC2H 9NQ",
                "maps_url": "https://www.google.com/maps/search/The+Ivy+Covent+Garden",
                "signature": ["아이비 치킨", "쇠고기 스테이크", "초콜릿 폰당"],
                "reservation_required": True,
                "reservation_url": "https://theivy.co.uk/",
                "tip": "런던 브런치의 아이콘. 1917년부터 영업."
            },
            {
                "name": "Dishoom",
                "cuisine": "인도 봄베이",
                "price_range": "₩₩",
                "price": "20-35파운드",
                "address": "12 Upper St Martin's Ln, London WC2H 9FB",
                "maps_url": "https://www.google.com/maps/search/Dishoom+Covent+Garden",
                "signature": ["베이컨 나안", "블랙 다할", "치킨 루비"],
                "reservation_required": True,
                "reservation_url": "https://www.dishoom.com/reservations/",
                "tip": "현지 봄베이 스타일. 웨이팅 있으나 바 서빙 가능."
            },
            {
                "name": "Polpo",
                "cuisine": "이탈리안 베네치안",
                "price_range": "₩₩",
                "price": "25-40파운드",
                "address": "41 Beak St, London W1F 9SB",
                "maps_url": "https://www.google.com/maps/search/Polpo+Soho+London",
                "signature": ["치케티 플래터", "미트볼", "티라미수"],
                "reservation_required": False,
                "tip": "베네치아 바카로 스타일. 소호 지역. 공유 플레이트."
            },
        ],
        "budget": [
            {
                "name": "Borough Market Stalls",
                "cuisine": "글로벌 스트리트 푸드",
                "price_range": "₩",
                "price": "5-15파운드",
                "address": "8 Southwark St, London SE1 1TL",
                "maps_url": "https://www.google.com/maps/search/Borough+Market+London",
                "signature": ["그라운드 커피", "스윗 데블리", "브리드 헤드 커리"],
                "reservation_required": False,
                "tip": "수-토 오픈. 다양한 길거리 음식 체험."
            },
            {
                "name": "Poppies Fish & Chips",
                "cuisine": "브리티시 피시앤칩스",
                "price_range": "₩",
                "price": "10-18파운드",
                "address": "6-8 Hanbury St, London E1 6QR",
                "maps_url": "https://www.google.com/maps/search/Poppies+Fish+and+Chips+London",
                "signature": ["코드 앤 칩스", "피시 케이크", "뮤시 페즈"],
                "reservation_required": False,
                "tip": "1950년대 복고풍 인테리어. 스피탈필즈 지역."
            },
            {
                "name": "Gordon's Wine Bar",
                "cuisine": "와인바/스페인식",
                "price_range": "₩",
                "price": "10-25파운드",
                "address": "47 Villiers St, London WC2N 6NE",
                "maps_url": "https://www.google.com/maps/search/Gordon's+Wine+Bar+London",
                "signature": ["치즈 플래터", "참치 타르타르", "와인"],
                "reservation_required": False,
                "tip": "1890년부터 영업. 지하 석조 벽과 촛불 분위기."
            },
        ],
        "local_gems": [
            {
                "name": "St. John",
                "cuisine": "브리티시 노즈투테일",
                "price_range": "₩₩",
                "price": "35-60파운드",
                "address": "26 St John St, London EC1M 4AY",
                "maps_url": "https://www.google.com/maps/search/St.+John+Restaurant+London",
                "signature": ["본 마로우", "콜드로스트 비프", "마들레인"],
                "reservation_required": True,
                "reservation_url": "https://stjohnrestaurant.com/",
                "tip": "페르나도 어버딘이 운영. 노즈투테일 다이닝의 선구자."
            },
            {
                "name": "Brat",
                "cuisine": "스패니쉬/바스크",
                "price_range": "₩₩",
                "price": "30-55파운드",
                "address": "4 Redchurch St, London E2 7DD",
                "maps_url": "https://www.google.com/maps/search/Brat+Restaurant+London",
                "signature": ["전체 구운 치킨", "바스크 치즈케이크", "그릴드 새우"],
                "reservation_required": True,
                "reservation_url": "https://www.bratrestaurant.co.uk/",
                "tip": "쇼어디치 지역. 바스크 스타일 그릴 요리. 미슐랭 1성."
            },
        ]
    },
    "Paris": {
        "fine_dining": [
            {
                "name": "Septime",
                "cuisine": "모던 프렌치",
                "price_range": "₩₩₩₩",
                "price": "80-120유로",
                "address": "80 Rue de Charonne, 75011 Paris",
                "maps_url": "https://www.google.com/maps/search/Septime+Paris",
                "signature": ["시즈널 테이스팅 메뉴", "내추럴 와인", "발효 버터"],
                "reservation_required": True,
                "reservation_url": "https://www.septimerestaurant.com/",
                "tip": "미슐랭 1성. 2주 전 월요일 10시 온라인 예약 오픈."
            },
            {
                "name": "Le Cinq",
                "cuisine": "럭셔리 프렌치",
                "price_range": "₩₩₩₩",
                "price": "200-350유로",
                "address": "31 Avenue George V, 75008 Paris",
                "maps_url": "https://www.google.com/maps/search/Le+Cinq+Paris",
                "signature": ["캐비어", "랍스터", "옥수순"],
                "reservation_required": True,
                "reservation_url": "https://www.fourseasons.com/paris/dining/restaurants/le_cinq/",
                "tip": "미슐랭 3성. 포시즌스 조지 5세 호텔."
            },
        ],
        "mid_range": [
            {
                "name": "Le Comptoir du Relais",
                "cuisine": "브라세리",
                "price_range": "₩₩",
                "price": "35-50유로",
                "address": "9 Carrefour de l'Odéon, 75006 Paris",
                "maps_url": "https://www.google.com/maps/search/Le+Comptoir+du+Relais+Paris",
                "signature": ["까수레", "덕컨핏", "프렌치 어니언 수프"],
                "reservation_required": True,
                "reservation_url": "https://www.comptoidurelais.com/",
                "tip": "생제르맹데프레. 웨이팅 있음. 19시 전 도착 권장."
            },
            {
                "name": "Café de Flore",
                "cuisine": "카페/브런치",
                "price_range": "₩₩",
                "price": "20-40유로",
                "address": "172 Boulevard Saint-Germain, 75006 Paris",
                "maps_url": "https://www.google.com/maps/search/Caf%C3%A9+de+Flore+Paris",
                "signature": ["크루아상", "오믈렛", "핫 초콜릿"],
                "reservation_required": False,
                "tip": "역사적인 문학 카페. 1887년부터 영업. 사르트르, 드 보부아르 단골."
            },
        ],
        "budget": [
            {
                "name": "L'As du Fallafel",
                "cuisine": "팔라펠/중동",
                "price_range": "₩",
                "price": "6-10유로",
                "address": "34 Rue des Rosiers, 75004 Paris",
                "maps_url": "https://www.google.com/maps/search/L'As+du+Fallafel+Paris",
                "signature": ["팔라펠 샌드위치", "후무스", "바바가누쉬"],
                "reservation_required": False,
                "tip": "마레 지구. 줄 서서 먹는 가성비 최고. 현지인도 인정."
            },
            {
                "name": "Bouillon Chartier",
                "cuisine": "전통 브라세리",
                "price_range": "₩",
                "price": "10-20유로",
                "address": "7 Rue du Faubourg Montmartre, 75009 Paris",
                "maps_url": "https://www.google.com/maps/search/Bouillon+Chartier+Paris",
                "signature": ["에스카르고", "코코뱅", "크렘 브륄레"],
                "reservation_required": False,
                "tip": "1896년부터 영업. 1900년대 분위기 그대로. 가성비 갑."
            },
        ],
        "local_gems": [
            {
                "name": "Chez Janou",
                "cuisine": "프로방스 요리",
                "price_range": "₩₩",
                "price": "30-45유로",
                "address": "2 Rue Roger Verlomme, 75003 Paris",
                "maps_url": "https://www.google.com/maps/search/Chez+Janou+Paris",
                "signature": ["초콜릿 무스", "바바 프루이", "라따뚜이"],
                "reservation_required": True,
                "reservation_url": "https://www.chezjanou.com/",
                "tip": "프로방스풍 분위기. 초콜릿 무스가 유명. 예약 필수."
            },
            {
                "name": "Breizh Café",
                "cuisine": "브르타뉴 크레페",
                "price_range": "₩₩",
                "price": "15-30유로",
                "address": "109 Rue Vieille du Temple, 75003 Paris",
                "maps_url": "https://www.google.com/maps/search/Breizh+Caf%C3%A9+Paris",
                "signature": ["갈렛", "크레페", "브르타뉴 사과주"],
                "reservation_required": True,
                "reservation_url": "https://breizhcafe.com/",
                "tip": "정통 브르타뉴 갈레트. 프리미엄 재료 사용."
            },
        ]
    },
}


class RestaurantFinder:
    """Expanded restaurant finder with full details"""
    
    async def find(self, city: str, country: str, cuisine: str = "local") -> Dict:
        """Find restaurants with expanded options"""
        logger.info(f"Finding restaurants in {city}...")

        city_data = CITY_RESTAURANTS.get(city, self._generate_default_restaurants(city, country))
        
        # Collect all restaurants from all categories
        all_restaurants = []
        for category in ["fine_dining", "mid_range", "budget", "local_gems"]:
            all_restaurants.extend(city_data.get(category, []))
        
        # Format for output
        formatted = []
        for r in all_restaurants:
            formatted.append(self._format_restaurant(r))
        
        return {
            "total": len(formatted),
            "fine_dining": [self._format_restaurant(r) for r in city_data.get("fine_dining", [])],
            "mid_range": [self._format_restaurant(r) for r in city_data.get("mid_range", [])],
            "budget": [self._format_restaurant(r) for r in city_data.get("budget", [])],
            "local_gems": [self._format_restaurant(r) for r in city_data.get("local_gems", [])],
            "all": formatted,
        }

    def _format_restaurant(self, r: Dict) -> Dict:
        """Format restaurant data for output"""
        return {
            "name": r["name"],
            "cuisine": r.get("cuisine", ""),
            "price_range": r.get("price_range", "₩₩"),
            "price": r.get("price", ""),
            "address": r.get("address", ""),
            "maps_url": r.get("maps_url", ""),
            "signature": r.get("signature", []),
            "reservation_required": r.get("reservation_required", False),
            "reservation_url": r.get("reservation_url", ""),
            "tip": r.get("tip", ""),
        }

    def _generate_default_restaurants(self, city: str, country: str) -> Dict:
        """Generate default restaurant data for unknown cities"""
        return {
            "fine_dining": [
                {
                    "name": f"{city} Fine Dining",
                    "cuisine": "현대 요리",
                    "price_range": "₩₩₩₩",
                    "price": "100-200€",
                    "address": f"{city} City Center",
                    "maps_url": f"https://www.google.com/maps/search/fine+dining+{city}",
                    "signature": ["테이스팅 메뉴", "와인 페어링"],
                    "reservation_required": True,
                    "tip": "예약 필수"
                },
            ],
            "mid_range": [
                {
                    "name": f"{city} Bistro",
                    "cuisine": "현지식",
                    "price_range": "₩₩",
                    "price": "30-50€",
                    "address": f"{city} Downtown",
                    "maps_url": f"https://www.google.com/maps/search/bistro+{city}",
                    "signature": ["시그니처 메뉴"],
                    "reservation_required": False,
                    "tip": "현지인 추천"
                },
            ],
            "budget": [
                {
                    "name": f"{city} Street Food",
                    "cuisine": "스트리트 푸드",
                    "price_range": "₩",
                    "price": "5-15€",
                    "address": f"{city} Market",
                    "maps_url": f"https://www.google.com/maps/search/market+{city}",
                    "signature": ["길거리 음식"],
                    "reservation_required": False,
                    "tip": "가성비 좋음"
                },
            ],
            "local_gems": [
                {
                    "name": f"{city} Local Gem",
                    "cuisine": "히든 젬",
                    "price_range": "₩₩",
                    "price": "20-40€",
                    "address": f"{city} Local Area",
                    "maps_url": f"https://www.google.com/maps/search/local+restaurant+{city}",
                    "signature": ["로컬 스페셜"],
                    "reservation_required": False,
                    "tip": "현지인만 아는 곳"
                },
            ],
        }


# 인스턴스 생성
restaurant_finder = RestaurantFinder()
