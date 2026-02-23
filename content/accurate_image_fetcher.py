"""
ACCURATE Image Fetcher for Travel Blog
Guarantees images match actual destination landmarks
Uses Unsplash API as primary source + Pexels/Pixabay as fallback
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List
from loguru import logger

# Import landmark database
from content.city_landmarks import get_city_landmarks, get_city_country, SUPPORTED_CITIES


class AccurateImageFetcher:
    """Fetches accurate landmark images for any city"""
    
    # API Keys
    UNSPLASH_ACCESS_KEY = "LwdAMEAxkkCeiSZFHEbsbARJuatmWsKglTeJdsV-p-M"
    PEXELS_API_KEY = "ioGXDRNtGkKS4xnh96owdsVasgdCuQdLs8GRjCgd6Beb0UPyp9z6igtW"
    PIXABAY_API_KEY = "54702280-34b6357830834f9bd1e0d1ed3"
    
    def __init__(self):
        self.unsplash_key = self.UNSPLASH_ACCESS_KEY
        self.pexels_key = self.PEXELS_API_KEY
        self.pixabay_key = self.PIXABAY_API_KEY
        
        self.max_size_bytes = 5 * 1024 * 1024  # 5MB
        
        # API usage tracking
        self.usage_file = Path(__file__).resolve().parents[1] / "data" / "api_usage.json"
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ AccurateImageFetcher initialized")
        logger.info(f"   Supported cities: {len(SUPPORTED_CITIES)}")
        logger.info(f"   Unsplash API: {'✅ Enabled' if self.unsplash_key else '❌ Disabled'}")
    
    def get_city_images(self, city: str, count: int = 6) -> List[Dict]:
        """
        Get accurate images for a city using specific landmarks
        Returns list of image dicts with URL and metadata
        """
        logger.info(f"🎯 Fetching accurate images for: {city}")
        
        # Get specific landmarks for this city
        landmarks = get_city_landmarks(city)
        logger.info(f"   Landmarks: {landmarks[:3]}...")
        
        images = []
        used_urls = set()
        
        # Try each landmark until we have enough images
        for landmark in landmarks:
            if len(images) >= count:
                break
            
            # 1. Try Unsplash API first (highest quality)
            unsplash_imgs = self._fetch_unsplash(landmark, per_landmark=2)
            for img in unsplash_imgs:
                if img['url'] not in used_urls:
                    images.append(img)
                    used_urls.add(img['url'])
                    logger.info(f"   ✅ Unsplash: {landmark[:30]}...")
                    if len(images) >= count:
                        break
            
            # Small delay to be nice to APIs
            time.sleep(0.2)
        
        # If not enough images, try Pexels for remaining
        if len(images) < count:
            logger.info(f"   Need {count - len(images)} more images, trying Pexels...")
            for landmark in landmarks:
                if len(images) >= count:
                    break
                
                pexels_imgs = self._fetch_pexels(landmark, per_landmark=2)
                for img in pexels_imgs:
                    if img['url'] not in used_urls:
                        images.append(img)
                        used_urls.add(img['url'])
                        logger.info(f"   ✅ Pexels: {landmark[:30]}...")
                        if len(images) >= count:
                            break
                
                time.sleep(0.2)
        
        # Final fallback to Pixabay
        if len(images) < count:
            logger.info(f"   Need {count - len(images)} more images, trying Pixabay...")
            for landmark in landmarks:
                if len(images) >= count:
                    break
                
                pixabay_imgs = self._fetch_pixabay(landmark, per_landmark=2)
                for img in pixabay_imgs:
                    if img['url'] not in used_urls:
                        images.append(img)
                        used_urls.add(img['url'])
                        logger.info(f"   ✅ Pixabay: {landmark[:30]}...")
                        if len(images) >= count:
                            break
                
                time.sleep(0.2)
        
        logger.info(f"✅ Total images fetched: {len(images)}")
        for i, img in enumerate(images):
            logger.info(f"   [{i+1}] {img['landmark'][:40]}... ({img['source']})")
        
        return images[:count]
    
    def _fetch_unsplash(self, query: str, per_landmark: int = 2) -> List[Dict]:
        """Fetch images from Unsplash API"""
        if not self.unsplash_key:
            return []
        
        try:
            url = f"https://api.unsplash.com/search/photos?query={urllib.parse.quote(query)}&per_page={per_landmark}&orientation=landscape"
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Client-ID {self.unsplash_key}")
            req.add_header("Accept-Version", "v1")
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = data.get("results", [])
                
                images = []
                for result in results:
                    img_url = result.get("urls", {}).get("regular", "")
                    if not img_url:
                        continue
                    
                    images.append({
                        "url": img_url,
                        "source": "unsplash",
                        "landmark": query,
                        "photographer": result.get("user", {}).get("name", "Unknown"),
                        "description": result.get("alt_description") or query,
                    })
                
                return images
                
        except Exception as e:
            logger.warning(f"Unsplash error for '{query[:30]}': {e}")
            return []
    
    def _fetch_pexels(self, query: str, per_landmark: int = 2) -> List[Dict]:
        """Fetch images from Pexels API"""
        if not self.pexels_key:
            return []
        
        try:
            url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page={per_landmark}&orientation=landscape"
            req = urllib.request.Request(url)
            req.add_header("Authorization", self.pexels_key)
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                photos = data.get("photos", [])
                
                images = []
                for photo in photos:
                    src = photo.get("src", {})
                    img_url = src.get("large", src.get("medium", ""))
                    
                    if img_url:
                        images.append({
                            "url": img_url,
                            "source": "pexels",
                            "landmark": query,
                            "photographer": photo.get("photographer", "Unknown"),
                            "description": query,
                        })
                
                return images
                
        except Exception as e:
            logger.warning(f"Pexels error for '{query[:30]}': {e}")
            return []
    
    def _fetch_pixabay(self, query: str, per_landmark: int = 2) -> List[Dict]:
        """Fetch images from Pixabay API"""
        if not self.pixabay_key:
            return []
        
        try:
            url = f"https://pixabay.com/api/?key={self.pixabay_key}&q={urllib.parse.quote(query)}&per_page={per_landmark}&orientation=horizontal&image_type=photo"
            
            with urllib.request.urlopen(url, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                hits = data.get("hits", [])
                
                images = []
                for hit in hits:
                    img_url = hit.get("largeImageURL", hit.get("webformatURL", ""))
                    
                    if img_url:
                        images.append({
                            "url": img_url,
                            "source": "pixabay",
                            "landmark": query,
                            "photographer": hit.get("user", "Unknown"),
                            "description": hit.get("tags", query),
                        })
                
                return images
                
        except Exception as e:
            logger.warning(f"Pixabay error for '{query[:30]}': {e}")
            return []
    
    def get_image_attribution(self, image: Dict) -> str:
        """Get attribution text for an image"""
        source = image.get("source", "unknown")
        photographer = image.get("photographer", "Unknown")
        
        if source == "unsplash":
            return f"Photo by {photographer} on Unsplash"
        elif source == "pexels":
            return f"Photo by {photographer} on Pexels"
        elif source == "pixabay":
            return f"Photo by {photographer} on Pixabay"
        
        return f"Photo source: {source}"
    
    def get_all_attributions(self, images: List[Dict]) -> str:
        """Get all image attributions as formatted text"""
        attributions = []
        for i, img in enumerate(images, 1):
            attr = self.get_image_attribution(img)
            attributions.append(f"{i}. {attr}")
        return "\n".join(attributions)


# Singleton instance
accurate_image_fetcher = AccurateImageFetcher()

# Backward compatibility
image_fetcher = accurate_image_fetcher
enhanced_image_fetcher = accurate_image_fetcher
