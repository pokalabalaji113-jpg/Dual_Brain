<div align="center">

# 🧠 DualBrain AI
### *The World's First Dual-Mode AI Career Intelligence Platform*

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.2-green?style=for-the-badge)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1-orange?style=for-the-badge)](https://langchain-ai.github.io/langgraph)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-purple?style=for-the-badge)](https://groq.com)
[![MCP](https://img.shields.io/badge/MCP-8_Tools-red?style=for-the-badge)](https://modelcontextprotocol.io)
[![FAISS](https://img.shields.io/badge/FAISS-RAG-yellow?style=for-the-badge)](https://faiss.ai)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

> **DualBrain AI** is an adaptive career intelligence platform that switches its AI reasoning model based on user role — **Job Seeker Brain** for those entering the market, **Employee Brain** for those growing inside a company. Powered by LangGraph multi-node agents, LangChain RAG pipelines, FAISS vector search, and MCP tool protocol.

<br/>

![DualBrain AI Demo](https://img.shields.io/badge/Status-Production_Ready-brightgreen?style=for-the-badge)

</div>

---

## 🎯 What Makes This Different

| Feature | DualBrain AI | Regular Chatbot |
|---|---|---|
| **Adaptive Brain** | Switches reasoning per role | Single mode only |
| **Video RAG** | Answers FROM video transcript (FAISS) | No video understanding |
| **URL Chatbot** | Paste any YouTube URL → instant Q&A | Not possible |
| **LangGraph Agents** | Multi-node pipeline per brain | Single LLM call |
| **MCP Protocol** | 8 exposed tools for external clients | No tool protocol |
| **Skill Verification** | AI quiz to detect fake skills | No verification |
| **Burnout AI** | Detects stress patterns + recovery | No wellness |

---

## 🧠 Architecture — Dual Brain System

```
┌─────────────────────────────────────────────────────────────┐
│                      DualBrain AI                           │
│                   Brain Switcher (app.py)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
┌─────────▼──────────┐   ┌──────────▼──────────┐
│  🎯 JOB SEEKER     │   │  💼 EMPLOYEE BRAIN  │
│      BRAIN         │   │                     │
│                    │   │  LangGraph Pipeline:│
│  LangGraph:        │   │  analyze_profile    │
│  extract_skills    │   │  → detect_gaps      │
│  → search_jobs     │   │  → gen_roadmap      │
│  → learning_path   │   │  → burnout_check    │
│  → suggest_videos  │   │  → career_advice    │
│  → final_report    │   │                     │
└────────────────────┘   └─────────────────────┘
          │                         │
          └────────────┬────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    SHARED SERVICES                          │
│  LangChain + Groq LLaMA 3.3 70B  │  FAISS Vector Store     │
│  YouTube Data API                 │  RAG Engine             │
│  YouTube Transcript API           │  MCP Server (8 tools)   │
│  SerpAPI Job Search               │  Resume Parser          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Features

### 🎯 Job Seeker Brain — 7 Modules

<details>
<summary><b>📄 Resume Analysis</b> — Click to expand</summary>

- Upload PDF, DOCX, or TXT resume
- **LangGraph 5-node pipeline** extracts skills automatically
- ATS compatibility score (0-100) with specific feedback
- Missing skills detection based on target job role
- Resume improvement suggestions (5 specific tips)
- Strength and weakness analysis
- Recommended job roles with LinkedIn + Naukri links
- One-click navigation to learn missing skills via YouTube

</details>

<details>
<summary><b>📺 Skill Videos</b> — Click to expand</summary>

- Search any skill — **50+ skills** with matched videos
- Videos embedded directly in app — **no YouTube redirect**
- Auto-loads transcript when video plays
- Smart fallback: known library → YouTube search embed
- Works for ANY skill even if not in library
- Skill chips from resume for one-click search

</details>

<details>
<summary><b>💬 Video Chatbot</b> — Click to expand</summary>

- **LangChain RAG + FAISS** — answers grounded in video transcript
- Semantic similarity search across transcript chunks
- 6 quick-prompt buttons for instant questions
- Falls back to general knowledge if no transcript
- No duplicate messages — single input source
- Full chat history with clear option

</details>

<details>
<summary><b>🔗 URL Chatbot</b> — Click to expand</summary>

- Paste **ANY YouTube URL** from browser
- Transcript extracted automatically
- RAG chatbot answers doubts from video content
- 8 quick-prompt buttons
- Works even for videos without transcripts (general knowledge mode)
- Available in BOTH brains

</details>

<details>
<summary><b>🗺 Learning Path</b> — Click to expand</summary>

- AI generates phase-by-phase roadmap for any skill
- 3-4 phases with 3-5 topics each
- YouTube videos embedded per topic
- Unique button keys — no duplicate key errors
- Career outcomes with job links
- Practice project suggestions

</details>

<details>
<summary><b>🔗 Job Links</b> — Click to expand</summary>

- LinkedIn + Naukri job links based on resume skills
- Fresher / Mid / Senior / Remote / Freelance categories
- AI-generated cover letter per job
- One-click apply buttons
- Real-time links based on target role

</details>

### 💼 Employee Brain — 6 Modules

<details>
<summary><b>🤖 Learning Companion</b> — Click to expand</summary>

- **LangGraph 5-node agent pipeline** runs end-to-end
- Profile → Skill Gaps → 3-Month Roadmap → Burnout Check → Career Advice
- YouTube video links per skill gap
- Persistent companion chat with profile context
- Links to Coursera courses per skill gap

</details>

<details>
<summary><b>🔀 Career Transition Engine</b> — Click to expand</summary>

- "I want to move from Backend to GenAI" → Full plan
- Feasibility score with explanation
- Skill overlap analysis
- Phase-by-phase transition roadmap
- Interview prep: key topics, practice questions, portfolio projects
- Salary change estimate
- YouTube videos per phase

</details>

<details>
<summary><b>🔥 Burnout Intelligence</b> — Click to expand</summary>

- 9-dimension assessment (hours, sleep, stress, motivation...)
- Burnout score 0-100 with risk level
- Detected mental and physical signals
- Immediate action plan (do today)
- Weekly recovery schedule
- Manager conversation script generator
- Learning pause recommendation

</details>

<details>
<summary><b>📈 Performance Analyzer</b> — Click to expand</summary>

- Quarterly performance analysis
- Promotion readiness score (0-100%)
- Skill utilization: well-used / underutilized / should-learn
- Resume improvement suggestions for promotion
- Timeline-based action plan (this week / month / quarter)
- Peer comparison insight

</details>

<details>
<summary><b>🧪 Skill Assessment Quiz</b> — Click to expand</summary>

- 10 AI-generated MCQ questions per domain
- Easy/Medium/Hard difficulty mix
- Detects if claimed skills are genuine
- Answer review with explanations
- YouTube videos for weak areas (embedded)
- Interview readiness rating
- Personalized 2-week study plan

</details>

<details>
<summary><b>👥 Team Intelligence</b> — Click to expand</summary>

- Team health score (0-100)
- Communication pattern analysis
- Bottleneck detection
- Quick wins recommendations
- Team rituals to add (with duration)
- Tools to try for better collaboration

</details>

---

## 🔌 MCP Server — 8 Tools

DualBrain AI exposes a full **Model Context Protocol** server that any MCP client can connect to:

```python
Tools available:
├── analyze_resume          # Full resume analysis → JSON
├── generate_learning_path  # Phase-by-phase roadmap
├── search_jobs             # LinkedIn + Naukri job links
├── career_transition       # Full transition plan
├── burnout_analysis        # Stress detection + recovery
├── youtube_url_chat        # Answer from any YouTube URL
├── skill_assessment        # MCQ quiz generation
└── search_youtube_videos   # Find videos for any skill
```

### Connect to Claude Desktop:
```json
{
  "mcpServers": {
    "dualbrain-ai": {
      "command": "python",
      "args": ["mcp/mcp_server.py"],
      "cwd": "/path/to/dual_brain_ai",
      "env": {
        "GROQ_API_KEY": "your_key_here"
      }
    }
  }
}
```

---

## 📁 Project Structure

```
dual_brain_ai/
│
├── app.py                          # Brain switcher + routing
├── requirements.txt                # All dependencies
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
│
├── .streamlit/
│   ├── config.toml                 # Clean minimal theme
│   └── secrets.toml                # API keys (git ignored)
│
├── pages/                          # 12 feature pages
│   ├── __init__.py
│   ├── resume_analysis.py          # ATS + skills + jobs + improvements
│   ├── skill_videos.py             # YouTube embedded player
│   ├── video_chatbot.py            # RAG chatbot (FAISS)
│   ├── url_chatbot.py              # ANY YouTube URL chatbot ← NEW
│   ├── learning_path.py            # Phase-by-phase roadmap
│   ├── job_links.py                # LinkedIn + Naukri + cover letter
│   ├── learning_companion.py       # LangGraph employee pipeline
│   ├── career_transition.py        # Role transition engine
│   ├── burnout_intelligence.py     # Stress detection
│   ├── performance_analyzer.py     # Promotion readiness
│   ├── skill_assessment.py         # MCQ quiz
│   └── team_intelligence.py        # Collaboration patterns
│
├── graph/                          # LangGraph agents
│   ├── __init__.py
│   ├── seeker_graph.py             # 5-node job seeker pipeline
│   └── employee_graph.py           # 5-node employee pipeline
│
├── mcp/                            # MCP Protocol server
│   ├── __init__.py
│   ├── mcp_server.py               # 8 MCP tools
│   └── claude_desktop_config.json  # Claude Desktop config
│
└── utils/                          # Shared services
    ├── __init__.py
    ├── llm_client.py               # LangChain + Groq
    ├── claude_client.py            # Compatibility shim
    ├── rag_engine.py               # FAISS vector store
    ├── resume_parser.py            # PyMuPDF + python-docx
    ├── youtube_utils.py            # YouTube API + transcript
    └── job_search.py               # SerpAPI + fallback
```

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/dual_brain_ai.git
cd dual_brain_ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API keys
Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY     = "gsk_..."        # Required — free at console.groq.com
YOUTUBE_API_KEY  = "AIza..."        # Optional — Google Cloud Console
SERPAPI_KEY      = "..."            # Optional — serpapi.com
```

### 4. Run
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## 🔑 API Keys

| Key | Required | Free? | Get it from |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | ✅ Free | [console.groq.com](https://console.groq.com) |
| `YOUTUBE_API_KEY` | Optional | ✅ Free (10k/day) | [Google Cloud Console](https://console.cloud.google.com) |
| `SERPAPI_KEY` | Optional | ✅ Free (100/mo) | [serpapi.com](https://serpapi.com) |

> Without YouTube API key → 50+ built-in videos + YouTube search fallback
> Without SerpAPI key → LinkedIn + Naukri direct links

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit |
| **LLM** | Groq — LLaMA 3.3 70B |
| **LLM Framework** | LangChain + LangChain-Groq |
| **Agent Orchestration** | LangGraph (multi-node pipelines) |
| **Vector Store** | FAISS (Facebook AI) |
| **Embeddings** | Sentence Transformers (all-MiniLM-L6-v2) |
| **RAG** | LangChain RAG + FAISS retriever |
| **Tool Protocol** | MCP (Model Context Protocol) |
| **Resume Parsing** | PyMuPDF + python-docx |
| **YouTube** | YouTube Data API v3 + youtube-transcript-api |
| **Job Search** | SerpAPI (Google Jobs) |
| **Language** | Python 3.12 |

---

## 🤝 Contributing

1. Fork the repository
2. Create your branch: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ using LangChain · LangGraph · Groq · FAISS · MCP · Streamlit**

⭐ Star this repo if it helped you!

</div>
