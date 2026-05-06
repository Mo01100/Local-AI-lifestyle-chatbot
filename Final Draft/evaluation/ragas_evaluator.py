"""
ragas_evaluator.py  (v2 — Hybrid, no LLM-judge hang)
=====================================================
Evaluates the Health AI Chatbot RAG pipeline using a hybrid metric suite.
Does NOT require Ollama to act as a judge (avoids OUTPUT_PARSING_FAILURE hangs).

Metrics computed:
  ┌─────────────────────────────────┬────────────────────────────────────────┐
  │ Metric                          │ Method                                 │
  ├─────────────────────────────────┼────────────────────────────────────────┤
  │ ROUGE-1 / ROUGE-2 / ROUGE-L     │ rouge-score (n-gram overlap)           │
  │ BLEU                            │ nltk (n-gram precision)                │
  │ Answer Semantic Similarity      │ sentence-transformers cosine sim       │
  │ Context Relevance               │ ChromaDB distance → similarity         │
  │ Faithfulness Proxy              │ cosine(answer ↔ context) embedding     │
  │ Answer F1 (token overlap)       │ Token-level precision/recall/F1        │
  │ BERTScore F1                    │ bert-score (contextual embeddings)     │
  └─────────────────────────────────┴────────────────────────────────────────┘

Usage:
  cd "c:\\Users\\Mohamed Metwaly\\Downloads\\Final Draft"
  python evaluation/ragas_evaluator.py
"""

import sys
import json
import time
import warnings
from pathlib import Path
from datetime import datetime

warnings.filterwarnings("ignore")

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).parent.parent
EVAL_DIR = Path(__file__).parent
sys.path.append(str(ROOT / "scripts"))   # llm/, rag/, translation/
sys.path.append(str(ROOT))               # evaluation package
sys.path.append(str(EVAL_DIR))           # sibling: eval_dataset

RESULTS_DIR = EVAL_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# ── Imports ───────────────────────────────────────────────────────────────────
print("Loading evaluation libraries...")

import numpy as np
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.tokenize import word_tokenize
import nltk
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

print("✓ Libraries loaded")


# ─────────────────────────────────────────────────────────────────────────────
#  METRIC IMPLEMENTATIONS
# ─────────────────────────────────────────────────────────────────────────────

def compute_rouge(prediction: str, reference: str) -> dict:
    """ROUGE-1, ROUGE-2, ROUGE-L F1 scores."""
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    scores = scorer.score(reference, prediction)
    return {
        "rouge1": round(scores["rouge1"].fmeasure, 4),
        "rouge2": round(scores["rouge2"].fmeasure, 4),
        "rougeL": round(scores["rougeL"].fmeasure, 4),
    }


def compute_bleu(prediction: str, reference: str) -> float:
    """Sentence BLEU with smoothing (handles short answers)."""
    smooth  = SmoothingFunction().method1
    ref_tok = word_tokenize(reference.lower())
    hyp_tok = word_tokenize(prediction.lower())
    if not hyp_tok:
        return 0.0
    score = sentence_bleu([ref_tok], hyp_tok, smoothing_function=smooth)
    return round(score, 4)


def compute_token_f1(prediction: str, reference: str) -> dict:
    """Token-level precision, recall, F1 (used in QA evaluation, e.g., SQuAD)."""
    pred_tokens = set(word_tokenize(prediction.lower()))
    ref_tokens  = set(word_tokenize(reference.lower()))
    common      = pred_tokens & ref_tokens

    if not common:
        return {"token_precision": 0.0, "token_recall": 0.0, "token_f1": 0.0}

    precision = len(common) / len(pred_tokens) if pred_tokens else 0.0
    recall    = len(common) / len(ref_tokens)  if ref_tokens  else 0.0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "token_precision": round(precision, 4),
        "token_recall":    round(recall, 4),
        "token_f1":        round(f1, 4),
    }


def embed_texts(model: SentenceTransformer, texts: list) -> np.ndarray:
    """Batch-encode texts to embeddings."""
    return model.encode(texts, convert_to_numpy=True, show_progress_bar=False)


def compute_semantic_similarity(model, text_a: str, text_b: str) -> float:
    """Cosine similarity between two texts in embedding space (0–1)."""
    embs = embed_texts(model, [text_a, text_b])
    sim  = cosine_similarity([embs[0]], [embs[1]])[0][0]
    return round(float(max(0.0, sim)), 4)


