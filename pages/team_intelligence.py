"""
pages/team_intelligence.py
Employee Brain — Team collaboration intelligence.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import json
from utils.llm_client import call_llm


def analyze_team(data: dict) -> dict:
    prompt = f"""
Analyze team collaboration:
Team size: {data['team_size']} | Your role: {data['your_role']}
Tools: {data['tools']} | Meetings/week: {data['meetings']}h
Challenges: {data['challenges']} | Strengths: {data['strengths']}
Conflicts: {data['conflicts']} | Pace: {data['pace']} | Mode: {data['work_mode']}

Return ONLY this JSON:
{{
  "team_health_score": 72,
  "collaboration_efficiency": "medium",
  "communication_patterns": [
    {{"pattern":"name","observation":"detail","severity":"good"}}
  ],
  "bottlenecks": ["bottleneck1","bottleneck2"],
  "quick_wins": ["win1","win2","win3"],
  "team_rituals_to_add": [
    {{"ritual":"Daily Standup","frequency":"daily","purpose":"sync","duration_minutes":15}}
  ],
  "individual_actions": ["action1","action2"],
  "tools_to_try": ["Notion for docs","Loom for async updates"],
  "communication_tips": ["tip1","tip2","tip3"]
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
    st.markdown("## 👥 Team Intelligence System")
    st.markdown("Powered by **LangChain + Groq LLaMA 3.3 70B**")
    st.markdown("---")

    with st.form("team_form"):
        c1, c2 = st.columns(2)
        with c1:
            team_size  = st.number_input("Team size",        2, 50, 5)
            your_role  = st.selectbox("Your role in team",
                ["Team Member","Tech Lead","Engineering Manager","Scrum Master","Other"])
            meetings   = st.slider("Meeting hours/week",     0, 40, 8)
            pace       = st.selectbox("Delivery pace",
                ["Behind schedule","On track","Ahead of schedule"])
            work_mode  = st.selectbox("Work mode",           ["Remote","Hybrid","In-office"])
        with c2:
            tools      = st.text_input("Communication tools",placeholder="Slack, Jira, GitHub, Zoom")
            strengths  = st.text_area("Team strengths",      placeholder="Strong technical skills", height=70)
            challenges = st.text_area("Collaboration challenges",
                placeholder="Unclear ownership, too many meetings",  height=70)
            conflicts  = st.text_area("Recent conflicts",
                placeholder="Disagreements on architecture",         height=70)

        submitted = st.form_submit_button("🔍 Analyze Team", type="primary", use_container_width=True)

    if submitted:
        with st.spinner("Analyzing team dynamics..."):
            result = analyze_team({
                "team_size": team_size, "your_role": your_role, "meetings": meetings,
                "pace": pace, "work_mode": work_mode, "tools": tools,
                "strengths": strengths, "challenges": challenges, "conflicts": conflicts,
            })
        st.session_state.team_result = result

    result = st.session_state.get("team_result")
    if not result:
        st.info("Fill the form above to analyze your team.")
        return
    if "error" in result:
        st.error("Analysis failed. Try again.")
        return

    score = result.get("team_health_score", 0)
    eff   = result.get("collaboration_efficiency","—")
    color = "#2d9e2d" if score>=70 else "#e07000" if score>=50 else "#cc2222"

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Team Health Score",        f"{score}/100")
    with c2: st.metric("Collaboration Efficiency", eff.capitalize())
    with c3: st.metric("Bottlenecks Found",        len(result.get("bottlenecks",[])))

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["Patterns & Bottlenecks","Action Plan","Team Rituals"])

    with tab1:
        st.markdown("**🔍 Communication Patterns**")
        for p in result.get("communication_patterns",[]):
            emoji = {"good":"✅","neutral":"ℹ️","bad":"⚠️"}.get(p.get("severity"),"ℹ️")
            st.markdown(f"{emoji} **{p['pattern']}:** {p['observation']}")
        st.markdown("---")
        st.markdown("**🚧 Bottlenecks**")
        for b in result.get("bottlenecks",[]): st.markdown(f"- {b}")

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**⚡ Quick Wins**")
            for w in result.get("quick_wins",[]): st.markdown(f"- {w}")
            st.markdown("**🧑 What YOU Can Do**")
            for a in result.get("individual_actions",[]): st.markdown(f"- {a}")
        with c2:
            st.markdown("**💡 Tools to Try**")
            for t in result.get("tools_to_try",[]): st.markdown(f"- {t}")
            st.markdown("**📢 Communication Tips**")
            for tip in result.get("communication_tips",[]): st.markdown(f"- {tip}")

    with tab3:
        for ritual in result.get("team_rituals_to_add",[]):
            with st.expander(f"📅 {ritual['ritual']} ({ritual['frequency']}, {ritual.get('duration_minutes','?')}min)"):
                st.markdown(f"**Purpose:** {ritual['purpose']}")
