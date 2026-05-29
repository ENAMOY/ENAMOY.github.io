import json
import os

# Use absolute path to be safe
CONTENT_FILE = '/Users/andyshengruilee/Documents/website/web2Lord/romans/romans_content.json'

if not os.path.exists(CONTENT_FILE):
    print(f"File not found: {CONTENT_FILE}")
    exit(1)

with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
    content = json.load(f)

preface_count = 0
section_count = 0

for item in content:
    if item['type'] == 'preface':
        preface_count += len(item['sections'])
    elif item['type'] == 'part':
        for chapter in item['data']['chapters']:
            section_count += len(chapter['sections'])

print(f"Preface sections: {preface_count}")
print(f"Content sections: {section_count}")
