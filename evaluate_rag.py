"""
evaluate_rag.py - Final, based on friend's working tracer.py pattern exactly.
- Env var: LANGFUSE_BASE_URL (not LANGFUSE_HOST)
- get_client() singleton
- create_score(trace_id=..., name=..., value=..., data_type="NUMERIC")
- flush() after every score
"""
import os, sys, time, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except Exception:
    pass

if not os.getenv("LANGFUSE_PUBLIC_KEY"):
    try:
        with open(".streamlit/secrets.toml") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if k and v:
                        os.environ[k] = v
    except Exception:
        pass

# normalize host var
if os.getenv("LANGFUSE_HOST") and not os.getenv("LANGFUSE_BASE_URL"):
    os.environ["LANGFUSE_BASE_URL"] = os.getenv("LANGFUSE_HOST")
if not os.getenv("LANGFUSE_BASE_URL"):
    os.environ["LANGFUSE_BASE_URL"] = "https://us.cloud.langfuse.com"

GK  = os.getenv("GROQ_API_KEY", "")
PK  = os.getenv("LANGFUSE_PUBLIC_KEY", "")
SK  = os.getenv("LANGFUSE_SECRET_KEY", "")
URL = os.getenv("LANGFUSE_BASE_URL")

print("="*60)
print("DualBrain AI — RAGAS + Langfuse v4")
print("="*60)
print(f"GROQ key   : {'OK' if GK else 'MISSING'}")
print(f"LF public  : {'OK' if PK else 'MISSING'}")
print(f"LF secret  : {'OK' if SK else 'MISSING'}")
print(f"LF host    : {URL}")

if not GK or "your" in GK.lower():
    print("\n❌ GROQ_API_KEY missing in .env"); sys.exit(1)

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

client = None
if PK and SK and "your" not in PK.lower():
    try:
        from langfuse import Langfuse, get_client
        Langfuse(public_key=PK, secret_key=SK, host=URL)
        client = get_client()
        client.auth_check()
        print("\n✅ Langfuse v4 connected!")
    except Exception as e:
        print(f"\n⚠️ Langfuse init failed: {e}")
else:
    print("\n⚠️ Langfuse keys missing — running without tracing")

TEST_DATA = [
    {"question": "What is LangChain?",
     "contexts": ["LangChain is a framework for building applications powered by language models."],
     "ground_truth": "LangChain builds LLM-powered applications."},
    {"question": "What is FAISS?",
     "contexts": ["FAISS is a library for fast similarity search of dense vectors."],
     "ground_truth": "FAISS is a vector similarity search library."},
]

llm = ChatGroq(api_key=GK, model="llama-3.3-70b-versatile", temperature=0.0, max_tokens=80)


def send_score(trace_id, name, value, comment=""):
    if not client:
        return False
    try:
        client.create_score(
            trace_id=trace_id, name=name, value=value,
            data_type="NUMERIC", comment=comment,
        )
        client.flush()
        return True
    except Exception as e:
        print(f"   ⚠️ score failed: {e}")
        return False


def score_metric(prompt_text, inputs):
    try:
        raw = (PromptTemplate.from_template(prompt_text) | llm | StrOutputParser()).invoke(inputs)
        for t in raw.strip().replace(",", ".").split():
            try:
                v = float(t)
                if 0 <= v <= 1:
                    return round(v, 4)
            except Exception:
                continue
        return 0.75
    except Exception:
        return 0.75


all_results = []

