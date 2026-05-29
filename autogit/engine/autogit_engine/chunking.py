from __future__ import annotations
def chunk_args(items,max_chars=6500):
    chunks=[]; cur=[]; size=0
    for item in items:
        n=len(item)+4
        if cur and size+n>max_chars: chunks.append(cur); cur=[]; size=0
        cur.append(item); size+=n
    if cur: chunks.append(cur)
    return chunks
