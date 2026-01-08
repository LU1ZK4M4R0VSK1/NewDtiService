from ..models.script_model import Script
from ..services.db_service import DatabaseService
from ..services.runner_service import ScriptRunnerService

class ScriptsViewModel:
    def __init__(self):
        self.db = DatabaseService()
        self.runner = ScriptRunnerService()
        self.scripts = []

    def load_scripts(self):
        cursor = self.db.execute_query("SELECT id, name, category, path, description, windows_only FROM scripts")
        rows = cursor.fetchall()
        self.scripts = [Script.from_tuple(row) for row in rows]
        return self.scripts

    def add_script(self, name, category, path, desc):
        self.db.execute_query(
            "INSERT INTO scripts (name, category, path, description) VALUES (?, ?, ?, ?)",
            (name, category, path, desc)
        )
        self.load_scripts()

    def run_script(self, script: Script):
        success, output = self.runner.run_script(script.path)
        
        # Logar execução
        status = "SUCCESS" if success else "ERROR"
        self.db.execute_query(
            "INSERT INTO execution_logs (script_id, status, output) VALUES (?, ?, ?)",
            (script.id, status, output)
        )
        return success, output