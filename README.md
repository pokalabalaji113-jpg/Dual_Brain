# 🧠 DualBrain AI — Adaptive Career Intelligence Platform

> Two specialized AI brains, one platform: **Job Seeker Brain** and **Employee Brain**, each running its own LangGraph pipeline, sharing a Hybrid RAG engine, an MCP tool server, and full Langfuse + RAGAS observability.

---

## 🚀 What This Project Demonstrates

This isn't a single-prompt chatbot. It's a full GenAI engineering stack covering **8 distinct concepts** that interviewers look for:

| # | Concept | Where it's used |
|---|---------|------------------|
| 1 | Multi-agent orchestration | LangGraph sequential pipelines (seeker_graph.py, employee_graph.py) |
| 2 | Retrieval-Augmented Generation | Video transcript Q&A, URL chatbot |
| 3 | Hybrid Retrieval | FAISS (dense) + BM25 (sparse) via EnsembleRetriever |
| 4 | Tool Protocol (MCP) | 8 exposed tools for external AI clients |
| 5 | LLM Observability | Langfuse tracing on every LLM call |
| 6 | Automated Evaluation | RAGAS metrics → Langfuse Scores dashboard |
| 7 | Document Processing | PyMuPDF/python-docx resume parsing |
| 8 | Production Deployment | Docker + Streamlit Cloud |

---

## 🏗️ Full Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Streamlit UI — app.py (Brain Switcher)       │
└───────────────┬─────────────────────┬────────────────────┘
                 │                     │
        ┌────────▼────────┐   ┌───────▼─────────┐
        │  SEEKER GRAPH    │   │  EMPLOYEE GRAPH  │
        │  (LangGraph,     │   │  (LangGraph,     │
        │   5 nodes)       │   │   5 nodes)       │
        └────────┬────────┘   └───────┬─────────┘
                 │                     │
        ┌────────▼─────────────────────▼────────┐
        │       Shared Services Layer (utils/)   │
        │  llm_client │ rag_engine │ youtube_utils │
        │  resume_parser │ job_search              │
        └────────┬────────────────────┬──────────┘
                 │                    │
        ┌────────▼──────┐    ┌────────▼────────┐
        │ Hybrid RAG     │    │ MCP Server       │
        │ FAISS + BM25   │    │ (8 tools)        │
        └────────────────┘    └─────────────────┘
                 │
        ┌────────▼──────────┐
        │ Langfuse + RAGAS   │
        │ (tracing + scoring)│
        └────────────────────┘
