from __future__ import annotations

import json
import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHUNKS_FILE = PROJECT_ROOT / "data" / "chunks" / "lecture_chunks.json"
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "vector_store"
COLLECTION_NAME = "lecture_chunks"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


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


def build_documents(chunks: list[dict]) -> tuple[list[Document], list[str]]:
    documents: list[Document] = []
    ids: list[str] = []

    for chunk in chunks:
        chunk_id = chunk["chunk_id"]
        text = chunk["text"]

        metadata = {
            "chunk_id": chunk_id,
            "source_file": chunk["source_file"],
            "source_path": chunk["source_path"],
            "lecture_title": chunk["lecture_title"],
            "lecture_date": chunk["lecture_date"] or "",
            "page_number": chunk["page_number"],
        }

        documents.append(
            Document(
                page_content=text,
                metadata=metadata,
            )
        )
        ids.append(chunk_id)

    return documents, ids


def main() -> None:
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks")

    reset_vector_store()

    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    documents, ids = build_documents(chunks)

    print("Building Chroma vector store...")
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        ids=ids,
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTOR_STORE_DIR),
    )

    print(f"Done. Stored {len(ids)} chunks in vector store:")
    print(VECTOR_STORE_DIR)


if __name__ == "__main__":
    main()