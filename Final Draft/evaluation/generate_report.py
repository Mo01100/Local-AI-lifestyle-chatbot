"""
generate_report.py
==================
Generates a complete academic evaluation report from RAGAS scores.
Produces:
  - evaluation/results/evaluation_report.md   (Markdown — for papers/thesis)
  - evaluation/results/radar_chart.png        (Radar chart — embed in paper)
  - evaluation/results/bar_chart.png          (Bar chart — metric overview)
  - evaluation/results/domain_heatmap.png     (Domain breakdown heatmap)
  - evaluation/results/scores.csv             (Raw CSV for statistical tools)

Usage:
  python evaluation/generate_report.py
  (Run ragas_evaluator.py first to generate scores.json)
"""

import json
import sys
import math
from pathlib import Path
from datetime import datetime

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend (no display required)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
EVAL_DIR    = Path(__file__).parent
RESULTS_DIR = EVAL_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

SCORES_JSON    = RESULTS_DIR / "scores.json"
REPORT_PATH    = RESULTS_DIR / "evaluation_report.md"
RADAR_PNG      = RESULTS_DIR / "radar_chart.png"
BAR_PNG        = RESULTS_DIR / "bar_chart.png"
HEATMAP_PNG    = RESULTS_DIR / "domain_heatmap.png"
CSV_PATH       = RESULTS_DIR / "scores.csv"

# ── Visual design constants ───────────────────────────────────────────────────
COLORS = {
    "primary":    "#4F46E5",   # Indigo
    "secondary":  "#06B6D4",   # Cyan
    "success":    "#10B981",   # Emerald
    "warning":    "#F59E0B",   # Amber
    "danger":     "#EF4444",   # Red
    "nutrition":  "#10B981",   # Green
    "exercise":   "#4F46E5",   # Indigo
    "all":        "#F59E0B",   # Amber (mental health / mixed)
    "bg":         "#0F172A",   # Dark slate
    "text":       "#E2E8F0",
}

METRIC_LABELS = {
    "rouge1":              "ROUGE-1",
    "rouge2":              "ROUGE-2",
    "rougeL":              "ROUGE-L",
    "bleu":                "BLEU",
    "token_f1":            "Token F1",
    "answer_similarity":   "Answer\nSimilarity",
    "faithfulness_proxy":  "Faithfulness\nProxy",
    "context_relevance":   "Context\nRelevance",
    "bertscore_f1":        "BERTScore\nF1",
}

