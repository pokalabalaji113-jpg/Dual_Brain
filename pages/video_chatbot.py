"""
pages/video_chatbot.py
Improved chatbot — RAG grounded, no duplicates, better UX.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.llm_client import call_llm_with_history

MAX_WORDS = 4000


def get_rag_answer(question: str, transcript: str, video_title: str) -> str:
    try:
        from utils.rag_engine import get_retriever
        from utils.llm_client import get_rag_chain
        retriever = get_retriever(transcript, video_title)
        system    = f"""You are an expert tutor for the YouTube video: "{video_title}".
Answer ONLY based on the retrieved transcript context.
If the answer is not in the transcript, say: "This wasn't covered in the video" and give a brief general answer.
Be clear, educational, structured with bullet points when needed."""
        chain = get_rag_chain(retriever, system)
        return chain.invoke(question)
    except Exception:
        words    = transcript.split()[:MAX_WORDS]
        trimmed  = " ".join(words)
        messages = [{"role": "user", "content":
            f"""You are a tutor for the video: "{video_title}".
Use ONLY the transcript below to answer. If not found, say so clearly.

TRANSCRIPT:
{trimmed}

QUESTION: {question}

Give a clear, structured answer with bullet points where needed."""}]
        return call_llm_with_history(messages)


def get_general_answer(question: str, video_title: str) -> str:
    messages = [{"role": "user", "content":
        f"""You are an expert tutor. The user watched a video titled: "{video_title}".
Answer their question about this topic. Be educational, clear, and use bullet points.
Question: {question}"""}]
    return call_llm_with_history(messages)


def render():
    st.markdown("## 💬 Video Chatbot")
    st.markdown("Powered by **LangChain RAG + FAISS + Groq LLaMA 3.3 70B**")

    video_url   = st.session_state.get("current_video_url", "")
    video_title = st.session_state.get("current_video_title", "")
    transcript  = st.session_state.get("current_video_transcript", None)

    if not video_url:
        st.info("👈 Go to **Skill Videos**, play a video, then click 'Chat about this video'.")
        st.markdown("**Or enter a YouTube URL directly:**")
        manual_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        if manual_url and st.button("Load Video", type="primary"):
            from utils.youtube_utils import extract_video_id_from_url, get_transcript
            vid_id = extract_video_id_from_url(manual_url)
            if vid_id:
                with st.spinner("Loading transcript..."):
                    t = get_transcript(vid_id)
                st.session_state.current_video_url        = manual_url
                st.session_state.current_video_transcript = t
                st.session_state.current_video_title      = "YouTube Video"
                st.session_state.chat_history             = []
                st.rerun()
            else:
                st.error("Invalid YouTube URL.")
        return

    # Status bar
    if transcript:
        st.success(f"✅ **{video_title}** — FAISS RAG Active ({len(transcript.split())} words)")
    else:
        st.warning(f"⚠️ **{video_title}** — No transcript. Using general knowledge.")

    # Quick prompts
    st.markdown("**Quick questions:**")
    quick = [
        "Summarize this video in 5 points",
        "What are the key takeaways?",
        "Quiz me with 3 questions",
        "What should I learn next?",
        "Explain the main concept simply",
        "What are prerequisites for this?",
    ]
    cols = st.columns(3)
    for i, qp in enumerate(quick):
        with cols[i % 3]:
            if st.button(qp, key=f"qp_{i}", use_container_width=True):
                st.session_state.pending_message = qp

    st.markdown("---")

    # Init history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Single input source — no duplicates
    pending    = st.session_state.pop("pending_message", None)
    user_input = st.chat_input("Ask anything about this video...")
    final      = pending or user_input

    if final:
        st.session_state.chat_history.append({"role": "user", "content": final})
        with st.chat_message("user"):
            st.markdown(final)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if transcript:
                    response = get_rag_answer(final, transcript, video_title)
                else:
                    response = get_general_answer(final, video_title)
            st.markdown(response)

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.session_state.chat_history:
            if st.button("🗑 Clear"):
                st.session_state.chat_history = []
                st.rerun()
    with col2:
        if st.button("🔄 Load Different Video", use_container_width=True):
            st.session_state.current_video_url        = ""
            st.session_state.current_video_transcript = None
            st.session_state.current_video_title      = ""
            st.session_state.chat_history             = []
            st.session_state.seeker_page              = "Skill Videos"
            st.rerun()
