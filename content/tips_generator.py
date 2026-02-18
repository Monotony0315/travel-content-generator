"""Travel tips with practical driving/parking guidance."""

from __future__ import annotations

from typing import Dict
from loguru import logger
import urllib.parse


class TipsGenerator:
    async def generate(self, city: str, country: str, currency: str, language: str) -> Dict:
        logger.info(f"Generating travel tips for {city}...")
        return {
            "voice": f"아래 팁은 '여행자 입장에서 바로 써먹는 정보' 중심으로 정리했어. 과장 없이 현실적으로 구성했어.",
            "transportation": {
                "city_transport": "중심지 숙소 + 도보 + 대중교통 조합이 가장 효율적",
                "car_rental": "외곽/근교까지 볼 계획이면 2~3일만 렌트하는 방식이 비용 효율적",
            },
            "driving_and_parking": {
                "parking_strategy": "도심은 민영보다 공영주차장이 가격/안정성에서 유리한 편",
                "maps_parking": f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(city + ' public parking')}",
                "maps_rental": f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(city + ' car rental')}",
            },
            "money": {
                "currency": currency,
                "budget": "중급 기준 1일 15~25만원 선으로 계획하면 무난",
            },
            "communication": {
                "language": language,
                "tip": "영어가 통하는 지역이더라도 번역 앱 오프라인 패키지는 꼭 받아두는 걸 추천",
            },
            "safety": {
                "tips": [
                    "관광지 주변 소매치기 대비해서 가방은 앞으로 메기",
                    "야간 이동은 큰 길 위주",
                    "여권 원본은 숙소 보관 + 사본 휴대",
                ]
            },
        }
