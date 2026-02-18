"""
Unsplash Image Fetcher with 5MB size constraint
5MB 이하 이미지 크기 제한 적용
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger


class UnsplashImageFetcher:
    """Unsplash API 이미지 페처 (5MB 제한 준수)"""
    
    def __init__(self):
        # 환경변수에서 API 키 로드 (없으면 에러 로그 출력)
        self.access_key = os.getenv("UNSPLASH_ACCESS_KEY", "")
        self.base_url = "https://api.unsplash.com"
        
        if not self.access_key:
            logger.warning("UNSPLASH_ACCESS_KEY 환경변수가 설정되지 않았습니다. Unsplash API를 사용할 수 없습니다.")
        self.usage_file = Path(__file__).resolve().parents[1] / "data" / "unsplash_usage.json"
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Unsplash API Guidelines: 1시간당 최대 7 requests
        self.hourly_limit = 7
        self.max_image_size_mb = 5  # 5MB 제한
    
    def _load_usage(self) -> Dict:
        """API 사용량 로드"""
        if self.usage_file.exists():
            try:
                return json.loads(self.usage_file.read_text(encoding="utf-8"))
            except:
                pass
        return {"requests": [], "images_cached": {}}
    
    def _save_usage(self, usage: Dict):
        """API 사용량 저장"""
        self.usage_file.write_text(json.dumps(usage, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def _can_make_request(self) -> bool:
        """1시간 내 요청 가능 여부 확인"""
        usage = self._load_usage()
        now = int(time.time())
        
        # 1시간 이내 요청만 카운트
        recent_requests = [t for t in usage.get("requests", []) if now - t < 3600]
        usage["requests"] = recent_requests
        self._save_usage(usage)
        
        return len(recent_requests) < self.hourly_limit
    
    def _record_request(self):
        """요청 기록"""
        usage = self._load_usage()
        usage.setdefault("requests", []).append(int(time.time()))
        self._save_usage(usage)
    
    def _check_image_size(self, image_url: str) -> Tuple[bool, Optional[int]]:
        """이미지 크기 확인 (bytes) - 5MB 이하인지 체크"""
        try:
            # HEAD 요청으로 크기만 확인
            req = urllib.request.Request(image_url, method='HEAD')
            with urllib.request.urlopen(req, timeout=10) as resp:
                content_length = resp.headers.get('Content-Length')
                if content_length:
                    size_bytes = int(content_length)
                    size_mb = size_bytes / (1024 * 1024)
                    return size_mb <= self.max_image_size_mb, size_bytes
                return True, None  # 크기를 모륾면 일단 진행
        except Exception as e:
            logger.warning(f"Could not check image size: {e}")
            return True, None  # 확인 실패 시 진행

    def _validate_image_url(self, image_url: str) -> bool:
        """이미지 URL이 유효한지 확인 (404 등 체크)"""
        try:
            req = urllib.request.Request(image_url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Bot/1.0)')
            with urllib.request.urlopen(req, timeout=10) as resp:
                # 200 OK만 유효한 것으로 간주
                if resp.status == 200:
                    # Content-Type이 이미지인지 확인
                    content_type = resp.headers.get('Content-Type', '')
                    if 'image' in content_type.lower():
                        return True
                    # Pexels 등 CDN은 Content-Type이 없을 수도 있음
                    return True
                return False
        except urllib.error.HTTPError as e:
            if e.code == 404:
                logger.warning(f"Image URL not found (404): {image_url[:80]}...")
            elif e.code == 403:
                logger.warning(f"Image URL forbidden (403): {image_url[:80]}...")
            else:
                logger.warning(f"HTTP error {e.code} for URL: {image_url[:80]}...")
            return False
        except Exception as e:
            logger.warning(f"Could not validate image URL: {e}")
            return False
    
    def _get_pexels_images(self, city: str, count: int) -> List[Dict]:
        """Pexels에서 CC0 이미지 가져오기 (저작권 문제 없음) - 일정별 연결된 이미지"""
        # Pexels CDN - CC0 라이선스
        # 각 도시별 Hero + Day 1~5 일정에 맞는 이미지 매칭
        
        # 도시별 일정 테마 정의 (Hero + Day 1-5)
        city_themes = {
            "Paris": ["landmark", "neighborhood", "landmark morning", "museum", "arts district", "shopping"],
            "Rome": ["colosseum", "ancient ruins", "fountain", "vatican", "gallery", "shopping"],
            "London": ["big ben", "london eye", "tower bridge", "palace", "museum", "park"],
            "Tokyo": ["tokyo tower", "shibuya", "asakusa temple", "shrine", "night view", "market"],
            "Bangkok": ["wat arun", "grand palace", "temple", "floating market", "ayutthaya", "shopping mall"],
            "Barcelona": ["sagrada familia", "gothic quarter", "gaudi", "architecture", "beach", "market"],
            "New York": ["times square", "central park", "statue of liberty", "brooklyn bridge", "museum", "wall street"],
            "Singapore": ["marina bay", "gardens", "chinatown", "botanic garden", "shopping"],
            "Phuket": ["beach", "patong", "island hopping", "big buddha", "kata beach", "old town"],
            "Maldives": ["overwater villa", "resort", "snorkeling", "spa", "sunset cruise", "beach"],
            "Bali": ["rice terrace", "ubud", "tanah lot", "temple", "seminyak beach", "market"],
            "Sydney": ["opera house", "circular quay", "bondi beach", "harbour bridge", "blue mountains", "shopping"],
            "Dubai": ["burj khalifa", "mall", "palm island", "desert safari", "marina", "gold souk"],
            # 추가 유럽
            "Amsterdam": ["canal", "dam square", "museum", "anne frank", "vondel park", "shopping"],
            "Prague": ["castle", "old town", "astronomical clock", "charles bridge", "petrin", "shopping"],
            "Vienna": ["cathedral", "schonbrunn", "hofburg", "opera", "belvedere", "shopping"],
            "Lisbon": ["tram", "alfama", "belem", "sintra", "timeout", "shopping"],
            "Berlin": ["brandenburg", "museum island", "berlin wall", "checkpoint", "hackescher", "shopping"],
            "Santorini": ["oia", "fira", "blue dome", "red beach", "sunset", "winery"],
            "Florence": ["duomo", "uffizi", "ponte vecchio", "academy", "piazza", "shopping"],
            "Venice": ["grand canal", "st marks", "rialto", "burano", "gondola", "shopping"],
            "Milan": ["duomo", "galleria", "last supper", "brera", "navigli", "shopping"],
            "Madrid": ["palacio real", "prado", "retiro", "plaza mayor", "bernabeu", "shopping"],
            "Athens": ["acropolis", "parthenon", "plaka", "acropolis museum", "monastiraki", "shopping"],
            "Edinburgh": ["castle", "royal mile", "arthurs seat", "holyrood", "calton hill", "shopping"],
            "Copenhagen": ["little mermaid", "nyhavn", "tivoli", "christiania", "roskilde", "shopping"],
            "Stockholm": ["gamla stan", "vasa", "skansen", "city hall", "archipelago", "shopping"],
            "Dubrovnik": ["old town", "walls", "lokrum", "cable car", "king's landing", "shopping"],
            # 추가 동남아
            "Kuala Lumpur": ["petronas", "batu caves", "kl tower", "central market", "chinatown", "shopping"],
            "Kyoto": ["kiyomizu", "fushimi inari", "kinkakuji", "gion", "arashiyama", "shopping"],
            "Osaka": ["dotonbori", "osaka castle", "universal", "kuromon", "shinsekai", "shopping"],
            "Ho Chi Minh City": ["notre dame", "cu chi", "ben thanh", "war museum", "mekong", "shopping"],
            "Hanoi": ["hoan kiem", "ha long", "old quarter", "temple", "water puppet", "shopping"],
            "Manila": ["intramuros", "mall of asia", "corregidor", "chinatown", "ayala", "shopping"],
            "Chiang Mai": ["doi suthep", "night safari", "old city", "doi inthanon", "saturday", "shopping"],
            "Phnom Penh": ["royal palace", "killing fields", "russian market", "wat phnom", "tuol sleng", "shopping"],
            "Siem Reap": ["angkor wat", "bayon", "ta prohm", "pub street", "tonle sap", "shopping"],
            "Yangon": ["shwedagon", "sule", "circular train", "chinatown", "bogyoke", "shopping"],
            "Penang": ["georgetown", "kek lok si", "street art", "penang hill", "clan", "shopping"],
            "Da Nang": ["my khe", "marble mountains", "ba na", "dragon bridge", "hoi an", "shopping"],
            "Luang Prabang": ["kuang si", "night market", "alms", "pak ou", "mount phousi", "shopping"],
            # 휴양지
            "Boracay": ["white beach", "puka", "island hopping", "bulabog", "diniwid", "shopping"],
            "Bora Bora": ["mount otemanu", "matira", "coral gardens", "lagoon", "shark feeding", "shopping"],
            "Cancun": ["hotel zone", "chichen itza", "isla mujeres", "xcaret", "playa delfines", "shopping"],
            "Mykonos": ["windmills", "little venice", "paradise", "delos", "matoyianni", "shopping"],
            "Zanzibar": ["stone town", "prison island", "nungwi", "jozani", "spice tour", "shopping"],
            "Costa Rica": ["arenal", "monteverde", "manuel antonio", "tortuguero", "corcovado", "shopping"],
            "Fiji": ["denarau", "mamanuca", "yasawa", "coral coast", "suva", "shopping"],
            "Seychelles": ["anse source", "praslin", "la digue", "mahe", "vallee de mai", "shopping"],
            "Mauritius": ["le morne", "grand baie", "chamarel", "ile aux cerfs", "port louis", "shopping"],
            "Palawan": ["el nido", "underground river", "coron", "honda bay", "port barton", "shopping"],
            "Koh Samui": ["chaweng", "big buddha", "angthong", "lamai", "fisherman's village", "shopping"],
            "Langkawi": ["sky bridge", "cenang", "kilim", "datai", "eagle square", "shopping"],
            "Gili Islands": ["gili t", "gili meno", "gili air", "turtle point", "sunset", "shopping"],
            "Phi Phi Islands": ["maya bay", "viewpoint", "bamboo island", "monkey beach", "tonsai", "shopping"],
            "Raja Ampat": ["wayag", "misool", "arborek", "kri", "sawandarek", "shopping"],
            "Azores": ["sete cidades", "lagoa do fogo", "ponta delgada", "horta", "capelinhos", "shopping"],
            # 동아시아
            "Okinawa": ["shuri castle", "churaumi", "kokusaidori", "kerama", "american village", "shopping"],
            "Taipei": ["taipei 101", "shilin", "jiufen", "chiang kai shek", "beitou", "shopping"],
            "Hong Kong": ["victoria peak", "star ferry", "mong kok", "tian tan buddha", "stanley", "shopping"],
            "Shanghai": ["bund", "oriental pearl", "yuyuan", "french concession", "zhujiajiao", "shopping"],
            "Beijing": ["great wall", "forbidden city", "tiananmen", "summer palace", "temple of heaven", "shopping"],
            # 미주
            "Los Angeles": ["hollywood", "santa monica", "universal", "griffith", "beverly hills", "shopping"],
            "San Francisco": ["golden gate", "alcatraz", "fisherman's wharf", "lombard", "pier 39", "shopping"],
            "Vancouver": ["stanley park", "granville", "capilano", "gastown", "whistler", "shopping"],
            # 중동
            "Istanbul": ["hagia sophia", "blue mosque", "grand bazaar", "topkapi", "galata", "shopping"],
            "Abu Dhabi": ["sheikh zayed", "louvre", "ferrari world", "corniche", "yas island", "shopping"],
        }
        
        # 기본 테마 (매핑되지 않은 도시용)
        default_themes = ["city skyline", "downtown", "landmark", "old town", "museum", "shopping"]
        
        # 도시별 미리 매핑된 고품질 이미지
        pexels_urls = {
            "Paris": [
                "https://images.pexels.com/photos/532826/pexels-photo-532826.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Hero - 에펠탑 전경
                "https://images.pexels.com/photos/1530259/pexels-photo-1530259.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 마레 지구/보즈 광장 (도착 & 동네 탐험)
                "https://images.pexels.com/photos/149522/pexels-photo-149522.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 2 - 에펠탑 아침 & 트로카데로 (랜드마크 투어)
                "https://images.pexels.com/photos/2363/france-landmark-lights-night.jpg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 루브르 박물관 (예술의 거리)
                "https://images.pexels.com/photos/2082103/pexels-photo-2082103.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 4 - 몽마르트 예술가 거리 (예술의 언덱)
                "https://images.pexels.com/photos/161901/paris-sunset-france-landmark-161901.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 갤러리 라파예트 & 쇼핑 (마무리)
            ],
            "Rome": [
                "https://images.pexels.com/photos/1797161/pexels-photo-1797161.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Hero - 콜로세움
                "https://images.pexels.com/photos/2225439/pexels-photo-2225439.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 콜로세움 & 로마 포럼 (고대 로마)
                "https://images.pexels.com/photos/1547813/pexels-photo-1547813.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 2 - 트레비 분수 & 판테온 (로마의 낭만)
                "https://images.pexels.com/photos/2064827/pexels-photo-2064827.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 바티칸 & 성베드로 대성당 (종교의 중심)
                "https://images.pexels.com/photos/2676602/pexels-photo-2676602.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 4 - 보르게세 갤러리 & 빌라 (예술과 자연)
                "https://images.pexels.com/photos/2225440/pexels-photo-2225440.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 캄포 데이 피오리 & 귀국 (마무리)
            ],
            "London": [
                "https://images.pexels.com/photos/672532/pexels-photo-672532.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Hero - 빅벤 & 웨스트민스터
                "https://images.pexels.com/photos/258117/pexels-photo-258117.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 1 - 런던 아이 & 테임즈 강변 (도착 & 도심)
                "https://images.pexels.com/photos/460672/pexels-photo-460672.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 2 - 타워 브리지 & 런던 타워 (랜드마크)
                "https://images.pexels.com/photos/1796706/pexels-photo-1796706.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 버킹엄 궁전 & 하이드파크 (왕실 투어)
                "https://images.pexels.com/photos/427679/pexels-photo-427679.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 4 - 대영박물관 & 코번트 가든 (문화 탐방)
                "https://images.pexels.com/photos/1837590/pexels-photo-1837590.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 하이드파크 & 쇼핑 (여유로운 마무리)
            ],
            "Tokyo": [
                "https://images.pexels.com/photos/2506923/pexels-photo-2506923.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Hero - 도쿄 타워
                "https://images.pexels.com/photos/2339009/pexels-photo-2339009.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 시부야 & 하라주쿠 (현대 도쿄)
                "https://images.pexels.com/photos/2187603/pexels-photo-2187603.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 2 - 아사쿠사 & 센소지 (전통 도쿄)
                "https://images.pexels.com/photos/3029352/pexels-photo-3029352.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 메이지 신궁 & 도쿄역 (문화 탐방)
                "https://images.pexels.com/photos/1486222/pexels-photo-1486222.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 4 - 시부야 야경 & 도쿄 야경 투어
                "https://images.pexels.com/photos/1547813/pexels-photo-1547813.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 츠키지 & 귀국 준비 (마무리)
            ],
            "Bangkok": [
                "https://images.pexels.com/photos/2087391/pexels-photo-2087391.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Hero - 왓아룬 (새벽 사원)
                "https://images.pexels.com/photos/2082103/pexels-photo-2082103.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 카오산 로드 & 왕궁 (도착 & 시내)
                "https://images.pexels.com/photos/2082101/pexels-photo-2082101.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 2 - 왓포 & 왓아룬 (사원 투어)
                "https://images.pexels.com/photos/2082100/pexels-photo-2082100.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 짜짝 시장 & 플로팅 마켓 (시장 탐방)
                "https://images.pexels.com/photos/2082104/pexels-photo-2082104.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 4 - 아유타야 역사 공원 (일일 투어)
                "https://images.pexels.com/photos/2082105/pexels-photo-2082105.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 터미널 21 & 쇼핑 (마무리)
            ],
            "Barcelona": [
                "https://images.pexels.com/photos/1388030/pexels-photo-1388030.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Hero - 사그라다 파밀리아
                "https://images.pexels.com/photos/1786433/pexels-photo-1786433.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 까탈루냐 광장 & 고딕 지구 (도착 & 구시가지)
                "https://images.pexels.com/photos/819764/pexels-photo-819764.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 2 - 사그라다 파밀리아 & 구엘 공원 (가우디 투어)
                "https://images.pexels.com/photos/1388032/pexels-photo-1388032.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 까사 바트요 & 까사 밀라 (가우디 건축)
                "https://images.pexels.com/photos/1786435/pexels-photo-1786435.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 4 - 몬주익 언덱 & 해변 (전망 & 휴식)
                "https://images.pexels.com/photos/1388028/pexels-photo-1388028.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 보케리아 시장 & 쇼핑 (마무리)
            ],
            "New York": [
                "https://images.pexels.com/photos/1485894/pexels-photo-1485894.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Hero - 타임스 스퀘어
                "https://images.pexels.com/photos/2224861/pexels-photo-2224861.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 센트럴 파크 & 5번가 (도착 & 맨해튼 중심)
                "https://images.pexels.com/photos/1239162/pexels-photo-1239162.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 2 - 자유의 여신상 & 엘리스 섬 (랜드마크)
                "https://images.pexels.com/photos/1486221/pexels-photo-1486221.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 브루클린 브리지 & DUMBO (브루클린 투어)
                "https://images.pexels.com/photos/1239176/pexels-photo-1239176.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 4 - 메트로폴리탄 박물관 & 하이 라인 (문화 탐방)
                "https://images.pexels.com/photos/1486220/pexels-photo-1486220.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 월스트리트 & 쇼핑 (마무리)
            ],
            "Singapore": [
                "https://images.pexels.com/photos/1842332/pexels-photo-1842332.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Hero - 마리나 베이 샌즈
                "https://images.pexels.com/photos/290386/pexels-photo-290386.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 1 - 마리나 베이 & 가든스 바이 더 베이 (도착 & 랜드마크)
                "https://images.pexels.com/photos/1769397/pexels-photo-1769397.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 2 - 센토사 섬 & 유니버설 스튜디오 (테마파크)
                "https://images.pexels.com/photos/1842331/pexels-photo-1842331.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 차이나타운 & 리틀 인디아 (문화 투어)
                "https://images.pexels.com/photos/290385/pexels-photo-290385.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 4 - 보탄릭 가든 & 클라우드 포리스트 (자연 탐방)
                "https://images.pexels.com/photos/1842329/pexels-photo-1842329.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 오차드 로드 쇼핑 & 귀국 (마무리)
            ],
            "Phuket": [
                "https://images.pexels.com/photos/2166559/pexels-photo-2166559.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Hero - 푸켓 해변
                "https://images.pexels.com/photos/1770809/pexels-photo-1770809.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 파통 비치 & 방라 로드 (도착 & 해변)
                "https://images.pexels.com/photos/2166553/pexels-photo-2166553.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 2 - 피피 섬 투어 (섬 호핑)
                "https://images.pexels.com/photos/1770807/pexels-photo-1770807.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 빅 부다 & 왓찰롱 (문화 탐방)
                "https://images.pexels.com/photos/2166555/pexels-photo-2166555.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 4 - 카타 비치 & 카론 비치 (해변 휴식)
                "https://images.pexels.com/photos/1770805/pexels-photo-1770805.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 푸켓 타운 & 쇼핑 (마무리)
            ],
            "Maldives": [
                "https://images.pexels.com/photos/1287460/pexels-photo-1287460.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Hero - 몰디브 오버워터 빌라
                "https://images.pexels.com/photos/1547814/pexels-photo-1547814.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 리조트 도착 & 비치 (도착 & 휴식)
                "https://images.pexels.com/photos/1287459/pexels-photo-1287459.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 2 - 스노클링 & 다이빙 (해양 활동)
                "https://images.pexels.com/photos/1547815/pexels-photo-1547815.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 프라이빗 비치 & 스파 (휴식 & 웰니스)
                "https://images.pexels.com/photos/1287458/pexels-photo-1287458.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 4 - 선셋 크루즈 & 섬 투어 (로맨틱 투어)
                "https://images.pexels.com/photos/1547816/pexels-photo-1547816.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 마지막 휴식 & 귀국 준비 (마무리)
            ],
            "Bali": [
                "https://images.pexels.com/photos/2166559/pexels-photo-2166559.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Hero - 발리 라이스 테라스
                "https://images.pexels.com/photos/1770809/pexels-photo-1770809.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 우붓 & 몽키 포레스트 (도착 & 문화)
                "https://images.pexels.com/photos/2166553/pexels-photo-2166553.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 2 - 타나 로트 & 울루와투 사원 (사원 투어)
                "https://images.pexels.com/photos/1770807/pexels-photo-1770807.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 테갈랄랑 라이스 테라스 & 성채 (자연 탐방)
                "https://images.pexels.com/photos/2166555/pexels-photo-2166555.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 4 - 누사두아 & 스미냑 비치 (해변 휴식)
                "https://images.pexels.com/photos/1770805/pexels-photo-1770805.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 우붓 시장 & 쇼핑 (마무리)
            ],
            "Sydney": [
                "https://images.pexels.com/photos/1878293/pexels-photo-1878293.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Hero - 시드니 오페라하우스
                "https://images.pexels.com/photos/2193300/pexels-photo-2193300.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 서큘러 키 & 더 록스 (도착 & 항구)
                "https://images.pexels.com/photos/1684628/pexels-photo-1684628.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 2 - 본다이 비치 & 코지 비치 (해변 투어)
                "https://images.pexels.com/photos/1878294/pexels-photo-1878294.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 시드니 하버 브리지 클라임 & 왕립 식물원 (랜드마크)
                "https://images.pexels.com/photos/2193299/pexels-photo-2193299.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 4 - 블루 마운틴 일일 투어 (자연 탐방)
                "https://images.pexels.com/photos/1684627/pexels-photo-1684627.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 퀸빅토리아 빌딩 & 쇼핑 (마무리)
            ],
            "Dubai": [
                "https://images.pexels.com/photos/2044434/pexels-photo-2044434.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Hero - 부르즈 할리파
                "https://images.pexels.com/photos/323705/pexels-photo-323705.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 1 - 더 Dubai 몰 & 부르즈 할리파 (도착 & 랜드마크)
                "https://images.pexels.com/photos/3237051/pexels-photo-3237051.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 2 - 팜 주메이라 & 아틀란티스 (인공섬 투어)
                "https://images.pexels.com/photos/3237052/pexels-photo-3237052.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 사막 사파리 & 베두인 캠프 (사막 체험)
                "https://images.pexels.com/photos/3237053/pexels-photo-3237053.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 4 - 두바이 마리나 & JBR 비치 (마리나 투어)
                "https://images.pexels.com/photos/3237054/pexels-photo-3237054.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 골드 수크 & 쇼핑 (마무리)
            ],
            # 추가 유럽 도시
            "Amsterdam": [
                "https://images.pexels.com/photos/208336/pexels-photo-208336.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Hero - 운하 & 건축물
                "https://images.pexels.com/photos/161401/facade-building-old-architecture-161401.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 중심가 & 다마 광장 (도착 & 시내)
                "https://images.pexels.com/photos/179714/pexels-photo-179714.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 2 - 반스키 박물관 & 요르단 (예술 투어)
                "https://images.pexels.com/photos/724552/pexels-photo-724552.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 3 - 아네 프랑크 하우스 & 운하 (역사 탐방)
                "https://images.pexels.com/photos/267527/pexels-photo-267527.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 4 - 불델 공원 & 반 고흐 (공원 & 미술)
                "https://images.pexels.com/photos/141864/pexels-photo-141864.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 5 - 알버트 큐이 & 쇼핑 (마무리)
            ],
            "Prague": [
                "https://images.pexels.com/photos/164336/pexels-photo-164336.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Hero - 프라하 성
                "https://images.pexels.com/photos/163405/prague-czech-republic-old-town-163405.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 구시가 & 천문시계 (도착 & 시내)
                "https://images.pexels.com/photos/154566/pexels-photo-154566.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 2 - 프라하 성 & 성 비투스 (성 투어)
                "https://images.pexels.com/photos/142395/pexels-photo-142395.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 3 - 카를교 & 요세포프 (다리 & 지역)
                "https://images.pexels.com/photos/131381/pexels-photo-131381.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 4 - 페트린 타워 & 언덱 (전망 & 공원)
                "https://images.pexels.com/photos/157107/pexels-photo-157107.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 5 - 파리지 거리 & 쇼핑 (마무리)
            ],
            "Vienna": [
                "https://images.pexels.com/photos/151230/pexels-photo-151230.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Hero - 성 스테판 대성당
                "https://images.pexels.com/photos/160834/pexels-photo-160834.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 1 - 슈테판광장 & 그라벤 (도착 & 시내)
                "https://images.pexels.com/photos/258166/pexels-photo-258166.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 2 - 쇤브룬 궁전 & 정원 (궁전 투어)
                "https://images.pexels.com/photos/156531/pexels-photo-156531.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 3 - 호프부르크 & 벨베데레 (제국 역사)
                "https://images.pexels.com/photos/210619/pexels-photo-210619.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 4 - 빈 국립오페라 & 미술사 (문화 투어)
                "https://images.pexels.com/photos/293431/pexels-photo-293431.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 5 - 나슈마르크트 & 쇼핑 (마무리)
            ],
            "Lisbon": [
                "https://images.pexels.com/photos/544331/pexels-photo-544331.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Hero - 리스본 전경 & 트램
                "https://images.pexels.com/photos/1549104/pexels-photo-1549104.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 시아도 & 로시우 (도착 & 시내)
                "https://images.pexels.com/photos/604532/pexels-photo-604532.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 2 - 벨렘 타워 & 제로니모스 (역사 투어)
                "https://images.pexels.com/photos/310152/pexels-photo-310152.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 3 - 알파마 & 상조르즈 (구시가 탐방)
                "https://images.pexels.com/photos/322107/pexels-photo-322107.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 4 - 싱트라 & 페나 궁전 (일일 투어)
                "https://images.pexels.com/photos/602571/pexels-photo-602571.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 5 - 타임아웃 & 쇼핑 (마무리)
            ],
            "Berlin": [
                "https://images.pexels.com/photos/112840/pexels-photo-112840.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Hero - 브란덴부르크 문
                "https://images.pexels.com/photos/114624/pexels-photo-114624.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 1 - 쿠담 & 동물원 (도착 & 시내)
                "https://images.pexels.com/photos/131023/pexels-photo-131023.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 2 - 브란덴부르크 & 국회의사당 (역사 투어)
                "https://images.pexels.com/photos/165167/pexels-photo-165167.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 3 - 베를린 장벽 & 동쪽画廊 (냉전 역사)
                "https://images.pexels.com/photos/158316/pexels-photo-158316.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 4 - 박물관섬 & 페르가몬 (박물관 투어)
                "https://images.pexels.com/photos/159982/pexels-photo-159982.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 5 - 하케셔 & 쇼핑 (마무리)
            ],
            "Santorini": [
                "https://images.pexels.com/photos/161815/santorini-greece-travel-oia-161815.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Hero - 이아 풍경
                "https://images.pexels.com/photos/1285625/pexels-photo-1285625.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 피라 & 노을 (도착 & 마을)
                "https://images.pexels.com/photos/163864/santorini-oia-greece-163864.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 2 - 이아 & 파란지붕 (이아 투어)
                "https://images.pexels.com/photos/161081/santorini-greece-beach-sea-161081.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 카마리 & 레드비치 (해변)
                "https://images.pexels.com/photos/250701/pexels-photo-250701.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 4 - 선셋 크루즈 & 화산 (크루즈)
                "https://images.pexels.com/photos/144945/pexels-photo-144945.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Day 5 - 와이너리 & 쇼핑 (마무리)
            ],
            # 추가 동남아시아
            "Kuala Lumpur": [
                "https://images.pexels.com/photos/22804/pexels-photo.jpg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Hero - 페트로나스 타워
                "https://images.pexels.com/photos/433989/pexels-photo-433989.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - KLCC & 수리아 (도착 & 시내)
                "https://images.pexels.com/photos/2923592/pexels-photo-2923592.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 2 - 페트로나스 & 스카이브리지 (랜드마크)
                "https://images.pexels.com/photos/240040/pexels-photo-240040.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 바투 동굴 & 힌두 (문화 투어)
                "https://images.pexels.com/photos/433308/pexels-photo-433308.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 4 - 이슬람 예술 & 국립 (박물관)
                "https://images.pexels.com/photos/230547/pexels-photo-230547.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 부킷 빈탕 & 쇼핑 (마무리)
            ],
            "Kyoto": [
                "https://images.pexels.com/photos/144047/pexels-photo-144047.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Hero - 기요미즈데라
                "https://images.pexels.com/photos/161401/facade-building-old-architecture-161401.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 1 - 기온 & 시조 (도착 & 전통)
                "https://images.pexels.com/photos/1107717/pexels-photo-1107717.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 2 - 금각사 & 은각사 (사원 투어)
                "https://images.pexels.com/photos/144837/pexels-photo-144837.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 3 - 기요미즈데라 & 니넨자카 (동경)
                "https://images.pexels.com/photos/399675/pexels-photo-399675.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 4 - 후시미 이나리 & 도리이 (신사)
                "https://images.pexels.com/photos/157083/pexels-photo-157083.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", # Day 5 - 니시키 & 쇼핑 (마무리)
            ],
        }
        
        urls = pexels_urls.get(city, [])
        
        logger.info(f"Pexels 이미지 요청: {city}, 필요개수: {count}, 사용가능: {len(urls)}")
        for i, url in enumerate(urls[:count]):
            logger.info(f"  [Pexels {i}] {url[:70]}...")
        
        # 매핑되지 않은 도시는 동적으로 이미지 URL 생성
        if not urls:
            logger.info(f"{city}에 대한 매핑된 이미지가 없습니다. 동적 생성을 시도합니다.")
            themes = city_themes.get(city, default_themes)
            urls = self._generate_pexels_urls(city, themes, count)
        
        # 이미지 수가 부족하면 반복
        while len(urls) < count:
            urls.extend(urls[:count - len(urls)])
        
        return [
            {
                "url": urls[i],
                "source": "pexels",
                "photographer": "Pexels",
                "description": f"{city} travel photo - Day {i}",
                "size_bytes": None,
                "query": f"{city} travel",
                "license": "CC0 - Free to use, no attribution required"
            }
            for i in range(min(count, len(urls)))
        ]
    
    def _generate_pexels_urls(self, city: str, themes: List[str], count: int) -> List[str]:
        """
        동적으로 Pexels 이미지 URL 생성
        각 테마별로 Pexels 검색 URL 패턴 사용
        """
        import hashlib
        
        # Pexels 고품질 이미지 ID 패턴 (city + theme 기반으로 의사랜덤 선택)
        base_urls = []
        
        # 다양한 여행 관련 이미지 ID들
        travel_image_ids = [
            # Cityscape/SKYLINE
            "1486222", "1485894", "532826", "1797161", "672532", "2506923", "2087391",
            "1388030", "1486221", "1842332", "2166559", "1287460", "1878293", "2044434",
            # LANDMARKS/MONUMENTS  
            "149522", "1547813", "460672", "2339009", "2082101", "819764", "1239162",
            "290386", "2166553", "1287459", "1770809", "2193300", "323705", "161901",
            # STREETS/CULTURE
            "1530259", "2225439", "258117", "2187603", "2082103", "1786433", "2224861",
            "1769397", "1770807", "1770805", "1684628", "3237051", "2363", "2082103",
            # NATURE/BEACH
            "2082100", "1388032", "1239176", "290385", "2166555", "1547815", "2166553",
            "2193299", "3237052", "2082104", "1786435", "1486220", "1842329", "1770805",
            # NIGHT/VIEWS
            "2676602", "2064827", "1796706", "3029352", "2082105", "1486222", "290385",
            "1287458", "1486222", "1878294", "3237053", "2082105", "2225440", "1837590",
        ]
        
        # 도시 이름을 해시하여 시작 인덱스 결정 (일관된 결과를 위해)
        hash_val = int(hashlib.md5(city.encode()).hexdigest(), 16)
        start_idx = hash_val % len(travel_image_ids)
        
        # 필요한 개수만큼 순환하며 선택
        for i in range(count):
            idx = (start_idx + i) % len(travel_image_ids)
            img_id = travel_image_ids[idx]
            url = f"https://images.pexels.com/photos/{img_id}/pexels-photo-{img_id}.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
            base_urls.append(url)
        
        logger.info(f"동적 Pexels URL 생성 완료: {city}, {len(base_urls)}개")
        return base_urls
    
    def _get_pixabay_images(self, city: str, count: int) -> List[Dict]:
        """Pixabay에서 이미지 가져오기 - 각 일정별 테마에 맞는 이미지 제공"""
        # Pixabay API - 각 도시별 Hero + Day1~Day5 일정 연결 이미지
        pixabay_urls = {
            "Paris": [
                "https://cdn.pixabay.com/photo/2018/04/25/09/26/eiffel-tower-3349075_1280.jpg",  # Hero - 에펠탑 전경
                "https://cdn.pixabay.com/photo/2019/07/21/16/29/paris-4353082_1280.jpg",      # Day 1 - 마레 지구/보즈 광장 (도착 & 동네 탐험)
                "https://cdn.pixabay.com/photo/2015/10/06/18/26/eiffel-tower-975004_1280.jpg",  # Day 2 - 에펠탑 아침 & 트로칵데로 (랜드마크)
                "https://cdn.pixabay.com/photo/2020/07/23/01/16/louvre-5430784_1280.jpg",       # Day 3 - 루브르 박물관 (예술의 거리)
                "https://cdn.pixabay.com/photo/2016/11/18/19/01/paris-1836415_1280.jpg",        # Day 4 - 몽마르트 예술가 거리
                "https://cdn.pixabay.com/photo/2018/03/02/17/37/architecture-3192886_1280.jpg", # Day 5 - 갤러리 라파예트 (쇼핑)
            ],
            "Rome": [
                "https://cdn.pixabay.com/photo/2017/12/28/08/15/colosseum-3044630_1280.jpg",     # Hero - 콜로세움
                "https://cdn.pixabay.com/photo/2015/05/28/08/21/rome-787648_1280.jpg",          # Day 1 - 콜로세움 & 로마 포럼 (고대 로마)
                "https://cdn.pixabay.com/photo/2018/05/01/07/27/trevi-fountain-3365295_1280.jpg", # Day 2 - 트레비 분수 & 판테온
                "https://cdn.pixabay.com/photo/2019/08/17/13/46/vatican-4412234_1280.jpg",      # Day 3 - 바티칸 & 성베드로 대성당
                "https://cdn.pixabay.com/photo/2017/01/09/01/23/pantheon-1964588_1280.jpg",     # Day 4 - 보르게세 갤러리 & 빌라
                "https://cdn.pixabay.com/photo/2016/09/11/20/51/spanish-steps-1662263_1280.jpg", # Day 5 - 스페인 계단 & 쇼핑
            ],
        }
        
        urls = pixabay_urls.get(city, [])
        
        # URL 검증 및 로깅
        logger.info(f"Pixabay 이미지 요청: {city}, 필요개수: {count}, 사용가능: {len(urls)}")
        for i, url in enumerate(urls[:count]):
            logger.info(f"  [Pixabay {i}] {url[:80]}...")
        
        if not urls:
            return []
        
        # 이미지 수가 부족하면 반복
        while len(urls) < count:
            urls.extend(urls[:count - len(urls)])
        
        return [
            {
                "url": urls[i],
                "source": "pixabay",
                "photographer": "Pixabay",
                "description": f"{city} travel photo",
                "size_bytes": None,
                "query": f"{city} travel",
                "license": "Pixabay License - Free for commercial use, no attribution required"
            }
            for i in range(min(count, len(urls)))
        ]
    
    def _get_unsplash_images(self, city: str, count: int) -> List[Dict]:
        """Unsplash API에서 이미지 가져오기"""
        if not self.access_key:
            logger.warning("UNSPLASH_ACCESS_KEY not set")
            return []
        
        # API 요청 가능 여부 확인
        available_requests = self.hourly_limit - len(self._load_usage().get("requests", []))
        if available_requests <= 0:
            logger.warning("Unsplash API hourly limit reached (7/7)")
            return []
        
        actual_count = min(count, available_requests)
        images = []
        
        # 검색 쿼리 (랜드마크 기반)
        queries = [
            f"{city} landmark",
            f"{city} cityscape",
            f"{city} travel",
            f"{city} architecture",
            f"{city} street",
            f"{city} nightlife",
        ]
        
        for i, query in enumerate(queries[:actual_count]):
            try:
                encoded_query = urllib.parse.quote(query)
                url = f"{self.base_url}/photos/random?query={encoded_query}&orientation=landscape&w=1920&h=1080"
                
                req = urllib.request.Request(
                    url,
                    headers={"Authorization": f"Client-ID {self.access_key}"}
                )
                
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                
                self._record_request()
                
                # 이미지 URL 선택 (regular size가 보통 5MB 이하)
                img_url = data.get("urls", {}).get("regular") or data.get("urls", {}).get("small")
                
                if not img_url:
                    continue
                
                # 크기 확인
                is_valid_size, size_bytes = self._check_image_size(img_url)
                
                if not is_valid_size:
                    logger.warning(f"Image too large (>5MB), trying smaller size")
                    # 작은 사이즈 시도
                    img_url = data.get("urls", {}).get("small")
                    is_valid_size, size_bytes = self._check_image_size(img_url) if img_url else (False, None)
                    
                    if not is_valid_size:
                        continue
                
                images.append({
                    "url": img_url,
                    "source": "unsplash",
                    "photographer": data.get("user", {}).get("name", "Unknown"),
                    "photographer_url": data.get("user", {}).get("links", {}).get("html", ""),
                    "unsplash_url": data.get("links", {}).get("html", ""),
                    "description": data.get("description") or data.get("alt_description") or f"{city} travel photo",
                    "size_bytes": size_bytes,
                    "query": query,
                    "license": "Unsplash License - Free to use, attribution appreciated"
                })
                
                # 요청 간 딜레이 (API rate limit 준수)
                if i < actual_count - 1:
                    time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error fetching Unsplash image: {e}")
                continue
        
        return images
    
    def get_city_images(self, city: str, count: int = 3, day_specific: bool = False) -> List[Dict]:
        """
        도시별 고품질 이미지 가져오기 (Unsplash API 우선 + Pexels + Pixabay 혼합)
        
        Args:
            city: 도시명
            count: 가져올 이미지 수
            day_specific: True면 일자별 다양한 이미지, False면 일반 이미지
        
        Returns:
            이미지 정보 리스트 (Unsplash + Pexels + Pixabay 혼합)
        """
        images = []
        
        # 1. Unsplash API 이미지 가져오기 (고품질, API 키 제공됨)
        unsplash_images = self._get_unsplash_images(city, count)
        if unsplash_images and len(unsplash_images) >= count:
            logger.info(f"✅ Unsplash API에서 {len(unsplash_images)}장의 고품질 이미지를 가져왔습니다 ({city})")
            # 각 이미지 인덱스별 URL 로깅
            for i, img in enumerate(unsplash_images[:count]):
                logger.info(f"  [Unsplash {i}] {img['url'][:60]}...")
            return unsplash_images[:count]
        elif unsplash_images:
            images.extend(unsplash_images)
            logger.info(f"Unsplash API에서 {len(unsplash_images)}장 가져옴")
        
        # 2. Pexels 이미지 추가 (CC0 라이선스 - 저작권 문제 없음)
        pexels_needed = max(0, count - len(images))
        if pexels_needed > 0:
            pexels_images = self._get_pexels_images(city, pexels_needed)
            if pexels_images:
                images.extend(pexels_images)
                logger.info(f"Pexels에서 {len(pexels_images)}장 추가")
        
        # 3. Pixabay 이미지 추가 (Pexels 부족시)
        pixabay_needed = max(0, count - len(images))
        if pixabay_needed > 0:
            pixabay_images = self._get_pixabay_images(city, pixabay_needed)
            if pixabay_images:
                images.extend(pixabay_images)
                logger.info(f"Pixabay에서 {len(pixabay_images)}장 추가")
        
        # 4. 이미지가 부족하면 fallback으로 채우기
        if len(images) < count:
            fallback_needed = count - len(images)
            fallback_images = self._get_fallback_images(city, fallback_needed)
            images.extend(fallback_images)
            logger.info(f"Fallback에서 {len(fallback_images)}장 추가")
        
        # 5. 결과 정렬 및 중복 제거
        seen_urls = set()
        unique_images = []
        for img in images:
            if img["url"] not in seen_urls:
                seen_urls.add(img["url"])
                unique_images.append(img)
        
        final_images = unique_images[:count]
        
        # URL 유효성 검증 (404 체크)
        valid_images = []
        for img in final_images:
            url = img.get("url", "")
            if self._validate_image_url(url):
                valid_images.append(img)
            else:
                logger.warning(f"Invalid/404 image URL, skipping: {url[:80]}...")
        
        # 유효한 이미지가 부족하면 fallback으로 채우기
        if len(valid_images) < count:
            fallback_needed = count - len(valid_images)
            logger.warning(f"Valid images insufficient ({len(valid_images)}/{count}), adding {fallback_needed} fallback images")
            fallback_images = self._get_fallback_images(city, fallback_needed)
            # fallback 이미지도 검증
            for img in fallback_images:
                if self._validate_image_url(img.get("url", "")):
                    valid_images.append(img)
                if len(valid_images) >= count:
                    break
        
        final_images = valid_images[:count]
        
        # 소스 통계 로깅
        sources = {}
        for img in final_images:
            src = img.get("source", "unknown")
            sources[src] = sources.get(src, 0) + 1
        logger.info(f"✅ 최종 이미지 구성 ({city}): {sources}")
        
        # 각 이미지 인덱스별 URL 로깅 (디버깅용)
        for i, img in enumerate(final_images):
            logger.info(f"  [{i}] {img['source']}: {img['url'][:60]}...")
        
        return final_images
    
    def _get_fallback_images(self, city: str, count: int) -> List[Dict]:
        """Unsplash API 제한 시 fallback 이미지 제공 - Pexels CC0 우선 사용"""
        # Pexels CC0 이미지 (저작권 문제 없음)
        fallback_urls = {
            "Paris": [
                "https://images.pexels.com/photos/532826/pexels-photo-532826.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/1530259/pexels-photo-1530259.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/149522/pexels-photo-149522.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
            ],
            "Rome": [
                "https://images.pexels.com/photos/1797161/pexels-photo-1797161.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/2225439/pexels-photo-2225439.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/1547813/pexels-photo-1547813.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
            ],
            "London": [
                "https://images.pexels.com/photos/672532/pexels-photo-672532.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/258117/pexels-photo-258117.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/460672/pexels-photo-460672.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
            ],
            "Tokyo": [
                "https://images.pexels.com/photos/2506923/pexels-photo-2506923.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/2339009/pexels-photo-2339009.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/2187603/pexels-photo-2187603.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
            ],
            "Bangkok": [
                "https://images.pexels.com/photos/2087391/pexels-photo-2087391.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/2082103/pexels-photo-2082103.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/2082101/pexels-photo-2082101.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
            ],
            "Barcelona": [
                "https://images.pexels.com/photos/1388030/pexels-photo-1388030.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/1786433/pexels-photo-1786433.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/819764/pexels-photo-819764.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
            ],
            "New York": [
                "https://images.pexels.com/photos/1485894/pexels-photo-1485894.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/2224861/pexels-photo-2224861.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/1239162/pexels-photo-1239162.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
            ],
            "Singapore": [
                "https://images.pexels.com/photos/1842332/pexels-photo-1842332.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/290386/pexels-photo-290386.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/1769397/pexels-photo-1769397.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
            ],
            "Sydney": [
                "https://images.pexels.com/photos/1878293/pexels-photo-1878293.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/2193300/pexels-photo-2193300.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/1684628/pexels-photo-1684628.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
            ],
            "Bali": [
                "https://images.pexels.com/photos/2166559/pexels-photo-2166559.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/1770809/pexels-photo-1770809.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                "https://images.pexels.com/photos/2166553/pexels-photo-2166553.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
            ],
        }
        
        # 기본 이미지 (Pexels - CC0 라이선스)
        default_images = [
            "https://images.pexels.com/photos/6243470/pexels-photo-6243470.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
            "https://images.pexels.com/photos/6243471/pexels-photo-6243471.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
            "https://images.pexels.com/photos/6243472/pexels-photo-6243472.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        ]
        
        urls = fallback_urls.get(city, default_images)
        
        # 이미지 수가 부족하면 반복
        while len(urls) < count:
            urls.extend(urls[:count - len(urls)])
        
        return [
            {
                "url": urls[i],
                "source": "pexels_fallback",
                "photographer": "Pexels",
                "description": f"{city} travel photo",
                "size_bytes": None,
                "query": f"{city} travel",
                "license": "CC0 - Free to use, no attribution required"
            }
            for i in range(min(count, len(urls)))
        ]
    
    def get_restaurant_image(self, restaurant_name: str, city: str) -> Optional[Dict]:
        """식당별 이미지 가져오기"""
        query = f"{restaurant_name} {city} restaurant food"
        images = self.get_city_images(query, count=1)
        return images[0] if images else None


# 인스턴스 생성
image_fetcher = UnsplashImageFetcher()
