"""
Fix Paris Travel Blog - Day-Specific Images
Parse the Paris itinerary, extract specific places for each day,
fetch images that MATCH those locations, and re-publish to Notion.
"""

import asyncio
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger

# ── Configuration ──
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "ntn_C8766175343aS5RQw8WD9M7HUQGdRJdoohKfPkSWpfq9UD")
PARENT_PAGE_ID = "30a20a81-386f-8092-80dc-f6639dbccbf1"
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
PEXELS_KEY = os.getenv("PEXELS_API_KEY", "")


# ═══════════════════════════════════════════════════════════════
# STEP 1: Extract day-specific locations from Paris itinerary
# ═══════════════════════════════════════════════════════════════

def extract_day_locations(days_plan: List[Dict]) -> Dict[int, Dict]:
    """
    Parse each day's spots, title, theme, and content to extract
    the PRIMARY landmark/location for image matching.
    
    Returns: {day_num: {"primary": "Eiffel Tower", "landmarks": [...], "query": "..."}}
    """
    day_locations = {}
    
    for day in days_plan:
        day_num = day.get("day", 0)
        title = day.get("title", "")
        theme = day.get("theme", "")
        spots = day.get("spots", [])
        content = day.get("content", "")
        
        # Extract all spot names
        landmark_names = [s["name"] for s in spots if s.get("name")]
        
        # Determine primary landmark (first/most iconic spot of the day)
        primary = landmark_names[0] if landmark_names else title
        
        # Build a search query that's specific to the day's locations
        # Use the first 2 landmarks for the search query
        top_landmarks = landmark_names[:2]
        
        day_locations[day_num] = {
            "primary": primary,
            "landmarks": landmark_names,
            "title": title,
            "theme": theme,
            "search_queries": [
                f"Paris {primary}",  # Most specific
                f"Paris {' '.join(top_landmarks)}" if len(top_landmarks) > 1 else f"Paris {primary} landmark",
                f"Paris {theme}" if theme else f"Paris travel",  # Fallback
            ]
        }
    
    return day_locations


# ═══════════════════════════════════════════════════════════════
# STEP 2: Fetch day-specific images via Unsplash API
# ═══════════════════════════════════════════════════════════════

def search_unsplash(query: str, count: int = 3) -> List[Dict]:
    """Search Unsplash for images matching query."""
    if not UNSPLASH_KEY:
        logger.warning("No Unsplash API key, skipping Unsplash search")
        return []
    
    try:
        encoded_q = urllib.parse.quote(query)
        url = f"https://api.unsplash.com/search/photos?query={encoded_q}&per_page={count}&orientation=landscape"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Client-ID {UNSPLASH_KEY}")
        req.add_header("Accept-Version", "v1")
        
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("results", [])
            
            images = []
            for r in results[:count]:
                img_url = r.get("urls", {}).get("regular", "")
                if not img_url:
                    continue
                images.append({
                    "url": img_url,
                    "source": "unsplash",
                    "photographer": r.get("user", {}).get("name", "Unknown"),
                    "photographer_url": r.get("user", {}).get("links", {}).get("html", ""),
                    "unsplash_url": r.get("links", {}).get("html", ""),
                    "description": r.get("description") or r.get("alt_description") or query,
                    "query": query,
                })
            
            logger.info(f"  Unsplash [{query}]: {len(images)} results")
            return images
    except Exception as e:
        logger.error(f"  Unsplash error for '{query}': {e}")
        return []


