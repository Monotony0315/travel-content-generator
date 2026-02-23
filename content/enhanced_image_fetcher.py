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
    """Pexels + Pixabay API 우선 사용, 일정별 테마 이미지, 5MB 제한 준수 (Unsplash DISABLED)"""
    
    # API Keys (Hardcoded for consistency - Unsplash DISABLED for testing)
    UNSPLASH_ACCESS_KEY = ""  # DISABLED
    PEXELS_API_KEY = "ioGXDRNtGkKS4xnh96owdsVasgdCuQdLs8GRjCgd6Beb0UPyp9z6igtW"
    PIXABAY_API_KEY = "54702280-34b6357830834f9bd1e0d1ed3"
    
    def __init__(self):
        # API Keys - Use hardcoded values (Unsplash DISABLED)
        self.unsplash_key = ""  # DISABLED for testing
        self.pexels_key = self.PEXELS_API_KEY
        self.pixabay_key = self.PIXABAY_API_KEY
        
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
        """URL 유효성 확인 - HEAD 실패 시 GET 시도"""
        try:
            # 먼저 HEAD 요청 시도
            req = urllib.request.Request(url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except:
            # HEAD 실패하면 GET으로 첫 바이트만 확인
            try:
                req = urllib.request.Request(url, method='GET')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                req.add_header('Range', 'bytes=0-0')
                with urllib.request.urlopen(req, timeout=10) as resp:
                    return resp.status in [200, 206]
            except:
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
        """Unsplash API로 이미지 가져오기 (DISABLED FOR TESTING - Using Pexels + Pixabay only)"""
        logger.info("Unsplash API DISABLED for testing - skipping")
        return []  # DISABLED - Using Pexels + Pixabay only
        
        # Original code below (disabled):
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
            req.add_header("User-Agent", "Mozilla/5.0 (Travel Content Bot)")
            
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
        """Pexels 정적 URL (API 제한시 fallback) - 검증된 작동 URL 사용"""
        # 검증된 Pexels 정적 URL 매핑
        pexels_static_urls = {
            "Prague": [
                "https://images.pexels.com/photos/164336/pexels-photo-164336.jpeg",
                "https://images.pexels.com/photos/163405/pexels-photo-163405.jpeg",
                "https://images.pexels.com/photos/154566/pexels-photo-154566.jpeg",
                "https://images.pexels.com/photos/142395/pexels-photo-142395.jpeg",
                "https://images.pexels.com/photos/131381/pexels-photo-131381.jpeg",
                "https://images.pexels.com/photos/157107/pexels-photo-157107.jpeg",
            ],
            "Paris": [
                "https://images.pexels.com/photos/532826/pexels-photo-532826.jpeg",
                "https://images.pexels.com/photos/149114/pexels-photo-149114.jpeg",
                "https://images.pexels.com/photos/1461974/pexels-photo-1461974.jpeg",
                "https://images.pexels.com/photos/1308940/pexels-photo-1308940.jpeg",
                "https://images.pexels.com/photos/843037/pexels-photo-843037.jpeg",
                "https://images.pexels.com/photos/2817495/pexels-photo-2817495.jpeg",
                "https://images.pexels.com/photos/699466/pexels-photo-699466.jpeg",
                "https://images.pexels.com/photos/2082103/pexels-photo-2082103.jpeg",
                "https://images.pexels.com/photos/1963082/pexels-photo-1963082.jpeg",
                "https://images.pexels.com/photos/2344/cars-france-landmark-lights.jpg",
                "https://images.pexels.com/photos/161901/paris-sunset-eiffel-tower-champs-de-mars.jpg",
                "https://images.pexels.com/photos/1530259/pexels-photo-1530259.jpeg",
            ],
            "Rome": [
                "https://images.pexels.com/photos/753626/pexels-photo-753626.jpeg",
                "https://images.pexels.com/photos/2676602/pexels-photo-2676602.jpeg",
                "https://images.pexels.com/photos/2225442/pexels-photo-2225442.jpeg",
                "https://images.pexels.com/photos/2064827/pexels-photo-2064827.jpeg",
            ],
            "Barcelona": [
                "https://images.pexels.com/photos/819764/pexels-photo-819764.jpeg",
                "https://images.pexels.com/photos/1388030/pexels-photo-1388030.jpeg",
                "https://images.pexels.com/photos/2567788/pexels-photo-2567788.jpeg",
                "https://images.pexels.com/photos/1386444/pexels-photo-1386444.jpeg",
                "https://images.pexels.com/photos/1874675/pexels-photo-1874675.jpeg",
                "https://images.pexels.com/photos/3757144/pexels-photo-3757144.jpeg",
                "https://images.pexels.com/photos/1268855/pexels-photo-1268855.jpeg",
            ],
            "London": [
                "https://images.pexels.com/photos/460672/pexels-photo-460672.jpeg",
                "https://images.pexels.com/photos/1796715/pexels-photo-1796715.jpeg",
                "https://images.pexels.com/photos/325185/pexels-photo-325185.jpeg",
                "https://images.pexels.com/photos/427679/pexels-photo-427679.jpeg",
            ],
            "Amsterdam": [
                "https://images.pexels.com/photos/208733/pexels-photo-208733.jpeg",
                "https://images.pexels.com/photos/161001/pexels-photo-161001.jpeg",
                "https://images.pexels.com/photos/248149/pexels-photo-248149.jpeg",
            ],
        }
        
        urls = pexels_static_urls.get(city, [])
        
        # 도시별 URL이 없으면 유럽/여행 일반 이미지 사용
        if not urls:
            urls = [
                "https://images.pexels.com/photos/532826/pexels-photo-532826.jpeg",
                "https://images.pexels.com/photos/149114/pexels-photo-149114.jpeg",
                "https://images.pexels.com/photos/753626/pexels-photo-753626.jpeg",
                "https://images.pexels.com/photos/164336/pexels-photo-164336.jpeg",
                "https://images.pexels.com/photos/208733/pexels-photo-208733.jpeg",
                "https://images.pexels.com/photos/460672/pexels-photo-460672.jpeg",
                "https://images.pexels.com/photos/699466/pexels-photo-699466.jpeg",
                "https://images.pexels.com/photos/2082103/pexels-photo-2082103.jpeg",
                "https://images.pexels.com/photos/1461974/pexels-photo-1461974.jpeg",
                "https://images.pexels.com/photos/1308940/pexels-photo-1308940.jpeg",
                "https://images.pexels.com/photos/843037/pexels-photo-843037.jpeg",
                "https://images.pexels.com/photos/2817495/pexels-photo-2817495.jpeg",
            ]
        
        images = []
        for i, url in enumerate(urls[:count]):
            # URL 검증 (HEAD 요청이 실패할 수 있으므로 GET으로 변경)
            try:
                req = urllib.request.Request(url, method='GET')
                req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Bot/1.0)')
                req.add_header('Range', 'bytes=0-0')  # Only fetch first byte to check if valid
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status in [200, 206]:  # 206 = Partial Content
                        images.append({
                            "url": url + "?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                            "source": "pexels_static",
                            "photographer": "Pexels",
                            "description": f"{city} travel",
                        })
            except Exception as e:
                logger.debug(f"Static URL failed: {url[:60]}... - {e}")
                continue
        
        logger.info(f"Static fallback: {len(images)} valid images for {city}")
        return images
    
    def _get_image_url_key(self, url: str) -> str:
        """URL에서 고유 식별자 추출 (중복 체크용)"""
        # 쿼리 파라미터 제거하고 기본 URL 비교
        return url.split('?')[0].strip()
    
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
        used_urls = set()  # URL 중복 체크용
        
        # 일정별 검색어 생성
        queries = self._generate_day_queries(city, country, days_plan, count)
        
        logger.info(f"Getting images for {city}: {queries}")
        
        # 1. 먼저 정적 이미지로 기본 확보 (city-specific)
        static_imgs = self._get_pexels_static(city, count)
        for img in static_imgs:
            url_key = self._get_image_url_key(img["url"])
            if url_key not in used_urls:
                images.append(img)
                used_urls.add(url_key)
                if len(images) >= count:
                    break
        
        # 2. Unsplash API 우선 시도 (고품질)
        if len(images) < count:
            for query in queries:
                if len(images) >= count:
                    break
                unsplash_imgs = self._get_unsplash_images(query, 2)
                for img in unsplash_imgs:
                    url_key = self._get_image_url_key(img["url"])
                    if url_key not in used_urls and self._validate_url(img["url"]):
                        images.append(img)
                        used_urls.add(url_key)
                        if len(images) >= count:
                            break
        
        # 3. Pexels API (CC0 라이선스)
        if len(images) < count:
            for query in queries:
                if len(images) >= count:
                    break
                pexels_imgs = self._get_pexels_images(query, 2)
                for img in pexels_imgs:
                    url_key = self._get_image_url_key(img["url"])
                    if url_key not in used_urls and self._validate_url(img["url"]):
                        images.append(img)
                        used_urls.add(url_key)
                        if len(images) >= count:
                            break
        
        # 4. Pixabay API (추가 소스)
        if len(images) < count:
            for query in queries:
                if len(images) >= count:
                    break
                pixabay_imgs = self._get_pixabay_images(query, 2)
                for img in pixabay_imgs:
                    url_key = self._get_image_url_key(img["url"])
                    if url_key not in used_urls and self._validate_url(img["url"]):
                        images.append(img)
                        used_urls.add(url_key)
                        if len(images) >= count:
                            break
        
        # 5. 정적 이미지로 부족분 보충
        if len(images) < count:
            additional_static = self._get_pexels_static(city, count)
            for img in additional_static:
                url_key = self._get_image_url_key(img["url"])
                if url_key not in used_urls:
                    images.append(img)
                    used_urls.add(url_key)
                    if len(images) >= count:
                        break
        
        logger.info(f"✅ Total images collected: {len(images)}")
        for i, img in enumerate(images):
            logger.info(f"  [{i}] {img['source']}: {img['url'][:60]}...")
        
        return images[:count]
    
    def _generate_day_queries(self, city: str, country: str, days_plan: List[Dict], count: int) -> List[str]:
        """일정별 검색어 생성 - 도시별 특정 랜드마크 사용"""
        queries = []
        
        # 도시별 특정 랜드마크 매핑
        CITY_LANDMARKS = {
            "Vienna": ["Schönbrunn Palace Vienna", "St. Stephen's Cathedral Vienna", "Belvedere Palace Vienna", 
                      "Hofburg Palace Vienna", "Prater Vienna Giant Wheel", "Vienna State Opera"],
            "London": ["Big Ben London", "Tower Bridge London", "Buckingham Palace London", 
                      "British Museum London", "Westminster Abbey London", "London Eye"],
            "Paris": ["Eiffel Tower Paris", "Louvre Museum Paris", "Notre-Dame Cathedral Paris", 
                     "Arc de Triomphe Paris", "Sacré-Cœur Paris", "Seine River Paris"],
            "Rome": ["Colosseum Rome", "Vatican City Rome", "Trevi Fountain Rome", 
                    "Pantheon Rome", "Roman Forum Rome", "Spanish Steps Rome"],
            "Amsterdam": ["Amsterdam Canal houses", "Rijksmuseum Amsterdam", "Anne Frank House Amsterdam", 
                         "Van Gogh Museum Amsterdam", "Dam Square Amsterdam", "Vondelpark Amsterdam"],
            "Prague": ["Prague Castle", "Charles Bridge Prague", "Old Town Square Prague", 
                      "Prague Astronomical Clock", "St. Vitus Cathedral Prague", "Prague Jewish Quarter"],
            "Barcelona": ["Sagrada Familia Barcelona", "Park Güell Barcelona", "Casa Batlló Barcelona", 
                         "Gothic Quarter Barcelona", "La Rambla Barcelona", "Camp Nou Barcelona"],
            "Florence": ["Duomo Florence", "Uffizi Gallery Florence", "Ponte Vecchio Florence",
                        "David Michelangelo Florence", "Palazzo Vecchio Florence", "Boboli Gardens Florence"],
            "Venice": ["Grand Canal Venice", "St. Mark's Square Venice", "Rialto Bridge Venice",
                      "Doge's Palace Venice", "Burano Island Venice", "Gondola Venice"],
        }
        
        # 해당 도시의 랜드마크 가져오기
        landmarks = CITY_LANDMARKS.get(city, [f"{city} famous landmark", f"{city} iconic place"])
        
        # Hero 이미지용 - 첫 번째 랜드마크 사용
        queries.append(f"{landmarks[0]} exterior view")
        
        if days_plan and len(days_plan) > 0:
            for i, day in enumerate(days_plan[:5]):
                theme = day.get("theme", "")
                title = day.get("title", "")
                
                # 테마 기반 검색어 생성 + 특정 랜드마크 사용
                if "도착" in title or "적응" in theme:
                    queries.append(f"{city} city center aerial view")
                elif "상징" in theme or "랜드마크" in theme:
                    landmark_idx = min(1, len(landmarks)-1)
                    queries.append(f"{landmarks[landmark_idx]} exterior architecture")
                elif "문화" in theme or "예술" in theme or "박물관" in theme:
                    landmark_idx = min(2, len(landmarks)-1)
                    queries.append(f"{landmarks[landmark_idx]} interior museum")
                elif "쇼핑" in theme or "마무리" in theme:
                    queries.append(f"{city} shopping street cafe")
                elif "음식" in theme or "맛집" in theme:
                    queries.append(f"{city} traditional food restaurant")
                elif "야경" in theme or "밤" in theme:
                    landmark_idx = min(3, len(landmarks)-1)
                    queries.append(f"{landmarks[landmark_idx]} night illuminated")
                else:
                    landmark_idx = i % len(landmarks)
                    queries.append(f"{landmarks[landmark_idx]} scenic view")
        else:
            # 일정 정보 없으면 랜드마크 순환 사용
            for i in range(5):
                landmark_idx = i % len(landmarks)
                queries.append(f"{landmarks[landmark_idx]} beautiful view")
        
        return queries[:count]


# 싱글톤 인스턴스
enhanced_image_fetcher = EnhancedImageFetcher()

# 기존 호환성을 위한 alias
image_fetcher = enhanced_image_fetcher
# 기존 호환성을 위한 alias
image_fetcher = enhanced_image_fetcher
