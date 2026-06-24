#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

DATA_DIR = 'one2one-multilang/data'
DB_FILE = 'one2one-multilang/bible_data/verses_master.json'

def load_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    verse_db = load_json(DB_FILE)
    print(f"Initial DB size: {len(verse_db)}")

    files = [f for f in os.listdir(DATA_DIR) if f.endswith('_verses.json')]
    
    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        try:
            data = load_json(filepath)
        except:
            continue
            
        for key, item in data.items():
            ref = item.get('ref')
            versions = item.get('versions', {})
            
            if ref and versions:
                ref = ref.strip()
                if ref not in verse_db:
                    verse_db[ref] = {}
                
                # Merge versions
                if 'ccb' in versions:
                    verse_db[ref]['ccb'] = versions['ccb']
                if 'esv' in versions:
                    verse_db[ref]['esv'] = versions['esv']
                # We can also store CUV if we want the DB to be complete
                if 'cuv' in versions:
                    verse_db[ref]['cuv'] = versions['cuv']

    save_json(DB_FILE, verse_db)
    print(f"Final DB size: {len(verse_db)}")

if __name__ == '__main__':
    main()
