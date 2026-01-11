import faiss
import numpy as np
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

index = faiss.read_index("data/faiss.index")

chunks = Path("data/chunks.txt").read_text(
    encoding="utf-8"
).split("\n\n---\n")

def embed_text(text):
    return client.embeddings.create(
        model = "text-embedding-3-small",
        input = text
    ).data[0].embedding

def retrieve(query, k=3):
    query_vec = np.array([embed_text(query)]).astype("float32")
    distances, indices = index.search(query_vec, k)
    return [chunks[i] for i in indices[0]]

query = "what is the main topic of the document?"
results = retrieve(query)