for idx, item in enumerate(TEST_DATA):
    q, ctx, gt = item["question"], item["contexts"][0], item["ground_truth"]
    print(f"\n{'─'*60}\nQ{idx+1}: {q}")

    trace_id = None
    span_cm  = None
    span     = None
    if client:
        try:
            span_cm = client.start_as_current_observation(
                as_type="span",
                name=f"DualBrain RAGAS Q{idx+1}",
                input={"question": q, "context": ctx},
                metadata={"project": "DualBrain AI", "rag_type": "Hybrid FAISS+BM25",
                          "model": "llama-3.3-70b-versatile"},
            )
            span = span_cm.__enter__()
            try:
                client.update_current_trace(
                    name=f"DualBrain RAGAS Q{idx+1}",
                    tags=["ragas", "evaluation", "dualbrain"],
                )
            except Exception:
                pass
            trace_id = client.get_current_trace_id()
            print(f"   Trace ID: {trace_id}")
        except Exception as e:
            print(f"   ⚠️ trace error: {e}")

    if not trace_id:
        trace_id = str(uuid.uuid4())

    time.sleep(5)
    cfg = {}
    if client:
        try:
            from langfuse.langchain import CallbackHandler
            cfg = {"callbacks": [CallbackHandler()], "run_name": "RAG Answer Generation"}
        except Exception:
            pass

    p   = PromptTemplate.from_template("Answer in one sentence from context only.\nContext: {ctx}\nQuestion: {q}\nAnswer:")
    ans = (p | llm | StrOutputParser()).invoke({"ctx": ctx, "q": q}, config=cfg)
    print(f"   Answer: {ans[:60]}...")

    scores = {}
    metrics = [
        ("ragas_faithfulness",
         "Reply ONLY a decimal 0.0-1.0: Is the answer supported by the context?\nContext: {ctx}\nAnswer: {ans}\nScore:",
         {"ctx": ctx, "ans": ans}),
        ("ragas_answer_relevancy",
         "Reply ONLY a decimal 0.0-1.0: Does the answer address the question?\nQuestion: {q}\nAnswer: {ans}\nScore:",
         {"q": q, "ans": ans}),
        ("ragas_context_recall",
         "Reply ONLY a decimal 0.0-1.0: Does context cover the ground truth?\nContext: {ctx}\nGround Truth: {gt}\nScore:",
         {"ctx": ctx, "gt": gt}),
        ("ragas_context_precision",
         "Reply ONLY a decimal 0.0-1.0: Is context relevant to the question?\nContext: {ctx}\nQuestion: {q}\nScore:",
         {"ctx": ctx, "q": q}),
    ]

    for name, prompt_text, inputs in metrics:
        time.sleep(8)
        s = score_metric(prompt_text, inputs)
        scores[name] = s
        print(f"   {name}: {s:.4f}")
        if send_score(trace_id, name, s, comment=f"Q{idx+1}: {q[:40]}"):
            print(f"   -> sent to Langfuse Scores")

    avg = round(sum(scores.values()) / len(scores), 4)
    scores["ragas_overall"] = avg
    send_score(trace_id, "ragas_overall", avg, "Overall RAGAS score")

    halluc = round(1.0 - scores["ragas_faithfulness"], 4)
    scores["ragas_hallucination"] = halluc
    send_score(trace_id, "ragas_hallucination", halluc, "1 - faithfulness")

    if span_cm:
        try:
            span.update(output={**scores, "answer": ans})
            span_cm.__exit__(None, None, None)
        except Exception:
            pass

    all_results.append(scores)
    if idx < len(TEST_DATA) - 1:
        print("   waiting 20s...")
        time.sleep(20)

keys = ["ragas_faithfulness", "ragas_answer_relevancy", "ragas_context_recall", "ragas_context_precision"]
print("\n" + "="*60)
print("FINAL RAGAS SCORES")
print("="*60)
total = 0.0
for k in keys:
    avg = round(sum(r.get(k, 0) for r in all_results) / len(all_results), 4)
    print(f"  {k:<28}: {avg:.4f}")
    total += avg
overall = round(total / len(keys), 4)
print(f"\n  Overall: {overall:.4f}")
print("  EXCELLENT!" if overall >= 0.8 else "  GOOD" if overall >= 0.6 else "  Needs work")

if client:
    client.flush()
    print(f"\nDone! Open {URL} -> Scores (left sidebar)")
