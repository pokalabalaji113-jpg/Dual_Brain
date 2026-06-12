"""
utils/llm_client.py
LangChain + Groq + Langfuse v3 — based on working reference pattern.
Sets env vars first, then imports — same pattern as your working project.
"""

import os

# ── Set Langfuse env vars FIRST before any import (proven pattern) ─────────────
def _bootstrap_langfuse():
    """Read keys and set env vars before Langfuse imports."""
    # Try .env file first
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except Exception:
        pass

    # Try secrets.toml fallback
    if not os.getenv("LANGFUSE_PUBLIC_KEY"):
        try:
            with open(".streamlit/secrets.toml") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and v:
                            os.environ[k] = v
        except Exception:
            pass

    # Fix: rename BASE_URL to HOST if someone used wrong key name
    if os.getenv("LANGFUSE_BASE_URL") and not os.getenv("LANGFUSE_HOST"):
        os.environ["LANGFUSE_HOST"] = os.getenv("LANGFUSE_BASE_URL")

_bootstrap_langfuse()

import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

MODEL_NAME  = "llama-3.3-70b-versatile"
TEMPERATURE = 0.3
MAX_TOKENS  = 2048


def _get_langfuse_handler():
    """
    Langfuse v3 handler — same pattern as your working reference project.
    Uses langfuse.langchain.CallbackHandler after env vars are set.
    """
    try:
        pk = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        sk = os.getenv("LANGFUSE_SECRET_KEY", "")
        host = os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com")

        if not pk or not sk:
            return None
        if "your" in pk.lower() or "your" in sk.lower():
            return None

        # v3 pattern: init singleton first
        from langfuse import Langfuse
        Langfuse(public_key=pk, secret_key=sk, host=host)

        # then get handler
        from langfuse.langchain import CallbackHandler
        handler = CallbackHandler()
        return handler

    except Exception:
        return None


def _get_secret(key):
    val = os.getenv(key, "")
    if not val:
        try:
            val = st.secrets.get(key, "")
        except Exception:
            val = ""
    return val


def get_llm(temperature=None, max_tokens=None):
    api_key = _get_secret("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found!")
        st.stop()
    return ChatGroq(
        api_key=api_key,
        model=MODEL_NAME,
        temperature=temperature if temperature is not None else TEMPERATURE,
        max_tokens=max_tokens if max_tokens is not None else MAX_TOKENS,
    )


def call_llm(prompt, system="", max_tokens=None, temperature=None,
             trace_name="DualBrain LLM Call"):
    llm  = get_llm(temperature=temperature, max_tokens=max_tokens)
    msgs = []
    if system:
        msgs.append(SystemMessage(content=system))
    msgs.append(HumanMessage(content=prompt))

    handler = _get_langfuse_handler()
    config  = {"callbacks": [handler], "run_name": trace_name} if handler else {}

    return (llm | StrOutputParser()).invoke(msgs, config=config)


def call_llm_with_history(history, system="", max_tokens=None,
                          temperature=None, trace_name="DualBrain Chat"):
    llm  = get_llm(temperature=temperature, max_tokens=max_tokens)
    msgs = []
    if system:
        msgs.append(SystemMessage(content=system))
    for m in history:
        if m["role"] == "user":
            msgs.append(HumanMessage(content=m["content"]))
        else:
            msgs.append(AIMessage(content=m["content"]))

    handler = _get_langfuse_handler()
    config  = {"callbacks": [handler], "run_name": trace_name} if handler else {}

    return (llm | StrOutputParser()).invoke(msgs, config=config)


def get_rag_chain(retriever, system_prompt):
    llm    = get_llm(temperature=0.1, max_tokens=1024)
    prompt = PromptTemplate.from_template(
        system_prompt + "\n\nContext:\n{context}\n\nQuestion: {question}"
    )
    def fmt(docs):
        return "\n\n".join(d.page_content for d in docs)

    chain = (
        {"context": retriever | fmt, "question": RunnablePassthrough()}
        | prompt | llm | StrOutputParser()
    )

    handler = _get_langfuse_handler()
    config  = {"callbacks": [handler], "run_name": "DualBrain RAG"} if handler else {}

    class RAGChain:
        def invoke(self, q):
            return chain.invoke(q, config=config)

    return RAGChain()