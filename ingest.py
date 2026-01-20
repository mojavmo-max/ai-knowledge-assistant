import pdfplumber
from pathlib import Path
import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
from pathlib import Path
import faiss

load_dotenv()
client = OpenAI()

DATA_DIR = Path("data")
DOCS_DIR = DATA_DIR / "docs"
INDEX_PATH = DATA_DIR / "faiss.index"
CHUNKS_PATH = DATA_DIR / "chunks.txt"

def load_pdf(path:Path) -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    
    return text

def load_chunks():
    if not CHUNKS_PATH.exists():
        return []
    
    return CHUNKS_PATH.read_text(encoding="utf-8").split("\n\n---\n")


def chunk_text(text, size = 500, overlap = 100):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start+size])
        start += (size-overlap)

    return chunks

def embed_chunks(chunks):
    embeddings = []

    for chunk in chunks:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunk
        )
        embeddings.append(response.data[0].embedding)

    embeddings = np.array(embeddings).astype("float32")

    if INDEX_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))
    else:
        index = faiss.IndexFlatL2(embeddings.shape[1])

    index.add(embeddings)
    faiss.write_index(index, str(INDEX_PATH))

    existing_chunks = load_chunks()
    all_chunks = existing_chunks + chunks

    CHUNKS_PATH.write_text(
        "\n\n---\n".join(all_chunks),
        encoding="utf-8"
    )