```

---

## 🤖 Agent Workflow — Sequential Multi-Agent Graphs (LangGraph)

Both brains use a **deterministic sequential StateGraph** (not a ReAct/supervisor agent — chosen deliberately because each step depends on the previous step's output, so a routing LLM call would be wasted cost).

### Job Seeker Graph (`seeker_graph.py`)
```
extract_skills → search_jobs → generate_learning_path → suggest_videos → generate_report
```

### Employee Graph (`employee_graph.py`)
```
analyze_profile → detect_skill_gaps → generate_roadmap → check_burnout → career_advice
```

Each node:
1. Reads a shared `state` dict
2. Calls `call_llm()` with a "return ONLY JSON" system prompt
3. Updates `state` with structured output
4. Passes to the next node via `add_edge()`

---

## 🔀 Hybrid RAG Pipeline (the part most people skip)

```python
EnsembleRetriever(
    retrievers=[faiss_retriever, bm25_retriever],
    weights=[0.6, 0.4]   # 60% semantic, 40% keyword
)
```

| Retriever | Type | Catches |
|-----------|------|---------|
| FAISS (Sentence-Transformers `all-MiniLM-L6-v2`) | Dense/semantic | Paraphrased questions, conceptual similarity |
| BM25 | Sparse/keyword | Exact terms, acronyms, names that embeddings miss |

**Why this matters in interviews:** pure dense retrieval fails on exact keyword matches (e.g., error codes, proper nouns); pure sparse retrieval fails on paraphrasing. Hybrid covers both failure modes.

---

## 🔌 MCP Server — 8 Tools Exposed

| Tool | Purpose |
|------|---------|
| `analyze_resume` | Full resume → skills/gaps/ATS score (JSON) |
| `generate_learning_path` | Phase-based roadmap for any skill |
| `search_jobs` | Job listing links/results |
| `career_transition` | Role A → Role B feasibility + roadmap |
| `burnout_analysis` | 9-dim burnout scoring + recovery plan |
| `skill_assessment` | 10 AI-generated MCQs per domain |
| `youtube_url_chat` | Transcript-grounded Q&A on any YouTube URL |
| `search_youtube_videos` | Skill → curated/searched video results |

This means DualBrain AI isn't just a Streamlit app — it's also a **callable AI service** any MCP client (e.g. Claude Desktop) can plug into.

---

## 📊 Observability — Langfuse + RAGAS

Every LLM call is wrapped with `langfuse.langchain.CallbackHandler`, producing a trace per generation. On top of that, `evaluate_rag.py` runs **RAGAS-style scoring** on RAG answers and pushes results back into the same trace using `client.create_score(trace_id=..., name=..., value=...)`.

| Metric | Measures |
|--------|----------|
| `ragas_faithfulness` | Is the answer grounded in retrieved context? |
| `ragas_answer_relevancy` | Does it actually answer the question? |
| `ragas_context_recall` | Did retrieval surface the needed info? |
| `ragas_context_precision` | Is the retrieved context free of noise? |
| `ragas_hallucination` | Derived: `1 - faithfulness` |
| `ragas_overall` | Average of the four core metrics |

**Key gotcha (v3/v4 SDK):**
- ❌ `langfuse.trace(...)` — removed in SDK v3+
- ✅ `langfuse.start_as_current_observation(as_type="span", ...)` + `get_current_trace_id()`
- ❌ `trace.score(...)` — silently no-ops
- ✅ `client.create_score(trace_id=..., name=..., value=..., data_type="NUMERIC")`
- Env var is `LANGFUSE_BASE_URL` (or `LANGFUSE_HOST` for older SDKs) — must point to `us.cloud.langfuse.com` if your project is on the US region

---

## 🧰 Full Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| LLM | Groq — LLaMA 3.3 70B Versatile | Free, extremely fast inference |
| Orchestration | LangChain | Standard chains, prompt templates, output parsers |
| Multi-agent | LangGraph | Stateful sequential pipelines |
| Vector store | FAISS | Dense semantic search |
| Sparse retrieval | BM25 (`rank_bm25`) | Keyword/exact-match search |
| Embeddings | Sentence-Transformers (`all-MiniLM-L6-v2`) | Local, free, no API cost |
| Document parsing | PyMuPDF, python-docx | Resume text extraction |
| Video | youtube-transcript-api, YouTube Data API | Transcript fetch + search |
| Tool protocol | MCP (Model Context Protocol) | External AI client integration |
| Observability | Langfuse v3/v4 | Tracing every LLM call |
| Evaluation | RAGAS-style custom scorer | Faithfulness/relevancy/recall/precision |
| UI | Streamlit | Rapid multi-page app |
| Container | Docker | Reproducible deployment |
| Hosting | Streamlit Community Cloud | Free public demo |

---

## 📁 Project Structure

```
dual_brain_ai/
├── app.py                     # Brain switcher / router
├── graph/
│   ├── seeker_graph.py         # 5-node Job Seeker LangGraph
│   └── employee_graph.py       # 5-node Employee LangGraph
├── pages/                       # Streamlit pages per feature
│   ├── resume_analysis.py
│   ├── skill_videos.py
│   ├── video_chatbot.py
│   ├── url_chatbot.py
│   ├── learning_path.py
│   ├── job_links.py
│   ├── learning_companion.py
│   ├── career_transition.py
│   ├── burnout_intelligence.py
│   ├── performance_analyzer.py
│   ├── skill_assessment.py
│   └── team_intelligence.py
├── utils/
│   ├── llm_client.py            # Groq + Langfuse callback wiring
│   ├── rag_engine.py             # Hybrid FAISS+BM25 retriever
│   ├── resume_parser.py
│   ├── youtube_utils.py
│   ├── job_search.py
│   └── claude_client.py
├── mcp/
│   ├── mcp_server.py             # 8-tool MCP server
│   └── claude_desktop_config.json
├── evaluate_rag.py                # RAGAS + Langfuse scoring script
├── Dockerfile
├── .dockerignore
├── requirements.txt
└── .streamlit/secrets.toml        # API keys (gitignored)
```

---

## ⚙️ Setup

```bash
pip install -r requirements.txt
```

`.streamlit/secrets.toml`:
```toml
GROQ_API_KEY        = "gsk_..."
LANGFUSE_PUBLIC_KEY = "pk-lf-..."
LANGFUSE_SECRET_KEY = "sk-lf-..."
LANGFUSE_BASE_URL   = "https://us.cloud.langfuse.com"
YOUTUBE_API_KEY     = "..."   # optional
SERPAPI_KEY         = "..."   # optional
```

Run locally:
```bash
streamlit run app.py
```

Run evaluation:
```bash
python evaluate_rag.py
```

Run with Docker:
```bash
docker build -t dualbrain-ai .
docker run -p 8501:8501 --env-file .env dualbrain-ai
```

---

## 🧩 Design Decisions (talk about these in interviews)

1. **Sequential graph over ReAct agent** — deterministic dependencies between steps mean a router LLM call adds cost without adding value.
2. **Hybrid retrieval over pure FAISS** — covers both semantic paraphrasing and exact keyword matches.
3. **Reference-free RAGAS metrics** — `Faithfulness`, `ResponseRelevancy`, `LLMContextPrecisionWithoutReference` don't need ground-truth answers, so evaluation runs on *every* production query, not just a curated test set.
4. **Hallucination as a derived metric** — `1 - faithfulness`, free extra signal with zero added LLM calls.
5. **MCP exposure** — turns the app from "a UI" into "a service other agents can call."

---

## 🐛 Issues Solved During Build (good interview talking points)

- Groq model deprecation mid-project → migrated to `llama-3.3-70b-versatile`
- 429 rate limits during RAGAS eval → added delays + reduced `max_tokens`
- Langfuse SDK breaking changes (`trace()` removed, `score()` → `create_score()`, `LANGFUSE_HOST` → `LANGFUSE_BASE_URL`)
- Streamlit `DuplicateElementKey` on repeated video IDs → composite keys (`skill_idx + vid_idx`)
- Leaked API keys in git history → key rotation + history reset
- Sidebar collapse issue on Streamlit Cloud → CSS fix for `collapsedControl`

---

## 📜 License
MIT
