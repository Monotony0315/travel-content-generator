"""
Final Verification Test for Travel Blog Fixes
Tests: 1) No emojis, 2) Markdown links, 3) Unique images
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from content.rich_city_generator import rich_city_generator
from content.enhanced_image_fetcher import enhanced_image_fetcher

# Emoji pattern - only actual emoji symbols, not CJK characters
EMOJI_LIST = [
    '🎯', '✅', '⚠️', '📌', '💡', '🔗', '📍', '⭐', '✈️', '🎫', '🍽️',
    '🎵', '🎶', '🎨', '🎭', '🎪', '🎬', '🎤', '🎧', '🎼', '🎹', '🥁',
    '🎷', '🎸', '🎺', '🎻', '🎲', '🎯', '🎳', '🎮', '🎰', '🎱', '🎪',
    '🎨', '🎬', '🎤', '🎧', '🎼', '🎹', '🥁', '🎷', '🎸', '🎺', '🎻',
    '📱', '📲', '☎️', '📞', '📟', '📠', '🔋', '🔌', '💻', '🖥️', '🖨️',
    '⌨️', '🖱️', '🖲️', '💽', '💾', '💿', '📀', '🎥', '🎞️', '📽️', '🎬',
    '📺', '📷', '📸', '📹', '📼', '🔍', '🔎', '🔬', '🔭', '📡', '🕯️',
    '💡', '🔦', '🏮', '📔', '📕', '📖', '📗', '📘', '📙', '📚', '📓',
    '📒', '📃', '📜', '📄', '📰', '🗞️', '📑', '🔖', '🏷️', '💰', '💴',
    '💵', '💶', '💷', '💸', '💳', '💹', '💱', '💲', '✉️', '📧', '📨',
    '📩', '📤', '📥', '📦', '📫', '📪', '📬', '📭', '📮', '🗳️', '✏️',
    '✒️', '🖋️', '🖊️', '🖌️', '🖍️', '📝', '💼', '📁', '📂', '🗂️', '📅',
    '📆', '🗒️', '🗓️', '📇', '📈', '📉', '📊', '📋', '📌', '📍', '📎',
    '🖇️', '📏', '📐', '✂️', '🗃️', '🗄️', '🗑️', '🔒', '🔓', '🔏', '🔐',
    '🔑', '🗝️', '🔨', '⛏️', '⚒️', '🛠️', '🗡️', '⚔️', '🔫', '🏹', '🛡️',
    '🔧', '🔩', '⚙️', '🗜️', '⚗️', '⚖️', '🔗', '⛓️', '🧰', '🧲', '🧪',
    '🧫', '🧬', '🔬', '🔭', '📡', '💉', '💊', '🩸', '🩹', '🩺', '🌡️',
    '🧷', '🧹', '🧺', '🧻', '🧼', '🧽', '🛁', '🛀', '🧴', '🛎️', '🔑',
    '🗝️', '🚪', '🛋️', '🛏️', '🛌', '🖼️', '🛍️', '🛒', '🎁', '🎈', '🎏',
    '🎀', '🎊', '🎉', '🎎', '🏆', '🏅', '🥇', '🥈', '🥉', '🏵️', '🎗️',
    '🎖️', '🎟️', '🎫', '🎮', '🕹️', '🎰', '🎲', '🧩', '🧸', '🪀', '🪁',
    '🎭', '🎨', '🎬', '🎤', '🎧', '🎼', '🎹', '🥁', '🎷', '🎸', '🎺',
    '🎻', '🪕', '🎮', '🎰', '🎲', '🧩', '🧸', '🪀', '🪁', '🪂', '🪃',
    '🪄', '🪅', '🪆', '🪐', '🪑', '🪒', '🪓', '🪔', '🪕', '🪖', '🪗',
    '🪘', '🪙', '🪚', '🪛', '🪜', '🪝', '🪞', '🪟', '🪠', '🪡', '🪢',
    '🪣', '🪤', '🪥', '🪦', '🪧', '🪨', '🪩', '🪪', '🪽', '🪾', '🪿',
    '🫀', '🫁', '🫂', '🫃', '🫄', '🫅', '🫆', '🫇', '🫈', '🫉', '🫊',
    '🫋', '🫌', '🫍', '🫎', '🫏', '🫐', '🫑', '🫒', '🫓', '🫔', '🫕',
    '🫖', '🫗', '🫘', '🫙', '🫚', '🫛', '🫜', '🫝', '🫞', '🫟', '🫠',
    '🫡', '🫢', '🫣', '🫤', '🫥', '🫦', '🫧', '🫨', '🫩', '🫪', '🫫',
    '🫬', '🫭', '🫮', '🫯', '🫰', '🫱', '🫲', '🫳', '🫴', '🫵', '🫶',
    '🫷', '🫸', '🫹', '🫺', '🫻', '🫼', '🫽', '🫾', '🫿'
]
EMOJI_PATTERN = re.compile('|'.join(re.escape(e) for e in EMOJI_LIST))

def check_emojis(text, context=""):
    """Check for emojis in text"""
    emojis = EMOJI_PATTERN.findall(text)
    if emojis:
        print(f"  ❌ FOUND EMOJIS in {context}: {emojis}")
        return False
    return True

def check_url_format(text, context=""):
    """Check that URLs use markdown format [text](url), not raw URLs"""
    # Find raw URLs (not in markdown format)
    raw_url_pattern = r'(?<![\]\(])https?://[^\s\)]+'
    raw_urls = re.findall(raw_url_pattern, text)
    
    # Filter out URLs that are inside markdown links
    markdown_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    markdown_urls = re.findall(markdown_pattern, text)
    markdown_url_set = set(url for _, url in markdown_urls)
    
    actual_raw = [url for url in raw_urls if url not in markdown_url_set]
    
    if actual_raw:
        print(f"  ❌ FOUND RAW URLs in {context}: {actual_raw[:3]}")
        return False
    return True

def test_fixes():
    print("="*70)
    print("FINAL VERIFICATION TEST - Travel Blog Fixes")
    print("="*70)
    
    # Test 1: Generate London content and check for emojis
    print("\n[Test 1] Generating London content...")
    content = rich_city_generator.generate_rich_content("London", "UK", "유럽", days=5)
    
    emoji_pass = True
    url_pass = True
    
    # Check intro
    intro = content.get("intro", "")
    if not check_emojis(intro, "intro"):
        emoji_pass = False
    if not check_url_format(intro, "intro"):
        url_pass = False
    
    # Check days_plan content
    days_plan = content.get("days_plan", [])
    for i, day in enumerate(days_plan, 1):
        day_content = day.get("content", "")
        if not check_emojis(day_content, f"Day {i} content"):
            emoji_pass = False
        if not check_url_format(day_content, f"Day {i} content"):
            url_pass = False
    
    if emoji_pass:
        print("  ✅ PASS: No emojis found in content")
    else:
        print("  ❌ FAIL: Emojis still present in content")
    
    if url_pass:
        print("  ✅ PASS: All URLs use markdown format")
    else:
        print("  ❌ FAIL: Raw URLs found in content")
    
    # Test 2: Check images are unique
    print("\n[Test 2] Fetching images for London...")
    images = enhanced_image_fetcher.get_city_images("London", "UK", days_plan, count=6)
    
    if len(images) >= 6:
        print(f"  ✅ Retrieved {len(images)} images")
        
        # Check for duplicates
        urls = [img.get("url", "") for img in images]
        unique_urls = set(urls)
        
        if len(unique_urls) == len(urls):
            print(f"  ✅ All {len(urls)} images have unique URLs")
            image_pass = True
        else:
            print(f"  ❌ FAIL: Found {len(urls) - len(unique_urls)} duplicate image(s)")
            # Show duplicates
            from collections import Counter
            url_counts = Counter(urls)
            for url, count in url_counts.items():
                if count > 1:
                    print(f"      Duplicate: {url[:60]}... (appears {count} times)")
            image_pass = False
        
        # Show image details
        print("\n  Image Details:")
        for i, img in enumerate(images[:6], 1):
            source = img.get("source", "unknown")
            url = img.get("url", "")[:60]
            print(f"    [{i}] {source}: {url}...")
    else:
        print(f"  ❌ FAIL: Only retrieved {len(images)} images (need 6)")
        image_pass = False
    
    # Final Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    all_pass = emoji_pass and url_pass and image_pass
    
    if emoji_pass:
        print("  ✅ Fix 1: No emojis/icons")
    else:
        print("  ❌ Fix 1: Emojis still present")
    
    if url_pass:
        print("  ✅ Fix 2: URLs converted to markdown links")
    else:
        print("  ❌ Fix 2: Raw URLs still present")
    
    if image_pass:
        print("  ✅ Fix 3: 6 unique images (no duplicates)")
    else:
        print("  ❌ Fix 3: Duplicate images found")
    
    print("="*70)
    
    if all_pass:
        print("\n🎉 ALL TESTS PASSED! Ready to generate London blog.")
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")
    
    return all_pass

if __name__ == "__main__":
    success = test_fixes()
    sys.exit(0 if success else 1)
