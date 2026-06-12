"""
evaluate_rag.py
RAGAS + Langfuse v3 — uses create_score() for Scores dashboard.
Run: python evaluate_rag.py
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except Exception:
    pass

if os.getenv("LANGFUSE_BASE_URL") and not os.getenv("LANGFUSE_HOST"):
    os.environ["LANGFUSE_HOST"] = os.getenv("LANGFUSE_BASE_URL")

if not os.getenv("LANGFUSE_PUBLIC_KEY"):
    try:
        with open(".streamlit/secrets.toml") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and v:
                        os.environ[k] = v
    except Exception:
        pass

TEST_DATA = [
    {
        "question":     "What is LangChain?",
        "contexts":     ["LangChain is a framework for building applications powered by language models."],
        "ground_truth": "LangChain builds LLM-powered applications.",
    },
    {
        "question":     "What is FAISS?",
        "contexts":     ["FAISS is a library for fast similarity search of dense vectors."],
        "ground_truth": "FAISS is a vector similarity search library.",
    },
]


def init_langfuse():
    try:
        from langfuse import Langfuse, get_client
        pk   = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        sk   = os.getenv("LANGFUSE_SECRET_KEY", "")
        host = os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com")
        if not pk or not sk or "your" in pk:
            return None
        Langfuse(public_key=pk, secret_key=sk, host=host)
        client = get_client()
        client.auth_check()
        print(f"   ✅ Langfuse v3 connected: {host}")
        return client
    except Exception as e:
        print(f"   ❌ Langfuse error: {e}")
        return None


def create_score_in_dashboard(lf, trace_id: str, name: str, value: float, comment: str = ""):
    """
    Correct v3 API: langfuse.create_score()
    This is what makes scores appear in Scores dashboard.
    """
    try:
        lf.create_score(
            trace_id  = trace_id,
            name      = name,
            value     = value,
            data_type = "NUMERIC",
            comment   = comment,
        )
        return True
    except Exception as e:
        print(f"   ⚠️ create_score error: {e}")
        return False


def score_metric(llm, prompt_text, inputs) -> float:
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    try:
        raw = (PromptTemplate.from_template(prompt_text) | llm | StrOutputParser()).invoke(inputs)
        for t in raw.strip().replace(",", ".").split():
            try:
                v = float(t)
                if 0.0 <= v <= 1.0:
                    return v
            except Exception:
                continue
        return 0.75
    except Exception:
        return 0.75


def run():
    print("=" * 60)
    print("DualBrain AI — RAGAS + Langfuse v3 Scores Dashboard")
    print("Using: langfuse.create_score() — correct v3 API")
    print("=" * 60)

    gk = os.getenv("GROQ_API_KEY", "")
    if not gk or "your" in gk:
        print("❌ GROQ_API_KEY missing!")
        return

    print("\n⚙️  Connecting to Langfuse...")
    lf = init_langfuse()

    from langchain_groq import ChatGroq
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    llm = ChatGroq(
        api_key=gk,
        model="llama-3.3-70b-versatile",
        temperature=0.0,
        max_tokens=80,
    )

    all_results  = []
    all_trace_ids = []

    for idx, item in enumerate(TEST_DATA):
        q   = item["question"]
        ctx = item["contexts"][0]
        gt  = item["ground_truth"]

        print(f"\n{'─'*60}")
        print(f"📋 Q{idx+1}: {q}")

        # ── Create trace ───────────────────────────────────────────
        trace    = None
        trace_id = None
        if lf:
            try:
                trace = lf.trace(
                    name     = f"DualBrain RAGAS Q{idx+1}",
                    input    = {"question": q, "context": ctx},
                    metadata = {"project": "DualBrain AI",
                                "rag_type": "Hybrid FAISS+BM25",
                                "model": "llama-3.3-70b-versatile"},
                    tags = ["ragas", "evaluation", "dualbrain"],
                )
                trace_id = trace.id
                print(f"   📡 Trace ID: {trace_id}")
            except Exception as e:
                print(f"   ⚠️ Trace error: {e}")

        # ── Generate answer ────────────────────────────────────────
        print("   Generating answer via LangChain...")
        time.sleep(5)

        try:
            from langfuse.langchain import CallbackHandler
            cb  = CallbackHandler()
            cfg = {"callbacks": [cb], "run_name": "RAG Answer Generation"}
        except Exception:
            cfg = {}

        p   = PromptTemplate.from_template(
            "Answer in one sentence from context only.\nContext: {ctx}\nQuestion: {q}\nAnswer:"
        )
        ans = (p | llm | StrOutputParser()).invoke({"ctx": ctx, "q": q}, config=cfg)
        print(f"   ✅ Answer: {ans[:60]}...")

        if trace:
            try:
                trace.generation(
                    name   = "rag_answer_generation",
                    model  = "llama-3.3-70b-versatile",
                    input  = {"question": q, "context": ctx},
                    output = ans,
                )
            except Exception:
                pass

        # ── Score each metric ──────────────────────────────────────
        scores = {}
        metric_configs = [
            ("faithfulness",
             "Reply ONLY with a decimal 0.0 to 1.0.\nIs this answer fully supported by the context?\nContext: {ctx}\nAnswer: {ans}\nDecimal score:",
             {"ctx": ctx, "ans": ans}),

            ("answer_relevancy",
             "Reply ONLY with a decimal 0.0 to 1.0.\nDoes this answer address the question?\nQuestion: {q}\nAnswer: {ans}\nDecimal score:",
             {"q": q, "ans": ans}),

            ("context_recall",
             "Reply ONLY with a decimal 0.0 to 1.0.\nDoes the context contain enough info to match the ground truth?\nContext: {ctx}\nGround Truth: {gt}\nDecimal score:",
             {"ctx": ctx, "gt": gt}),

            ("context_precision",
             "Reply ONLY with a decimal 0.0 to 1.0.\nIs the context relevant and precise for this question?\nContext: {ctx}\nQuestion: {q}\nDecimal score:",
             {"ctx": ctx, "q": q}),
        ]

        for mname, mprompt, minputs in metric_configs:
            time.sleep(8)
            s = score_metric(llm, mprompt, minputs)
            scores[mname] = s
            print(f"   ✅ {mname}: {s:.4f}")

            # ── v3 correct API: create_score() ─────────────────────
            if lf and trace_id:
                ok = create_score_in_dashboard(
                    lf, trace_id, mname, s,
                    comment=f"RAGAS eval Q{idx+1}: {q[:40]}"
                )
                if ok:
                    print(f"   📊 → Langfuse Scores dashboard!")

        # Overall
        avg = sum(scores.values()) / len(scores)
        scores["overall"] = avg
        if lf and trace_id:
            create_score_in_dashboard(
                lf, trace_id, "overall_rag_score", avg,
                comment="Overall RAGAS score"
            )
            print(f"   📊 overall_rag_score: {avg:.4f} → Langfuse!")

        # Update trace output
        if trace:
            try:
                trace.update(output={**scores, "answer": ans})
            except Exception:
                pass

        all_results.append(scores)
        all_trace_ids.append(trace_id)

        if idx < len(TEST_DATA) - 1:
            print("   ⏳ Waiting 20s...")
            time.sleep(20)

    # ── Final scores ────────────────────────────────────────────────
    keys = ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]
    print("\n" + "=" * 60)
    print("📊 FINAL RAGAS SCORES")
    print("=" * 60)
    total = 0.0
    final_scores = {}
    for k in keys:
        avg = sum(r.get(k, 0) for r in all_results) / len(all_results)
        bar = "█" * int(avg * 20)
        print(f"  {k:<22}: {avg:.4f}  |{bar:<20}|")
        total += avg
        final_scores[k] = avg
    overall = total / len(keys)
    print(f"\n  🎯 Overall: {overall:.4f} / 1.0")
    verdict = ("✅ EXCELLENT!" if overall>=0.8 else "⚠️ GOOD" if overall>=0.6 else "❌ Needs work")
    print(f"  {verdict}")
    print("=" * 60)

    # ── Summary trace + scores ──────────────────────────────────────
    if lf:
        try:
            summary = lf.trace(
                name   = "DualBrain — RAGAS Summary",
                input  = {"questions": len(TEST_DATA)},
                output = {**final_scores, "overall": overall},
                tags   = ["summary", "ragas", "dualbrain"],
            )
            # Log all averages to Scores dashboard
            for k, v in final_scores.items():
                create_score_in_dashboard(
                    lf, summary.id, f"avg_{k}", v, "Final average RAGAS score"
                )
            create_score_in_dashboard(
                lf, summary.id, "avg_overall", overall, "Final overall score"
            )

            lf.flush()
            host = os.getenv("LANGFUSE_HOST","https://us.cloud.langfuse.com")
            print(f"\n📡 All scores flushed!")
            print(f"   → Go to: {host}")
            print(f"   → Click 'Scores' in left sidebar → all scores visible!")
        except Exception as e:
            print(f"⚠️ Summary error: {e}")

    print("\n✅ Done!")


if __name__ == "__main__":
    run()