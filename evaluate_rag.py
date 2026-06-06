"""
evaluate_rag.py
RAGAS evaluation for DualBrain AI Hybrid RAG pipeline.
Metrics: Faithfulness, Answer Relevancy, Context Recall, Context Precision

Run: python evaluate_rag.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()


# ── Sample test dataset ────────────────────────────────────────────────────────
# Format: question, answer (from RAG), contexts (retrieved chunks), ground_truth
TEST_DATA = [
    {
        "question": "What is LangChain used for?",
        "answer": "LangChain is used for building applications powered by large language models by providing chains, prompts, and retrieval components.",
        "contexts": [
            "LangChain is a framework for developing applications powered by language models.",
            "It provides tools for prompt management, chains, and retrieval-augmented generation.",
        ],
        "ground_truth": "LangChain is a framework for building LLM-powered applications.",
    },
    {
        "question": "What is RAG?",
        "answer": "RAG stands for Retrieval Augmented Generation. It retrieves relevant documents from a vector store and uses them as context for the LLM to generate accurate answers.",
        "contexts": [
            "RAG combines retrieval systems with language model generation.",
            "The retriever finds relevant chunks and passes them to the LLM as context.",
        ],
        "ground_truth": "RAG is a technique that retrieves relevant documents and uses them to ground LLM responses.",
    },
    {
        "question": "What is FAISS?",
        "answer": "FAISS is Facebook AI Similarity Search, a vector database for fast similarity search over embeddings.",
        "contexts": [
            "FAISS is a library for efficient similarity search and clustering of dense vectors.",
            "It allows storing text embeddings and retrieving the most similar chunks quickly.",
        ],
        "ground_truth": "FAISS is a vector similarity search library by Facebook AI.",
    },
    {
        "question": "What is BM25?",
        "answer": "BM25 is a keyword-based sparse retrieval algorithm that ranks documents by term frequency and inverse document frequency.",
        "contexts": [
            "BM25 is a ranking function used in information retrieval based on keyword matching.",
            "It scores documents based on how often query terms appear relative to document length.",
        ],
        "ground_truth": "BM25 is a keyword matching retrieval algorithm used in information retrieval.",
    },
    {
        "question": "What is LangGraph?",
        "answer": "LangGraph is a graph-based orchestration framework that enables multi-node agent pipelines where each node performs a specific task and passes state to the next.",
        "contexts": [
            "LangGraph allows building stateful multi-agent workflows as directed graphs.",
            "Each node in the graph represents a step in the AI pipeline.",
        ],
        "ground_truth": "LangGraph is a framework for building multi-node agent pipelines using graph architecture.",
    },
]


def run_ragas_evaluation():
    """Run RAGAS evaluation on the test dataset."""
    try:
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision,
        )
        from datasets import Dataset

        print("=" * 60)
        print("🧪 DualBrain AI — RAGAS Evaluation")
        print("=" * 60)

        # Build dataset
        data = {
            "question":    [d["question"]    for d in TEST_DATA],
            "answer":      [d["answer"]      for d in TEST_DATA],
            "contexts":    [d["contexts"]    for d in TEST_DATA],
            "ground_truth":[d["ground_truth"]for d in TEST_DATA],
        }
        dataset = Dataset.from_dict(data)

        print(f"\n📊 Evaluating {len(TEST_DATA)} test cases...")
        print("Metrics: Faithfulness | Answer Relevancy | Context Recall | Context Precision\n")

        # Run evaluation
        result = evaluate(
            dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_recall,
                context_precision,
            ],
        )

        # Display results
        print("\n" + "=" * 60)
        print("📈 RAGAS EVALUATION RESULTS")
        print("=" * 60)
        df = result.to_pandas()
        print(df.to_string(index=False))

        print("\n" + "=" * 60)
        print("📊 AVERAGE SCORES")
        print("=" * 60)
        print(f"Faithfulness:       {result['faithfulness']:.4f}  (How factually correct are answers)")
        print(f"Answer Relevancy:   {result['answer_relevancy']:.4f}  (How relevant are answers to questions)")
        print(f"Context Recall:     {result['context_recall']:.4f}  (How much ground truth is in context)")
        print(f"Context Precision:  {result['context_precision']:.4f}  (How precise is the retrieved context)")
        print("=" * 60)

        overall = (
            result['faithfulness'] +
            result['answer_relevancy'] +
            result['context_recall'] +
            result['context_precision']
        ) / 4

        print(f"\n🎯 Overall RAG Score: {overall:.4f} / 1.0")
        if overall >= 0.8:
            print("✅ Excellent RAG performance!")
        elif overall >= 0.6:
            print("⚠️ Good RAG performance — room for improvement.")
        else:
            print("❌ RAG needs improvement.")

        return result

    except ImportError:
        print("❌ RAGAS not installed.")
        print("Run: pip install ragas datasets")
        return None
    except Exception as e:
        print(f"❌ Evaluation error: {e}")
        return None


if __name__ == "__main__":
    run_ragas_evaluation()
