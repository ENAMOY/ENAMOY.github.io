#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

DATA_DIR = 'one2one-multilang/data'
DB_FILE = 'one2one-multilang/bible_data/verses_master.json'

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file {DB_FILE} not found.")
        return

    verse_db = load_json(DB_FILE)
    print(f"Loaded {len(verse_db)} verses from master database.")

    # List of files to update
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('_verses.json')]
    
    total_updated = 0

    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        try:
            data = load_json(filepath)
        except json.JSONDecodeError:
            print(f"Skipping {filename}: Invalid JSON")
            continue

        file_updated_count = 0
        
        for key, item in data.items():
            ref = item.get('ref')
            # Normalize ref (strip spaces just in case)
            if ref:
                ref = ref.strip()
            
            if ref and ref in verse_db:
                db_entry = verse_db[ref]
                if 'versions' not in item:
                    item['versions'] = {}
                
                # Update CCB
                if 'ccb' in db_entry:
                    item['versions']['ccb'] = db_entry['ccb']
                
                # Update ESV
                if 'esv' in db_entry:
                    item['versions']['esv'] = db_entry['esv']
                
                file_updated_count += 1
        
        if file_updated_count > 0:
            save_json(filepath, data)
            print(f"Updated {file_updated_count} verses in {filename}")
            total_updated += file_updated_count
        else:
            print(f"No updates for {filename}")

    print(f"Total verses updated: {total_updated}")

if __name__ == '__main__':
    main()
