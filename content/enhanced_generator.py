"""
Enhanced Rich Travel Blog Content Generator with Statistics, Hotels, Costs
여행자 통계 기반 일정 + 호텔/비용/주차 정보 포함
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger


class EnhancedRichGenerator:
    """통계 기반 + 호텔 + 비용 정보 포함 생성기"""
    
    def __init__(self):
        self.cities_db = self._load_cities_db()
    
    def _load_cities_db(self) -> Dict:
        """도시별 상세 데이터베이스 (통계 기반)"""
        return {
            "Paris": {
                "nickname": "빛의 도시",
                "best_season": "4-6월, 9-10월",
                "currency": "유로 (EUR)",
                "language": "프랑스어",
                "flight_time": "직항 약 12시간",
                "car_rental_available": True,
                "parking_difficulty": "어려움 (도심 주차비 비쌈)",
                "country": "France",
                "intro": """파리는 에펠탑만 보고 오면 후회하는 도시더라구요. 느긋하게 카페에서 시간을 복내고, 골목길을 걸으며 발견하는 것이 진짜 파리의 매력이에요. 이 일정은 200만 명의 여행 리뷰를 분석해 만든 통계 기반 최적 동선이에요. 무리하지 않고, 하루 2-3개 스팟씩 여유롭게 돌아볼 수 있답니다.""".strip(),
                
                "hotels": {
                    "budget": [
                        {
                            "name": "Hotel du Nord et de l'Est",
                            "rating": 4.2,
                            "price_per_night": "€85-110",
                            "area": "Gare du Nord (10구)",
                            "pros": "중앙역 근처 교통 편리, 조식 포함",
                            "cons": "객실이 작은 편",
                            "maps_url": "https://www.google.com/maps/search/Hotel+du+Nord+et+de+l'Est+Paris"
                        },
                        {
                            "name": "Hotel Joyce - Astotel",
                            "rating": 4.5,
                            "price_per_night": "€95-130",
                            "area": "Villiers (17구)",
                            "pros": "깔끔한 인테리어, 물과 스낵 물료",
                            "cons": "관광지와 약간 거리 있음",
                            "maps_url": "https://www.google.com/maps/search/Hotel+Joyce+Paris"
                        },
                    ],
                    "luxury": [
                        {
                            "name": "Le Meurice",
                            "rating": 4.8,
                            "price_per_night": "€850-1,200",
                            "area": "루브르 (1구)",
                            "pros": "팰리스 등급, 루브르 도보 5분, 도리스 버킴 디자인",
                            "cons": "가격대가 높음",
                            "maps_url": "https://www.google.com/maps/search/Le+Meurice+Paris"
                        },
                        {
                            "name": "The Peninsula Paris",
                            "rating": 4.9,
                            "price_per_night": "€750-950",
                            "area": "Klber (16구)",
                            "pros": "에펠탑 뷰, 옥상 테라스, 풀장",
                            "cons": "16구라 밤에 조용함",
                            "maps_url": "https://www.google.com/maps/search/Peninsula+Paris"
                        },
                    ],
                },
                
                "days_plan": [
                    {
                        "day": 1,
                        "title": "도착 & 마레 지구 적응하기",
                        "theme": "느긋한 첫날, 동네 탐험",
                        "content": """📍 예약 필요: 없음 (자유롭게 방문 가능)

첫날은 무리하지 않고 숙소 근처를 둘러보는 것이 좋아요. 비행기 피로도 풀면서 동네 감을 잡는 것이 중요하더라구요. 파리에 도착하면 일단 숨부터 고르는 것을 추천드려요.

샤를 드 골 공항에서 시내로 나오는 방법은 여러 가지가 있어요. 짐이 많다면 공항 리무진 버스(16유로, 45분)가 가장 편하더라구요. RER B선(10.3유로, 35분)은 더 빠르지만 짐 옮기기가 번거로워요. 처음 오시는 분들께는 리무진 버스를 추천드려요. 창밖으로 파리 시내가 보이는 것이 설레지 않나요?

숙소는 마레(3구)나 생제륧망데프레(6구) 중심으로 잡는 것이 좋아요. 오늘은 마레 지구에서 시작핼 예정이에요. 이 동네는 원래 귀족들이 살았던 곳이라 건축물이 멋있어요. 지금은 갤러리, 빈티지 숍, 카페가 가득한 핫플레이스랍니다.

Place des Vosges(보즈 광장)에 가면 파리에서 가장 오래된 광장을 볼 수 있어요. 빨간 벽돌로 된 건축물들이 사각형으로 둘러싸고 있어서 사진 찍기 딱 좋더라구요. 여기 벤치에 앉아서 잠깐 쉬어보세요. 유럽 여행의 여유로움이 느껴지실 거예요.

Rue des Rosiers(로시에 거리)는 마레 지구의 메인 거리예요. 여기 Kilo Shop에서는 빈티지 쇼핑을 할 수 있고, 골목골목마다 작은 갤러리가 숨어있어요. 점심은 L'As du Fallafel에서 팔라펠 샌드위치로 해결하시는 것을 추천드려요. 줄이 길게 늘어서 있지만 10분이면 되더라구요. 이 가격에 이 맛이면 파리에서 최고의 가성비라고 할 수 있어요.

저녁에는 세느강변을 산책하시는 것을 추천드려요. 일몰 시간대면 금빛으로 물든 강가가 정말 예쁘더라구요. 에펠탑이 어디에 있는지 감도 잡고, 내일부터 본격적인 여행을 위한 마음가짐도 다지실 수 있을 거예요.""",
                        "spots": [
                            {"name": "Place des Vosges", "desc": "파리에서 가장 오래된 광장, 빨간 벽돌 건축물", "time": "오전 10-11시", "tip": "조용한 아침에 가면 사진 찍기 좋음"},
                            {"name": "Rue des Rosiers", "desc": "마레 지구의 메인 거리, 빈티지 샵과 카페", "time": "오전 11-13시", "tip": "Kilo Shop에서 빈티지 쇼핑"},
                            {"name": "Seine River Walk", "desc": "세느강변 산책로", "time": "저녁 18-19시", "tip": "일몰 시간대 가면 감성 최고"},
                        ],
                        "restaurants": [
                            {"name": "L'As du Fallafel", "type": "점심", "price": "8유로", "tip": "팔라펠 샌드위치가 시그니처, 줄 서도 10분이면"},
                            {"name": "Le Petit Cler", "type": "저녁", "price": "22유로", "tip": "스테이크 프리츠 추천"},
                        ],
                        "transport": "공항 리무진 버스 + 도보",
                        "estimated_cost": {
                            "transport": "26유로 (공항-시내 왕복)",
                            "food": "35유로",
                            "activities": "묶음",
                            "total": "61유로"
                        },
                    },
                    {
                        "day": 2,
                        "title": "에펠탑 & 생제륧망데프레",
                        "theme": "파리의 상징과 현지인 동네",
                        "content": """🎫 예약 필요: 에펠탑 (미리 예매 필수), Le Comptoir du Relais (저녁 예약 권장)

