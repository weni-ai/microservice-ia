import cohere
import os
from typing import List, Dict


RERANK_MODEL = os.environ.get("RERANK_MODEL")
RERANK_API_KEY: str = os.environ.get("RERANK_API_KEY")
RERANK_THRESHOLD = float(os.environ.get("RERANK_THRESHOLD"))


def rerank_chunks(
    query: str,
    chunks_list: List[Dict],
    threshold: float = RERANK_THRESHOLD,
    max_docs: int = 5,
):
    if chunks_list:
        print("[+  Rerank Chunks +]")
        co = cohere.Client(RERANK_API_KEY)
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
    return chunks_list