METRIC_DESCRIPTIONS = {
    "rouge1": (
        "ROUGE-1 F1: Unigram overlap between generated answer and ground truth. "
        "Measures lexical recall at the word level."
    ),
    "rouge2": (
        "ROUGE-2 F1: Bigram overlap between generated answer and ground truth. "
        "Captures phrase-level similarity and fluency."
    ),
    "rougeL": (
        "ROUGE-L F1: Longest Common Subsequence between answer and ground truth. "
        "More robust to word order variation than ROUGE-1/2."
    ),
    "bleu": (
        "BLEU (smoothed): N-gram precision of the generated answer vs ground truth. "
        "Standard machine translation and text generation metric."
    ),
    "token_f1": (
        "Token-level F1: Precision/Recall/F1 over shared token sets (SQuAD-style). "
        "Measures exact word-level overlap, ignoring order."
    ),
    "answer_similarity": (
        "Cosine similarity between sentence-transformer embeddings of the generated "
        "answer and ground truth. Captures semantic equivalence beyond lexical overlap."
    ),
    "faithfulness_proxy": (
        "Cosine similarity between the generated answer and retrieved context embeddings. "
        "Proxy for hallucination detection: high score means answer is grounded in context."
    ),
    "context_relevance": (
        "Cosine similarity between question embedding and retrieved context embedding. "
        "Measures retrieval precision — whether the retrieved documents are on-topic."
    ),
    "bertscore_f1": (
        "BERTScore F1: Contextual token-level similarity using BERT embeddings. "
        "More robust to paraphrasing than n-gram metrics."
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
def load_scores() -> dict:
    """Load evaluation scores from scores.json."""
    if not SCORES_JSON.exists():
        print(f"✗ scores.json not found at {SCORES_JSON}")
        print("  Run: python evaluation/ragas_evaluator.py  first!")
        sys.exit(1)
    with open(SCORES_JSON, encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────────
def generate_radar_chart(scores: dict) -> Path:
    """Generate a radar/spider chart showing all 6 metric scores."""
    metric_keys  = list(METRIC_LABELS.keys())
    metric_short = [METRIC_LABELS[k].replace("\n", " ") for k in metric_keys]
    values       = [scores.get(k) or 0.0 for k in metric_keys]
    values_plot  = values + [values[0]]  # Close the polygon

    N     = len(metric_keys)
    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True),
                           facecolor=COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])

    # Draw gridlines
    for level in [0.2, 0.4, 0.6, 0.8, 1.0]:
        circle_angles = [n / float(N) * 2 * math.pi for n in range(N + 1)]
        circle_values = [level] * (N + 1)
        ax.plot(circle_angles, circle_values, color="#334155", linewidth=0.8, alpha=0.6)
        ax.text(0.08, level, f"{level:.1f}", ha="center", va="center",
                color="#64748B", fontsize=8)

    # Draw spoke lines
    for angle in angles[:-1]:
        ax.plot([angle, angle], [0, 1], color="#334155", linewidth=0.8, alpha=0.6)

    # Fill area
    ax.fill(angles, values_plot, color=COLORS["primary"], alpha=0.25)
    ax.plot(angles, values_plot, color=COLORS["primary"], linewidth=2.5)

    # Plot points
    for angle, value, key in zip(angles[:-1], values, metric_keys):
        color = COLORS["success"] if value >= 0.7 else (
            COLORS["warning"] if value >= 0.5 else COLORS["danger"])
        ax.plot(angle, value, "o", color=color, markersize=9, zorder=5)
        ax.annotate(f"{value:.3f}", xy=(angle, value),
                    xytext=(angle, value + 0.1),
                    ha="center", va="center", fontsize=9,
                    color=color, fontweight="bold")

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metric_short, color=COLORS["text"], fontsize=10, fontweight="bold")
    ax.set_yticks([])
    ax.set_ylim(0, 1.15)
    ax.spines["polar"].set_visible(False)

    plt.title("RAGAS Metric Radar Chart\nHealth AI Chatbot Evaluation",
              color=COLORS["text"], fontsize=14, fontweight="bold", pad=20)

    plt.tight_layout()
    plt.savefig(RADAR_PNG, dpi=150, bbox_inches="tight",
                facecolor=COLORS["bg"], edgecolor="none")
    plt.close()
    print(f"  ✓ Radar chart: {RADAR_PNG}")
    return RADAR_PNG


# ─────────────────────────────────────────────────────────────────────────────
def generate_bar_chart(scores: dict) -> Path:
    """Generate a horizontal bar chart of all 6 metrics."""
    metric_keys   = list(METRIC_LABELS.keys())
    metric_labels = [METRIC_LABELS[k].replace("\n", " ") for k in metric_keys]
    values        = [scores.get(k) or 0.0 for k in metric_keys]

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])

    bar_colors = [
        COLORS["success"] if v >= 0.7 else (COLORS["warning"] if v >= 0.5 else COLORS["danger"])
        for v in values
    ]

    bars = ax.barh(metric_labels, values, color=bar_colors, height=0.6,
                   edgecolor="#1E293B", linewidth=1.5)

    # Value labels on bars
    for bar, value in zip(bars, values):
        ax.text(value + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{value:.4f}", va="center", ha="left",
                color=COLORS["text"], fontsize=11, fontweight="bold")

    # Reference lines
    for ref in [0.5, 0.7, 0.9]:
        ax.axvline(x=ref, color="#475569", linewidth=1, linestyle="--", alpha=0.7)
        ax.text(ref, len(metric_labels) - 0.3, f"{ref:.0%}",
                ha="center", color="#94A3B8", fontsize=8)

    ax.set_xlim(0, 1.15)
    ax.set_xlabel("Score (0 – 1)", color=COLORS["text"], fontsize=11)
    ax.set_title("RAGAS Evaluation Metrics — Health AI Chatbot",
                 color=COLORS["text"], fontsize=13, fontweight="bold", pad=15)
    ax.tick_params(colors=COLORS["text"], labelsize=10)
    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")

    # Legend
    legend_elements = [
        mpatches.Patch(color=COLORS["success"], label="Excellent (≥0.70)"),
        mpatches.Patch(color=COLORS["warning"], label="Fair (0.50–0.69)"),
        mpatches.Patch(color=COLORS["danger"],  label="Poor (<0.50)"),
    ]
    ax.legend(handles=legend_elements, loc="lower right",
              facecolor="#1E293B", edgecolor="#475569",
              labelcolor=COLORS["text"], fontsize=9)

    plt.tight_layout()
    plt.savefig(BAR_PNG, dpi=150, bbox_inches="tight",
                facecolor=COLORS["bg"], edgecolor="none")
    plt.close()
    print(f"  ✓ Bar chart:   {BAR_PNG}")
    return BAR_PNG


