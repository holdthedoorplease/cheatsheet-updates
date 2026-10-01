#!/usr/bin/env python3
"""
Generates plus-en.html by injecting s# blocks from standard-en.html into plus-source.html.

Usage: python build-plus.py  (run from E-errata/docs/)

Markers in standard-en.html:
  <!-- BEGIN_S_SIDEBAR --> ... <!-- END_S_SIDEBAR -->
  <!-- BEGIN_S_TOC -->     ... <!-- END_S_TOC -->
  <!-- BEGIN_S_ENTRIES --> ... <!-- END_S_ENTRIES -->

plus-source.html has matching empty marker pairs; the script fills them in.

Side effect: auto-updates the "Last updated: YYYY-MM-DD" line in standard-en.html
and plus-source.html to the most recent "Updated: YYYY-MM-DD" date found across
all entries in both files.
"""
import re
from pathlib import Path

MARKER_RE = re.compile(
    r'<!--\s*BEGIN_(\w+)\s*-->(.*?)<!--\s*END_\1\s*-->',
    re.DOTALL
)
ENTRY_DATE_RE = re.compile(r'Updated:\s*(\d{4}-\d{2}-\d{2})')
LAST_UPDATED_RE = re.compile(r'(Last updated:\s*)\d{4}-\d{2}-\d{2}')

def extract_blocks(html):
    return {m.group(1): m.group(2) for m in MARKER_RE.finditer(html)}

def inject_blocks(html, blocks):
    def replacer(m):
        key = m.group(1)
        if key in blocks:
            return f'<!-- BEGIN_{key} -->{blocks[key]}<!-- END_{key} -->'
        return m.group(0)
    return MARKER_RE.sub(replacer, html)

def latest_entry_date(*html_texts):
    dates = []
    for html in html_texts:
        dates.extend(ENTRY_DATE_RE.findall(html))
    return max(dates) if dates else None

def update_last_updated(html, date):
    return LAST_UPDATED_RE.sub(rf'\g<1>{date}', html)

docs = Path(__file__).parent
standard_path = docs / 'en-standard.html'
plus_src_path  = docs / 'en-z-mcq.html'

standard = standard_path.read_text(encoding='utf-8')
plus_src  = plus_src_path.read_text(encoding='utf-8')

latest = latest_entry_date(standard, plus_src)
if latest:
    updated_standard = update_last_updated(standard, latest)
    updated_plus_src  = update_last_updated(plus_src,  latest)
    if updated_standard != standard:
        standard_path.write_text(updated_standard, encoding='utf-8')
        print(f'Updated en-standard.html → Last updated: {latest}')
    if updated_plus_src != plus_src:
        plus_src_path.write_text(updated_plus_src, encoding='utf-8')
        print(f'Updated en-z-mcq.html → Last updated: {latest}')
    standard = updated_standard
    plus_src  = updated_plus_src

blocks = extract_blocks(standard)
result = inject_blocks(plus_src, blocks)

(docs / 'en-plus.html').write_text(result, encoding='utf-8')
print(f'Built en-plus.html ({len(blocks)} blocks: {", ".join(blocks)})')