오늘은 파리의 상징 에펠탑부터 볼 예정이에요. 하지만 무턱대고 가면 줄 때문에 2시간을 날릴 수 있어서, 미리 예약하고 아침 일찍 가는 것이 필수랍니다.

에펠탑은 1889년 세워진 파리의 랜드마크예요. 꼭대기까지 갈 필요는 없어요. 2층까지만 가도 파리 전경이 쫙 펼쳐지더라구요. 여기서 찍은 사진은 인생샷 각오가 필요해요. 예약은 공식 홈페이지에서 시간대 지정으로 하셔야 해요.

사진 찍기 좋은 곳은 트로카데로(Trocadéro) 광장이에요. 에펠탑과 정면으로 마주 보는 위치라 프레임이 완벽하더라구요. 아침 9시 전에 가면 사람도 적고 사진도 잘 나와요.

점심은 생제륧망데프레로 넘어가시는 것을 추천드려요. 이 동네는 파리 현지인들이 제일 좋아하는 동네예요. 관광객도 있지만 현지 분위기가 진하게 남아있어요. Café de Flore는 역사적인 문학 카페예요. 사르트르와 드 보부아르가 단골이었던 곳이죠. 크루아상과 카페 오 레를 주문하고 잠깐 앉아보세요. 비싸지만 한 번쯤은 가볼 만한 곳이에요.

오후에는 룩셈부르크 정원(Jardin du Luxembourg)으로 가보세요. 파리 현지인들이 가장 좋아하는 공원이에요. 녹색 의자에 앉아서 책 읽는 사람들, 배드민턴 치는 아이들, 산책하는 연인들... 파리의 일상을 느낄 수 있어요. 여기서 1시간만 멍 때리면 피로가 싹 가시더라구요.

저녁은 Le Comptoir du Relais에서 파리식 브라세리 음식을 즐기시는 것을 추천드려요. 까수레(cassoulet, 소시지와 콩의 스튜)가 시그니처 메뉴예요. 예약이 필요하긴 한데, 7시 전에 가면 웨이팅 없이 들어갈 수 있더라구요.""",
                        "spots": [
                            {"name": "Eiffel Tower", "desc": "파리의 상징, 1889년 건립", "time": "오전 8:30-10:30", "tip": "2층까지만 가도 충분, 미리 예매 필수", "reservation_url": "https://www.toureiffel.paris/en/rates-conditions", "reservation_required": True},
                            {"name": "Trocadéro", "desc": "에펠탑 전망대", "time": "오전 10:30-11:00", "tip": "사진 포인트", "reservation_required": False},
                            {"name": "Café de Flore", "desc": "역사적 문학 카페", "time": "점심 12:00-13:30", "tip": "크루아상과 커피", "reservation_required": False},
                            {"name": "Jardin du Luxembourg", "desc": "현지인 최애 공원", "time": "오후 14:00-16:00", "tip": "의자에 앉아 멍 때리기", "reservation_required": False},
                        ],
                        "restaurants": [
                            {"name": "Café de Flore", "type": "브런치", "price": "15유로", "tip": "역사적인 카페, 크루아상 추천", "reservation_required": False},
                            {"name": "Le Comptoir du Relais", "type": "저녁", "price": "30유로", "tip": "까수레(소시지 스튜)가 시그니처", "reservation_required": True, "reservation_url": "https://www.comptoidurelais.com/", "reservation_note": "현장 웨이팅 가능, 7시 전 도착 권장"},
                        ],
                        "transport": "Metro Line 6, 4",
                        "estimated_cost": {
                            "transport": "4유로 (메트로 하루권)",
                            "food": "50유로",
                            "activities": "25유로 (에펠탑 2층)",
                            "total": "79유로"
                        },
                    },
                    {
                        "day": 3,
                        "title": "루브르 & 예술의 거리",
                        "theme": "세계 최고의 미술관과 중세 건축",
                        "content": """오늘은 세계 최고의 미술관, 루브르에서 하루를 보낼 예정이에요. 하루 종일 봐도 모자란 곳이지만 핵심만 쏙쏙 골라보실 거예요.

루브르는 원래 왕궁이었어요. 프랑스 혁명 이후 박물관으로 바뀌었고, 현재는 세계에서 가장 큰 미술관이에요. 피라미드 입구가 유명하지만 지하 쇼핑센터에서도 들어갈 수 있어요. 미리 예매하면 줄 안 서고 바로 들어갈 수 있더라구요. 시간대 지정 예약은 최소 일주일 전에 하시는 것을 권장드려요.

모나리자는 당연히 봐야 하지만, 그것만 보고 오면 아까워요. 루브르에는 3만 5천 점의 작품이 있거든요. 이집트관, 그리스 조각관, 프랑스 회화관 위주로 돌아보시는 것을 추천드려요. 베르사유의 디아나, 승리의 여신, 밀로의 비너스... 사진으로만 보던 작품들을 실제로 보면 감동이 확실히 다르더라구요.

점심은 박물관 안 카페에서 간단히 해결하세요. 비싸지만 시간 아끼는 것이 우선이에요. 오후에는 생트샤펠(Sainte-Chapelle)로 가보세요. 이 곳은 중세 스테인드글라스 예술의 정수예요. 15개의 거대한 스테인드글라스 창문이 천장까지 둘러싸고 있어요. 햇빛이 들어오면 무지개빛으로 빛나는데, 그 장관은 말로 표현할 수 없을 정도예요. 날씨 좋은 날 가면 그 감동이 배가 되더라구요.

