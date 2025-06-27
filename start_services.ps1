Write-Host "🔄 Starting Qdrant via Docker..."
docker run -d --name qdrant-test -p 6333:6333 qdrant/qdrant

Write-Host "🧠 Verifying Ollama is running..."
try {
    $response = Invoke-RestMethod -Uri http://localhost:11434 -Method Get
    Write-Host "✅ Ollama is running."
} catch {
    Write-Host "❌ Ollama is not running. Please open a terminal and run: ollama serve"
    exit 1
}

Write-Host "📦 Pulling required models..."
ollama pull nomic-embed-text
ollama pull deepseek-r1

Write-Host "✅ All services are ready!"
