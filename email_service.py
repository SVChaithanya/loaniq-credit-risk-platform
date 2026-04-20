import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GMAIL = os.getenv("GMAIL_ADDRESS")
PASS = os.getenv("GMAIL_APP_PASSWORD")


def _send(to_email, subject, html):
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL, PASS)
            smtp.sendmail(GMAIL, to_email, msg.as_string())

        return True
    except Exception as e:
        logger.error(e)
        print("EMAIL ERROR:", e)   # add this temporarily
        return False


def send_verification_email(email, name, otp):
    html = f"<h3>Hi {name}</h3><h1>{otp}</h1><p>Valid 10 mins</p>"
    return _send(email, "OTP Verification", html)