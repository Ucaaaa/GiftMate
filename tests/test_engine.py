from pathlib import Path
from chatbot import ChatbotEngine, load_themes
from chatbot.engine import preprocess, similarity, validate_theme

ROOT = Path(__file__).resolve().parents[1]
THEME = load_themes(ROOT / "themes")["giftmate"]

def test_theme_loads():
    assert THEME["id"] == "giftmate"
    assert len(THEME["intents"]) >= 8

def test_theme_valid():
    assert validate_theme(THEME) == []

def test_preprocess_lowercase_and_punctuation():
    assert preprocess("Halo, GiftMate!") == ["halo", "giftmate"]

def test_preprocess_normalization():
    assert "bagaimana" in preprocess("gmn cara pilih hadiah")

def test_similarity_exact():
    assert similarity(["hadiah", "ulang", "tahun"], ["hadiah", "ulang", "tahun"]) == 1.0

def test_greeting_classified():
    assert ChatbotEngine(THEME).classify("halo")[0] == "salam"

def test_budget_classified():
    assert ChatbotEngine(THEME).classify("budget hadiah 100 ribu")[0] == "input_budget"

def test_recommendation_classified():
    assert ChatbotEngine(THEME).classify("rekomendasi hadiah")[0] == "rekomendasi_hadiah"

def test_fallback_for_unrelated_question():
    tag, _ = ChatbotEngine(THEME).classify("berapa harga bensin hari ini")
    assert tag is None

def test_reply_has_required_fields():
    result = ChatbotEngine(THEME).reply("halo")
    assert {"reply", "intent", "score"} <= result.keys()

def test_explain_returns_candidates():
    candidates = ChatbotEngine(THEME).explain("rekomendasi hadiah")
    assert len(candidates) == 3
    assert candidates[0]["intent"] == "rekomendasi_hadiah"
