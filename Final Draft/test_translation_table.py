"""
Translation Quality Test for Chapter 4 - Figure 12
Outputs results to an HTML file to handle Arabic Unicode correctly.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from scripts.translation.translation_service import TranslationService
import time

service = TranslationService(cache_translations=True)

lang_names = {
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "ar": "Arabic",
}

test_cases = [
    ("fr", "Quels exercices puis-je faire pour perdre du poids ?"),
    ("fr", "Combien de calories brule une heure de marche ?"),
    ("fr", "Quelle est la meilleure alimentation pour les muscles ?"),
    ("fr", "Puis-je faire du sport avec une blessure au genou ?"),
    ("es", "Cuantos vasos de agua debo beber al dia?"),
    ("es", "Cuales son los mejores ejercicios para el abdomen?"),
    ("es", "Como puedo mejorar mi resistencia fisica?"),
    ("es", "Que debo comer antes de hacer ejercicio?"),
    ("de", "Wie viele Kalorien hat ein Apfel?"),
    ("de", "Was sind gute Ubungen fur den Rucken?"),
    ("de", "Wie oft sollte ich in der Woche trainieren?"),
    ("de", "Welche Lebensmittel helfen beim Abnehmen?"),
    ("ar", "\u0645\u0627 \u0647\u064a \u0623\u0641\u0636\u0644 \u062a\u0645\u0627\u0631\u064a\u0646 \u0644\u0641\u0642\u062f\u0627\u0646 \u0627\u0644\u0648\u0632\u0646\u061f"),
    ("ar", "\u0643\u0645 \u0639\u062f\u062f \u0627\u0644\u0633\u0639\u0631\u0627\u062a \u0641\u064a \u0648\u062c\u0628\u0629 \u0625\u0641\u0637\u0627\u0631 \u0635\u062d\u064a\u0629\u061f"),
    ("ar", "\u0645\u0627 \u0647\u064a \u0627\u0644\u0623\u0637\u0639\u0645\u0629 \u0627\u0644\u063a\u0646\u064a\u0629 \u0628\u0627\u0644\u0628\u0631\u0648\u062a\u064a\u0646\u061f"),
    ("ar", "\u0643\u064a\u0641 \u0623\u062d\u0633\u0646 \u0644\u064a\u0627\u0642\u062a\u064a \u0627\u0644\u0628\u062f\u0646\u064a\u0629 \u0641\u064a \u0627\u0644\u0645\u0646\u0632\u0644\u061f"),
]

def rate(original, translated):
    if not translated or translated == original:
        return "Poor"
    ratio = len(translated) / max(len(original), 1)
    if 0.4 < ratio < 3.0:
        return "Good"
    return "Moderate"

rows = []
for lang_code, input_text in test_cases:
    start = time.time()
    translated, _ = service.translate_to_english(input_text, source_lang=lang_code)
    duration = round(time.time() - start, 2)
    accuracy = rate(input_text, translated)
    rows.append((lang_names[lang_code], lang_code, input_text, translated, accuracy, duration))

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Figure 12 - Translation Quality Table</title>
<style>
  body { font-family: 'Segoe UI', sans-serif; background: #f5f5f5; padding: 40px; }
  h2 { color: #1a1a2e; margin-bottom: 4px; }
  p { color: #555; font-size: 13px; margin-bottom: 20px; }
  table { border-collapse: collapse; width: 100%; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  th { background: #1a1a2e; color: white; padding: 12px 16px; text-align: left; font-size: 13px; }
  td { padding: 11px 16px; font-size: 13px; border-bottom: 1px solid #eee; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #f0f4ff; }
  .lang-header td { background: #e8eaf6; font-weight: bold; font-size: 13px; color: #3949ab; }
  .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }
  .Good { background: #e8f5e9; color: #2e7d32; }
  .Moderate { background: #fff3e0; color: #e65100; }
  .Poor { background: #fce4ec; color: #c62828; }
  .time { color: #999; font-size: 11px; }
</style>
</head>
<body>
<h2>Figure 12: Translation Quality Comparison Table</h2>
<p>Argos Translate tested across French, Spanish, German, and Arabic using exercise and lifestyle queries.</p>
<table>
  <thead>
    <tr>
      <th>Language</th>
      <th>Sample Input</th>
      <th>Translated Output (English)</th>
      <th>Accuracy Rating</th>
      <th>Response Time</th>
    </tr>
  </thead>
  <tbody>
"""

current_lang = ""
for lang_name, lang_code, original, translated, accuracy, duration in rows:
    if lang_name != current_lang:
        current_lang = lang_name
        html += f'<tr class="lang-header"><td colspan="5">{lang_name}</td></tr>\n'
    dir_attr = 'rtl' if lang_code == 'ar' else 'ltr'
    html += f"""<tr>
      <td>{lang_name}</td>
      <td dir="{dir_attr}">{original}</td>
      <td>{translated}</td>
      <td><span class="badge {accuracy}">{accuracy}</span></td>
      <td class="time">{duration}s</td>
    </tr>\n"""

html += """  </tbody>
</table>
</body>
</html>"""

with open("figure12_translation_table.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Done. Open figure12_translation_table.html in your browser and take a screenshot.")
