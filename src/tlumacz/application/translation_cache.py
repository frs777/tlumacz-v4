"""Thread-safe SQLite translation cache."""

from __future__ import annotations

import hashlib
import sqlite3
import threading
from pathlib import Path


class TranslationCache:
    """Persist translations keyed by all prompt/model inputs."""

    MAX_AGE_DAYS = 7

    def __init__(self, cache_dir: Path, *, enabled: bool = True) -> None:
        self._enabled = enabled
        self._lock = threading.Lock()
        self._conn: sqlite3.Connection | None = None
        self._hits = 0
        self._misses = 0
        if not enabled:
            return
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(
                cache_dir / "cache.db",
                check_same_thread=False,
            )
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS translations "
                "(key TEXT PRIMARY KEY, translation TEXT NOT NULL, "
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            )
            self._conn.commit()
            self._cleanup()
        except (OSError, sqlite3.Error):
            self._enabled = False
            self._conn = None

    def _cleanup(self) -> None:
        if self._conn is None:
            return
        self._conn.execute(
            f"DELETE FROM translations WHERE created_at < "
            f"datetime('now', '-{self.MAX_AGE_DAYS} days')"
        )
        self._conn.commit()

    @staticmethod
    def _key(
        chunk: str,
        system_prompt: str,
        skill_text: str,
        model: str,
        temperature: float,
        source_language: str = "",
    ) -> str:
        parts = [chunk, system_prompt, skill_text, model, repr(temperature), source_language]
        digest = hashlib.sha256()
        for part in parts:
            encoded = part.encode("utf-8")
            digest.update(len(encoded).to_bytes(8, "big"))
            digest.update(encoded)
        return digest.hexdigest()

    def get(
        self,
        chunk: str,
        system_prompt: str,
        skill_text: str,
        model: str,
        temperature: float,
        source_language: str = "",
    ) -> str | None:
        if not self._enabled or self._conn is None:
            return None
        key = self._key(chunk, system_prompt, skill_text, model, temperature, source_language)
        with self._lock:
            try:
                row = self._conn.execute(
                    "SELECT translation FROM translations WHERE key = ?",
                    (key,),
                ).fetchone()
            except sqlite3.Error:
                row = None
            if row is None:
                self._misses += 1
                return None
            self._hits += 1
            return str(row[0])

    def put(
        self,
        chunk: str,
        system_prompt: str,
        skill_text: str,
        model: str,
        temperature: float,
        translation: str,
        source_language: str = "",
    ) -> None:
        if not self._enabled or self._conn is None:
            return
        key = self._key(chunk, system_prompt, skill_text, model, temperature, source_language)
        with self._lock:
            try:
                self._conn.execute(
                    "INSERT OR REPLACE INTO translations (key, translation) "
                    "VALUES (?, ?)",
                    (key, translation),
                )
                self._conn.commit()
            except sqlite3.Error:
                return

    def clear(self) -> None:
        if self._conn is None:
            return
        with self._lock:
            try:
                self._conn.execute("DELETE FROM translations")
                self._conn.commit()
            except sqlite3.Error:
                return

    def stats(self) -> dict[str, int | bool]:
        if not self._enabled or self._conn is None:
            return {"entries": 0, "enabled": False, "hits": 0, "misses": 0}
        with self._lock:
            count = int(
                self._conn.execute("SELECT COUNT(*) FROM translations").fetchone()[0]
            )
        return {
            "entries": count,
            "enabled": True,
            "hits": self._hits,
            "misses": self._misses,
        }

    def reset_stats(self) -> None:
        with self._lock:
            self._hits = 0
            self._misses = 0

    def close(self) -> None:
        if self._conn is None:
            return
        with self._lock:
            self._conn.close()
            self._conn = None

    def __del__(self) -> None:
        """Awaryjny cleanup deskryptora SQLite poza normalnym lifecycle."""
        try:
            self.close()
        except Exception:
            # Finalizer nie może maskować błędów ani blokować zamykania procesu.
            pass


__all__ = ["TranslationCache"]
