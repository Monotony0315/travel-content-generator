"""
Rich Travel Blog Content Generator
실제 여행 블로그처럼 풍부한 콘텐츠 생성
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger


class RichContentGenerator:
    """GPT-5.2 스타일의 풍부한 여행 블로그 콘텐츠 생성기"""
    
    def __init__(self):
        self.cities_db = self._load_cities_db()
    
    def _load_cities_db(self) -> Dict:
        """도시별 상세 데이터베이스"""
        return {
            "Paris": {
                "nickname": "빛의 도시, 러브의 도시",
                "best_season": "4-6월, 9-10월",
                "currency": "유로 (EUR)",
                "language": "프랑스어",
                "timezone": "CET (UTC+1)",
                "flight_time": "직항 약 12시간",
                "intro": """
파리는 그냥 '가본다'로 끝나는 도시가 아니야. 에펠탑만 보고 오면 섭섭해진다는 말이 괜히 나온 게 아니거든. 
나도 처음엔 뻔한 랜드마크 체크리스트만 들고 갔다가, 현지에서 만난 작은 카페 하나에 반해서 
3시간을 앉아있었던 적이 있어. 그게 파리야. 느긋하게, 그리고 깊게 파고들어야 비로소 보이는 도시.

이번 가이드에서는 내가 직접 다녀온 것처럼 자연스럽게, 하지만 정직하게 추천하는 코스만 담았어.
무리한 일정 없이, 하루 2-3개 스팟씩 여유롭게 돌아볼 수 있게 짰으니까 참고해서 너만의 파리를 찾아봐.
                """.strip(),
                
                "days_plan": [
                    {
                        "day": 1,
                        "title": "도착 & 마레 지구 산책",
                        "theme": "느긋한 적응의 날",
                        "content": """
오늘은 무리하지 말고, 숙소 근처 마레 지구를 가볍게 둘러보는 걸로 시작하자. 
샤를 드 골 공항에서 시내로 나오는 게 제일 편한데, RER B선 타고 샤텔레 방면으로 40분이면 중심가야. 
대신 짐 많으면 공항 리무진 버스(16유로)가 더 편해.

**오전: 숙소 체크인 & 주변 탐색**
숙소는 마레(3구)나 생제륧망데프레(6구)가 처음엔 제일 좋아. 
체크인하고 나와서 근처 빵집에서 갓 구운 바게트 하나 들고, 세느강변을 슬슬 걸어보자. 
오전 11시쯤이면 강변에 현지인들 러닝하는 거 볼 수 있는데, 그게 파리의 아침이야.

**오후: 플레스 드 보그 & 뒤편 골목**
점심은 마레 지구의 L'As du Fallafel(루 드 로지에 34)에서 해결하자. 
줄이 항상 있지만 10-15분이면 들어가고, 팔라펠 샌드위치 하나(8유로)면 배부를 거야. 
테이크아웃해서 마레의 작은 광장 플레스 드 보그에 앉아먹으면 그게 100점 만점의 파리 점심이야.

오후에는 마레의 빈티지 샵들 구경. 뒤편 골목으로 들어가면 Kilo Shop이나 Free'p'Star 같은 
빈티지 샵들 있는데, 5-15유로면 괜찮은 아이템 하나씩 건질 수 있어.

**저녁: 세느강변 산책 & 야경**
저녁은 무리하지 말고 숙소 근처 비스트로에서 가볍게. 
마레 지구의 Le Petit Cler(루 클레르 29)는 에펠탑에서 10분 거리라 위치도 좋고, 
파리지앵 분위기 나는 곳이야. 스테이크 프리츠(22유로) 추천. 
저녁 먹고 세느강변 20분 산책하고 들어가면 딱 좋은 첫날 마무리야.
                        """.strip(),
                        "spots": ["Place des Vosges", "Rue des Rosiers", "Seine River Walk"],
                        "restaurants": ["L'As du Fallafel (점심)", "Le Petit Cler (저녁)"],
                    },
                    {
                        "day": 2,
                        "title": "에펠탑 & 생제륧망 데프레",
                        "theme": "클로식 파리의 정석",
                        "content": """
오늘은 파리의 상징, 에펠탑부터 시작하는 클래식 코스야. 
하지만 무턱대고 가지 말고, 전략적으로 접근해야 해.

**오전: 에펠탑 (8:30 출발 필수!)**
에펠탑은 무조건 8:30-9:00 사이에 도착해야 줄 안 서고 올라갈 수 있어. 
 Champ de Mars 공원 쪽에서 접근하면 사진 찍기 좋은 스팟 여러 개 있어. 
 정상까지 엘리베이터 타고 올라가면 25유로, 2층까지만이면 16유로야.
 
