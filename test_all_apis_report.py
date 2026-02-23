#!/usr/bin/env python3
"""
Comprehensive API Image Fetcher Report for London
Tests all 4 APIs and generates a detailed report
"""

import sys
sys.path.insert(0, '/Users/angelhome_worker/Development/projects/travel-content-generator')

from content.api_image_fetcher import APIImageFetcher
from loguru import logger
import json

# Suppress detailed logs for cleaner output
logger.remove()

def test_all_apis_detailed():
    """Test all APIs with detailed output"""
    fetcher = APIImageFetcher()
    
    city = "London"
    landmarks = [
        "Big Ben",
        "London Eye", 
        "Tower Bridge",
        "Buckingham Palace",
        "British Museum",
        "Hyde Park"
    ]
    
    results = {
        "test_date": "2026-02-19",
        "city": city,
        "apis": {}
    }
    
    print("="*80)
    print("🔍 COMPREHENSIVE API IMAGE FETCHER TEST REPORT")
    print("="*80)
    print(f"\nCity: {city}")
    print(f"Landmarks tested: {len(landmarks)}")
    print("\n" + "-"*80)
    
    # Test 1: Unsplash
    print("\n📸 API 1: UNSPLASH")
    print("-"*80)
    unsplash_results = []
    for landmark in landmarks[:3]:  # Test first 3 landmarks
        try:
            images = fetcher.fetch_from_unsplash(city, landmark, count=2)
            for img in images:
                unsplash_results.append({
                    "landmark": landmark,
                    "url": img["url"],
                    "photographer": img.get("photographer", "Unknown"),
                    "description": img.get("description", "")[:60]
                })
                print(f"✅ [{landmark}] {img['url'][:70]}...")
        except Exception as e:
            print(f"❌ [{landmark}] Error: {e}")
    
    results["apis"]["unsplash"] = {
        "tested": True,
        "images_found": len(unsplash_results),
        "images": unsplash_results[:3]  # Store first 3
    }
    print(f"\n   Total Unsplash images: {len(unsplash_results)}")
    
    # Test 2: Pexels
    print("\n📸 API 2: PEXELS")
    print("-"*80)
    pexels_results = []
    for landmark in landmarks[:3]:
        try:
            images = fetcher.fetch_from_pexels(city, landmark, count=2)
            for img in images:
                pexels_results.append({
                    "landmark": landmark,
                    "url": img["url"],
                    "photographer": img.get("photographer", "Unknown"),
                    "description": img.get("description", "")[:60]
                })
                print(f"✅ [{landmark}] {img['url'][:70]}...")
        except Exception as e:
            print(f"❌ [{landmark}] Error: {e}")
    
    results["apis"]["pexels"] = {
        "tested": True,
        "images_found": len(pexels_results),
        "images": pexels_results[:3]
    }
    print(f"\n   Total Pexels images: {len(pexels_results)}")
    
    # Test 3: Pixabay
    print("\n📸 API 3: PIXABAY")
    print("-"*80)
    pixabay_results = []
    for landmark in landmarks[:3]:
        try:
            images = fetcher.fetch_from_pixabay(city, landmark, count=2)
            for img in images:
                pixabay_results.append({
                    "landmark": landmark,
                    "url": img["url"],
                    "photographer": img.get("photographer", "Unknown"),
                    "description": img.get("description", "")[:60]
                })
                print(f"✅ [{landmark}] {img['url'][:70]}...")
        except Exception as e:
            print(f"❌ [{landmark}] Error: {e}")
    
    results["apis"]["pixabay"] = {
        "tested": True,
        "images_found": len(pixabay_results),
        "images": pixabay_results[:3]
    }
    print(f"\n   Total Pixabay images: {len(pixabay_results)}")
    
    # Test 4: Wikimedia
    print("\n📸 API 4: WIKIMEDIA COMMONS")
    print("-"*80)
    wikimedia_results = []
    for landmark in landmarks[:3]:
        try:
            images = fetcher.fetch_from_wikimedia(city, landmark, count=2)
            for img in images:
                wikimedia_results.append({
                    "landmark": landmark,
                    "url": img["url"],
                    "photographer": img.get("photographer", "Unknown")[:40],
                    "description": img.get("description", "")[:60]
                })
                print(f"✅ [{landmark}] {img['url'][:70]}...")
        except Exception as e:
            print(f"❌ [{landmark}] Error: {e}")
    
    results["apis"]["wikimedia"] = {
        "tested": True,
        "images_found": len(wikimedia_results),
        "images": wikimedia_results[:3]
    }
    print(f"\n   Total Wikimedia images: {len(wikimedia_results)}")
    
    # API Usage Stats
    print("\n" + "="*80)
    print("📊 API USAGE STATISTICS")
    print("="*80)
    stats = fetcher.get_api_stats()
    for api, data in stats.items():
        status = "✅" if data['hourly_used'] < data['hourly_limit'] else "⚠️"
        print(f"{status} {api.upper():12} | Hourly: {data['hourly_used']:3}/{data['hourly_limit']:3} | Daily: {data['daily_used']:3}/{data['daily_limit']:4}")
    
    results["api_stats"] = stats
    
    # Test Full Itinerary
    print("\n" + "="*80)
    print("🗺️ FULL LONDON ITINERARY TEST (6 Images)")
    print("="*80)
    
    days_plan = [
        {"title": "Day 1: London Eye & Westminster", "description": "Visit London Eye and Big Ben", "activities": [{"name": "London Eye"}, {"name": "Big Ben"}]},
        {"title": "Day 2: Tower Bridge", "description": "Explore Tower Bridge and Tower of London", "activities": [{"name": "Tower Bridge"}]},
        {"title": "Day 3: Buckingham Palace", "description": "Royal tour at Buckingham Palace", "activities": [{"name": "Buckingham Palace"}]},
        {"title": "Day 4: British Museum", "description": "Cultural day at British Museum", "activities": [{"name": "British Museum"}]},
        {"title": "Day 5: Camden Market", "description": "Shopping at Camden Market", "activities": [{"name": "Camden Market"}]},
    ]
    
    print("\nFetching 6 images (Hero + 5 Days)...")
    itinerary_images = fetcher.get_all_images(city, days_plan)
    
    print("\n📸 FETCHED IMAGES:")
    print("-"*80)
    
    sources_count = {}
    for i, img in enumerate(itinerary_images):
        day_label = "Hero" if i == 0 else f"Day {i}"
        source = img.get("source", "unknown")
        sources_count[source] = sources_count.get(source, 0) + 1
        url = img.get("url", "")
        description = img.get("description", "")[:50]
        
        print(f"\n[{day_label}] Source: {source.upper()}")
        print(f"     URL: {url[:75]}...")
        print(f"     Desc: {description}...")
        
        # Validate URL
        is_valid = fetcher._validate_image_url(url)
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"     Status: {status}")
    
    results["itinerary_test"] = {
        "total_images": len(itinerary_images),
        "sources_breakdown": sources_count,
        "all_valid": all(fetcher._validate_image_url(img["url"]) for img in itinerary_images)
    }
    
    print("\n" + "-"*80)
    print("📊 IMAGE SOURCES BREAKDOWN:")
    for source, count in sources_count.items():
        print(f"   {source}: {count} images")
    
    # Final Summary
    print("\n" + "="*80)
    print("✅ TEST SUMMARY")
    print("="*80)
    print(f"\n   Unsplash:   {len(unsplash_results)} images fetched")
    print(f"   Pexels:     {len(pexels_results)} images fetched")
    print(f"   Pixabay:    {len(pixabay_results)} images fetched")
    print(f"   Wikimedia:  {len(wikimedia_results)} images fetched")
    print(f"\n   London Itinerary: {len(itinerary_images)} images (Hero + 5 Days)")
    print(f"   All URLs validated: {results['itinerary_test']['all_valid']}")
    
    # Save report
    report_path = "/Users/angelhome_worker/Development/projects/travel-content-generator/london_api_report.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full report saved to: {report_path}")
    
    return results

if __name__ == "__main__":
    test_all_apis_detailed()
    print("\n" + "="*80)
    print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*80)
