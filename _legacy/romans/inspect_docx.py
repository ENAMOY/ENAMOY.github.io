import docx
import os

file_path = '/Users/andyshengruilee/Documents/website/web2Lord/romans/罗马书讲道集 第一部 V2.0 Martha.docx'
output_path = '/Users/andyshengruilee/Documents/website/web2Lord/romans/docx_dump.txt'

doc = docx.Document(file_path)

with open(output_path, 'w', encoding='utf-8') as f:
    for i, p in enumerate(doc.paragraphs):
        text = p.text.strip()
        if text:
            style = p.style.name
            f.write(f"{i}: [{style}] {text}\n")