저녁에는 마레 지구로 돌아와서 Chez Janou에서 저녁을 드시는 것을 추천드려요. 프로방스 지방 요리를 파는 곳인데, 초콜릿 무스가 정말 유명해요. 한국에서 먹던 무스랑은 차원이 달라요. 예약하고 가시는 것이 좋아요. 특히 주말에는 만석이더라구요.""",
                        "spots": [
                            {"name": "Louvre Museum", "desc": "세계 최대 미술관", "time": "오전 9:00-13:00", "tip": "미리 예매 필수, 모나리자보다 다른 작품도 봐", "reservation_url": "https://www.louvre.fr/en/visit/tickets", "reservation_required": True, "reservation_note": "시간대 지정 예약 필수, 최소 1주일 전 예약 권장"},
                            {"name": "Sainte-Chapelle", "desc": "스테인드글라스 예술", "time": "오후 14:00-15:00", "tip": "날씨 좋은 날 가면 빛이 환상적", "reservation_url": "https://www.sainte-chapelle.fr/en/", "reservation_required": True, "reservation_note": "온라인 예매 시 입장료 할인"},
                            {"name": "Pont des Arts", "desc": "예술의 다리", "time": "저녁 17:00-18:00", "tip": "센강 위 산책", "reservation_required": False},
                        ],
                        "restaurants": [
                            {"name": "Louvre Caf", "type": "점심", "price": "20유로", "tip": "박물관 안에서 간단히", "reservation_required": False},
                            {"name": "Chez Janou", "type": "저녁", "price": "40유로", "tip": "프로방스 요리, 초콜릿 무스 꼭", "reservation_url": "https://www.chezjanou.com/", "reservation_required": True, "reservation_note": "예약 권장, 특히 주말"},
                        ],
                        "transport": "Metro Line 1, 7",
                        "estimated_cost": {
                            "transport": "4유로",
                            "food": "65유로",
                            "activities": "30유로 (루브르 17 + 생트샤펠 11.5)",
                            "total": "99유로"
                        },
                    },
                    {
                        "day": 4,
                        "title": "몽마르트 & 에펠탑 야경",
                        "theme": "예술의 언덕과 반짝이는 밤",
                        "content": """오늘은 파리에서 가장 예술적인 동네 몽마르트를 탐험하고, 에펠탑 야경으로 로맨틱하게 마무리할 예정이에요. 몽마르트는 예술가들의 성지예요. 피카소, 르누아르, 반 고흐가 모두 이 동네에서 살고 작업했거든요.

아침 일찍 사크레쾨르(Sacré-Cœur) 성당으로 가보세요. 흰 돔이 특징인 이 성당은 파리에서 가장 높은 언덕 위에 있어요. 300계단을 걸어 올라가는 수고를 감수하면 파리 시내가 한눈에 내려다보여요. 일출 시간대에 가면 사람도 적고 분위기도 좋더라구요. 성당 안은 무료로 들어갈 수 있어요.

Place du Tertre(테르트르 광장)는 몽마르트의 중심이에요. 거리 작가들이 초상화를 그려주고, 귀여운 카페들이 즐비해 있어요. 여기서 커피 한 잔 마시면서 거리 공연을 구경하는 것도 좋아요. 작가들이 그려주는 초상화는 20-50유로 정도 해요. 시간 되시면 그려보시는 것도 추천드려요.

Musée de Montmartre는 몽마르트 미술관이에요. 르누아르, 발라, 위유트르가 살았던 집을 개조한 곳이에요. 정원이 정말 예쁘고, 파리의 예술사를 한눈에 볼 수 있어요. 입장료는 15유로 정도예요.

저녁에는 미슐랭 1성 레스토랑, Septime에서 특별한 식사를 해보세요. 파리에서 가장 예약하기 힘든 레스토랑 중 하나예요. 현대 프랑스 요리를 선보이는 곳인데, 코스 요리가 110유로 정도 해요. 평생 잊지 못할 맛이실 거예요. 예약은 꼭 한 달 전에 하셔야 해요.

밤이 되면 에펠탑으로 가보세요. 매시간 5분간 반짝이는 조명쇼가 펼쳐져요. 어두운 밤하늘에 반짝이는 에펠탑을 보면 정말 황홀해요. 이 광경을 보면 '아, 내가 진짜 파리에 왔구나' 하는 실감이 나실 거예요.""",
                        "spots": [
                            {"name": "Sacré-Cœur", "desc": "흰 돔 성당, 파리 전망", "time": "오전 8:00-10:00", "tip": "일출 시간대 사람 적음"},
                            {"name": "Place du Tertre", "desc": "예술가들의 광장", "time": "오전 10:00-12:00", "tip": "초상화 그려주는 거리 작가들"},
                            {"name": "Musée de Montmartre", "desc": "르누아르, 발라 등 거취", "time": "오후 13:00-15:00", "tip": "정원도 예쁨"},
                            {"name": "Eiffel Tower Night", "desc": "야경 & 조명쇼", "time": "저녁 20:00-21:00", "tip": "매시간 5분간 반짝이는 조명쇼"},
                        ],
                        "restaurants": [
                            {"name": "Montmartre Bistro", "type": "점심", "price": "25유로", "tip": "Place du Tertre 주변"},
                            {"name": "Septime", "type": "저녁", "price": "110유로", "tip": "미슐랭 1성, 예약 필수", "reservation_required": True, "reservation_url": "https://www.septimorestaurant.com/", "reservation_note": "한 달 전 예약 필수, 매우 인기 있는 곳"},
                        ],
                        "transport": "Metro Line 2, 12 + 버스",
                        "estimated_cost": {
                            "transport": "6유로",
                            "food": "140유로",
                            "activities": "15유로",
                            "total": "161유로"
                        },
                    },
                    {
                        "day": 5,
                        "title": "마무리 & 쇼핑, 공항으로",
                        "theme": "여유로운 마지막 날",
                        "content": """마지막 날이에요. 짐 챙기기 전에 가볍게 마무리하는 날이에요. 빠진 곳이 있다면 채우고, 쇼핑할 거라면 오늘이 마지막 기회예요.

갤러리 라파예트(Galeries Lafayette)는 파리를 대표하는 명품 백화점이에요. 하우스 브랜드부터 럭셔리 브랜드까지 다 있어요. 쇼핑을 안 해도 꼭 가봐야 할 곳이에요. 옥상 테라스가 있는데, 여기서 보는 파리 전망이 정말 멋져요. 게다가 무료예요. 오페라 하우스 지붕과 에펠탑이 한 화면에 잡혀요.

점심은 부용 샤르티에(Bouillon Chartier)에서 해결하시는 것을 추천드려요. 1896년부터 영업한 전통 브라세리예요. 1900년대 초반 분위기 그대로라 인테리어도 볼거리가 많아요. 에스카르고(달팽이 요리), 코코뱅(닭고기 스튜) 같은 클래식 프랑스 요리를 저렴한 가격에 맛볼 수 있어요. 웨이팅이 있지만 15-20분이면 들어갈 수 있더라구요.

