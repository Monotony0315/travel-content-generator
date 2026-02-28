#!/usr/bin/env python3
"""
Rate-limited web search utility for Brave Search API
- Max 1 call per minute to avoid rate limits
- Caches results for 1 hour
- Falls back to web_fetch for detailed content
"""

import json
import time
import os
from pathlib import Path
from typing import Optional, List, Dict
import urllib.request
import urllib.error
import urllib.parse

from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = Path(__file__).parent.parent / "data" / "search_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

LAST_CALL_FILE = CACHE_DIR / ".last_brave_call"
MIN_INTERVAL = 60  # seconds between calls


def _get_last_call_time() -> float:
    """Get timestamp of last API call"""
    if LAST_CALL_FILE.exists():
        try:
            return float(LAST_CALL_FILE.read_text().strip())
        except:
            return 0
    return 0


def _set_last_call_time():
    """Record current timestamp as last call"""
    LAST_CALL_FILE.write_text(str(time.time()))


def _wait_for_rate_limit():
    """Wait until we can make next API call"""
    last_call = _get_last_call_time()
    elapsed = time.time() - last_call
    if elapsed < MIN_INTERVAL:
        wait = MIN_INTERVAL - elapsed
        print(f"[RateLimit] Waiting {wait:.1f}s before next search...")
        time.sleep(wait)


def _get_cache_key(query: str) -> str:
    """Generate cache file key from query"""
    import hashlib
    return hashlib.md5(query.lower().encode()).hexdigest()[:12]


def _get_cached_result(query: str, max_age_hours: int = 1) -> Optional[List[Dict]]:
    """Get cached search result if fresh enough"""
    cache_file = CACHE_DIR / f"{_get_cache_key(query)}.json"
    if not cache_file.exists():
        return None
    
    try:
        data = json.loads(cache_file.read_text())
        age_hours = (time.time() - data.get("timestamp", 0)) / 3600
        if age_hours < max_age_hours:
            print(f"[Cache] Using cached result for: {query[:50]}...")
            return data.get("results", [])
    except:
        pass
    return None


def _cache_result(query: str, results: List[Dict]):
    """Cache search results"""
    cache_file = CACHE_DIR / f"{_get_cache_key(query)}.json"
    cache_file.write_text(json.dumps({
        "timestamp": time.time(),
        "query": query,
        "results": results
    }, ensure_ascii=False, indent=2))


def search_brave_rate_limited(query: str, count: int = 5) -> List[Dict]:
    """
    Search with Brave API, respecting rate limits
    
    Args:
        query: Search query
        count: Number of results (1-10)
    
    Returns:
        List of search results
    """
    # Check cache first
    cached = _get_cached_result(query)
    if cached:
        return cached
    
    # Wait for rate limit
    _wait_for_rate_limit()
    
    api_key = os.getenv("BRAVE_API_KEY", "")
    if not api_key:
        raise RuntimeError("BRAVE_API_KEY not set")
    
    url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count={count}"
    
    req = urllib.request.Request(
        url=url,
        headers={
            "Accept": "application/json",
            "X-Subscription-Token": api_key
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = data.get("web", {}).get("results", [])
            
            # Record call time
            _set_last_call_time()
            
            # Cache results
            _cache_result(query, results)
            
            return results
            
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("[RateLimit] Brave API rate limit hit, waiting...")
            time.sleep(60)
            return search_brave_rate_limited(query, count)  # Retry once
        raise


def smart_search(query: str, use_fetch: bool = True) -> str:
    """
    Smart search that combines Brave search with web_fetch
    
    Args:
        query: Search query
        use_fetch: Whether to fetch full content from top result
    
    Returns:
        Combined search results as text
    """
    # Get search results
    results = search_brave_rate_limited(query, count=5)
    
    if not results:
        return f"No results found for: {query}"
    
    output = []
    output.append(f"## Search Results: {query}\n")
    
    for i, r in enumerate(results[:3], 1):
        output.append(f"{i}. **{r.get('title', 'No title')}**")
        output.append(f"   URL: {r.get('url', '')}")
        output.append(f"   {r.get('description', 'No description')[:200]}...\n")
    
    # Optionally fetch full content from top result
    if use_fetch and results:
        top_url = results[0].get('url', '')
        if top_url:
            try:
                import sys
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from web_fetch import web_fetch
                
                print(f"[Fetch] Getting full content from: {top_url[:60]}...")
                content = web_fetch(top_url, max_chars=5000)
                
                if content:
                    output.append("\n### Detailed Content:\n")
                    output.append(content[:3000])  # Limit length
                    
            except Exception as e:
                print(f"[Fetch] Failed: {e}")
    
    return "\n".join(output)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 rate_limited_search.py 'search query'")
        sys.exit(1)
    
    query = sys.argv[1]
    print(smart_search(query))
