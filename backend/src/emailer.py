# src/emailer.py
import os
import smtplib
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASS = os.getenv("SMTP_PASS", "").strip()
FROM_EMAIL = os.getenv("FROM_EMAIL", "no-reply@localhost")

def _send_raw(to: str, subject: str, body: str, subtype: str = "plain") -> bool:
    """Envio real via SMTP; se não tiver SMTP configurado, apenas loga e segue."""
    if not SMTP_HOST:
        print(f"[emailer] (mock) To: {to} | Subject: {subject}\n---{subtype}---\n{body}\n--------------")
        return True

    msg = MIMEText(body, _subtype=subtype, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as s:
        if SMTP_USER and SMTP_PASS:
            try:
                s.starttls()
            except Exception:
                # Alguns servidores já vêm em TLS/SSL
                pass
            s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(FROM_EMAIL, [to], msg.as_string())
    return True

def send_email(to: str, subject: str, text_body: str, html_body: str | None = None) -> bool:
    """
    Assinatura compatível:
      - 3 args: send_email(to, subject, text_body)
      - 4 args: send_email(to, subject, text_body, html_body)
    Se html_body vier, priorizamos HTML, senão enviamos texto puro.
    """
    try:
        if html_body and html_body.strip():
            return _send_raw(to, subject, html_body, subtype="html")
        return _send_raw(to, subject, text_body, subtype="plain")
    except Exception as e:
        # Nunca derruba o fluxo de negócio
        print(f"[emailer] erro ao enviar: {e}")
        return False
