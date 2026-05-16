"""
graph/employee_graph.py
LangGraph agent for Employee Brain.
Graph flow:
  analyze_profile -> detect_skill_gaps -> generate_roadmap -> check_burnout -> career_advice -> END
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from utils.llm_client import call_llm
import json


# ── State ──────────────────────────────────────────────────────────────────────
class EmployeeState(TypedDict):
    current_role: str
    target_role: str
    company_stack: str
    weak_areas: List[str]
    work_hours: int
    profile_summary: str
    skill_gaps: List[str]
    roadmap: str
    burnout_risk: str
    career_advice: str


# ── Nodes ──────────────────────────────────────────────────────────────────────
def analyze_profile_node(state: EmployeeState) -> EmployeeState:
    prompt = f"""
Analyze this employee profile in 2-3 sentences:
Current Role: {state.get('current_role')}
Target Role: {state.get('target_role')}
Company Stack: {state.get('company_stack')}
Weak Areas: {', '.join(state.get('weak_areas', []))}
Be professional and insightful.
"""
    state["profile_summary"] = call_llm(prompt)
    return state


def detect_skill_gaps_node(state: EmployeeState) -> EmployeeState:
    prompt = f"""
Identify top 5 skill gaps to move from {state.get('current_role')} to {state.get('target_role')}.
Company stack: {state.get('company_stack')}
Known weak areas: {', '.join(state.get('weak_areas', []))}
Return ONLY this JSON:
{{"gaps": ["gap1", "gap2", "gap3", "gap4", "gap5"]}}
"""
    raw = call_llm(prompt)
    try:
        clean = raw.strip().strip("```json").strip("```").strip()
        data = json.loads(clean)
        state["skill_gaps"] = data.get("gaps", [])
    except Exception:
        state["skill_gaps"] = []
    return state


def generate_roadmap_node(state: EmployeeState) -> EmployeeState:
    gaps = ", ".join(state.get("skill_gaps", []))
    prompt = f"""
Create a 3-month learning roadmap for an employee:
Current: {state.get('current_role')} | Target: {state.get('target_role')}
Skill gaps to fix: {gaps}
Month by month plan, specific and actionable. Under 250 words.
"""
    state["roadmap"] = call_llm(prompt)
    return state


def check_burnout_node(state: EmployeeState) -> EmployeeState:
    hours = state.get("work_hours", 8)
    prompt = f"""
Assess burnout risk for an employee working {hours} hours/day
targeting promotion from {state.get('current_role')} to {state.get('target_role')}.
Give a 1-sentence risk level and 2 quick recovery tips.
"""
    state["burnout_risk"] = call_llm(prompt)
    return state


def career_advice_node(state: EmployeeState) -> EmployeeState:
    prompt = f"""
Give 3 powerful, specific career tips for someone going from
{state.get('current_role')} to {state.get('target_role')}.
Based on their roadmap: {state.get('roadmap', '')[:300]}
Be direct, motivating, and practical.
"""
    state["career_advice"] = call_llm(prompt)
    return state


# ── Graph builder ──────────────────────────────────────────────────────────────
def build_employee_graph():
    graph = StateGraph(EmployeeState)
    graph.add_node("analyze_profile", analyze_profile_node)
    graph.add_node("detect_skill_gaps", detect_skill_gaps_node)
    graph.add_node("generate_roadmap", generate_roadmap_node)
    graph.add_node("check_burnout", check_burnout_node)
    graph.add_node("career_advice", career_advice_node)
    graph.set_entry_point("analyze_profile")
    graph.add_edge("analyze_profile", "detect_skill_gaps")
    graph.add_edge("detect_skill_gaps", "generate_roadmap")
    graph.add_edge("generate_roadmap", "check_burnout")
    graph.add_edge("check_burnout", "career_advice")
    graph.add_edge("career_advice", END)
    return graph.compile()


def run_employee_graph(
    current_role: str,
    target_role: str,
    company_stack: str,
    weak_areas: List[str],
    work_hours: int = 8,
) -> EmployeeState:
    app = build_employee_graph()
    result = app.invoke(EmployeeState(
        current_role=current_role,
        target_role=target_role,
        company_stack=company_stack,
        weak_areas=weak_areas,
        work_hours=work_hours,
        profile_summary="",
        skill_gaps=[],
        roadmap="",
        burnout_risk="",
        career_advice="",
    ))
    return result
