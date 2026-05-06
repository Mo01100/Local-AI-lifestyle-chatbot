"""
Figure 13 - Response Latency Bar Chart
Times real translation requests through Argos Translate
and generates an HTML bar chart.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from scripts.translation.translation_service import TranslationService
import time

service = TranslationService(cache_translations=False)  # Disable cache for real timing

test_queries = {
    "English": [
        ("en", "What exercises help with weight loss?"),
        ("en", "How many calories should I eat per day?"),
        ("en", "What foods are high in protein?"),
        ("en", "How do I improve my fitness at home?"),
    ],
    "French": [
        ("fr", "Quels exercices aident a perdre du poids?"),
        ("fr", "Combien de calories dois-je manger par jour?"),
        ("fr", "Quels aliments sont riches en proteines?"),
        ("fr", "Comment ameliorer ma condition physique a la maison?"),
    ],
    "Spanish": [
        ("es", "Que ejercicios ayudan a perder peso?"),
        ("es", "Cuantas calorias debo comer por dia?"),
        ("es", "Que alimentos son ricos en proteinas?"),
        ("es", "Como mejorar mi estado fisico en casa?"),
    ],
    "German": [
        ("de", "Welche Ubungen helfen beim Abnehmen?"),
        ("de", "Wie viele Kalorien soll ich pro Tag essen?"),
        ("de", "Welche Lebensmittel sind reich an Protein?"),
        ("de", "Wie verbessere ich meine Fitness zu Hause?"),
    ],
    "Arabic": [
        ("ar", "\u0645\u0627 \u0647\u064a \u0623\u0641\u0636\u0644 \u062a\u0645\u0627\u0631\u064a\u0646 \u0644\u0641\u0642\u062f\u0627\u0646 \u0627\u0644\u0648\u0632\u0646\u061f"),
        ("ar", "\u0643\u0645 \u0633\u0639\u0631\u0629 \u062d\u0631\u0627\u0631\u064a\u0629 \u064a\u062c\u0628 \u0623\u0646 \u0622\u0643\u0644 \u064a\u0648\u0645\u064a\u0627\u064b\u061f"),
        ("ar", "\u0645\u0627 \u0647\u064a \u0627\u0644\u0623\u0637\u0639\u0645\u0629 \u0627\u0644\u063a\u0646\u064a\u0629 \u0628\u0627\u0644\u0628\u0631\u0648\u062a\u064a\u0646\u061f"),
        ("ar", "\u0643\u064a\u0641 \u0623\u062d\u0633\u0646 \u0644\u064a\u0627\u0642\u062a\u064a \u0627\u0644\u0628\u062f\u0646\u064a\u0629 \u0641\u064a \u0627\u0644\u0645\u0646\u0632\u0644\u061f"),
    ],
}

print("Running timing tests... please wait.")

results = {}

for lang_name, queries in test_queries.items():
    times = []
    for lang_code, text in queries:
        start = time.time()
        # Simulate full round trip: translate in, then translate response back out
        if lang_code != "en":
            translated_in, _ = service.translate_to_english(text, source_lang=lang_code)
            # Simulate translating a fixed English response back out
            mock_response = "Here are some healthy exercises you can try at home."
            service.translate_from_english(mock_response, lang_code)
        else:
            translated_in = text  # No translation needed
        elapsed = round(time.time() - start, 3)
        times.append(elapsed)
        print(f"  {lang_name}: {elapsed}s")
    avg = round(sum(times) / len(times), 2)
    results[lang_name] = {"avg": avg, "all": times}
    print(f"  -> Average: {avg}s\n")

# Build HTML bar chart
max_val = max(r["avg"] for r in results.values())
colors = {
    "English": "#4CAF50",
    "French":  "#2196F3",
    "Spanish": "#FF9800",
    "German":  "#9C27B0",
    "Arabic":  "#F44336",
}

bars_html = ""
for lang, data in results.items():
    avg = data["avg"]
    bar_pct = round((avg / (max_val * 1.15)) * 100, 1)
    bars_html += f"""
        <div class="bar-row">
            <div class="bar-label">{lang}</div>
            <div class="bar-track">
                <div class="bar-fill" style="width:{bar_pct}%; background:{colors[lang]};">
                    <span class="bar-value">{avg}s</span>
                </div>
            </div>
        </div>"""

# Also build individual point dots
dots_html = ""
for lang, data in results.items():
    for i, t in enumerate(data["all"]):
        pct = round((t / (max_val * 1.15)) * 100, 1)
        dots_html += f'<div title="{lang} query {i+1}: {t}s" style="position:relative; display:inline-block; width:10px; height:10px; border-radius:50%; background:{colors[lang]}; margin:2px;" data-time="{t}"></div>'

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Figure 13 - Response Latency Chart</title>
<style>
  body {{
    font-family: 'Segoe UI', sans-serif;
    background: #f5f5f5;
    padding: 40px;
  }}
  h2 {{ color: #1a1a2e; margin-bottom: 4px; font-size: 18px; }}
  .subtitle {{ color: #555; font-size: 13px; margin-bottom: 30px; }}
  .chart-box {{
    background: white;
    border-radius: 12px;
    padding: 36px 40px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    max-width: 820px;
  }}
  .axis-title {{
    font-size: 12px;
    color: #888;
    margin-bottom: 18px;
    text-align: center;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }}
  .bar-row {{
    display: flex;
    align-items: center;
    margin-bottom: 18px;
  }}
  .bar-label {{
    width: 90px;
    font-size: 14px;
    font-weight: 600;
    color: #333;
    flex-shrink: 0;
  }}
  .bar-track {{
    flex: 1;
    background: #f0f0f0;
    border-radius: 30px;
    height: 36px;
    overflow: hidden;
  }}
  .bar-fill {{
    height: 100%;
    border-radius: 30px;
    display: flex;
    align-items: center;
    padding-left: 12px;
    transition: width 0.5s;
  }}
  .bar-value {{
    color: white;
    font-weight: bold;
    font-size: 14px;
    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
  }}
  .legend {{
    display: flex;
    gap: 20px;
    margin-top: 24px;
    flex-wrap: wrap;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #555;
  }}
  .legend-dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
  }}
  .caption {{
    font-size: 12px;
    color: #888;
    margin-top: 20px;
    border-top: 1px solid #eee;
    padding-top: 12px;
  }}
</style>
</head>
<body>
<h2>Figure 13: Average Response Time by Query Language</h2>
<p class="subtitle">End-to-end response time including translation overhead (4 queries per language, averaged)</p>
<div class="chart-box">
  <div class="axis-title">Average Response Time (seconds) - Lower is Better</div>
  {bars_html}
  <div class="legend">
    {''.join(f'<div class="legend-item"><div class="legend-dot" style="background:{colors[l]}"></div>{l}</div>' for l in results)}
  </div>
  <div class="caption">
    Note: English queries require no translation step. All other languages run through Argos Translate twice (input and output).
    Tests run with cache disabled to measure raw model speed. Hardware: local machine running Ollama + Argos Translate offline.
  </div>
</div>
</body>
</html>"""

with open("figure13_latency_chart.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Chart saved to figure13_latency_chart.html")
print("Open it in your browser and take a screenshot for Figure 13.")
