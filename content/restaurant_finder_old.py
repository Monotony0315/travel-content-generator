"""Restaurant recommendations (10 picks, budget/standard/premium)."""

from __future__ import annotations

from typing import Dict, List
from loguru import logger
import urllib.parse


CITY_RESTAURANTS = {
    "Paris": {
        "budget": [
            {"name": "L'As du Fallafel", "type": "팔라펠/길거리음식", "signature": "팔라펠 샌드위치", "tip": "마레 지구에서 현지인들도 줄 서 먹는 가성비 갑"},
            {"name": "Breizh Café", "type": "갈렛/크레페", "signature": "버터 크레페", "tip": "정통 브르타뉴 크레페를 합리적인 가격에"},
            {"name": "Bouillon Chartier", "type": "브라세리", "signature": "전통 프렌치 코스", "tip": "1900년대 초창기부터 이어진 가성비 브라세리"},
        ],
        "standard": [
            {"name": "Café de Flore", "type": "카페/브런치", "signature": "크루아상/오믈렛", "tip": "생제륧망데프레의 역사적인 카페"},
            {"name": "Le Comptoir du Relais", "type": "브라세리", "signature": "카수레/덕컨핏", "tip": "몽파륜나스 지역 현지인 맛집"},
            {"name": "Le Petit Cler", "type": "비스트로", "signature": "스테이크 프리츠", "tip": "에펠탑 근처 조용한 동네 비스트로"},
            {"name": "Chez Janou", "type": "프로방스 요리", "signature": "바바 프루이/초콜릿 무스", "tip": "프로방스풍 분위기와 디저트가 일품"},
        ],
        "premium": [
            {"name": "Septime", "type": "모던 프렌치", "signature": "테이스팅 메뉴", "tip": "미슐랭 1성, 예약 필수, 인기 폭발"},
            {"name": "Le Cinq", "type": "럭셔리 다이닝", "signature": "호텔 미슐랭 3성", "tip": "포시즌스 조지 5세 호텔, 파리 정점"},
            {"name": "L'Ambroisie", "type": "클로식 프렌치", "signature": "전통 미슐랭", "tip": "보석상(Place des Vosges)의 전설적인 레스토랑"},
        ]
    },
    "Rome": {
        "budget": [
            {"name": "Da Enzo al 29", "type": "트라스테베레", "signature": "까륵소 에 페페", "tip": "트라스테베레 현지인 추천, 웨이팅 각오"},
            {"name": "Trapizzino", "type": "스트리트 푸드", "signature": "트라피치노", "tip": "피자+슈퍼머스 합체, 길거리 음식의 정석"},
            {"name": "Roscioli Salumeria", "type": "델리/샌드위치", "signature": "까르파치오/파니니", "tip": "고급 델리지만 스탠딩으로 가성비 즐기기"},
        ],
        "standard": [
            {"name": "Pizzarium Bonci", "type": "피자 알 타촐", "signature": "포테이토 포르치니 피자", "tip": "가브리엘 본치의 알 타촐 피자 전문점"},
            {"name": "Armando al Pantheon", "type": "로만 트라디셔널", "signature": "알프레도/까륵소 에 페페", "tip": "판테온 2분 거리 역사적인 가게"},
            {"name": "La Campana", "type": "로만/씨푸드", "signature": "브루스케타/카치오 에 페페", "tip": "1518년부터 영업 중인 로마에서 가장 오래된 레스토랑"},
            {"name": "Il Pagliaccio", "type": "이탤리안 모던", "signature": "테이스팅 메뉴", "tip": "트라스테베레 감성 모던 이탤리안"},
        ],
        "premium": [
            {"name": "La Pergola", "type": "미슐랭 3성", "signature": "럭셔리 이탤리안", "tip": "카포디몬테 호텔, 로마 미슐랭 3성 유일"},
            {"name": "Flavio al Velavevodetto", "type": "로만/트라디셔널", "signature": "아마트리치아나/까초 에 페페", "tip": "테스타치오 언덕, 현지인이 추천하는 프리미엄"},
            {"name": "Roscioli Ristorante", "type": "고급 델리 레스토랑", "signature": "까르파치오/푸아그라 라비올리", "tip": "고급 재료, 와인 페어링 추천"},
        ]
    },
    "Tokyo": {
        "budget": [
            {"name": "Ichiran Ramen", "type": "라멘", "signature": "돈코츠 라멘", "tip": "혼밥 가능, 24시간, 시부야/신주쿠 어디서나"},
            {"name": "Sukiya/Matsuya", "type": "규동 체인", "signature": "규동/마늘버터 규동", "tip": "24시간, 500엔대부터, 품질 일정"},
            {"name": "Omoide Yokocho", "type": "야키토리 골목", "signature": "꼬치/야키토리", "tip": "신주쿠 서쪽, 정통 이자카야 거리"},
        ],
        "standard": [
            {"name": "Kyubey", "type": "스시", "signature": "오마카세", "tip": "긴자 본점, 미슐랭 스타, 예약 권장"},
            {"name": "Gonpachi Nishi-Azabu", "type": "이자카야/킬빌", "signature": "소바/꼬치", "tip": "영화 킬빌 촬영지, 분위기 좋은 이자카야"},
            {"name": "Afuri", "type": "유즈 라멘", "signature": "유즈 시오 라멘", "tip": "깔끔한 유즈 국물, 하라주쿠/시부야"},
            {"name": "Tsukiji Outer Market", "type": "시장 음식", "signature": "카이센동/타마고야키", "tip": "츠키지 장외시장, 아침~오전이 대전제"},
        ],
        "premium": [
            {"name": "Sushi Saito", "type": "스시", "signature": "오마카세", "tip": "미슐랭 3성, 도쿄 스시 정점, 예약 극악"},
            {"name": "Narisawa", "type": "모던 재패니즈", "signature": "이노베이티브", "tip": "미슐랭 2성, 지속가능성 테마, 나마리사와"},
            {"name": "Ishikawa", "type": "가이세키", "signature": "전통 가이세키", "tip": "미슐랭 3성, 고간야마, 예약 필수"},
        ]
    },
    "Barcelona": {
        "budget": [
            {"name": "La Boqueria Market", "type": "시장", "signature": "엘 퀴미 데 라 보케리아", "tip": "쥬스/해산물/이비리코 햄, 라 람블라"},
            {"name": "Churrería Laietana", "type": "츄러스", "signature": "츄러스 콘 초콜라테", "tip": "아침 츄러스, 현지인들이 줄 서는 곳"},
            {"name": "Bar Cañete", "type": "탑스 바", "signature": "파타타 브라바스/안초비", "tip": "고딕 지구, 전통 탑스, 가성비 좋음"},
        ],
        "standard": [
            {"name": "Tickets Bar", "type": "어번 탑스", "signature": "창의적 핀초스", "tip": "에드리아 형제, 미슐랭 1성, 예약 필수"},
            {"name": "Bar Mut", "type": "모던 스페니쉬", "signature": "해산물/리소토", "tip": "에샴플 지역, 현지 셰프들도 자주 오는 곳"},
            {"name": "7 Portes", "type": "파에야", "signature": "파에야/피데이아", "tip": "1836년 시작, 바르셀로나 역사상 파에야"},
            {"name": "Cervecería Catalana", "type": "탑스/핀초스", "signature": "브라바스/감바스", "tip": "현지인 인기 핫플, 에샴플"},
        ],
        "premium": [
            {"name": "Disfrutar", "type": "모던 스페니쉬", "signature": "테이스팅 메뉴", "tip": "미슐랭 2성, 엘 불리 정신 계승, 예약 필수"},
            {"name": "Lasarte", "type": "미슐랭 3성", "signature": "럭셔리 바스크", "tip": "몬주익 호텔, 바르셀로나 유일 미슐랭 3성"},
            {"name": "ABaC", "type": "아방가르드", "signature": "테크니컬 디너", "tip": "미슐랭 3성, 조르디 크루즈, 예약 극악"},
        ]
    },
    "Sydney": {
        "budget": [
            {"name": "Harry's Café de Wheels", "type": "파이/길거리", "signature": "타이거 파이", "tip": "울루물루 항구, 1945년부터, 시드니 아이콘"},
            {"name": "Chat Thai", "type": "타이", "signature": "파타이/얌꿍", "tip": "현지인 인기 체인, 다양한 지점"},
            {"name": "Mamak", "type": "말레이시안", "signature": "로티 캐나이", "tip": "치나타운, 합리적 가격에 강렬한 맛"},
        ],
        "standard": [
            {"name": "Quay", "type": "모던 오스트레일리안", "signature": "하버 뷰 디너", "tip": "오페라하우스 뷰, 미슐랭 스타, 예약 필수"},
            {"name": "Bennelong", "type": "파인 다이닝", "signature": "오페라하우스 내", "tip": "시드니 오페라하우스, 시그니처 럭셔리"},
            {"name": "Icebergs Dining Room", "type": "이탤리안/뷰", "signature": "본다이 비치 뷰", "tip": "본다이 비치 정면, 인스타 감성 최고"},
            {"name": "Tetsuya's", "type": "프렌치 재패니즈", "signature": "컨템퍼러리", "tip": "호주 미슐랭 레전드, 예약 필수"},
        ],
        "premium": [
            {"name": "Restaurant Hubert", "type": "프렌치", "signature": "클래식 프렌치", "tip": "다운타운 지하, 분위기와 퀄리티 모두"},
            {"name": "Rockpool Bar & Grill", "type": "스테이크하우스", "signature": "웨그휴 스테이크", "tip": "호주산 프리미엄 소고기 전문"},
            {"name": "Momofuku Seiobo", "type": "모던", "signature": "데이비드 창 컨셉", "tip": "더 스타, 모모푸쿠, 창의적 메뉴"},
        ]
    },
    "New York": {
        "budget": [
            {"name": "Joe's Pizza", "type": "피자", "signature": "치즈 슬라이스", "tip": "그리니치 빌리지, $3 슬라이스, 영화 촬영지"},
            {"name": "Shake Shack", "type": "버거", "signature": "쉑버거/쉑스택", "tip": "매디슨 스퀘어 파크 본점, 현지 버거 체인"},
            {"name": "Katz's Delicatessen", "type": "델리", "signature": "패스트라미 샌드위치", "tip": "로어 이스트 사이드, 1888년부터, 유명"},
        ],
        "standard": [
            {"name": "Peter Luger Steak House", "type": "스테이크", "signature": "포터하우스", "tip": "브루클린, 미국 최고 스테이크하우스 중 하나"},
            {"name": "Le Bernardin", "type": "씨푸드", "signature": "미슐랭 3성 씨푸드", "tip": "에릭 리퍼트, 뉴욕 씨푸드 정점"},
            {"name": "Gramercy Tavern", "type": "아메리칸", "signature": "뉴 아메리칸", "tip": "그래머시 파크, 미슐랭 스타, 예약 권장"},
            {"name": "Momofuku Noodle Bar", "type": "아시안 퓨전", "signature": "라멘/포크번", "tip": "데이비드 창, 이스트 빌리지, 창의적"},
        ],
        "premium": [
            {"name": "Eleven Madison Park", "type": "플랜트베이스드", "signature": "미슐랭 3성", "tip": "완전 채식, 뉴욕 다이닝 정점"},
            {"name": "Per Se", "type": "프렌치", "signature": "토마스 켈러", "tip": "타임워너 센터, 미슐랭 3성, 럭셔리"},
            {"name": "Chef's Table at Brooklyn Fare", "type": "오마카세", "signature": "미슐랭 3성", "tip": "브루클린, 18석, 프라이빗 경험"},
        ]
    },
    "London": {
        "budget": [
            {"name": "Borough Market", "type": "마켓", "signature": "스리트 푸드", "tip": "런던 최고 푸드 마켓, 토-일 필수"},
            {"name": "Dishoom", "type": "인디언", "signature": "커리/나안", "tip": "봄베이 스타일, 코번트 가든/킹스크로스"},
            {"name": "Poppies Fish & Chips", "type": "피시앤칩스", "signature": "피시앤칩스", "tip": "스피탈필즈, 1950년대 복고풍, 가성비"},
        ],
        "standard": [
            {"name": "Duck & Waffle", "type": "브런치", "signature": "덕앤와플", "tip": "해러드 타워 40층, 24시간, 런던 뷰"},
            {"name": "The Ledbury", "type": "모던 유러피안", "signature": "미슐랭 2성", "tip": "노팅힐, 베이컨, 예약 필수"},
            {"name": "Padella", "type": "파스타", "signature": "카초 에 페페/라비올리", "tip": "버로우 마켓, 줄 서는 건 당연, 가성비"},
            {"name": "Gymkhana", "type": "인디언", "signature": "타도리/커리", "tip": "미슐랭 1성, 메이페어, 북인도 요리"},
        ],
        "premium": [
            {"name": "Restaurant Gordon Ramsay", "type": "프렌치", "signature": "미슐랭 3성", "tip": "체헐시, 고든 램지 본점"},
            {"name": "The Fat Duck", "type": "모던", "signature": "헤스턴 블루멘탈", "tip": "윈저 근교, 미슐랭 3성, 실험적"},
            {"name": "Sketch (The Lecture Room)", "type": "모던", "signature": "미슐랭 2성", "tip": "메이페어, 아트+다이닝, 인테리어 유명"},
        ]
    },
    "Bangkok": {
        "budget": [
            {"name": "Thip Samai", "type": "팟타이", "signature": "팟타이 쿵", "tip": "오리지널 팟타이, 바나나잎 포장, 대왕궁 근처"},
            {"name": "Jay Fai", "type": "씨푸드", "signature": "드라이 라끼", "tip": "미슐랭 스트리트 푸드, 웨이팅 길음, 예약 추천"},
            {"name": "Khao Gaeng Jake Puey", "type": "카레라이스", "signature": "카레라이스", "tip": "짜뚜짝 시장, 다양한 토핑, 현지인 추천"},
        ],
        "standard": [
            {"name": "Gaggan Anand", "type": "프로그레시브 인디언", "signature": "오마카세", "tip": "미슐랭 2성, 25코스 이모지 메뉴, 예약 필수"},
            {"name": "Le Du", "type": "타이 모던", "signature": "타이 테이스팅", "tip": "미슐랭 1성, 태국 와인 페어링"},
            {"name": "Sra Bua by Kiin Kiin", "type": "타이 모던", "signature": "컨템퍼러리 타이", "tip": "시암 켐핀스키, 분자요리 접목"},
            {"name": "Supanniga Eating Room", "type": "타이 홈쿠킹", "signature": "동북부 타이", "tip": "톤손, 할머니 레시피, 현지 분위기"},
        ],
        "premium": [
            {"name": "Sühring", "type": "저먼 모던", "signature": "쌍둥이 셰프", "tip": "미슐랭 2성, 독일식 파인다이닝"},
            {"name": "Mezzaluna", "type": "프렌치", "signature": "르 부아 스테이트 타워", "tip": "64층 뷰, 클래식 프렌치, 예약 필수"},
            {"name": "Ginza Sushi Ichi", "type": "스시", "signature": "오마카세", "tip": "은카로스 방콕, 도쿄 본점, 프리미엄"},
        ]
    },
    "Singapore": {
        "budget": [
            {"name": "Maxwell Food Centre", "type": "호커센터", "signature": "칠리크랩/차이나타운", "tip": "티안 톈 훗(칠리크랩), 경제적, 늘 붐빔"},
            {"name": "Lau Pa Sat", "type": "호커센터", "signature": "사테 스트리트", "tip": "금융가 중심, 저녁 사테 거리 유명"},
            {"name": "Tian Tian Hainanese Chicken Rice", "type": "치킨라이스", "signature": "하이난 치킨라이스", "tip": "맥스웸 센터, 고든 램지도 인정한 맛"},
        ],
        "standard": [
            {"name": "Odette", "type": "모던 프렌치", "signature": "미슐랭 3성", "tip": "내셔널 갤러리, 줄리안 로이어, 예약 필수"},
            {"name": "Burnt Ends", "type": "스모크/그릴", "signature": "BBQ 테이스팅", "tip": "미슐랭 1성, 옹바루, 불맛 요리"},
            {"name": "Jumbo Seafood", "type": "씨푸드", "signature": "칠리크랩", "tip": "싱가포르 대표, 이스트 코스트/리버사이드"},
            {"name": "Liao Fan Hawker Chan", "type": "쏘셜 미슐랭", "signature": "쏘야 치킨라이스", "tip": "세계에서 가장 저렴한 미슐랭, 차이나타운"},
        ],
        "premium": [
            {"name": "Les Amis", "type": "클래식 프렌치", "signature": "미슐랭 3성", "tip": "식스티언 샹젤리제, 싱가포르 프렌치 정점"},
            {"name": "Waku Ghin", "type": "재패니즈", "signature": "테츠야 와쿠다", "tip": "마리나베이 샌즈, 미슐랭 2성, 오마카세"},
            {"name": "Corner House", "type": "가스트로노미", "signature": "보태니컬", "tip": "싱가포르 보태닉 가든, 미슐랭 1성"},
        ]
    },
    "Vancouver": {
        "budget": [
            {"name": "Granville Island Public Market", "type": "푸드마켓", "signature": "다양한 부스", "tip": "현지 농산물/푸드, 아침~오후, 강변 뷰"},
            {"name": "Peaceful Restaurant", "type": "중식", "signature": "누들/손빈 만두", "tip": "리치몬드/브로드웨이, 대륙식 중식, 가성비"},
            {"name": "Japadog", "type": "핫도그", "signature": "일본식 핫도그", "tip": "거리 푸드, 시내 곳곳, 현지 인기"},
        ],
        "standard": [
            {"name": "Miku", "type": "아바스시 스시", "signature": "플레임 토러드", "tip": "워터프론트, 밴쿠버 스시 대표"},
            {"name": "Bao Bei", "type": "차이니즈", "signature": "모던 차이나타운", "tip": "칭파오, 샹하이/광둥 퓨전"},
            {"name": "Cioppino's", "type": "이탤리안/씨푸드", "signature": "차피노", "tip": "예일타운, 20년+ 전통, 로컬 인기"},
            {"name": "Nightingale", "type": "브리티시 컬리너리", "signature": "데이비드 호크워스", "tip": "데이비드 호크워스, 현대적"},
        ],
        "premium": [
            {"name": "Hawksworth Restaurant", "type": "컨템퍼러리", "signature": "캐나다 재료", "tip": "로즈우드 호텔, 컨템퍼러리 캐나다"},
            {"name": "Boulevard Kitchen & Oyster Bar", "type": "씨푸드", "signature": "오이스터바", "tip": "서튼 플레이스, 신선한 해산물"},
            {"name": "Tojo's Restaurant", "type": "재패니즈", "signature": "롤/오마카세", "tip": "시청 근처, 캘리포니아 롤 발상지"},
        ]
    }
}


