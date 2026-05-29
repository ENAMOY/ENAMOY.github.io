import json
import os
import re
import hashlib

CONTENT_FILE = 'romans/romans_content.json'
OUTPUT_DIR = 'romans'
PAGES_DIR = 'romans/pages'
DATA_DIR = 'romans/data'

def load_content():
    with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_id(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()[:8]

def parse_scripture(text):
    # Pattern: Text ending with (Book Ref)
    # Example: ...福音。(罗马书1:1)
    # Also handle spaces: (罗马书 1:1)
    # Also handle range: (罗马书 1:1-7)
    # Also handle version suffix: (罗马书 1:1 和合本) -> The doc seems to have "和合本" sometimes?
    # Looking at JSON: "(罗马书 1:18 和合本)"
    
    pattern = re.compile(r'(.*)[（\(]([\u4e00-\u9fa5]+\s*\d+[:：]\d+(?:[-－]\d+)?(?:.*)?)[）\)]$')
    match = pattern.match(text.strip())
    if match:
        scripture_text = match.group(1).strip()
        reference = match.group(2).strip()
        return scripture_text, reference
    return None, None

def create_html_page(title, subtitle, content_paragraphs, prev_page, next_page, page_id):
    verses_data = {}
    
    html_content = []
    html_content.append(f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 罗马书讲道集</title>
    <link rel="stylesheet" href="../css/style.css">
    <style>
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.05); }}
        body {{ background-color: #f5f7fa; color: #333; font-family: "PingFang SC", "Microsoft YaHei", sans-serif; }}
        h1 {{ color: #2c3e50; }}
        .subtitle {{ color: #7f8c8d; font-size: 1.1em; margin-bottom: 30px; }}
        p {{ line-height: 1.8; margin-bottom: 1.5em; text-align: justify; }}
        .navigation {{ display: flex; justify-content: space-between; margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; }}
        .nav-btn {{ text-decoration: none; color: #3498db; padding: 10px 20px; border: 1px solid #3498db; border-radius: 5px; transition: all 0.3s; }}
        .nav-btn:hover {{ background: #3498db; color: white; }}
        .nav-btn.disabled {{ opacity: 0.5; pointer-events: none; border-color: #ccc; color: #ccc; }}
        .home-btn {{ background: #f8f9fa; border-color: #ddd; color: #666; }}
        .home-btn:hover {{ background: #e9ecef; color: #333; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <div class="subtitle">{subtitle}</div>
        </header>
        <div class="content">
''')

    for p in content_paragraphs:
        s_text, s_ref = parse_scripture(p)
        if s_text:
            # It's a scripture
            v_id = generate_id(s_text + s_ref)
            verses_data[v_id] = {
                "id": v_id,
                "ref": s_ref,
                "versions": {
                    "cuv": s_text,
                    "ccb": "（暂无当代译本）",
                    "esv": "(ESV not available)"
                }
            }
            html_content.append(f'<div class="scripture-container" data-id="{v_id}"><div class="scripture-text">{s_text}</div><div class="scripture-ref">({s_ref})</div></div>')
        else:
            html_content.append(f'<p>{p}</p>')

    # Navigation
    prev_link = f'<a href="{prev_page}" class="nav-btn">← 上一篇</a>' if prev_page else '<span class="nav-btn disabled">← 上一篇</span>'
    next_link = f'<a href="{next_page}" class="nav-btn">下一篇 →</a>' if next_page else '<span class="nav-btn disabled">下一篇 →</span>'
    
    html_content.append(f'''
        </div>
        <div class="navigation">
            {prev_link}
            <a href="../index.html" class="nav-btn home-btn">目录</a>
            {next_link}
        </div>
    </div>
    <script src="../js/bible-version.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            // Initialize bible manager
            // We need to pass the page_id to load the correct JSON
            window.bibleManager.init('{page_id}');
        }});
    </script>
</body>
</html>
''')

    # Save HTML
    with open(os.path.join(PAGES_DIR, f'{page_id}.html'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))
        
    # Save JSON
    with open(os.path.join(DATA_DIR, f'{page_id}_verses.json'), 'w', encoding='utf-8') as f:
        json.dump(verses_data, f, ensure_ascii=False, indent=2)

def generate_site():
    content = load_content()
    
    # Flatten structure for navigation
    pages = []
    
    # Process Preface
    preface_count = 0
    for item in content:
        if item['type'] == 'preface':
            for section in item['sections']:
                preface_count += 1
                pages.append({
                    'title': section['title'],
                    'subtitle': '前言',
                    'content': section['content'],
                    'id': f'preface_{preface_count}'
                })
        elif item['type'] == 'part':
            part_title = item['data']['title']
            for chapter in item['data']['chapters']:
                chap_title = chapter['title']
                for i, section in enumerate(chapter['sections']):
                    sec_title = section['title']
                    # ID: partX_chapY_secZ -> simplified to pX_cY_sZ
                    # But we don't have explicit numbers easily, so let's use a counter or hash
                    # Let's use a sequential ID for simplicity in filenames
                    page_id = f"page_{len(pages)}"
                    pages.append({
                        'title': sec_title,
                        'subtitle': f"{part_title} > {chap_title}",
                        'content': section['content'],
                        'id': page_id
                    })

    # Generate Pages
    for i, page in enumerate(pages):
        prev_page = f"{pages[i-1]['id']}.html" if i > 0 else None
        next_page = f"{pages[i+1]['id']}.html" if i < len(pages) - 1 else None
        
        create_html_page(
            page['title'],
            page['subtitle'],
            page['content'],
            prev_page,
            next_page,
            page['id']
        )
        print(f"Generated {page['id']}.html")

    # Generate Index (TOC)
    generate_index(content, pages)

def generate_index(content, pages_flat):
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>罗马书讲道集 - 目录</title>
    <link rel="stylesheet" href="css/style.css">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; font-family: sans-serif; }
        .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 15px; padding: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        h1 { text-align: center; color: #333; margin-bottom: 40px; }
        .part-title { font-size: 1.4em; color: #667eea; margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .chapter-title { font-size: 1.2em; color: #555; margin-top: 20px; margin-bottom: 10px; font-weight: bold; padding-left: 10px; border-left: 4px solid #667eea; }
        .section-list { list-style: none; padding: 0; }
        .section-item { margin-bottom: 10px; padding-left: 20px; }
        .section-item a { text-decoration: none; color: #666; display: block; padding: 8px; border-radius: 5px; transition: background 0.2s; }
        .section-item a:hover { background: #f0f2f5; color: #333; }
        .home-link { display: block; text-align: center; margin-bottom: 20px; color: white; text-decoration: none; opacity: 0.8; }
        .home-link:hover { opacity: 1; }
    </style>
</head>
<body>
    <a href="../index.html" class="home-link">← 返回主页</a>
    <div class="container">
        <h1>罗马书讲道集</h1>
'''
    
    page_map = {p['title']: p['id'] for p in pages_flat}
    # Note: Titles might not be unique, but in this book they seem to be "一、...", "二、..." which are not unique globally.
    # We need a better mapping.
    # Let's iterate content and pop from pages_flat? No, pages_flat is linear.
    
    page_idx = 0
    
    for item in content:
        if item['type'] == 'preface':
            html += '<div class="part-title">前言</div><ul class="section-list">'
            for section in item['sections']:
                pid = pages_flat[page_idx]['id']
                html += f'<li class="section-item"><a href="pages/{pid}.html">{section["title"]}</a></li>'
                page_idx += 1
            html += '</ul>'
            
        elif item['type'] == 'part':
            html += f'<div class="part-title">{item["data"]["title"]}</div>'
            for chapter in item['data']['chapters']:
                html += f'<div class="chapter-title">{chapter["title"]}</div><ul class="section-list">'
                for section in chapter['sections']:
                    pid = pages_flat[page_idx]['id']
                    html += f'<li class="section-item"><a href="pages/{pid}.html">{section["title"]}</a></li>'
                    page_idx += 1
                html += '</ul>'

    html += '''
    </div>
</body>
</html>
'''
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print("Generated index.html")

if __name__ == '__main__':
    generate_site()