**팁: 꼭 2층까지만 가도 충분해.** 정상은 안개 끼면 아무것도 안 보이고, 
2층 뷰가 오히려 파리 시내가 더 잘 보여. 사진도 2층이 더 예쁘게 나와.

**점심: 생제륧망 데프레 카페**
에펠탑에서 메트로 4호선 타고 생제륧망 데프레역 남으면 15분이야. 
Café de Flore(불바르 생제륧망 172)는 역사적인 카페라 가볍게 커피 한 잔(6유로) 하기 좋아. 
사르트르와 복파르가 단골이었던 곳이야. 크루아상(4유로)도 괜찮고.

**오후: 룩셈부르크 공원 & 라틴 지구**
카페에서 10분 걸으면 룩셈부르크 공원이야. 현지인들이 가장 좋아하는 공원 중 하나로, 
의자에 앉아서 책 읽거나 멍 때리는 사람들 볼 수 있어. 1시간 정도 느긋하게 쉬다가 
라틴 지구(Saint-Michel역 주변)로 넘어가자.

**저녁: 몽파륜나스 비스트로**
저녁은 몽파륜나스 근처 Le Comptoir du Relais(까르티에 드 롬 9). 
현지인들이 진짜 많이 가는 곳이라 웨이팅 있을 수 있는데, 7시 반 전에 가면 괜찮아. 
까수레(소시지와 콩 스튜, 18유로)가 시그니처야. 파리지앵 로컬 분위기 제대로 느낄 수 있어.
                        """.strip(),
                        "spots": ["Eiffel Tower", "Café de Flore", "Jardin du Luxembourg", "Latin Quarter"],
                        "restaurants": ["Café de Flore (브런치)", "Le Comptoir du Relais (저녁)"],
                    },
                    {
                        "day": 3,
                        "title": "루브르 & 마레 심층 탐방",
                        "theme": "예술과 감성",
                        "content": """
오늘은 파리의 예술 심장부를 들여다보는 날이야. 
루브르는 정말 하루 종일 봐도 모자란 곳이지만, 핵심만 쏙쏙 골라보자.

**오전: 루브르 박물관 (9:00 오픈런)**
루브르는 미리 온라인 예매(17유로) 필수야. 현장 구매하면 줄이 어마어마하게 길어. 
입구는 지하 쇼핑센터 Carousel du Louvre에서 들어가는 게 제일 빨라.

**꼭 봐야 할 3가지만:**
1. 모나리자 (Denon Wing 1층) - 사람 엄청 많지만 한 번은 봐야 해
2. 미로의 비너스 (Sully Wing)
3. 승리의 여신 (Denon Wing)

이거만 봐도 2시간. 나머지는 발길 닿는 대로 천천히 구경하자. 
12시쯤 박물관 안에 있는 카페에서 가볍게 점심(15유로 정도) 먹어도 좋아.

**오후: 마레 재방문 & 생트 샤펠**
루브르에서 15분 걸으면 생트 샤펠(Sainte-Chapelle)이야. 
이건 진짜 숨겨진 보석 같은 곳인데, 스테인드글라스 창문이 장난 아니야. 
입장료 11.5유로인데 값어치 충분히 해.

**저녁: Chez Janou (프로방스 요리)**
마레 지구의 Chez Janou(루 드 로ジ에 2)는 프로방스풍 레스토랑이야. 
저녁 7시 반쯤 가면 좋고, 초콜릿 무스가 진짜 유명해. 
코스로 먹으면 35-40유로 정도. 분위기가 너무 좋아서 데이트하기에도, 
친구들이랑 가기에도 딱이야.
                        """.strip(),
                        "spots": ["Louvre Museum", "Sainte-Chapelle", "Marais District"],
                        "restaurants": ["Louvre Café (점심)", "Chez Janou (저녁)"],
                    },
                    {
                        "day": 4,
                        "title": "몽마르트 & 루브르 주변",
                        "theme": "파리의 영혼을 느끼다",
                        "content": """
오늘은 파리에서 가장 예술적이고 로맨틱한 동네, 몽마르트를 탐험하는 날이야. 
여긴 정말 다른 파리야. 관광지 느낌 있지만 현지 예술가들의 영혼이 살아있는 곳이거든.

**오전: 몽마르트 언덕 일출 (선택)**
일찍 일어날 수 있다면, 몽마르트 언덕에서 일출 보는 거 강력 추천해. 
지하철 12호선 Abbesses역 내려서 10분 올라가면 Sacré-Cœur 성당 나와. 
오전 7-8시면 관광객 없이 한적하게 사진 찍을 수 있어.