def _clean_context(context: str) -> str:
    """
    Strip metadata headers and boilerplate from the retrieved context string
    so that the embedding reflects the actual document content.
    Lines that are purely separators, collection names, or score annotations
    are removed before embedding.
    """
    import re
    lines = context.splitlines()
    clean = []
    for line in lines:
        stripped = line.strip()
        # Skip empty lines, separator lines, and common metadata patterns
        if not stripped:
            continue
        if re.match(r'^[-=]{3,}', stripped):          # ---, ===
            continue
        if re.match(r'^(Source|Collection|Score|Doc|Document|Result)\s*[:\d]', stripped, re.I):
            continue
        clean.append(stripped)
    cleaned = " ".join(clean)
    # Fallback: if cleaning removed everything, use original
    return cleaned if cleaned.strip() else context


def compute_faithfulness_proxy(model, answer: str, context: str) -> float:
    """
    Faithfulness proxy: cosine similarity between the answer and the
    retrieved context. High score → answer is semantically grounded in context.
    This is a proxy for RAGAS faithfulness (which needs an LLM judge).
    Context is cleaned of metadata headers before embedding.
    """
    clean = _clean_context(context)
    return compute_semantic_similarity(model, answer, clean)


def compute_context_relevance(model, question: str, context: str) -> float:
    """
    Context relevance: cosine similarity between question and retrieved context.
    High score → retrieval is on-topic (proxy for RAGAS context precision).
    Context is cleaned of metadata headers before embedding.
    """
    clean = _clean_context(context)
    return compute_semantic_similarity(model, question, clean)


