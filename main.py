# main.py
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from app.parser import parse_pdf
from app.embedder import embed_and_store
from app.retriever import retrieve_context
from app.ollama_client import query_ollama

app = FastAPI(title="10-K AI Research Assistant")

# Optional CORS setup if you're using a frontend like Streamlit or React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts a PDF file, parses it into chunks, and stores embeddings in Qdrant.
    """
    content = await file.read()
    chunks = parse_pdf(content)
    embed_and_store(chunks)
    return {"message": f"✅ Uploaded and embedded {len(chunks)} chunks."}

@app.get("/ask")
def ask_question(query: str = Query(..., description="Your natural language question")):
    """
    Accepts a question, retrieves similar chunks, and queries the LLM with context.
    """
    context_chunks = retrieve_context(query)
    answer = query_ollama(query, context_chunks)
    return {
        "question": query,
        "answer": answer,
        "context_used": context_chunks  # Optional: useful for debugging or display
    }