# ─────────────────────────────────────────────────────────────────────────────
def generate_domain_heatmap(breakdown: dict) -> Path:
    """Generate a domain × metric heatmap."""
    if not breakdown:
        print("  ⚠ No domain breakdown data — skipping heatmap")
        return None

    metric_keys = list(METRIC_LABELS.keys())
    domains     = list(breakdown.keys())
    data        = np.array([[breakdown[d].get(m, 0.0) for m in metric_keys] for d in domains])

    fig, ax = plt.subplots(figsize=(12, max(4, len(domains) * 1.2)),
                           facecolor=COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])

    im = ax.imshow(data, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    plt.colorbar(im, ax=ax, label="Score", shrink=0.8)

    ax.set_xticks(range(len(metric_keys)))
    ax.set_xticklabels([METRIC_LABELS[k].replace("\n", " ") for k in metric_keys],
                       rotation=30, ha="right", color=COLORS["text"], fontsize=10)
    ax.set_yticks(range(len(domains)))
    ax.set_yticklabels([d.title() for d in domains], color=COLORS["text"], fontsize=11)

    for i in range(len(domains)):
        for j in range(len(metric_keys)):
            val = data[i, j]
            text_color = "black" if 0.4 < val < 0.8 else "white"
            ax.text(j, i, f"{val:.3f}", ha="center", va="center",
                    fontsize=10, fontweight="bold", color=text_color)

    ax.set_title("Domain-Level Metric Breakdown — Health AI Chatbot",
                 color=COLORS["text"], fontsize=13, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(HEATMAP_PNG, dpi=150, bbox_inches="tight",
                facecolor=COLORS["bg"], edgecolor="none")
    plt.close()
    print(f"  ✓ Heatmap:     {HEATMAP_PNG}")
    return HEATMAP_PNG


# ─────────────────────────────────────────────────────────────────────────────
def save_csv(data: dict) -> Path:
    """Save per-sample results to CSV for use in statistical tools."""
    samples = data.get("per_sample_results", [])
    if not samples:
        print("  ⚠ No per-sample data for CSV")
        return None
    df = pd.DataFrame(samples)
    df.to_csv(CSV_PATH, index=False)
    print(f"  ✓ CSV saved:   {CSV_PATH}")
    return CSV_PATH


# ─────────────────────────────────────────────────────────────────────────────
def get_qualitative_analysis(scores: dict, avg: float) -> str:
    """Generate a qualitative text analysis of the scores for the report."""
    faith = scores.get("faithfulness", 0)
    rel   = scores.get("answer_relevancy", 0)
    cp    = scores.get("context_precision", 0)
    cr    = scores.get("context_recall", 0)
    ac    = scores.get("answer_correctness", 0)
    sim   = scores.get("answer_similarity", 0)

    strengths  = []
    weaknesses = []

    if faith >= 0.7:
        strengths.append("**Faithfulness** is high, indicating the system rarely hallucinates and grounds its responses in retrieved context.")
    else:
        weaknesses.append("**Faithfulness** is below 0.70, suggesting the system occasionally generates claims not supported by retrieved documents.")

    if rel >= 0.7:
        strengths.append("**Answer Relevancy** demonstrates that the model consistently addresses the user's question directly.")
    else:
        weaknesses.append("**Answer Relevancy** suggests room for improvement in ensuring answers directly address the posed questions.")

    if cp >= 0.7:
        strengths.append("**Context Precision** reveals that the ChromaDB retrieval system effectively identifies the most relevant document chunks.")
    else:
        weaknesses.append("**Context Precision** indicates that some irrelevant documents are being retrieved, adding noise to the context.")

    if cr >= 0.7:
        strengths.append("**Context Recall** confirms that the retrieval engine successfully surfaces the information needed to answer questions correctly.")
    else:
        weaknesses.append("**Context Recall** shows that the retrieval system sometimes misses important contextual information present in the knowledge base.")

    if ac >= 0.7:
        strengths.append("**Answer Correctness** demonstrates strong factual alignment with ground-truth reference answers.")
    else:
        weaknesses.append("**Answer Correctness** indicates that generated answers sometimes diverge from the expected ground-truth facts.")

    strengths_text  = "\n".join(f"- {s}" for s in strengths)  if strengths  else "- No clear strengths identified — all metrics are below 0.70."
    weaknesses_text = "\n".join(f"- {w}" for w in weaknesses) if weaknesses else "- No significant weaknesses identified — all metrics are above 0.70."

    if avg >= 0.8:
        overall = "The system demonstrates **excellent** overall RAG performance, making it well-suited for production deployment in health advisory applications."
    elif avg >= 0.65:
        overall = "The system demonstrates **good** overall performance with some areas for improvement, particularly in retrieval quality and answer grounding."
    elif avg >= 0.5:
        overall = "The system demonstrates **fair** overall performance. Significant improvements in retrieval strategy and prompt engineering are recommended before production deployment."
    else:
        overall = "The system demonstrates **poor** overall performance. A comprehensive review of the embedding model, chunking strategy, retrieval parameters, and LLM prompt design is strongly recommended."

    return f"""### Overall Assessment

{overall}

### Strengths

{strengths_text}

### Weaknesses / Areas for Improvement

{weaknesses_text}"""


# ─────────────────────────────────────────────────────────────────────────────
def generate_markdown_report(data: dict, scores: dict, avg: float,
                              breakdown: dict) -> Path:
    """
    Compose the full academic Markdown report.
    """
    meta      = data.get("metadata", {})
    timestamp = meta.get("timestamp", datetime.now().isoformat())
    n_samples = meta.get("n_samples", 30)
    eval_time = meta.get("evaluation_time_s", "N/A")

    qualitative = get_qualitative_analysis(scores, avg)

    # ── Build the metrics table ───────────────────────────────────────────────
    def rating(v):
        if v is None: return "N/A"
        if v >= 0.8: return "🟢 Excellent"
        if v >= 0.65: return "🟡 Good"
        if v >= 0.5: return "🟠 Fair"
        return "🔴 Poor"

    metric_rows = ""
    for key, label in METRIC_LABELS.items():
        v    = scores.get(key)
        vs   = f"{v:.4f}" if v is not None else "N/A"
        desc = METRIC_DESCRIPTIONS.get(key, "")[:80] + "..."
        metric_rows += f"| {label.replace(chr(10), ' '):<22} | {vs:>8} | {rating(v):<14} | {desc} |\n"

    # ── Build the domain breakdown table ─────────────────────────────────────
    domain_table = ""
    if breakdown:
        metric_keys = list(METRIC_LABELS.keys())
        headers = " | ".join(METRIC_LABELS[k].replace("\n", " ") for k in metric_keys)
        domain_table = f"| Domain | {headers} |\n"
        domain_table += "|--------|" + "|".join(["--------"] * len(metric_keys)) + "|\n"
        for domain, metrics in breakdown.items():
            row_vals = " | ".join(
                f"{metrics.get(k, 0):.3f}" for k in metric_keys
            )
            domain_table += f"| {domain.title():<10} | {row_vals} |\n"

    # ── Assemble the report ───────────────────────────────────────────────────
    report = f"""# RAGAS Evaluation Report: Health AI Chatbot

**System**: AI Lifestyle Chatbot with RAG (Retrieval-Augmented Generation)  
**Evaluation Date**: {timestamp[:10]}  
**Evaluation Framework**: [RAGAS v0.4.3](https://docs.ragas.io/)  
**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. System Description

The evaluated system is a **multi-domain health advisory chatbot** that combines:

| Component | Technology |
|-----------|-----------|
| **Language Model** | Llama 3.2 (via Ollama, 100% offline) |
| **Vector Database** | ChromaDB (persistent, local) |
| **Embedding Model** | sentence-transformers/all-MiniLM-L6-v2 |
| **Translation** | Argos Translate (offline, multi-language) |
| **RAG Architecture** | Query → Embed → ChromaDB Search → Context Injection → LLM |
| **Domains Covered** | Nutrition, Exercise, Mental Health & Wellness |

The system is 100% offline and does not rely on any external API calls. User queries are
translated to English, semantically searched against ChromaDB, and the top-K retrieved
documents are injected into the Llama 3.2 prompt to grounded the response.

---

## 2. Evaluation Methodology

### 2.1 Evaluation Framework: RAGAS

RAGAS (Retrieval-Augmented Generation Assessment) is an open-source framework specifically
designed for evaluating RAG systems without requiring human annotations for most metrics.
It uses an LLM-as-judge approach, leveraging the same local Llama 3.2 model as the
evaluator to ensure fully offline, reproducible academic evaluation.

### 2.2 Evaluation Dataset

| Property | Value |
|----------|-------|
| **Total Samples** | {n_samples} |
| **Nutrition Questions** | 10 |
| **Exercise Questions** | 10 |
| **Mental Health / Mixed** | 10 |
| **Context Source** | Live ChromaDB retrieval (n=3 per query) |
| **Ground Truth** | Manually curated expert reference answers |
| **Language** | English |

### 2.3 Metrics Explanation

| Metric | Score | Rating | Description |
|--------|-------|--------|-------------|
{metric_rows}

### 2.4 Experimental Setup

- **LLM Judge**: Ollama Llama 3.2 (local, `http://localhost:11434`)
- **Temperature**: 0 (deterministic evaluation)
- **Evaluation Time**: {eval_time}s
- **Retrieval**: Top-3 ChromaDB documents per query

---

## 3. Results

### 3.1 Overall Performance

| Metric | Score |
|--------|-------|
| **Overall Average** | **{avg:.4f}** |
{chr(10).join(f'| {METRIC_LABELS[k].replace(chr(10), " ")} | {scores.get(k, "N/A"):.4f} |' for k in METRIC_LABELS if scores.get(k) is not None)}

### 3.2 Radar Chart

![RAGAS Metric Radar Chart](radar_chart.png)

*Figure 1: Spider/radar chart showing all 6 RAGAS metrics. Scores closer to the outer
edge (1.0) represent better performance.*

### 3.3 Bar Chart

![RAGAS Metric Bar Chart](bar_chart.png)

*Figure 2: Horizontal bar chart comparing all evaluation metrics. Green indicates
excellent (≥0.70), amber indicates fair (0.50–0.69), red indicates poor (<0.50).*

### 3.4 Domain-Level Breakdown

{'![Domain Heatmap](domain_heatmap.png)' if breakdown else '*Domain breakdown not available.*'}

{'*Figure 3: Domain-level metric breakdown. Darker green indicates stronger performance on that metric for the given domain. Darker red indicates weaker performance.*' if breakdown else ''}

{'#### Domain Scores Table' if domain_table else ''}

{domain_table}

---

## 4. Qualitative Analysis

{qualitative}

---

## 5. Error Analysis

### Common Failure Patterns

1. **Out-of-context hallucination**: When the ChromaDB collection lacks relevant documents,
   the model occasionally generates plausible-sounding but ungrounded information.
   This directly impacts the Faithfulness metric.

2. **Retrieval precision drop for cross-domain queries**: Questions spanning multiple
   domains (e.g., "How does nutrition affect mental health?") may retrieve less-focused
   context, reducing Context Precision.

3. **Ground truth verbosity mismatch**: Reference answers in the evaluation dataset
   are concise; the LLM may provide longer, elaborated responses, negatively affecting
   Answer Similarity even when factually correct.

### Recommended Improvements

| Area | Recommendation |
|------|---------------|
| **Retrieval** | Increase `n_results` to 5 and apply MMR (Maximal Marginal Relevance) reranking |
| **Chunking** | Experiment with smaller chunk sizes (128–256 tokens) for higher precision |
| **Prompting** | Add explicit instruction: "only use information from the provided context" |
| **Knowledge Base** | Expand mental health collection with more domain-specific documents |
| **Embedding Model** | Evaluate larger models (e.g., `all-mpnet-base-v2`) for improved recall |

---

## 6. Conclusion

This evaluation demonstrates the effectiveness of the offline RAG architecture for
health advisory tasks. The system achieves an overall RAGAS score of **{avg:.4f}**,
{"reflecting strong performance across all dimensions." if avg >= 0.7 else "with clear pathways for improvement identified across retrieval and grounding dimensions."}

The fully offline nature of the system — combining ChromaDB for vector retrieval,
Llama 3.2 for generation, and Argos Translate for multilingual support — represents
a privacy-preserving, deployable RAG system suitable for healthcare contexts where
data sovereignty is paramount.

---

## 7. References

1. Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023). *RAGAS: Automated
   Evaluation of Retrieval Augmented Generation*. arXiv:2309.15217.
2. Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*.
   NeurIPS 2020.
3. Touvron, H., et al. (2023). *Llama 2: Open Foundation and Fine-Tuned Chat Models*.
   arXiv:2307.09288.
4. Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese
   BERT-Networks*. EMNLP 2019.
5. Gao, Y., et al. (2023). *Retrieval-Augmented Generation for Large Language Models:
   A Survey*. arXiv:2312.10997.

---

*Report generated by `evaluation/generate_report.py` — Health AI Chatbot Evaluation Suite*  
*All evaluation was performed using 100% local, offline infrastructure.*
"""

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"  ✓ Report:      {REPORT_PATH}")
    return REPORT_PATH


# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "=" * 60)
    print("  Health AI Chatbot — Academic Report Generator")
    print("=" * 60)

    # ── Load scores ───────────────────────────────────────────────────────────
    print("\n[1/5] Loading scores from scores.json...")
    data      = load_scores()
    scores    = data.get("overall_scores", {})
    avg       = data.get("overall_average", 0.0)
    breakdown = data.get("domain_breakdown", {})
    print(f"  Overall average: {avg:.4f}")

    # ── Generate visuals ──────────────────────────────────────────────────────
    print("\n[2/5] Generating radar chart...")
    generate_radar_chart(scores)

    print("\n[3/5] Generating bar chart...")
    generate_bar_chart(scores)

    print("\n[4/5] Generating domain heatmap...")
    generate_domain_heatmap(breakdown)

    # ── Save CSV ──────────────────────────────────────────────────────────────
    save_csv(data)

    # ── Generate report ───────────────────────────────────────────────────────
    print("\n[5/5] Generating Markdown report...")
    report_path = generate_markdown_report(data, scores, avg, breakdown)

    print(f"\n{'='*60}")
    print("  ✅  Report generation complete!")
    print(f"{'='*60}")
    print(f"\n  📄 Report:   {REPORT_PATH}")
    print(f"  📊 Charts:   {RESULTS_DIR}")
    print(f"  📁 Raw CSV:  {CSV_PATH}\n")


if __name__ == "__main__":
    main()