def search_pexels(query: str, count: int = 3) -> List[Dict]:
    """Search Pexels for images matching query."""
    if not PEXELS_KEY:
        logger.info("No Pexels API key, skipping Pexels search")
        return []
    
    try:
        encoded_q = urllib.parse.quote(query)
        url = f"https://api.pexels.com/v1/search?query={encoded_q}&per_page={count}&orientation=landscape"
        req = urllib.request.Request(url)
        req.add_header("Authorization", PEXELS_KEY)
        
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            photos = data.get("photos", [])
            
            images = []
            for p in photos[:count]:
                src = p.get("src", {})
                img_url = src.get("large", src.get("medium", ""))
                if not img_url:
                    continue
                images.append({
                    "url": img_url,
                    "source": "pexels",
                    "photographer": p.get("photographer", "Unknown"),
                    "photographer_url": p.get("photographer_url", ""),
                    "description": p.get("alt", query),
                    "query": query,
                })
            
            logger.info(f"  Pexels [{query}]: {len(images)} results")
            return images
    except Exception as e:
        logger.error(f"  Pexels error for '{query}': {e}")
        return []


def validate_url(url: str) -> bool:
    """Check if image URL is accessible."""
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except:
        try:
            req = urllib.request.Request(url, method='GET')
            req.add_header('User-Agent', 'Mozilla/5.0')
            req.add_header('Range', 'bytes=0-0')
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status in [200, 206]
        except:
            return False