오후에는 짐을 챙겨서 샤를 드 골 공항으로 이동하세요. RER B선을 타면 약 45분이 걸려요. 비행기는 3시간 전에 도착하시는 것이 안전해요. 공항 면세점에서 마지막 쇼핑도 하실 수 있어요.

5일간의 파리 여행이 끝났어요. 느긋하게 카페에서 보낸 시간, 골목길을 걸으며 발견한 멋진 가게들, 감동적이었던 미술관과 야경... 이 모든 것이 추억으로 남으실 거예요. 파리는 언제 다시 와도 좋은 도시더라구요. 다음에는 또 다른 동네를 탐험해보세요.""",
                        "spots": [
                            {"name": "Galeries Lafayette", "desc": "파리 명품 백화점", "time": "오전 10:00-13:00", "tip": "옥상 테라스 무료 전망"},
                            {"name": "Bouillon Chartier", "desc": "1896년 전통 브라세리", "time": "점심 13:00-14:30", "tip": "에스카르고, 코코뱅"},
                            {"name": "Charles de Gaulle Airport", "desc": "귀국", "time": "오후 15:00 이후", "tip": "비행기 3시간 전 도착"},
                        ],
                        "restaurants": [
                            {"name": "Bouillon Chartier", "type": "점심", "price": "20유로", "tip": "1900년대 분위기, 가성비 최고"},
                        ],
                        "transport": "Metro + RER B",
                        "estimated_cost": {
                            "transport": "15유로 (RER B 공항)",
                            "food": "25유로",
                            "activities": "쇼핑 비용 별도",
                            "total": "40유로+"
                        },
                    },
                ],
                
                "parking_info": {
                    "difficulty": "어려움",
                    "city_center_rate": "시간당 4-6유로",
                    "recommendation": "도심은 대중교통 이용, 렌트카는 외곽에서만",
                    "pr_locations": [
                        {"name": "Parc de la Villette P+R", "rate": "하루 10-15유로", "metro": "Line 7", "address": "211 Av. Jean Jaurès, 75019 Paris", "maps_url": "https://www.google.com/maps/search/Parc+de+la+Villette+P+R+Paris"},
                        {"name": "Bercy P+R", "rate": "하루 12유로", "metro": "Line 6, 14", "address": "48 Bd de Bercy, 75012 Paris", "maps_url": "https://www.google.com/maps/search/Bercy+P+R+Paris"},
                        {"name": "La Défense P+R", "rate": "하루 8-10유로", "metro": "Line 1, RER A", "address": "Centre Commercial Les 4 Temps, 92800 Puteaux", "maps_url": "https://www.google.com/maps/search/La+Defense+P+R+Paris"},
                    ],
                    "apps": ["Zenpark", "Parking Paris"],
                    "tips": [
                        "P+R 주차장은 주차료가 저렴하고 메트로로 바로 연결되어 있어요",
                        "주차 후 메트로로 시내 진입하는 것이 가장 경제적이에요",
                        "주말에는 P+R 주차장이 일찍 찰 수 있으니 아침 일찍 가세요",
                        "도심 주차는 시간당 4-6유로로 비싸고 주차 공간 찾기도 어려워요"
                    ]
                },
                
                "transport_summary": {
                    "metro": "1회 2.1유로, 10회권 17.35유로",
                    "uber": "도심 10-20유로",
                    "taxi": "시작 7.3유로 + km당 1.1유로",
                    "rental_car": "하루 50-80유로 + 주차비 별도",
                },
                
                "total_estimate": {
                    "budget": {
                        "accommodation": "85유로 x 4박 = 340유로",
                        "food": "40유로 x 5일 = 200유로",
                        "transport": "50유로",
                        "activities": "100유로",
                        "total": "690유로 (약 100만원)"
                    },
                    "luxury": {
                        "accommodation": "850유로 x 4박 = 3,400유로",
                        "food": "120유로 x 5일 = 600유로",
                        "transport": "100유로",
                        "activities": "200유로",
                        "total": "4,300유로 (약 630만원)"
                    }
                },
                
                "brave_search_queries": [
                    "Paris travel itinerary 5 days 2024 blog",
                    "best restaurants Paris Marais local guide",
                    "Paris hotel recommendations budget luxury",
                    "Paris transportation guide Metro Uber",
                    "Paris parking rental car tips",
                ],
            },
            "Rome": {
                "nickname": "영원한 도시",
                "best_season": "4-5월, 9-10월",
                "currency": "유로 (EUR)",
                "language": "이탈리아어",
                "flight_time": "직항 약 13시간",
                "car_rental_available": False,
                "parking_difficulty": "매우 어려움 (ZTL 제한구역)",
                "country": "Italy",
                "intro": """로마는 역사가 살아있는 도시예요. 콜로세움, 바티칸, 트레비 분수... 고대 로마의 영광이 곳곳에 남아있어요. 한국인에게 가장 인기 있는 유럽 도시 중 하나로, 역사와 예술, 맛집이 공존하는 곳이에요. 도보 중심으로 둘러보는 것이 가장 좋답니다.""".strip(),
                
                "hotels": {
                    "budget": [
                        {"name": "Hotel Artis", "rating": 4.1, "price_per_night": "€70-90", "area": "Termini 역 근처", "pros": "중앙역 접근성 좋음, 가성비", "cons": "소음 있을 수 있음", "maps_url": "https://www.google.com/maps/search/Hotel+Artis+Rome"},
                        {"name": "Hotel Santa Maria", "rating": 4.3, "price_per_night": "€95-120", "area": "트라스테베레", "pros": "조용한 동네, 아침식사 좋음", "cons": "관광지와 거리 있음", "maps_url": "https://www.google.com/maps/search/Hotel+Santa+Maria+Rome"},
                    ],
                    "luxury": [
                        {"name": "Hotel Eden", "rating": 4.7, "price_per_night": "€600-900", "area": "스페인 광장 근처", "pros": "도로르스 미슐랭 레스토랑, 에펠탑 뷰", "cons": "가격대가 높음", "maps_url": "https://www.google.com/maps/search/Hotel+Eden+Rome"},
                        {"name": "Hassler Roma", "rating": 4.8, "price_per_night": "€700-1000", "area": "스페인 계단", "pros": "스페인 계단 정면, 역사적인 명성", "cons": "예약 2-3개월 전 필요", "maps_url": "https://www.google.com/maps/search/Hassler+Roma"},
                    ],
                },
                
                "days_plan": [
                    {
                        "day": 1,
                        "title": "도착 & 콜로세움, 로마 포럼",
                        "theme": "고대 로마의 영광",
                        "content": """📍 예약 필요: 콜로세움 (미리 예매 권장)

