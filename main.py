"""
Travel Content Generator
여행 콘텐츠 자동 생성 시스템

매일 1개 도시의 여행 일정과 식당 정보를 자동 생성하여 Notion에 발행
"""

import os
import sys
import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from loguru import logger

# 프로젝트 경로 설정
sys.path.insert(0, str(Path(__file__).parent))

from data.destinations import DESTINATIONS
from content.itinerary_generator import ItineraryGenerator
from content.restaurant_finder import RestaurantFinder
from content.tips_generator import TipsGenerator
from content.reference_fetcher import ReferenceFetcher
from notion.publisher import NotionPublisher


class TravelContentGenerator:
    """여행 콘텐츠 생성기 메인 클래스"""
    
    def __init__(self):
        self.itinerary_gen = ItineraryGenerator()
        self.restaurant_finder = RestaurantFinder()
        self.tips_gen = TipsGenerator()
        self.refs = ReferenceFetcher()
        self.notion = NotionPublisher()
        
        logger.info("🌍 Travel Content Generator initialized")
    
    def select_destination(self, category: Optional[str] = None) -> Dict:
        """
        오늘의 여행지 선택
        
        Args:
            category: 'europe', 'asia', 'americas', 'oceania', None(랜덤)
        
        Returns:
            선택된 도시 정보
        """
        if category and category in DESTINATIONS:
            cities = DESTINATIONS[category]
        else:
            # 모든 카테고리에서 랜덤
            all_cities = []
            for cat_cities in DESTINATIONS.values():
                all_cities.extend(cat_cities)
            cities = all_cities
        
        # 랜덤 선택
        destination = random.choice(cities)
        
        logger.info(f"✈️ Selected destination: {destination['name']}, {destination['country']}")
        
        return destination
    
    async def generate_content(self, destination: Dict) -> Dict:
        """
        콘텐츠 생성
        
        Returns:
            {
                'destination': 도시 정보,
                'itinerary': 여행 일정,
                'restaurants': 식당 정보,
                'tips': 여행 팁,
                'budget': 예산 정보
            }
        """
        logger.info(f"📝 Generating content for {destination['name']}...")
        
        # 여행 일정 생성
        itinerary = await self.itinerary_gen.generate(
            city=destination['name'],
            country=destination['country'],
            days=destination.get('recommended_days', 5),
            style=destination.get('travel_style', 'classic')
        )
        
        # 식당 정보 생성
        restaurants = await self.restaurant_finder.find(
            city=destination['name'],
            country=destination['country'],
            cuisine=destination.get('cuisine', 'local')
        )
        
        # 여행 팁 생성
        tips = await self.tips_gen.generate(
            city=destination['name'],
            country=destination['country'],
            currency=destination.get('currency', 'USD'),
            language=destination.get('language', 'English')
        )
        
        references = {
            'photo': self.refs.get_photo(destination['name'], destination['country']),
            'blog_links': self.refs.get_blog_links(destination['name'], destination['country'])
        }

        return {
            'destination': destination,
            'itinerary': itinerary,
            'restaurants': restaurants,
            'tips': tips,
            'references': references,
            'generated_at': datetime.now().isoformat()
        }
    
    async def publish(self, content: Dict) -> str:
        """
        Notion에 발행
        
        Returns:
            발행된 페이지 URL
        """
        url = await self.notion.publish_travel_guide(content)
        
        logger.info(f"✅ Published to Notion: {url}")
        
        return url
    
    async def run_daily(self):
        """일일 실행"""
        print("="*70)
        print("🌍 Travel Content Generator - Daily Run")
        print("="*70)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        print()
        
        # 1. 여행지 선택
        destination = self.select_destination()
        
        # 2. 콘텐츠 생성
        content = await self.generate_content(destination)
        
        # 3. Notion 발행
        url = await self.publish(content)
        
        # 4. 결과 출력
        print("\n" + "="*70)
        print("✅ Content Generated Successfully!")
        print("="*70)
        print(f"Destination: {destination['name']}, {destination['country']}")
        print(f"Itinerary: {content['itinerary']['days']} days")
        print(f"Restaurants: {content['restaurants']['total']} places")
        print(f"Notion URL: {url}")
        print("="*70)
        
        return url


async def main():
    """메인 실행"""
    generator = TravelContentGenerator()
    
    # 일일 실행
    await generator.run_daily()


if __name__ == '__main__':
    asyncio.run(main())
