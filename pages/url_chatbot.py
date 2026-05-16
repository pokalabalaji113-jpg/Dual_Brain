"""
pages/url_chatbot.py - Fixed: passes title + transcript correctly to chatbot.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.youtube_utils import get_transcript, extract_video_id_from_url, get_embed_html
from utils.llm_client import call_llm, call_llm_with_history

MAX_WORDS = 4000


def fetch_video_title(vid_id: str) -> str:
    """Try to get video title via YouTube API or oEmbed."""
    try:
        import urllib.request, json
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid_id}&format=json"
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
            return data.get("title", f"YouTube Video ({vid_id})")
    except Exception:
        return f"YouTube Video ({vid_id})"


def get_answer(question: str, transcript: str, video_title: str) -> str:
    """Answer using RAG if transcript available, else general knowledge about title."""
    if transcript:
        # Try FAISS RAG first
        try:
            from utils.rag_engine import get_retriever
            from utils.llm_client import get_rag_chain
            retriever = get_retriever(transcript, video_title)
            system = f"""You are an expert tutor for the YouTube video: "{video_title}".
Answer ONLY based on the transcript context provided.
If the answer is not in the transcript, say "This wasn't covered in this video" then give a brief general answer.
Use bullet points for clarity. Be educational and concise."""
            chain = get_rag_chain(retriever, system)
            return chain.invoke(question)
        except Exception:
            pass

        # Fallback: direct transcript in prompt
        ctx = " ".join(transcript.split()[:MAX_WORDS])
        prompt = f"""You are a tutor for the YouTube video: "{video_title}".
Use ONLY this transcript to answer the question.
If the answer is not in the transcript, say so clearly then give a brief general answer.

TRANSCRIPT:
{ctx}

QUESTION: {question}

Give a clear, structured answer with bullet points where helpful."""
        return call_llm(prompt)
    else:
        # No transcript — use video title as context
        prompt = f"""You are an expert tutor. The user watched a YouTube video titled: "{video_title}".
Answer their question about the topics discussed in this video using your knowledge.
Be educational, clear, and use bullet points.

Question: {question}"""
        return call_llm(prompt)


def render():
    st.markdown("## 🔗 YouTube URL Chatbot")
    st.markdown("Paste **any YouTube URL** → transcript extracted → ask your doubts instantly.")
    st.markdown("Available in **both Job Seeker and Employee Brain.**")
    st.markdown("---")

    # ── Step 1: URL Input ──────────────────────────────────────────────────────
    st.markdown("### Step 1 — Paste YouTube URL")
    col1, col2 = st.columns([3, 1])
    with col1:
        url_input = st.text_input(
            "YouTube Video URL",
            placeholder="https://www.youtube.com/watch?v=...",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        load_btn = st.button("🚀 Load Video", type="primary", use_container_width=True)

    if load_btn and url_input:
        vid_id = extract_video_id_from_url(url_input.strip())
        if not vid_id:
            st.error("❌ Invalid YouTube URL.")
            return

        with st.spinner("Fetching video title..."):
            title = fetch_video_title(vid_id)

        with st.spinner("Extracting transcript..."):
            transcript = get_transcript(vid_id)

        st.session_state.url_bot_vid_id     = vid_id
        st.session_state.url_bot_url        = url_input.strip()
        st.session_state.url_bot_transcript = transcript
        st.session_state.url_bot_title      = title
        st.session_state.url_bot_history    = []

        if transcript:
            st.success(f"✅ '{title}' — Transcript loaded ({len(transcript.split())} words). Chatbot ready!")
        else:
            st.warning(f"⚠️ '{title}' — No transcript available. Chatbot answers from general knowledge about this topic.")
        st.rerun()

    # ── No video loaded ────────────────────────────────────────────────────────
    vid_id     = st.session_state.get("url_bot_vid_id", "")
    transcript = st.session_state.get("url_bot_transcript", None)
    video_title= st.session_state.get("url_bot_title", "")
    video_url  = st.session_state.get("url_bot_url", "")

    if not vid_id:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
### 💡 How to use
**Step 1:** Watch any video on YouTube

**Step 2:** Copy the URL from your browser

**Step 3:** Paste it above → Click **Load Video**

**Step 4:** Ask your doubts below!
            """)
        with col2:
            st.markdown("""
### 📋 Supported formats
- `youtube.com/watch?v=VIDEO_ID`
- `youtu.be/VIDEO_ID`
- `youtube.com/embed/VIDEO_ID`

### ✅ Works for
- Any tutorial / course video
- Tech talks and lectures
- Any video with captions enabled
            """)

        # Quick load from skill videos
        cur_url   = st.session_state.get("current_video_url","")
        cur_title = st.session_state.get("current_video_title","")
        cur_trans = st.session_state.get("current_video_transcript")
        if cur_url:
            st.markdown("---")
            st.markdown(f"**Last video from Skill Videos:** *{cur_title}*")
            if st.button("💬 Continue chatting about this video", type="secondary"):
                cur_vid_id = extract_video_id_from_url(cur_url)
                if cur_vid_id:
                    st.session_state.url_bot_vid_id     = cur_vid_id
                    st.session_state.url_bot_url        = cur_url
                    st.session_state.url_bot_transcript = cur_trans
                    st.session_state.url_bot_title      = cur_title
                    st.session_state.url_bot_history    = []
                    st.rerun()
        return

    # ── Step 2: Video loaded ───────────────────────────────────────────────────
    st.markdown("### Step 2 — Video Loaded ✅")

    col_v, col_i = st.columns([2, 1])
    with col_v:
        st.markdown(get_embed_html(vid_id, width=500, height=280), unsafe_allow_html=True)
    with col_i:
        st.markdown(f"**📹 Title:** {video_title}")
        if transcript:
            st.success(f"✅ Transcript: {len(transcript.split())} words\n\nRAG: FAISS Active")
        else:
            st.warning("⚠️ No transcript\n\nMode: General Knowledge")
        if st.button("🔄 Load Different Video", use_container_width=True):
            for key in ["url_bot_vid_id","url_bot_url","url_bot_transcript",
                        "url_bot_title","url_bot_history"]:
                st.session_state[key] = "" if "history" not in key else []
            st.rerun()

    # ── Step 3: Chat ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Step 3 — Ask Your Doubts")

    quick = ["Summarize this video in 5 points","What are the key concepts?",
             "Quiz me with 3 questions","What should I learn next?",
             "Explain the main concept simply","What are the prerequisites?",
             "Give me code examples","What are common mistakes?"]
    cols = st.columns(4)
    for i, qp in enumerate(quick):
        with cols[i % 4]:
            if st.button(qp, key=f"url_qp_{i}", use_container_width=True):
                st.session_state.url_pending = qp

    st.markdown("---")

    if "url_bot_history" not in st.session_state:
        st.session_state.url_bot_history = []

    for msg in st.session_state.url_bot_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    pending    = st.session_state.pop("url_pending", None)
    user_input = st.chat_input("Ask anything about this video...")
    final      = pending or user_input

    if final:
        st.session_state.url_bot_history.append({"role": "user", "content": final})
        with st.chat_message("user"):
            st.markdown(final)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_answer(final, transcript, video_title)
            st.markdown(response)
        st.session_state.url_bot_history.append({"role": "assistant", "content": response})
        st.rerun()

    if st.session_state.url_bot_history:
        if st.button("🗑 Clear Chat"):
            st.session_state.url_bot_history = []
            st.rerun()
