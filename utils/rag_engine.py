"""
utils/rag_engine.py
FAISS-based RAG engine for Video Chatbot.
Splits transcript into chunks, embeds with sentence-transformers,
stores in FAISS, retrieves relevant chunks per query.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


@st.cache_resource(show_spinner=False)
def get_embeddings():
    """Load sentence-transformer embeddings (cached)."""
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )


def build_vectorstore(transcript: str, video_title: str = "") -> FAISS:
    """
    Split transcript into chunks and build a FAISS vector store.
    Returns a FAISS retriever-ready store.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=[". ", "? ", "! ", "\n", " "],
    )
    chunks = splitter.split_text(transcript)
    docs = [
        Document(page_content=chunk, metadata={"source": video_title, "chunk": i})
        for i, chunk in enumerate(chunks)
    ]
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore


def get_retriever(transcript: str, video_title: str = "", k: int = 4):
    """Build vectorstore and return a retriever."""
    vs = build_vectorstore(transcript, video_title)
    return vs.as_retriever(search_kwargs={"k": k})