**점심: 몽마르트 비스트로**
Place du Tertre 광장 주변의 작은 비스트로에서 점심. 
여기가 관광지라 가격이 좀 비싼데(25-30유로), 분위기를 위해 한 번쯤은 괜찮아. 
아니면 성당 뒤편으로 내려가면 더 로컬적인 식당들 많아.

**오후: 에펠탑 야경 (Retry)**
첫날 에펠탑 낮에 갔다면, 오늘 저녁에 다시 한 번 야경으로 가보자. 
Trocadéro 광장(에펠탑 건너편)에서 보는 야경이 진짜 예술이야. 
해질 녘(8-9시)에 가서 낮→밤 변하는 거 지켜보면 10분마다 반짝이는 조명쇼도 볼 수 있어.

**저녁: Septime (미슐랭 스타)**
오늘은 특별한 저녁으로 미슐랭 스타 Septime(루 드 샤론 80) 가보자. 
예약이 극악이긴 한데,运好면 당일 웨이팅도 가능해. 
테이스팅 메뉴 90-120유로로 파리 미슐랭 중에서는 가성비 괜찮은 편이야. 
진짜 예약 못 잡았다면 대안으로 Breizh Café에서 저녁(크레페 특화, 25유로)도 좋아.
                        """.strip(),
                        "spots": ["Sacré-Cœur", "Place du Tertre", "Trocadéro", "Eiffel Tower Night View"],
                        "restaurants": ["Montmartre Bistro (점심)", "Septime or Breizh Café (저녁)"],
                    },
                    {
                        "day": 5,
                        "title": "베르사유 or 자유일정 & 작별",
                        "theme": "마무리와 쇼핑",
                        "content": """
마지막 날. 짐 챙기기 전에 가볍게 마무리하는 날이야.

**오전: 베르사유 궁전 (선택) or 생략**
베르사유 가려면 반나절은 꼭 잡아야 해. RER C선 타고 40분이면 가고, 
입장료 20유로. 정원까지 포함하면 27유로. 
근데 5일 일정이면 베르사유는 조금 무리일 수 있어. 
대신 샹젤리제 거리나 갤러리 라파예트에서 쇼핑하는 게 더 현실적일 거야.

**점심: 보욘 샤르티에**
마지막 점심은 보욘 샤르티에(루 드 몽마르트 7)에서 파리 전통 음식으로 마무리하자. 
1900년대 초부터 영업 중인 곳이라 내부도 클래식하고, 에스카르고(달팽이, 12유로)나 
코코뱅(닭볶음탕 비슷, 15유로) 추천. 가격도 착해서 20-25유로면 배불리 먹을 수 있어.

**오후: 마레 재방문 or 갤러리 라파예트**
남은 시간은 마레 지구의 빈티지 샵들 마저 구경하거나, 
갤러리 라파예트(오스만점) 백화점 옥상 테라스(무료)에서 파리 시내 전망 보는 걸로 마무리하자. 
여기 옥상도 에펠탑이랑 오페라하우스 뷰 예쁘게 나와.

**저녁: 공항 이동**
샤를 드 골 공항 가려면 시내에서 RER B선으로 40-50분 걸리니까, 
비행기 시간 3시간 전에는 출발하는 게 안전해. 
공항에서 세금 환급(Tax Refund) 하려면 1시간 더 일찍 가야 해.

