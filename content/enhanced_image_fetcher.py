"""
Enhanced Image Fetcher - Unsplash API 우선 + 일정별 테마 이미지
5MB 제한 준수, 다운사이징 지원, 다중 플랫폼 fallback
"""

from __future__ import annotations

import io
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple, BinaryIO
from loguru import logger


class EnhancedImageFetcher:
    """Unsplash API 우선 사용, 일정별 테마 이미지, 5MB 제한 준수"""
    
    def __init__(self):
        # API Keys
        self.unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY", "")
        self.pexels_key = os.getenv("PEXELS_API_KEY", "")
        self.pixabay_key = os.getenv("PIXABAY_API_KEY", "")
        
        # Settings
        self.max_size_mb = 5
        self.max_size_bytes = 5 * 1024 * 1024
        self.target_width = 1260
        self.target_height = 750
        
        # Usage tracking
        self.usage_file = Path(__file__).resolve().parents[1] / "data" / "image_usage.json"
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"EnhancedImageFetcher initialized")
        logger.info(f"  Unsplash API: {'Available' if self.unsplash_key else 'Not configured'}")
        logger.info(f"  Pexels API: {'Available' if self.pexels_key else 'Not configured'}")
        logger.info(f"  Pixabay API: {'Available' if self.pixabay_key else 'Not configured'}")
    
    def _load_usage(self) -> Dict:
        """API 사용량 로드"""
        if self.usage_file.exists():
            try:
                return json.loads(self.usage_file.read_text(encoding="utf-8"))
            except:
                pass
        return {"unsplash": [], "pexels": [], "pixabay": []}
    
    def _save_usage(self, usage: Dict):
        """API 사용량 저장"""
        self.usage_file.write_text(json.dumps(usage, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def _can_use_api(self, api_name: str, limit_per_hour: int = 50) -> bool:
        """API 사용 가능 여부 확인"""
        usage = self._load_usage()
        now = int(time.time())
        
        recent = [t for t in usage.get(api_name, []) if now - t < 3600]
        usage[api_name] = recent
        self._save_usage(usage)
        
        return len(recent) < limit_per_hour
    
    def _record_api_use(self, api_name: str):
        """API 사용 기록"""
        usage = self._load_usage()
        usage.setdefault(api_name, []).append(int(time.time()))
        self._save_usage(usage)
    
    def _check_image_size(self, url: str) -> Tuple[bool, int]:
        """이미지 크기 확인"""
        try:
            req = urllib.request.Request(url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Bot/1.0)')
            with urllib.request.urlopen(req, timeout=15) as resp:
                content_length = resp.headers.get('Content-Length')
                if content_length:
                    size = int(content_length)
                    return size <= self.max_size_bytes, size
                return True, 0
        except Exception as e:
            logger.warning(f"Could not check size for {url[:60]}: {e}")
            return True, 0
    
    def _validate_url(self, url: str) -> bool:
        """URL 유효성 확인"""
        try:
            req = urllib.request.Request(url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Bot/1.0)')
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.status == 200
        except Exception as e:
            return False
    
    def get_image_attribution(self, image: Dict) -> str:
        """이미지 출처 정보 생성"""
        source = image.get("source", "unknown")
        photographer = image.get("photographer", "Unknown")
        
        if source == "unsplash":
            photographer_url = image.get("photographer_url", "")
            unsplash_url = image.get("unsplash_url", "")
            if photographer_url and unsplash_url:
                return f"Photo by [{photographer}]({photographer_url}) on [Unsplash]({unsplash_url})"
            return f"Photo by {photographer} on Unsplash"
        
        elif source == "pexels":
            photographer_url = image.get("photographer_url", "")
            if photographer_url:
                return f"Photo by [{photographer}]({photographer_url}) on [Pexels](https://www.pexels.com)"
            return f"Photo by {photographer} on Pexels"
        
        elif source == "pixabay":
            return f"Photo by {photographer} on [Pixabay](https://pixabay.com)"
        
        elif source in ["pexels_static", "static"]:
            return f"Photo from Pexels (Free to use)"
        
        return f"Photo source: {source}"
    
    def get_all_attributions(self, images: List[Dict]) -> str:
        """모든 이미지의 출처 정보를 하나의 문자열로 반환"""
        attributions = []
        for i, img in enumerate(images, 1):
            attr = self.get_image_attribution(img)
            attributions.append(f"{i}. {attr}")
        return "\n".join(attributions)
    
    def _get_unsplash_images(self, query: str, count: int = 6) -> List[Dict]:
        """Unsplash API로 이미지 가져오기 (우선 순위 1)"""
        if not self.unsplash_key:
            logger.info("Unsplash API key not configured, skipping")
            return []
        
        if not self._can_use_api("unsplash", 50):
            logger.warning("Unsplash API hourly limit reached")
            return []
        
        try:
            url = f"https://api.unsplash.com/search/photos?query={urllib.parse.quote(query)}&per_page={count}&orientation=landscape"
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Client-ID {self.unsplash_key}")
            req.add_header("Accept-Version", "v1")
            
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = data.get("results", [])
                
                images = []
                for result in results[:count]:
                    img_url = result.get("urls", {}).get("regular", "")
                    if not img_url:
                        continue
                    
                    # 크기 확인
                    valid, size = self._check_image_size(img_url)
                    if not valid:
                        logger.warning(f"Unsplash image too large ({size} bytes), using smaller version")
                        # 작은 버전 사용
                        img_url = result.get("urls", {}).get("small", img_url)
                    
                    images.append({
                        "url": img_url,
                        "source": "unsplash",
                        "photographer": result.get("user", {}).get("name", "Unknown"),
                        "photographer_url": result.get("user", {}).get("links", {}).get("html", ""),
                        "unsplash_url": result.get("links", {}).get("html", ""),
                        "description": result.get("description") or result.get("alt_description") or query,
                        "width": result.get("width", 0),
                        "height": result.get("height", 0),
                    })
                
                if images:
                    self._record_api_use("unsplash")
                    logger.info(f"✅ Unsplash: {len(images)} images for '{query}'")
                
                return images
                
        except Exception as e:
            logger.error(f"Unsplash API error: {e}")
            return []
    
    def _get_pexels_images(self, query: str, count: int = 6) -> List[Dict]:
        """Pexels API로 이미지 가져오기 (우선 순위 2)"""
        if not self.pexels_key:
            logger.info("Pexels API key not configured, using static URLs")
            return self._get_pexels_static(query, count)
        
        if not self._can_use_api("pexels", 200):
            logger.warning("Pexels API hourly limit reached, using static")
            return self._get_pexels_static(query, count)
        
        try:
            url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page={count}&orientation=landscape"
            req = urllib.request.Request(url)
            req.add_header("Authorization", self.pexels_key)
            
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                photos = data.get("photos", [])
                
                images = []
                for photo in photos[:count]:
                    # 5MB 이하 버전 선택
                    src = photo.get("src", {})
                    img_url = src.get("large", src.get("medium", src.get("original", "")))
                    
                    if not img_url:
                        continue
                    
                    # 크기 확인
                    valid, size = self._check_image_size(img_url)
                    if not valid:
                        img_url = src.get("medium", img_url)
                    
                    images.append({
                        "url": img_url,
                        "source": "pexels",
                        "photographer": photo.get("photographer", "Unknown"),
                        "photographer_url": photo.get("photographer_url", ""),
                        "description": photo.get("alt", query),
                        "width": photo.get("width", 0),
                        "height": photo.get("height", 0),
                    })
                
                if images:
                    self._record_api_use("pexels")
                    logger.info(f"✅ Pexels API: {len(images)} images for '{query}'")
                
                return images
                
        except Exception as e:
            logger.error(f"Pexels API error: {e}, falling back to static")
            return self._get_pexels_static(query, count)
    
    def _get_pixabay_images(self, query: str, count: int = 6) -> List[Dict]:
        """Pixabay API로 이미지 가져오기 (우선 순위 3)"""
        if not self.pixabay_key:
            return []
        
        if not self._can_use_api("pixabay", 100):
            logger.warning("Pixabay API hourly limit reached")
            return []
        
        try:
            url = f"https://pixabay.com/api/?key={self.pixabay_key}&q={urllib.parse.quote(query)}&per_page={count}&orientation=horizontal&image_type=photo"
            
            with urllib.request.urlopen(url, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                hits = data.get("hits", [])
                
                images = []
                for hit in hits[:count]:
                    img_url = hit.get("webformatURL", hit.get("largeImageURL", ""))
                    
                    if not img_url:
                        continue
                    
                    # 크기 확인
                    valid, size = self._check_image_size(img_url)
                    if not valid:
                        img_url = hit.get("previewURL", img_url)
                    
                    images.append({
                        "url": img_url,
                        "source": "pixabay",
                        "photographer": hit.get("user", "Unknown"),
                        "description": hit.get("tags", query),
                        "width": hit.get("webformatWidth", 0),
                        "height": hit.get("webformatHeight", 0),
                    })
                
                if images:
                    self._record_api_use("pixabay")
                    logger.info(f"✅ Pixabay: {len(images)} images for '{query}'")
                
                return images
                
        except Exception as e:
            logger.error(f"Pixabay API error: {e}")
            return []
    
    def _get_pexels_static(self, city: str, count: int = 6) -> List[Dict]:
        """Pexels 정적 URL (API 제한시 fallback)"""
        # 정적 URL 매핑 (기존 코드 유지)
        pexels_static_urls = {
            "Prague": [
                "https://images.pexels.com/photos/164336/pexels-photo-164336.jpeg",
                "https://images.pexels.com/photos/163405/prague-czech-republic-old-town-163405.jpeg",
                "https://images.pexels.com/photos/154566/pexels-photo-154566.jpeg",
                "https://images.pexels.com/photos/142395/pexels-photo-142395.jpeg",
                "https://images.pexels.com/photos/131381/pexels-photo-131381.jpeg",
                "https://images.pexels.com/photos/157107/pexels-photo-157107.jpeg",
            ],
            # ... 더 많은 도시
        }
        
        urls = pexels_static_urls.get(city, [])
        if not urls:
            # 기본 이미지
            urls = [
                "https://images.pexels.com/photos/6243470/pexels-photo-6243470.jpeg",
                "https://images.pexels.com/photos/6243471/pexels-photo-6243471.jpeg",
                "https://images.pexels.com/photos/6243472/pexels-photo-6243472.jpeg",
            ]
        
        images = []
        for i, url in enumerate(urls[:count]):
            if self._validate_url(url):
                images.append({
                    "url": url + "?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                    "source": "pexels_static",
                    "photographer": "Pexels",
                    "description": f"{city} travel",
                })
        
        return images
    
    def get_city_images(self, city: str, country: str = "", days_plan: List[Dict] = None, count: int = 6) -> List[Dict]:
        """
        일정별 테마 이미지 가져오기
        
        Args:
            city: 도시명
            country: 국가명
            days_plan: 일별 일정 정보 (테마 매칭용)
            count: 필요한 이미지 수 (Hero + Day 1-5 = 6)
        """
        images = []
        
        # 일정별 검색어 생성
        queries = self._generate_day_queries(city, country, days_plan, count)
        
        logger.info(f"Getting images for {city}: {queries}")
        
        # 1. Unsplash API 우선 시도 (고품질)
        for query in queries:
            if len(images) >= count:
                break
            unsplash_imgs = self._get_unsplash_images(query, 2)
            for img in unsplash_imgs:
                if img not in images and self._validate_url(img["url"]):
                    images.append(img)
                    if len(images) >= count:
                        break
        
        # 2. Pexels API (CC0 라이선스)
        if len(images) < count:
            for query in queries:
                if len(images) >= count:
                    break
                pexels_imgs = self._get_pexels_images(query, 2)
                for img in pexels_imgs:
                    if img not in images and self._validate_url(img["url"]):
                        images.append(img)
                        if len(images) >= count:
                            break
        
        # 3. Pixabay API (추가 소스)
        if len(images) < count:
            for query in queries:
                if len(images) >= count:
                    break
                pixabay_imgs = self._get_pixabay_images(query, 2)
                for img in pixabay_imgs:
                    if img not in images and self._validate_url(img["url"]):
                        images.append(img)
                        if len(images) >= count:
                            break
        
        # 4. 정적 이미지 fallback
        if len(images) < count:
            static_imgs = self._get_pexels_static(city, count - len(images))
            for img in static_imgs:
                if img not in images:
                    images.append(img)
                    if len(images) >= count:
                        break
        
        logger.info(f"✅ Total images collected: {len(images)}")
        for i, img in enumerate(images):
            logger.info(f"  [{i}] {img['source']}: {img['url'][:60]}...")
        
        return images[:count]
    
    def _generate_day_queries(self, city: str, country: str, days_plan: List[Dict], count: int) -> List[str]:
        """일정별 검색어 생성"""
        queries = []
        
        # Hero 이미지용
        queries.append(f"{city} {country} travel landmark cityscape")
        
        if days_plan and len(days_plan) > 0:
            for day in days_plan[:5]:
                theme = day.get("theme", "")
                title = day.get("title", "")
                
                # 테마 기반 검색어 생성
                if "도착" in title or "적응" in theme:
                    queries.append(f"{city} airport arrival city center")
                elif "상징" in theme or "랜드마크" in theme:
                    queries.append(f"{city} famous landmark iconic")
                elif "문화" in theme or "예술" in theme or "박물관" in theme:
                    queries.append(f"{city} museum culture art")
                elif "해변" in theme or "휴양" in theme:
                    queries.append(f"{city} beach resort relax")
                elif "쇼핑" in theme or "마무리" in theme:
                    queries.append(f"{city} shopping street market")
                elif "음식" in theme or "맛집" in theme:
                    queries.append(f"{city} food restaurant local")
                elif "야경" in theme or "밤" in theme:
                    queries.append(f"{city} night view skyline")
                else:
                    queries.append(f"{city} travel destination")
        else:
            # 일정 정보 없으면 기본 쿼리
            queries.extend([
                f"{city} landmark",
                f"{city} street",
                f"{city} architecture",
                f"{city} food",
                f"{city} night",
            ])
        
        return queries[:count]


# 싱글톤 인스턴스
enhanced_image_fetcher = EnhancedImageFetcher()

# 기존 호환성을 위한 alias
image_fetcher = enhanced_image_fetcher
