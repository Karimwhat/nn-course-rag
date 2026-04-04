from __future__ import annotations

import json
import shutil
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHUNKS_FILE = PROJECT_ROOT / "data" / "chunks" / "lecture_chunks.json"
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "vector_store"
COLLECTION_NAME = "lecture_chunks"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def load_chunks() -> list[dict]:
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(f"Chunks file not found: {CHUNKS_FILE}")

    with CHUNKS_FILE.open("r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not isinstance(chunks, list):
        raise ValueError("lecture_chunks.json must contain a list of chunk objects.")

    return chunks


def reset_vector_store() -> None:
    if VECTOR_STORE_DIR.exists():
        shutil.rmtree(VECTOR_STORE_DIR)
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks")

    reset_vector_store()

    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
    collection = client.create_collection(name=COLLECTION_NAME)

    documents: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []

    for chunk in chunks:
        chunk_id = chunk["chunk_id"]
        text = chunk["text"]

        metadata = {
            "source_file": chunk["source_file"],
            "source_path": chunk["source_path"],
            "lecture_title": chunk["lecture_title"],
            "lecture_date": chunk["lecture_date"] or "",
            "page_number": chunk["page_number"],
        }

        documents.append(text)
        metadatas.append(metadata)
        ids.append(chunk_id)

    print("Computing embeddings...")
    embeddings = model.encode(documents, show_progress_bar=True).tolist()

    print("Adding chunks to Chroma collection...")
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"Done. Stored {len(ids)} chunks in vector store:")
    print(VECTOR_STORE_DIR)


if __name__ == "__main__":
    main()