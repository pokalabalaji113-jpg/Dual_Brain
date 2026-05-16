"""
pages/performance_analyzer.py
Employee Brain — Performance analysis + promotion readiness + resume improvement.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import json
from utils.llm_client import call_llm


def analyze_performance(data: dict) -> dict:
    prompt = f"""
Analyze employee performance:
Role: {data['role']} | Experience: {data['experience']} years
Achievements: {data['achievements']}
Daily skills: {data['daily_skills']}
Unused skills: {data['unused_skills']}
Projects: {data['projects']}
Self-rating: {data['self_rating']}/10
Manager feedback: {data['manager_feedback']}
Goals: {data['goals']}
Blockers: {data['blockers']}

Return ONLY this JSON:
{{
  "performance_score": 75,
  "growth_velocity": "steady",
  "top_strengths": ["s1","s2","s3"],
  "improvement_areas": [
    {{"area":"area name","impact":"high","how_to_improve":"specific action"}}
  ],
  "skill_utilization": {{
    "well_used": ["skill1","skill2"],
    "underutilized": ["skill1"],
    "should_learn": ["skill1","skill2"]
  }},
  "resume_improvements": [
    "Add quantified achievements like reduced load time by X%",
    "Add missing skills section",
    "Include certifications",
    "Improve summary section",
    "Add GitHub/portfolio links"
  ],
  "quarterly_goals_assessment": "assessment paragraph",
  "promotion_readiness": 65,
  "promotion_gaps": ["gap1","gap2"],
  "recommended_actions": [
    {{"action":"specific action","timeline":"this week","impact":"expected result"}}
  ],
  "peer_comparison_insight": "insight paragraph"
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
    st.markdown("## 📈 Performance Analyzer")
    st.markdown("Powered by **LangChain + Groq LLaMA 3.3 70B**")
    st.markdown("---")

    with st.form("perf_form"):
        c1, c2 = st.columns(2)
        with c1:
            role         = st.text_input("Your role",          placeholder="Senior Frontend Developer")
            experience   = st.number_input("Years in role",    0, 20, 1)
            self_rating  = st.slider("Self rating (1-10)",     1, 10, 7)
            daily_skills = st.text_input("Daily skills",       placeholder="React, TypeScript, GraphQL")
            unused_skills= st.text_input("Rarely used skills", placeholder="Python, AWS")
        with c2:
            achievements   = st.text_area("Key achievements this quarter",
                placeholder="Shipped login redesign, reduced load time by 40%", height=90)
            projects       = st.text_area("Recent projects",
                placeholder="Payment gateway, mobile app rewrite", height=70)
            manager_feedback= st.text_area("Manager feedback",
                placeholder="Good technical skills, needs better communication", height=70)
            goals    = st.text_input("Goals next quarter", placeholder="Get promoted, learn system design")
            blockers = st.text_input("Blockers",           placeholder="Too many meetings, unclear requirements")

        submitted = st.form_submit_button("📊 Analyze Performance", type="primary", use_container_width=True)

    if submitted:
        with st.spinner("Analyzing your performance..."):
            result = analyze_performance({
                "role": role, "experience": experience, "self_rating": self_rating,
                "daily_skills": daily_skills, "unused_skills": unused_skills,
                "achievements": achievements, "projects": projects,
                "manager_feedback": manager_feedback, "goals": goals, "blockers": blockers,
            })
        st.session_state.perf_result = result

    result = st.session_state.get("perf_result")
    if not result:
        st.info("Fill the form above to get your performance analysis.")
        return
    if "error" in result:
        st.error("Analysis failed. Try again.")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Performance Score",   f"{result.get('performance_score',0)}/100")
    with c2: st.metric("Promotion Readiness", f"{result.get('promotion_readiness',0)}%")
    with c3: st.metric("Growth Velocity",     result.get("growth_velocity","—").capitalize())
    with c4: st.metric("Improvement Areas",   len(result.get("improvement_areas",[])))

    st.markdown("---")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Strengths & Gaps", "Skills", "Resume Improvements", "Action Plan", "Promotion Path"
    ])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**✅ Top Strengths**")
            for s in result.get("top_strengths", []): st.markdown(f"- {s}")
        with c2:
            st.markdown("**📈 Improvement Areas**")
            for a in result.get("improvement_areas", []):
                emoji = {"high":"🔴","medium":"🟡","low":"🟢"}.get(a.get("impact"),"⚪")
                st.markdown(f"{emoji} **{a['area']}** — {a['how_to_improve']}")
        st.info(result.get("quarterly_goals_assessment",""))
        st.markdown(f"*{result.get('peer_comparison_insight','')}*")

    with tab2:
        skills = result.get("skill_utilization", {})
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**✅ Well Used**")
            for s in skills.get("well_used",    []): st.markdown(f"- {s}")
        with c2:
            st.markdown("**⚠️ Underutilized**")
            for s in skills.get("underutilized",[]): st.markdown(f"- {s}")
        with c3:
            st.markdown("**📚 Should Learn**")
            for s in skills.get("should_learn", []):
                col_s, col_b = st.columns([2,1])
                with col_s: st.markdown(f"- {s}")
                with col_b:
                    if st.button("📺", key=f"sl_{s}"):
                        st.session_state.chip_skill  = s
                        st.session_state.brain_mode  = "seeker"
                        st.session_state.seeker_page = "Skill Videos"
                        st.rerun()

    with tab3:
        st.markdown("### 📄 Resume Improvement Suggestions")
        st.markdown("*Make these changes to boost your resume for promotion or job switch:*")
        for i, tip in enumerate(result.get("resume_improvements", []), 1):
            st.markdown(f"""
            <div style="background:#f8f8f8;border-left:4px solid #111;
                        padding:12px 16px;margin-bottom:8px;border-radius:0 8px 8px 0;">
                <b>{i}.</b> {tip}
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        tl_groups = {"this week":[], "this month":[], "this quarter":[]}
        for a in result.get("recommended_actions", []):
            tl = a.get("timeline","this month")
            if tl in tl_groups: tl_groups[tl].append(a)
        for period, actions in tl_groups.items():
            if actions:
                st.markdown(f"**{period.title()}**")
                for a in actions:
                    st.markdown(f"- **{a['action']}** → {a.get('impact','')}")

    with tab5:
        promo = result.get("promotion_readiness", 0)
        color = "#2d9e2d" if promo>=70 else "#e07000" if promo>=50 else "#cc2222"
        st.markdown(f'<div style="font-size:2rem;font-weight:800;color:{color};">{promo}% Promotion Ready</div>',
                    unsafe_allow_html=True)
        gaps = result.get("promotion_gaps", [])
        if gaps:
            st.markdown("**What's holding you back:**")
            for g in gaps: st.markdown(f"- {g}")
        else:
            st.success("You appear ready for the next level! Talk to your manager.")
