"""
pages/job_links.py
Job Seeker Brain — Top 5 jobs from LinkedIn + Naukri + cover letter generator.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.llm_client import call_llm


def generate_cover_letter(job_title: str, company: str, resume_data: dict) -> str:
    name   = resume_data.get("name", "the candidate") if resume_data else "the candidate"
    skills = ", ".join(resume_data.get("skills", [])[:6]) if resume_data else ""
    exp    = resume_data.get("experience_years", 0) if resume_data else 0
    prompt = f"""
Write a professional cover letter (3 paragraphs, under 250 words) for:
Job: {job_title} at {company}
Candidate: {name} | Experience: {exp} years | Skills: {skills}
Make it specific, professional, and compelling. No placeholders.
"""
    return call_llm(prompt)


def render():
    st.markdown("## 🔗 Job Links")
    st.markdown("Find top jobs from **LinkedIn & Naukri** based on your resume + role.")
    st.markdown("---")

    resume_data = st.session_state.get("resume_data", {})
    skills      = resume_data.get("skills", []) if resume_data else []
    default_role= st.session_state.get("job_role_target", "") or \
                  (resume_data.get("current_role","") if resume_data else "")

    c1, c2, c3 = st.columns([2,1,1])
    with c1: job_role = st.text_input("Job Role", value=default_role,
                                       placeholder="Data Scientist, ML Engineer")
    with c2: location = st.text_input("Location", value="India")
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("🔍 Find Jobs", type="primary", use_container_width=True)

    if skills:
        st.info(f"💡 Using skills from resume: {', '.join(skills[:5])}" +
                (" ..." if len(skills)>5 else ""))

    if search_btn and job_role:
        st.session_state.job_results       = _build_job_links(job_role, skills, location)
        st.session_state.job_role_searched = job_role

    jobs = st.session_state.get("job_results", [])
    if not jobs:
        st.info("Enter a job role and click Find Jobs.")
        return

    searched = st.session_state.get("job_role_searched", job_role)
    st.markdown(f"### Top Jobs for: **{searched}**")
    st.markdown("---")

    for i, job in enumerate(jobs, 1):
        st.markdown(f"""
        <div style="border:1px solid #e0e0e0;border-radius:10px;padding:16px;margin-bottom:12px;">
            <div style="font-size:1.05rem;font-weight:700;">{i}. {job['title']}</div>
            <div style="color:#444;font-size:0.88rem;margin-top:4px;">
                🏢 {job['company']} &nbsp;|&nbsp; 📍 {job['location']}
                &nbsp;|&nbsp; 💰 {job.get('salary','Not disclosed')}
                &nbsp;|&nbsp; 🕒 {job.get('posted','')}
            </div>
            <div style="color:#666;font-size:0.85rem;margin-top:8px;">{job['snippet']}</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1,1,2])
        with c1: st.link_button("🔗 Apply", job["link"], use_container_width=True)
        with c2:
            if st.button("✉ Cover Letter", key=f"cl_{i}", use_container_width=True):
                with st.spinner("Writing cover letter..."):
                    letter = generate_cover_letter(job["title"], job["company"], resume_data)
                st.session_state[f"cover_{i}"] = letter

        if st.session_state.get(f"cover_{i}"):
            with st.expander("📄 Cover Letter", expanded=True):
                st.text_area("Copy this:", value=st.session_state[f"cover_{i}"], height=250,
                             key=f"cl_text_{i}")

    st.markdown("---")
    st.markdown("""
    <div style="color:#999;font-size:0.8rem;">
    💡 Add SERPAPI_KEY to .streamlit/secrets.toml for real-time job data.
    Currently showing curated job links based on your role.
    </div>
    """, unsafe_allow_html=True)


def _build_job_links(job_role: str, skills: list, location: str) -> list:
    """Build job links for LinkedIn and Naukri."""
    enc_role   = job_role.replace(" ", "%20")
    enc_plus   = job_role.replace(" ", "+").lower()
    enc_loc    = location.replace(" ", "%20")
    skills_str = "+".join(skills[:3]) if skills else ""

    return [
        {
            "title":    f"{job_role} — LinkedIn (Last 24h)",
            "company":  "LinkedIn",
            "location": location,
            "salary":   "See listing",
            "posted":   "Today",
            "snippet":  f"Latest {job_role} openings posted in the last 24 hours on LinkedIn.",
            "link":     f"https://www.linkedin.com/jobs/search/?keywords={enc_role}&f_TPR=r86400&location={enc_loc}",
        },
        {
            "title":    f"{job_role} — Naukri.com",
            "company":  "Naukri",
            "location": location,
            "salary":   "Competitive",
            "posted":   "Today",
            "snippet":  f"Top {job_role} jobs on Naukri matching your profile.",
            "link":     f"https://www.naukri.com/{enc_plus}-jobs-in-{location.lower().replace(' ','-')}",
        },
        {
            "title":    f"Remote {job_role} — LinkedIn",
            "company":  "LinkedIn Remote",
            "location": "Remote",
            "salary":   "Negotiable",
            "posted":   "This week",
            "snippet":  f"Remote {job_role} opportunities — work from anywhere.",
            "link":     f"https://www.linkedin.com/jobs/search/?keywords={enc_role}&f_WT=2",
        },
        {
            "title":    f"{job_role} Fresher / Junior — Naukri",
            "company":  "Naukri",
            "location": "India",
            "salary":   "₹3-8 LPA",
            "posted":   "This week",
            "snippet":  f"Entry level {job_role} jobs for freshers and 0-2 years experience.",
            "link":     f"https://www.naukri.com/{enc_plus}-jobs?experience=0,2",
        },
        {
            "title":    f"Senior {job_role} — LinkedIn",
            "company":  "LinkedIn",
            "location": location,
            "salary":   "₹15-40 LPA",
            "posted":   "This week",
            "snippet":  f"Senior {job_role} roles for experienced professionals.",
            "link":     f"https://www.linkedin.com/jobs/search/?keywords=Senior+{enc_role}&location={enc_loc}",
        },
    ]
