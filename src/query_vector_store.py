from __future__ import annotations

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "vector_store"
COLLECTION_NAME = "lecture_chunks"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5


def main() -> None:
    if not VECTOR_STORE_DIR.exists():
        raise FileNotFoundError(
            f"Vector store not found at {VECTOR_STORE_DIR}. Run build_vector_store.py first."
        )

    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
    collection = client.get_collection(name=COLLECTION_NAME)

    while True:
        query = input("\nAsk a question (or type q to quit): ").strip()
        if query.lower() == "q":
            break
        if not query:
            continue

        query_embedding = model.encode(query).tolist()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=TOP_K,
        )

        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        print("\nTop results:\n")
        for i, (chunk_id, doc, meta, dist) in enumerate(zip(ids, documents, metadatas, distances), start=1):
            print(f"Result {i}")
            print(f"Chunk ID: {chunk_id}")
            print(f"Lecture: {meta.get('lecture_title', '')}")
            print(f"Date: {meta.get('lecture_date', '')}")
            print(f"Page: {meta.get('page_number', '')}")
            print(f"Distance: {dist:.4f}")
            print("Text:")
            print(doc[:1000])
            print("-" * 80)


if __name__ == "__main__":
    main()