**마무리 인사:**
5일간의 파리 여행, 어땠어? 나도 이 글 쓰면서 다시 가고 싶어졌네. 
파리는 무리하게 보겠다고 하면 오히려 피곤하기만 한 도시야. 
하루 2-3개 스팟, 여유롭게 걷고, 카페에서 멍 때리는 시간도 꼭 포함시켜야 
진짜 파리를 느낄 수 있어. 다음에 또 다른 도시에서 만나자! 🥐✨
                        """.strip(),
                        "spots": ["Bouillon Chartier", "Galeries Lafayette Rooftop", "Charles de Gaulle Airport"],
                        "restaurants": ["Bouillon Chartier (점심)"],
                    },
                ],
                
                "restaurants_detail": {
                    "budget": [
                        {
                            "name": "L'As du Fallafel",
                            "address": "34 Rue des Rosiers, 75004 Paris",
                            "metro": "Saint-Paul (Line 1)",
                            "price": "€ (8-12€)",
                            "signature": "팔라펠 샌드위치",
                            "description": "마레 지구의 레전드길거리 음식. 줄이 항상 있지만 10분이면 들어간다. 중동식 샌드위치에 피클과 소스가 듬뿍.",
                            "tip": "테이크아웃해서 근처 Place des Vosges에서 먹으면 그게 100점 만점의 점심",
                        },
                        {
                            "name": "Breizh Café",
                            "address": "109 Rue Vieille du Temple, 75003 Paris",
                            "metro": "Saint-Sébastien - Froissart (Line 8)",
                            "price": "€ (12-20€)",
                            "signature": "갈렛(메밀크레페)",
                            "description": "정통 브르타뉴 갈렛과 크레페 전문점. 고소한 버터와 계란, 구운 햄이 어우러진 갈렛 컴플렛이 시그니처.",
                            "tip": "저녁에는 예약 필수지만, 점심은 웨이팅 가능. 사이더와 함께 먹으면 브르타뉴 정취 제대로",
                        },
                        {
                            "name": "Bouillon Chartier",
                            "address": "7 Rue du Faubourg Montmartre, 75009 Paris",
                            "metro": "Grands Boulevards (Line 8,9)",
                            "price": "€ (15-25€)",
                            "signature": "전통 프렌치 브라세리",
                            "description": "1896년부터 영업 중인 파리의 역사. 높은 천장과 거울, 빈티지 인테리어가 그대로 보존되어 있음. 에스카르고와 코코뱅 추천.",
                            "tip": "내부가 엄청 넓지만 저녁은 웨이팅 있을 수 있음. 오후 6시 전에 가는 게 좋아",
                        },
                    ],
                    "mid_range": [
                        {
                            "name": "Café de Flore",
                            "address": "172 Boulevard Saint-Germain, 75006 Paris",
                            "metro": "Saint-Germain-des-Prés (Line 4)",
                            "price": "€€ (20-35€)",
                            "signature": "크루아상, 오믈렛",
                            "description": "파리에서 가장 유명한 문학 카페. 사르트르와 보부아르가 단골이었던 곳. 비싸지만 한 번쯤은 가볼 만한 가치가 있어.",
                            "tip": "아침 9-10시가 한적하고 분위기 좋음. 테라스 자리가 인기 많아",
                        },
                        {
                            "name": "Le Comptoir du Relais",
                            "address": "9 Carrefour de l'Odéon, 75006 Paris",
                            "metro": "Odéon (Line 4,10)",
                            "price": "€€ (25-40€)",
                            "signature": "까수레(소시지 콩 스튜)",
                            "description": "몽파륜나스의 현지인 맛집. 예약 없이는 거의 못 들어가지만,运好면 바에 앉을 수도 있어. 정통 비스트로 요리가 일품.",
                            "tip": "저녁은 웨이팅 30분-1시간 각오. 오후 7시 전 도착 추천",
                        },
                        {
                            "name": "Le Petit Cler",
                            "address": "29 Rue Cler, 75007 Paris",
                            "metro": "École Militaire (Line 8)",
                            "price": "€€ (22-35€)",
                            "signature": "스테이크 프리츠",
                            "description": "에펠탑에서 10분 거리의 아늑한 동네 비스트로. Rue Cler 시장 근처라 구경하기도 좋고, 가격도 합리적.",
                            "tip": "저녁에 에펠탑 야경 보기 전에 들르기 딱 좋은 위치",
                        },
                        {
                            "name": "Chez Janou",
                            "address": "2 Rue Roger Verlomme, 75003 Paris",
                            "metro": "Saint-Sébastien - Froissart (Line 8)",
                            "price": "€€ (30-45€)",
                            "signature": "초콜릿 무스, 프로방스 요리",
                            "description": "마레 지구의 프로방스풍 레스토랑. 벽에 걸린 수백 개의 파스텔 색상 파스텔이 인상적. 초콜릿 무스가 전설적.",
                            "tip": "디저트로 초콜릿 무스 꼭 주문! 코스로 먹으면 40€ 선",
                        },
                    ],
                    "fine_dining": [
                        {
                            "name": "Septime",
                            "address": "80 Rue de Charonne, 75011 Paris",
                            "metro": "Charonne (Line 9)",
                            "price": "€€€ (90-120€)",
                            "signature": "모던 프렌치 테이스팅",
                            "description": "파리에서 가장 예약하기 어려운 레스토랑 중 하나. 미슐랭 1성. 시즌별 로컬 식재료를 사용한 창의적인 요리가 특징.",
                            "tip": "예약은 월요일 오전 10시(프랑스 시간) 홈페이지 오픈런. 당일 웨이팅도 가능하긴 함",
                        },
                        {
                            "name": "Le Cinq",
                            "address": "31 Avenue George V, 75008 Paris",
                            "metro": "George V (Line 1)",
                            "price": "€€€€ (350-500€)",
                            "signature": "미슐랭 3성 럭셔리",
                            "description": "포시즌스 호텔 조지 5세 내의 3 미슐랭 스타 레스토랑. 크리스찬 르 스케르가 이끄는 파리 정상의 다이닝.",
                            "tip": "드레스 코드 있음(스마트 캐주얼 이상). 예약은 최소 한 달 전 필수",
                        },
                        {
                            "name": "L'Ambroisie",
                            "address": "9 Place des Vosges, 75004 Paris",
                            "metro": "Saint-Paul (Line 1)",
                            "price": "€€€€ (300-450€)",
                            "signature": "클래식 프렌치 가스트로노미",
                            "description": "Place des Vosges 광장에 위치한 전설적인 3 미슐랭 스타. 1986년부터 미슐랭 3성을 유지 중인 클래식 프렌치의 정수.",
                            "tip": "고전적인 프렌치 다이닝을 원한다면 최고의 선택. 분위기도 우아함",
                        },
                    ],
                },
                
                "tips": [
                    {
                        "category": "교통",
                        "icon": "🚇",
                        "content": "파리 지하철은 1-2권역만으로도 주요 관광지 다 커버됨. Navigo Weekly Pass(주간권, 30€)가 여러 번 이동하면 이득. 택시는 Uber보다 Bolt가 더 저렴."
                    },
                    {
                        "category": "주차",
                        "icon": "🅿️",
                        "content": "파리 시내 주차는 시간당 4-6€로 비쌈. 렌트카는 외곽 P+R 주차장(지하철 환승 주차, 하루 10-15€) 활용하거나, 아예 렌트하지 않는 게 낫다."
                    },
                    {
                        "category": "세금환급",
                        "icon": "💶",
                        "content": "100€ 이상 구매 시 세금 환급(Tax Free) 가능. 결제할 때 여권 제시하고 Tax Free Form 받기. 공항에서 스캔하고 환급은 현금/카드 선택 가능."
                    },
                    {
                        "category": "예약",
                        "icon": "📅",
                        "content": "루브르, 에펠탑, 미슐랭 레스토랑은 미리 예약 필수. 특히 Septime 같은 인기 맛집은 월요일 오픈런으로 예약 잡아야 함."
                    },
                    {
                        "category": "식당",
                        "icon": "🍽️",
                        "content": "파리 식당은 12-14시(점심), 19:30-22:30(저녁) 영업. 그 사이 시간대에는 거의 문 닫음. 늦은 저녁은 21시 전에 가는 게 안전."
                    },
                    {
                        "category": "안전",
                        "icon": "⚠️",
                        "content": "관광지 주변 소매치기 주의. 특히 루브르, 에펠탑, 몽마르트. 가방은 항상 앞으로 메고, 귀중품은 숙소 세이프박스에."
                    },
                ],
                
                "conclusion": """
