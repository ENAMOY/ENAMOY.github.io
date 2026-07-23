import json

with open('one2one-multilang/bible_data/verses_master.json', 'r') as f:
    data = json.load(f)

for ref, versions in data.items():
    cuv = versions.get('cuv', '').strip()
    ccb = versions.get('ccb', '').strip()
    
    if cuv and ccb and cuv == ccb:
        print(f"Identical: {ref}")
        print(f"CUV: {cuv}")