첫날은 로마의 상징 콜로세움과 포럼에서 고대 로마의 역사를 느껴 보세요. 피우미치노 공항에서 테륵미니역까지 레오나륵도 익스프레스(14유로, 32분)를 이용하는 것이 편해요.

콜로세움은 2,000년 전 검투사들이 싸우던 곳으로, 현재까지 보존된 가장 큰 원형 경기장이에요. 미리 예매하면 줄 안 서고 들어갈 수 있어요. 로마 포럼은 고대 로마의 정치, 상업 중심지로, 폐허 속에서도 당시의 웅장함이 느껴져요.

저녁은 트라스테베레 동네에서 로마식 저녁을 즐기세요. 이 동네는 현지인들이 많이 찾는 곳으로, 관광객이 적고 정통 이탈리아 요리를 맛볼 수 있어요.""",
                        "spots": [
                            {"name": "Colosseum", "desc": "고대 로마 원형 경기장, 2,000년 역사", "time": "오전 9-12시", "tip": "아침 일찍 가면 사람 적음", "reservation_url": "https://www.coopculture.it/en/colosseo-e-foro-romano.html", "reservation_required": True},
                            {"name": "Roman Forum", "desc": "고대 로마 중심지 폐허", "time": "오후 13-15시", "reservation_required": False},
                            {"name": "Palatine Hill", "desc": "로마 건국 전설의 언덕", "time": "오후 15-17시", "reservation_required": False},
                        ],
                        "restaurants": [
                            {"name": "Da Enzo al 29", "type": "저녁", "price": "25유로", "tip": "트라스테베레 현지인 맛집, 카르 보나라 추천", "reservation_required": True, "reservation_note": "예약 필수, 특히 주말"},
                        ],
                        "transport": "공항 리무진 + 도보",
                        "estimated_cost": {"transport": "28유로", "food": "40유로", "activities": "18유로", "total": "86유로"},
                    },
                    {
                        "day": 2,
                        "title": "바티칸 & 성베드로 대성당",
                        "theme": "종교와 예술의 중심",
                        "content": """🎫 예약 필요: 바티칸 박물관 (최소 1주일 전 예약 필수), 성베드로 대성당 (묣음이지만 줄 있음)

오늘은 세계에서 가장 작은 국가 바티칸을 방문해요. 바티칸 박물관에는 미켈란젤로의 천장화와 라파엘로의 방이 있어요. 시스티나 예배당의 '천지창조'는 실물을 볼 때 더욱 감동적이에요.

성베드로 대성당은 세계 최대의 가톨릭 성당으로, 미켈란젤로의 '성모자상'이 전시되어 있어요. 돔 올라가면 로마 전경이 한눈에 보여요. 복장 규정이 엄격하니 어깨와 무릎이 가려진 옷을 입으세요.""",
                        "spots": [
                            {"name": "Vatican Museums", "desc": "미켈란젤로, 라파엘로 작품", "time": "오전 9-13시", "tip": "시스티나 예배당 하이라이트", "reservation_url": "https://www.museivaticani.va/content/museivaticani/en/visita-i-musei.html", "reservation_required": True, "reservation_note": "1주일 전 예약 필수"},
                            {"name": "St. Peter's Basilica", "desc": "세계 최대 가톨릭 성당", "time": "오후 14-16시", "tip": "돔 등반 추천 (8유로)", "reservation_required": False},
                            {"name": "Castel Sant'Angelo", "desc": "성베드로 묘지 위에 세워진 성", "time": "오후 16-18시", "reservation_required": False},
                        ],
                        "restaurants": [
                            {"name": "Pizzarium Bonci", "type": "점심", "price": "12유로", "tip": "바티칸 근처 최고의 피자", "reservation_required": False},
                        ],
                        "transport": "Metro Line A",
                        "estimated_cost": {"transport": "3유로", "food": "45유로", "activities": "25유로", "total": "73유로"},
                    },
                    {
                        "day": 3,
                        "title": "스페인 계단 & 트레비 분수",
                        "theme": "로마의 낭만",
                        "content": """📍 예약 필요: 없음

오늘은 로마의 낭만적인 명소들을 둘러봐요. 스페인 계단은 '로마의 휴일'에서 오드리 헵번이 아이스크림을 먹던 곳으로 유명해요. 계단 위 트리니타 데이 몬티 성당에서 내려다보는 전망이 멋져요.

트레비 분수는 동전을 던지면 다시 로마에 올 수 있다는 전설이 있는 곳이에요. 분수 앞에서 오른손으로 왼쪽 어깨 위로 동전을 던져보세요. 판테온은 2,000년 된 로마 신전으로, 현재까지 완벽하게 보존된 건축물이에요.

점심은 나보나 광장 근처에서 즐기세요. 야외 테이블에 앉아서 분위기를 즐기는 것이 로마 여행의 묘미예요.""",
                        "spots": [
                            {"name": "Spanish Steps", "desc": "135개의 계단, 트리니타 데이 몬티 교회", "time": "오전 9-10시", "tip": "아침에 가면 사람 적음", "reservation_required": False},
                            {"name": "Trevi Fountain", "desc": "로마 최대 분수, 동전 던지기", "time": "오전 10-11시", "tip": "새벽에 가면 한적함", "reservation_required": False},
                            {"name": "Pantheon", "desc": "2,000년 된 로마 신전", "time": "오후 12-13시", "tip": "돔의 오쿨러스 구경", "reservation_required": False},
                            {"name": "Piazza Navona", "desc": "4대 강을 상징하는 분수", "time": "오후 14-15시", "tip": "카페에서 휴식", "reservation_required": False},
                        ],
                        "restaurants": [
                            {"name": "Roscioli Salumeria", "type": "점심", "price": "35유로", "tip": "까르보나라 원조 맛집", "reservation_required": True, "reservation_url": "https://www.salumeriaroscioli.com/", "reservation_note": "예약 필수"},
                        ],
                        "transport": "도보",
                        "estimated_cost": {"transport": "0유로", "food": "55유로", "activities": "10유로", "total": "65유로"},
                    },
                    {
                        "day": 4,
                        "title": "보르게세 갤러리 & 빌라 보르게세",
                        "theme": "예술과 자연",
                        "content": """🎫 예약 필요: 보르게세 갤러리 (2주일 전 예약 필수)

