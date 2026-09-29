import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config


def send_otp_email(to_email: str, otp_code: str, user_name: str = "User") -> bool:
    """
    Send OTP verification email via SMTP.
    Returns True if sent successfully, False otherwise.
    """
    server_host = Config.MAIL_SERVER
    server_port = Config.MAIL_PORT
    username = Config.MAIL_USERNAME
    password = (Config.MAIL_PASSWORD or "").replace(" ", "").strip()
    sender_email = Config.MAIL_DEFAULT_SENDER

    if not username or not password:
        print("[EMAIL WARNING] Mail username or password not configured in .env.")
        return False

    subject = "AI-NewsGen Copilot - Verify Your Email OTP"

    # Plain text version
    text_content = f"""Hello {user_name},

Thank you for registering on AI-NewsGen Copilot.

Your One-Time Password (OTP) for email verification is:
{otp_code}

This OTP is valid for 10 minutes. Please do not share this code with anyone.

If you did not request this code, please ignore this email.

Best regards,
The AI-NewsGen Copilot Team
"""

    # HTML version with modern styling
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #0b132b;
            color: #e2e8f0;
            margin: 0;
            padding: 20px;
        }}
        .email-container {{
            max-width: 540px;
            margin: 0 auto;
            background-color: #1c2541;
            border-radius: 12px;
            padding: 32px;
            border: 1px solid #3a506b;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        }}
        .brand {{
            font-size: 22px;
            font-weight: 700;
            color: #6366f1;
            margin-bottom: 20px;
            text-align: center;
        }}
        .greeting {{
            font-size: 16px;
            margin-bottom: 12px;
            color: #f8fafc;
        }}
        .otp-box {{
            background: #0f172a;
            border: 2px dashed #6366f1;
            border-radius: 8px;
            padding: 18px;
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            letter-spacing: 8px;
            color: #38bdf8;
            margin: 24px 0;
        }}
        .notice {{
            font-size: 14px;
            color: #94a3b8;
            line-height: 1.6;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #334155;
            font-size: 12px;
            color: #64748b;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="brand">📰 AI-NewsGen Copilot</div>
        <p class="greeting">Hello <strong>{user_name}</strong>,</p>
        <p class="notice">Thank you for registering. Use the One-Time Password (OTP) below to verify your email address:</p>
        
        <div class="otp-box">{otp_code}</div>
        
        <p class="notice">
            ⏰ This code will expire in <strong>10 minutes</strong>.<br>
            🔒 For security reasons, please do not share this code with anyone.
        </p>
        <p class="notice">If you did not request this verification, please safely ignore this email.</p>
        
        <div class="footer">
            © 2026 AI-NewsGen Copilot • Automated Email Notification
        </div>
    </div>
</body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"AI-NewsGen Copilot <{sender_email}>"
    msg["To"] = to_email

    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        if Config.MAIL_USE_TLS:
            server = smtplib.SMTP(server_host, server_port, timeout=12)
            server.starttls()
        else:
            server = smtplib.SMTP(server_host, server_port, timeout=12)

        server.login(username, password)
        server.sendmail(sender_email, [to_email], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send OTP email: {type(e).__name__}: {e}")
        return False
