#!/usr/bin/env python3
"""
Integrated Rich Travel Blog Generator
Uses subagent for content + accurate images + rich Notion publishing
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from content.accurate_image_fetcher import accurate_image_fetcher
from notion.rich_publisher import rich_publisher
from loguru import logger
import argparse

# Import subagent caller
from sessions_send import send_to_subagent_and_wait


def generate_rich_blog(city: str, days: int = 5):
    """
    Generate rich travel blog using subagent and publish to Notion
    """
    logger.info(f"🎯 Generating RICH travel blog for: {city}")
    logger.info(f"   Days: {days}")
    
    # Step 1: Get rich content from subagent
    logger.info("📖 Step 1: Requesting rich content from travel blogger subagent...")
    
    prompt = f"""당신은 60개국 이상을 여행한 프로 여행 블로거입니다. 

**{city}**의 {days}일 여행 가이드를 작성해주세요.

**필수 지침:**
1. 이모지 최소화 (AI 느낌 없이 자연스럽게)
2. 데이터 기반 상세 설명 + 경험 위주 풍부한 설명
3. 매일 식당 3티어 추천 (가성비/중간/고급) - 실제 가격 포함
4. 이동 수단 및 렌트카 주차 정보 포함
5. 각 일정별 대표 이미지 설명 (실제 여행블로그처럼)
6. 통계적으로 최적의 여행 기간 선정

**출력 형식:**
```markdown
# [도시명] 완벽 가이드: 데이터 기반 [일수]일 일정

**통계적으로 최적의 방문 기간:** X일

[도시 소개 - 2-3문단, 통계와 역사 포함]

---

## Day 1: [테마]
**[이미지 설명]** [구체적 풍경 묘사]

### Morning (시간대)
**[장소명]** ([한글번역])
- 주소: [구체적 주소]
- 입장료: [가격]
- 영업시간: [시간]
- [상세 설명 3-4문단 - 역사, 볼거리, 개인팁]

### Lunch
**[티어 1: 가성비] [식당명]** - [요리타입]
- 주소: [주소]
- 가격대: [가격]
- [설명 및 추천메뉴]

**[티어 2: 중간] [식당명]** - [요리타입]
...

**[티어 3: 고급] [식당명]** - [요리타입]
...

### Afternoon (시간대)
...

### Evening (시간대)
...

### Day 1 비용 정산:
| 항목 | 비용 |
|------|------|
| 교통 | XX엔 |
| 식사 | XX엔 |
| 입장료 | XX엔 |
| 기타 | XX엔 |
| **합계** | **XX엔** |

[Day 2-5 동일 형식...]

---

## 전체 요약 및 실용 정보

### [일수]일 총 예산 (1인 기준)
| 티어 | 식비 | 교통/입장료 | 기타 | 합계 |
|------|------|-------------|------|------|
| **가성비 티어** | XX엔 | XX엔 | XX엔 | **XX엔** |
| **중간 티어** | XX엔 | XX엔 | XX엔 | **XX엔** |
| **고급 티어** | XX엔 | XX엔 | XX엔 | **XX엔** |

### 교통 팁 정리
...

### 렌트카 정보
...

### 추천 숙소 3티어
...

**작성자 노트:**
[마무리 멘트]
```

지금 바로 작성 시작!"""

    # Call subagent
    subagent_key = "agent:main:subagent:460440e3-d74a-43d8-8b05-85c6df0104b8"
    
    try:
        # Send request to subagent
        from sessions_send import sessions_send
        
        response = sessions_send(
            sessionKey=subagent_key,
            message=prompt,
            timeoutSeconds=600
        )
        
        # Extract content from response
        rich_content = response.get('reply', '')
        
        if not rich_content or len(rich_content) < 1000:
            logger.error("❌ Subagent returned insufficient content")
            return None
        
        logger.info(f"✅ Received rich content: {len(rich_content)} characters")
        
    except Exception as e:
        logger.error(f"❌ Failed to get content from subagent: {e}")
        return None
    
    # Step 2: Fetch accurate images
    logger.info("🖼️ Step 2: Fetching accurate landmark images...")
    images = accurate_image_fetcher.get_city_images(city, count=6)
    logger.info(f"✅ Got {len(images)} images")
    
    # Step 3: Publish to Notion
    logger.info("📝 Step 3: Publishing rich content to Notion...")
    try:
        url = rich_publisher.publish_travel_guide(city, rich_content, images)
        logger.info(f"✅ Published successfully!")
        logger.info(f"🔗 URL: {url}")
        return url
    except Exception as e:
        logger.error(f"❌ Failed to publish: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Generate rich travel blog with subagent")
    parser.add_argument("--city", type=str, required=True, help="City name")
    parser.add_argument("--days", type=int, default=5, help="Number of days")
    
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print(f"RICH TRAVEL BLOG GENERATOR")
    print(f"{'='*70}\n")
    
    url = generate_rich_blog(args.city, args.days)
    
    if url:
        print(f"\n{'='*70}")
        print("SUCCESS!")
        print(f"{'='*70}")
        print(f"URL: {url}")
        print(f"{'='*70}\n")
    else:
        print(f"\n{'='*70}")
        print("FAILED!")
        print(f"{'='*70}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
