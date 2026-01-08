import os
import json
import psutil
from typing import Tuple, List
from src.services.ticket_service import TicketService

class TicketsViewModel:
    def __init__(self):
        self.service = TicketService()

    def get_logged_in_user(self) -> str:
        """Obtém o nome do usuário logado na máquina usando psutil."""
        users = psutil.users()
        if users:
            return users[0].name
        return "usuario.desconhecido"

    def load_atendentes(self) -> List[str]:
        """Carrega a lista de atendentes do arquivo JSON."""
        try:
            # Ajuste o caminho conforme a estrutura do seu projeto
            base_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(base_dir, '..', '..', 'data', 'atendentes.json')
            
            if not os.path.exists(json_path):
                return ["Atendente não encontrado"]

            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("atendentes", [])
        except Exception as e:
            print(f"Erro ao carregar atendentes: {e}")
            return []

    def submit_ticket(self, comentario: str, categoria: str, status: str, atendente: str) -> Tuple[bool, str]:
        # Validação simples
        if not comentario or len(comentario.strip()) < 5:
            return False, "Por favor, insira um comentário válido."
        
        if "Selecione" in [categoria, status, atendente]:
            return False, "Por favor, preencha todos os campos de seleção."
        
        user = self.get_logged_in_user()
        success = self.service.send_email_ticket(comentario, categoria, status, user, atendente)
        
        if success:
            return True, "Chamado enviado com sucesso!"
        return False, "Falha no envio. Verifique a rede ou credenciais."