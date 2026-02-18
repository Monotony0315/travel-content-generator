"""
Settings
환경 설정
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Notion 설정
NOTION_API_KEY = os.getenv('NOTION_API_KEY', '')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID', '')

# OpenAI 설정 (콘텐츠 생성용)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# 프로젝트 설정
PROJECT_NAME = "Travel Content Generator"
VERSION = "1.0.0"

# 콘텐츠 설정
CONTENT_CONFIG = {
    'daily_destination': True,  # 매일 1개 도시
    'publish_time': '09:00',    # 발행 시간
    'timezone': 'Asia/Seoul',
    'default_days': 5,          # 기본 일정 일수
    'supported_styles': [
        'classic',      # 클래식
        'romantic',     # 로맨틱
        'foodie',       # 미식
        'adventure',    # 어드벤처
        'luxury',       # 럭셔리
        'budget'        # 가성비
    ]
}

# 지역별 설정
REGIONS = {
    'europe': {
        'name': '유럽',
        'currency': 'EUR',
        'count': 120
    },
    'asia': {
        'name': '아시아',
        'currency': 'KRW/JPY/CNY',
        'count': 100
    },
    'americas': {
        'name': '아메리카',
        'currency': 'USD',
        'count': 80
    },
    'oceania': {
        'name': '오세아니아',
        'currency': 'AUD/NZD',
        'count': 35
    },
    'africa': {
        'name': '아프리카',
        'currency': 'USD/EUR',
        'count': 20
    },
    'middle_east': {
        'name': '중동',
        'currency': 'USD',
        'count': 10
    }
}

# 총 여행지 수
TOTAL_DESTINATIONS = sum(r['count'] for r in REGIONS.values())  # 365개
