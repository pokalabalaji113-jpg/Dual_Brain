"""
pages/burnout_intelligence.py
Employee Brain — AI burnout detection + recovery plan.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import json
from utils.llm_client import call_llm


def analyze_burnout(responses: dict) -> dict:
    prompt = f"""
Analyze burnout risk:
Work hours/day: {responses['hours']}
Sleep hours: {responses['sleep']}
Work-life balance (1-10): {responses['balance']}
Overwhelmed (1-10): {responses['overwhelmed']}
Motivation (1-10): {responses['motivation']}
Active projects: {responses['projects']}
Weeks since vacation: {responses['vacation']}
Physical symptoms: {responses['physical']}
Feelings: {responses['feelings']}

Return ONLY this JSON:
{{
  "burnout_score": 65,
  "risk_level": "moderate",
  "detected_patterns": ["pattern1","pattern2","pattern3"],
  "physical_signals": ["signal1","signal2"],
  "mental_signals": ["signal1","signal2"],
  "immediate_actions": ["action1","action2","action3"],
  "weekly_schedule": [
    {{"day":"Monday","work_hours":8,"break_minutes":30,"recovery_activity":"30min walk"}}
  ],
  "long_term_strategies": ["strategy1","strategy2","strategy3"],
  "talk_to_manager_script": "Hi [Manager], I wanted to discuss my current workload...",
  "learning_pause_recommended": false,
  "recovery_timeline_weeks": 3
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
    st.markdown("## 🔥 Burnout & Workload Intelligence")
    st.markdown("Powered by **LangChain + Groq LLaMA 3.3 70B**")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        hours      = st.slider("Work hours/day",            4, 18, 8)
        sleep      = st.slider("Sleep hours/night",         3, 12, 7)
        balance    = st.slider("Work-life balance (1-10)",  1, 10, 5)
        overwhelmed= st.slider("Feeling overwhelmed (1-10)",1, 10, 5)
        motivation = st.slider("Motivation level (1-10)",   1, 10, 6)
    with col2:
        projects = st.number_input("Active projects right now", 1, 20, 3)
        vacation = st.number_input("Weeks since last break",    0, 52, 4)
        physical = st.multiselect("Physical symptoms",
            ["Headaches","Back/neck pain","Eye strain","Fatigue",
             "Poor appetite","Insomnia","None"], default=["None"])
        feelings = st.text_area("How are you feeling?",
            placeholder="Describe in your own words...", height=100)

    if st.button("🔍 Analyze My Burnout Risk", type="primary", use_container_width=True):
        with st.spinner("Analyzing patterns..."):
            result = analyze_burnout({
                "hours": hours, "sleep": sleep, "balance": balance,
                "overwhelmed": overwhelmed, "motivation": motivation,
                "projects": projects, "vacation": vacation,
                "physical": ", ".join(physical), "feelings": feelings,
            })
        st.session_state.burnout_result = result

    result = st.session_state.get("burnout_result")
    if not result:
        st.info("Complete the assessment above.")
        return
    if "error" in result:
        st.error("Analysis failed. Try again.")
        return

    score = result.get("burnout_score", 0)
    risk  = result.get("risk_level", "unknown")
    colors = {"low":"#2d9e2d","moderate":"#e07000","high":"#cc4400","critical":"#cc0000"}
    bgs    = {"low":"#f0fff0","moderate":"#fff8e0","high":"#fff0e0","critical":"#fff0f0"}
    color  = colors.get(risk, "#666")
    bg     = bgs.get(risk, "#f8f8f8")

    st.markdown(f"""
    <div style="background:{bg};border:2px solid {color};border-radius:12px;
                padding:20px;margin-bottom:20px;">
        <div style="font-size:2.5rem;font-weight:900;color:{color};">{score}/100</div>
        <div style="font-size:1.1rem;font-weight:700;color:{color};text-transform:uppercase;">
            {risk.upper()} BURNOUT RISK
        </div>
        <div style="color:#444;margin-top:8px;">
            Recovery timeline: {result.get('recovery_timeline_weeks','?')} weeks
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Patterns", "Recovery Plan", "Weekly Schedule", "Manager Script"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🧠 Mental Signals**")
            for s in result.get("mental_signals", []):   st.markdown(f"- {s}")
            st.markdown("**🔴 Detected Patterns**")
            for p in result.get("detected_patterns", []): st.markdown(f"- {p}")
        with c2:
            st.markdown("**🏥 Physical Signals**")
            for s in result.get("physical_signals", []): st.markdown(f"- {s}")
        if result.get("learning_pause_recommended"):
            st.warning("⚠️ AI Recommends: Pause new learning. Focus on recovery first.")

    with tab2:
        st.markdown("**⚡ Do These Today**")
        for a in result.get("immediate_actions", []):    st.markdown(f"- {a}")
        st.markdown("**📅 Long-term Strategies**")
        for s in result.get("long_term_strategies", []): st.markdown(f"- {s}")

    with tab3:
        for day in result.get("weekly_schedule", []):
            st.markdown(
                f"**{day.get('day')}:** Work {day.get('work_hours','?')}h | "
                f"Breaks {day.get('break_minutes','?')}min | "
                f"Recovery: {day.get('recovery_activity','rest')}"
            )

    with tab4:
        script = result.get("talk_to_manager_script", "")
        if script:
            st.markdown("Use this to talk to your manager about workload:")
            st.text_area("Manager Script", value=script, height=200)
