"""Penyimpanan riwayat percakapan menggunakan SQLite."""
import sqlite3
from pathlib import Path

class ChatHistory:
    def __init__(self, db_path):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL, theme TEXT NOT NULL,
                sender TEXT NOT NULL CHECK(sender IN ('user','bot')),
                text TEXT NOT NULL, intent TEXT, score REAL,
                created_at TIMESTAMP DEFAULT (datetime('now','localtime'))
            );
            CREATE INDEX IF NOT EXISTS idx_session_theme ON messages(session_id, theme);
            """)

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def add(self, session_id, theme, sender, text, intent=None, score=None):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO messages(session_id,theme,sender,text,intent,score) VALUES(?,?,?,?,?,?)",
                (session_id, theme, sender, text, intent, score)
            )

    def get(self, session_id, theme, limit=100):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT sender,text,intent,score,created_at FROM messages WHERE session_id=? AND theme=? ORDER BY id DESC LIMIT ?",
                (session_id, theme, limit)
            ).fetchall()
        return [dict(r) for r in reversed(rows)]

    def clear(self, session_id, theme):
        with self._connect() as conn:
            conn.execute("DELETE FROM messages WHERE session_id=? AND theme=?", (session_id, theme))

    def stats(self, theme):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT COALESCE(intent,'(tidak dikenali)') AS intent, COUNT(*) AS jumlah FROM messages WHERE theme=? AND sender='user' GROUP BY intent ORDER BY jumlah DESC",
                (theme,)
            ).fetchall()
        return [dict(r) for r in rows]

    def unknown_questions(self, theme, limit=20):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT text,score,created_at FROM messages WHERE theme=? AND sender='user' AND intent IS NULL ORDER BY id DESC LIMIT ?",
                (theme, limit)
            ).fetchall()
        return [dict(r) for r in rows]

    def summary(self, theme):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) total, SUM(CASE WHEN intent IS NULL THEN 1 ELSE 0 END) gagal, COUNT(DISTINCT session_id) sesi FROM messages WHERE theme=? AND sender='user'",
                (theme,)
            ).fetchone()
        total, failed = row["total"] or 0, row["gagal"] or 0
        return {"total": total, "tidak_dikenali": failed, "sesi": row["sesi"] or 0,
                "persen_dikenali": round(100*(total-failed)/total, 1) if total else 0.0}
