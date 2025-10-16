import os, smtplib, ssl
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_TLS  = os.getenv("SMTP_TLS", "true").lower() == "true"
SMTP_SSLF = os.getenv("SMTP_SSL", "false").lower() == "true"  # novo: suporta SSL (porta 465)
FROM_NAME = os.getenv("SMTP_FROM_NAME", "Casa do Cigano")
FROM_MAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER or "no-reply@example.com")

def send_email(to_email: str, subject: str, text: str, html: str | None = None) -> bool:
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and to_email):
        return False  # SMTP não configurado
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{FROM_MAIL}>"
    msg["To"] = to_email
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")

    try:
        # Se SMTP_SSL=true OU porta 465, usar SSL direto
        if SMTP_SSLF or SMTP_PORT == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                if SMTP_TLS:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
        return True
    except Exception as e:
        print("EMAIL ERROR:", e)
        return False
