"""
pages/skill_videos.py
Bulletproof: Works for any skill. Never shows unavailable video.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.youtube_utils import search_youtube_videos, get_embed_html, get_transcript


def render():
    st.markdown("## 📺 Skill Videos")
    st.markdown("Search for any skill — watch videos right here, no YouTube tab needed.")
    st.markdown("---")

    prefill_skills = st.session_state.get("missing_skills_focus", [])
    resume_skills  = []
    if st.session_state.get("resume_data"):
        resume_skills = (st.session_state.resume_data or {}).get("skills", []) or []

    col1, col2 = st.columns([2, 1])
    with col1:
        skill_input = st.text_input("Enter a skill to learn",
            placeholder="e.g. Cloud Computing, Docker, GenAI, System Design")
    with col2:
        max_vids = st.selectbox("Videos to fetch", [3, 5, 8, 10], index=1)

    # Quick chips
    chip_list = list(dict.fromkeys(prefill_skills + resume_skills))[:10]
    if chip_list:
        st.markdown("**Quick pick:**")
        cols = st.columns(min(len(chip_list), 5))
        for i, skill in enumerate(chip_list[:5]):
            with cols[i]:
                if st.button(skill, key=f"chip_{i}_{skill[:8]}"):
                    st.session_state.search_skill = skill
                    st.session_state.skill_videos = []
                    st.rerun()

    search_skill = st.session_state.pop("search_skill", None)
    actual_skill = search_skill or skill_input
    search_btn   = st.button("🔍 Search Videos", type="primary")

    if search_btn and actual_skill:
        with st.spinner(f"Finding videos for '{actual_skill}'..."):
            videos = search_youtube_videos(actual_skill, max_results=max_vids)
        st.session_state.skill_videos       = videos
        st.session_state.skill_searched     = actual_skill
        st.session_state.selected_video_idx = 0
        # Auto-load first non-search video transcript
        for v in videos:
            vid_id = v.get("video_id","")
            if vid_id and not vid_id.startswith("SEARCH_"):
                with st.spinner("Loading transcript..."):
                    t = get_transcript(vid_id)
                st.session_state.current_video_transcript = t
                st.session_state.current_video_url        = v["url"]
                st.session_state.current_video_title      = v["title"]
                st.session_state.chat_history             = []
                break

    videos = st.session_state.get("skill_videos", [])
    if not videos:
        st.info("Enter any skill above and click Search Videos.")
        return

    searched = st.session_state.get("skill_searched","")
    st.markdown(f"### Results for: **{searched}**")

    if st.button("🗺 Generate Learning Path for this Skill"):
        st.session_state.lp_skill    = searched
        st.session_state.seeker_page = "Learning Path"
        st.rerun()

    st.markdown("---")
    list_col, player_col = st.columns([1, 2])

    with list_col:
        st.markdown("**Playlist**")
        for i, vid in enumerate(videos):
            is_active = st.session_state.get("selected_video_idx", 0) == i
            is_search = vid.get("is_search", False)
            border = "2px solid #111" if is_active else "1px solid #e0e0e0"
            bg     = "#f8f8f8"        if is_active else "#fff"
            icon   = "🔍" if is_search else f"{i+1}."
            st.markdown(f"""
            <div style="border:{border};border-radius:8px;padding:10px;
                        margin-bottom:8px;background:{bg};">
                <div style="font-size:0.82rem;font-weight:600;line-height:1.3;">
                    {icon} {vid['title'][:55]}{"..." if len(vid['title'])>55 else ""}
                </div>
                <div style="font-size:0.72rem;color:#888;margin-top:2px;">{vid['channel']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("▶ Play", key=f"play_{i}_{searched[:8]}", use_container_width=True):
                st.session_state.selected_video_idx = i
                vid_id = vid.get("video_id","")
                if vid_id and not vid_id.startswith("SEARCH_"):
                    with st.spinner("Loading transcript..."):
                        t = get_transcript(vid_id)
                    st.session_state.current_video_transcript = t
                    st.session_state.current_video_url        = vid["url"]
                    st.session_state.current_video_title      = vid["title"]
                    st.session_state.chat_history             = []
                st.rerun()

    with player_col:
        idx = st.session_state.get("selected_video_idx", 0)
        if idx < len(videos):
            vid       = videos[idx]
            vid_id    = vid.get("video_id","")
            is_search = vid.get("is_search", False)

            st.markdown(get_embed_html(vid_id, width=660, height=380), unsafe_allow_html=True)

            if not is_search:
                st.markdown(f"**{vid['title']}**")
                st.markdown(f"*{vid['channel']}*")
                transcript = st.session_state.get("current_video_transcript")
                cur_url    = st.session_state.get("current_video_url","")
                if cur_url == vid["url"]:
                    if transcript:
                        st.success(f"✅ Transcript loaded ({len(transcript.split())} words) — Chatbot ready!")
                    else:
                        st.warning("⚠️ No transcript — Chatbot uses general knowledge.")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💬 Chat about this video", use_container_width=True):
                        if cur_url != vid["url"] and vid_id:
                            with st.spinner("Loading transcript..."):
                                t = get_transcript(vid_id)
                            st.session_state.current_video_transcript = t
                            st.session_state.current_video_url        = vid["url"]
                            st.session_state.current_video_title      = vid["title"]
                            st.session_state.chat_history             = []
                        st.session_state.seeker_page = "Video Chatbot"
                        st.rerun()
                with c2:
                    if st.button("🗺 Learning Path", use_container_width=True):
                        st.session_state.lp_skill    = searched
                        st.session_state.seeker_page = "Learning Path"
                        st.rerun()
