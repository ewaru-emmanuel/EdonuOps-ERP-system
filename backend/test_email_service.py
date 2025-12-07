import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

smtp_user = os.getenv("SES_SMTP_USER")
smtp_pass = os.getenv("SES_SMTP_PASS")
from_email = os.getenv("SES_FROM_EMAIL")
to_email = "apolloemmanuel01@gmail.com"  # test recipient

msg = MIMEText("This is a test email from EdonuOps ERP.")
msg["Subject"] = "SES SMTP Test"
msg["From"] = from_email
msg["To"] = to_email

with smtplib.SMTP("email-smtp.eu-north-1.amazonaws.com", 587) as server:
    server.starttls()
    server.login(smtp_user, smtp_pass)
    server.send_message(msg)
    print("✅ Test email sent successfully!")
