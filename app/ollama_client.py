import httpx
from typing import List

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "deepseek-r1"

def format_prompt(query: str, context_chunks: List[str]) -> str:
    context = "\n\n".join(context_chunks)
    return f"""You are a financial analyst AI. Given the context from a 10-K filing, answer the question concisely.

Context:
{context}

Question: {query}

Answer:"""

def query_ollama(query: str, context_chunks: List[str]) -> str:
    prompt = format_prompt(query, context_chunks)
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = httpx.post(f"{OLLAMA_URL}/api/generate", json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "[No response from model]")
    except Exception as e:
        return f"[Error querying Ollama]: {str(e)}"
