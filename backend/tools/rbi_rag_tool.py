import glob
import hashlib
import os
import pickle
from pathlib import Path

from crewai.tools import tool

DATA_DIR = Path(__file__).parent.parent / "data" / "rbi_circulars"
INDEX_PATH = DATA_DIR / "faiss_index.pkl"
CHUNKS_PATH = DATA_DIR / "chunks.pkl"

_index = None
_chunks = None


def _load_index() -> bool:
    global _index, _chunks
    if _index is not None:
        return True
    if not INDEX_PATH.exists() or not CHUNKS_PATH.exists():
        return False
    try:
        import faiss

        with open(INDEX_PATH, "rb") as f:
            _index = pickle.load(f)
        with open(CHUNKS_PATH, "rb") as f:
            _chunks = pickle.load(f)
        return True
    except Exception:
        return False


def _embed(text: str):
    import numpy as np

    vec = np.zeros(512, dtype=np.float32)
    t = text.lower()
    for i in range(len(t) - 2):
        h = int(hashlib.md5(t[i : i + 3].encode()).hexdigest(), 16) % 512
        vec[h] += 1.0
    n = np.linalg.norm(vec)
    return vec / n if n > 0 else vec


def build_rbi_index(pdf_dir: str = None) -> tuple[bool, str]:
    import faiss
    import numpy as np
    import PyPDF2

    pdf_dir = pdf_dir or str(DATA_DIR)
    pdfs = glob.glob(os.path.join(pdf_dir, "*.pdf"))
    if not pdfs:
        return False, "No PDFs found in data/rbi_circulars/"

    chunks = []
    for path in pdfs:
        try:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = "".join(p.extract_text() + "\n" for p in reader.pages)
            words = text.split()
            for i in range(0, len(words), 150):
                chunk = " ".join(words[i : i + 200])
                if len(chunk) > 80:
                    chunks.append({"text": chunk, "source": os.path.basename(path)})
        except Exception:
            continue

    if not chunks:
        return False, "Could not extract text from PDFs."

    embs = np.array([_embed(c["text"]) for c in chunks], dtype=np.float32)
    idx = faiss.IndexFlatIP(embs.shape[1])
    idx.add(embs)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(INDEX_PATH, "wb") as f:
        pickle.dump(idx, f)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    global _index, _chunks
    _index, _chunks = idx, chunks
    return True, f"Indexed {len(chunks)} chunks from {len(pdfs)} PDFs."


@tool("RBI Regulatory Search")
def search_rbi_regulations(query: str) -> str:
    """
    Search RBI circulars and regulatory documents using FAISS vector search (RAG).
    Use to find RBI actions, penalties, guidelines relevant to a bank or NBFC.
    query: e.g. 'RBI penalty HDFC Bank' or 'NBFC capital adequacy norms 2025'
    """
    import numpy as np

    if not _load_index():
        return (
            "RBI circular index not available — no PDFs indexed yet. "
            "Proceed with news-based regulatory research instead."
        )

    q_vec = _embed(query).reshape(1, -1)
    distances, indices = _index.search(q_vec, k=5)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx >= 0 and dist > 0.05:
            c = _chunks[idx]
            results.append(f"[{c['source']} | score {dist:.3f}]\n{c['text']}")

    return "\n\n---\n\n".join(results) if results else "No relevant RBI circulars found for this query."
