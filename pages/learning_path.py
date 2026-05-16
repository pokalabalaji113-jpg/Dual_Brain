"""
pages/learning_path.py
Fixed: Unique button keys to prevent duplicate key error.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import json
from utils.llm_client import call_llm
from utils.youtube_utils import search_youtube_videos, get_embed_html, get_transcript


def generate_learning_path(skill, current_skills, level) -> dict:
    known = ", ".join(current_skills) if current_skills else "none"
    prompt = f"""
Create a learning path for: "{skill}"
Current skills: {known} | Level: {level}

Return ONLY this JSON:
{{
  "skill": "{skill}",
  "estimated_weeks": 8,
  "phases": [
    {{
      "phase_number": 1,
      "phase_name": "Foundation",
      "duration_weeks": 2,
      "topics": [
        {{
          "topic": "Topic name",
          "description": "What to learn and why",
          "search_query": "Best YouTube search for this topic",
          "importance": "high"
        }}
      ],
      "milestone": "What you can do after this phase"
    }}
  ],
  "missing_foundations": ["prerequisite1"],
  "career_outcomes": ["Job role 1","Job role 2"],
  "practice_projects": ["Project 1","Project 2","Project 3"]
}}
Make 3-4 phases, 3-5 topics each. Return ONLY valid JSON.
"""
    raw = call_llm(prompt)
    try:
        clean = raw.strip().strip("```json").strip("```").strip()
        return json.loads(clean)
    except Exception:
        return {"error": raw}


def render():
    st.markdown("## 🗺 Learning Path")
    st.markdown("Powered by **LangChain + Groq LLaMA 3.3 70B**")
    st.markdown("---")

    c1, c2, c3 = st.columns([2, 1.5, 1])
    with c1:
        skill = st.text_input("Skill to learn",
            value=st.session_state.get("lp_skill", ""),
            placeholder="e.g. Machine Learning, React, System Design")
    with c2:
        level = st.selectbox("Experience level", ["Beginner", "Intermediate", "Advanced"])
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        gen_btn = st.button("🗺 Generate Path", type="primary", use_container_width=True)

    resume_skills = []
    if st.session_state.get("resume_data"):
        resume_skills = (st.session_state.resume_data or {}).get("skills", []) or []

    if gen_btn and skill:
        with st.spinner(f"Building {skill} learning path..."):
            path = generate_learning_path(skill, resume_skills, level)
        st.session_state.current_learning_path = path
        st.session_state.lp_skill = skill

    path = st.session_state.get("current_learning_path")
    if not path:
        st.info("Enter a skill and click Generate Path.")
        return
    if "error" in path:
        st.error("Generation failed. Try again.")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Skill",    path.get("skill", skill))
    with c2: st.metric("Duration", f"{path.get('estimated_weeks','?')} weeks")
    with c3: st.metric("Phases",   len(path.get("phases", [])))
    with c4: st.metric("Outcomes", len(path.get("career_outcomes", [])))

    missing = path.get("missing_foundations", [])
    if missing:
        st.warning(f"⚠️ Learn these first: {', '.join(missing)}")

    st.markdown("---")

    phases     = path.get("phases", [])
    tab_labels = [f"Phase {p['phase_number']}: {p['phase_name']}" for p in phases]
    tabs       = st.tabs(tab_labels)

    for tab, phase in zip(tabs, phases):
        with tab:
            st.markdown(f"**Duration:** {phase.get('duration_weeks','?')} weeks")
            st.markdown(f"**🎯 Milestone:** *{phase.get('milestone','')}*")
            st.markdown("---")

            for t_idx, topic in enumerate(phase.get("topics", [])):
                imp   = topic.get("importance", "medium")
                emoji = {"high":"🔴","medium":"🟡","low":"🟢"}.get(imp, "⚪")

                # ── UNIQUE KEY: phase_number + topic_index ──────────────────
                ph_num  = phase.get("phase_number", 0)
                btn_key = f"vid_ph{ph_num}_t{t_idx}"

                with st.expander(f"{emoji} {topic['topic']}", expanded=(imp == "high")):
                    st.markdown(f"**{topic.get('description','')}**")
                    search_q = topic.get("search_query", topic["topic"])
                    st.markdown(f"*Search: `{search_q}`*")

                    if st.button("📺 Find & Play Videos", key=btn_key, use_container_width=True):
                        with st.spinner(f"Searching videos for {topic['topic']}..."):
                            vids = search_youtube_videos(search_q, max_results=2)

                        for v_idx, v in enumerate(vids):
                            vid_id = v.get("video_id", "")
                            if vid_id:
                                st.markdown(get_embed_html(vid_id, width=580, height=320),
                                            unsafe_allow_html=True)
                                st.markdown(f"**{v['title']}** — {v['channel']}")

                                # ── UNIQUE chat button key ──────────────────
                                chat_key = f"chat_ph{ph_num}_t{t_idx}_v{v_idx}"
                                if st.button("💬 Chat about this video", key=chat_key):
                                    with st.spinner("Loading transcript..."):
                                        tr = get_transcript(vid_id)
                                    st.session_state.current_video_transcript = tr
                                    st.session_state.current_video_url        = v["url"]
                                    st.session_state.current_video_title      = v["title"]
                                    st.session_state.chat_history             = []
                                    st.session_state.seeker_page              = "Video Chatbot"
                                    st.rerun()
                                st.markdown("---")
                            else:
                                st.info(f"Add YOUTUBE_API_KEY for real '{search_q}' videos.")

    st.markdown("---")
    ca, cb = st.columns(2)
    with ca:
        st.markdown("### 🎯 Career Outcomes")
        for role in path.get("career_outcomes", []):
            enc = role.replace(" ", "%20")
            c1, c2 = st.columns([2, 1])
            with c1: st.markdown(f"**{role}**")
            with c2: st.link_button("Find Jobs",
                f"https://www.linkedin.com/jobs/search/?keywords={enc}")
    with cb:
        st.markdown("### 🛠 Practice Projects")
        for proj in path.get("practice_projects", []):
            st.markdown(f"- {proj}")
