# app/retriever_async.py

import asyncio
from typing import List, Dict
from app.embedder_async import embed_text_ollama_async, qdrant, COLLECTION_NAME

async def retrieve_context(query: str, top_k: int = 5) -> List[Dict[str, str]]:
    """
    Embeds the user's query using Ollama and retrieves top-k matching chunks from Qdrant.

    Returns: List of dicts with 'text' and 'section'.
    """
    vector = await embed_text_ollama_async(query)  # ✅ pass string, not list
    if not vector:
        return [{"section": "ERROR", "text": "[Error embedding query]"}]

    search_results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=top_k
    )

    return [
        {
            "section": hit.payload.get("section", "Unknown Section"),
            "text": hit.payload.get("text", "")
        }
        for hit in search_results
    ]
