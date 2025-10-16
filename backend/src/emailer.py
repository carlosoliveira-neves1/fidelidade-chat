import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

"""
send_email(to_email, subject, text, html=None, from_email=None)

- Se variáveis SMTP estiverem configuradas, envia de verdade.
- Caso contrário, faz fallback para log/print (não quebra a API em dev).
- Aceita corpo HTML opcional (4º argumento).
"""

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
DEFAULT_FROM = os.getenv("SMTP_FROM", "no-reply@localhost")

def _has_smtp():
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASS)

def send_email(to_email: str, subject: str, text: str, html: str | None = None, from_email: str | None = None) -> bool:
    from_addr = from_email or DEFAULT_FROM
    to_addr = (to_email or "").strip()
    if not to_addr:
        # sem destinatário — nada a fazer
        print("[emailer] destinatário vazio; ignorando envio")
        return False

    # Monta mensagem (texto + html opcional)
    if html:
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(text or "", "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
    else:
        msg = MIMEText(text or "", "plain", "utf-8")
    msg["Subject"] = subject or ""
    msg["From"] = from_addr
    msg["To"] = to_addr

    if _has_smtp():
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls(context=context)
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(from_addr, [to_addr], msg.as_string())
            print(f"[emailer] enviado para {to_addr}")
            return True
        except Exception as e:
            print(f"[emailer] falha no SMTP: {e}")
            return False

    # Fallback: apenas loga (útil em dev/Render sem SMTP)
    print("==== EMAIL (FAKE) ====")
    print(f"From: {from_addr}")
    print(f"To:   {to_addr}")
    print(f"Subj: {subject}")
    print("-- TEXT --")
    print(text or "")
    if html:
        print("-- HTML --")
        print(html)
    print("======================")
    return True
