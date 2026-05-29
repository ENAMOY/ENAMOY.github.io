import docx
import json
import re
import os

file_path = 'romans/罗马书讲道集 第一部 V2.0 Martha.docx'
output_path = 'romans/romans_content.json'

def parse_docx(file_path):
    doc = docx.Document(file_path)
    
    content = []
    current_part = None
    current_chapter = None
    current_section = None
    
    # Regex patterns
    part_pattern = re.compile(r'^第[一二三四五六七八九十]+部')
    chapter_pattern = re.compile(r'^第[一二三四五六七八九十]+章')
    section_pattern = re.compile(r'^[一二三四五六七八九十]+、')
    
    # Skip TOC (heuristic: skip until we see "前言" or "序言" or "第一部" in body)
    # Actually, looking at the analysis, the body starts around paragraph 108 ("前言").
    # But "第一部" starts later.
    # Let's iterate and state-manage.
    
    start_processing = False
    
    for p in doc.paragraphs:
        text = p.text.strip()
        style = p.style.name
        
        if not text:
            continue
            
        # Skip TOC entries based on style
        if 'toc' in style.lower():
            continue
            
        # Also skip lines that look like TOC entries (ending with numbers) if style check fails
        # Regex for ending with number: \d+$
        if re.search(r'\d+$', text) and '\t' in p.text:
             continue

        # Heuristic to start processing actual content
        if text == "前言" and not start_processing:
            start_processing = True
            # Create a dummy part/chapter for Preface if needed, or just treat as separate
            current_section = {"title": "前言", "content": []}
            content.append({"type": "preface", "title": "前言", "sections": [current_section]})
            continue
            
        if text == "序言" and not start_processing: # In case we missed Preface or it's separate
             start_processing = True
        
        # Special handling for Part 1 and Chapter 1 which miss the "第一部" / "第一章" prefix in body
        if text == "福音与神的义（罗1:1-17）":
            start_processing = True
            current_part = {"title": "第一部 " + text, "chapters": []}
            content.append({"type": "part", "data": current_part})
            current_chapter = None
            current_section = None
            continue

        if text == "保罗奉召（罗1:1）":
            current_chapter = {"title": "第一章 " + text, "sections": []}
            if current_part:
                current_part["chapters"].append(current_chapter)
            else:
                # Fallback if Part 1 was missed
                current_part = {"title": "第一部", "chapters": [current_chapter]}
                content.append({"type": "part", "data": current_part})
            current_section = None
            continue

        if not start_processing:
            # Check if we hit the first part directly
            if part_pattern.match(text):
                start_processing = True
            else:
                continue

        # Now processing
        if part_pattern.match(text):
            current_part = {"title": text, "chapters": []}
            content.append({"type": "part", "data": current_part})
            current_chapter = None
            current_section = None
        elif chapter_pattern.match(text):
            current_chapter = {"title": text, "sections": []}
            if current_part:
                current_part["chapters"].append(current_chapter)
            else:
                # Orphan chapter (shouldn't happen ideally)
                content.append({"type": "chapter", "data": current_chapter})
            current_section = None
        elif section_pattern.match(text):
            current_section = {"title": text, "content": []}
            if current_chapter:
                current_chapter["sections"].append(current_section)
            elif current_part:
                 # Section directly under Part? Unlikely but possible
                 pass
            else:
                # Section at root (like Preface/Intro)
                # If we are in the "preface" block
                if content and content[-1]["type"] == "preface":
                     content[-1]["sections"].append(current_section)
        else:
            # Normal text
            if current_section:
                current_section["content"].append(text)
            elif current_chapter:
                # Text directly under Chapter before first Section
                # Create an intro section for the chapter if needed
                if not current_chapter["sections"]:
                    current_chapter["sections"].append({"title": "引言", "content": []})
                current_chapter["sections"][-1]["content"].append(text)
            elif current_part:
                 # Text directly under Part
                 pass
            elif content and content[-1]["type"] == "preface":
                 content[-1]["sections"][-1]["content"].append(text)

    return content

try:
    data = parse_docx(file_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Successfully extracted content to {output_path}")
except Exception as e:
    print(f"Error: {e}")
