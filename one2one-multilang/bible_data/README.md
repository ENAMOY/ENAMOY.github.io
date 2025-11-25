# Bible Data

This directory contains the Bible verse database for the One2One project.

## Files

- `verses_master.json`: The central database containing all verses used in the course.
  - Format: `{"Book Chapter:Verse": {"cuv": "...", "ccb": "...", "esv": "..."}}`

## How to Update

1. **Edit `verses_master.json`**: You can manually correct or add verses here.
2. **Run Update Script**: Run `python3 one2one-multilang/update_course_from_db.py` to propagate changes to the course data files (`data/chapter_*.json`).

## Adding Full Bibles

If you obtain full Bible JSON files (e.g., `ccb_full.json`), you can place them here and modify the update script to query them.
