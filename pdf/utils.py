import re
import os
import fitz  # PyMuPDF

from pdfai.client import co
from .models import PDFDocument


def normalize_title(title):
    title = title.lower().strip()
    return re.sub(r'\s+', ' ', title)


def generate_unique_title(user, base_title):
    normalized_base = normalize_title(base_title)

    if not PDFDocument.objects.filter(user=user, title__iexact=normalized_base).exists():
        return base_title

    i = 1
    while True:
        new_title = f"{base_title} ({i})"
        if not PDFDocument.objects.filter(user=user, title__iexact=normalize_title(new_title)).exists():
            return new_title
        i += 1


def extract_pdf_title_or_heading(file_path: str, original_name: str = None) -> str:
    doc = fitz.open(file_path)

    title = doc.metadata.get("title")
    if title:
        return title.strip()

    if original_name:
        name_without_ext = os.path.splitext(original_name)[0]
    else:
        file_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(file_name)[0]

    clean_name = name_without_ext.replace("_", " ").strip()
    return clean_name or "Untitled PDF"


def chunk_text(text, max_words=200):
    words = text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]


def batch_chunks(chunks, batch_size=96):
    batches = []
    for i in range(0, len(chunks), batch_size):
        batches.append(chunks[i:i + batch_size])
    return batches


def embed_chunks(chunks):
    batches = batch_chunks(chunks, batch_size=96)

    all_embeddings = []
    for batch in batches:
        response = co.embed(
            texts=batch,
            model="embed-english-v3.0",
            embedding_types=["float"],
            input_type='search_document'
        )
        all_embeddings.extend(response.embeddings.float_)
    return all_embeddings
    # return dict(all_embeddings).get("float_")[0]


def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text
