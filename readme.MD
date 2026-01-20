## AI Knowledge Assistant

Ask questions over your PDFs using retrieval-augmented generation(RAG)

## Setup
1- Create venv
2- Install Requirements
3- Add OPENAI_API_KEY to .env

## Run
1- python load_docs.py
2- python chunk_text.py
3- python embed_chunks.py
4- python rag.py

## Limitations
- Depends on document quality
- No UI or API yet

# API
POST /documents
POST /chat

Swagger: 127.0.0.1:8000/docs