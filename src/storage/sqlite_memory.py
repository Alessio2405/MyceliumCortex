import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import aiosqlite
    _HAS_AIOSQLITE = True
except Exception:
    aiosqlite = None
    _HAS_AIOSQLITE = False
    import sqlite3

class PersistentMemory:
    """Simple async SQLite-backed conversation memory.

    Tables:
      - conversations(id TEXT PRIMARY KEY, meta JSON)
      - messages(id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id TEXT, role TEXT, content TEXT, timestamp TEXT)

    Usage:
      mem = PersistentMemory("./data/miniclaw.db")
      await mem.init_db()
      await mem.store_message("conv1", "user", "hello")
      msgs = await mem.get_messages("conv1")
    """

    def __init__(self, db_path: str = "./data/myceliumcortex.db"):
        self.db_path = db_path
        self._init_lock = asyncio.Lock()
        self._initialized = False

    async def init_db(self):
        if self._initialized:
            return
        async with self._init_lock:
            if self._initialized:
                return
            if _HAS_AIOSQLITE:
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute("PRAGMA journal_mode=WAL;")
                    await db.execute(
                        """
                        CREATE TABLE IF NOT EXISTS conversations (
                            id TEXT PRIMARY KEY,
                            meta TEXT
                        )
                        """
                    )
                    await db.execute(
                        """
                        CREATE TABLE IF NOT EXISTS messages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            conversation_id TEXT,
                            role TEXT,
                            content TEXT,
                            timestamp TEXT
                        )
                        """
                    )
                    await db.commit()
            else:
                # Fallback to synchronous sqlite3 in a thread
                def _init_sync(path: str):
                    import os
                    dirp = os.path.dirname(path) or '.'
                    os.makedirs(dirp, exist_ok=True)
                    conn = sqlite3.connect(path)
                    cur = conn.cursor()
                    cur.execute("PRAGMA journal_mode=WAL;")
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS conversations (
                            id TEXT PRIMARY KEY,
                            meta TEXT
                        )
                        """
                    )
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS messages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            conversation_id TEXT,
                            role TEXT,
                            content TEXT,
                            timestamp TEXT
                        )
                        """
                    )
                    conn.commit()
                    conn.close()

                await asyncio.to_thread(_init_sync, self.db_path)
            self._initialized = True

    async def store_message(self, conversation_id: str, role: str, content: str, timestamp: Optional[str] = None):
        await self.init_db()
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        if _HAS_AIOSQLITE:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT OR IGNORE INTO conversations (id, meta) VALUES (?, ?)",
                    (conversation_id, "{}"),
                )
                await db.execute(
                    "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                    (conversation_id, role, content, timestamp),
                )
                await db.commit()
        else:
            def _store_sync(path: str, conv_id: str, role_v: str, content_v: str, ts: str):
                import os
                dirp = os.path.dirname(path) or '.'
                os.makedirs(dirp, exist_ok=True)
                conn = sqlite3.connect(path)
                cur = conn.cursor()
                cur.execute("INSERT OR IGNORE INTO conversations (id, meta) VALUES (?, ?)", (conv_id, "{}"))
                cur.execute(
                    "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                    (conv_id, role_v, content_v, ts),
                )
                conn.commit()
                conn.close()

            await asyncio.to_thread(_store_sync, self.db_path, conversation_id, role, content, timestamp)

    async def get_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        await self.init_db()
        query = "SELECT id, role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY id ASC"
        if limit:
            query += " LIMIT ?"
            params = (conversation_id, limit)
        else:
            params = (conversation_id,)
        if _HAS_AIOSQLITE:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                await cursor.close()
            return [
                {"id": r[0], "role": r[1], "content": r[2], "timestamp": r[3]} for r in rows
            ]
        else:
            def _get_sync(path: str, q: str, p: tuple):
                import os
                dirp = os.path.dirname(path) or '.'
                os.makedirs(dirp, exist_ok=True)
                conn = sqlite3.connect(path)
                cur = conn.cursor()
                cur.execute(q, p)
                rows = cur.fetchall()
                conn.close()
                return rows

            rows = await asyncio.to_thread(_get_sync, self.db_path, query, params)
            return [{"id": r[0], "role": r[1], "content": r[2], "timestamp": r[3]} for r in rows]

    async def clear_conversation(self, conversation_id: str):
        await self.init_db()
        if _HAS_AIOSQLITE:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
                await db.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
                await db.commit()
        else:
            def _clear_sync(path: str, conv_id: str):
                import os
                dirp = os.path.dirname(path) or '.'
                os.makedirs(dirp, exist_ok=True)
                conn = sqlite3.connect(path)
                cur = conn.cursor()
                cur.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
                cur.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
                conn.commit()
                conn.close()

            await asyncio.to_thread(_clear_sync, self.db_path, conversation_id)
