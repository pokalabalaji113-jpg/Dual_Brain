"""
pages/skill_assessment.py
Fixed: Duplicate button key error in weak areas video section.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import json
from utils.llm_client import call_llm
from utils.youtube_utils import search_youtube_videos, get_embed_html, get_transcript


def generate_quiz(domain: str, experience: int, skills: str) -> list:
    prompt = f"""
Generate exactly 10 multiple choice questions to assess a {domain} professional
with {experience} years experience. Their stated skills: {skills}

Make questions that genuinely test depth of knowledge — not surface level.
Mix easy (20%), medium (50%), hard (30%) questions.

Return ONLY this JSON array (no extra text):
[
  {{
    "question_number": 1,
    "question": "Question text here?",
    "options": {{
      "A": "Option A text",
      "B": "Option B text",
      "C": "Option C text",
      "D": "Option D text"
    }},
    "correct_answer": "A",
    "explanation": "Why A is correct",
    "topic": "Topic name this tests",
    "difficulty": "medium"
  }}
]
Make all 10 questions. Return ONLY valid JSON array.
"""
    raw = call_llm(prompt, max_tokens=3000)
    try:
        clean = raw.strip().strip("```json").strip("```").strip()
        data  = json.loads(clean)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def analyze_results(questions: list, answers: dict, domain: str) -> dict:
    correct      = 0
    wrong_topics = []
    for q in questions:
        qn  = str(q["question_number"])
        ans = answers.get(qn, "")
        if ans == q["correct_answer"]:
            correct += 1
        else:
            wrong_topics.append(q["topic"])

    total        = len(questions)
    score_pct    = int((correct / total) * 100) if total else 0
    wrong_unique = list(dict.fromkeys(wrong_topics))

    prompt = f"""
A {domain} professional scored {score_pct}% ({correct}/{total}) on a skill assessment.
Weak topics identified: {', '.join(wrong_unique) if wrong_unique else 'None'}