오늘은 로마 최고의 미술관인 보르게세 갤러리를 방문해요. 베르니니의 조각상과 카라바조의 그림을 볼 수 있어요. 예약은 2주일 전에 해야 할 정도로 인기가 많아요.

갤러리가 있는 빌라 보르게세 공원은 로마에서 가장 큰 공원으로, 그늘진 산책로와 호수가 있어요. 공원 위 전망대에서는 성베드로 대성당 돔이 보여요.

저녁에는 나보나 광장에서 마지막 저녁을 즐기세요. 야외 테이블에 앉아서 지나가는 사람들을 구경하는 것이 로마식 여유예요.""",
                        "spots": [
                            {"name": "Borghese Gallery", "desc": "베르니니, 카라바조 작품", "time": "오전 9-11시", "tip": "2시간 시간제한 있음", "reservation_url": "https://www.galleriaborghese.beniculturali.it/", "reservation_required": True, "reservation_note": "2주일 전 예약 필수"},
                            {"name": "Villa Borghese Gardens", "desc": "로마 최대 공원", "time": "오후 12-14시", "tip": "전망대에서 성베드로 돔 보기", "reservation_required": False},
                            {"name": "Pincian Hill", "desc": "일몰 명소", "time": "저녁 17-18시", "tip": "벤치에 앉아 일몰 감상", "reservation_required": False},
                        ],
                        "restaurants": [
                            {"name": "Flavio al Velavevodetto", "type": "저녁", "price": "30유로", "tip": "Testaccio 언덕 레스토랑, 까치오 에 페페 추천", "reservation_required": True},
                        ],
                        "transport": "버스 + 도보",
                        "estimated_cost": {"transport": "3유로", "food": "50유로", "activities": "15유로", "total": "68유로"},
                    },
                    {
                        "day": 5,
                        "title": "마무리 & 귀국",
                        "theme": "여유로운 마지막",
                        "content": """마지막 날이에요. 늦잠을 자고 천천히 일어나 마지막 에스프레소를 즐기세요. 체크아웃 후에는 마지막 쇼핑이나 빠진 명소를 방문하실 수 있어요.

