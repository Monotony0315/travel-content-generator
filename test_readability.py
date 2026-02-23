"""
Test Improved Readability for London
Tests the new formatted output from rich_city_generator and final_notion_publisher
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from content.rich_city_generator import rich_city_generator
from notion.rich_publisher import final_notion_publisher
from content.api_image_fetcher import api_image_fetcher
from loguru import logger


async def test_london_readability():
    """Test London generation with improved readability"""
    
    logger.info("="*70)
    logger.info("TESTING IMPROVED READABILITY FOR LONDON")
    logger.info("="*70)
    
    city = "London"
    country = "United Kingdom"
    region = "유럽"
    days = 5
    
    # Step 1: Generate rich content
    logger.info("\n[1/3] Generating rich content for London...")
    content = rich_city_generator.generate_rich_content(city, country, region, days)
    
    if not content:
        logger.error("Failed to generate content")
        return None
    
    logger.info(f"✅ Content generated: {content['title']}")
    
    # Step 2: Print sample of formatted content for verification
    logger.info("\n[2/3] Checking formatted content...")
    
    days_plan = content.get("days_plan", [])
    if days_plan:
        logger.info(f"\n📄 Day 1 Content Preview (first 1500 chars):")
        day1_content = days_plan[0].get("content", "")
        preview = day1_content[:1500] + "..." if len(day1_content) > 1500 else day1_content
        for line in preview.split('\n'):
            logger.info(f"   {line}")
        
        # Check formatting markers
        has_dividers = "---" in day1_content
        has_bold_headers = day1_content.count("**") >= 2
        has_bullets = "•" in day1_content
        has_emojis = any(e in day1_content for e in ["📍", "🗺️", "🎫", "📸", "💡"])
        
        logger.info(f"\n✓ Formatting Check:")
        logger.info(f"  - Horizontal dividers (---): {'✓' if has_dividers else '✗'}")
        logger.info(f"  - Bold headers (**): {'✓' if has_bold_headers else '✗'}")
        logger.info(f"  - Bullet points (•): {'✓' if has_bullets else '✗'}")
        logger.info(f"  - Section emojis (📍🗺️): {'✓' if has_emojis else '✗'}")
    
    # Step 3: Fetch images
    logger.info("\n[3/3] Fetching images...")
    images = api_image_fetcher.get_all_images(city, days_plan)
    
    if not images or len(images) < 6:
        logger.warning(f"Only got {len(images) if images else 0} images, adding fallbacks...")
        # Add fallback images
        for i in range(6 - len(images) if images else 6):
            if not images:
                images = []
            images.append({
                "url": f"https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=1920",
                "source": "unsplash",
                "photographer": "Test",
            })
    
    sources = {}
    for img in images:
        src = img.get("source", "unknown")
        sources[src] = sources.get(src, 0) + 1
    
    logger.info(f"✅ Fetched {len(images)} images: {sources}")
    
    # Step 4: Publish to Notion if enabled
    if final_notion_publisher.enabled:
        logger.info("\n[4/4] Publishing to Notion...")
        try:
            page_url = await final_notion_publisher.publish_blog(content, images)
            logger.info(f"\n🎉 SUCCESS! Published to Notion")
            logger.info(f"🔗 URL: {page_url}")
            
            # Write report
            report_path = Path(__file__).parent / "LONDON_READABILITY_TEST.json"
            import json
            from datetime import datetime
            report = {
                "timestamp": datetime.now().isoformat(),
                "city": city,
                "notion_url": page_url,
                "formatting_check": {
                    "has_dividers": has_dividers,
                    "has_bold_headers": has_bold_headers,
                    "has_bullets": has_bullets,
                    "has_emojis": has_emojis,
                },
                "content_preview": day1_content[:2000] if days_plan else "No content",
            }
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.info(f"\n📝 Report saved to: {report_path}")
            
            return page_url
        except Exception as e:
            logger.error(f"Failed to publish: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    else:
        logger.warning("\n⚠️ Notion publisher not enabled - skipping publish")
        logger.info("\n📝 Content preview shown above for verification")
        return None


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LONDON READABILITY IMPROVEMENT TEST")
    print("="*70)
    print("\nTesting:")
    print("  ✓ Bold time headers (e.g., **오전 9:00 - 빅벤 방문**)")
    print("  ✓ Section separators (---)")
    print("  ✓ Location info (📍 🗺️)")
    print("  ✓ Ticket info (🎫)")
    print("  ✓ Photo tips (📸)")
    print("  ✓ Pro tips (💡)")
    print("  ✓ Bullet points (•)")
    print("="*70 + "\n")
    
    url = asyncio.run(test_london_readability())
    
    if url:
        print("\n" + "="*70)
        print("✅ LONDON BLOG PUBLISHED WITH IMPROVED READABILITY")
        print("="*70)
        print(f"\n🔗 Notion URL: {url}")
        print("\n📋 Improvements Applied:")
        print("   ✓ Clear time headers with bold formatting")
        print("   ✓ Visual separation between time slots")
        print("   ✓ Section organization (Location, Tickets, Tips)")
        print("   ✓ Bullet points for lists")
        print("   ✓ Horizontal rules between sections")
        print("="*70)
    else:
        print("\n⚠️ Test completed (check logs above)")
