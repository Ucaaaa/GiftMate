from pathlib import Path
from app import create_app

ROOT = Path(__file__).resolve().parents[1]

def make_client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db"),
                      "THEMES_DIR": str(ROOT / "themes"), "SECRET_KEY": "test-secret"})
    return app.test_client()

def test_home_page(tmp_path):
    response = make_client(tmp_path).get("/")
    assert response.status_code == 200
    assert b"GiftMate" in response.data

def test_chat_page(tmp_path):
    response = make_client(tmp_path).get("/chat/giftmate")
    assert response.status_code == 200

def test_unknown_theme_404(tmp_path):
    assert make_client(tmp_path).get("/chat/tidak-ada").status_code == 404

def test_api_chat_success(tmp_path):
    response = make_client(tmp_path).post("/api/chat", json={"theme":"giftmate","message":"halo"})
    assert response.status_code == 200
    assert response.json["intent"] == "salam"

def test_api_chat_empty_message(tmp_path):
    response = make_client(tmp_path).post("/api/chat", json={"theme":"giftmate","message":" "})
    assert response.status_code == 400

def test_api_chat_invalid_theme(tmp_path):
    response = make_client(tmp_path).post("/api/chat", json={"theme":"x","message":"halo"})
    assert response.status_code == 400

def test_history_persists_in_session(tmp_path):
    client = make_client(tmp_path)
    client.post("/api/chat", json={"theme":"giftmate","message":"halo"})
    response = client.get("/api/history/giftmate")
    assert response.status_code == 200
    assert len(response.json) == 2

def test_clear_history(tmp_path):
    client = make_client(tmp_path)
    client.post("/api/chat", json={"theme":"giftmate","message":"halo"})
    client.delete("/api/history/giftmate")
    assert client.get("/api/history/giftmate").json == []

def test_explain_endpoint(tmp_path):
    response = make_client(tmp_path).post("/api/explain", json={"theme":"giftmate","message":"halo"})
    assert response.status_code == 200
    assert "candidates" in response.json

def test_stats_endpoint(tmp_path):
    client = make_client(tmp_path)
    client.post("/api/chat", json={"theme":"giftmate","message":"halo"})
    assert client.get("/api/stats/giftmate").status_code == 200
