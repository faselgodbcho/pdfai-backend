import fitz
import numpy as np

from pdfai.client import co
from pdf.utils import chunk_text, embed_chunks

from pdf.models import PDFChunk


def embed_query(prompt):
    response = co.embed(
        texts=[prompt],
        model="embed-english-v3.0",
        input_type="search_query",
        embedding_types=["float"],
    )

    return response.embeddings.float_[0]


def cosine_sim(a, b):
    a = np.array(a).flatten()
    b = np.array(b).flatten()
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join(page.get_text() for page in doc)
