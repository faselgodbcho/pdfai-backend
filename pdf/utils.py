import fitz  # PyMuPDF
from pdfai.client import co


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
