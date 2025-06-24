import httpx
from typing import List
from app.embedder import qdrant, COLLECTION_NAME, embed_text_ollama

def retrieve_context(query: str, top_k: int = 5) -> List[str]:
    """
    Embeds the user's query using Ollama and searches Qdrant for top-k matches.
    """
    query_vector = embed_text_ollama([query])
    if not query_vector:
        return ["[Error embedding query]"]

    search_results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector[0],
        limit=top_k
    )

    return [hit.payload["text"] for hit in search_results]
