import os
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from app.parser import parse_pdf_sections
from app.embedder_async import embed_and_store_async
from app.retriever_async import retrieve_context
import ollama
from dotenv import load_dotenv

load_dotenv()

OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "deepseek-r1")

app = FastAPI()

# CORS (for Streamlit local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    chunks = parse_pdf_sections(pdf_bytes)  # section-aware
    await embed_and_store_async(chunks)
    return {"message": f"Stored {len(chunks)} chunks from {file.filename}"}


@app.get("/ask")
@app.get("/ask")
async def ask_question(query: str = Query(...), top_k: int = 5):
    results = await retrieve_context(query, top_k=top_k)

    context_blocks = [
        f"Section: {r['section']}\nContent: {r['text']}" for r in results
    ]
    context_str = "\n\n".join(context_blocks)
    prompt = f"""Use only the context below to answer the question.

Context:
{context_str}

Question: {query}

Answer:"""

    try:
        response = ollama.chat(
            model= OLLAMA_CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response["message"]["content"]
    except Exception as e:
        answer = f"[Error from Ollama]: {e}"

    return {
        "answer": answer,
        "context_used": context_blocks
    }