"""
Notion Image Manager - Download, verify, and manage images for Notion pages
Uses reliable external hosting with fallback chain
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from loguru import logger
import mimetypes
import base64

# PIL for image resizing with aspect ratio preservation
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logger.warning("PIL/Pillow not installed. Image resizing will use fallback method.")


class NotionImageManager:
    """
    Manages images for Notion pages:
    1. Downloads images from various sources
    2. Verifies and optimizes them
    3. Provides reliable URLs for Notion blocks
    
    Strategy:
    - Download and verify all images locally
    - Use optimized direct URLs with retry logic
    - Implement multiple fallback sources
    """
    
    def __init__(self):
        self.temp_dir = Path(__file__).resolve().parents[1] / "temp_images"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache for processed images
        self._url_cache: Dict[str, Dict] = {}
        
        # Cloudinary config (for reliable hosting fallback)
        self.cloudinary_cloud = os.getenv("CLOUDINARY_CLOUD_NAME", "")
        self.cloudinary_key = os.getenv("CLOUDINARY_API_KEY", "")
        self.cloudinary_secret = os.getenv("CLOUDINARY_API_SECRET", "")
        
        # Imgur config (secondary fallback)
        self.imgur_client_id = os.getenv("IMGUR_CLIENT_ID", "")
    
    def download_image(self, image_url: str, city: str, index: int, 
                       landmark: str = "") -> Optional[Dict]:
        """
        Download image from URL and save locally
        
        Returns:
            Dict with local_path, size, mime_type, hash or None if failed
        """
        if not image_url or not image_url.startswith("http"):
            logger.warning(f"Invalid image URL: {image_url}")
            return None
        
        # Create city-specific directory
        city_dir = self.temp_dir / self._sanitize_filename(city)
        city_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        clean_landmark = self._sanitize_filename(landmark or f"image_{index}")[:30]
        filename = f"{index:02d}_{clean_landmark}.jpg"
        local_path = city_dir / filename
        
        # Check cache
        cache_key = f"{city}_{image_url}"
        if cache_key in self._url_cache:
            cached = self._url_cache[cache_key]
            if Path(cached["local_path"]).exists():
                logger.info(f"Using cached image: {local_path.name}")
                return cached
        
        try:
            logger.info(f"Downloading: {image_url[:70]}...")
            
            # Download with proper headers
            req = urllib.request.Request(image_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            req.add_header('Accept', 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8')
            req.add_header('Accept-Language', 'en-US,en;q=0.9')
            req.add_header('Referer', 'https://www.google.com/')
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                image_data = resp.read()
                
                # Verify size
                if len(image_data) < 1000:
                    logger.warning(f"Image too small: {len(image_data)} bytes")
                    return None
                
                if len(image_data) > 20 * 1024 * 1024:  # 20MB limit
                    logger.warning(f"Image too large: {len(image_data)} bytes")
                    return None
                
                # Write to file
                local_path.write_bytes(image_data)
                
                # Verify it's a valid image
                if not self._validate_image_file(local_path):
                    logger.warning(f"Invalid image file: {local_path}")
                    local_path.unlink(missing_ok=True)
                    return None
                
                # Resize image while maintaining aspect ratio
                resized_path, new_size = self.resize_maintain_aspect(local_path, max_width=1920, max_height=1080, quality=85)
                
                # Get file info (use resized file)
                final_image_data = resized_path.read_bytes()
                file_size = len(final_image_data)
                mime_type = self._detect_mime_type(local_path)
                file_hash = hashlib.md5(final_image_data).hexdigest()[:16]
                
                result = {
                    "local_path": str(local_path),
                    "filename": filename,
                    "size": file_size,
                    "mime_type": mime_type,
                    "hash": file_hash,
                    "original_url": image_url,
                    "city": city,
                    "landmark": landmark,
                }
                
                # Cache result
                self._url_cache[cache_key] = result
                
                logger.info(f"✅ Downloaded: {filename} ({file_size:,} bytes, {mime_type})")
                return result
                
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP {e.code} downloading image: {image_url[:60]}...")
            return None
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for use in filename"""
        import re
        # Replace spaces and special chars with underscore
        cleaned = re.sub(r'[^\w\s-]', '', name.lower())
        cleaned = re.sub(r'[-\s]+', '_', cleaned)
        return cleaned[:50]

    def resize_maintain_aspect(self, image_path: Path, max_width: int = 1920, max_height: int = 1080, quality: int = 85) -> Tuple[Path, Tuple[int, int]]:
        """
        Resize image while maintaining aspect ratio.
        Fits within max_width x max_height without cropping.
        
        Args:
            image_path: Path to the image file
            max_width: Maximum width constraint
            max_height: Maximum height constraint
            quality: JPEG quality (0-100)
            
        Returns:
            Tuple of (output_path, (new_width, new_height))
        """
        if not HAS_PIL:
            logger.warning("PIL not available, skipping resize")
            return image_path, (0, 0)
        
        try:
            img = Image.open(image_path)
            original_width, original_height = img.size
            aspect_ratio = original_width / original_height
            
            # Calculate new size maintaining aspect ratio
            if aspect_ratio > max_width / max_height:
                # Image is wider - constrain by width
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
            else:
                # Image is taller - constrain by height
                new_height = max_height
                new_width = int(max_height * aspect_ratio)
            
            # Only resize if the image is larger than target
            if original_width <= max_width and original_height <= max_height:
                logger.debug(f"Image already within bounds: {original_width}x{original_height}")
                return image_path, (original_width, original_height)
            
            # Resize with high quality
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary (for JPEG output)
            if resized.mode in ('RGBA', 'P'):
                resized = resized.convert('RGB')
            
            # Save with quality setting
            resized.save(image_path, quality=quality, optimize=True)
            
            logger.info(f"Resized image: {original_width}x{original_height} -> {new_width}x{new_height} (aspect ratio preserved)")
            return image_path, (new_width, new_height)
            
        except Exception as e:
            logger.error(f"Resize failed: {e}")
            return image_path, (0, 0)
    
    def _validate_image_file(self, file_path: Path) -> bool:
        """Validate file is a valid image by checking magic bytes"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(12)
                
                # JPEG: FF D8 FF
                if header[:3] == b'\xff\xd8\xff':
                    return True
                # PNG: 89 50 4E 47
                if header[:4] == b'\x89PNG':
                    return True
                # WebP: RIFF....WEBP
                if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
                    return True
                # GIF: GIF87a or GIF89a
                if header[:3] == b'GIF':
                    return True
                    
            logger.debug(f"Unknown image format. Header: {header[:8].hex()}")
            return False
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    def _detect_mime_type(self, file_path: Path) -> str:
        """Detect MIME type from file content"""
        with open(file_path, 'rb') as f:
            header = f.read(12)
            
        if header[:3] == b'\xff\xd8\xff':
            return 'image/jpeg'
        if header[:4] == b'\x89PNG':
            return 'image/png'
        if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
            return 'image/webp'
        if header[:3] == b'GIF':
            return 'image/gif'
            
        # Fallback to extension-based detection
        mime, _ = mimetypes.guess_type(str(file_path))
        return mime or 'image/jpeg'
    
    def get_reliable_image_url(self, image_info: Dict, original_img: Dict) -> str:
        """
        Get the most reliable URL for an image
        
        Strategy:
        1. Try Cloudinary upload (most reliable)
        2. Try Imgur upload
        3. Return optimized original URL
        """
        local_path = Path(image_info["local_path"])
        
        # Try Cloudinary first
        if self.cloudinary_cloud and self.cloudinary_key:
            cloudinary_url = self._upload_to_cloudinary(local_path)
            if cloudinary_url:
                logger.info(f"Using Cloudinary URL: {cloudinary_url[:60]}...")
                return cloudinary_url
        
        # Try Imgur
        if self.imgur_client_id:
            imgur_url = self._upload_to_imgur(local_path)
            if imgur_url:
                logger.info(f"Using Imgur URL: {imgur_url[:60]}...")
                return imgur_url
        
        # Fallback: return optimized original URL
        original_url = image_info["original_url"]
        optimized_url = self._optimize_url(original_url)
        logger.info(f"Using optimized original URL: {optimized_url[:60]}...")
        return optimized_url
    
    def _optimize_url(self, url: str) -> str:
        """Optimize image URL for reliability - maintains aspect ratio (no cropping)"""
        # Remove existing query parameters from certain CDNs
        if 'unsplash.com' in url:
            # Use Unsplash's image service WITHOUT cropping
            # fit=fill maintains aspect ratio within bounds
            base = url.split('?')[0]
            return f"{base}?w=1920&h=1080&fit=fill&q=85&fm=jpg"
        
        if 'pexels.com' in url:
            base = url.split('?')[0]
            # Use fit=contain to maintain aspect ratio without cropping
            return f"{base}?auto=compress&cs=tinysrgb&w=1920&h=1080&fit=contain&dpr=1"
        
        if 'pixabay.com' in url:
            # Pixabay URLs are usually already optimized
            return url
        
        if 'wikimedia.org' in url:
            # Wikimedia supports thumbnail parameters
            if '/thumb/' not in url:
                return url
            return url
        
        return url
    
    def _upload_to_cloudinary(self, local_path: Path) -> Optional[str]:
        """Upload image to Cloudinary"""
        if not all([self.cloudinary_cloud, self.cloudinary_key, self.cloudinary_secret]):
            return None
        
        try:
            import time
            import random
            
            # Cloudinary upload API
            url = f"https://api.cloudinary.com/v1_1/{self.cloudinary_cloud}/image/upload"
            
            # Generate signature
            timestamp = str(int(time.time()))
            public_id = f"travel_blog/{local_path.stem}_{random.randint(1000, 9999)}"
            
            params = {
                "timestamp": timestamp,
                "public_id": public_id,
            }
            
            # Create signature
            signature_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())]) + self.cloudinary_secret
            signature = hashlib.sha1(signature_string.encode()).hexdigest()
            
            # Build multipart form data manually
            boundary = '----WebKitFormBoundary' + ''.join(random.choices('0123456789abcdef', k=16))
            
            image_data = local_path.read_bytes()
            mime_type = self._detect_mime_type(local_path)
            
            body = io.BytesIO()
            
            # Add file
            body.write(f'--{boundary}\r\n'.encode())
            body.write(f'Content-Disposition: form-data; name="file"; filename="{local_path.name}"\r\n'.encode())
            body.write(f'Content-Type: {mime_type}\r\n\r\n'.encode())
            body.write(image_data)
            body.write(b'\r\n')
            
            # Add other fields
            for key, value in params.items():
                body.write(f'--{boundary}\r\n'.encode())
                body.write(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
                body.write(value.encode())
                body.write(b'\r\n')
            
            body.write(f'--{boundary}\r\n'.encode())
            body.write(b'Content-Disposition: form-data; name="api_key"\r\n\r\n')
            body.write(self.cloudinary_key.encode())
            body.write(b'\r\n')
            
            body.write(f'--{boundary}\r\n'.encode())
            body.write(b'Content-Disposition: form-data; name="signature"\r\n\r\n')
            body.write(signature.encode())
            body.write(b'\r\n')
            
            body.write(f'--{boundary}--\r\n'.encode())
            
            req = urllib.request.Request(url, data=body.getvalue())
            req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
            
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return data.get('secure_url') or data.get('url')
                
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
            return None
    
    def _upload_to_imgur(self, local_path: Path) -> Optional[str]:
        """Upload image to Imgur"""
        if not self.imgur_client_id:
            return None
        
        try:
            image_data = local_path.read_bytes()
            
            req = urllib.request.Request("https://api.imgur.com/3/image")
            req.add_header("Authorization", f"Client-ID {self.imgur_client_id}")
            
            payload = urllib.parse.urlencode({
                "image": base64.b64encode(image_data).decode("utf-8"),
                "type": "base64",
            }).encode("utf-8")
            
            with urllib.request.urlopen(req, data=payload, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("success"):
                    return data["data"]["link"]
                else:
                    logger.error(f"Imgur error: {data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Imgur upload failed: {e}")
            return None
    
    def process_images(self, images: List[Dict], city: str) -> List[Dict]:
        """
        Process all images for a city
        
        Args:
            images: List of image dicts from API fetcher
            city: City name
        
        Returns:
            List of processed images with reliable URLs
        """
        processed = []
        
        logger.info(f"Processing {len(images)} images for {city}")
        
        for i, img in enumerate(images):
            original_url = img.get("url", "")
            landmark = img.get("description", f"image_{i}")
            
            # Download image
            image_info = self.download_image(original_url, city, i, landmark)
            
            if image_info:
                # Get reliable URL
                reliable_url = self.get_reliable_image_url(image_info, img)
                
                # Update image dict
                processed_img = img.copy()
                processed_img["url"] = reliable_url
                processed_img["local_path"] = image_info["local_path"]
                processed_img["uploaded"] = reliable_url != original_url
                processed_img["size"] = image_info["size"]
                
                processed.append(processed_img)
                logger.info(f"✅ Image {i+1}: {reliable_url[:60]}...")
            else:
                # Keep original if download failed
                processed.append(img)
                logger.warning(f"⚠️ Image {i+1}: Using original URL (download failed)")
        
        return processed
    
    def get_download_stats(self) -> Dict:
        """Get statistics about downloaded images"""
        stats = {
            "total_cities": 0,
            "total_images": 0,
            "total_size_mb": 0,
        }
        
        if not self.temp_dir.exists():
            return stats
        
        for city_dir in self.temp_dir.iterdir():
            if city_dir.is_dir():
                stats["total_cities"] += 1
                for img_file in city_dir.iterdir():
                    if img_file.is_file():
                        stats["total_images"] += 1
                        stats["total_size_mb"] += img_file.stat().st_size / (1024 * 1024)
        
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        return stats
    
    def cleanup(self, city: str = None, older_than_days: int = None):
        """Clean up temporary files"""
        try:
            if city:
                city_dir = self.temp_dir / self._sanitize_filename(city)
                if city_dir.exists():
                    import shutil
                    shutil.rmtree(city_dir)
                    logger.info(f"Cleaned up: {city}")
            elif older_than_days:
                from datetime import datetime, timedelta
                cutoff = datetime.now() - timedelta(days=older_than_days)
                
                for city_dir in self.temp_dir.iterdir():
                    if city_dir.is_dir():
                        # Check modification time
                        mtime = datetime.fromtimestamp(city_dir.stat().st_mtime)
                        if mtime < cutoff:
                            import shutil
                            shutil.rmtree(city_dir)
                            logger.info(f"Cleaned up old: {city_dir.name}")
            else:
                # Clean everything
                import shutil
                for item in self.temp_dir.iterdir():
                    if item.is_dir():
                        shutil.rmtree(item)
                logger.info("Cleaned up all temp files")
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")


# Singleton instance
image_manager = NotionImageManager()
