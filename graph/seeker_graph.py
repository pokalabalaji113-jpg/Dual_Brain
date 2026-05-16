"""
graph/seeker_graph.py
LangGraph agent for Job Seeker Brain.
Graph flow:
  extract_skills -> search_jobs -> generate_learning_path -> suggest_videos -> generate_report -> END
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from utils.llm_client import call_llm
import json


# ── State ──────────────────────────────────────────────────────────────────────
class SeekerState(TypedDict):
    resume_text: str
    job_role: str
    skills: List[str]
    missing_skills: List[str]
    job_suggestions: List[str]
    learning_path: str
    video_queries: List[str]
    final_report: str


# ── Nodes ──────────────────────────────────────────────────────────────────────
def extract_skills_node(state: SeekerState) -> SeekerState:
    prompt = f"""
Extract all technical and soft skills from this resume.
Target job role: {state.get('job_role', 'Software Developer')}
Resume: {state['resume_text'][:3000]}
Return ONLY this JSON:
{{"skills": ["skill1", "skill2"], "missing_skills": ["skill3", "skill4"]}}
"""
    raw = call_llm(prompt)
    try:
        clean = raw.strip().strip("```json").strip("```").strip()
        data = json.loads(clean)
        state["skills"] = data.get("skills", [])
        state["missing_skills"] = data.get("missing_skills", [])
    except Exception:
        state["skills"] = []
        state["missing_skills"] = []
    return state


def search_jobs_node(state: SeekerState) -> SeekerState:
    skills_str = ", ".join(state.get("skills", [])[:8])
    prompt = f"""
Based on skills: {skills_str}
Target role: {state.get('job_role', '')}
Suggest 5 specific job titles to apply for.
Return ONLY this JSON:
{{"jobs": ["Job Title 1", "Job Title 2", "Job Title 3", "Job Title 4", "Job Title 5"]}}
"""
    raw = call_llm(prompt)
    try:
        clean = raw.strip().strip("```json").strip("```").strip()
        data = json.loads(clean)
        state["job_suggestions"] = data.get("jobs", [])
    except Exception:
        state["job_suggestions"] = []
    return state


def generate_learning_path_node(state: SeekerState) -> SeekerState:
    missing = ", ".join(state.get("missing_skills", [])[:5])
    if not missing:
        state["learning_path"] = "No critical skill gaps found. You are well prepared!"
        return state
    prompt = f"""
Create a 4-week learning plan for: {missing}
Week by week, specific and actionable. Under 200 words.
"""
    state["learning_path"] = call_llm(prompt)
    return state


def suggest_videos_node(state: SeekerState) -> SeekerState:
    missing = state.get("missing_skills", [])[:5]
    state["video_queries"] = [f"{skill} tutorial for beginners" for skill in missing]
    return state


def generate_report_node(state: SeekerState) -> SeekerState:
    prompt = f"""
Write a 3-4 sentence career readiness report as a professional coach:
Skills: {', '.join(state.get('skills', [])[:6])}
Missing: {', '.join(state.get('missing_skills', [])[:4])}
Suggested jobs: {', '.join(state.get('job_suggestions', []))}
Be encouraging, specific, and actionable.
"""
    state["final_report"] = call_llm(prompt)
    return state


# ── Graph builder ──────────────────────────────────────────────────────────────
def build_seeker_graph():
    graph = StateGraph(SeekerState)
    graph.add_node("extract_skills", extract_skills_node)
    graph.add_node("search_jobs", search_jobs_node)
    graph.add_node("generate_learning_path", generate_learning_path_node)
    graph.add_node("suggest_videos", suggest_videos_node)
    graph.add_node("generate_report", generate_report_node)
    graph.set_entry_point("extract_skills")
    graph.add_edge("extract_skills", "search_jobs")
    graph.add_edge("search_jobs", "generate_learning_path")
    graph.add_edge("generate_learning_path", "suggest_videos")
    graph.add_edge("suggest_videos", "generate_report")
    graph.add_edge("generate_report", END)
    return graph.compile()


def run_seeker_graph(resume_text: str, job_role: str = "") -> SeekerState:
    app = build_seeker_graph()
    result = app.invoke(SeekerState(
        resume_text=resume_text,
        job_role=job_role,
        skills=[],
        missing_skills=[],
        job_suggestions=[],
        learning_path="",
        video_queries=[],
        final_report="",
    ))
    return result