class RestaurantFinder:
    async def find(self, city: str, country: str, cuisine: str = "local") -> Dict:
        logger.info(f"Finding restaurants in {city}...")

        city_data = CITY_RESTAURANTS.get(city, {
            "budget": [
                {"name": f"{city} Street Market", "type": "마켓", "signature": "로컬 길거리 음식", "tip": "현지인들이 많이 찾는 저렴한 맛집"},
                {"name": f"{city} Local Eats", "type": "로컬 푸드", "signature": "현지인 맛집", "tip": "가성비 좋은 현지식"},
                {"name": f"{city} Food Stall", "type": "길거리", "signature": "스트리트 푸드", "tip": "빠르고 저렴하게 한 끼"},
            ],
            "standard": [
                {"name": f"{city} Bistro", "type": "비스트로", "signature": "현지식 정식", "tip": "분위기 좋은 중급 레스토랑"},
                {"name": f"{city} Kitchen", "type": "레스토랑", "signature": "시그니처 메뉴", "tip": "현지인도 추천하는 맛집"},
                {"name": f"{city} Grill", "type": "그릴/BBQ", "signature": "그릴 요리", "tip": "고기 요리가 일품"},
                {"name": f"{city} Cafe", "type": "브런치", "signature": "브런치/카페", "tip": "아침 식사하기 좋은 곳"},
            ],
            "premium": [
                {"name": f"{city} Fine Dining", "type": "파인다이닝", "signature": "테이스팅 코스", "tip": "스페셜한 날을 위한 선택"},
                {"name": f"{city} Signature", "type": "시그니처", "signature": "셰프 특선", "tip": "셰프 추천 메뉴로 즐기기"},
                {"name": f"{city} Luxury", "type": "럭셔리", "signature": "프리미엄", "tip": "고급스러운 분위기와 서비스"},
            ]
        })

        picks = []
        for grade in ["budget", "standard", "premium"]:
            for r in city_data.get(grade, []):
                q = urllib.parse.quote(f"{r['name']} {city}")
                maps = f"https://www.google.com/maps/search/?api=1&query={q}"
                parking_q = urllib.parse.quote(f"{r['name']} {city} parking")
                parking = f"https://www.google.com/maps/search/?api=1&query={parking_q}"
                price = "₩" if grade == "budget" else ("₩₩" if grade == "standard" else "₩₩₩")
                picks.append(
                    {
                        "grade": grade,
                        "name": r['name'],
                        "type": r['type'],
                        "signature": r['signature'],
                        "price": price,
                        "description": r['tip'],
                        "google_maps": maps,
                        "parking": {
                            "guide": "주변 공영/민영 주차장 우선 확인 추천",
                            "google_maps": parking,
                        },
                    }
                )

        return {
            "total": len(picks),
            "budget": [x for x in picks if x["grade"] == "budget"],
            "standard": [x for x in picks if x["grade"] == "standard"],
            "premium": [x for x in picks if x["grade"] == "premium"],
            "all": picks,
        }