Return ONLY this JSON:
{{
  "verdict": "Genuine Expert|Partially Skilled|Needs Improvement|Skill Gap Detected",
  "credibility_score": {score_pct},
  "summary": "2-3 sentence honest assessment",
  "strong_areas": ["area1","area2"],
  "weak_areas": {json.dumps(wrong_unique[:5])},
  "recommendations": ["rec1","rec2","rec3"],
  "interview_readiness": "Ready|Almost Ready|Needs More Prep",
  "study_plan": "Specific 2-week study plan for weak areas"
}}
Return ONLY valid JSON.
"""
    raw = call_llm(prompt)
    try:
        clean  = raw.strip().strip("```json").strip("```").strip()
        result = json.loads(clean)
        result["correct"]      = correct
        result["total"]        = total
        result["score_pct"]    = score_pct
        result["wrong_topics"] = wrong_unique
        return result
    except Exception:
        return {
            "verdict": "Assessment Complete",
            "credibility_score": score_pct,
            "summary": f"Scored {correct}/{total} ({score_pct}%)",
            "strong_areas": [], "weak_areas": wrong_unique,
            "recommendations": [], "interview_readiness": "Needs More Prep",
            "study_plan": "", "correct": correct,
            "total": total, "score_pct": score_pct, "wrong_topics": wrong_unique,
        }


def render():
    st.markdown("## 🧪 Skill Assessment Quiz")
    st.markdown("Powered by **LangChain + Groq LLaMA 3.3 70B**")
    st.markdown("*10 AI-generated MCQ questions to verify your skills are genuine.*")
    st.markdown("---")

    if "quiz_state" not in st.session_state:
        st.session_state.quiz_state = "setup"

    # ── SETUP ──────────────────────────────────────────────────────────────────
    if st.session_state.quiz_state == "setup":
        st.markdown("### 📋 Configure Your Assessment")
        col1, col2 = st.columns(2)
        with col1:
            domain     = st.text_input("Your domain / role",
                placeholder="e.g. Machine Learning, Backend Development, GenAI")
            experience = st.selectbox("Years of experience",
                ["0-1 years (Fresher)", "1-3 years (Junior)",
                 "3-5 years (Mid)", "5+ years (Senior)"])
        with col2:
            skills = st.text_area("Your claimed skills",
                placeholder="Python, TensorFlow, LangChain, Docker, AWS", height=100)
            target = st.text_input("Target role / job applying for",
                placeholder="e.g. ML Engineer at Google")

        st.markdown("""
        <div style="background:#f8f8f8;border-left:4px solid #111;padding:12px 16px;border-radius:0 8px 8px 0;">
            <b>What this test does:</b><br>
            ✅ Generates 10 domain-specific MCQ questions<br>
            ✅ Detects if your claimed skills are genuine<br>
            ✅ Shows which topics need improvement<br>
            ✅ Gives YouTube videos for weak areas<br>
            ✅ Rates your interview readiness
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        if st.button("🚀 Start Assessment", type="primary", use_container_width=True):
            if not domain:
                st.warning("Enter your domain first.")
                return
            exp_map = {
                "0-1 years (Fresher)": 0, "1-3 years (Junior)": 2,
                "3-5 years (Mid)": 4,     "5+ years (Senior)": 6,
            }
            with st.spinner(f"Generating 10 questions for {domain}..."):
                questions = generate_quiz(domain, exp_map.get(experience, 2), skills)
            if not questions:
                st.error("Failed to generate questions. Try again.")
                return
            st.session_state.quiz_questions  = questions
            st.session_state.quiz_domain     = domain
            st.session_state.quiz_skills     = skills
            st.session_state.quiz_target     = target
            st.session_state.quiz_answers    = {}
            st.session_state.quiz_state      = "quiz"
            st.session_state.quiz_current_q  = 0
            st.rerun()

    # ── QUIZ ───────────────────────────────────────────────────────────────────
    elif st.session_state.quiz_state == "quiz":
        questions = st.session_state.get("quiz_questions", [])
        answers   = st.session_state.get("quiz_answers", {})
        current_q = st.session_state.get("quiz_current_q", 0)
        total     = len(questions)

        if not questions:
            st.error("No questions found. Restart.")
            st.session_state.quiz_state = "setup"
            st.rerun()

        progress = current_q / total
        st.progress(progress)
        st.markdown(f"**Question {current_q + 1} of {total}** — {st.session_state.quiz_domain}")
        st.markdown("---")

        q        = questions[current_q]
        diff_emoji = {"easy":"🟢","medium":"🟡","hard":"🔴"}.get(q.get("difficulty","medium"),"🟡")
        st.markdown(f"{diff_emoji} *{q.get('difficulty','medium').capitalize()} — Topic: {q.get('topic','')}*")
        st.markdown(f"### Q{q['question_number']}. {q['question']}")
        st.markdown("")

        options  = q.get("options", {})
        opt_list = [f"{k}: {v}" for k, v in options.items()]
        qn_key   = str(q["question_number"])
        prev_ans = answers.get(qn_key, None)
        prev_idx = None
        if prev_ans:
            for i, o in enumerate(opt_list):
                if o.startswith(prev_ans):
                    prev_idx = i
                    break

        selected = st.radio("Choose your answer:", opt_list,
                            index=prev_idx, key=f"q_radio_{current_q}")

        st.markdown("")
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if current_q > 0:
                if st.button("⬅ Previous", key="prev_btn", use_container_width=True):
                    if selected:
                        st.session_state.quiz_answers[qn_key] = selected[0]
                    st.session_state.quiz_current_q -= 1
                    st.rerun()
        with col2:
            if current_q < total - 1:
                if st.button("Next ➡", key="next_btn", type="primary", use_container_width=True):
                    if selected:
                        st.session_state.quiz_answers[qn_key] = selected[0]
                    st.session_state.quiz_current_q += 1
                    st.rerun()
            else:
                if st.button("✅ Submit Quiz", key="submit_btn", type="primary", use_container_width=True):
                    if selected:
                        st.session_state.quiz_answers[qn_key] = selected[0]
                    answered = len(st.session_state.quiz_answers)
                    if answered < total:
                        st.warning(f"Answered {answered}/{total}. Answer all before submitting.")
                    else:
                        st.session_state.quiz_state = "results"
                        st.rerun()
        with col3:
            answered = len(answers)
            st.markdown(f"*Answered: {answered}/{total}*")

        # Navigator
        st.markdown("---")
        st.markdown("**Progress:**")
        nav_cols = st.columns(10)
        for i, ques in enumerate(questions):
            qn = str(ques["question_number"])
            with nav_cols[i]:
                status = "✅" if qn in answers else ("📝" if i == current_q else "⬜")
                if st.button(status, key=f"nav_q_{i}", use_container_width=True):
                    if selected:
                        st.session_state.quiz_answers[qn_key] = selected[0]
                    st.session_state.quiz_current_q = i
                    st.rerun()

    # ── RESULTS ────────────────────────────────────────────────────────────────
    elif st.session_state.quiz_state == "results":
        questions = st.session_state.get("quiz_questions", [])
        answers   = st.session_state.get("quiz_answers", {})
        domain    = st.session_state.get("quiz_domain", "")

        with st.spinner("Analyzing your results..."):
            result = analyze_results(questions, answers, domain)

        score     = result.get("score_pct", 0)
        verdict   = result.get("verdict", "Assessment Complete")
        readiness = result.get("interview_readiness", "")
        correct   = result.get("correct", 0)
        total     = result.get("total", 10)

        color   = "#2d9e2d" if score>=70 else "#e07000" if score>=50 else "#cc2222"
        r_color = {"Ready":"#2d9e2d","Almost Ready":"#e07000",
                   "Needs More Prep":"#cc2222"}.get(readiness,"#666")

        st.markdown(f"""
        <div style="border:2px solid {color};border-radius:12px;padding:24px;
                    margin-bottom:20px;text-align:center;">
            <div style="font-size:3rem;font-weight:900;color:{color};">{score}%</div>
            <div style="font-size:1.3rem;font-weight:700;margin:8px 0;">{correct}/{total} Correct</div>
            <div style="font-size:1.1rem;color:{color};font-weight:600;">{verdict}</div>
            <div style="color:{r_color};margin-top:8px;font-weight:600;">
                Interview Readiness: {readiness}
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Results", "📝 Review Answers", "📺 Fix Weak Areas", "🎯 Study Plan"
        ])

        with tab1:
            st.info(result.get("summary",""))
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Strong Areas**")
                for s in result.get("strong_areas",[]): st.markdown(f"- {s}")
            with col2:
                st.markdown("**🔴 Weak Areas**")
                for w in result.get("weak_areas",[]):   st.markdown(f"- {w}")
            st.markdown("**💡 Recommendations**")
            for r in result.get("recommendations",[]): st.markdown(f"- {r}")

        with tab2:
            st.markdown("### 📝 Answer Review")
            for q in questions:
                qn          = str(q["question_number"])
                user_ans    = answers.get(qn, "Not answered")
                correct_ans = q["correct_answer"]
                is_correct  = user_ans == correct_ans
                emoji       = "✅" if is_correct else "❌"
                with st.expander(f"{emoji} Q{q['question_number']}: {q['question'][:70]}..."):
                    st.markdown(f"**Your answer:** {user_ans} — {q['options'].get(user_ans,'')}")
                    if not is_correct:
                        st.markdown(f"**Correct:** {correct_ans} — {q['options'].get(correct_ans,'')}")
                    st.markdown(f"**Explanation:** {q.get('explanation','')}")
                    st.markdown(f"*Topic: {q.get('topic','')} | Difficulty: {q.get('difficulty','')}*")

        with tab3:
            weak_areas = result.get("weak_areas", [])
            if weak_areas:
                st.markdown("### 📺 Videos for Your Weak Areas")
                # ── FIXED: unique key uses skill_index + video_index ──────────
                for skill_idx, skill in enumerate(weak_areas[:5]):
                    st.markdown(f"#### 🔴 {skill}")
                    with st.spinner(f"Finding videos for {skill}..."):
                        vids = search_youtube_videos(skill + " tutorial", max_results=2)
                    for vid_idx, v in enumerate(vids):
                        vid_id = v.get("video_id","")
                        if vid_id and not vid_id.startswith("SEARCH_"):
                            st.markdown(get_embed_html(vid_id, width=620, height=340),
                                        unsafe_allow_html=True)
                            st.markdown(f"**{v['title']}** — {v['channel']}")
                            # ── UNIQUE KEY: skill_idx + vid_idx (no vid_id) ───
                            chat_key = f"quiz_chat_s{skill_idx}_v{vid_idx}"
                            if st.button("💬 Chat about this video",
                                         key=chat_key, use_container_width=True):
                                with st.spinner("Loading transcript..."):
                                    t = get_transcript(vid_id)
                                st.session_state.current_video_transcript = t
                                st.session_state.current_video_url        = v["url"]
                                st.session_state.current_video_title      = v["title"]
                                st.session_state.chat_history             = []
                                st.session_state.brain_mode               = "seeker"
                                st.session_state.seeker_page              = "Video Chatbot"
                                st.rerun()
                            st.markdown("---")
                        else:
                            st.info(f"Add YOUTUBE_API_KEY for embedded '{skill}' videos.")
            else:
                st.success("🎉 No major weak areas! You are well prepared.")

        with tab4:
            st.markdown("### 🎯 Your Personalized Study Plan")
            st.write(result.get("study_plan",""))
            st.markdown("---")
            if st.button("🔁 Retake Quiz", type="primary", use_container_width=True):
                st.session_state.quiz_state     = "setup"
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers   = {}
                st.session_state.quiz_current_q = 0
                st.rerun()
