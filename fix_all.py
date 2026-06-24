#!/usr/bin/env python3
"""
Batch fix for 圣经解经大全 chapter pages:
1. Convert unconverted **bold** and *italic* markdown to HTML
2. Fix CSS reference: ../style.css → ../../style.css (in chapter pages)
3. Fix code fences: ``` -> removed (in chapter pages)
"""
import re, os
from pathlib import Path

BASE = Path("/Users/andyshengruilee/programming/web2Lord/圣经解经大全")

def fix_markdown_in_html(html):
    """Fix unconverted markdown tokens inside HTML content"""
    # Fix **bold** → <strong>bold</strong> (but not inside <strong> tags already)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    # Fix *italic* → <em>italic</em> (single *, not **)
    html = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', html)
    # Remove stray ``` (code fence markers that weren't processed)
    html = re.sub(r'<p>```</p>\n?', '', html)
    html = re.sub(r'```\n?', '', html)
    return html

def fix_css_reference(html):
    """Change ../style.css to ../../style.css in chapter pages"""
    return html.replace('href="../style.css"', 'href="../../style.css"')

count_bold = 0
count_css = 0

for book_dir in sorted(BASE.iterdir()):
    if not book_dir.is_dir() or not book_dir.name.endswith("解经大全"):
        continue

    # Fix chapter HTML files
    for chapter_dir in sorted(book_dir.iterdir()):
        if not chapter_dir.is_dir():
            continue
        html_file = chapter_dir / "解经.html"
        if not html_file.exists():
            continue

        content = html_file.read_text(encoding='utf-8')

        # Check if needs bold fix
        if '**' in content:
            content = fix_markdown_in_html(content)
            count_bold += 1

        # Check if needs CSS fix
        if 'href="../style.css"' in content:
            content = fix_css_reference(content)
            count_css += 1

        html_file.write_text(content, encoding='utf-8')

book_css_fixes = 0
# Also fix book-level index.html CSS references
for book_dir in sorted(BASE.iterdir()):
    if not book_dir.is_dir() or not book_dir.name.endswith("解经大全"):
        continue
    index_file = book_dir / "index.html"
    if not index_file.exists():
        continue
    content = index_file.read_text(encoding='utf-8')
    # Fix book index CSS: some books use ../style.css which is fine (goes to global)
    # Some use style.css which is fine (goes to book level)
    # No change needed for book index
    pass

print(f"修复 bold markdown: {count_bold} 个章节")
print(f"修复 CSS 引用: {count_css} 个章节")
print("Done!")
