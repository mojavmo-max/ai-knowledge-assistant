from fastapi import FastAPI, UploadFile, File, HTTPException 
from pathlib import Path
from ingest import load_pdf, chunk_text, embed_chunks
from pydantic import BaseModel
from qa import question_answer
import time
from fastapi.middleware.cors import CORSMiddleware
import os
from vision.services.document_service import extract_text, process_document
import uuid
from starlette.concurrency import run_in_threadpool
import anyio


PORT = int(os.getenv("PORT", 8000))

app = FastAPI()

UPLOAD_DIR = Path("data/docs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024 # 10 MB
LAST_CALL = 0

anyio.to_thread.current_default_thread_limiter().total_tokens = 10

class Question(BaseModel):
    question: str


def rate_limit(seconds=2):
    global LAST_CALL
    if time.time() - LAST_CALL < seconds:
        raise HTTPException(status_code=400, detail="TOo many requests")
    LAST_CALL = time.time()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://ai-knowledge-assistant-tau.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def startup():
    if not UPLOAD_DIR.exists():
        UPLOAD_DIR.mkdir(parents=True)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/documents")
async def upload(file: UploadFile = File(...)):
    '''
        Upload a PDF document and index it for semantic search.
    '''
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed.")

    
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File uploaded is too large.")

    path = UPLOAD_DIR/file.filename
    path.write_bytes(content)

    text = load_pdf(path)
    chunks = chunk_text(text)
    embed_chunks(chunks)

    return {
        "status": "indexed",
        "chunks": len(chunks)
    }

@app.post("/chat")
async def chat(q: Question):
    '''
        Ask server questions about the documents uploaded.
    '''
    rate_limit()
    if not q.question.strip():
        raise HTTPException(status_code=400, detail="Empty question")
    answer = question_answer(q.question)
    return {"answer": answer}

@app.post("/invoiceDetails")
async def invoiceDetails(file: UploadFile = File(...)):
    '''
        Upload an invoice document and index it for semantic search.
    '''
    doc_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR/f"{doc_id}_{file.filename}"
    print(doc_id)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    start  = time.time()
    text = extract_text(file_path)
    print("Extraction time:", time.time() - start)
    start = time.time()
    try:
        structured, error = await run_in_threadpool(process_document, doc_id, text)
        print("Processing time:", time.time() - start)
        if error:
            return {"success": False, "data": None, "error": error}

        return {"success": True, "data": structured, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}
