import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class TicketService:
    def __init__(self):
        # Configurações fixas conforme solicitado
        self.smtp_server = "smtp.office365.com"
        self.smtp_port = 587
        self.smtp_user = "servicedti@cimentoitambe.com.br"
        self.smtp_password = "Itambe@!@#$%"
        self.from_address = "servicedti@cimentoitambe.com.br"
        self.to_address = "helpdesk@cimentoitambe.com.br"

    def send_email_ticket(self, comentario, categoria, status, usuario, atendente) -> bool:
        """Envia o chamado formatado para o HelpDesk."""
        cc_address = f"{usuario}@cimentoitambe.com.br"
        subject = f"Categoria: {categoria}"
        
        body = f"""
        E-mail gerado automaticamente pelo Service DTI.

        Solicito a abertura do chamado com as seguintes informações:

        Categoria: {categoria}
        Status: {status}
        Atendente: {atendente}
        Comentários: {comentario}

        Usuário: {usuario}
        """

        msg = MIMEMultipart()
        msg['From'] = self.from_address
        msg['To'] = self.to_address
        msg['Cc'] = cc_address
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                # Envia para o To e para o Cc
                server.sendmail(self.from_address, [self.to_address, cc_address], msg.as_string())
            return True
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
            return False