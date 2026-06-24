#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换 one2one 网站为多圣经版本网站
1. 复制 HTML 结构和内容
2. 识别经文块，添加 data-id
3. 提取经文到 JSON
4. 注入 JS/CSS
"""
import os
import json
import re
import hashlib
from bs4 import BeautifulSoup

SRC_DIR = '../one2one'
DST_DIR = '.'
DATA_DIR = 'data'

FILES_TO_PROCESS = [
    'index.html',
    'intro.html',
    'preface.html',
    'steps.html',
    'chapter_1.html',
    'chapter_2.html',
    'chapter_3.html',
    'chapter_4.html',
    'chapter_5.html',
    'chapter_6.html',
    'chapter_7.html'
]

def generate_verse_id(reference):
    """生成经文ID，使用引用的哈希值"""
    return hashlib.md5(reference.encode('utf-8')).hexdigest()[:8]

def process_file(filename):
    src_path = os.path.join(SRC_DIR, filename)
    if not os.path.exists(src_path):
        print(f"Skipping {filename}, not found.")
        return

    with open(src_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # 1. 注入 CSS
    head = soup.find('head')
    if head:
        link = soup.new_tag('link', rel='stylesheet', href='css/multilang.css')
        head.append(link)

    # 2. 处理经文
    verses_data = {}
    scripture_divs = soup.find_all('div', class_='scripture')
    
    for div in scripture_divs:
        # 转换为新的容器类名，以便 CSS 匹配
        div['class'] = ['scripture-container']
        
        text_div = div.find('div', class_='scripture-text')
        ref_div = div.find('div', class_='scripture-ref')
        
        if text_div and ref_div:
            cuv_text = text_div.get_text(separator='\n').strip()
            full_ref = ref_div.get_text().strip()
            
            # 提取纯引用 (去除括号和版本名)
            # 假设格式如 (罗马书 1:18 和合本) 或 (马可福音 1:17)
            clean_ref = full_ref.replace('(', '').replace(')', '').replace('和合本', '').strip()
            
            verse_id = generate_verse_id(clean_ref)
            div['data-id'] = verse_id
            
            verses_data[verse_id] = {
                "ref": clean_ref,
                "versions": {
                    "cuv": cuv_text,
                    "ccb": "（当代译本待补充）",
                    "esv": "(ESV translation to be added)"
                }
            }

    # 3. 注入 JS
    body = soup.find('body')
    if body:
        # 注入 bible-version.js
        script_lib = soup.new_tag('script', src='js/bible-version.js')
        body.append(script_lib)
        
        # 注入初始化代码
        page_id = filename.replace('.html', '')
        init_script = soup.new_tag('script')
        init_script.string = f"""
            document.addEventListener('DOMContentLoaded', () => {{
                window.bibleManager.init('{page_id}');
            }});
        """
        body.append(init_script)
        
        # 修改导航链接，确保指向当前目录
        # BeautifulSoup 解析后 href 保持原样，通常是相对路径，所以不需要大改
        # 但如果原链接指向 ../xxx 这种需要注意。这里假设原链接都是同级目录。

    # 4. 保存 HTML
    dst_path = os.path.join(DST_DIR, filename)
    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    # 5. 保存经文数据 JSON
    if verses_data:
        json_path = os.path.join(DATA_DIR, f'{filename.replace(".html", "")}_verses.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(verses_data, f, ensure_ascii=False, indent=2)
            
    print(f"Processed {filename}: {len(verses_data)} verses extracted.")

def main():
    for fname in FILES_TO_PROCESS:
        process_file(fname)

if __name__ == '__main__':
    main()
