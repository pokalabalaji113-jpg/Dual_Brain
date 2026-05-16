"""
pages/learning_companion.py
Employee Brain — LangGraph 5-node pipeline + full features.
Features: Dynamic roadmap, skill gaps, burnout check, career advice, companion chat.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils.llm_client import call_llm, call_llm_with_history
from graph.employee_graph import run_employee_graph


def render():
    st.markdown("## 🤖 AI Learning Companion")
    st.markdown("Powered by **LangGraph 5-Node Agent + LangChain + Groq LLaMA 3.3 70B**")
    st.markdown("---")

    # ── Profile form ───────────────────────────────────────────────────────────
    with st.expander("👤 Your Employee Profile", expanded=not st.session_state.get("emp_profile_saved")):
        col1, col2 = st.columns(2)
        with col1:
            current_role  = st.text_input("Current role",     placeholder="e.g. Backend Developer")
            company_stack = st.text_area( "Company tech stack", placeholder="Python, Django, PostgreSQL, AWS", height=80)
            work_hours    = st.slider("Work hours/day", 4, 16, 8)
            experience    = st.number_input("Years of experience", 0, 20, 2)
        with col2:
            target_role   = st.text_input("Target role / promotion", placeholder="e.g. Senior Dev, Tech Lead")
            completed_certs = st.text_area("Completed certifications", placeholder="AWS SAA, Python PCEP", height=60)
            weak_areas    = st.multiselect("Known weak areas", [
                "System Design", "Algorithms & DS", "Cloud Architecture",
                "Leadership", "Communication", "Frontend", "DevOps",
                "Security", "Testing", "Documentation", "GenAI/LLM"
            ])

        if st.button("🔁 Run LangGraph Agent Pipeline", type="primary", use_container_width=True):
            if not current_role or not target_role:
                st.warning("Please enter current role and target role.")
                return

            profile = {
                "current_role": current_role, "target_role": target_role,
                "company_stack": company_stack, "weak_areas": weak_areas,
                "work_hours": work_hours, "experience": experience,
                "completed_certs": completed_certs,
            }
            st.session_state.emp_profile      = profile
            st.session_state.emp_profile_saved = True

            with st.spinner("🔁 LangGraph running 5-node pipeline: Profile → Gaps → Roadmap → Burnout → Advice..."):
                result = run_employee_graph(
                    current_role=current_role,
                    target_role=target_role,
                    company_stack=company_stack,
                    weak_areas=weak_areas,
                    work_hours=work_hours,
                )
            st.session_state.emp_graph_result = result
            st.success("✅ LangGraph pipeline complete!")
            st.rerun()

    # ── LangGraph Results ──────────────────────────────────────────────────────
    result  = st.session_state.get("emp_graph_result")
    profile = st.session_state.get("emp_profile", {})

    if result:
        st.markdown("### 🔁 LangGraph Agent Results")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Current Role", profile.get("current_role", "—"))
        with c2: st.metric("Target Role",  profile.get("target_role",  "—"))
        with c3: st.metric("Skill Gaps",   len(result.get("skill_gaps", [])))

        st.markdown("---")
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👤 Profile Summary", "🔴 Skill Gaps", "🗺 3-Month Roadmap", "🔥 Burnout Check", "💡 Career Advice"
        ])

        with tab1:
            st.info(result.get("profile_summary", ""))
            if profile.get("completed_certs"):
                st.markdown(f"**✅ Certifications:** {profile['completed_certs']}")
            if profile.get("weak_areas"):
                st.markdown(f"**⚠️ Weak Areas:** {', '.join(profile['weak_areas'])}")

        with tab2:
            gaps = result.get("skill_gaps", [])
            st.markdown(f"**{len(gaps)} skill gaps identified to reach {profile.get('target_role', 'target role')}:**")
            for g in gaps:
                col_g, col_v, col_l = st.columns([2, 1, 1])
                with col_g:
                    st.markdown(f"- **{g}**")
                with col_v:
                    if st.button("📺 Videos", key=f"gap_v_{g}"):
                        st.session_state.chip_skill  = g
                        st.session_state.brain_mode  = "seeker"
                        st.session_state.seeker_page = "Skill Videos"
                        st.rerun()
                with col_l:
                    enc = g.replace(" ", "%20")
                    st.link_button("📚 Course", f"https://www.coursera.org/search?query={enc}")

        with tab3:
            st.write(result.get("roadmap", ""))

        with tab4:
            burnout = result.get("burnout_risk", "")
            hours   = profile.get("work_hours", 8)
            color   = "#fff0f0" if hours >= 10 else "#fff8e1" if hours >= 8 else "#f0fff0"
            st.markdown(f"""
            <div style="background:{color};padding:16px;border-radius:8px;margin-bottom:12px;">
                <b>Work Hours/Day:</b> {hours}h<br><br>
                {burnout}
            </div>
            """, unsafe_allow_html=True)
            if hours >= 10:
                st.warning("⚠️ High workload detected! Go to **Burnout Intelligence** for a full recovery plan.")
                if st.button("🔥 Open Burnout Intelligence →"):
                    st.session_state.employee_page = "Burnout Intelligence"
                    st.rerun()

        with tab5:
            st.write(result.get("career_advice", ""))
            st.markdown("---")
            if st.button("🔀 Want to switch roles? Open Career Transition Engine →", use_container_width=True):
                st.session_state.employee_page = "Career Transition"
                st.rerun()

    # ── Companion Chat ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💬 Learning Companion Chat")
    st.markdown("*Ask anything about your learning journey, skills, or career growth.*")

    if "lc_history" not in st.session_state:
        st.session_state.lc_history = []

    for msg in st.session_state.lc_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_msg = st.chat_input("Ask your companion anything...")
    if user_msg:
        st.session_state.lc_history.append({"role": "user", "content": user_msg})
        with st.chat_message("user"):
            st.markdown(user_msg)

        system_ctx = f"""You are an expert AI learning companion for an employee.
Profile: Current={profile.get('current_role','')}, Target={profile.get('target_role','')},
Stack={profile.get('company_stack','')}, Weak areas={profile.get('weak_areas',[])}
Give specific, actionable advice. Be encouraging and practical."""

        history = [{"role": "user", "content": system_ctx}] + st.session_state.lc_history

        with st.chat_message("assistant"):
            with st.spinner(""):
                resp = call_llm_with_history(history)
            st.markdown(resp)

        st.session_state.lc_history.append({"role": "assistant", "content": resp})
        st.rerun()

    if st.session_state.lc_history:
        if st.button("🗑 Clear Chat"):
            st.session_state.lc_history = []
            st.rerun()
