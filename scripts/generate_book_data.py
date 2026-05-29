
import os
import json
import re
from bs4 import BeautifulSoup

# Directory containing the HTML files
romans_dir = 'RomansAndy'
output_file = os.path.join(romans_dir, 'book_data.json')

book_data = []

# Helper to sort chapters numerically
def get_chapter_number(filename):
    if filename == 'preface.html':
        return 0
    match = re.search(r'chapter_(\d+)\.html', filename)
    if match:
        return int(match.group(1))
    return 9999

# Get all HTML files
files = [f for f in os.listdir(romans_dir) if f.endswith('.html') and (f.startswith('chapter_') or f == 'preface.html')]
files.sort(key=get_chapter_number)

for filename in files:
    file_path = os.path.join(romans_dir, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        
        title = soup.find('h1').get_text().strip() if soup.find('h1') else "Untitled"
        
        # Extract text content for search
        content_wrapper = soup.find('div', class_='content-wrapper')
        text_content = ""
        if content_wrapper:
            # Remove nav and home-link before extracting text
            for div in content_wrapper.find_all('div', class_=['nav', 'home-link']):
                div.decompose()
            text_content = content_wrapper.get_text(separator=' ', strip=True)
        
        # Get navigation links
        prev_link = ""
        next_link = ""
        nav_div = soup.find('div', class_='nav') # Note: In the file read, it was just class="nav" but let's check if soup finds it.
        # Actually in the file read: <div class="nav">
        
        # Re-read file to get nav links properly because I decomposed them above
        # Or just parse soup before decomposing.
        # Let's re-parse for nav to be safe.
    
    with open(file_path, 'r', encoding='utf-8') as f:
        soup_nav = BeautifulSoup(f, 'html.parser')
        nav_div = soup_nav.find('div', class_='nav')
        if nav_div:
            links = nav_div.find_all('a')
            for link in links:
                if '上一章' in link.text:
                    prev_link = link.get('href')
                elif '下一章' in link.text:
                    next_link = link.get('href')

    book_data.append({
        'id': filename,
        'title': title,
        'content': text_content,
        'prev': prev_link,
        'next': next_link
    })

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(book_data, f, ensure_ascii=False, indent=2)

print(f"Generated book_data.json with {len(book_data)} chapters.")
