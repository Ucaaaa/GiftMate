import os
import re
import uuid
from pathlib import Path
from flask import Flask, abort, jsonify, render_template, request, session
from chatbot import ChatbotEngine, ChatHistory, load_themes

BASE_DIR = Path(__file__).resolve().parent

def parse_budget(message):
    text = message.lower().replace(".", "").replace(",", "")
    nums = [int(x) for x in re.findall(r"\d+", text)]
    if not nums:
        return None
    amount = nums[0]
    if "juta" in text:
        amount *= 1_000_000
    elif "ribu" in text or "rb" in text:
        amount *= 1_000
    elif amount < 1000:
        amount *= 1_000
    return amount

def detect_value(message, choices):
    text = message.lower()
    for choice in choices:
        if choice in text:
            return choice
    return None

def recommend_gifts(profile, catalog):
    budget = profile.get("budget")
    recipient = profile.get("recipient")
    occasion = profile.get("occasion")
    hobby = profile.get("hobby")
    ranked = []
    for item in catalog:
        if budget is not None and not (item["min_budget"] <= budget <= item["max_budget"]):
            continue
        score = 0
        if recipient and recipient in item["recipients"]:
            score += 3
        if occasion and occasion in item["occasions"]:
            score += 2
        if hobby and hobby in item["hobbies"]:
            score += 4
        if score:
            ranked.append((score, item))
    ranked.sort(key=lambda pair: (-pair[0], pair[1]["min_budget"]))
    if not ranked:
        ranked = [(0, item) for item in catalog if budget is None or item["min_budget"] <= budget <= item["max_budget"]]
    return [item for _, item in ranked[:5]]

