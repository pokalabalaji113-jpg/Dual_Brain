"""
mcp/mcp_server.py
MCP (Model Context Protocol) Server for DualBrain AI.
Exposes all features as MCP tools that any MCP client can call.

Run standalone: python mcp/mcp_server.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from utils.llm_client import call_llm


# ── MCP Server instance ────────────────────────────────────────────────────────
server = Server("dualbrain-ai")


# ── Tool definitions ───────────────────────────────────────────────────────────
@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="analyze_resume",
            description="Analyze a resume text and extract skills, ATS score, strengths, weaknesses, and missing skills.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resume_text": {"type": "string", "description": "Full resume text"},
                    "job_role": {"type": "string", "description": "Target job role (optional)"},
                },
                "required": ["resume_text"],
            },
        ),
        types.Tool(
            name="generate_learning_path",
            description="Generate a phase-by-phase learning path for a given skill.",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill": {"type": "string", "description": "Skill to learn"},
                    "level": {"type": "string", "description": "Beginner / Intermediate / Advanced"},
                    "current_skills": {"type": "string", "description": "Comma-separated current skills"},
                },
                "required": ["skill"],
            },
        ),
        types.Tool(
            name="search_jobs",
            description="Get top 5 job suggestions based on skills and target role.",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_role": {"type": "string", "description": "Target job role"},
                    "skills": {"type": "string", "description": "Comma-separated skills"},
                },
                "required": ["job_role"],
            },
        ),
        types.Tool(
            name="career_transition_plan",
            description="Generate a full career transition plan from one role to another.",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_role": {"type": "string", "description": "Current role"},
                    "to_role": {"type": "string", "description": "Target role"},
                    "experience_years": {"type": "number", "description": "Years of experience"},
                    "current_skills": {"type": "string", "description": "Current skills"},
                },
                "required": ["from_role", "to_role"],
            },
        ),
        types.Tool(
            name="burnout_analysis",
            description="Analyze burnout risk and return recovery recommendations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "work_hours": {"type": "number", "description": "Daily work hours"},
                    "sleep_hours": {"type": "number", "description": "Daily sleep hours"},
                    "stress_level": {"type": "number", "description": "Stress level 1-10"},
                    "feelings": {"type": "string", "description": "How the employee feels"},
                },
                "required": ["work_hours", "stress_level"],
            },
        ),
        types.Tool(
            name="video_qa",
            description="Answer a question based on a YouTube video transcript.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Question to ask"},
                    "transcript": {"type": "string", "description": "YouTube video transcript"},
                    "video_title": {"type": "string", "description": "Video title"},
                },
                "required": ["question", "transcript"],
            },
        ),
    ]


# ── Tool handlers ──────────────────────────────────────────────────────────────
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    if name == "analyze_resume":
        resume_text = arguments["resume_text"]
        job_role = arguments.get("job_role", "")
        prompt = f"""
Analyze this resume and return JSON:
{{"skills": [], "missing_skills": [], "ats_score": 0-100, "strengths": [], "weaknesses": [], "recommended_roles": []}}
Target role: {job_role}
Resume: {resume_text[:3000]}
Return ONLY valid JSON.
"""
        result = call_llm(prompt)
        return [types.TextContent(type="text", text=result)]

    elif name == "generate_learning_path":
        skill = arguments["skill"]
        level = arguments.get("level", "Beginner")
        current = arguments.get("current_skills", "")
        prompt = f"""
Create a learning path for: {skill}
Level: {level} | Current skills: {current}
Return 3-4 phases with topics and estimated weeks. Be specific.
"""
        result = call_llm(prompt)
        return [types.TextContent(type="text", text=result)]

    elif name == "search_jobs":
        role = arguments["job_role"]
        skills = arguments.get("skills", "")
        prompt = f"""
Suggest 5 specific job titles and companies for:
Role: {role} | Skills: {skills}
Return as a numbered list with company type and salary range.
"""
        result = call_llm(prompt)
        return [types.TextContent(type="text", text=result)]

    elif name == "career_transition_plan":
        from_role = arguments["from_role"]
        to_role = arguments["to_role"]
        exp = arguments.get("experience_years", 2)
        skills = arguments.get("current_skills", "")
        prompt = f"""
Career transition plan:
FROM: {from_role} ({exp} years) TO: {to_role}
Current skills: {skills}
Include: skill gaps, 3-month roadmap, interview prep tips, estimated timeline.
"""
        result = call_llm(prompt)
        return [types.TextContent(type="text", text=result)]

    elif name == "burnout_analysis":
        hours = arguments["work_hours"]
        sleep = arguments.get("sleep_hours", 7)
        stress = arguments["stress_level"]
        feelings = arguments.get("feelings", "")
        prompt = f"""
Burnout analysis:
Work hours/day: {hours} | Sleep hours: {sleep} | Stress: {stress}/10
Feelings: {feelings}
Give: risk level (low/moderate/high/critical), 3 immediate actions, weekly schedule suggestion.
"""
        result = call_llm(prompt)
        return [types.TextContent(type="text", text=result)]

    elif name == "video_qa":
        question = arguments["question"]
        transcript = arguments["transcript"][:3000]
        title = arguments.get("video_title", "YouTube Video")
        prompt = f"""
You are an expert tutor for the video: "{title}"
Answer this question using the transcript below.
Question: {question}
Transcript: {transcript}
Give a clear, educational answer grounded in the transcript.
"""
        result = call_llm(prompt)
        return [types.TextContent(type="text", text=result)]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


# ── Run server ─────────────────────────────────────────────────────────────────
async def main():
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
