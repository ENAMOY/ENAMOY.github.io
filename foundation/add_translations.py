#!/usr/bin/env python3
"""
Stage 1: Add CCB/CSB/ESV translation data to all adult foundation answer JSONs.
Stage 2: Inject translation UI and JS into all lesson HTML files.
"""
import json, glob, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ANSWERS_DIR = os.path.join(BASE_DIR, "data", "answers")

# Book abbreviation -> eng code for ebible.app
BOOK_TO_CODE = {
    '创': 'gen', '出': 'exo', '利': 'lev', '民': 'num', '申': 'deu',
    '书': 'jos', '士': 'jdg', '得': 'rut', '撒上': '1sa', '撒下': '2sa',
    '王上': '1ki', '王下': '2ki', '代上': '1ch', '代下': '2ch',
    '拉': 'ezr', '尼': 'neh', '斯': 'est', '伯': 'job',
    '诗': 'psa', '箴': 'pro', '传': 'ecc', '歌': 'sng',
    '赛': 'isa', '耶': 'jer', '哀': 'lam', '结': 'ezk', '但': 'dan',
    '何': 'hos', '珥': 'jol', '摩': 'amo', '俄': 'oba', '拿': 'jon',
    '弥': 'mic', '鸿': 'nam', '哈': 'hab', '番': 'zep', '该': 'hag', '亚': 'zec', '玛': 'mal',
    '太': 'mat', '可': 'mrk', '路': 'luk', '约': 'jhn',
    '徒': 'act', '罗': 'rom', '林前': '1co', '林后': '2co',
    '加': 'gal', '弗': 'eph', '腓': 'php', '西': 'col',
    '帖前': '1th', '帖后': '2th', '提前': '1ti', '提后': '2ti', '多': 'tit', '门': 'phm',
    '来': 'heb', '雅': 'jas', '彼前': '1pe', '彼后': '2pe',
    '约一': '1jn', '约二': '2jn', '约三': '3jn', '犹': 'jud', '启': 'rev',
    '约壹': '1jn',  # Alternate
}

# Full Chinese name -> abbrev
FULL_TO_ABBREV = {
    '创世记': '创', '出埃及记': '出', '利未记': '利', '民数记': '民', '申命记': '申',
    '约书亚记': '书', '士师记': '士', '路得记': '得', '撒母耳记上': '撒上', '撒母耳记下': '撒下',
    '列王纪上': '王上', '列王纪下': '王下', '历代志上': '代上', '历代志下': '代下',
    '以斯拉记': '拉', '尼希米记': '尼', '以斯帖记': '斯', '约伯记': '伯',
    '诗篇': '诗', '箴言': '箴', '传道书': '传', '雅歌': '歌',
    '以赛亚书': '赛', '耶利米书': '耶', '耶利米哀歌': '哀', '以西结书': '结', '但以理书': '但',
    '何西阿书': '何', '约珥书': '珥', '阿摩司书': '摩', '俄巴底亚书': '俄', '约拿书': '拿',
    '弥迦书': '弥', '那鸿书': '鸿', '哈巴谷书': '哈', '西番雅书': '番', '哈该书': '该', '撒迦利亚书': '亚', '玛拉基书': '玛',
    '马太福音': '太', '马可福音': '可', '路加福音': '路', '约翰福音': '约',
    '使徒行传': '徒', '罗马书': '罗', '哥林多前书': '林前', '哥林多后书': '林后',
    '加拉太书': '加', '以弗所书': '弗', '腓立比书': '腓', '歌罗西书': '西',
    '帖撒罗尼迦前书': '帖前', '帖撒罗尼迦后书': '帖后',
    '提摩太前书': '提前', '提摩太后书': '提后', '提多书': '多', '腓利门书': '门',
    '希伯来书': '来', '雅各书': '雅', '彼得前书': '彼前', '彼得后书': '彼后',
    '约翰一书': '约一', '约翰二书': '约二', '约翰三书': '约三', '犹大书': '犹', '启示录': '启',
    '历代志下': '代下', '约翰壹书': '约一',
}

def normalize_ref(ref):
    """Normalize a reference to abbreviated format for ebible.app lookup."""
    ref = ref.strip()
    # Remove "请阅读" / "阅读" prefix
    ref = re.sub(r'^(请)?阅读\s*', '', ref)
    # Replace full names with abbreviations
    for full, abbrev in sorted(FULL_TO_ABBREV.items(), key=lambda x: -len(x[0])):
        if ref.startswith(full):
            ref = abbrev + ref[len(full):]
            break
    # Handle comma notation: "创 2:16,17" -> "创 2:16-17"
    ref = re.sub(r':(\d+),(\d+)', r':\1-\2', ref)
    return ref

