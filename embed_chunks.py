import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
from pathlib import Path
import faiss

load_dotenv()
client = OpenAI()

CHUNKS_PATH = Path("data/chunks.txt")
chunks = CHUNKS_PATH.read_text(encoding="utf-8").split("\n\n---\n")

embeddings = []
for chunk in chunks:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunk
    )
    embeddings.append(response.data[0].embedding)

embeddings = np.array(embeddings).astype("float32")

dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(embeddings)

faiss.write_index(index, "data/faiss.index")

'''testing'''

query = "What is this document about?"
query_embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input = query
).data[0].embedding

query_vec = np.array([query_embedding]).astype("float32")
D, I = index.search(query_vec, k=3)

print(I, D)
for i in I[0]:
    print(chunks[i][:300])