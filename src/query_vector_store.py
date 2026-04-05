from __future__ import annotations

import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "vector_store"
COLLECTION_NAME = "lecture_chunks"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
ANSWER_MODEL_NAME = "gemini-3-flash-preview"


def format_context(docs: list) -> str:
    """Format retrieved documents into a readable prompt context."""
    context_parts = []

    for i, doc in enumerate(docs, start=1):
        meta = doc.metadata
        lecture_title = meta.get("lecture_title", "")
        lecture_date = meta.get("lecture_date", "")
        page_number = meta.get("page_number", "")
        chunk_id = meta.get("chunk_id", "")
        chunk_number = meta.get("chunk_number", "")

        context_parts.append(
            f"[Document {i}; chunk_number: {chunk_number}]\n"
            f"Chunk ID: {chunk_id}\n"
            f"Lecture: {lecture_title}\n"
            f"Date: {lecture_date}\n"
            f"Page: {page_number}\n"
            f"Content:\n{doc.page_content}"
        )

    return "\n\n" + ("\n\n" + "=" * 80 + "\n\n").join(context_parts)


def query_vector_store(
    query, 
    vector_store,
    llm,
    enable_rag,
    enable_context=True,
    top_k = 10,
    print_chunks=False,
    print_context=False, 
    print_answer=False,
) -> str:
    """
    Send a query to the LLM and returns an answer string
    """

    if enable_rag:
        chunks = vector_store.similarity_search(query, k=top_k)
    else:
        # 1. Retrieve all items from the collection
        all_data = vector_store.get()
        # 2. Convert the raw dictionary output into a list of Document objects
        chunks = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(all_data["documents"], all_data["metadatas"])
        ]
        # 3. Sort the chunks. 
        # We sort by chunk_number to ensure chronological/sequential order.
        chunks.sort(key=lambda x: (x.metadata.get("chunk_number", "")))

    context = format_context(chunks)

    if print_chunks:
        print("\nTop retrieved chunks:\n")
        for i, doc in enumerate(chunks, start=1):
            meta = doc.metadata
            print(f"Result {i}")
            print(f"Chunk ID: {meta.get('chunk_id', '')}")
            print(f"Lecture: {meta.get('lecture_title', '')}")
            print(f"Date: {meta.get('lecture_date', '')}")
            print(f"Page: {meta.get('page_number', '')}")
            print(doc.page_content[:500])
            print("-" * 80)
    
    if print_context:
        print(context)

    if enable_context:
        system_prompt = f"""You are a helpful assistant answering questions about COMP 4107 course material.
            Use only the retrieved context below to answer the question.
            If the answer is not clearly supported by the context, say so.

            When possible:
            - answer clearly and directly
            - cite the supporting lecture/page/chunk IDs in a short "Sources" section, also include inline citations
            - do not invent facts not present in the context

            When you cite your answers, use the chunk_number.

            Retrieved Context:
            {context}
        """
    else:
        system_prompt = f"""You are a Computer Science student answering questions to the best of your ability
        """

    prompts = [
        ("system", system_prompt),
        ("human", query),
    ]
    response = llm.invoke(prompts)

    if print_answer:
        print(response.text)

    return response.text


def initialize_vector_store_llm():
    if not VECTOR_STORE_DIR.exists():
        raise FileNotFoundError(
            f"Vector store not found at {VECTOR_STORE_DIR}. Run build_vector_store.py first."
        )

    if not os.getenv("GOOGLE_API_KEY"):
        raise EnvironmentError(
            "GOOGLE_API_KEY is not set. Please set it before running this script."
        )

    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTOR_STORE_DIR),
        embedding_function=embeddings,
    )

    llm = ChatGoogleGenerativeAI(
        model=ANSWER_MODEL_NAME,
        temperature=0,
    )

    return vector_store, llm


if __name__ == "__main__":
    """
    Interactive Q&A prompt to manually test the query_vector_store function
    """

    vector_store, llm = initialize_vector_store_llm()

    while True:
        query = input("\nAsk a question (or type q to quit): ").strip()
       
        if query.lower() == "q":
            break
    
        if not query:
            continue

        answer = query_vector_store(query=query, vector_store=vector_store, llm=llm, enable_rag=False)
        
        print("\nAnswer:\n")
        print(answer)
        print("\n" + "=" * 100)