def parse_ref_for_fetch(ref):
    """Parse normalized ref into (book_code, ch, v1, v2) for ebible.app URL."""
    m = re.match(r'(.+?)\s+(\d+):(\d+)(?:-(\d+))?$', ref)
    if not m:
        return None
    book = m.group(1)
    ch = int(m.group(2))
    v1 = int(m.group(3))
    v2 = int(m.group(4)) if m.group(4) else v1
    book_code = BOOK_TO_CODE.get(book)
    if not book_code:
        return None
    return book_code, ch, v1, v2

def fetch_single_verse(book_code, ch, v, trans_code):
    """Fetch one verse from ebible.app, return text."""
    url = f"https://wx2.ebible.app/verse/{book_code}.{ch}.{v}.{trans_code}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            title_m = re.search(r'<title>(.*?)</title>', html)
            if title_m:
                title = title_m.group(1)
                title = re.sub(r'\s*\|\s*[^|]*$', '', title).strip()
                parts = title.split(' ', 2)
                if len(parts) >= 3:
                    return parts[2]
    except:
        pass
    return None

def fetch_passage(book_code, ch, v1, v2, trans_code):
    """Fetch all verses in a passage."""
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(fetch_single_verse, book_code, ch, v, trans_code): v for v in range(v1, v2 + 1)}
        results = {}
        for f in as_completed(futures):
            r = f.result()
            if r: results[futures[f]] = r
    if len(results) != (v2 - v1 + 1):
        return None
    return ''.join(results[v] for v in range(v1, v2 + 1))

def fetch_translation(norm_ref, trans_code):
    """Fetch full passage text for a given reference."""
    parsed = parse_ref_for_fetch(norm_ref)
    if not parsed:
        return None
    book_code, ch, v1, v2 = parsed
    return fetch_passage(book_code, ch, v1, v2, trans_code)

# ====== STAGE 1: Build translation data ======
print("=" * 60)
print("STAGE 1: Building translation data")
print("=" * 60)

# Load kids data as base
kids_answers = {}
kids_dir = "/Users/andyshengruilee/Downloads/AI协同工作区/真道之工/建立根基_Kids课程讲义/kids-foundation/data/answers"
for fpath in sorted(glob.glob(os.path.join(kids_dir, "kids_L*.json"))):
    data = json.load(open(fpath, encoding='utf-8'))
    for key, entry in data.get("answers", {}).items():
        ref = entry.get("reference", "")
        if ref:
            kids_answers[ref] = {
                'ccb': entry.get('ccb', ''),
                'csb': entry.get('csb', ''),
                'esv': entry.get('esv', ''),
                'has_ccb': entry.get('has_ccb', False),
                'has_csb': entry.get('has_csb', False),
                'has_esv': entry.get('has_esv', False),
            }

# Collect all unique refs from adult course + their normalized forms
adult_refs_info = {}  # original_ref -> normalized_ref
for fpath in sorted(glob.glob(os.path.join(ANSWERS_DIR, "foundation_L*.json"))):
    try:
        data = json.load(open(fpath, encoding='utf-8'))
        for key, entry in data.get("answers", {}).items():
            ref = entry.get("reference", "")
            if ref and ref not in adult_refs_info:
                adult_refs_info[ref] = normalize_ref(ref)
    except:
        pass

print(f"Total unique adult refs: {len(adult_refs_info)}")

# Build translation lookup: normalized_ref -> {ccb, csb, esv}
translations = {}

# First, check overlap with kids
from_kids = 0
for orig_ref, norm_ref in adult_refs_info.items():
    if orig_ref in kids_answers:
        k = kids_answers[orig_ref]
        if k['has_ccb'] or k['has_csb'] or k['has_esv']:
            translations[norm_ref] = {'ccb': k['ccb'], 'csb': k['csb'], 'esv': k['esv'],
                                       'has_ccb': k['has_ccb'], 'has_csb': k['has_csb'], 'has_esv': k['has_esv']}
            from_kids += 1

print(f"Covered from Kids data: {from_kids} refs")

# Find refs needing CCB, CSB, ESV
needs_ccb = set()
needs_csb = set()
needs_esv = set()
for orig_ref, norm_ref in adult_refs_info.items():
    if norm_ref not in translations:
        needs_ccb.add(norm_ref)
        needs_csb.add(norm_ref)
        needs_esv.add(norm_ref)
    else:
        t = translations[norm_ref]
        if not t['has_ccb']: needs_ccb.add(norm_ref)
        if not t['has_csb']: needs_csb.add(norm_ref)
        if not t['has_esv']: needs_esv.add(norm_ref)

print(f"Need CCB: {len(needs_ccb)}, CSB: {len(needs_csb)}, ESV: {len(needs_esv)}")

