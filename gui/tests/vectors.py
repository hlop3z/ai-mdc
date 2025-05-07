import os
import httpx
import chromadb
import fitz  # PyMuPDF
from chromadb.config import Settings

# Constants
DATA_DIR = "./docs"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "tinyllama:latest"

# Initialize Chroma
client = chromadb.Client(Settings(persist_directory="./chroma_data"))
collection = client.get_or_create_collection("file_docs")


def get_embedding(text):
    response = httpx.post(
        "http://localhost:11434/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text, "stream": False},
    )

    data = response.json()

    # Check if 'embedding' exists in response
    if "embedding" not in data or not isinstance(data, dict):
        raise ValueError("Invalid response format from Ollama embedding model.")

    embedding = data.get("embedding")
    if not embedding:
        raise ValueError("Embedding not found in Ollama response.")

    return embedding


def extract_texts(directory):
    """Load and extract text from .txt, .md, .pdf files."""
    texts = []
    text_files = (".txt", ".md")
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if filename.endswith(text_files):
            with open(path, "r", encoding="utf-8") as f:
                texts.append((filename, f.read()))
        elif filename.endswith(".pdf"):
            doc = fitz.open(path)
            pdf_text = "\n".join(page.get_text() for page in doc)
            texts.append((filename, pdf_text))
    return texts


def ingest_documents(directory):
    """Ingest and index documents from the directory into Chroma."""
    documents = extract_texts(directory)
    chunk_size = 512
    for name, content in documents:
        chunks = [
            content[i : i + chunk_size] for i in range(0, len(content), chunk_size)
        ]
        for i, chunk in enumerate(chunks):
            emb = get_embedding(chunk)
            doc_id = f"{name}-{i}"
            collection.add(documents=[chunk], embeddings=[emb], ids=[doc_id])
    print("Ingestion complete.")


# Ingest once at start
ingest_documents(DATA_DIR)


# Chat loop
while True:
    query = input("\nYou: ")
    emb = get_embedding(query)
    results = collection.query(query_embeddings=[emb], n_results=3)

    context_docs = results["documents"][0]
    print(context_docs)
    context = "\n---\n".join(context_docs)
    prompt = f"""You are an assistant answering based on the provided context.
Context:
{context}

User: {query}
Assistant:"""

    res = httpx.post(
        "http://localhost:11434/api/generate",
        json={"model": CHAT_MODEL, "prompt": prompt, "stream": False},
        timeout=60.0,
    )

    print("Bot:", res.json().get("response"))
