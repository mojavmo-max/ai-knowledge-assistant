from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
import json
from vision.vision import run_vision
from vision.ocr import run_ocr

load_dotenv()
client = OpenAI()

DATA_PATH = "db.txt"

def create_chunks(text, size=500, overlap=50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap

    with open("chunks.txt", "w", encoding="utf-8") as f:
        f.write("\n\n---\n".join(chunks))

    return chunks  

def create_embeddings(chunks):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input = chunks
    )

    embeddings = [e.embedding for e in res.data]

    with open("embeddings.json", "w") as f:
        json.dump(embeddings, f)

    return embeddings

def load_embeddings():
    with open("embeddings.json") as f:
        embeddings = json.load(f)
    
    return embeddings

def load_chunks():
    with open("chunks.txt", "r", encoding="utf-8") as f:
        chunks = f.read()
    
    return chunks

def search(query_embedding, embeddings, chunks, top_k=3):
    scores = []

    for i, emb in enumerate(embeddings):
        score = np.dot(query_embedding, emb)
        scores.append((score, chunks[i]))

    scores.sort(reverse=True)

    return [c for _, c in scores[:top_k]]

def extract_text(image_path):
    ocr_text = run_ocr(image_path)

    if len(ocr_text) < 200:
        return run_vision(image_path)

    return ocr_text

def process_document(doc_id, text):
    chunks = create_chunks(text)

    embeddings = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )

    doc_data = {
        "chunks": chunks,
        "embeddings": [e.embedding for e in embeddings.data],
        "metadata": extract_invoice_fields(text)
    }

    save_document(doc_id, doc_data)
    return doc_data["metadata"]

def extract_invoice_fields(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extact invoice fields. Return json ONLY. No additonal text. Return no content if invoice is not read-able."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        response_format = {"type": "json_object"}
    )
    
    content = response.choices[0].message.content

    try:
        data = json.loads(content)
        if not content or not data:
            raise ValueError("Empty LLM Response")
    except Exception as e:
        return{
            "error": "LLM_OUTPUT_INVALID",
            "raw_data": content
        }

    required = ["invoice_number", "total", "date"]
    for field in required:
        if "invoice" in data and field not in data["invoice"]:
            data["invoice"][field] = None

    return data

def save_document(doc_id, doc_data):
    try:
        with open(DATA_PATH, "r") as f:
            db = json.load(f)
    except FileNotFoundError:
        db = {}

    db[doc_id] = doc_data

    with open(DATA_PATH, "w") as f:
        json.dump(db, f)