# Fetch all needed translations
all_to_fetch = []
for ref in needs_ccb: all_to_fetch.append((ref, 'ccbs'))
for ref in needs_csb: all_to_fetch.append((ref, 'csbs'))
for ref in needs_esv: all_to_fetch.append((ref, 'esv'))

print(f"Total verse fetches: {len(all_to_fetch)}")

# Do batch fetches
fetch_results = {}
batch_size = 15
for batch_start in range(0, len(all_to_fetch), batch_size):
    batch = all_to_fetch[batch_start:batch_start+batch_size]
    with ThreadPoolExecutor(max_workers=15) as ex:
        futures = {}
        for ref, trans_code in batch:
            parsed = parse_ref_for_fetch(ref)
            if parsed:
                book_code, ch, v1, v2 = parsed
                # Fetch all verses in range
                for v in range(v1, v2 + 1):
                    f = ex.submit(fetch_single_verse, book_code, ch, v, trans_code)
                    futures[f] = (ref, trans_code, v, v1, v2)

        # Collect results
        passage_verses = {}  # (ref, trans_code) -> {verse_num: text}
        for f in as_completed(futures):
            ref, trans_code, v, v1, v2 = futures[f]
            text = f.result()
            key = (ref, trans_code)
            if key not in passage_verses:
                passage_verses[key] = {}
            if text:
                passage_verses[key][v] = text

        # Assemble passages
        for (ref, trans_code), verses in passage_verses.items():
            parsed = parse_ref_for_fetch(ref)
            if parsed:
                _, _, v1, v2 = parsed
                if len(verses) == (v2 - v1 + 1):
                    full_text = ''.join(verses[v] for v in range(v1, v2 + 1))
                    fetch_results[(ref, trans_code)] = full_text

    done = min(batch_start + batch_size, len(all_to_fetch))
    print(f"  Fetch progress: {done}/{len(all_to_fetch)}", flush=True)
    time.sleep(0.3)

# Build final translations dict
for ref, trans_code, text in [(r, tc, t) for (r, tc), t in fetch_results.items()]:
    if ref not in translations:
        translations[ref] = {'ccb': '', 'csb': '', 'esv': '', 'has_ccb': False, 'has_csb': False, 'has_esv': False}
    if trans_code == 'ccbs':
        translations[ref]['ccb'] = text
        translations[ref]['has_ccb'] = True
    elif trans_code == 'csbs':
        translations[ref]['csb'] = text
        translations[ref]['has_csb'] = True
    elif trans_code == 'esv':
        translations[ref]['esv'] = text
        translations[ref]['has_esv'] = True

# Apply to all answer JSONs
updated_jsons = 0
for fpath in sorted(glob.glob(os.path.join(ANSWERS_DIR, "foundation_L*.json"))):
    try:
        data = json.load(open(fpath, encoding='utf-8'))
        modified = False
        for key, entry in data.get("answers", {}).items():
            ref = entry.get("reference", "")
            if not ref: continue
            norm_ref = normalize_ref(ref)
            if norm_ref in translations:
                t = translations[norm_ref]
                if t['has_ccb'] and (not entry.get('has_ccb') or not entry.get('ccb', '').strip()):
                    entry['ccb'] = t['ccb']
                    entry['has_ccb'] = True
                    modified = True
                if t['has_csb'] and (not entry.get('has_csb') or not entry.get('csb', '').strip()):
                    entry['csb'] = t['csb']
                    entry['has_csb'] = True
                    modified = True
                if t['has_esv'] and (not entry.get('has_esv') or not entry.get('esv', '').strip()):
                    entry['esv'] = t['esv']
                    entry['has_esv'] = True
                    modified = True
        if modified:
            json.dump(data, open(fpath, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
            updated_jsons += 1
    except Exception as e:
        print(f"  Error processing {fpath}: {e}")

print(f"\nUpdated {updated_jsons} JSON files.")

# Count final stats
total, ccb, csb, esv = 0, 0, 0, 0
for fpath in sorted(glob.glob(os.path.join(ANSWERS_DIR, "foundation_L*.json"))):
    try:
        data = json.load(open(fpath, encoding='utf-8'))
        for key, entry in data.get("answers", {}).items():
            total += 1
            if entry.get('has_ccb') and entry.get('ccb','').strip(): ccb += 1
            if entry.get('has_csb') and entry.get('csb','').strip(): csb += 1
            if entry.get('has_esv') and entry.get('esv','').strip(): esv += 1
    except: pass

print(f"Final: total={total} | CCB={ccb}/{total} ({ccb*100//total}%) | CSB={csb}/{total} ({csb*100//total}%) | ESV={esv}/{total} ({esv*100//total}%)")

# Save stats for Stage 2
with open('/tmp/adult_translation_stats.json', 'w') as f:
    json.dump({'total': total, 'ccb': ccb, 'csb': csb, 'esv': esv}, f)

print("\nStage 1 complete. Translation data ready.")
