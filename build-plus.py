#!/usr/bin/env python3
"""
Generates plus-en.html by injecting s# blocks from standard-en.html into plus-source.html.

Usage: python build-plus.py  (run from E-errata/docs/)

Markers in standard-en.html:
  <!-- BEGIN_S_SIDEBAR --> ... <!-- END_S_SIDEBAR -->
  <!-- BEGIN_S_TOC -->     ... <!-- END_S_TOC -->
  <!-- BEGIN_S_ENTRIES --> ... <!-- END_S_ENTRIES -->

plus-source.html has matching empty marker pairs; the script fills them in.
"""
import re
from pathlib import Path

MARKER_RE = re.compile(
    r'<!--\s*BEGIN_(\w+)\s*-->(.*?)<!--\s*END_\1\s*-->',
    re.DOTALL
)

def extract_blocks(html):
    return {m.group(1): m.group(2) for m in MARKER_RE.finditer(html)}

def inject_blocks(html, blocks):
    def replacer(m):
        key = m.group(1)
        if key in blocks:
            return f'<!-- BEGIN_{key} -->{blocks[key]}<!-- END_{key} -->'
        return m.group(0)
    return MARKER_RE.sub(replacer, html)

docs = Path(__file__).parent
standard = (docs / 'standard-en.html').read_text(encoding='utf-8')
plus_src = (docs / 'plus-source.html').read_text(encoding='utf-8')

blocks = extract_blocks(standard)
result = inject_blocks(plus_src, blocks)

(docs / 'plus-en.html').write_text(result, encoding='utf-8')
print(f'Built plus-en.html ({len(blocks)} blocks: {", ".join(blocks)})')
