from pathlib import Path
import tiktoken

TEXT_DIR= Path("data/cleaned")
encoder = tiktoken.get_encoding("cl100k_base")

texts = []

for text_file in TEXT_DIR.glob("*.txt"):
    texts.append(text_file.read_text(encoding="utf-8"))

def chunk_text(text, max_token=300, overlap=20):
    tokens = encoder.encode(text)
    chunks = []

    start = 0
    while start < len(tokens):
        end = start + max_token
        chunk_tokens = tokens[start:end]
        chunk_text = encoder.decode(chunk_tokens)
        chunks.append(chunk_text)
        start = end - overlap
    
    return chunks

all_chunks = []

for text in texts:
    chunks = chunk_text(text)
    all_chunks.extend(chunks)

Path("data").mkdir(exist_ok=True)
Path("data/chunks.txt").write_text(
    "\n\n---\n".join(chunks),
    encoding="utf-8"
)


print(f"Total chunks: {len(all_chunks)}")
print(all_chunks[0][:500])