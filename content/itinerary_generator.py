"""Conversational itinerary generator with map links."""

from __future__ import annotations

from typing import Dict, List
from loguru import logger
import urllib.parse


CITY_SPOTS = {
    "Paris": {
        "spots": ["에펠탑", "루브르 박물관", "몽마르트 언덕", "샹젤리제 거리", "세느강 크루즈", "오르세 미술관", "생트 샤펠", "팡테온"],
        "areas": ["마레 지구", "라틴 지구", "생제륧망데프레", "몽파륜나스"],
        "intro": "파리는 크게 세 구역(1~7구역 핵심지, 4~6구역 감성지, 8구역 번화가)으로 나눠서 봐야 해. 동선 잘못 잡으면 지하철 타고 헤매게 되니까 이틀 단위로 구역을 묶어서 돌아보는 걸 추천해."
    },
    "Rome": {
        "spots": ["콜로세움", "바티칸 박물관", "트레비 분수", "판테온", "스페인 계단", "포로 로마노", "나복나 광장", "산탄젤로 성"],
        "areas": ["트라스테베레", "몬티", " campo de fiori", "나복나"],
        "intro": "로마는 역사적 중심지가 워낙 커서 반드시 도보 중심으로 계획해야 해. 고대 유적지와 바로크 양식 교회들이 섞여 있어서 하루에 한 구역씩 천천히 보는 게 낫고, 바티칸은 반나절을 꼭 배정해야 해."
    },
    "Tokyo": {
        "spots": ["시부야 스크램블", "아사쿠사 센소지", "하라주쿠", "시부야 스카이", "도쿄 타워", "메이지 신궁", "우에노 공원", "도쿄역"],
        "areas": ["신주쿠", "시부야", "아사쿠사", "긴자", "하라주쿠"],
        "intro": "도쿄는 요요선(山手線) 기준으로 동선을 짜면 제일 편해. 동쪽(아사쿠사/우에노), 중심(시부야/신주쿠), 서쪽(하라주쿠/시부야)으로 나눠서 하루씩 보는 게 지하철 환승 스트레스 없이 깔끔해."
    },
    "Barcelona": {
        "spots": ["사그라다 파밀리아", "구엘 공원", "까사 바트요", "까사 밀라", "고딕 지구", "보케리아 시장", "몬주익", "바르셀로네타 항구"],
        "areas": ["고딕 쿼터", "엘 보른", "그라시아", "에샴플"],
        "intro": "바르셀로나는 가우디 건축물과 구시가지가 핵심이야. 가우디 투어(사그라다 파밀리아-까사 밀라-구엘 공원)는 하루에 몰아보고, 고딕 지구와 보케리아 시장은 따로 반나절 잡아야 해."
    },
    "Sydney": {
        "spots": ["오페라하우스", "하버 브리지", "본다이 비치", "타롱가 동물원", "록스", "서큘러 키", "블루 마운틴", "왓슨스 베이"],
        "areas": ["서큘러 키", "더 록스", "본다이", "뉴타운", "달링 하버"],
        "intro": "시드니는 하버(항구) 중심 시내와 항핀(본다이)으로 크게 나뉘어. 첫날은 오페라하우스-하버 브리지-록스를 도보로 돌고, 이튿날은 버스로 본다이 비치 가는 게 표준 동선이야."
    },
    "New York": {
        "spots": ["타임스 스퀘어", "센트럴 파크", "엠파이어 스테이트", "자유의 여신상", "브루클린 브리지", "메트로폴리탄 미술관", "원 월드 트레이드", "고 LINE"],
        "areas": ["맨해튼 미드타운", "소호", "그리니치 빌리지", "브루클린"],
        "intro": "뉴욕은 맨해튼(미드타운-다운타운-업타운)으로 세 구역 나눠서 보는 게 좋아. 지하철이 24시간이라 밤에도 이동 가능하긴 한데, 구역별로 하루씩 묶어서 보는 게 지침 없이 즐기는 방법이야."
    },
    "London": {
        "spots": ["빅벤", "런던아이", "대영박물관", "타워브리지", "버킹엄 궁전", "내셔널 갤러리", "코번트 가든", "세인트 폴 대성당"],
        "areas": ["웨스트민스터", "시티", "소호", "노팅힐", "사우스뱅크"],
        "intro": "런던은 테임즈강 기준으로 남북이 완전히 달라. 북쪽(웨스트민스터-소호)이 관광핵심지고, 남쪽(사우스뱅크)은 문화시설 위주야. 지하철 zone 1~2만으로도 충분히 돌아볼 수 있어."
    },
    "Bangkok": {
        "spots": ["왓 아룬", "왕궁", "와트 포", "짜뚜짝 시장", "카오산 로드", "센트럴월드", "짜뚜짝 주말시장", "아이콘시암"],
        "areas": ["올드시티(끄룽텝)", "실롬", "수쿰빗", "차이나타운"],
        "intro": "방콕은 강(짜오프라야강) 기준으로 동서로 나뉘는데, 동쪽이 번화가(실롬/수쿰빗), 서쪽이 사원/궁궐(올드시티)이야. 보트(강)를 이용하면 교통체증 피하고 빠르게 이동할 수 있어."
    },
    "Singapore": {
        "spots": ["마리나베이 샌즈", "가든스바이더베이", "센토사", "유니버설 스튜디오", "차이나타운", "리틀 인디아", "클록 키", "오차드 로드"],
        "areas": ["마리나베이", "차이나타운", "클록 키", "보탁"],
        "intro": "싱가포르는 MRT(지하철)로 거의 모든 관광지를 커버할 수 있어. 마리나베이(랜드마크)와 차이나타운/리틀인디아(문화)를 하루씩, 센토사는 따로 하루 잡는 게 무난해."
    },
    "Vancouver": {
        "spots": ["스탠리 파크", "그랜빌 아일랜드", "캐필라노 서스펜션 브리지", "가스타운", "그라우스 마운틴", "리치몬드 나이트 마켓", "영 앤드 어버딘"],
        "areas": ["다운타운", "그랜빌 아일랜드", "리치몬드", "노스밴쿠버"],
        "intro": "밴쿠버는 다운타운(스탠리파크-가스타운)이 도보로 돌 수 있을 정도로 컴팩트해. 자연(캐필라노, 그라우스)은 차 렌트해서 반나절씩 다녀오는 게 좋고, 리치몬드는 아시아 음식 투어로 따로 가면 좋아."
    }
}