파리는 누구에게나 꿈의 여행지야. 하지만 무리한 일정은 오히려 그 꿈을 깨버릴 수도 있어. 
하루에 2-3개 스팟만 제대로 보고, 나머지 시간은 카페에서 느긋하게 보내는 게 진짜 파리 여행의 정석이야.

이 가이드가 너의 파리 여행에 조금이나마 도움이 되었으면 좋겠어. 
궁금한 점 있으면 언제든 댓글로 물어봐. 다음 여행지에서 또 만나자! 🗼✨
                """.strip(),
            },
        }
    
    def generate_blog_content(self, city: str, days: int = 5) -> Optional[Dict]:
        """풍부한 블로그 콘텐츠 생성"""
        if city not in self.cities_db:
            logger.warning(f"City {city} not in database")
            return None
        
        data = self.cities_db[city]
        
        return {
            "title": f"{city} 여행 완벽 가이드 | {days}일 일정 with 현지 맛집 10선",
            "destination": {
                "name": city,
                "country": data.get("country", "France"),
                "nickname": data.get("nickname", ""),
                "best_season": data.get("best_season", ""),
                "currency": data.get("currency", ""),
                "flight_time": data.get("flight_time", ""),
                "days": days,
            },
            "intro": data.get("intro", ""),
            "itinerary": data.get("days_plan", []),
            "restaurants": data.get("restaurants_detail", {}),
            "tips": data.get("tips", []),
            "conclusion": data.get("conclusion", ""),
            "generated_at": datetime.now().isoformat(),
        }


# 인스턴스 생성
rich_generator = RichContentGenerator()