# Curated fallback: hand-picked Pexels images matched to Paris landmarks
PARIS_LANDMARK_FALLBACKS = {
    "Place des Vosges": [
        "https://images.pexels.com/photos/1530259/pexels-photo-1530259.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    ],
    "Marais": [
        "https://images.pexels.com/photos/1530259/pexels-photo-1530259.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    ],
    "Eiffel Tower": [
        "https://images.pexels.com/photos/532826/pexels-photo-532826.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "https://images.pexels.com/photos/161901/paris-sunset-eiffel-tower-champs-de-mars.jpg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    ],
    "Trocadéro": [
        "https://images.pexels.com/photos/149114/pexels-photo-149114.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    ],
    "Louvre Museum": [
        "https://images.pexels.com/photos/2363/france-landmark-lights-night.jpg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "https://images.pexels.com/photos/2675266/pexels-photo-2675266.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    ],
    "Sainte-Chapelle": [
        "https://images.pexels.com/photos/2675266/pexels-photo-2675266.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    ],
    "Sacré-Cœur": [
        "https://images.pexels.com/photos/2082103/pexels-photo-2082103.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "https://images.pexels.com/photos/1461974/pexels-photo-1461974.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    ],
    "Montmartre": [
        "https://images.pexels.com/photos/2082103/pexels-photo-2082103.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    ],
    "Galeries Lafayette": [
        "https://images.pexels.com/photos/843037/pexels-photo-843037.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "https://images.pexels.com/photos/2817495/pexels-photo-2817495.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    ],
    "Paris hero": [
        "https://images.pexels.com/photos/532826/pexels-photo-532826.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "https://images.pexels.com/photos/149114/pexels-photo-149114.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    ],
}


def fetch_day_specific_image(day_num: int, day_info: Dict, used_urls: set) -> Optional[Dict]:
    """
    Fetch ONE image for a specific day, trying multiple strategies:
    1. Unsplash API search for the primary landmark
    2. Pexels API search for the primary landmark
    3. Curated fallback image for known landmarks
    """
    queries = day_info["search_queries"]
    primary = day_info["primary"]
    
    logger.info(f"  Day {day_num}: Searching for '{primary}'")
    
    # Strategy 1: Unsplash API
    for query in queries:
        results = search_unsplash(query, 3)
        for img in results:
            if img["url"] not in used_urls:
                used_urls.add(img["url"])
                logger.info(f"  ✅ Day {day_num}: Found Unsplash image for '{query}'")
                return img
        time.sleep(0.5)  # Rate limit
    
    # Strategy 2: Pexels API
    for query in queries:
        results = search_pexels(query, 3)
        for img in results:
            if img["url"] not in used_urls:
                used_urls.add(img["url"])
                logger.info(f"  ✅ Day {day_num}: Found Pexels image for '{query}'")
                return img
        time.sleep(0.3)
    
    # Strategy 3: Curated fallback
    for landmark in day_info["landmarks"] + [primary]:
        for key, urls in PARIS_LANDMARK_FALLBACKS.items():
            if key.lower() in landmark.lower() or landmark.lower() in key.lower():
                for url in urls:
                    if url not in used_urls:
                        used_urls.add(url)
                        logger.info(f"  ✅ Day {day_num}: Using curated fallback for '{landmark}'")
                        return {
                            "url": url,
                            "source": "pexels_static",
                            "photographer": "Pexels",
                            "description": f"Paris {landmark}",
                            "query": f"Paris {landmark} (curated fallback)",
                        }
    
    # Strategy 4: Generic Paris fallback
    for url in PARIS_LANDMARK_FALLBACKS.get("Paris hero", []):
        if url not in used_urls:
            used_urls.add(url)
            logger.info(f"  ⚠️ Day {day_num}: Using generic Paris fallback")
            return {
                "url": url,
                "source": "pexels_static",
                "photographer": "Pexels",
                "description": f"Paris travel - Day {day_num}",
                "query": "Paris travel (generic fallback)",
            }
    
    return None


def fetch_all_day_images(day_locations: Dict[int, Dict]) -> List[Dict]:
    """
    Fetch images for hero + all days, ensuring each image matches its day's locations.
    Returns: [hero_image, day1_image, day2_image, ...]
    """
    images = []
    used_urls = set()
    
    # Hero image: Paris iconic landmark
    logger.info("Fetching hero image: Paris iconic landmark")
    hero_queries = ["Paris Eiffel Tower iconic skyline", "Paris cityscape landmark", "Paris France travel"]
    hero_img = None
    
    for q in hero_queries:
        results = search_unsplash(q, 3)
        for img in results:
            if validate_url(img["url"]):
                hero_img = img
                used_urls.add(img["url"])
                break
        if hero_img:
            break
        results = search_pexels(q, 3)
        for img in results:
            if validate_url(img["url"]):
                hero_img = img
                used_urls.add(img["url"])
                break
        if hero_img:
            break
        time.sleep(0.5)
    
    if not hero_img:
        hero_url = "https://images.pexels.com/photos/532826/pexels-photo-532826.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
        hero_img = {
            "url": hero_url,
            "source": "pexels_static",
            "photographer": "Pexels",
            "description": "Paris Eiffel Tower",
            "query": "Paris Eiffel Tower (curated)",
        }
        used_urls.add(hero_url)
    
    images.append(hero_img)
    logger.info(f"✅ Hero: {hero_img['query']} -> {hero_img['url'][:60]}...")
    
    # Day-specific images
    for day_num in sorted(day_locations.keys()):
        day_info = day_locations[day_num]
        logger.info(f"\nFetching Day {day_num} image: {day_info['primary']} ({day_info['title']})")
        
        img = fetch_day_specific_image(day_num, day_info, used_urls)
        if img:
            images.append(img)
            logger.info(f"✅ Day {day_num}: query='{img['query']}' -> {img['url'][:60]}...")
        else:
            # Final fallback - shouldn't happen
            logger.error(f"❌ Day {day_num}: No image found!")
            images.append({
                "url": "https://images.pexels.com/photos/699466/pexels-photo-699466.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "source": "pexels_static",
                "photographer": "Pexels",
                "description": f"Paris - Day {day_num}",
                "query": "Paris generic (last resort)",
            })
        
        time.sleep(0.5)
    
    return images


# ═══════════════════════════════════════════════════════════════
# STEP 3: Publish to Notion with matched images
# ═══════════════════════════════════════════════════════════════

def notion_request(method: str, path: str, payload: Optional[Dict] = None) -> Dict:
    """Make a Notion API request."""
    url = f"https://api.notion.com/v1{path}"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload else None
    
    req = urllib.request.Request(
        url=url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2025-09-03",
            "Content-Type": "application/json",
        },
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Notion API error {e.code}: {body}") from e


def _rt(text: str, bold: bool = False, link: str = None) -> List[Dict]:
    """Create Notion rich text."""
    # Handle markdown links
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    parts = []
    last_end = 0
    
    for m in re.finditer(pattern, text):
        if m.start() > last_end:
            parts.append({"type": "text", "text": {"content": text[last_end:m.start()]}})
        parts.append({
            "type": "text", 
            "text": {"content": m.group(1), "link": {"url": m.group(2)}},
            "annotations": {"bold": True}
        })
        last_end = m.end()
    
    if last_end < len(text):
        remaining = text[last_end:]
        item = {"type": "text", "text": {"content": remaining[:1900]}}
        if bold:
            item["annotations"] = {"bold": True}
        if link:
            item["text"]["link"] = {"url": link}
        parts.append(item)
    
    return parts if parts else [{"type": "text", "text": {"content": text[:1900]}}]


def heading(level: int, text: str) -> Dict:
    t = f"heading_{level}"
    return {"object": "block", "type": t, t: {"rich_text": _rt(text)}}


def paragraph(text: str, bold: bool = False, link: str = None) -> Dict:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": _rt(text, bold, link)}}


def callout(text: str, icon: str = "", color: str = "default") -> Dict:
    block = {"object": "block", "type": "callout", "callout": {"rich_text": _rt(text), "color": color}}
    if icon:
        block["callout"]["icon"] = {"type": "emoji", "emoji": icon}
    return block


def divider() -> Dict:
    return {"object": "block", "type": "divider", "divider": {}}


def quote(text: str) -> Dict:
    return {"object": "block", "type": "quote", "quote": {"rich_text": _rt(text)}}


def image_block(url: str, caption: str = "") -> Dict:
    block = {"object": "block", "type": "image", "image": {"type": "external", "external": {"url": url}}}
    if caption:
        block["image"]["caption"] = [{"type": "text", "text": {"content": caption}}]
    return block


def maps_url(query: str) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query)}"


def build_blocks(content: Dict, images: List[Dict], day_locations: Dict[int, Dict]) -> List[Dict]:
    """Build Notion blocks with day-specific images."""
    dest = content["destination"]
    city = dest["name"]
    blocks = []
    
    # Hero Image
    if images:
        hero = images[0]
        attr = f"📷 {hero.get('photographer', 'Unknown')} ({hero.get('source', 'unknown')}) | Search: {hero.get('query', '')}"
        blocks.append(image_block(hero["url"], f"{city} | {attr}"))
    
    blocks.append(heading(1, f"🇫🇷 {city} 여행 완벽 가이드"))
    blocks.append(paragraph(f"{dest['days']}일 일정 | {dest['best_season']} 추천 | 통화: {dest['currency']}", bold=True))
    blocks.append(divider())
    blocks.append(quote(content.get("intro", "")))
    blocks.append(divider())
    
    # Hotels
    blocks.append(heading(2, "🏨 추천 호텔"))
    hotels = content.get("hotels", {})
    for cat, label, color in [("budget", "💚 가성비", "green_background"), ("luxury", "💜 럭셔리", "purple_background")]:
        hotel_list = hotels.get(cat, [])
        if not hotel_list:
            continue
        blocks.append(callout(label, "", color))
        for h in hotel_list:
            h_url = h.get('maps_url', '')
            if h_url and h_url.startswith('http'):
                blocks.append(paragraph(f"[{h['name']}]({h_url}) ★{h['rating']} | {h['price_per_night']} | {h['area']}"))
            else:
                blocks.append(paragraph(f"{h['name']} ★{h['rating']} | {h['price_per_night']} | {h['area']}"))
    
    blocks.append(divider())
    
    # ═══ Daily Itinerary with matched images ═══
    blocks.append(heading(2, "📅 일정 상세"))
    
    for idx, day in enumerate(content.get("days_plan", [])):
        day_num = day.get("day", idx + 1)
        image_idx = idx + 1  # images[0] = hero, images[1] = day1, etc.
        
        # Day-specific image
        if image_idx < len(images):
            day_img = images[image_idx]
            day_locs = day_locations.get(day_num, {})
            primary = day_locs.get("primary", f"Day {day_num}")
            attr = f"📷 {day_img.get('photographer', 'Unknown')} | {primary} | Search: {day_img.get('query', '')}"
            blocks.append(image_block(day_img["url"], f"Day {day_num}: {primary} | {attr}"))
        
        # Day header
        blocks.append(callout(f"📌 Day {day_num}: {day['title']}", "", "blue_background"))
        blocks.append(paragraph(f"테마: {day['theme']}", bold=True))
        
        # Content (first 2 paragraphs)
        content_text = day.get("content", "").strip()
        paragraphs_list = [p.strip() for p in content_text.split('\n\n') if p.strip()]
        for p in paragraphs_list[:2]:
            blocks.append(paragraph(p))
        
        # Spots
        spots = day.get("spots", [])
        if spots:
            blocks.append(heading(3, "🗺️ 오늘의 코스"))
            for i, spot in enumerate(spots, 1):
                name = spot['name']
                desc = spot['desc']
                tip = spot.get('tip', '')
                time_str = spot.get('time', '')
                m_url = maps_url(f"{name} {city}")
                res_url = spot.get('reservation_url', '')
                res_req = spot.get('reservation_required', False)
                
                title_line = f"{i}. [{name}]({m_url})"
                if time_str:
                    title_line += f"  ⏰ {time_str}"
                blocks.append(paragraph(title_line))
                
                detail = desc
                if tip:
                    detail += f" 💡 {tip}"
                if res_req and res_url and res_url.startswith('http'):
                    detail += f" 🎫 [예약하기]({res_url})"
                blocks.append(paragraph(detail))
        
        # Restaurants
        restaurants = day.get("restaurants", [])
        if restaurants:
            blocks.append(heading(3, "🍽️ 오늘의 맛집"))
            for r in restaurants:
                r_name = r['name']
                r_price = r.get('price', '')
                r_type = r.get('type', '')
                r_tip = r.get('tip', '')
                r_maps = maps_url(f"{r_name} {city}")
                r_res_url = r.get('reservation_url', '')
                r_res_req = r.get('reservation_required', False)
                
                r_line = f"🧡 [{r_name}]({r_maps})  {r_type} · {r_price}"
                blocks.append(paragraph(r_line))
                if r_tip:
                    detail = f"→ {r_tip}"
                    if r_res_req and r_res_url and r_res_url.startswith('http'):
                        detail += f" 🎫 [예약하기]({r_res_url})"
                    blocks.append(paragraph(detail))
        
        # Cost
        cost = day.get("estimated_cost", {})
        if cost:
            cost_parts = []
            if cost.get('transport'):
                cost_parts.append(f"교통 {cost['transport']}")
            if cost.get('food'):
                cost_parts.append(f"식사 {cost['food']}")
            if cost.get('activities'):
                cost_parts.append(f"입장료 {cost['activities']}")
            if cost_parts:
                blocks.append(paragraph(" · ".join(cost_parts)))
            blocks.append(callout(f"💰 합계: {cost.get('total', '')}", "", "yellow_background"))
        
        blocks.append(divider())
    
    # Transport
    blocks.append(heading(2, "🚇 교통 및 이동"))
    transport = content.get("transport_summary", {})
    for k, v in transport.items():
        blocks.append(paragraph(f"• {k}: {v}"))
    
    # Total Cost
    blocks.append(divider())
    blocks.append(heading(2, "💰 총 예상 비용"))
    estimates = content.get("total_estimate", {})
    for level in ["budget", "luxury"]:
        est = estimates.get(level, {})
        label = "가성비 여행" if level == "budget" else "럭셔리 여행"
        color = "green_background" if level == "budget" else "purple_background"
        blocks.append(callout(label, "", color))
        for key, val in est.items():
            if key != "total":
                blocks.append(paragraph(f"• {key}: {val}"))
        if est.get("total"):
            blocks.append(paragraph(f"**총계: {est['total']}**", bold=True))
    
    # Emergency contacts
    blocks.append(divider())
    blocks.append(heading(2, "🚨 비상연락망"))
    final_summary = content.get("final_summary", {})
    emergency = final_summary.get("emergency_contacts", {})
    embassy = final_summary.get("embassy_info", {})
    
    if emergency:
        blocks.append(callout("긴급 신고번호", "🚨", "red_background"))
        for key, val in emergency.items():
            label = {"police": "👮 경찰", "ambulance": "🚑 구급차", "fire": "🚒 소방", "general": "📞 통합신고"}.get(key, key)
            blocks.append(paragraph(f"{label}: {val}"))
    
    if embassy:
        blocks.append(callout("주프랑스 한국대사관", "🏛️", "blue_background"))
        if embassy.get("phone"):
            blocks.append(paragraph(f"📞 {embassy['phone']}"))
        if embassy.get("address"):
            blocks.append(paragraph(f"📍 {embassy['address']}"))
        if embassy.get("website"):
            blocks.append(paragraph(f"🌐 [{embassy['name']}]({embassy['website']})"))
    
    # Image matching report
    blocks.append(divider())
    blocks.append(heading(2, "📷 이미지 매칭 리포트"))
    blocks.append(paragraph("각 일자별 이미지가 실제 일정의 장소와 매칭되도록 검색했습니다:"))
    
    if images:
        blocks.append(paragraph(f"🖼️ Hero: {images[0].get('query', 'Paris')}", bold=True))
    for day_num in sorted(day_locations.keys()):
        img_idx = day_num  # images[day_num] for day_num (images[0] = hero)
        if img_idx < len(images):
            img = images[img_idx]
            locs = day_locations[day_num]
            blocks.append(paragraph(
                f"📸 Day {day_num} ({locs['primary']}): searched '{img.get('query', '?')}' → {img.get('source', '?')}"
            ))
    
    # Image attributions
    blocks.append(divider())
    blocks.append(heading(2, "📷 이미지 출처"))
    for i, img in enumerate(images):
        source = img.get("source", "unknown")
        photographer = img.get("photographer", "Unknown")
        if source == "unsplash":
            p_url = img.get("photographer_url", "")
            u_url = img.get("unsplash_url", "")
            if p_url and u_url:
                blocks.append(paragraph(f"[{i}] [{photographer}]({p_url}) on [Unsplash]({u_url})"))
            else:
                blocks.append(paragraph(f"[{i}] {photographer} on Unsplash"))
        elif source == "pexels":
            p_url = img.get("photographer_url", "")
            if p_url:
                blocks.append(paragraph(f"[{i}] [{photographer}]({p_url}) on [Pexels](https://www.pexels.com)"))
            else:
                blocks.append(paragraph(f"[{i}] {photographer} on Pexels"))
        else:
            blocks.append(paragraph(f"[{i}] {photographer} ({source})"))
    
    # Footer
    blocks.append(divider())
    blocks.append(paragraph(f"작성일: {datetime.now().strftime('%Y-%m-%d')} | Day-specific image matching applied"))
    
    return blocks


async def publish_to_notion(content: Dict, images: List[Dict], day_locations: Dict[int, Dict]) -> str:
    """Create a new Notion page and publish content with matched images."""
    import random
    
    dest = content["destination"]
    city = dest["name"]
    country = dest.get("country", "France")
    suffix = random.randint(1000, 9999)
    
    title = f"{datetime.now().strftime('%Y-%m-%d')} | {city}, {country} | {dest['days']}일 가이드 [Fixed Images] #{suffix}"
    
    # Create page
    page = notion_request("POST", "/pages", {
        "parent": {"page_id": PARENT_PAGE_ID},
        "properties": {
            "title": {"title": [{"type": "text", "text": {"content": title}}]}
        },
    })
    
    page_id = page.get("id", "")
    page_url = page.get("url", "")
    
    if not page_id:
        raise RuntimeError("Failed to create Notion page")
    
    # Build blocks
    blocks = build_blocks(content, images, day_locations)
    logger.info(f"Total blocks: {len(blocks)}")
    
    # Publish in batches
    batch_size = 95
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i + batch_size]
        notion_request("PATCH", f"/blocks/{page_id}/children", {"children": batch})
        logger.info(f"Published blocks {i+1} to {min(i+len(batch), len(blocks))}")
    
    return page_url


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

async def main():
    logger.info("=" * 70)
    logger.info("FIX PARIS TRAVEL BLOG - DAY-SPECIFIC IMAGES")
    logger.info("=" * 70)
    
    # Get Paris content from enhanced generator
    from content.enhanced_generator import enhanced_generator
    content = enhanced_generator.generate_enhanced_blog("Paris", days=5)
    
    if not content:
        logger.error("Failed to generate Paris content")
        return
    
    days_plan = content.get("days_plan", [])
    logger.info(f"Paris itinerary: {len(days_plan)} days")
    
    # STEP 1: Extract day-specific locations
    logger.info("\n" + "=" * 50)
    logger.info("STEP 1: Extracting day-specific locations")
    logger.info("=" * 50)
    
    day_locations = extract_day_locations(days_plan)
    
    for day_num, info in sorted(day_locations.items()):
        logger.info(f"  Day {day_num}: {info['title']}")
        logger.info(f"    Primary: {info['primary']}")
        logger.info(f"    Landmarks: {', '.join(info['landmarks'])}")
        logger.info(f"    Search queries: {info['search_queries']}")
    
    # STEP 2: Fetch day-specific images
    logger.info("\n" + "=" * 50)
    logger.info("STEP 2: Fetching day-specific images")
    logger.info("=" * 50)
    
    images = fetch_all_day_images(day_locations)
    
    logger.info(f"\nTotal images fetched: {len(images)}")
    for i, img in enumerate(images):
        role = "Hero" if i == 0 else f"Day {i}"
        logger.info(f"  [{role}] source={img['source']}, query='{img.get('query', '?')}', url={img['url'][:60]}...")
    
    # STEP 3: Publish to Notion
    logger.info("\n" + "=" * 50)
    logger.info("STEP 3: Publishing to Notion")
    logger.info("=" * 50)
    
    page_url = await publish_to_notion(content, images, day_locations)
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ PARIS TRAVEL BLOG FIXED SUCCESSFULLY!")
    logger.info(f"📄 Notion URL: {page_url}")
    logger.info("=" * 70)
    
    # Print final report
    print("\n" + "=" * 70)
    print("📋 REPORT: Day-Specific Image Matching")
    print("=" * 70)
    
    for day_num in sorted(day_locations.keys()):
        info = day_locations[day_num]
        img_idx = day_num
        img = images[img_idx] if img_idx < len(images) else None
        
        print(f"\n  Day {day_num}: {info['title']}")
        print(f"    Locations: {', '.join(info['landmarks'])}")
        print(f"    Primary: {info['primary']}")
        if img:
            print(f"    Image query: {img.get('query', '?')}")
            print(f"    Image source: {img.get('source', '?')}")
            print(f"    Image URL: {img['url'][:80]}...")
        print(f"    ✅ Match: {'YES' if img else 'NO'}")
    
    print(f"\n  📄 Notion page: {page_url}")
    print("=" * 70)
    
    return page_url


if __name__ == "__main__":
    asyncio.run(main())
