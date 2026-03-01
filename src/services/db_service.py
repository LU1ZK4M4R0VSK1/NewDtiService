import sqlite3
import os
from ..utils.constants import AppConfig

class DatabaseService:
    def __init__(self):
        # Garante que a pasta data existe ao lado do executável
        data_dir = os.path.join(AppConfig.BASE_DIR, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, AppConfig.DB_NAME)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabela Scripts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                path TEXT NOT NULL,
                description TEXT,
                windows_only BOOLEAN DEFAULT 0
            )
        """)
        
        # Tabela Logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_id INTEGER,
                status TEXT,
                output TEXT,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (script_id) REFERENCES scripts(id)
            )
        """)
        conn.commit()
        conn.close()

    def execute_query(self, query, params=()):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor