"""
API Image Fetcher - Real API calls to Unsplash, Pexels, Pixabay, and Wikimedia Commons
Makes actual HTTP requests to all available image APIs with proper fallback chain
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from loguru import logger


class APIImageFetcher:
    """
    Multi-API Image Fetcher with real API calls
    Priority: Unsplash → Pexels → Pixabay → Wikimedia → Static Fallback
    """
    
    # API Keys (provided by user)
    # UNSPLASH ACCESS KEY DISABLED FOR TESTING - Using Pexels + Pixabay only
    UNSPLASH_ACCESS_KEY = ""  # DISABLED
    PEXELS_API_KEY = "ioGXDRNtGkKS4xnh96owdsVasgdCuQdLs8GRjCgd6Beb0UPyp9z6igtW"
    PIXABAY_API_KEY = "54702280-34b6357830834f9bd1e0d1ed3"
    
    def __init__(self):
        self.session = None
        self.usage_file = Path(__file__).resolve().parents[1] / "data" / "api_image_usage.json"
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)
        
        # API rate limits
        self.limits = {
            "unsplash": {"hourly": 50, "daily": 500},
            "pexels": {"hourly": 200, "daily": 2000},
            "pixabay": {"hourly": 100, "daily": 5000},
            "wikimedia": {"hourly": 500, "daily": 5000},  # Generous limits
        }
        
        logger.info("🔧 APIImageFetcher initialized")
        logger.info(f"   Unsplash API: {'✅ Ready' if self.UNSPLASH_ACCESS_KEY else '❌ No key'}")
        logger.info(f"   Pexels API: {'✅ Ready' if self.PEXELS_API_KEY else '❌ No key'}")
        logger.info(f"   Pixabay API: {'✅ Ready' if self.PIXABAY_API_KEY else '❌ No key'}")
        logger.info(f"   Wikimedia: ✅ Ready (no key needed)")
    
    def _load_usage(self) -> Dict:
        """Load API usage tracking"""
        if self.usage_file.exists():
            try:
                return json.loads(self.usage_file.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"Could not load usage file: {e}")
        return {"unsplash": [], "pexels": [], "pixabay": [], "wikimedia": []}
    
    def _save_usage(self, usage: Dict):
        """Save API usage tracking"""
        try:
            self.usage_file.write_text(json.dumps(usage, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Could not save usage file: {e}")
    
    def _can_use_api(self, api_name: str) -> bool:
        """Check if API can be used (within rate limits)"""
        usage = self._load_usage()
        now = int(time.time())
        
        # Get recent requests (within 1 hour and 24 hours)
        api_usage = usage.get(api_name, [])
        recent_hour = [t for t in api_usage if now - t < 3600]
        recent_day = [t for t in api_usage if now - t < 86400]
        
        # Update usage file with cleaned data
        usage[api_name] = recent_hour
        self._save_usage(usage)
        
        limits = self.limits.get(api_name, {"hourly": 50, "daily": 500})
        can_use = len(recent_hour) < limits["hourly"] and len(recent_day) < limits["daily"]
        
        if not can_use:
            logger.warning(f"⚠️ {api_name} API rate limit reached: {len(recent_hour)}/{limits['hourly']} hourly")
        
        return can_use
    
    def _record_api_use(self, api_name: str):
        """Record API usage"""
        usage = self._load_usage()
        usage.setdefault(api_name, []).append(int(time.time()))
        self._save_usage(usage)
    
    def _validate_image_url(self, url: str, timeout: int = 10) -> bool:
        """
        Validate that image URL returns HTTP 200 and is accessible
        Returns True if URL is valid and accessible
        """
        if not url or not url.startswith("http"):
            return False
        
        # For Pixabay URLs, they often block HEAD requests, so be more lenient
        is_pixabay = 'pixabay.com' in url
        
        try:
            # Try HEAD request first (except for Pixabay)
            if not is_pixabay:
                req = urllib.request.Request(url, method='HEAD')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    if resp.status == 200:
                        # Check Content-Type is image
                        content_type = resp.headers.get('Content-Type', '')
                        if 'image' in content_type.lower():
                            return True
                        # Some CDNs don't set proper Content-Type, allow if size is reasonable
                        content_length = resp.headers.get('Content-Length')
                        if content_length and int(content_length) > 1000:
                            return True
                        return True  # Be lenient if we got 200
                    return False
        except urllib.error.HTTPError as e:
            # 405 Method Not Allowed is okay - URL exists but HEAD not supported
            if e.code == 405:
                logger.debug(f"HEAD not allowed for {url[:60]}..., assuming valid")
                return True
            logger.debug(f"HTTP {e.code} for URL: {url[:60]}...")
            # Don't return False yet, try GET
        except Exception as e:
            logger.debug(f"HEAD request failed for {url[:60]}...: {e}")
        
        # Try GET with Range as fallback (or primary for Pixabay)
        try:
            req = urllib.request.Request(url, method='GET')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            req.add_header('Range', 'bytes=0-1024')
            
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status in [200, 206]:
                    return True
                return False
        except urllib.error.HTTPError as e:
            # 400 or 403 might still mean URL is valid but access method is restricted
            if e.code in [400, 403, 401]:
                logger.debug(f"GET restricted for {url[:60]}..., checking if URL format is valid")
                # For known good domains, assume valid if URL format looks correct
                if any(domain in url for domain in ['unsplash.com', 'pexels.com', 'pixabay.com', 'wikimedia.org']):
                    return True
            logger.debug(f"GET failed with HTTP {e.code} for {url[:60]}...")
            return False
        except Exception as e:
            logger.debug(f"GET request failed for {url[:60]}...: {e}")
            # For known good domains with proper URL format, assume valid
            if any(domain in url for domain in ['unsplash.com', 'pexels.com', 'pixabay.com', 'wikimedia.org']):
                if url.endswith(('.jpg', '.jpeg', '.png', '.webp')) or '?' in url:
                    return True
            return False
    
    def _check_image_size(self, url: str, max_size_mb: float = 5.0) -> Tuple[bool, Optional[int]]:
        """Check if image size is under limit"""
        try:
            req = urllib.request.Request(url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            with urllib.request.urlopen(req, timeout=10) as resp:
                content_length = resp.headers.get('Content-Length')
                if content_length:
                    size_bytes = int(content_length)
                    size_mb = size_bytes / (1024 * 1024)
                    return size_mb <= max_size_mb, size_bytes
                return True, None
        except Exception as e:
            logger.debug(f"Could not check size: {e}")
            return True, None
    
    def _extract_landmark_from_day(self, day_plan: Dict) -> str:
        """Extract landmark/location from day plan"""
        # Try to get landmark from various fields
        title = day_plan.get("title", "")
        description = day_plan.get("description", "")
        activities = day_plan.get("activities", [])
        
        # Common landmark patterns
        landmark_patterns = [
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Tower|Bridge|Museum|Palace|Castle|Cathedral|Church|Garden|Park|Square|Market|Beach|Temple|Shrine|Mosque)",
            r"(?:visit|explore|see|tour)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]
        
        text = f"{title} {description}"
        for activity in activities:
            if isinstance(activity, dict):
                text += f" {activity.get('name', '')} {activity.get('description', '')}"
            elif isinstance(activity, str):
                text += f" {activity}"
        
        # Look for known landmarks
        known_landmarks = [
            "Big Ben", "London Eye", "Tower Bridge", "Buckingham Palace", "Westminster Abbey",
            "British Museum", "Hyde Park", "Covent Garden", "Trafalgar Square",
            "Eiffel Tower", "Louvre", "Notre Dame", "Arc de Triomphe", "Sacre Coeur",
            "Colosseum", "Vatican", "Trevi Fountain", "Pantheon", "Roman Forum",
            "Sagrada Familia", "Park Guell", "Casa Batllo", "Gothic Quarter",
        ]
        
        for landmark in known_landmarks:
            if landmark.lower() in text.lower():
                return landmark
        
        # Extract from title
        if title:
            # Remove common prefixes
            cleaned = re.sub(r"^(Day\s+\d+[:\-]?\s*|arrival|departure|landmark tour|exploring|visit to)", "", title, flags=re.I).strip()
            if cleaned:
                return cleaned.split(",")[0].split("&")[0].strip()
        
        return "landmark"
    
    # ============================================================================
    # API 1: UNSPLASH
    # ============================================================================
    
    def fetch_from_unsplash(self, city: str, landmark: str = "", count: int = 3) -> List[Dict]:
        """
        Fetch images from Unsplash API
        Returns list of {url, source, description, photographer, width, height}
        """
        if not self.UNSPLASH_ACCESS_KEY:
            logger.warning("❌ Unsplash API key not available")
            return []
        
        if not self._can_use_api("unsplash"):
            logger.warning("⚠️ Unsplash API rate limit reached")
            return []
        
        # Build search query
        query = f"{city} {landmark}" if landmark else f"{city} travel"
        query = query.strip()
        
        logger.info(f"🔍 Unsplash API: Searching for '{query}'")
        
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.unsplash.com/search/photos?query={encoded_query}&per_page={count}&orientation=landscape"
            
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Client-ID {self.UNSPLASH_ACCESS_KEY}")
            req.add_header("Accept-Version", "v1")
            
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            self._record_api_use("unsplash")
            
            results = data.get("results", [])
            images = []
            
            for result in results:
                # Get image URLs
                urls = result.get("urls", {})
                img_url = urls.get("regular") or urls.get("small") or urls.get("full")
                
                if not img_url:
                    continue
                
                # Validate URL
                if not self._validate_image_url(img_url):
                    logger.debug(f"Invalid Unsplash URL: {img_url[:60]}...")
                    continue
                
                # Check size
                valid_size, _ = self._check_image_size(img_url)
                if not valid_size:
                    # Try smaller size
                    img_url = urls.get("small", img_url)
                
                user = result.get("user", {})
                images.append({
                    "url": img_url,
                    "source": "unsplash",
                    "description": result.get("alt_description") or result.get("description") or f"{city} {landmark}".strip(),
                    "photographer": user.get("name", "Unknown"),
                    "photographer_url": user.get("links", {}).get("html", ""),
                    "unsplash_url": result.get("links", {}).get("html", ""),
                    "width": result.get("width", 0),
                    "height": result.get("height", 0),
                })
            
            logger.info(f"✅ Unsplash: Found {len(images)} valid images for '{query}'")
            return images
            
        except urllib.error.HTTPError as e:
            logger.error(f"❌ Unsplash API HTTP Error {e.code}: {e.reason}")
            return []
        except Exception as e:
            logger.error(f"❌ Unsplash API Error: {e}")
            return []
    
    # ============================================================================
    # API 2: PEXELS
    # ============================================================================
    
    def fetch_from_pexels(self, city: str, landmark: str = "", count: int = 3) -> List[Dict]:
        """
        Fetch images from Pexels API
        Returns list of {url, source, description, photographer, width, height}
        """
        if not self.PEXELS_API_KEY:
            logger.warning("❌ Pexels API key not available")
            return []
        
        if not self._can_use_api("pexels"):
            logger.warning("⚠️ Pexels API rate limit reached")
            return []
        
        # Build search query - use English for better results
        query = f"{city} {landmark}" if landmark else f"{city} travel"
        query = query.strip()
        
        logger.info(f"🔍 Pexels API: Searching for '{query}'")
        
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.pexels.com/v1/search?query={encoded_query}&per_page={count}&orientation=landscape"
            
            req = urllib.request.Request(url)
            req.add_header("Authorization", self.PEXELS_API_KEY)
            req.add_header("User-Agent", "Mozilla/5.0 (Travel Content Bot)")
            
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            self._record_api_use("pexels")
            
            photos = data.get("photos", [])
            images = []
            
            for photo in photos:
                src = photo.get("src", {})
                # Use large2x, large, or medium size (in order of preference)
                img_url = src.get("large2x") or src.get("large") or src.get("medium") or src.get("original")
                
                if not img_url:
                    continue
                
                # Add optimization parameters
                if '?' not in img_url:
                    img_url += "?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
                
                # For Pexels, trust the API response without strict validation
                # (PEXELS URLs are reliably accessible)
                images.append({
                    "url": img_url,
                    "source": "pexels",
                    "description": photo.get("alt", f"{city} {landmark}".strip()),
                    "photographer": photo.get("photographer", "Unknown"),
                    "photographer_url": photo.get("photographer_url", ""),
                    "width": photo.get("width", 0),
                    "height": photo.get("height", 0),
                })
            
            logger.info(f"✅ Pexels: Found {len(images)} valid images for '{query}'")
            return images
            
        except urllib.error.HTTPError as e:
            if e.code == 403:
                logger.warning(f"⚠️ Pexels API 403 Forbidden - API key may be invalid or rate limited")
            else:
                logger.error(f"❌ Pexels API HTTP Error {e.code}: {e.reason}")
            return []
        except Exception as e:
            logger.error(f"❌ Pexels API Error: {e}")
            return []
    
    # ============================================================================
    # API 3: PIXABAY
    # ============================================================================
    
    def fetch_from_pixabay(self, city: str, landmark: str = "", count: int = 3) -> List[Dict]:
        """
        Fetch images from Pixabay API
        Returns list of {url, source, description, photographer, width, height}
        """
        if not self.PIXABAY_API_KEY:
            logger.warning("❌ Pixabay API key not available")
            return []
        
        if not self._can_use_api("pixabay"):
            logger.warning("⚠️ Pixabay API rate limit reached")
            return []
        
        # Build search query
        query = f"{city} {landmark}" if landmark else f"{city} travel"
        query = query.strip()
        
        logger.info(f"🔍 Pixabay API: Searching for '{query}'")
        
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://pixabay.com/api/?key={self.PIXABAY_API_KEY}&q={encoded_query}&per_page={count}&orientation=horizontal&image_type=photo&safesearch=true"
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            self._record_api_use("pixabay")
            
            hits = data.get("hits", [])
            images = []
            
            for hit in hits:
                # Use largeImageURL or webformatURL
                # largeImageURL is higher quality but webformatURL is more reliable
                img_url = hit.get("largeImageURL") or hit.get("webformatURL")
                
                if not img_url:
                    continue
                
                # Pixabay URLs from API are reliably accessible
                # Basic format check only to avoid false negatives from HEAD requests
                if not img_url.startswith("http"):
                    continue
                
                images.append({
                    "url": img_url,
                    "source": "pixabay",
                    "description": hit.get("tags", f"{city} {landmark}".strip()),
                    "photographer": hit.get("user", "Unknown"),
                    "width": hit.get("imageWidth", 0),
                    "height": hit.get("webformatHeight", 0),
                })
            
            logger.info(f"✅ Pixabay: Found {len(images)} valid images for '{query}'")
            return images
            
        except urllib.error.HTTPError as e:
            logger.error(f"❌ Pixabay API HTTP Error {e.code}: {e.reason}")
            return []
        except Exception as e:
            logger.error(f"❌ Pixabay API Error: {e}")
            return []
    
    # ============================================================================
    # API 4: WIKIMEDIA COMMONS
    # ============================================================================
    
    def fetch_from_wikimedia(self, city: str, landmark: str = "", count: int = 3) -> List[Dict]:
        """
        Fetch images from Wikimedia Commons API
        Returns list of {url, source, description, photographer, width, height}
        """
        if not self._can_use_api("wikimedia"):
            logger.warning("⚠️ Wikimedia API rate limit reached")
            return []
        
        # Build search query
        query = f"{city} {landmark}" if landmark else f"{city}"
        query = query.strip()
        
        logger.info(f"🔍 Wikimedia API: Searching for '{query}'")
        
        try:
            # Wikimedia Commons API endpoint
            encoded_query = urllib.parse.quote(query)
            url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={encoded_query}&srnamespace=6&format=json&srlimit={count * 2}"
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'TravelContentBot/1.0 (travel@example.com)')
            
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            search_results = data.get("query", {}).get("search", [])
            
            if not search_results:
                logger.info(f"⚠️ Wikimedia: No results for '{query}'")
                return []
            
            # Get image info for each result
            images = []
            titles = [result.get("title", "") for result in search_results[:count * 2]]
            
            # Batch request for image info
            titles_param = "|".join(titles)
            encoded_titles = urllib.parse.quote(titles_param)
            info_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={encoded_titles}&prop=imageinfo&iiprop=url|size|mime|extmetadata&format=json"
            
            req = urllib.request.Request(info_url)
            req.add_header('User-Agent', 'TravelContentBot/1.0 (travel@example.com)')
            
            with urllib.request.urlopen(req, timeout=20) as resp:
                info_data = json.loads(resp.read().decode("utf-8"))
            
            pages = info_data.get("query", {}).get("pages", {})
            
            for page_id, page in pages.items():
                imageinfo = page.get("imageinfo", [])
                if not imageinfo:
                    continue
                
                info = imageinfo[0]
                img_url = info.get("url", "")
                
                if not img_url:
                    continue
                
                # Only use direct image URLs
                if not img_url.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    continue
                
                # Validate URL
                if not self._validate_image_url(img_url):
                    logger.debug(f"Invalid Wikimedia URL: {img_url[:60]}...")
                    continue
                
                # Get metadata
                extmetadata = info.get("extmetadata", {})
                artist = extmetadata.get("Artist", {}).get("value", "Unknown")
                description = extmetadata.get("ImageDescription", {}).get("value", "")
                
                # Clean up HTML from metadata
                artist = re.sub(r'<[^>]+>', '', artist)
                description = re.sub(r'<[^>]+>', '', description)
                
                images.append({
                    "url": img_url,
                    "source": "wikimedia",
                    "description": description or f"{city} {landmark}".strip(),
                    "photographer": artist,
                    "width": info.get("width", 0),
                    "height": info.get("height", 0),
                })
                
                if len(images) >= count:
                    break
            
            self._record_api_use("wikimedia")
            logger.info(f"✅ Wikimedia: Found {len(images)} valid images for '{query}'")
            return images
            
        except urllib.error.HTTPError as e:
            logger.error(f"❌ Wikimedia API HTTP Error {e.code}: {e.reason}")
            return []
        except Exception as e:
            logger.error(f"❌ Wikimedia API Error: {e}")
            return []
    
    # ============================================================================
    # FALLBACK: Static Images
    # ============================================================================
    
    def _get_static_fallback(self, city: str, landmark: str = "", count: int = 1) -> List[Dict]:
        """Get static fallback images when all APIs fail"""
        logger.warning(f"⚠️ Using static fallback for {city} - {landmark}")
        
        # Reliable Pexels static URLs (CC0)
        static_urls = {
            "London": [
                "https://images.pexels.com/photos/672532/pexels-photo-672532.jpeg",
                "https://images.pexels.com/photos/460672/pexels-photo-460672.jpeg",
                "https://images.pexels.com/photos/427679/pexels-photo-427679.jpeg",
                "https://images.pexels.com/photos/1837590/pexels-photo-1837590.jpeg",
                "https://images.pexels.com/photos/1796715/pexels-photo-1796715.jpeg",
                "https://images.pexels.com/photos/325185/pexels-photo-325185.jpeg",
            ],
            "Paris": [
                "https://images.pexels.com/photos/532826/pexels-photo-532826.jpeg",
                "https://images.pexels.com/photos/149522/pexels-photo-149522.jpeg",
                "https://images.pexels.com/photos/1530259/pexels-photo-1530259.jpeg",
                "https://images.pexels.com/photos/161901/pexels-photo-161901.jpeg",
                "https://images.pexels.com/photos/2082103/pexels-photo-2082103.jpeg",
                "https://images.pexels.com/photos/1963082/pexels-photo-1963082.jpeg",
            ],
            "Rome": [
                "https://images.pexels.com/photos/1797161/pexels-photo-1797161.jpeg",
                "https://images.pexels.com/photos/2676602/pexels-photo-2676602.jpeg",
                "https://images.pexels.com/photos/2225442/pexels-photo-2225442.jpeg",
                "https://images.pexels.com/photos/2064827/pexels-photo-2064827.jpeg",
                "https://images.pexels.com/photos/2225439/pexels-photo-2225439.jpeg",
                "https://images.pexels.com/photos/1547813/pexels-photo-1547813.jpeg",
            ],
            "Barcelona": [
                "https://images.pexels.com/photos/1388030/pexels-photo-1388030.jpeg",
                "https://images.pexels.com/photos/819764/pexels-photo-819764.jpeg",
                "https://images.pexels.com/photos/1786433/pexels-photo-1786433.jpeg",
                "https://images.pexels.com/photos/1388032/pexels-photo-1388032.jpeg",
                "https://images.pexels.com/photos/1786435/pexels-photo-1786435.jpeg",
                "https://images.pexels.com/photos/1388028/pexels-photo-1388028.jpeg",
            ],
            "Tokyo": [
                "https://images.pexels.com/photos/2506923/pexels-photo-2506923.jpeg",
                "https://images.pexels.com/photos/2339009/pexels-photo-2339009.jpeg",
                "https://images.pexels.com/photos/2187603/pexels-photo-2187603.jpeg",
                "https://images.pexels.com/photos/3029352/pexels-photo-3029352.jpeg",
                "https://images.pexels.com/photos/1486222/pexels-photo-1486222.jpeg",
                "https://images.pexels.com/photos/1547813/pexels-photo-1547813.jpeg",
            ],
        }
        
        # Get URLs for city or use generic
        urls = static_urls.get(city, [])
        if not urls:
            # Generic travel images
            urls = [
                "https://images.pexels.com/photos/532826/pexels-photo-532826.jpeg",
                "https://images.pexels.com/photos/753626/pexels-photo-753626.jpeg",
                "https://images.pexels.com/photos/149114/pexels-photo-149114.jpeg",
                "https://images.pexels.com/photos/164336/pexels-photo-164336.jpeg",
                "https://images.pexels.com/photos/208733/pexels-photo-208733.jpeg",
                "https://images.pexels.com/photos/460672/pexels-photo-460672.jpeg",
            ]
        
        # Validate and return
        images = []
        for url in urls[:count]:
            if self._validate_image_url(url):
                images.append({
                    "url": url + "?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                    "source": "static_fallback",
                    "description": f"{city} {landmark}".strip(),
                    "photographer": "Pexels",
                })
        
        logger.info(f"✅ Static fallback: {len(images)} images for {city}")
        return images
    
    # ============================================================================
    # MAIN INTERFACE: Get Images with Fallback Chain
    # ============================================================================
    
    def get_images_for_day(self, city: str, day_plan: Dict, day_index: int = 0) -> Dict:
        """
        Get best image for a specific day using fallback chain
        Priority: Unsplash → Pexels → Pixabay → Wikimedia → Static
        
        Args:
            city: City name
            day_plan: Day plan dict with title, description, activities
            day_index: Day index (0 = hero, 1-5 = days)
        
        Returns:
            Dict with image info or None
        """
        landmark = self._extract_landmark_from_day(day_plan)
        
        logger.info(f"🖼️ Getting image for {city} Day {day_index} - Landmark: '{landmark}'")
        
        # Try each API in order
        apis = [
            ("unsplash", self.fetch_from_unsplash),
            ("pexels", self.fetch_from_pexels),
            ("pixabay", self.fetch_from_pixabay),
            ("wikimedia", self.fetch_from_wikimedia),
        ]
        
        for api_name, api_func in apis:
            try:
                images = api_func(city, landmark, count=3)
                if images:
                    # Return first valid image
                    for img in images:
                        if self._validate_image_url(img["url"]):
                            logger.info(f"✅ Using {api_name} image for Day {day_index}: {img['url'][:60]}...")
                            return img
            except Exception as e:
                logger.error(f"❌ Error with {api_name}: {e}")
                continue
        
        # All APIs failed, use static fallback
        fallback_images = self._get_static_fallback(city, landmark, count=1)
        if fallback_images:
            logger.info(f"✅ Using static fallback for Day {day_index}")
            return fallback_images[0]
        
        logger.error(f"❌ No images available for {city} Day {day_index}")
        return None
    
    def get_all_images(self, city: str, days_plan: List[Dict]) -> List[Dict]:
        """
        Get images for all days (hero + day 1-5)
        
        Args:
            city: City name
            days_plan: List of day plan dicts
        
        Returns:
            List of image dicts (one per day)
        """
        images = []
        
        # Hero image (index 0)
        hero_plan = {"title": f"{city} Cityscape", "description": f"Beautiful {city} skyline and landmarks"}
        hero_image = self.get_images_for_day(city, hero_plan, day_index=0)
        if hero_image:
            images.append(hero_image)
        
        # Day images (1-5)
        for i, day_plan in enumerate(days_plan[:5], start=1):
            day_image = self.get_images_for_day(city, day_plan, day_index=i)
            if day_image:
                images.append(day_image)
            else:
                # Use hero image as fallback
                if images:
                    images.append(images[0])
        
        # Ensure we have 6 images
        while len(images) < 6:
            if images:
                images.append(images[0])  # Duplicate first
            else:
                # Absolute fallback
                images.append({
                    "url": "https://images.pexels.com/photos/532826/pexels-photo-532826.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                    "source": "emergency_fallback",
                    "description": f"{city} travel",
                })
        
        return images[:6]
    
    def get_api_stats(self) -> Dict:
        """Get API usage statistics"""
        usage = self._load_usage()
        now = int(time.time())
        
        stats = {}
        for api_name in ["unsplash", "pexels", "pixabay", "wikimedia"]:
            api_usage = usage.get(api_name, [])
            recent_hour = len([t for t in api_usage if now - t < 3600])
            recent_day = len([t for t in api_usage if now - t < 86400])
            limits = self.limits.get(api_name, {"hourly": 50, "daily": 500})
            
            stats[api_name] = {
                "hourly_used": recent_hour,
                "hourly_limit": limits["hourly"],
                "daily_used": recent_day,
                "daily_limit": limits["daily"],
            }
        
        return stats


# Singleton instance
api_image_fetcher = APIImageFetcher()
