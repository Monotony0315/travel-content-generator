#!/usr/bin/env python3
"""
Test script for API Image Fetcher
Tests all 4 APIs (Unsplash, Pexels, Pixabay, Wikimedia) with London
"""

import sys
sys.path.insert(0, '/Users/angelhome_worker/Development/projects/travel-content-generator')

from content.api_image_fetcher import APIImageFetcher
from loguru import logger
import json

# Configure logger to show all levels
logger.remove()
logger.add(sys.stdout, level="DEBUG")

def test_all_apis():
    """Test all APIs individually"""
    fetcher = APIImageFetcher()
    
    print("\n" + "="*70)
    print("🧪 TESTING ALL IMAGE APIS")
    print("="*70)
    
    city = "London"
    landmark = "Big Ben"
    
    results = {
        "unsplash": {"called": False, "count": 0, "urls": []},
        "pexels": {"called": False, "count": 0, "urls": []},
        "pixabay": {"called": False, "count": 0, "urls": []},
        "wikimedia": {"called": False, "count": 0, "urls": []},
    }
    
    # Test 1: Unsplash
    print(f"\n📸 TEST 1: Unsplash API")
    print("-"*70)
    try:
        images = fetcher.fetch_from_unsplash(city, landmark, count=3)
        results["unsplash"]["called"] = True
        results["unsplash"]["count"] = len(images)
        for img in images:
            results["unsplash"]["urls"].append(img["url"])
            print(f"   ✅ {img['url'][:70]}...")
        print(f"   📊 Found {len(images)} images")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Pexels
    print(f"\n📸 TEST 2: Pexels API")
    print("-"*70)
    try:
        images = fetcher.fetch_from_pexels(city, landmark, count=3)
        results["pexels"]["called"] = True
        results["pexels"]["count"] = len(images)
        for img in images:
            results["pexels"]["urls"].append(img["url"])
            print(f"   ✅ {img['url'][:70]}...")
        print(f"   📊 Found {len(images)} images")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Pixabay
    print(f"\n📸 TEST 3: Pixabay API")
    print("-"*70)
    try:
        images = fetcher.fetch_from_pixabay(city, landmark, count=3)
        results["pixabay"]["called"] = True
        results["pixabay"]["count"] = len(images)
        for img in images:
            results["pixabay"]["urls"].append(img["url"])
            print(f"   ✅ {img['url'][:70]}...")
        print(f"   📊 Found {len(images)} images")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Wikimedia
    print(f"\n📸 TEST 4: Wikimedia Commons API")
    print("-"*70)
    try:
        images = fetcher.fetch_from_wikimedia(city, landmark, count=3)
        results["wikimedia"]["called"] = True
        results["wikimedia"]["count"] = len(images)
        for img in images:
            results["wikimedia"]["urls"].append(img["url"])
            print(f"   ✅ {img['url'][:70]}...")
        print(f"   📊 Found {len(images)} images")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    for api, data in results.items():
        status = "✅" if data["called"] and data["count"] > 0 else "❌"
        print(f"{status} {api.upper()}: Called={data['called']}, Images={data['count']}")
    
    # Save results
    with open("/Users/angelhome_worker/Development/projects/travel-content-generator/api_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to api_test_results.json")
    
    return results

def test_london_itinerary():
    """Test with London 5-day itinerary"""
    fetcher = APIImageFetcher()
    
    print("\n" + "="*70)
    print("🗺️ TESTING LONDON ITINERARY (6 IMAGES)")
    print("="*70)
    
    # London 5-day itinerary
    days_plan = [
        {
            "title": "Day 1: London Eye & Westminster",
            "description": "Arrive in London, visit London Eye and explore Westminster area including Big Ben",
            "activities": [
                {"name": "London Eye", "description": "Iconic Ferris wheel with panoramic views"},
                {"name": "Big Ben", "description": "Famous clock tower at Palace of Westminster"}
            ]
        },
        {
            "title": "Day 2: Tower Bridge & Tower of London",
            "description": "Explore historic Tower Bridge and the Tower of London",
            "activities": [
                {"name": "Tower Bridge", "description": "Victorian Gothic style bascule bridge"},
                {"name": "Tower of London", "description": "Historic castle and former prison"}
            ]
        },
        {
            "title": "Day 3: Buckingham Palace & Hyde Park",
            "description": "Royal London tour including Buckingham Palace and Hyde Park",
            "activities": [
                {"name": "Buckingham Palace", "description": "Official residence of the monarch"},
                {"name": "Hyde Park", "description": "Large royal park in central London"}
            ]
        },
        {
            "title": "Day 4: British Museum & Covent Garden",
            "description": "Cultural day at British Museum and Covent Garden",
            "activities": [
                {"name": "British Museum", "description": "World-renowned museum of human history"},
                {"name": "Covent Garden", "description": "Shopping and entertainment district"}
            ]
        },
        {
            "title": "Day 5: Camden Market & Shopping",
            "description": "Final day shopping at Camden Market and Oxford Street",
            "activities": [
                {"name": "Camden Market", "description": "Alternative fashion and crafts market"},
                {"name": "Oxford Street", "description": "Major shopping street in London"}
            ]
        }
    ]
    
    print(f"\n🖼️ Fetching 6 images for London (Hero + 5 Days)...")
    print("-"*70)
    
    images = fetcher.get_all_images("London", days_plan)
    
    print(f"\n📸 FETCHED IMAGES:")
    print("-"*70)
    for i, img in enumerate(images):
        day_label = "Hero" if i == 0 else f"Day {i}"
        print(f"\n[{day_label}] Source: {img.get('source', 'unknown')}")
        print(f"     URL: {img.get('url', 'N/A')[:70]}...")
        print(f"     Description: {img.get('description', 'N/A')[:50]}...")
    
    # Get API stats
    print("\n" + "-"*70)
    print("📊 API USAGE STATS:")
    stats = fetcher.get_api_stats()
    for api, data in stats.items():
        print(f"   {api}: {data['hourly_used']}/{data['hourly_limit']} hourly, {data['daily_used']}/{data['daily_limit']} daily")
    
    return images

if __name__ == "__main__":
    # Test all APIs
    test_all_apis()
    
    # Test London itinerary
    images = test_london_itinerary()
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)
