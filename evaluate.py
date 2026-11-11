import csv
from pathlib import Path
from chatbot import ChatbotEngine, load_themes

ROOT = Path(__file__).parent
theme = load_themes(ROOT / "themes")["giftmate"]
bot = ChatbotEngine(theme)
rows = list(csv.DictReader((ROOT / "evaluasi" / "giftmate.csv").open(encoding="utf-8")))
correct = 0
for row in rows:
    predicted, score = bot.classify(row["message"])
    expected = row["expected_intent"] or None
    ok = predicted == expected
    correct += ok
    print(f"{'BENAR' if ok else 'SALAH':5} | {row['message']:<38} | harapan={expected} prediksi={predicted} skor={score:.2f}")
print(f"\nAkurasi: {correct}/{len(rows)} = {100*correct/len(rows):.1f}%")
