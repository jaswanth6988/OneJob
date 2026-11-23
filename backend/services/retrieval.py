"""Deterministic passage retrieval for private resume grounding.

No external embedding service or vector database is required. Passages are scoped
by the caller's owned resume. Token-overlap ranking is intentionally inspectable.
"""
import re
from collections import Counter

def retrieve_passages(text: str, query: str, limit: int = 4):
    words = text.split()
    chunks = [' '.join(words[i:i+120]) for i in range(0,len(words),100)]
    tokens = set(re.findall(r'[a-z0-9+#.]{2,}',query.lower()))
    ranked=[]
    for index,chunk in enumerate(chunks):
        counts=Counter(re.findall(r'[a-z0-9+#.]{2,}',chunk.lower()))
        score=sum(min(counts[token],3) for token in tokens)
        if score: ranked.append({'source':f'resume:passage-{index+1}','text':chunk,'relevance':score})
    return sorted(ranked,key=lambda row:(-row['relevance'],row['source']))[:limit]

def grounded_context(text, query):
    passages=retrieve_passages(text,query)
    return '\n\n'.join(f"[{p['source']}] {p['text']}" for p in passages)
