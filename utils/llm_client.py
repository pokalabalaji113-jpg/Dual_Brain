"""
utils/llm_client.py
Central LangChain + Groq LLM client for DualBrain AI.
All AI calls go through LangChain — no direct Groq calls.
"""

import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser


def get_llm(model: str = "llama-3.3-70b-versatile", temperature: float = 0.3) -> ChatGroq:
    """Return a LangChain ChatGroq instance."""
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not found. Add it to .streamlit/secrets.toml")
        st.stop()
    return ChatGroq(
        api_key=api_key,
        model=model,
        temperature=temperature,
    )


def call_llm(prompt: str, system: str = "", max_tokens: int = 2048) -> str:
    """Simple single-turn LangChain LLM call."""
    llm = get_llm()
    messages = []
    if system:
        messages.append(SystemMessage(content=system))
    messages.append(HumanMessage(content=prompt))
    chain = llm | StrOutputParser()
    return chain.invoke(messages)


def call_llm_with_history(history: list, system: str = "") -> str:
    """
    Multi-turn LangChain call.
    history: [{"role": "user"|"assistant", "content": "..."}]
    """
    from langchain_core.messages import AIMessage
    llm = get_llm()
    messages = []
    if system:
        messages.append(SystemMessage(content=system))
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    chain = llm | StrOutputParser()
    return chain.invoke(messages)


def get_rag_chain(retriever, system_prompt: str):
    """
    Build a LangChain RAG chain using a retriever.
    Used by Video Chatbot for transcript-grounded answers.
    """
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.prompts import PromptTemplate

    llm = get_llm()

    prompt = PromptTemplate.from_template(
        system_prompt + "\n\nContext:\n{context}\n\nQuestion: {question}"
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain
