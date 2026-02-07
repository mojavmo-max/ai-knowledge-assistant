from dotenv import load_dotenv
from openai import OpenAI
import json
from vision.services.image_processing_service import run_ocr, run_vision
from vision.services.invoice_service import extract_invoice_fields
import hashlib
from cachetools import TTLCache
from threading import Lock
import time

load_dotenv()
client = OpenAI()

DATA_PATH = "db.txt"

CACHE = TTLCache(maxsize = 500, ttl=60*30)
cache_lock = Lock()
IN_FLIGHT = set()

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


def extract_text(image_path):
    ocr_text = run_ocr(image_path)

    if len(ocr_text) < 200:
        return run_vision(image_path)

    return ocr_text
    

def generate_cache_key(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def process_document(doc_id, text):
    key = generate_cache_key(text)

    if key in IN_FLIGHT:
        time.sleep(8)
        with cache_lock:
            return CACHE.get(key)
    
    IN_FLIGHT.add(key)

    with cache_lock:
        if key in CACHE:
            return CACHE[key]

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

    try:
        save_document(doc_id, doc_data)
        data = doc_data["metadata"]

        if not data:
            with cache_lock:
                CACHE[key] = None, "Empty response"
            raise ValueError("Empty response")
        
        if data.get("error"):
            with cache_lock:
                CACHE[key] = None, data["error"]
            return None, data["error"]

        with cache_lock:
            CACHE[key] = data, None
        return data, None
    finally:
        IN_FLIGHT.remove(key)
    

def save_document(doc_id, doc_data):
    try:
        with open(DATA_PATH, "r") as f:
            db = json.load(f)
    except FileNotFoundError:
        db = {}

    db[doc_id] = doc_data

    with open(DATA_PATH, "w") as f:
        json.dump(db, f)