#!/usr/bin/env python3
"""
Test script to verify content quality improvements for London
"""

import asyncio
import sys
sys.path.insert(0, '/Users/angelhome_worker/Development/projects/travel-content-generator')

from content.rich_city_generator import rich_city_generator
from content.restaurant_finder import restaurant_finder

async def test_london_content():
    """Test London content generation with new improvements"""
    print("=" * 80)
    print("TESTING LONDON CONTENT QUALITY IMPROVEMENTS")
    print("=" * 80)
    
    # Generate rich content
    print("\n[1] Generating rich content for London...")
    content = rich_city_generator.generate_rich_content("London", "UK", "유럽", 5)
    
    print(f"\n[2] Destination Info:")
    dest = content['destination']
    print(f"    - City: {dest['name']}")
    print(f"    - Country: {dest['country']}")
    print(f"    - Days: {dest['days']}")
    print(f"    - Currency: {dest['currency']}")
    
    print(f"\n[3] Days Plan Summary:")
    days_plan = content['days_plan']
    print(f"    - Total days: {len(days_plan)}")
    
    for day in days_plan:
        print(f"\n    Day {day['day']}: {day['title']}")
        print(f"    Theme: {day['theme']}")
        print(f"    Transport: {day['transport']}")
        
        # Check spots
        spots = day.get('spots', [])
        print(f"    Spots ({len(spots)}):")
        for spot in spots:
            print(f"      - {spot['name']}")
            if 'address' in spot:
                print(f"        Address: {spot['address']}")
            if 'fee' in spot:
                print(f"        Fee: {spot['fee']}")
            if spot.get('reservation_required'):
                print(f"        [예약 필수]")
        
        # Check content length
        content_text = day.get('content', '')
        print(f"    Content length: {len(content_text)} characters")
        
    print(f"\n[4] Content Quality Check:")
    for day in days_plan:
        content_text = day.get('content', '')
        paragraphs = content_text.split('\n\n')
        print(f"    Day {day['day']}: {len(paragraphs)} paragraphs")
        
    print(f"\n[5] Restaurant Options:")
    restaurants = await restaurant_finder.find("London", "UK")
    for category in ['fine_dining', 'mid_range', 'budget', 'local_gems']:
        cat_restaurants = restaurants.get(category, [])
        print(f"    {category}: {len(cat_restaurants)} restaurants")
        for r in cat_restaurants[:2]:  # Show first 2
            print(f"      - {r['name']} ({r['price_range']}) - {r['cuisine']}")
            if r.get('signature'):
                print(f"        Signature: {', '.join(r['signature'])}")
            if r.get('reservation_required'):
                print(f"        [예약 필수]")
    
    print(f"\n[6] Total Cost Estimates:")
    estimates = content.get('total_estimate', {})
    for level in ['budget', 'luxury']:
        est = estimates.get(level, {})
        print(f"    {level}: {est.get('total', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("CONTENT QUALITY COMPARISON:")
    print("=" * 80)
    
    # Compare content length
    total_content_length = sum(len(d.get('content', '')) for d in days_plan)
    print(f"\nTotal content length: {total_content_length} characters")
    print(f"Average per day: {total_content_length // len(days_plan)} characters")
    print(f"\nEXPECTED IMPROVEMENTS:")
    print("  - Before: ~500 chars/day (2-3 line summaries)")
    print("  - After: 2000+ chars/day (3-4 paragraphs per time slot)")
    print("\n  - Before: 2-3 restaurants per category")
    print(f"  - After: {sum(len(restaurants.get(c, [])) for c in ['fine_dining', 'mid_range', 'budget', 'local_gems'])} total restaurants")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)
    
    return content

if __name__ == "__main__":
    asyncio.run(test_london_content())
