"""
Generate Enhanced Rich Travel Blog - Daily Automation
최종 버전 - SEO 최적화 + 통계 기반 일정 + 호텔 + 비용 + 인라인 링크 + 도시 자동 순환
"""

import asyncio
import sys
import argparse
import os
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).parent))

from content.enhanced_generator import enhanced_generator
from content.accurate_image_fetcher import accurate_image_fetcher
from notion.seo_publisher import SEOEnhancedPublisher
from notion.fixed_publisher import FixedNotionPublisher
from content.style_enforcer import apply_style_guard
from city_rotator import get_next_city, get_city_by_name
from loguru import logger




def _provider_is_gemini_active() -> bool:
    return os.getenv("TRAVEL_BLOG_PROVIDER", "").lower().strip() == "gemini" and os.getenv("TRAVEL_BLOG_USE_GEMINI", "0") == "1"


def _is_rich_content(content: Dict[str, Any], min_day_len: int = 500) -> bool:
    """부족한 풍부성 방지용 게이트: 품질 기준 미달이면 게시 중단."""
    days = content.get("days_plan") or []
    if not isinstance(days, list) or not days:
        logger.error("풍부성 체크 실패: days_plan 없음")
        return False

    for d in days[:2]:
        txt = str(d.get("content") or "").strip()
        if len(txt) < min_day_len:
            logger.error(f"풍부성 체크 실패: Day {d.get('day', '?')} 본문이 짧음 ({len(txt)}자)")
            return False

        # 오전/오후/저녁 분리 유무
        missing = [tag for tag in ["오전", "오후", "저녁"] if tag not in txt]
        if missing:
            logger.error(f"풍부성 체크 실패: Day {d.get('day', '?')} 본문에 구간 라벨 누락 {missing}")
            return False

    # 식당 밀도(최소 1티어당 1개)
    day = days[0] if days else {}
    rc = day.get("restaurant_markdown", "") or ""
    if not rc or ("가성비" not in rc or "일반" not in rc or "고급" not in rc):
        logger.error("풍부성 체크 실패: Day1 식당 추천 3티어 누락")
        return False

    return True


def _warn_if_not_gemini(provider_active: bool) -> bool:
    if provider_active:
        return True
    logger.warning("현재 TRAVEL_BLOG_PROVIDER가 gemini가 아니어서 풍부성 품질이 낮을 수 있습니다.")
    return False

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

    # ===== 스타일 보정: 블로거 톤/일정·식당·호텔 표현 일관성 고정 =====
    try:
        import json
        guard_config_path = Path(__file__).parent / 'data' / 'travel_blog_style_guard.json'
        with open(guard_config_path, 'r', encoding='utf-8') as f:
            guard_config = json.load(f)
        # fallback: enforce required structure + writing tone
        content = apply_style_guard(content, city, country, city_info.get('region', '동아시아'), guard_config, day_count=4 if not content.get('destination', {}).get('days') else content['destination'].get('days', 4))
    except Exception as e:
        logger.warning(f"Style guard skipped due to error: {e}")

    # Gemini/풍부성 가드: 최소 품질 기준 미달 시 발행 중단 (반드시 사용자에게 알림)
    if not _warn_if_not_gemini(_provider_is_gemini_active()):
        pass

    if not _is_rich_content(content):
        logger.error("일정이 충분히 풍부하지 않아 발행을 중단했습니다. (요청: Gemini 기반 풍부한 글/일자별 고정 비중 정비)")
        return None

    logger.info(f"Content generated: {content['title']}")
    
    # Fetch accurate landmark images for the city
    # NEW: Uses specific landmark database to ensure images match actual destination
    logger.info("Fetching ACCURATE landmark images for the city...")
    images = accurate_image_fetcher.get_city_images(
        city=city, 
        count=6
    )
    
    # 이미지 API가 실패해도 본문 업로드는 진행한다.
    if not images or len(images) < 3:
        logger.warning(f"⚠️ Failed to get enough images for {city}; continuing without images")
        images = images or []
    else:
        logger.info(f"✅ Got {len(images)} accurate images for {city}")
    logger.info(f"Fetched {len(images)} images")
    
    # Publish to Notion
    mode = os.getenv("TRAVEL_PUBLISHER", "seo").lower().strip()
    logger.info(f"Publishing to Notion with mode: {mode}")

    if mode == "fixed":
        publisher = FixedNotionPublisher()
    elif mode == "minimal":
        publisher = FixedNotionPublisher()
        os.environ["TRAVEL_PUBLISHER_MINIMAL"] = "1"
    else:
        publisher = SEOEnhancedPublisher()

    if not publisher.enabled:
        logger.warning("selected publisher not enabled, fallback to FixedNotionPublisher")
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
    parser.add_argument("--publisher", choices=["seo", "fixed", "minimal"], default=os.getenv("TRAVEL_PUBLISHER", "seo").lower().strip(), help="Notion publisher mode")
    parser.add_argument("--writer", choices=["openai", "codex", "gemini"], default="gemini", help="Narrative writer backend (default: gemini)")
    parser.add_argument("--writer-model", type=str, default=None, help="Writer model name for codex, e.g. gpt-5.2-codex")
    args = parser.parse_args()

    # runtime config injection for downstream modules
    os.environ["TRAVEL_PUBLISHER"] = args.publisher
    if args.writer == "codex":
        os.environ["TRAVEL_BLOG_PROVIDER"] = "codex"
        os.environ["TRAVEL_BLOG_PREFER_CLAUDE"] = "1"
        os.environ["TRAVEL_BLOG_USE_CLAUDE"] = "1"
        if args.writer_model:
            os.environ["TRAVEL_BLOG_MODEL_CLAUDE"] = args.writer_model
    elif args.writer == "gemini":
        os.environ["TRAVEL_BLOG_PROVIDER"] = "gemini"
        os.environ["TRAVEL_BLOG_USE_GEMINI"] = "1"
    else:
        os.environ["TRAVEL_BLOG_PROVIDER"] = "openai"
        os.environ["TRAVEL_BLOG_TRY_OPENAI"] = "1"
        os.environ["TRAVEL_BLOG_PREFER_CLAUDE"] = "0"

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
