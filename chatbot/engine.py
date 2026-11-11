"""Mesin chatbot rule-based GiftMate sesuai pendekatan modul praktikum."""
import json
import random
import re
from difflib import SequenceMatcher
from pathlib import Path

NORMALISASI = {
    "gak": "tidak", "ga": "tidak", "nggak": "tidak", "enggak": "tidak",
    "gimana": "bagaimana", "gmn": "bagaimana", "bgmn": "bagaimana",
    "brp": "berapa", "yg": "yang", "dgn": "dengan", "utk": "untuk",
    "sy": "saya", "aku": "saya", "gue": "saya", "gw": "saya",
    "kak": "", "min": "", "dong": "", "sih": "", "nih": "", "ya": "",
    "makasih": "terima kasih", "thanks": "terima kasih", "thx": "terima kasih",
    "hai": "halo", "hi": "halo", "hello": "halo", "hallo": "halo",
}
STOPWORDS = {
    "yang", "di", "ke", "dari", "dan", "atau", "itu", "ini", "untuk", "dengan",
    "adalah", "apa", "saya", "mau", "ingin", "tolong", "bisa", "boleh", "kah",
    "pada", "akan", "juga", "ada", "tentang", "mohon", "info", "informasi",
}
BOBOT_JACCARD, BOBOT_FUZZY, BOBOT_CAKUPAN = 0.4, 0.3, 0.3
KUNCI_WAJIB_TEMA = ["id", "name", "bot_name", "avatar", "color", "description", "greeting", "suggestions", "fallback", "intents"]

def preprocess(teks):
    teks = re.sub(r"[^a-z0-9\s]", " ", str(teks).lower())
    tokens = []
    for kata in teks.split():
        for k in NORMALISASI.get(kata, kata).split():
            if k and k not in STOPWORDS:
                tokens.append(k)
    return tokens

def similarity(tokens_a, tokens_b):
    if not tokens_a or not tokens_b:
        return 0.0
    a, b = set(tokens_a), set(tokens_b)
    jaccard = len(a & b) / len(a | b)
    fuzzy = SequenceMatcher(None, " ".join(tokens_a), " ".join(tokens_b)).ratio()
    cakupan = len(a & b) / len(b)
    return round(BOBOT_JACCARD*jaccard + BOBOT_FUZZY*fuzzy + BOBOT_CAKUPAN*cakupan, 4)

def validate_theme(theme):
    masalah = [f"kunci '{k}' tidak ada" for k in KUNCI_WAJIB_TEMA if k not in theme]
    if masalah:
        return masalah
    if not theme["fallback"]:
        masalah.append("daftar 'fallback' kosong")
    tags, pola_milik = set(), {}
    for n, intent in enumerate(theme["intents"]):
        for k in ("tag", "patterns", "responses"):
            if k not in intent:
                masalah.append(f"intent ke-{n+1}: kunci '{k}' tidak ada")
        tag = intent.get("tag", f"#{n+1}")
        if tag in tags:
            masalah.append(f"tag '{tag}' dipakai lebih dari sekali")
        tags.add(tag)
        if not intent.get("patterns"):
            masalah.append(f"intent '{tag}': patterns kosong")
        if not intent.get("responses"):
            masalah.append(f"intent '{tag}': responses kosong")
        for pola in intent.get("patterns", []):
            key = " ".join(preprocess(pola))
            if not key:
                masalah.append(f"intent '{tag}': pola kosong setelah praproses")
            elif key in pola_milik and pola_milik[key] != tag:
                masalah.append(f"pola '{pola}' ada di intent '{pola_milik[key]}' dan '{tag}'")
            pola_milik.setdefault(key, tag)
    return masalah

def load_themes(folder):
    themes = {}
    for path in sorted(Path(folder).glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        errors = validate_theme(data)
        if errors:
            raise ValueError(f"File tema {path.name} tidak valid: " + "; ".join(errors))
        themes[data["id"]] = data
    if not themes:
        raise ValueError(f"Tidak ada file tema JSON di {folder}")
    return themes

class ChatbotEngine:
    def __init__(self, theme, threshold=0.45):
        self.theme = theme
        self.threshold = threshold
        self.patterns = [(i["tag"], p, preprocess(p)) for i in theme["intents"] for p in i["patterns"]]

    def explain(self, message, top=3):
        tokens = preprocess(message)
        best = {}
        for tag, pattern, ptokens in self.patterns:
            score = similarity(tokens, ptokens)
            if tag not in best or score > best[tag][1]:
                best[tag] = (pattern, score)
        return [{"intent": tag, "pattern": p, "score": score}
                for tag, (p, score) in sorted(best.items(), key=lambda x: -x[1][1])[:top]]

    def classify(self, message):
        candidates = self.explain(message, 1)
        if not candidates or candidates[0]["score"] < self.threshold:
            return None, candidates[0]["score"] if candidates else 0.0
        return candidates[0]["intent"], candidates[0]["score"]

    def reply(self, message):
        tag, score = self.classify(message)
        if tag is None:
            return {"reply": random.choice(self.theme["fallback"]), "intent": None, "score": score}
        intent = next(i for i in self.theme["intents"] if i["tag"] == tag)
        return {"reply": random.choice(intent["responses"]), "intent": tag, "score": score}