def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "giftmate-dev-key-ganti-di-server"),
        DATABASE=os.environ.get("DATABASE", str(BASE_DIR / "chat_history.db")),
        THEMES_DIR=str(BASE_DIR / "themes"),
        THRESHOLD=float(os.environ.get("THRESHOLD", "0.45")),
        ADMIN_KEY=os.environ.get("ADMIN_KEY", ""),
        MAX_LEN=500
    )
    if config:
        app.config.update(config)
    themes = load_themes(app.config["THEMES_DIR"])
    engines = {tid: ChatbotEngine(t, app.config["THRESHOLD"]) for tid, t in themes.items()}
    history = ChatHistory(app.config["DATABASE"])

    def sid():
        if "sid" not in session:
            session["sid"] = uuid.uuid4().hex
        return session["sid"]

    def theme_or_404(theme_id):
        if theme_id not in themes:
            abort(404, description=f"Tema '{theme_id}' tidak ditemukan")
        return themes[theme_id]

    def admin_check():
        key = app.config["ADMIN_KEY"]
        if key and request.args.get("key") != key:
            abort(403, description="Kunci admin salah atau tidak ada")

    @app.get("/")
    def index():
        return render_template("index.html", themes=themes.values())

    @app.get("/chat/<theme_id>")
    def chat_page(theme_id):
        return render_template("chat.html", theme=theme_or_404(theme_id))

    @app.get("/admin/<theme_id>")
    def admin_page(theme_id):
        admin_check()
        theme = theme_or_404(theme_id)
        summary = history.summary(theme_id)
        return render_template("admin.html", theme=theme, summary=summary,
                               stats=history.stats(theme_id),
                               unknown=history.unknown_questions(theme_id),
                               threshold=app.config["THRESHOLD"])

    @app.get("/api/themes")
    def api_themes():
        return jsonify([{"id": t["id"], "name": t["name"], "description": t["description"]}
                        for t in themes.values()])

    @app.post("/api/chat")
    def api_chat():
        data = request.get_json(silent=True) or {}
        message = str(data.get("message", "")).strip()
        theme_id = data.get("theme", "")
        if theme_id not in engines:
            return jsonify({"error": "Tema tidak valid"}), 400
        if not message:
            return jsonify({"error": "Pesan tidak boleh kosong"}), 400
        if len(message) > app.config["MAX_LEN"]:
            return jsonify({"error": f"Pesan maksimal {app.config['MAX_LEN']} karakter"}), 400

        theme = themes[theme_id]
        profile = session.get(f"profile_{theme_id}", {})
        pending = session.get(f"pending_{theme_id}", "")
        tag, score = engines[theme_id].classify(message)
        reply = None
        result_intent = tag

        # Saat sesi rekomendasi aktif, jawaban singkat diarahkan ke parameter yang sedang diminta.
        if pending == "recipient":
            recipient = detect_value(message, ["sahabat", "teman", "pasangan", "ibu", "ayah", "rekan kerja", "saudara"])
            if recipient:
                profile["recipient"] = recipient
                session.pop(f"pending_{theme_id}", None)
            else:
                reply = "Aku belum menangkap penerimanya. Pilih salah satu: sahabat, teman, pasangan, ibu, ayah, saudara, atau rekan kerja."
        elif pending == "occasion":
            occasion = detect_value(message, ["ulang tahun", "wisuda", "anniversary", "pernikahan", "hari spesial"])
            if occasion:
                profile["occasion"] = occasion
                session.pop(f"pending_{theme_id}", None)
            else:
                reply = "Momen yang tersedia: ulang tahun, wisuda, anniversary, pernikahan, atau hari spesial."
        elif pending == "budget":
            amount = parse_budget(message)
            if amount and amount > 0:
                profile["budget"] = amount
                session.pop(f"pending_{theme_id}", None)
            else:
                reply = "Masukkan budget dalam angka, misalnya Rp75.000 atau 100 ribu."
        elif pending == "hobby":
            hobby = detect_value(message, ["membaca", "menulis", "olahraga", "musik", "fotografi", "tanaman", "berkebun", "skincare", "menggambar", "kopi", "kuliner", "belajar", "relaksasi", "seni"])
            if hobby:
                profile["hobby"] = hobby
                session.pop(f"pending_{theme_id}", None)
            else:
                reply = "Sebutkan hobi penerima, misalnya membaca, musik, olahraga, fotografi, tanaman, menggambar, atau kopi."
        elif tag == "rekomendasi_hadiah":
            profile = {}
            reply = "Siapa penerima hadiahnya? (sahabat, teman, pasangan, orang tua, saudara, atau rekan kerja)"
            session[f"pending_{theme_id}"] = "recipient"
        elif tag == "pilih_penerima":
            recipient = detect_value(message, ["sahabat", "teman", "pasangan", "ibu", "ayah", "rekan kerja", "saudara"])
            if recipient:
                profile["recipient"] = recipient
                reply = "Untuk momen apa hadiahnya? (ulang tahun, wisuda, anniversary, pernikahan, atau hari spesial)"
                session[f"pending_{theme_id}"] = "occasion"
            else:
                reply = "Sebutkan penerimanya, misalnya sahabat, teman, pasangan, ibu, ayah, saudara, atau rekan kerja."
        elif tag == "input_budget":
            amount = parse_budget(message)
            if amount:
                profile["budget"] = amount
                reply = "Budget dicatat. Kalau ingin rekomendasi lengkap, ketik 'rekomendasi hadiah' untuk mulai dari awal."
            else:
                reply = "Sebutkan budget dalam angka, misalnya Rp50.000 atau 100 ribu."
        elif tag == "pilih_momen":
            occasion = detect_value(message, ["ulang tahun", "wisuda", "anniversary", "pernikahan", "hari spesial"])
            reply = f"Momen {occasion} cocok dipertimbangkan." if occasion else "Momen yang bisa dipilih: ulang tahun, wisuda, anniversary, pernikahan, atau hari spesial."
        elif tag == "tanya_hobi":
            hobby = detect_value(message, ["membaca", "menulis", "olahraga", "musik", "fotografi", "tanaman", "berkebun", "skincare", "menggambar", "kopi", "kuliner", "belajar", "relaksasi", "seni"])
            reply = f"Minat {hobby} bisa menjadi petunjuk memilih hadiah yang lebih personal." if hobby else "Contoh hobi: membaca, musik, olahraga, fotografi, tanaman, menggambar, dan kopi."
        else:
            reply = engines[theme_id].reply(message)["reply"]

        # Setelah satu parameter terisi dalam alur, lanjutkan pertanyaan berikutnya.
        if reply is None:
            if "recipient" not in profile:
                reply = "Untuk siapa hadiahnya? (sahabat, teman, pasangan, ibu, ayah, saudara, atau rekan kerja)"
                session[f"pending_{theme_id}"] = "recipient"
            elif "occasion" not in profile:
                reply = "Untuk momen apa? (ulang tahun, wisuda, anniversary, pernikahan, atau hari spesial)"
                session[f"pending_{theme_id}"] = "occasion"
            elif "budget" not in profile:
                reply = "Berapa budget yang tersedia? Contoh: 50 ribu, 100 ribu, atau Rp150.000."
                session[f"pending_{theme_id}"] = "budget"
            elif "hobby" not in profile:
                reply = "Apa hobi atau minat penerima? Contoh: membaca, musik, olahraga, fotografi, tanaman, atau kopi."
                session[f"pending_{theme_id}"] = "hobby"
            else:
                items = recommend_gifts(profile, theme.get("gift_catalog", []))
                if items:
                    lines = ["Ini beberapa ide hadiah yang cocok dengan kriteriamu:"]
                    for n, item in enumerate(items, 1):
                        lines.append(f"{n}. {item['name']} (estimasi Rp{item['min_budget']:,}–Rp{item['max_budget']:,}) — {item['description']}")
                    lines.append("Harga hanya estimasi dan dapat berbeda antarpenjual. Ketik 'rekomendasi hadiah' untuk mencari opsi lain.")
                    reply = "\n".join(lines)
                else:
                    reply = "Belum ada hadiah di katalog yang sesuai dengan budget tersebut. Coba budget yang sedikit lebih fleksibel atau mulai ulang dengan 'rekomendasi hadiah'."
                session.pop(f"pending_{theme_id}", None)
                profile = {}
        session[f"profile_{theme_id}"] = profile

        if tag is None and not pending:
            result_intent = None
            score = engines[theme_id].classify(message)[1]
        history.add(sid(), theme_id, "user", message, result_intent, score)
        history.add(sid(), theme_id, "bot", reply, result_intent, score)
        return jsonify({"reply": reply, "intent": result_intent, "score": round(score, 4)})

    @app.post("/api/explain")
    def api_explain():
        data = request.get_json(silent=True) or {}
        theme_id = data.get("theme", "")
        if theme_id not in engines:
            return jsonify({"error": "Tema tidak valid"}), 400
        message = str(data.get("message", ""))[:app.config["MAX_LEN"]]
        return jsonify({"threshold": app.config["THRESHOLD"], "candidates": engines[theme_id].explain(message)})

    @app.get("/api/history/<theme_id>")
    def api_history(theme_id):
        theme_or_404(theme_id)
        return jsonify(history.get(sid(), theme_id))

    @app.delete("/api/history/<theme_id>")
    def api_clear_history(theme_id):
        theme_or_404(theme_id)
        history.clear(sid(), theme_id)
        session.pop(f"profile_{theme_id}", None)
        session.pop(f"pending_{theme_id}", None)
        return jsonify({"status": "ok"})

    @app.get("/api/stats/<theme_id>")
    def api_stats(theme_id):
        admin_check()
        theme_or_404(theme_id)
        return jsonify(history.stats(theme_id))

    @app.errorhandler(403)
    @app.errorhandler(404)
    def handle_error(err):
        if request.path.startswith("/api/"):
            return jsonify({"error": err.description}), err.code
        return render_template("404.html", message=err.description, code=err.code), err.code

    return app

app = create_app()
if __name__ == "__main__":
    app.run(debug=True)
