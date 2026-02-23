#!/usr/bin/env python3
"""
Enhanced Markdown-to-Notion Publisher with Image Block Support
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.error
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger


class MarkdownNotionPublisher:
    """Converts markdown to Notion blocks with proper image handling"""
    
    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"
    MAX_TEXT = 1900
    
    def __init__(self):
        self.api_key = os.getenv("NOTION_API_KEY", "")
        self.parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID", "")
        self.enabled = bool(self.api_key and self.parent_page_id)
    
    def _request(self, method: str, path: str, payload: dict = None) -> dict:
        url = f"{self.BASE_URL}{path}"
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8') if payload else None
        
        req = urllib.request.Request(
            url=url, data=data, method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": self.NOTION_VERSION,
                "Content-Type": "application/json",
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='ignore')
            logger.error(f"Notion API {e.code}: {body[:200]}")
            raise RuntimeError(f"Notion API error {e.code}: {body[:200]}")
    
    def _make_text_block(self, text: str) -> dict:
        """Create a paragraph block with plain text"""
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": text[:self.MAX_TEXT]}}]
            }
        }

    def _make_rich_text_block(self, rich_text: List[dict]) -> dict:
        """Create a paragraph block with rich_text (supports links)."""
        # Notion hard-limits text lengths; we keep chunks small.
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": rich_text[:100]  # safety cap on segments
            }
        }

    def _rt_from_markdown_inline(self, s: str) -> List[dict]:
        """Convert markdown inline links [text](url) into Notion rich_text."""
        out: List[dict] = []
        pattern = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
        pos = 0
        for m in pattern.finditer(s):
            if m.start() > pos:
                chunk = s[pos:m.start()]
                if chunk:
                    out.append({"type": "text", "text": {"content": chunk}})
            text = m.group(1)
            url = m.group(2)
            out.append({"type": "text", "text": {"content": text, "link": {"url": url}}})
            pos = m.end()
        if pos < len(s):
            chunk = s[pos:]
            if chunk:
                out.append({"type": "text", "text": {"content": chunk}})
        # Trim overlong segments conservatively
        for seg in out:
            if seg.get("type") == "text":
                c = seg["text"].get("content", "")
                if len(c) > self.MAX_TEXT:
                    seg["text"]["content"] = c[: self.MAX_TEXT]
        return out

    def _make_table_block(self, rows: List[List[str]], has_header: bool = True) -> dict:
        """Create a Notion table block with table_row children."""
        if not rows:
            return self._make_text_block("(empty table)")
        width = max(len(r) for r in rows)

        def cell_rt(txt: str) -> List[dict]:
            # Keep links clickable even inside tables if they exist.
            return self._rt_from_markdown_inline(txt)

        children = []
        for r in rows:
            # pad
            r = r + [""] * (width - len(r))
            children.append({
                "object": "block",
                "type": "table_row",
                "table_row": {
                    "cells": [cell_rt(c) for c in r]
                }
            })

        return {
            "object": "block",
            "type": "table",
            "table": {
                "table_width": width,
                "has_column_header": bool(has_header),
                "has_row_header": False,
                "children": children
            }
        }
    
    def _make_heading_block(self, text: str, level: int = 1) -> dict:
        """Create a heading block"""
        block_type = f"heading_{min(level, 3)}"
        return {
            "object": "block",
            "type": block_type,
            block_type: {
                "rich_text": [{"type": "text", "text": {"content": text[:self.MAX_TEXT]}}]
            }
        }
    
    def _make_image_block(self, url: str, caption: str = "") -> dict:
        """Create an image block with external URL"""
        block = {
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {"url": url}
            }
        }
        if caption:
            block["image"]["caption"] = [{"type": "text", "text": {"content": caption}}]
        return block
    
    def _make_divider_block(self) -> dict:
        """Create a divider block"""
        return {"object": "block", "type": "divider", "divider": {}}
    
    def _make_quote_block(self, text: str) -> dict:
        """Create a quote block"""
        return {
            "object": "block",
            "type": "quote",
            "quote": {
                "rich_text": [{"type": "text", "text": {"content": text[:self.MAX_TEXT]}}]
            }
        }
    
    def _is_table_line(self, s: str) -> bool:
        s = s.strip()
        return s.startswith('|') and '|' in s[1:]

    def _parse_table_row(self, s: str) -> List[str]:
        # split and trim; ignore outer pipes
        parts = [p.strip() for p in s.strip().strip('|').split('|')]
        return parts

    def _is_table_sep(self, s: str) -> bool:
        # e.g. |---|:---:|---|
        s = s.strip().strip('|')
        if not s:
            return False
        parts = [p.strip() for p in s.split('|')]
        return all(re.fullmatch(r':?-{3,}:?', p) is not None for p in parts)

    def parse_markdown_to_blocks(self, markdown: str) -> List[dict]:
        """Parse markdown into Notion blocks with image + table + inline-link support."""
        blocks: List[dict] = []
        lines = markdown.split('\n')
        i = 0

        while i < len(lines):
            raw = lines[i]
            line = raw.strip()

            if not line:
                i += 1
                continue

            # Markdown table block
            if self._is_table_line(line):
                # capture until non-table line
                table_lines = []
                while i < len(lines) and self._is_table_line(lines[i].strip()):
                    table_lines.append(lines[i].strip())
                    i += 1
                # parse
                rows = []
                for idx, tl in enumerate(table_lines):
                    if idx == 1 and self._is_table_sep(tl):
                        continue
                    rows.append(self._parse_table_row(tl))
                has_header = len(table_lines) >= 2 and self._is_table_sep(table_lines[1])
                blocks.append(self._make_table_block(rows, has_header=has_header))
                continue

            # Image
            img_match = re.match(r'!\[([^\]]*)\]\(([^\)]+)\)', line)
            if img_match:
                caption = img_match.group(1)
                url = img_match.group(2)
                # Caption is provided by the markdown author. Keep as-is (so we can include proper attribution like "Photo: Unsplash/Pexels/Pixabay/Wikimedia").
                blocks.append(self._make_image_block(url, caption or ""))
                i += 1
                continue

            # Divider
            if line in ('---', '***'):
                blocks.append(self._make_divider_block())
                i += 1
                continue

            # Headings
            h1_match = re.match(r'^# (.+)$', line)
            if h1_match:
                blocks.append(self._make_heading_block(h1_match.group(1), 1))
                i += 1
                continue
            h2_match = re.match(r'^## (.+)$', line)
            if h2_match:
                blocks.append(self._make_heading_block(h2_match.group(1), 2))
                i += 1
                continue
            h3_match = re.match(r'^### (.+)$', line)
            if h3_match:
                blocks.append(self._make_heading_block(h3_match.group(1), 3))
                i += 1
                continue

            # Blockquote
            if line.startswith('>'):
                blocks.append(self._make_quote_block(line[1:].strip()))
                i += 1
                continue

            # Paragraph with inline links
            rich = self._rt_from_markdown_inline(line)
            blocks.append(self._make_rich_text_block(rich))
            i += 1

        return blocks
    
    def publish(self, title: str, markdown: str) -> str:
        """Publish markdown content to Notion with image blocks"""
        if not self.enabled:
            raise RuntimeError("Notion API not configured")
        
        # Create page
        page = self._request("POST", "/pages", {
            "parent": {"page_id": self.parent_page_id},
            "properties": {
                "title": {"title": [{"text": {"content": title}}]}
            }
        })
        
        page_id = page["id"]
        page_url = page.get("url", f"https://notion.so/{page_id.replace('-', '')}")
        
        # Parse markdown to blocks
        blocks = self.parse_markdown_to_blocks(markdown)
        
        logger.info(f"Total blocks: {len(blocks)}")
        
        # Add blocks in batches
        batch_size = 95
        for j in range(0, len(blocks), batch_size):
            batch = blocks[j:j+batch_size]
            self._request("PATCH", f"/blocks/{page_id}/children", {"children": batch})
            logger.info(f"  Added {j+1}-{min(j+len(batch), len(blocks))} / {len(blocks)}")
        
        return page_url


# Global instance
md_publisher = MarkdownNotionPublisher()


if __name__ == "__main__":
    # Test with sample content
    title = "Test Paris Guide"
    
    markdown = """# 파리 5일 여행

파리는 멋진 도시예요.

![에펠탑 사진](https://images.unsplash.com/photo-1511739001486-6bfe10ce785f)

## Day 1: 에펠탑

[트로카드로](https://maps.google.com/?q=Trocadero)에서 시작하세요.

> 파리의 아침은 정말 아름다워요.

---

## Day 2: 루브르

루브르 박물관을 방문하세요.
"""
    
    url = md_publisher.publish(title, markdown)
    print(f"Published: {url}")
