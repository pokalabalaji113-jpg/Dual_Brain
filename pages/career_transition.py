"""
pages/career_transition.py
Employee Brain — Dynamic Career Transition Engine.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import json
from utils.llm_client import call_llm
from utils.youtube_utils import search_youtube_videos, get_embed_html


def generate_transition_plan(from_role, to_role, experience, current_skills) -> dict:
    prompt = f"""
Career transition plan:
FROM: {from_role} ({experience} years)  TO: {to_role}
Current skills: {current_skills}

Return ONLY this JSON:
{{
  "feasibility_score": 75,
  "feasibility_reason": "reason",
  "estimated_weeks": 16,
  "skill_overlap": ["skill1","skill2"],
  "new_skills_required": [
    {{"skill":"name","priority":"high","weeks_to_learn":4}}
  ],
  "learning_phases": [
    {{"phase":1,"name":"Foundation","duration_weeks":4,"focus":"what to learn","projects":["project1"]}}
  ],
  "interview_prep": {{
    "key_topics": ["topic1","topic2"],
    "practice_questions": ["q1","q2"],
    "portfolio_projects": ["proj1","proj2"]
  }},
  "salary_change": "20-30% increase expected",
  "companies_hiring": ["Startup","Product company","MNC"],
  "success_tips": ["tip1","tip2","tip3"]
}}
Return ONLY valid JSON.
"""
    raw = call_llm(prompt)
    try:
        clean = raw.strip().strip("```json").strip("```").strip()
        return json.loads(clean)
    except Exception:
        return {"error": raw}


def render():
    st.markdown("## 🔀 Career Transition Engine")
    st.markdown("Powered by **LangChain + Groq LLaMA 3.3 70B**")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1: from_role   = st.text_input("Current role",   placeholder="Backend Developer")
    with col2: to_role     = st.text_input("Target role",    placeholder="GenAI Engineer")
    with col3: experience  = st.number_input("Years exp",    0, 30, 2)
    current_skills = st.text_input("Current skills", placeholder="Python, Django, SQL, Docker")

    # Presets
    st.markdown("**Popular transitions:**")
    presets = [
        ("Backend → GenAI",     "Backend Developer",     "GenAI Engineer"),
        ("Dev → ML",            "Software Developer",    "ML Engineer"),
        ("ML → MLOps",          "ML Engineer",           "MLOps Engineer"),
        ("Frontend → FullStack","Frontend Developer",    "Full Stack Developer"),
        ("Dev → Tech Lead",     "Software Engineer",     "Technical Lead"),
    ]
    cols = st.columns(len(presets))
    for i, (label, fr, to) in enumerate(presets):
        with cols[i]:
            if st.button(label, key=f"preset_{i}"):
                st.session_state.ct_from = fr
                st.session_state.ct_to   = to
                st.rerun()

    from_role = st.session_state.get("ct_from", from_role)
    to_role   = st.session_state.get("ct_to",   to_role)

    if st.button("🔀 Generate Transition Plan", type="primary", use_container_width=True):
        if not from_role or not to_role:
            st.warning("Enter both current and target role.")
            return
        with st.spinner(f"Planning {from_role} → {to_role} transition..."):
            plan = generate_transition_plan(from_role, to_role, experience, current_skills)
        st.session_state.transition_plan = plan

    plan = st.session_state.get("transition_plan")
    if not plan: 
        st.info("Enter roles and click Generate.")
        return
    if "error" in plan:
        st.error("Generation failed. Try again.")
        return

    score = plan.get("feasibility_score", 0)
    color = "#2d9e2d" if score>=70 else "#e07000" if score>=50 else "#cc2222"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:20px;padding:16px;
                border:1px solid #e0e0e0;border-radius:10px;margin-bottom:16px;">
        <div style="font-size:2.5rem;font-weight:900;color:{color};">{score}%</div>
        <div>
            <div style="font-weight:700;">Transition Feasibility</div>
            <div style="color:#666;font-size:0.85rem;">{plan.get('feasibility_reason','')}</div>
        </div>
        <div style="margin-left:auto;text-align:right;">
            <b>⏱ {plan.get('estimated_weeks','?')} weeks</b><br>
            <small>{plan.get('salary_change','')}</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Skills Gap", "Learning Phases", "Interview Prep", "Resources"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**✅ Skills That Transfer**")
            for s in plan.get("skill_overlap", []):
                st.markdown(f"- {s}")
        with c2:
            st.markdown("**📚 New Skills Needed**")
            for s in sorted(plan.get("new_skills_required", []),
                           key=lambda x: {"high":0,"medium":1,"low":2}.get(x.get("priority"),1)):
                emoji = {"high":"🔴","medium":"🟡","low":"🟢"}.get(s.get("priority"),"⚪")
                col_s, col_b = st.columns([2,1])
                with col_s:
                    st.markdown(f"{emoji} **{s['skill']}** — {s.get('weeks_to_learn','?')} weeks")
                with col_b:
                    if st.button("📺", key=f"ts_{s['skill']}"):
                        st.session_state.chip_skill  = s['skill']
                        st.session_state.brain_mode  = "seeker"
                        st.session_state.seeker_page = "Skill Videos"
                        st.rerun()

    with tab2:
        for phase in plan.get("learning_phases", []):
            with st.expander(f"Phase {phase['phase']}: {phase['name']} ({phase.get('duration_weeks','?')} weeks)"):
                st.markdown(f"**Focus:** {phase['focus']}")
                for proj in phase.get("projects", []):
                    st.markdown(f"- 🛠 {proj}")
                if st.button("📺 Find Videos", key=f"phase_v_{phase['phase']}"):
                    with st.spinner("Searching..."):
                        vids = search_youtube_videos(phase["focus"], max_results=2)
                    for v in vids:
                        vid_id = v.get("video_id","")
                        if vid_id:
                            st.markdown(get_embed_html(vid_id, width=580, height=320), unsafe_allow_html=True)
                            st.markdown(f"**{v['title']}** — {v['channel']}")

    with tab3:
        ip = plan.get("interview_prep", {})
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**📌 Key Topics**")
            for t in ip.get("key_topics", []):      st.markdown(f"- {t}")
            st.markdown("**💼 Portfolio Projects**")
            for p in ip.get("portfolio_projects",[]): st.markdown(f"- {p}")
        with c2:
            st.markdown("**❓ Practice Questions**")
            for q in ip.get("practice_questions",[]): st.markdown(f"- {q}")

    with tab4:
        st.markdown("**🏢 Companies Hiring**")
        for c in plan.get("companies_hiring", []): st.markdown(f"- {c}")
        st.markdown("**💡 Success Tips**")
        for tip in plan.get("success_tips", []):   st.markdown(f"- {tip}")
        enc = to_role.replace(" ", "%20")
        st.markdown("**🔗 Apply Now:**")
        st.link_button("LinkedIn Jobs", f"https://www.linkedin.com/jobs/search/?keywords={enc}")
        st.link_button("Naukri Jobs",   f"https://www.naukri.com/{to_role.replace(' ','+').lower()}-jobs")