def compute_bertscore(predictions: list, references: list) -> dict:
    """
    BERTScore precision, recall, F1 using contextual embeddings.
    Computed in batch at the end (more efficient than per-sample).

    NOTE: rescale_with_baseline is intentionally disabled — it requires
    pre-computed baseline files for each model/language and collapses
    scores toward 0 when the baseline is missing or mismatched.
    Raw BERTScore F1 for a healthy system is typically 0.85–0.92.
    """
    try:
        from bert_score import score as bert_score_fn
        P, R, F = bert_score_fn(
            predictions, references,
            lang="en", rescale_with_baseline=False,
            verbose=False, device="cpu"
        )
        return {
            "bertscore_precision": round(float(P.mean()), 4),
            "bertscore_recall":    round(float(R.mean()), 4),
            "bertscore_f1":        round(float(F.mean()), 4),
        }
    except Exception as e:
        print(f"  ⚠ BERTScore failed: {e}")
        return {"bertscore_precision": None, "bertscore_recall": None, "bertscore_f1": None}


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN EVALUATION LOOP
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_all(pipeline, embed_model) -> tuple:
    """
    Run every metric across all 30 Q&A evaluation samples.
    Returns (per_sample_results, aggregate_scores).
    """
    from eval_dataset import EVAL_QUESTIONS

    per_sample  = []
    predictions = []
    references  = []

    total = len(EVAL_QUESTIONS)

    print(f"\n{'='*60}")
    print(f"  Running Hybrid Evaluation ({total} samples)")
    print(f"{'='*60}\n")

    for i, item in enumerate(EVAL_QUESTIONS, 1):
        q      = item["question"]
        gt     = item["ground_truth"]
        domain = item.get("domain")
        dlabel = domain if domain else "all"

        print(f"  [{i:02d}/{total}] {dlabel:12s} | {q[:55]}...")

        # ── 1. Retrieve context from ChromaDB ─────────────────────────────
        context = pipeline.retrieval_engine.get_context_for_llm(
            q, domain=domain, n_results=3
        )

        # ── 2. Generate answer from the full pipeline ─────────────────────
        try:
            result = pipeline.process_query(q, domain=domain, n_context_results=3)
            answer = result["english_response"]
        except Exception as e:
            print(f"    ⚠ Pipeline error: {e}")
            answer = ""

        predictions.append(answer)
        references.append(gt)

        # ── 3. Compute per-sample metrics ─────────────────────────────────
        rouge      = compute_rouge(answer, gt)
        bleu       = compute_bleu(answer, gt)
        token_f1   = compute_token_f1(answer, gt)
        ans_sim    = compute_semantic_similarity(embed_model, answer, gt)
        faith      = compute_faithfulness_proxy(embed_model, answer, context)
        ctx_rel    = compute_context_relevance(embed_model, q, context)

        row = {
            "id":               i,
            "domain":           dlabel,
            "question":         q,
            "answer":           answer,
            "ground_truth":     gt,
            "context":          context[:200] + "..." if len(context) > 200 else context,
            # individual metrics
            "rouge1":           rouge["rouge1"],
            "rouge2":           rouge["rouge2"],
            "rougeL":           rouge["rougeL"],
            "bleu":             bleu,
            "token_precision":  token_f1["token_precision"],
            "token_recall":     token_f1["token_recall"],
            "token_f1":         token_f1["token_f1"],
            "answer_similarity":ans_sim,
            "faithfulness_proxy": faith,
            "context_relevance":  ctx_rel,
        }
        per_sample.append(row)

        # Brief log
        print(f"    ROUGE-L={rouge['rougeL']:.3f}  BLEU={bleu:.3f}  "
              f"Sim={ans_sim:.3f}  Faith={faith:.3f}  CtxRel={ctx_rel:.3f}")

    # ── 4. BERTScore (batch) ──────────────────────────────────────────────
    print("\n  Computing BERTScore (batch)...")
    bs = compute_bertscore(predictions, references)
    print(f"  BERTScore F1 = {bs['bertscore_f1']}")

    # ── 5. Aggregate ──────────────────────────────────────────────────────
    def avg(key):
        vals = [r[key] for r in per_sample if r.get(key) is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    aggregate = {
        "rouge1":             avg("rouge1"),
        "rouge2":             avg("rouge2"),
        "rougeL":             avg("rougeL"),
        "bleu":               avg("bleu"),
        "token_precision":    avg("token_precision"),
        "token_recall":       avg("token_recall"),
        "token_f1":           avg("token_f1"),
        "answer_similarity":  avg("answer_similarity"),
        "faithfulness_proxy": avg("faithfulness_proxy"),
        "context_relevance":  avg("context_relevance"),
        "bertscore_precision": bs["bertscore_precision"],
        "bertscore_recall":    bs["bertscore_recall"],
        "bertscore_f1":        bs["bertscore_f1"],
    }

    return per_sample, aggregate, bs


# ─────────────────────────────────────────────────────────────────────────────
#  PER-DOMAIN BREAKDOWN
# ─────────────────────────────────────────────────────────────────────────────

def domain_breakdown(per_sample: list) -> dict:
    """Average each metric per domain."""
    domains = {}
    for row in per_sample:
        d = row["domain"]
        if d not in domains:
            domains[d] = []
        domains[d].append(row)

    result = {}
    metric_keys = [
        "rouge1", "rouge2", "rougeL", "bleu",
        "token_f1", "answer_similarity",
        "faithfulness_proxy", "context_relevance",
    ]
    for domain, rows in domains.items():
        result[domain] = {
            k: round(sum(r[k] for r in rows if r.get(k) is not None) / len(rows), 4)
            for k in metric_keys
        }
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  PRINT RESULTS TABLE
# ─────────────────────────────────────────────────────────────────────────────

METRIC_DISPLAY = [
    ("rouge1",              "ROUGE-1 F1              (n-gram unigram overlap)"),
    ("rouge2",              "ROUGE-2 F1              (n-gram bigram overlap)"),
    ("rougeL",              "ROUGE-L F1              (longest common subsequence)"),
    ("bleu",                "BLEU                    (n-gram precision, smoothed)"),
    ("token_f1",            "Token F1                (SQuAD-style token overlap)"),
    ("answer_similarity",   "Answer Semantic Sim.    (sentence-transformers cosine)"),
    ("faithfulness_proxy",  "Faithfulness Proxy      (answer ↔ context cosine)"),
    ("context_relevance",   "Context Relevance       (question ↔ context cosine)"),
    ("bertscore_f1",        "BERTScore F1            (contextual embeddings)"),
]

def print_results_table(aggregate: dict, elapsed: float, n_samples: int):
    def rating(v):
        if v is None:  return "  N/A   "
        if v >= 0.70:  return "EXCELLENT"
        if v >= 0.50:  return "  GOOD  "
        if v >= 0.35:  return "  FAIR  "
        return          "  POOR  "

    print(f"\n{'='*72}")
    print("  EVALUATION RESULTS — Health AI Chatbot RAG System")
    print(f"{'='*72}")
    print(f"  {'Metric':<45} {'Score':>8}  {'Rating'}")
    print(f"  {'-'*68}")

    valid_scores = []
    for key, label in METRIC_DISPLAY:
        v      = aggregate.get(key)
        vs     = f"{v:.4f}" if v is not None else "  N/A  "
        rat    = rating(v)
        print(f"  {label:<45} {vs:>8}  {rat}")
        if v is not None:
            valid_scores.append(v)

    overall = sum(valid_scores) / len(valid_scores) if valid_scores else 0
    print(f"  {'-'*68}")
    print(f"  {'Overall Average':<45} {overall:.4f}")
    print(f"{'='*72}")
    print(f"\n  Samples: {n_samples}  |  Time: {elapsed:.1f}s  |  LLM: Llama 3.2 (generation only)")
    print(f"{'='*72}\n")
    return overall


# ─────────────────────────────────────────────────────────────────────────────
#  SAVE
# ─────────────────────────────────────────────────────────────────────────────

def save_results(aggregate, overall, breakdown, per_sample, elapsed):
    output = {
        "metadata": {
            "timestamp":           datetime.now().isoformat(),
            "system":              "Health AI Chatbot — RAG + Llama 3.2",
            "llm_generation":      "Ollama llama3.2",
            "llm_judge":           "None (no LLM judge — embedding/n-gram metrics)",
            "embeddings":          "all-MiniLM-L6-v2 (sentence-transformers)",
            "vector_db":           "ChromaDB (persistent, local)",
            "n_samples":           len(per_sample),
            "evaluation_time_s":   round(elapsed, 2),
        },
        "overall_scores":   aggregate,
        "overall_average":  round(overall, 4),
        "domain_breakdown": breakdown,
        "per_sample_results": per_sample,
    }

    path = RESULTS_DIR / "scores.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"✓ Saved: {path}")

    # CSV
    import csv
    csv_path = RESULTS_DIR / "scores.csv"
    if per_sample:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=per_sample[0].keys())
            writer.writeheader()
            writer.writerows(per_sample)
        print(f"✓ Saved: {csv_path}")


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  Health AI Chatbot — Hybrid Academic Evaluation")
    print("=" * 60)

    # ── 1. Load sentence-transformers model ───────────────────────────────
    print("\n[1/4] Loading embedding model (all-MiniLM-L6-v2)...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✓ Embedding model ready")

    # ── 2. Initialize RAG pipeline ────────────────────────────────────────
    print("\n[2/4] Initializing RAG LLM Pipeline...")
    try:
        from llm.rag_llm_pipeline import RAGLLMPipeline
        pipeline = RAGLLMPipeline()
    except Exception as e:
        print(f"✗ Pipeline failed: {e}")
        print("  Make sure Ollama is running: ollama serve")
        sys.exit(1)

    # ── 3. Run evaluation ─────────────────────────────────────────────────
    print("\n[3/4] Running evaluation across all 30 samples...")
    start = time.time()
    per_sample, aggregate, bs = evaluate_all(pipeline, embed_model)
    elapsed = time.time() - start

    # ── 4. Report & save ──────────────────────────────────────────────────
    print("\n[4/4] Computing results...")
    overall   = print_results_table(aggregate, elapsed, len(per_sample))
    breakdown = domain_breakdown(per_sample)

    print("\nDomain Breakdown (ROUGE-L | Sim | Faithfulness | CtxRel):")
    for domain, metrics in breakdown.items():
        print(f"  {domain:<15} ROUGE-L={metrics['rougeL']:.3f}  "
              f"Sim={metrics['answer_similarity']:.3f}  "
              f"Faith={metrics['faithfulness_proxy']:.3f}  "
              f"Ctx={metrics['context_relevance']:.3f}")

    save_results(aggregate, overall, breakdown, per_sample, elapsed)

    print("\n✅ Evaluation complete!")
    print("   → Run: python evaluation/generate_report.py")
    print("     to generate the full academic Markdown report + charts.\n")


if __name__ == "__main__":
    main()
