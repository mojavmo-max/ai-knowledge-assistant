import pdfplumber
from pathlib import Path

DOCS_DIR = Path("data/docs")
OUT_DIR = Path("data/cleaned")
OUT_DIR.mkdir(exist_ok=True)

def load_pdf(path):
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)

def clean_text(raw):
    result = raw.replace("\n", " ")
    result = " ".join(result.split())
    return result

for pdf_file in DOCS_DIR.glob("*.pdf"):
    content = load_pdf(pdf_file)
    cleanedContent = clean_text(content)
    out_path = OUT_DIR / f"{pdf_file.stem}.txt"
    out_path.write_text(cleanedContent, encoding="utf-8")


