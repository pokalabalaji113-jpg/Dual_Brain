"""
pages/resume_analysis.py
Job Seeker Brain — Full resume analysis with LangGraph pipeline.
Features: ATS score, skills, missing skills, resume improvement suggestions,
job role match, YouTube links for missing skills, LinkedIn/Naukri job links.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import json
from utils.resume_parser import extract_resume_text
from utils.llm_client import call_llm
from graph.seeker_graph import run_seeker_graph


def analyze_resume_detailed(resume_text: str, job_role: str = "") -> dict:
    role_hint = f"Target role: {job_role}." if job_role else ""
    prompt = f"""
Analyze this resume and return ONLY this JSON (no extra text):
{{
  "name": "candidate name",
  "email": "email or N/A",
  "phone": "phone or N/A",
  "current_role": "current or most recent job title",
  "experience_years": 0,
  "education": "highest degree and institution",
  "skills": ["skill1","skill2","skill3"],
  "strengths": ["strength1","strength2","strength3"],
  "weaknesses": ["weakness1","weakness2","weakness3"],
  "missing_skills": ["missing1","missing2","missing3"],
  "ats_score": 75,
  "ats_feedback": "Specific ATS optimization feedback paragraph",
  "resume_improvements": [
    "Specific improvement 1 to make resume stronger",
    "Specific improvement 2",
    "Specific improvement 3",
    "Specific improvement 4",
    "Specific improvement 5"
  ],
  "summary_feedback": "Professional 2-3 paragraph career feedback",
  "recommended_job_roles": ["role1","role2","role3"]
}}
{role_hint}
Resume text: {resume_text[:4000]}
Return ONLY valid JSON. No markdown, no explanation.
"""
    raw = call_llm(prompt)
    try:
        clean = raw.strip().strip("```json").strip("```").strip()
        return json.loads(clean)
    except Exception:
        return {"error": "Parse failed", "raw": raw}


def render():
    st.markdown("## 📄 Resume Analysis")
    st.markdown("Powered by **LangChain + LangGraph + Groq LLaMA 3.3 70B**")
    st.markdown("---")

    col1, col2 = st.columns([1.2, 1])
    with col1:
        uploaded = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
        job_role = st.text_input("Target Job Role (optional)", placeholder="e.g. Data Scientist, ML Engineer")
        analyze_btn = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)
    with col2:
        st.markdown("""
        **What you get:**
        - ✅ ATS compatibility score
        - ✅ Skills extracted automatically
        - ✅ Missing skills detection
        - ✅ Resume improvement suggestions
        - ✅ YouTube videos for missing skills
        - ✅ LinkedIn + Naukri job links
        - ✅ LangGraph multi-step AI pipeline
        - ✅ Cover letter generator
        """)

    st.markdown("---")

    if analyze_btn:
        if not uploaded:
            st.warning("Please upload a resume file.")
            return

        with st.spinner("Reading resume..."):
            resume_text = extract_resume_text(uploaded)

        if not resume_text:
            st.error("Could not extract text. Try PDF or DOCX format.")
            return

        st.session_state.resume_text       = resume_text
        st.session_state.job_role_target   = job_role

        with st.spinner("🔗 LangChain: Analyzing resume details..."):
            analysis = analyze_resume_detailed(resume_text, job_role)
        st.session_state.resume_data = analysis

        with st.spinner("🔁 LangGraph: Running 5-node agent pipeline..."):
            graph_result = run_seeker_graph(resume_text, job_role)
        st.session_state.graph_result = graph_result

        if "error" not in analysis:
            # Store missing skills for Skill Videos page
            st.session_state.missing_skills_focus = analysis.get("missing_skills", [])
            st.success("✅ Analysis complete!")

    # ── Display results ────────────────────────────────────────────────────────
    data = st.session_state.get("resume_data") or {}
    graph = st.session_state.get("graph_result") or {}

    if not data or not isinstance(data, dict) or "error" in data:
        if data.get("error"):
            st.error("Analysis failed. Try again.")
        return

    # Metrics row
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Candidate",    data.get("name", "—"))
    with c2: st.metric("ATS Score",    f"{data.get('ats_score', 0)}/100")
    with c3: st.metric("Experience",   f"{data.get('experience_years', 0)} yrs")
    with c4: st.metric("Current Role", data.get("current_role", "—")[:20])

    st.markdown("---")

    # Skills chips
    st.markdown("### 🛠 Skills Detected")
    skills = data.get("skills", [])
    if skills:
        html = " ".join([
            f'<span style="background:#f0f0f0;padding:3px 10px;border-radius:20px;'
            f'margin:3px;display:inline-block;font-size:0.85rem;">{s}</span>'
            for s in skills
        ])
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Analysis", "🔴 Missing Skills", "📈 Improvements", "🔁 LangGraph", "💼 Jobs", "📄 Roles"
    ])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**✅ Strengths**")
            for s in data.get("strengths", []):
                st.markdown(f"- {s}")
        with c2:
            st.markdown("**⚠️ Weaknesses**")
            for w in data.get("weaknesses", []):
                st.markdown(f"- {w}")
        st.markdown("---")
        score = data.get("ats_score", 0)
        color = "#2d9e2d" if score >= 70 else "#e07000" if score >= 50 else "#cc2222"
        st.markdown(f'<div style="font-size:2.5rem;font-weight:800;color:{color};">{score}/100 ATS Score</div>',
                    unsafe_allow_html=True)
        st.info(data.get("ats_feedback", ""))
        st.markdown("---")
        st.write(data.get("summary_feedback", ""))

    with tab2:
        missing = data.get("missing_skills", [])
        if missing:
            st.markdown("### 🔴 Missing Skills for Your Target Role")
            html = " ".join([
                f'<span style="background:#fff0f0;border:1px solid #ffcccc;padding:4px 12px;'
                f'border-radius:20px;margin:3px;display:inline-block;font-size:0.9rem;">{s}</span>'
                for s in missing
            ])
            st.markdown(html, unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("### 📺 Learn Missing Skills — YouTube Videos")
            for skill in missing:
                col_s, col_b = st.columns([2, 1])
                with col_s:
                    st.markdown(f"**{skill}**")
                with col_b:
                    if st.button(f"▶ Watch {skill}", key=f"yt_{skill}", use_container_width=True):
                        st.session_state.missing_skills_focus = [skill]
                        st.session_state.chip_skill           = skill
                        st.session_state.seeker_page          = "Skill Videos"
                        st.rerun()
            st.markdown("---")
            if st.button("📺 Load ALL Missing Skills in Skill Videos →", type="primary", use_container_width=True):
                st.session_state.missing_skills_focus = missing
                st.session_state.seeker_page          = "Skill Videos"
                st.rerun()
        else:
            st.success("✅ No major skill gaps detected for this role!")

    with tab3:
        st.markdown("### 📈 Resume Improvement Suggestions")
        st.markdown("*Make these changes to significantly improve your resume:*")
        improvements = data.get("resume_improvements", [])
        for i, tip in enumerate(improvements, 1):
            st.markdown(f"""
            <div style="background:#f8f8f8;border-left:4px solid #111;
                        padding:12px 16px;margin-bottom:8px;border-radius:0 8px 8px 0;">
                <b>{i}.</b> {tip}
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.markdown("### 🔁 LangGraph 5-Node Pipeline Results")
        st.info(graph.get("final_report", "Run analysis to see LangGraph report."))
        if graph.get("learning_path"):
            st.markdown("**📅 4-Week Learning Plan:**")
            st.write(graph.get("learning_path"))
        if graph.get("job_suggestions"):
            st.markdown("**💼 Suggested Job Titles:**")
            for j in graph.get("job_suggestions", []):
                st.markdown(f"- {j}")
        if graph.get("video_queries"):
            st.markdown("**📺 Recommended Video Searches:**")
            for q in graph.get("video_queries", []):
                col_q, col_b = st.columns([3, 1])
                with col_q:
                    st.markdown(f"- `{q}`")
                with col_b:
                    skill_name = q.replace(" tutorial for beginners", "")
                    if st.button("Watch", key=f"vq_{q[:20]}"):
                        st.session_state.chip_skill  = skill_name
                        st.session_state.seeker_page = "Skill Videos"
                        st.rerun()

    with tab5:
        st.markdown("### 💼 Job Links — LinkedIn & Naukri")
        job_role_val = st.session_state.get("job_role_target", "") or data.get("current_role", "Developer")
        skills_str   = "+".join(skills[:3]) if skills else ""
        encoded_role = job_role_val.replace(" ", "%20")
        encoded_role_plus = job_role_val.replace(" ", "+")

        st.markdown(f"""
        <div style="display:grid;gap:10px;">
            <a href="https://www.linkedin.com/jobs/search/?keywords={encoded_role}&f_TPR=r86400"
               target="_blank"
               style="background:#0a66c2;color:white;padding:12px 20px;border-radius:8px;
                      text-decoration:none;font-weight:600;display:block;text-align:center;">
               🔗 LinkedIn — {job_role_val} Jobs (Last 24h)
            </a>
            <a href="https://www.naukri.com/{encoded_role_plus.lower()}-jobs"
               target="_blank"
               style="background:#ff7555;color:white;padding:12px 20px;border-radius:8px;
                      text-decoration:none;font-weight:600;display:block;text-align:center;">
               🔗 Naukri — {job_role_val} Jobs
            </a>
            <a href="https://www.linkedin.com/jobs/search/?keywords={encoded_role}&location=India"
               target="_blank"
               style="background:#333;color:white;padding:12px 20px;border-radius:8px;
                      text-decoration:none;font-weight:600;display:block;text-align:center;">
               🔗 LinkedIn India — {job_role_val} Jobs
            </a>
            <a href="https://www.naukri.com/jobs-in-india?k={encoded_role_plus}"
               target="_blank"
               style="background:#555;color:white;padding:12px 20px;border-radius:8px;
                      text-decoration:none;font-weight:600;display:block;text-align:center;">
               🔗 Naukri — Search by Skills
            </a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🔍 Get Top 5 AI-Matched Jobs →", type="primary", use_container_width=True):
            st.session_state.seeker_page = "Job Links"
            st.rerun()

    with tab6:
        st.markdown("### 🎯 Recommended Job Roles")
        for i, role in enumerate(data.get("recommended_job_roles", []), 1):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.markdown(f"**{i}. {role}**")
            with c2:
                encoded = role.replace(" ", "%20")
                st.link_button("LinkedIn", f"https://www.linkedin.com/jobs/search/?keywords={encoded}")
            with c3:
                encoded2 = role.replace(" ", "+").lower()
                st.link_button("Naukri", f"https://www.naukri.com/{encoded2}-jobs")
