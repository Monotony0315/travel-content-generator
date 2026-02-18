"""
Generate Enhanced Rich Travel Blog - Daily Automation
최종 버전 - 통계 기반 일정 + 호텔 + 비용 + 인라인 링크 + 도시 자동 순환 + 여행 블로그 링크
"""

import asyncio
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from content.enhanced_generator import enhanced_generator
from content.enhanced_image_fetcher import enhanced_image_fetcher
from notion.fixed_publisher import FixedNotionPublisher
from city_rotator import get_next_city, get_city_by_name
from loguru import logger


async def generate_enhanced_blog(city_name: str = None):
    """최종 버전 블로그 생성 - 도시 자동 순환"""
    
    # 도시가 지정되지 않으면 순환에서 다음 도시 가져오기
    if city_name is None:
        city_info = get_next_city()
        logger.info(f"Auto-selected city from rotation: {city_info['name']} ({city_info['country']})")
    else:
        city_info = get_city_by_name(city_name)
        if city_info is None:
            logger.error(f"City {city_name} not found in database")
            return None
        logger.info(f"Using specified city: {city_info['name']}")
    
    city = city_info['name']
    country = city_info.get('country', '')
    blog_links = city_info.get('blog_links', [])
    
    logger.info(f"Starting ENHANCED blog generation for {city}")
    
    # Generate enhanced content
    logger.info("Generating enhanced content with hotels, costs, statistics...")
    content = enhanced_generator.generate_enhanced_blog(city, days=5)
    
    if not content:
        logger.error(f"Failed to generate content for {city}")
        return None
    
    # Add blog links to content
    content['blog_links'] = blog_links
    content['city_info'] = city_info
    
    logger.info(f"Content generated: {content['title']}")
    
    # Fetch more images for daily sections (hero + 5 days = 6 images)
    # 일정별 테마에 맞는 이미지 가져오기
    logger.info("Fetching images with day-specific themes (Unsplash API priority)...")
    days_plan = content.get('days_plan', [])
    images = enhanced_image_fetcher.get_city_images(
        city=city, 
        country=country,
        days_plan=days_plan,
        count=6
    )
    logger.info(f"Fetched {len(images)} images")
    
    # Publish to Notion
    logger.info("Publishing to Notion with inline links...")
    publisher = FixedNotionPublisher()
    
    if not publisher.enabled:
        logger.error("Notion publisher not enabled")
        return None
    
    try:
        page_url = await publisher.publish_blog(content, images)
        logger.info(f"Published successfully!")
        logger.info(f"URL: {page_url}")
        return page_url
    except Exception as e:
        logger.error(f"Failed to publish: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate travel blog for a city")
    parser.add_argument("--city", type=str, help="City name (default: auto-rotate)")
    args = parser.parse_args()
    
    city = args.city if args.city else None
    url = asyncio.run(generate_enhanced_blog(city))
    
    if url:
        print("\n" + "="*70)
        print("ENHANCED TRAVEL BLOG GENERATED SUCCESSFULLY!")
        print("="*70)
        print(f"URL: {url}")
        print("="*70)
    else:
        print("\nFailed to generate blog")
        sys.exit(1)
