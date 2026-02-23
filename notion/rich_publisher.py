"""
Rich Content Notion Publisher
Directly publishes subagent-generated rich travel content to Notion
"""

import os
import re
from datetime import datetime
from typing import Dict, List
from loguru import logger
from notion_client import Client


class RichContentPublisher:
    """Publishes rich subagent-generated content directly to Notion"""
    
    def __init__(self):
        self.notion = Client(auth=os.getenv("NOTION_API_KEY"))
        self.parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")
    
    def publish_travel_guide(self, city: str, content: str, images: List[Dict]) -> str:
        """
        Publish rich travel guide directly to Notion
        
        Args:
            city: City name
            content: Full rich content from subagent (markdown format)
            images: List of image dicts with urls
        """
        
        # Parse content sections
        title = self._extract_title(content)
        days_content = self._parse_days(content)
        practical_info = self._parse_practical_info(content)
        
        # Create main page
        page_title = f"{datetime.now().strftime('%Y-%m-%d')} {city} Complete Travel Guide"
        
        page = self.notion.pages.create(
            parent={"page_id": self.parent_page_id},
            properties={
                "title": {"title": [{"text": {"content": page_title}}]}
            }
        )
        
        page_id = page["id"]
        
        # Build blocks
        blocks = []
        
        # Hero image
        if images:
            blocks.append(self._create_image_block(images[0]["url"], f"{city} 여행의 시작"))
        
        # Introduction
        intro = self._extract_intro(content)
        if intro:
            blocks.extend(self._create_text_blocks(intro))
        
        # Each day
        for day_num, day_content in days_content.items():
            blocks.append(self._create_heading_1(f"Day {day_num}"))
            blocks.extend(self._format_day_content(day_content))
            
            # Add relevant image for this day
            if len(images) > day_num:
                blocks.append(self._create_image_block(
                    images[min(day_num, len(images)-1)]["url"],
                    f"Day {day_num} 대표 이미지"
                ))
        
        # Practical info section
        if practical_info:
            blocks.append(self._create_heading_1("실용 정보"))
            blocks.extend(self._format_practical_info(practical_info))
        
        # Add all blocks
        self._add_blocks_to_page(page_id, blocks)
        
        logger.info(f"✅ Published rich travel guide to Notion: {page_title}")
        return f"https://www.notion.so/{page_id.replace('-', '')}"
    
    def _extract_title(self, content: str) -> str:
        """Extract title from content"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1) if match else "Travel Guide"
    
    def _extract_intro(self, content: str) -> str:
        """Extract introduction (content before first Day)"""
        match = re.search(r'^(.*?)##\s+Day\s+1', content, re.DOTALL)
        if match:
            intro = match.group(1).strip()
            # Remove title
            intro = re.sub(r'^#\s+.+$', '', intro, flags=re.MULTILINE).strip()
            return intro
        return ""
    
    def _parse_days(self, content: str) -> Dict[int, str]:
        """Parse each day's content"""
        days = {}
        day_pattern = r'##\s+Day\s+(\d+):?\s*([^\n]*)\n(.*?)(?=##\s+Day|\Z)'
        
        for match in re.finditer(day_pattern, content, re.DOTALL):
            day_num = int(match.group(1))
            day_title = match.group(2).strip()
            day_content = match.group(3).strip()
            days[day_num] = f"**{day_title}**\n\n{day_content}"
        
        return days
    
    def _parse_practical_info(self, content: str) -> str:
        """Parse practical info section"""
        match = re.search(r'##\s+(?:전체 요약|실용 정보|요약).*?$(.*)', content, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _format_day_content(self, day_content: str) -> List[Dict]:
        """Format day content into Notion blocks"""
        blocks = []
        
        # Split by sections (Morning, Lunch, Afternoon, Evening)
        sections = re.split(r'###\s+', day_content)
        
        for section in sections:
            if not section.strip():
                continue
            
            # Check if it's a time section
            time_match = re.match(r'(Morning|Lunch|Afternoon|Evening).*?\n', section, re.IGNORECASE)
            
            if time_match:
                section_title = time_match.group(0).strip()
                section_body = section[len(time_match.group(0)):].strip()
                
                blocks.append(self._create_heading_3(section_title))
                blocks.extend(self._create_rich_text_blocks(section_body))
            else:
                blocks.extend(self._create_rich_text_blocks(section))
        
        return blocks
    
    def _format_practical_info(self, info: str) -> List[Dict]:
        """Format practical info into blocks"""
        blocks = []
        
        # Split by subsections
        sections = re.split(r'###\s+', info)
        
        for section in sections:
            if not section.strip():
                continue
            
            lines = section.strip().split('\n')
            if lines:
                # First line is heading
                blocks.append(self._create_heading_2(lines[0]))
                # Rest is content
                if len(lines) > 1:
                    content = '\n'.join(lines[1:])
                    blocks.extend(self._create_rich_text_blocks(content))
        
        return blocks
    
    def _create_heading_1(self, text: str) -> Dict:
        return {
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        }
    
    def _create_heading_2(self, text: str) -> Dict:
        return {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        }
    
    def _create_heading_3(self, text: str) -> Dict:
        return {
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        }
    
    def _create_text_blocks(self, text: str) -> List[Dict]:
        """Create paragraph blocks from text"""
        blocks = []
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": para.strip()}}]
                    }
                })
        
        return blocks
    
    def _create_rich_text_blocks(self, text: str) -> List[Dict]:
        """Create rich text blocks with formatting"""
        blocks = []
        
        # Split by double newlines
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Check for list items
            if para.startswith('- ') or para.startswith('* '):
                items = [line.strip()[2:] for line in para.split('\n') if line.strip().startswith('- ') or line.strip().startswith('* ')]
                if items:
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": items[0]}}]
                        }
                    })
                    for item in items[1:]:
                        blocks.append({
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {
                                "rich_text": [{"type": "text", "text": {"content": item}}]
                            }
                        })
            # Check for table-like content (budget tables)
            elif '|' in para:
                blocks.extend(self._create_table_from_text(para))
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": self._parse_inline_formatting(para)
                    }
                })
        
        return blocks
    
    def _parse_inline_formatting(self, text: str) -> List[Dict]:
        """Parse inline markdown formatting (bold, italic)"""
        parts = []
        
        # Split by bold markers
        bold_pattern = r'\*\*(.+?)\*\*'
        segments = re.split(bold_pattern, text)
        
        for i, segment in enumerate(segments):
            if segment:
                if i % 2 == 1:  # Odd indices are bold
                    parts.append({
                        "type": "text",
                        "text": {"content": segment},
                        "annotations": {"bold": True}
                    })
                else:
                    parts.append({
                        "type": "text",
                        "text": {"content": segment}
                    })
        
        return parts if parts else [{"type": "text", "text": {"content": text}}]
    
    def _create_table_from_text(self, text: str) -> List[Dict]:
        """Create a table from markdown table text"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Filter out separator lines
        rows = [line for line in lines if not re.match(r'^[\|\-\s]+$', line)]
        
        if len(rows) < 1:
            return [{
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]}
            }]
        
        # Parse rows
        table_rows = []
        for row in rows:
            cells = [cell.strip() for cell in row.split('|') if cell.strip()]
            table_rows.append(cells)
        
        if not table_rows:
            return []
        
        num_columns = max(len(row) for row in table_rows)
        
        # Build table block
        table_block = {
            "object": "block",
            "type": "table",
            "table": {
                "table_width": num_columns,
                "has_column_header": True,
                "has_row_header": False,
                "children": []
            }
        }
        
        for row in table_rows:
            table_row = {
                "object": "block",
                "type": "table_row",
                "table_row": {
                    "cells": []
                }
            }
            for cell in row:
                table_row["table_row"]["cells"].append([
                    {"type": "text", "text": {"content": cell}}
                ])
            table_block["table"]["children"].append(table_row)
        
        return [table_block]
    
    def _create_image_block(self, url: str, caption: str = "") -> Dict:
        return {
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {"url": url},
                "caption": [{"type": "text", "text": {"content": caption}}] if caption else []
            }
        }
    
    def _add_blocks_to_page(self, page_id: str, blocks: List[Dict]):
        """Add blocks to page in batches"""
        batch_size = 100
        
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]
            try:
                self.notion.blocks.children.append(
                    block_id=page_id,
                    children=batch
                )
                logger.info(f"   Added {i+1}-{min(i+len(batch), len(blocks))} / {len(blocks)}")
            except Exception as e:
                logger.error(f"   Error adding blocks {i+1}-{i+len(batch)}: {e}")


# Singleton
rich_publisher = RichContentPublisher()
