# app/embedder_async.py

import os
import hashlib
import asyncio
import httpx
from typing import List, Dict
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

# Load environment variables
load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
EMBED_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/embeddings"  # ✅ Correct endpoint

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "tenk_chunks")

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def init_collection():
    if COLLECTION_NAME not in [c.name for c in qdrant.get_collections().collections]:
        qdrant.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )

async def embed_text_ollama_async(text: str) -> List[float]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                EMBED_URL,
                json={"model": OLLAMA_EMBED_MODEL, "prompt": text}
            )
            response.raise_for_status()
            return response.json()["embedding"]  # ✅ Correct key: "embedding"
        except Exception as e:
            print(f"❌ Async embedding error: {e}")
            return []

async def embed_and_store_async(chunks: List[Dict[str, str]]):
    """
    Asynchronously embeds and stores chunks in Qdrant.

    Each chunk should have 'text' and 'section' keys.
    """
    init_collection()

    valid_chunks = []
    for chunk in chunks:
        text = chunk.get("text", "").strip()
        word_count = len(text.split())
        if word_count == 0:
            print("⏭️ Skipping empty chunk.")
            continue
        if word_count > 1000:
            print(f"⏭️ Skipping overly long chunk ({word_count} words).")
            continue
        valid_chunks.append(chunk)

    if not valid_chunks:
        print("⚠️ No valid chunks to embed.")
        return

    points = []

    for chunk in valid_chunks:
        text = chunk["text"]
        section = chunk.get("section", "Unknown Section")

        vector = await embed_text_ollama_async(text)
        if not vector:
            print("⚠️ Failed to embed a chunk. Skipping.")
            continue

        point_id = int(hashlib.sha256(text.encode()).hexdigest(), 16) % (10**16)
        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "text": text,
                    "section": section
                }
            )
        )

    if points:
        qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"✅ Stored {len(points)} chunks in Qdrant (async).")
    else:
        print("❌ No vectors stored. All embeddings may have failed.")