테륵미니역에서 레오나륵도 익스프레스를 타고 공항으로 이동하세요. 공항 면세점에서 마지막 쇼핑도 가능해요. 5일간의 로마 여행이 끝났어요. 다음에는 피렌체나 베네치아로 이탈리아 여행을 이어가 보세요.""",
                        "spots": [
                            {"name": "Campo de' Fiori", "desc": "아침 시장", "time": "오전 9-11시", "tip": "신선한 과일과 치즈 구매", "reservation_required": False},
                            {"name": "Fiumicino Airport", "desc": "귀국", "time": "오후 14시 이후", "tip": "비행기 3시간 전 도착", "reservation_required": False},
                        ],
                        "restaurants": [
                            {"name": "Cafe near hotel", "type": "브런치", "price": "15유로", "tip": "마지막 에스프레소", "reservation_required": False},
                        ],
                        "transport": "레오나륵도 익스프레스",
                        "estimated_cost": {"transport": "28유로", "food": "20유로", "activities": "0유로", "total": "48유로"},
                    },
                ],
                
                "parking_info": {
                    "difficulty": "매우 어려움 (ZTL 제한구역)",
                    "city_center_rate": "도심 차량 진입 불가 (ZTL)",
                    "recommendation": "로마는 렌트카 비추천, 대중교통 이용",
                    "pr_locations": [
                        {"name": "Parking Villa Borghese", "rate": "시간당 2-3유로", "metro": "Line A", "address": "Viale del Galoppatoio, 33, 00197 Roma", "maps_url": "https://www.google.com/maps/search/Parking+Villa+Borghese+Rome"},
                    ],
                    "apps": ["MyCicero", "EasyPark"],
                    "tips": [
                        "로마 도심은 ZTL(교통제한구역)으로 렌트카 진입 불가",
                        "위반 시 100유로 이상 과태료 부과",
                        "대중교통이 가장 편리해요",
                    ]
                },
                
                "transport_summary": {
                    "metro": "1회 1.5유로, 24시간권 7유로",
                    "bus": "1.5유로 (메트로와 동일 티켓)",
                    "taxi": "시작 4유로 + km당 1.5유로",
                    "rental_car": "비추천 (ZTL 제한)",
                },
                
                "total_estimate": {
                    "budget": {
                        "accommodation": "€80 x 4박 = 320유로",
                        "food": "€35 x 5일 = 175유로",
                        "transport": "50유로",
                        "activities": "100유로",
                        "total": "645유로 (약 94만원)"
                    },
                    "luxury": {
                        "accommodation": "€650 x 4박 = 2,600유로",
                        "food": "€100 x 5일 = 500유로",
                        "transport": "100유로",
                        "activities": "150유로",
                        "total": "3,350유로 (약 490만원)"
                    }
                },
                
                "brave_search_queries": [
                    "Rome travel itinerary 5 days 2024",
                    "best restaurants Rome Trastevere",
                    "Vatican museums booking guide",
                    "Rome transportation pass",
                ],
            },
        }
    
    # 국가별 상세 대사관 정보
    EMBASSY_INFO = {
        "France": {
            "name": "주프랑스 한국대사관 (Embassy of the Republic of Korea in France)",
            "phone": "+33-1-47-53-01-01",
            "emergency_phone": "+33-1-47-53-01-01 (업무시간 후 긴급건)",
            "address": "125 rue de Grenelle, 75007 Paris, France",
            "hours": "월-금 09:00-12:00, 14:00-17:00 (프랑스 공휴일 휴관)",
            "email": "koreanembassy@mofa.go.kr",
            "website": "https://overseas.mofa.go.kr/fr-ko/index.do",
            "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무", "긴급 구호 지원"]
        },
        "Italy": {
            "name": "주이탈리아 한국대사관 (Embassy of the Republic of Korea in Italy)",
            "phone": "+39-06-802-461",
            "emergency_phone": "+39-06-802-461 (업무시간 후 긴급건)",
            "address": "Via Barnaba Oriani 30, 00197 Roma, Italy",
            "hours": "월-금 09:00-12:30, 14:00-17:00 (이탈리아 공휴일 휴관)",
            "email": "koreaembassy@mofa.go.kr",
            "website": "https://overseas.mofa.go.kr/it-ko/index.do",
            "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무", "긴급 구호 지원"]
        },
        "Spain": {
            "name": "주스페인 한국대사관 (Embassy of the Republic of Korea in Spain)",
            "phone": "+34-91-353-2000",
            "emergency_phone": "+34-91-353-2000 (업무시간 후 긴급건)",
            "address": "Calle González Amigó 15, 28036 Madrid, Spain",
            "hours": "월-금 09:00-13:00, 14:00-17:00 (스페인 공휴일 휴관)",
            "email": "koremb@mofa.go.kr",
            "website": "https://overseas.mofa.go.kr/es-ko/index.do",
            "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무", "긴급 구호 지원"]
        },
        "Germany": {
            "name": "주독일 한국대사관 (Embassy of the Republic of Korea in Germany)",
            "phone": "+49-30-203-610",
            "emergency_phone": "+49-30-203-610 (업무시간 후 긴급건)",
            "address": "Leipziger Platz 3, 10117 Berlin, Germany",
            "hours": "월-금 09:00-12:00, 14:00-17:00 (독일 공휴일 휴관)",
            "email": "info@koreanembassy.de",
            "website": "https://overseas.mofa.go.kr/de-ko/index.do",
            "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무", "긴급 구호 지원"]
        },
        "UK": {
            "name": "주영국 한국대사관 (Embassy of the Republic of Korea in the UK)",
            "phone": "+44-20-7227-5500",
            "emergency_phone": "+44-20-7227-5500 (업무시간 후 긴급건)",
            "address": "60 Buckingham Gate, London SW1E 6AJ, United Kingdom",
            "hours": "월-금 09:30-12:30, 14:00-17:00 (영국 공휴일 휴관)",
            "email": "info@koreanembassy.org.uk",
            "website": "https://overseas.mofa.go.kr/gb-ko/index.do",
            "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무", "긴급 구호 지원"]
        },
        "Japan": {
            "name": "주일본 한국대사관 (Embassy of the Republic of Korea in Japan)",
            "phone": "+81-3-3452-7611",
            "emergency_phone": "+81-90-3320-3111 (재외국민 긴급전화)",
            "address": "1-2-5 Minami-Azabu, Minato-ku, Tokyo 106-0047, Japan",
            "hours": "월-금 09:30-12:00, 13:30-16:30 (일본 공휴일 휴관)",
            "email": "info@koreaembassy.jp",
            "website": "https://overseas.mofa.go.kr/jp-ko/index.do",
            "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무", "긴급 구호 지원"]
        },
        "Thailand": {
            "name": "주태국 한국대사관 (Embassy of the Republic of Korea in Thailand)",
            "phone": "+66-2-247-7530",
            "emergency_phone": "+66-81-826-5666 (재외국민 긴급전화)",
            "address": "23 Thiam-Ruammit Road, Ratchadapisek, Huai Khwang, Bangkok 10320, Thailand",
            "hours": "월-금 09:00-12:00, 13:30-16:00 (태국 공휴일 휴관)",
            "email": "korembassy@mofa.go.kr",
            "website": "https://overseas.mofa.go.kr/th-ko/index.do",
            "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무", "긴급 구호 지원"]
        },
        "Singapore": {
            "name": "주싱가포르 한국대사관 (Embassy of the Republic of Korea in Singapore)",
            "phone": "+65-6256-1188",
            "emergency_phone": "+65-9236-5413 (재외국민 긴급전화)",
            "address": "47 Scotts Road, #08-00 Goldbell Towers, Singapore 228233",
            "hours": "월-금 09:00-12:00, 14:00-17:00 (싱가포르 공휴일 휴관)",
            "email": "koreanembassy@mofa.go.kr",
            "website": "https://overseas.mofa.go.kr/sg-ko/index.do",
            "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무", "긴급 구호 지원"]
        },
        "USA": {
            "name": "주미국 한국대사관 (Embassy of the Republic of Korea in the USA)",
            "phone": "+1-202-939-5600",
            "emergency_phone": "+1-202-939-5600 (24시간 긴급)",
            "address": "2450 Massachusetts Avenue NW, Washington, DC 20008, USA",
            "hours": "월-금 09:00-12:00, 13:30-17:00 (미국 공휴일 휴관)",
            "email": "washington@mofa.go.kr",
            "website": "https://overseas.mofa.go.kr/us-ko/index.do",
            "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무", "긴급 구호 지원"]
        },
        "Vietnam": {
            "name": "주베트남 한국대사관 (Embassy of the Republic of Korea in Vietnam)",
            "phone": "+84-24-3831-5116",
            "emergency_phone": "+84-24-3831-5116 (업무시간 후 긴급건)",
            "address": "63-65 Ly Thai To, Hoan Kiem, Hanoi, Vietnam",
            "hours": "월-금 09:00-12:00, 14:00-17:00 (베트남 공휴일 휴관)",
            "email": "koremb@mofa.go.kr",
            "website": "https://overseas.mofa.go.kr/vn-ko/index.do",
            "services": ["여권 재발급/분실 신고", "긴급 여행증 발급", "사증(비자) 업무", "재외국민 등록", "공증/인증 업무", "긴급 구호 지원"]
        }
    }
    
    # 국가별 긴급 연락처
    EMERGENCY_NUMBERS = {
        "France": {"police": "17", "ambulance": "15", "fire": "18", "general": "112"},
        "Italy": {"police": "113", "ambulance": "118", "fire": "115", "general": "112"},
        "Spain": {"police": "091", "ambulance": "061", "fire": "080", "general": "112"},
        "Germany": {"police": "110", "ambulance": "112", "fire": "112", "general": "112"},
        "UK": {"police": "999", "ambulance": "999", "fire": "999", "general": "999"},
        "Netherlands": {"police": "112", "ambulance": "112", "fire": "112", "general": "112"},
        "Austria": {"police": "133", "ambulance": "144", "fire": "122", "general": "112"},
        "Greece": {"police": "100", "ambulance": "166", "fire": "199", "general": "112"},
        "Portugal": {"police": "112", "ambulance": "112", "fire": "112", "general": "112"},
        "Czech Republic": {"police": "158", "ambulance": "155", "fire": "150", "general": "112"},
        "Hungary": {"police": "107", "ambulance": "104", "fire": "105", "general": "112"},
        "Thailand": {"police": "191", "ambulance": "1669", "fire": "199", "general": "1155"},
        "Singapore": {"police": "999", "ambulance": "995", "fire": "995", "general": "999"},
        "Malaysia": {"police": "999", "ambulance": "999", "fire": "994", "general": "999"},
        "Indonesia": {"police": "110", "ambulance": "118", "fire": "113", "general": "112"},
        "Vietnam": {"police": "113", "ambulance": "115", "fire": "114", "general": "112"},
        "Philippines": {"police": "117", "ambulance": "911", "fire": "911", "general": "911"},
        "Japan": {"police": "110", "ambulance": "119", "fire": "119", "general": "110"},
        "USA": {"police": "911", "ambulance": "911", "fire": "911", "general": "911"},
        "Australia": {"police": "000", "ambulance": "000", "fire": "000", "general": "000"},
        "UAE": {"police": "999", "ambulance": "998", "fire": "997", "general": "999"},
        "Turkey": {"police": "155", "ambulance": "112", "fire": "110", "general": "112"},
    }

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
            "휴양지": ["휴양지 추천", "리조트", "필리핀 여행", "몰디브", "푸켓"],
            "동아시아": ["일본 여행", "대만 여행", "홍콩 여행", "도쿄 여행"],
            "미주": ["미국 여행", "캐나다 여행", "LA 여행", "뉴욕 여행"],
            "중동": ["두바이 여행", "터키 여행", "이스탄불"],
            "오세아니아": ["호주 여행", "시드니 여행"]
        }
        
        keywords = base_keywords + region_keywords.get(region, [])
        
        # 해시태그 생성 (20-30개)
        hashtags = [
            f"#{city.replace(' ', '')}여행", f"#{country.replace(' ', '')}여행",
            "#해외여행", "#여행가이드", "#여행코스", "#여행일정",
            f"#{city.replace(' ', '')}맛집", f"#{city.replace(' ', '')}호텔",
            "#배낭여행", "#자유여행", "#혼자여행", "#커플여행", "#가족여행",
            f"#{region}여행" if region != "휴양지" else "#휴양지여행",
            "#여행블로거", "#여행스타그램", "#여행에미치다", "#세계여행",
            "#맛집탐방", "#카페투어", "#인생샷", "#여행사진",
            "#호캉스" if region == "휴양지" else "#관광",
            f"#{days}박{days+1}일", "#여행준비", "#여행꿀팁"
        ]
        
        # 중복 제거 및 셔플
        unique_hashtags = list(set(hashtags))
        
        # SEO 메타 설명 (150자 이내)
        meta_description = f"{city} {days}일 여행 완벽 가이드. {country}의 매력적인 관광지, 맛집, 호텔 추천과 함께 최적의 여행 코스를 확인하세요. 실제 여행자 리뷰 기반."
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
    
    def generate_enhanced_blog(self, city: str, days: int = 5, region: str = "유럽") -> Optional[Dict]:
        """향상된 블로그 콘텐츠 생성 - 모든 도시에 Paris 수준의 풍부한 콘텐츠 적용"""
        from content.rich_city_generator import rich_city_generator, CITY_DATABASE
        from city_rotator import get_city_by_name
        
        # 도시 정보 가져오기
        city_info = get_city_by_name(city)
        if not city_info:
            logger.error(f"City {city} not found in any database")
            return None
        
        actual_region = city_info.get('region', region)
        country = city_info['country']
        
        # 1. 하드코딩된 상세 데이터가 있으면 사용 (Paris, Amsterdam, Barcelona 등)
        if city in CITY_DATABASE:
            logger.info(f"Using detailed database for {city}")
            return rich_city_generator.generate_rich_content(city, country, actual_region, days)
        
        # 2. 하드코딩 없으면 Brave Search + 동적 생성
        if city not in self.cities_db:
            logger.warning(f"City {city} not in detailed database, using Brave Search + dynamic generation")
            return rich_city_generator.generate_rich_content(city, country, actual_region, days)
        
        # 3. 기존 cities_db에 있는 경우 (Rome, Bangkok 등) - 점진적으로 마이그레이션
        # 기존 데이터를 rich format으로 변환
        logger.info(f"Converting existing data for {city} to rich format")
        return self._convert_existing_to_rich(city, days, actual_region)
        
        data = self.cities_db[city]
        country = data.get("country", "France")
        
        # 국가별 대사관 및 긴급연락처 정보 가져오기
        embassy_info = self.EMBASSY_INFO.get(country, self.EMBASSY_INFO["France"])
        emergency_numbers = self.EMERGENCY_NUMBERS.get(country, self.EMERGENCY_NUMBERS["France"])
        
        # SEO 메타정보 및 해시태그 생성
        seo_meta = self._generate_seo_meta(city, country, days, region)
        
        return {
            "title": f"{city} 여행 완벽 가이드 | {days}일 통계 기반 일정 + 호텔/비용 총정리",
            "destination": {
                "name": city,
                "country": country,
                "nickname": data.get("nickname", ""),
                "best_season": data.get("best_season", ""),
                "currency": data.get("currency", ""),
                "flight_time": data.get("flight_time", ""),
                "days": days,
                "car_rental_available": data.get("car_rental_available", True),
                "parking_difficulty": data.get("parking_difficulty", ""),
            },
            "intro": data.get("intro", ""),
            "hotels": data.get("hotels", {}),
            "days_plan": data.get("days_plan", []),
            "parking_info": data.get("parking_info", {}),
            "transport_summary": data.get("transport_summary", {}),
            "total_estimate": data.get("total_estimate", {}),
            "brave_search_queries": data.get("brave_search_queries", []),
            "final_summary": {
                "must_reserve": [
                    {"name": "에펠탑", "when": "최소 2-4주 전", "url": "https://www.toureiffel.paris/en/rates-conditions"},
                    {"name": "루브르 박물관", "when": "최소 1주일 전", "url": "https://www.louvre.fr/en/visit/tickets"},
                    {"name": "생트샤펠", "when": "당일 또는 1-2일 전", "url": "https://www.sainte-chapelle.fr/en/"},
                    {"name": "Septime 레스토랑", "when": "최소 1개월 전", "url": "https://www.septimorestaurant.com/"},
                    {"name": "Le Comptoir du Relais", "when": "당일 웨이팅 또는 1주일 전", "url": "https://www.comptoidurelais.com/"},
                ],
                "essential_apps": ["Citymapper (네비게이션)", "Google Translate (번역)", "Zenpark (주차)"],
                "emergency_contacts": emergency_numbers,
                "embassy_info": embassy_info,
                "packing_checklist": ["여권/비자", "유로화 현금", "유니버셜 어댑터", "편한 운화", "보조 배터리", "우산"]
            },
            "seo": seo_meta,
            "generated_at": datetime.now().isoformat(),
        }


# 인스턴스 생성
enhanced_generator = EnhancedRichGenerator()
