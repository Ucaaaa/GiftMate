import argparse
from pathlib import Path
from chatbot import ChatbotEngine, load_themes

parser = argparse.ArgumentParser(description="GiftMate chatbot di terminal")
parser.add_argument("--debug", action="store_true", help="Tampilkan kandidat intent")
args = parser.parse_args()
theme = load_themes(Path(__file__).parent / "themes")["giftmate"]
bot = ChatbotEngine(theme)
print(f"{theme['bot_name']}: {theme['greeting']}\n")
while True:
    message = input("Kamu: ").strip()
    if message.lower() in {"keluar", "exit", "quit"}:
        print("GiftMate: Sampai jumpa!")
        break
    result = bot.reply(message)
    print(f"GiftMate: {result['reply']}")
    print(f"[intent: {result['intent'] or 'tidak dikenali'} | skor: {result['score']:.2f}]")
    if args.debug:
        for candidate in bot.explain(message):
            print(f"  - {candidate['intent']}: {candidate['score']:.2f} | {candidate['pattern']}")
    print()
