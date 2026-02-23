"""
Enhanced Rich Travel Blog Content Generator
MAJOR IMPROVEMENTS (2026-02-19):
- Rich daily itinerary with detailed time slot descriptions (3-4 paragraphs each)
- Reduced emoji usage (max 1-2 per section)
- Specific locations per day (no repetition)
- Booking links with prices
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger


class EnhancedRichGenerator:
    """Rich content generator with professional formatting"""
    
    def __init__(self):
        self.cities_db = self._load_cities_db()

    def _load_cities_db(self) -> Dict:
        """Load city database"""
        return {}  # Now using rich_city_generator for city data

    def generate_enhanced_blog(self, city: str, days: int = 5, region: str = "유럽") -> Optional[Dict]:
        """Generate rich blog content"""
        from content.rich_city_generator import rich_city_generator
        from city_rotator import get_city_by_name
        
        city_info = get_city_by_name(city)
        if not city_info:
            logger.error(f"City {city} not found")
            return None
        
        actual_region = city_info.get('region', region)
        country = city_info['country']
        
        # Use rich_city_generator for detailed content
        return rich_city_generator.generate_rich_content(city, country, actual_region, days)

    def _generate_seo_meta(self, city: str, country: str, days: int, region: str = "유럽") -> Dict:
        """SEO metadata"""
        base_keywords = [
            f"{city} 여행", f"{country} 여행", "해외여행", "여행 가이드",
            f"{city} 여행 코스", f"{city} 여행 일정", f"{city} 맛집",
            f"{city} 호텔", f"{city} 관광"
        ]
        
        hashtags = [
            f"#{city.replace(' ', '')}여행", f"#{country.replace(' ', '')}여행",
            "#해외여행", "#여행가이드", "#여행코스", "#여행일정",
            f"#{city.replace(' ', '')}맛집", f"#{city.replace(' ', '')}호텔",
        ]
        
        return {
            "keywords": base_keywords,
            "hashtags": list(set(hashtags)),
            "meta_description": f"{city} {days}일 여행 완벽 가이드. {country}의 매력적인 관광지, 맛집, 호텔 추천과 함께 최적의 여행 코스를 확인하세요.",
        }


# 인스턴스 생성
enhanced_generator = EnhancedRichGenerator()
