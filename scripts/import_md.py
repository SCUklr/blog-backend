#!/usr/bin/env python3
"""
Import markdown posts from the frontend `src/posts` into the running FastAPI backend.
Features:
 - YAML front-matter parsing (uses PyYAML)
 - --dry-run mode
 - --dedupe: will query existing posts and skip by title

Usage:
  python scripts/import_md.py [--dry-run] [--dedupe]

It expects the frontend posts to be at ../scuklr.github.io/src/posts
and the backend API base at http://localhost:8000/api (override with IMPORT_API_BASE)
"""
import os
import argparse
from pathlib import Path
import requests
import yaml

ROOT = Path(__file__).resolve().parents[2]  # server/ -> project root
FRONTEND_POSTS = ROOT / 'scuklr.github.io' / 'src' / 'posts'
API_BASE = os.environ.get('IMPORT_API_BASE', 'http://localhost:8000/api')

def find_md_files():
    if not FRONTEND_POSTS.exists():
        print(f"Posts folder not found: {FRONTEND_POSTS}")
        return []
    md_files = list(FRONTEND_POSTS.rglob('*.md'))
    md_files = [p for p in md_files if p.name.lower() != 'readme.md']
    return md_files

def parse_front_matter(text):
    # split YAML front-matter delimited by ---
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2].lstrip('\n')
            try:
                data = yaml.safe_load(fm_text) or {}
            except Exception as e:
                print('YAML parse error:', e)
                data = {}
            return data, body
    return {}, text

def normalize_tags(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v]
    if isinstance(v, str):
        return [t.strip() for t in v.split(',') if t.strip()]
    return []

def get_existing_titles():
    try:
        r = requests.get(f"{API_BASE}/posts", timeout=10)
        if r.status_code == 200:
            return set([str(x.get('title')).strip() for x in r.json() if x.get('title')])
    except Exception as e:
        print('Warning: failed to fetch existing posts:', e)
    return set()

def main(dry_run=False, dedupe=False):
    files = find_md_files()
    if not files:
        print('No markdown files found to import.')
        return 0

    existing = set()
    if dedupe:
        existing = get_existing_titles()

    success = 0
    fail = 0
    for p in files:
        try:
            text = p.read_text(encoding='utf-8')
            fm, body = parse_front_matter(text)
            title = (fm.get('title') or p.stem).strip()
            description = fm.get('description') or fm.get('desc') or ''
            tags = normalize_tags(fm.get('tags'))

            if dedupe and title in existing:
                print(f"SKIP (exists): {title}")
                continue

            payload = {
                'title': title,
                'content': body,
                'description': description,
                'tags': tags
            }
            print(f"Posting {p} -> {payload['title']} (tags: {tags})")
            if dry_run:
                print('  dry-run: not posting')
                success += 1
                continue

            r = requests.post(f"{API_BASE}/posts", json=payload, timeout=10)
            if r.status_code in (200,201):
                print('  OK')
                success += 1
            else:
                print('  FAILED', r.status_code, r.text)
                fail += 1
        except Exception as e:
            print('Error processing', p, e)
            fail += 1

    print(f"Done. success={success}, fail={fail}")
    return 0 if fail == 0 else 2

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Do not POST, only parse and show')
    parser.add_argument('--dedupe', action='store_true', help='Query existing posts and skip by title')
    args = parser.parse_args()
    raise SystemExit(main(dry_run=args.dry_run, dedupe=args.dedupe))
