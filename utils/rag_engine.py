"""
utils/rag_engine.py
Hybrid RAG = FAISS (dense) + BM25 (sparse) combined.
Dense: semantic similarity via sentence-transformers
Sparse: keyword matching via BM25
Final: weighted combination of both scores
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


@st.cache_resource(show_spinner=False)
def get_embeddings():
    """Load sentence-transformer embeddings (cached)."""
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )


def split_text(transcript: str, video_title: str = "") -> list:
    """Split transcript into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=[". ", "? ", "! ", "\n", " "],
    )
    chunks = splitter.split_text(transcript)
    return [
        Document(
            page_content=chunk,
            metadata={"source": video_title, "chunk": i}
        )
        for i, chunk in enumerate(chunks)
    ]


def build_faiss_retriever(docs: list, k: int = 4):
    """Build FAISS dense retriever."""
    from langchain_community.vectorstores import FAISS
    embeddings  = get_embeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": k})


def build_bm25_retriever(docs: list, k: int = 4):
    """Build BM25 sparse retriever (keyword matching)."""
    try:
        from langchain_community.retrievers import BM25Retriever
        retriever   = BM25Retriever.from_documents(docs)
        retriever.k = k
        return retriever
    except ImportError:
        return None


def get_retriever(transcript: str, video_title: str = "", k: int = 4):
    """
    Hybrid RAG retriever — FAISS + BM25 combined.
    Falls back to FAISS only if BM25 not available.
    """
    docs             = split_text(transcript, video_title)
    faiss_retriever  = build_faiss_retriever(docs, k=k)
    bm25_retriever   = build_bm25_retriever(docs, k=k)

    if bm25_retriever:
        try:
            from langchain.retrievers import EnsembleRetriever
            # 60% FAISS (semantic) + 40% BM25 (keyword)
            hybrid = EnsembleRetriever(
                retrievers=[faiss_retriever, bm25_retriever],
                weights=[0.6, 0.4],
            )
            return hybrid
        except Exception:
            pass

    # Fallback: FAISS only
    return faiss_retriever
