import cohere
import os
from typing import List, Dict


RERANK_MODEL = "rerank-multilingual-v3.0"
RERANK_API_KEY: str = os.environ.get("RERANK_API_KEY")
RERANK_THRESHOLD = float(os.environ.get("RERANK_THRESHOLD"))

co = cohere.Client(RERANK_API_KEY)

def rerank_chunks(
    query: str,
    chunks_list: List[Dict],
    threshold: float = RERANK_THRESHOLD,
    max_docs: int = 5,
):
    responses = co.rerank(
        model=RERANK_MODEL,
        query=query,
        documents=chunks_list,
        top_n=max_docs
    )
    results = []


    for r in responses.results:
        if r.relevance_score > threshold:
            results.append(r.document)
    return results[:max_docs]
