import hashlib
import httpx
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

# Configuration
OLLAMA_EMBED_MODEL = "deepseek-embed"  # Or another local Ollama embedding model
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "tenk_chunks"

# Connect to Qdrant
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def init_collection():
    """
    Create the collection in Qdrant if it doesn't exist.
    Adjust 'size' if your embedding vector size differs.
    """
    if COLLECTION_NAME not in [c.name for c in qdrant.get_collections().collections]:
        qdrant.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )
        print(f"✅ Created Qdrant collection: {COLLECTION_NAME}")

def embed_text_ollama(texts: List[str]) -> List[List[float]]:
    """
    Use Ollama to generate embeddings from a list of text chunks.
    """
    try:
        response = httpx.post(
            "http://localhost:11434/v1/embeddings",
            json={"model": OLLAMA_EMBED_MODEL, "prompt": texts}
        )
        response.raise_for_status()
        data = response.json()
        return data["embeddings"]
    except Exception as e:
        print(f"❌ Ollama embedding error: {e}")
        return []

def embed_and_store(chunks: List[str]):
    """
    Embeds the provided text chunks using Ollama and stores them in Qdrant.
    """
    init_collection()
    vectors = embed_text_ollama(chunks)

    if not vectors:
        print("❌ No vectors returned. Aborting upsert.")
        return

    points = []
    for chunk, vector in zip(chunks, vectors):
        point_id = int(hashlib.sha256(chunk.encode()).hexdigest(), 16) % (10**16)
        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload={"text": chunk}
            )
        )

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Stored {len(points)} chunks in Qdrant.")
