#!/usr/bin/env python3
"""
Direct Rich Content Publisher for Notion
Bypasses template generators, uses subagent content directly
"""

import os
import sys
import re
import json
import urllib.request
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from content.accurate_image_fetcher import accurate_image_fetcher


class DirectRichPublisher:
    """Publishes subagent-generated rich content directly to Notion"""
    
    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"
    
    def __init__(self):
        self.api_key = os.getenv("NOTION_API_KEY", "")
        self.parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID", "")
    
    def _request(self, method: str, path: str, payload: dict = None) -> dict:
        url = f"{self.BASE_URL}{path}"
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8') if payload else None
        
        req = urllib.request.Request(
            url=url,
            data=data,
            method=method,
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
            raise RuntimeError(f"Notion API error {e.code}: {body}")
    
    def publish(self, city: str, content: str, images: list) -> str:
        """Publish rich content to Notion"""
        
        # Create page
        title = f"{datetime.now().strftime('%Y-%m-%d')} {city} 완벽 가이드 | 프로 여행 블로거 추천 일정"
        
        page = self._request("POST", "/pages", {
            "parent": {"page_id": self.parent_page_id},
            "properties": {
                "title": {"title": [{"text": {"content": title}}]}
            }
        })
        
        page_id = page["id"]
        
        # Build blocks from content
        blocks = self._content_to_blocks(content, images)
        
        # Add blocks in batches
        batch_size = 100
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i+batch_size]
            self._request("PATCH", f"/blocks/{page_id}/children", {
                "children": batch
            })
            logger.info(f"   Added blocks {i+1}-{min(i+len(batch), len(blocks))}")
        
        return f"https://notion.so/{page_id.replace('-', '')}"
    
    def _content_to_blocks(self, content: str, images: list) -> list:
        """Convert markdown content to Notion blocks"""
        blocks = []
        img_idx = 0
        
        # Split content by lines
        lines = content.split('\n')
        i = 0
        current_day = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines
            if not line.strip():
                i += 1
                continue
            
            # Heading 1 (# Title)
            if line.startswith('# ') and not line.startswith('## '):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:].strip()}}]
                    }
                })
            
            # Heading 2 (## Day X)
            elif line.startswith('## '):
                current_day += 1
                # Add image before each new day (except first)
                if current_day > 1 and img_idx < len(images):
                    blocks.append(self._image_block(images[img_idx]["url"], f"Day {current_day}"))
                    img_idx += 1
                
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:].strip()}}]
                    }
                })
            
            # Heading 3 (### Section)
            elif line.startswith('### '):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": line[4:].strip()}}]
                    }
                })
            
            # Bullet list (- item)
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                item_text = line.strip()[2:]
                # Check if bold in item
                rich_text = self._parse_bold(item_text)
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": rich_text}
                })
            
            # Table (| col1 | col2 |)
            elif '|' in line and ('---' in line or line.strip().startswith('|')):
                # Collect table rows
                table_lines = [line]
                i += 1
                while i < len(lines) and '|' in lines[i]:
                    if '---' not in lines[i]:  # Skip separator
                        table_lines.append(lines[i])
                    i += 1
                
                if len(table_lines) >= 2:
                    table_block = self._create_table(table_lines)
                    if table_block:
                        blocks.append(table_block)
                continue  # Skip i += 1 at end
            
            # Divider (---)
            elif line.strip() == '---':
                blocks.append({
                    "object": "block",
                    "type": "divider",
                    "divider": {}
                })
            
            # Regular paragraph
            else:
                rich_text = self._parse_bold(line)
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": rich_text}
                })
            
            i += 1
        
        return blocks
    
    def _parse_bold(self, text: str) -> list:
        """Parse **bold** text"""
        parts = []
        # Split by **
        segments = re.split(r'\*\*', text)
        for idx, seg in enumerate(segments):
            if seg:
                if idx % 2 == 1:  # Odd indices are bold
                    parts.append({
                        "type": "text",
                        "text": {"content": seg},
                        "annotations": {"bold": True}
                    })
                else:
                    parts.append({"type": "text", "text": {"content": seg}})
        return parts if parts else [{"type": "text", "text": {"content": text}}]
    
    def _create_table(self, lines: list) -> dict:
        """Create Notion table from markdown lines"""
        # Parse rows
        rows = []
        for line in lines:
            if '---' in line:
                continue
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells:
                rows.append(cells)
        
        if not rows:
            return None
        
        num_cols = max(len(r) for r in rows)
        
        # Build table
        table = {
            "object": "block",
            "type": "table",
            "table": {
                "table_width": num_cols,
                "has_column_header": True,
                "has_row_header": False,
                "children": []
            }
        }
        
        for row in rows:
            table_row = {
                "object": "block",
                "type": "table_row",
                "table_row": {"cells": []}
            }
            for cell in row:
                table_row["table_row"]["cells"].append([
                    {"type": "text", "text": {"content": cell}}
                ])
            table["table"]["children"].append(table_row)
        
        return table
    
    def _image_block(self, url: str, caption: str = "") -> dict:
        return {
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {"url": url},
                "caption": [{"type": "text", "text": {"content": caption}}]
            }
        }


# Create instance
direct_publisher = DirectRichPublisher()