class ItineraryGenerator:
    def __init__(self):
        self.templates = {
            "classic": self._plan,
            "romantic": self._plan,
            "foodie": self._plan,
            "adventure": self._plan,
            "luxury": self._plan,
            "budget": self._plan,
        }

    async def generate(self, city: str, country: str, days: int = 5, style: str = "classic") -> Dict:
        logger.info(f"Generating {days}-day itinerary for {city}...")
        
        city_data = CITY_SPOTS.get(city, {
            "spots": [f"{city} 핵심 명소", f"{city} 대표 랜드마크", f"{city} 인기 관광지"],
            "areas": [f"{city} 구시가지", f"{city} 중심가", f"{city} 신시가지"],
            "intro": f"이번 {city} 코스는 실제로 다녀왔다고 과장하지 않고, 처음 가는 여행자 입장에서 동선이 꼬이지 않게 짠 일정이야. {city}의 핵심 스팟을 무리 없이 즐길 수 있게 구성했어."
        })
        
        return {
            "city": city,
            "country": country,
            "days": days,
            "style": style,
            "intro": city_data["intro"],
            "days_plan": self._plan(city, country, days, city_data),
        }

    def _maps(self, q: str) -> str:
        return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(q)}"

    def _plan(self, city: str, country: str, days: int, city_data: Dict) -> List[Dict]:
        spots = city_data["spots"]
        areas = city_data["areas"]
        
        narratives = [
            "도착 첫날은 숙소 근처 중심지를 가볍게 돌면서 동네 감을 잡는 게 중요해. 무리하게 먼 곳 가면 체력 방전되니까 첫날은 가까운 스팟 위주로.",
            "본격적으로 핵심 랜드마크 돌아보는 날이야. 오전 일찍 가면 사람 적고 사진도 편하게 찍을 수 있어. 오후는 실내로 들어가서 쉬엄쉬엄.",
            "이제 좀 벗어나서 로컬 동네나 시장 같은 곳을 봐야 해. 관광지보다는 실제 현지인들 사는 분위기 느낄 수 있는 코스로 잡았어.",
            "자유 일정으로 쇼핑하거나 빠진 곳 채우거나, 아니면 그냥 카페에서 늦잠 자도 돼. 여행 중 하루는 여유롭게 보내는 게 장기전에 도움이야.",
            "마지막 날은 짐 챙기기 전에 가볍게 근처 산책하고, 기념품 사고, 맛있는 걸로 마무리하면 딱 좋아. 공항 갈 시간만 잘 계산하면 돼."
        ]
        
        plans = []
        for d in range(1, days + 1):
            spot_idx = (d - 1) % len(spots)
            area_idx = (d - 1) % len(areas)
            
            morning_spot = spots[spot_idx]
            afternoon_spot = spots[(spot_idx + 1) % len(spots)] if len(spots) > 1 else spots[spot_idx]
            evening_area = areas[area_idx]
            
            narrative = narratives[min(d - 1, len(narratives) - 1)]
            
            plans.append(
                {
                    "day": d,
                    "theme": f"{city} Day {d}",
                    "narrative": narrative,
                    "morning": {
                        "activity": f"오전에는 {morning_spot}부터 시작해서 분위기 잡아가 보자.",
                        "spot": morning_spot,
                        "google_maps": self._maps(f"{morning_spot} {city}"),
                    },
                    "afternoon": {
                        "activity": f"오후에는 {afternoon_spot} 쪽으로 이동해서 천천히 러봐.",
                        "spot": afternoon_spot,
                        "google_maps": self._maps(f"{afternoon_spot} {city}"),
                    },
                    "evening": {
                        "activity": f"저녁에는 {evening_area} 쪽에서 저녁 먹고 산책하며 하루 마무리.",
                        "spot": evening_area,
                        "google_maps": self._maps(f"{evening_area} {city}"),
                    },
                    "parking": {
                        "tip": "렌트카 이용 시 구글맵 '공영주차장' 검색해서 미리 위치 체크해두는 게 좋아. 도심은 주차비 비싸니까 P&R(환승주차장) 활용 추천.",
                        "google_maps": self._maps(f"{city} 공영주차장"),
                    },
                }
            )
        return plans
