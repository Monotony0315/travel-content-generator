#!/usr/bin/env python3
"""
Direct Markdown-to-Notion Publisher
Takes raw markdown content and publishes it to Notion with proper formatting.
No templates, no generators - just clean markdown to Notion blocks.
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
    """Converts markdown to Notion blocks and publishes directly"""
    
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
    
    def publish(self, title: str, markdown: str, image_urls: List[str] = None) -> str:
        """
        Publish markdown content to Notion
        
        Args:
            title: Page title
            markdown: Full markdown content
            image_urls: List of image URLs to insert between days
        
        Returns:
            Notion page URL
        """
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
        
        # Convert markdown to blocks
        blocks = self._markdown_to_blocks(markdown, image_urls or [])
        
        logger.info(f"Total blocks: {len(blocks)}")
        
        # Add blocks in batches
        batch_size = 95
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i+batch_size]
            self._request("PATCH", f"/blocks/{page_id}/children", {"children": batch})
            logger.info(f"  Added {i+1}-{min(i+len(batch), len(blocks))} / {len(blocks)}")
        
        return page_url
    
    def _markdown_to_blocks(self, md: str, image_urls: List[str]) -> List[Dict]:
        """Convert markdown text to Notion API blocks"""
        blocks = []
        lines = md.split('\n')
        i = 0
        img_idx = 0
        day_count = 0
        in_numbered_list = False
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Empty line
            if not stripped:
                in_numbered_list = False
                i += 1
                continue
            
            # Divider
            if stripped == '---' or stripped == '***':
                blocks.append({"object": "block", "type": "divider", "divider": {}})
                i += 1
                continue
            
            # Heading 1: # Title
            if stripped.startswith('# ') and not stripped.startswith('## '):
                blocks.append(self._heading(1, stripped[2:]))
                i += 1
                continue
            
            # Heading 2: ## Day X or ## Section
            if stripped.startswith('## '):
                text = stripped[3:]
                # Insert image before new Day sections
                if re.match(r'Day\s+\d', text):
                    day_count += 1
                    if img_idx < len(image_urls):
                        blocks.append(self._image_block(
                            image_urls[img_idx],
                            f"Day {day_count}"
                        ))
                        img_idx += 1
                
                blocks.append(self._heading(2, text))
                i += 1
                continue
            
            # Heading 3: ### Section
            if stripped.startswith('### '):
                blocks.append(self._heading(3, stripped[4:]))
                i += 1
                continue
            
            # Table: | col | col |
            if '|' in stripped and stripped.startswith('|'):
                table_lines = []
                while i < len(lines) and '|' in lines[i].strip():
                    row = lines[i].strip()
                    # Skip separator rows (|---|---|)
                    if not re.match(r'^\|[\s\-:|]+\|$', row):
                        table_lines.append(row)
                    i += 1
                
                if table_lines:
                    table_block = self._build_table(table_lines)
                    if table_block:
                        blocks.append(table_block)
                continue
            
            # Numbered list: 1. item
            if re.match(r'^\d+\.\s', stripped):
                text = re.sub(r'^\d+\.\s', '', stripped)
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {"rich_text": self._rich_text(text)}
                })
                i += 1
                continue
            
            # Bullet list: - item or * item
            if stripped.startswith('- ') or stripped.startswith('* '):
                text = stripped[2:]
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": self._rich_text(text)}
                })
                i += 1
                continue
            
            # Callout: > text
            if stripped.startswith('> '):
                blocks.append({
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": self._rich_text(stripped[2:]),
                        "icon": {"emoji": "💡"}
                    }
                })
                i += 1
                continue
            
            # Regular paragraph
            # Collect consecutive non-special lines as one paragraph
            para_lines = [stripped]
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if (not next_line or 
                    next_line.startswith('#') or 
                    next_line.startswith('- ') or
                    next_line.startswith('* ') or
                    next_line.startswith('> ') or
                    next_line.startswith('|') or
                    next_line == '---' or
                    re.match(r'^\d+\.\s', next_line)):
                    break
                para_lines.append(next_line)
                i += 1
            
            full_text = ' '.join(para_lines)
            
            # Split long paragraphs
            if len(full_text) > self.MAX_TEXT:
                chunks = self._split_text(full_text)
                for chunk in chunks:
                    blocks.append(self._paragraph(chunk))
            else:
                blocks.append(self._paragraph(full_text))
        
        # Add remaining images at the end
        while img_idx < len(image_urls):
            blocks.append(self._image_block(image_urls[img_idx], ""))
            img_idx += 1
        
        return blocks
    
    def _rich_text(self, text: str) -> List[Dict]:
        """Parse text with **bold** and [links](url) into Notion rich_text"""
        if not text:
            return [{"type": "text", "text": {"content": ""}}]
        
        parts = []
        # Combined pattern for bold and links
        pattern = r'(\*\*(.+?)\*\*|\[([^\]]+)\]\(([^\)]+)\))'
        
        last_end = 0
        for match in re.finditer(pattern, text):
            # Add text before match
            if match.start() > last_end:
                pre = text[last_end:match.start()]
                if pre:
                    parts.append({"type": "text", "text": {"content": pre}})
            
            if match.group(2):  # Bold
                parts.append({
                    "type": "text",
                    "text": {"content": match.group(2)},
                    "annotations": {"bold": True}
                })
            elif match.group(3):  # Link
                parts.append({
                    "type": "text",
                    "text": {"content": match.group(3), "link": {"url": match.group(4)}},
                    "annotations": {"bold": True, "underline": True}
                })
            
            last_end = match.end()
        
        # Add remaining text
        if last_end < len(text):
            remaining = text[last_end:]
            if remaining:
                parts.append({"type": "text", "text": {"content": remaining}})
        
        return parts if parts else [{"type": "text", "text": {"content": text}}]
    
    def _heading(self, level: int, text: str) -> Dict:
        key = f"heading_{level}"
        return {"object": "block", "type": key, key: {"rich_text": self._rich_text(text)}}
    
    def _paragraph(self, text: str) -> Dict:
        return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": self._rich_text(text)}}
    
    def _image_block(self, url: str, caption: str = "") -> Dict:
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
    
    def _build_table(self, lines: List[str]) -> Optional[Dict]:
        """Build Notion table from markdown table lines"""
        rows = []
        for line in lines:
            cells = [c.strip() for c in line.split('|')]
            cells = [c for c in cells if c]  # Remove empty from leading/trailing |
            if cells:
                rows.append(cells)
        
        if len(rows) < 2:
            return None
        
        num_cols = max(len(r) for r in rows)
        
        # Pad rows to same width
        for row in rows:
            while len(row) < num_cols:
                row.append("")
        
        children = []
        for row in rows:
            cells = []
            for cell in row[:num_cols]:
                cells.append(self._rich_text(cell))
            children.append({
                "object": "block",
                "type": "table_row",
                "table_row": {"cells": cells}
            })
        
        return {
            "object": "block",
            "type": "table",
            "table": {
                "table_width": num_cols,
                "has_column_header": True,
                "has_row_header": False,
                "children": children
            }
        }
    
    def _split_text(self, text: str, max_len: int = 1900) -> List[str]:
        """Split long text into chunks"""
        if len(text) <= max_len:
            return [text]
        
        chunks = []
        while text:
            if len(text) <= max_len:
                chunks.append(text)
                break
            pos = text.rfind('. ', 0, max_len)
            if pos == -1:
                pos = text.rfind(' ', 0, max_len)
            if pos == -1:
                pos = max_len
            chunks.append(text[:pos+1])
            text = text[pos+1:].strip()
        return chunks


# Singleton
md_publisher = MarkdownNotionPublisher()


if __name__ == "__main__":
    """Test: publish a markdown file to Notion"""
    if len(sys.argv) < 2:
        print("Usage: python3 md_publisher.py <markdown_file> [title]")
        sys.exit(1)
    
    md_file = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else f"Travel Guide {datetime.now().strftime('%Y-%m-%d')}"
    
    with open(md_file, 'r') as f:
        content = f.read()
    
    url = md_publisher.publish(title, content)
    print(f"Published: {url}")
