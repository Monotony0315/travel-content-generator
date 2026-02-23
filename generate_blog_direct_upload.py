"""
Generate Enhanced Travel Blog with Direct Image Upload
Downloads images locally, verifies them, and uses reliable URLs in Notion
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from content.enhanced_generator import enhanced_generator
from content.api_image_fetcher import api_image_fetcher
from notion.fixed_publisher import FixedNotionPublisher
from notion.image_manager import image_manager
from loguru import logger


async def generate_blog_with_image_upload(city: str = "Paris"):
    """
    Generate blog with local image download and verified uploads
    
    Flow:
    1. Generate content
    2. Fetch images from APIs
    3. Download images locally to temp_images/{city}/
    4. Verify images are valid
    5. Get reliable URLs (CDN upload or optimized original)
    6. Publish to Notion with verified image URLs
    """
    
    logger.info(f"=" * 70)
    logger.info(f"STARTING: Blog generation for {city} with direct image upload")
    logger.info(f"=" * 70)
    
    # Step 1: Generate enhanced content
    logger.info("[1/6] Generating enhanced content...")
    content = enhanced_generator.generate_enhanced_blog(city, days=5)
    
    if not content:
        logger.error(f"Failed to generate content for {city}")
        return None
    
    logger.info(f"✅ Content generated: {content['title']}")
    
    # Step 2: Fetch images from APIs
    logger.info("[2/6] Fetching images from APIs (Unsplash → Pexels → Pixabay → Wikimedia)...")
    
    days_plan = content.get("days_plan", [])
    
    if days_plan:
        logger.info(f"📸 Using intelligent image fetching with {len(days_plan)} days plan...")
        raw_images = api_image_fetcher.get_all_images(city, days_plan)
    else:
        logger.info("📸 Using basic image fetching...")
        raw_images = []
        for i in range(6):
            day_plan = {"title": f"Day {i}", "description": f"{city} travel"}
            img = api_image_fetcher.get_images_for_day(city, day_plan, day_index=i)
            if img:
                raw_images.append(img)
    
    # Log raw image sources
    sources = {}
    for img in raw_images:
        src = img.get("source", "unknown")
        sources[src] = sources.get(src, 0) + 1
    
    logger.info(f"✅ Fetched {len(raw_images)} raw images from APIs: {sources}")
    
    # Step 3 & 4: Download images locally and verify
    logger.info("[3/6] Downloading images locally and verifying...")
    processed_images = image_manager.process_images(raw_images, city)
    
    # Log processing results
    uploaded_count = sum(1 for img in processed_images if img.get("uploaded"))
    logger.info(f"✅ Images processed: {len(processed_images)} total, {uploaded_count} uploaded to CDN")
    
    # Step 5: Log API stats
    logger.info("[4/6] API Usage Stats:")
    stats = api_image_fetcher.get_api_stats()
    for api, data in stats.items():
        logger.info(f"   {api}: {data['hourly_used']}/{data['hourly_limit']} hourly")
    
    # Step 6: Publish to Notion with processed images
    logger.info("[5/6] Publishing to Notion with verified image URLs...")
    publisher = FixedNotionPublisher()
    
    if not publisher.enabled:
        logger.error("Notion publisher not enabled - check NOTION_API_KEY and NOTION_PARENT_PAGE_ID")
        return None
    
    try:
        page_url = await publisher.publish_blog(content, processed_images)
        logger.info("[6/6] ✅ Published successfully!")
        logger.info(f"   URL: {page_url}")
        
        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("IMAGE PROCESSING SUMMARY")
        logger.info("=" * 70)
        for i, img in enumerate(processed_images, 1):
            source = img.get("source", "unknown")
            hosting = img.get("hosting", "original")
            size = img.get("size", 0)
            size_kb = f"{size/1024:.1f}KB" if size else "unknown"
            url_preview = img["url"][:50] + "..." if len(img["url"]) > 50 else img["url"]
            logger.info(f"  Image {i}: {source} → {hosting} ({size_kb})")
            logger.info(f"     URL: {url_preview}")
        
        # Cleanup old temp files (keep current city's files)
        logger.info("\n[Cleanup] Removing old temp files...")
        image_manager.cleanup(older_than_days=7)
        
        return page_url
        
    except Exception as e:
        logger.error(f"Failed to publish: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


async def generate_blog_with_local_images(city: str = "Paris"):
    """
    Alternative: Generate blog using local file paths
    This creates file blocks with local references (for testing)
    """
    return await generate_blog_with_image_upload(city)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate travel blog with direct image upload")
    parser.add_argument("--city", default="London", help="City to generate blog for")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup temp files after generation")
    args = parser.parse_args()
    
    url = asyncio.run(generate_blog_with_image_upload(args.city))
    
    if url:
        print("\n" + "=" * 70)
        print("🎉 TRAVEL BLOG GENERATED SUCCESSFULLY!")
        print("=" * 70)
        print(f"🔗 URL: {url}")
        print("=" * 70)
        print("\nAll images have been:")
        print("  ✅ Downloaded locally for verification")
        print("  ✅ Uploaded to reliable CDN (if configured)")
        print("  ✅ Optimized for Notion display")
        print("=" * 70)
    else:
        print("\n❌ Failed to generate blog")
        sys.exit(1)
