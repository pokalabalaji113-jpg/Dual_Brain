"""
DualBrain AI — Job Seeker & Employee Intelligence Platform
Fixed: Sidebar proper width, readable navigation, no compression.
"""

import sys
import os
import importlib.util
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

st.set_page_config(
    page_title="DualBrain AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* ── Hide collapse arrow ── */
    [data-testid="collapsedControl"] { display: none !important; }

    /* ── Sidebar fixed width, always open ── */
    section[data-testid="stSidebar"] {
        width: 220px !important;
        min-width: 220px !important;
        max-width: 220px !important;
        transform: translateX(0px) !important;
        visibility: visible !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        width: 220px !important;
        padding: 1rem 0.8rem !important;
        overflow-x: hidden !important;
    }

    /* ── Sidebar buttons — full text visible ── */
    section[data-testid="stSidebar"] button {
        white-space: normal !important;
        word-wrap: break-word !important;
        height: auto !important;
        min-height: 38px !important;
        font-size: 0.82rem !important;
        padding: 6px 10px !important;
        line-height: 1.3 !important;
        text-align: left !important;
    }

    /* ── Main content area ── */
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }

    /* ── Brain cards ── */
    .brain-card {
        border: 1.5px solid #e0e0e0;
        border-radius: 10px;
        padding: 24px 20px;
        text-align: center;
        background: #fff;
    }
    .brain-icon  { font-size: 2.4rem; margin-bottom: 8px; }
    .brain-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 4px; }
    .brain-sub   { font-size: 0.82rem; color: #666; }

    .section-label {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #999;
        margin-bottom: 6px;
        margin-top: 4px;
    }

    #MainMenu { visibility: hidden; }
    footer     { visibility: hidden; }
    header     { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Page maps ──────────────────────────────────────────────────────────────────
SEEKER_PAGES = {
    "Resume Analysis": "resume_analysis",
    "Skill Videos":    "skill_videos",
    "Video Chatbot":   "video_chatbot",
    "URL Chatbot":     "url_chatbot",
    "Learning Path":   "learning_path",
    "Job Links":       "job_links",
}

EMPLOYEE_PAGES = {
    "Learning Companion":   "learning_companion",
    "Career Transition":    "career_transition",
    "Burnout Intelligence": "burnout_intelligence",
    "Performance Analyzer": "performance_analyzer",
    "Skill Assessment":     "skill_assessment",
    "Team Intelligence":    "team_intelligence",
    "URL Chatbot":          "url_chatbot",
}

# ── Session state defaults ─────────────────────────────────────────────────────
defaults = {
    "brain_mode":               None,
    "seeker_page":              "Resume Analysis",
    "employee_page":            "Learning Companion",
    "resume_data":              None,
    "chat_history":             [],
    "current_video_transcript": None,
    "current_video_url":        None,
    "current_video_title":      "",
    "skill_videos":             [],
    "skill_searched":           "",
    "selected_video_idx":       0,
    "job_results":              [],
    "resume_text":              "",
    "job_role_target":          "",
    "missing_skills_focus":     [],
    "lp_skill":                 "",
    "emp_profile":              {},
    "emp_profile_saved":        False,
    "emp_roadmap":              None,
    "transition_plan":          None,
    "burnout_result":           None,
    "perf_result":              None,
    "team_result":              None,
    "lc_history":               [],
    "url_bot_vid_id":           "",
    "url_bot_url":              "",
    "url_bot_transcript":       None,
    "url_bot_title":            "",
    "url_bot_history":          [],
    "quiz_state":               "setup",
    "quiz_questions":           [],
    "quiz_answers":             {},
    "quiz_current_q":           0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state.seeker_page not in SEEKER_PAGES:
    st.session_state.seeker_page = "Resume Analysis"
if st.session_state.employee_page not in EMPLOYEE_PAGES:
    st.session_state.employee_page = "Learning Companion"


# ── Page loader ────────────────────────────────────────────────────────────────
def load_page(filename: str):
    page_path = os.path.join(BASE_DIR, "pages", f"{filename}.py")
    if not os.path.exists(page_path):
        st.error(f"❌ File not found: {page_path}")
        return
    spec   = importlib.util.spec_from_file_location(filename, page_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.render()


# ── Brain selector ─────────────────────────────────────────────────────────────
def render_brain_selector():
    st.markdown("## 🧠 DualBrain AI")
    st.markdown("Choose your mode to begin. The AI adapts its intelligence to your role.")
    st.markdown("---")
    col1, col2, _ = st.columns([1, 1, 0.2])
    with col1:
        st.markdown("""
        <div class="brain-card">
            <div class="brain-icon">🎯</div>
            <div class="brain-title">Job Seeker Brain</div>
            <div class="brain-sub">Resume analysis · Skill videos · Learning paths · Job links</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter Job Seeker Mode", key="btn_seeker", use_container_width=True):
            st.session_state.brain_mode  = "seeker"
            st.session_state.seeker_page = "Resume Analysis"
            st.rerun()
    with col2:
        st.markdown("""
        <div class="brain-card">
            <div class="brain-icon">💼</div>
            <div class="brain-title">Employee Brain</div>
            <div class="brain-sub">Learning companion · Career transitions · Burnout intelligence · Performance</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter Employee Mode", key="btn_employee", use_container_width=True):
            st.session_state.brain_mode    = "employee"
            st.session_state.employee_page = "Learning Companion"
            st.rerun()
    st.markdown("---")
    st.markdown(
        '<div style="color:#999;font-size:0.82rem;">'
        'DualBrain AI — LangChain · LangGraph · Groq LLaMA 3.3 70B · FAISS · MCP'
        '</div>',
        unsafe_allow_html=True,
    )


# ── Sidebar ────────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("### 🧠 DualBrain AI")
        st.markdown("---")

        if st.session_state.brain_mode:
            mode_label = (
                "🎯 Job Seeker"
                if st.session_state.brain_mode == "seeker"
                else "💼 Employee"
            )
            st.markdown(f"**Active:** {mode_label}")
            if st.button("↩ Switch Brain", use_container_width=True):
                st.session_state.brain_mode = None
                st.rerun()
            st.markdown("---")

        if st.session_state.brain_mode == "seeker":
            st.markdown(
                '<div class="section-label">Job Seeker Tools</div>',
                unsafe_allow_html=True,
            )
            for page in SEEKER_PAGES:
                active = st.session_state.seeker_page == page
                if st.button(
                    page,
                    key=f"nav_{page}",
                    use_container_width=True,
                    type="primary" if active else "secondary",
                ):
                    st.session_state.seeker_page = page
                    st.rerun()

        elif st.session_state.brain_mode == "employee":
            st.markdown(
                '<div class="section-label">Employee Tools</div>',
                unsafe_allow_html=True,
            )
            for page in EMPLOYEE_PAGES:
                active = st.session_state.employee_page == page
                if st.button(
                    page,
                    key=f"nav_{page}",
                    use_container_width=True,
                    type="primary" if active else "secondary",
                ):
                    st.session_state.employee_page = page
                    st.rerun()

        st.markdown("---")
        st.markdown(
            '<div style="color:#999;font-size:0.75rem;">DualBrain AI v1.0</div>',
            unsafe_allow_html=True,
        )


# ── Routing ────────────────────────────────────────────────────────────────────
render_sidebar()

if st.session_state.brain_mode is None:
    render_brain_selector()

elif st.session_state.brain_mode == "seeker":
    page = st.session_state.seeker_page
    if page not in SEEKER_PAGES:
        st.session_state.seeker_page = "Resume Analysis"
        page = "Resume Analysis"
    load_page(SEEKER_PAGES[page])

elif st.session_state.brain_mode == "employee":
    page = st.session_state.employee_page
    if page not in EMPLOYEE_PAGES:
        st.session_state.employee_page = "Learning Companion"
        page = "Learning Companion"
    load_page(EMPLOYEE_PAGES[page])
