import sqlite3
import os
import shutil
from datetime import datetime
from ..utils.constants import AppConfig
from typing import Tuple, Any

# Log para diagnóstico de sincronização
temp_dir = os.environ.get("TEMP", os.environ.get("TMP", "C:\\Temp"))
DB_LOG_PATH = os.path.join(temp_dir, "dti_db_debug.log")

def _log(msg: str):
    try:
        with open(DB_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - {msg}\n")
    except:
        pass

class DatabaseService:
    def __init__(self):
        # Pasta local (ProgramData) para máxima performance e escrita garantida
        prog_data = os.environ.get("PROGRAMDATA", "C:\\ProgramData")
        self.local_data_dir = os.path.join(prog_data, "DTIService", "data")
        os.makedirs(self.local_data_dir, exist_ok=True)
        self.db_path = os.path.join(self.local_data_dir, AppConfig.DB_NAME)

        # Pasta mestre (Rede) para compartilhamento de scripts
        self.master_data_dir = os.path.join(AppConfig.BASE_DIR, "data")
        self.master_db_path = os.path.join(self.master_data_dir, AppConfig.DB_NAME)

        _log(f"--- INICIALIZANDO APP v12 ---")
        
        # 1. Puxa do mestre ao iniciar (Sincronização de Entrada)
        self._pull_from_master()
        
        # 2. Inicializa o banco (cria tabelas e ativa WAL)
        self._init_db()

    def _pull_from_master(self):
        """Copia o banco do servidor para o local se o Mestre for estritamente mais novo."""
        if not os.path.exists(self.master_db_path):
            _log(f"PULL: Master não encontrado em {self.master_db_path}")
            return

        try:
            mtime_master = os.path.getmtime(self.master_db_path)
            size_master = os.path.getsize(self.master_db_path)
            
            mtime_local = os.path.getmtime(self.db_path) if os.path.exists(self.db_path) else 0
            size_local = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            _log(f"PULL Check: Master(sz={size_master}, mt={mtime_master}) | Local(sz={size_local}, mt={mtime_local})")

            # Proteção: Só faz o Pull se o Master for realmente mais novo ou o local não existir
            if not os.path.exists(self.db_path) or mtime_master > (mtime_local + 1):
                _log("Diferença detectada. Puxando Master -> Local...")
                shutil.copy2(self.master_db_path, self.db_path)
                _log("PULL realizado com sucesso.")
            else:
                _log("PULL pulado: Local já atualizado.")
        except Exception as e:
            _log(f"ERRO no PULL: {e}")

    def sync_to_master(self) -> Tuple[bool, str]:
        """Envia o banco local para o servidor. Retorna (sucesso, mensagem_erro)."""
        _log("Iniciando PUSH Local -> Rede...")
        try:
            if not os.path.exists(self.master_data_dir):
                _log(f"Criando diretório master: {self.master_data_dir}")
                os.makedirs(self.master_data_dir, exist_ok=True)
            
            # Tenta copy2 (preserva metadados)
            try:
                shutil.copy2(self.db_path, self.master_db_path)
                _log("PUSH (copy2) realizado com sucesso.")
                return True, ""
            except Exception as e1:
                _log(f"PUSH (copy2) falhou: {e1}. Tentando copy simples...")
                try:
                    shutil.copy(self.db_path, self.master_db_path)
                    _log("PUSH (copy simples) realizado com sucesso.")
                    return True, ""
                except Exception as e2:
                    error_msg = str(e2)
                    _log(f"ERRO CRÍTICO no PUSH: {error_msg}")
                    return False, error_msg
        except Exception as e:
            error_msg = str(e)
            _log(f"ERRO de diretório no PUSH: {error_msg}")
            return False, error_msg

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
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
        finally:
            conn.close()

    def execute_query(self, query, params=(), is_select=False) -> Any:
        """Executa query. Para escrita em scripts, retorna (success, error_msg)."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if is_select:
                result = cursor.fetchall()
                return result
            
            conn.commit()
            
            # Se for alteração nos scripts, sincroniza
            upper_q = query.strip().upper()
            if any(x in upper_q for x in ["INSERT", "UPDATE", "DELETE"]) and "SCRIPTS" in upper_q:
                conn.close()
                conn = None
                success, error_msg = self.sync_to_master()
                return success, error_msg
            
            return True, ""
        except Exception as e:
            _log(f"ERRO SQL ({query}): {e}")
            if conn:
                conn.close()
            # Retorna erro para o chamador
            return False, str(e)
        finally:
            if conn:
                conn.close()