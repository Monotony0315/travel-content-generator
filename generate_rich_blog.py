"""
Generate Enhanced Rich Travel Blog
최종 버전 - 통계 기반 일정 + 호텔 + 비용 + 인라인 링크
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from content.enhanced_generator import enhanced_generator
from content.image_fetcher import image_fetcher
from notion.fixed_publisher import FixedNotionPublisher
from loguru import logger


async def generate_enhanced_blog(city: str = "Paris"):
    """최종 버전 블로그 생성"""
    
    logger.info(f"Starting ENHANCED blog generation for {city}")
    
    # Generate enhanced content
    logger.info("Generating enhanced content with hotels, costs, statistics...")
    content = enhanced_generator.generate_enhanced_blog(city, days=5)
    
    if not content:
        logger.error(f"Failed to generate content for {city}")
        return None
    
    logger.info(f"Content generated: {content['title']}")
    
    # Fetch more images for daily sections (hero + 5 days = 6 images)
    logger.info("Fetching Unsplash images for hero + daily sections...")
    images = image_fetcher.get_city_images(city, count=6)
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
    url = asyncio.run(generate_enhanced_blog("Paris"))
    
    if url:
        print("\n" + "="*70)
        print("ENHANCED TRAVEL BLOG GENERATED SUCCESSFULLY!")
        print("="*70)
        print(f"URL: {url}")
        print("="*70)
    else:
        print("\nFailed to generate blog")
        sys.exit(1)
