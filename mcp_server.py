"""
mcp/mcp_server.py
DualBrain AI — MCP Server
Exposes all features as MCP tools callable by any MCP client (Claude Desktop, etc.)

Run: python mcp/mcp_server.py
Connect via: claude_desktop_config.json
"""
import os, sys, json, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from utils.llm_client import call_llm
from utils.youtube_utils import get_transcript, extract_video_id_from_url, search_youtube_videos

server = Server("dualbrain-ai")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="analyze_resume",
            description="Analyze a resume. Returns skills, ATS score, missing skills, strengths, weaknesses, job recommendations.",
            inputSchema={"type":"object","properties":{
                "resume_text": {"type":"string","description":"Full resume text"},
                "job_role":    {"type":"string","description":"Target job role (optional)"}
            },"required":["resume_text"]},
        ),
        types.Tool(
            name="generate_learning_path",
            description="Generate a phase-by-phase learning path for any skill.",
            inputSchema={"type":"object","properties":{
                "skill":          {"type":"string","description":"Skill to learn"},
                "level":          {"type":"string","description":"Beginner/Intermediate/Advanced"},
                "current_skills": {"type":"string","description":"Current skills comma separated"}
            },"required":["skill"]},
        ),
        types.Tool(
            name="search_jobs",
            description="Get top job suggestions for a role and skills.",
            inputSchema={"type":"object","properties":{
                "job_role": {"type":"string","description":"Target job role"},
                "skills":   {"type":"string","description":"Skills comma separated"}
            },"required":["job_role"]},
        ),
        types.Tool(
            name="career_transition",
            description="Generate full career transition plan from one role to another.",
            inputSchema={"type":"object","properties":{
                "from_role":       {"type":"string","description":"Current role"},
                "to_role":         {"type":"string","description":"Target role"},
                "experience_years":{"type":"number","description":"Years of experience"},
                "current_skills":  {"type":"string","description":"Current skills"}
            },"required":["from_role","to_role"]},
        ),
        types.Tool(
            name="burnout_analysis",
            description="Analyze burnout risk and return recovery plan.",
            inputSchema={"type":"object","properties":{
                "work_hours":  {"type":"number","description":"Daily work hours"},
                "sleep_hours": {"type":"number","description":"Daily sleep hours"},
                "stress_level":{"type":"number","description":"Stress 1-10"},
                "feelings":    {"type":"string","description":"How the person feels"}
            },"required":["work_hours","stress_level"]},
        ),
        types.Tool(
            name="youtube_url_chat",
            description="Extract transcript from a YouTube URL and answer a question about it.",
            inputSchema={"type":"object","properties":{
                "youtube_url": {"type":"string","description":"Full YouTube video URL"},
                "question":    {"type":"string","description":"Question to ask about the video"}
            },"required":["youtube_url","question"]},
        ),
        types.Tool(
            name="skill_assessment",
            description="Generate MCQ questions to assess knowledge in a domain.",
            inputSchema={"type":"object","properties":{
                "domain":     {"type":"string","description":"Domain to assess"},
                "experience": {"type":"number","description":"Years of experience"},
                "skills":     {"type":"string","description":"Claimed skills"}
            },"required":["domain"]},
        ),
        types.Tool(
            name="search_youtube_videos",
            description="Search YouTube for tutorial videos on any skill or topic.",
            inputSchema={"type":"object","properties":{
                "query":       {"type":"string","description":"Skill or topic to search"},
                "max_results": {"type":"number","description":"Number of results (default 5)"}
            },"required":["query"]},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    if name == "analyze_resume":
        prompt = f"""Analyze this resume. Return JSON with:
skills, missing_skills, ats_score (0-100), strengths, weaknesses,
resume_improvements, recommended_job_roles.
Target role: {arguments.get('job_role','')}
Resume: {arguments['resume_text'][:3000]}
Return ONLY valid JSON."""
        return [types.TextContent(type="text", text=call_llm(prompt))]

    elif name == "generate_learning_path":
        prompt = f"""Create learning path for: {arguments['skill']}
Level: {arguments.get('level','Beginner')} | Current: {arguments.get('current_skills','')}
Return 3-4 phases with topics, duration, YouTube search queries, milestones."""
        return [types.TextContent(type="text", text=call_llm(prompt))]

    elif name == "search_jobs":
        role   = arguments['job_role']
        skills = arguments.get('skills','')
        enc    = role.replace(' ','%20')
        result = f"""Top job links for {role}:
1. LinkedIn (24h): https://www.linkedin.com/jobs/search/?keywords={enc}&f_TPR=r86400
2. Naukri: https://www.naukri.com/{role.replace(' ','+').lower()}-jobs
3. LinkedIn Remote: https://www.linkedin.com/jobs/search/?keywords={enc}&f_WT=2
4. Indeed: https://www.indeed.com/jobs?q={enc}"""
        return [types.TextContent(type="text", text=result)]

    elif name == "career_transition":
        prompt = f"""Career transition plan:
FROM: {arguments['from_role']} ({arguments.get('experience_years',2)} years)
TO: {arguments['to_role']}
Skills: {arguments.get('current_skills','')}
Include: feasibility score, skill gaps, 3-month roadmap, interview prep, timeline."""
        return [types.TextContent(type="text", text=call_llm(prompt))]

    elif name == "burnout_analysis":
        prompt = f"""Burnout analysis:
Work: {arguments['work_hours']}h/day | Sleep: {arguments.get('sleep_hours',7)}h
Stress: {arguments['stress_level']}/10 | Feelings: {arguments.get('feelings','')}
Give: risk level, 3 immediate actions, weekly schedule, recovery tips."""
        return [types.TextContent(type="text", text=call_llm(prompt))]

    elif name == "youtube_url_chat":
        url      = arguments['youtube_url']
        question = arguments['question']
        vid_id   = extract_video_id_from_url(url)
        if not vid_id:
            return [types.TextContent(type="text", text="Invalid YouTube URL.")]
        transcript = get_transcript(vid_id)
        if transcript:
            ctx    = " ".join(transcript.split()[:3000])
            prompt = f"""Answer based on this YouTube video transcript.
Question: {question}
Transcript: {ctx}
If not in transcript, say so and give general answer."""
        else:
            prompt = f"Answer this question about the YouTube video {url}: {question}"
        return [types.TextContent(type="text", text=call_llm(prompt))]

    elif name == "skill_assessment":
        prompt = f"""Generate 5 MCQ questions for {arguments['domain']}
Experience: {arguments.get('experience',2)} years | Skills: {arguments.get('skills','')}
Return JSON array with question, options (A/B/C/D), correct_answer, explanation."""
        return [types.TextContent(type="text", text=call_llm(prompt))]

    elif name == "search_youtube_videos":
        query   = arguments['query']
        n       = int(arguments.get('max_results', 5))
        videos  = search_youtube_videos(query, max_results=n)
        result  = f"YouTube videos for '{query}':\n"
        for i, v in enumerate(videos, 1):
            result += f"{i}. {v['title']} — {v['channel']}\n   URL: {v['url']}\n"
        return [types.TextContent(type="text", text=result)]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as streams:
        await server.run(
            streams[0], streams[1],
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
