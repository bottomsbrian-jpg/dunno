"""
nexus_alerting.py — Email + webhook alerting for NEXUS.
Usage: from nexus_alerting import alert; alert("msg", level="ERROR", exc=e)
"""
import logging, smtplib, socket, textwrap, traceback
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import requests
import nexus_config as cfg

log = logging.getLogger("nexus.alerting")
HOSTNAME = socket.gethostname()
_LEVEL_COLORS = {"INFO": 3066993, "WARNING": 16776960, "ERROR": 15158332, "CRITICAL": 10038562}

def alert(message: str, level: str = "ERROR", exc: Optional[BaseException] = None, bot_name: Optional[str] = None) -> None:
    tb_text   = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)) if exc else ""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    mode_tag  = "LIVE" if cfg.IS_LIVE else "PAPER"
    bot_tag   = f"[{bot_name}]" if bot_name else "[NEXUS]"
    subject   = f"[NEXUS {level}] {message[:80]}"
    body = textwrap.dedent(f"""
        {mode_tag} {bot_tag} — {level}
        Host : {HOSTNAME}  |  Time : {timestamp}  |  Mode : {cfg.TRADING_MODE.upper()}
        Bot  : {bot_name or 'N/A'}

        {message}
    """).strip()
    if tb_text:
        body += f"\n\nTraceback:\n{tb_text}"
    if cfg.ALERT_EMAIL_ENABLED:
        _send_email(subject, body)
    if cfg.ALERT_WEBHOOK_ENABLED:
        _send_webhook(f"{mode_tag} {bot_tag}", level, message, tb_text, timestamp)

def _send_email(subject, body):
    if not (cfg.SMTP_USER and cfg.SMTP_PASSWORD and cfg.ALERT_EMAIL_TO):
        log.warning("Email alerting enabled but credentials incomplete."); return
    recipients = [r.strip() for r in cfg.ALERT_EMAIL_TO.split(",") if r.strip()]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject; msg["From"] = cfg.ALERT_EMAIL_FROM or cfg.SMTP_USER; msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(cfg.SMTP_HOST, cfg.SMTP_PORT, timeout=15) as s:
            s.ehlo(); s.starttls(); s.login(cfg.SMTP_USER, cfg.SMTP_PASSWORD)
            s.sendmail(msg["From"], recipients, msg.as_string())
        log.info("Alert email sent to %s", recipients)
    except Exception as e:
        log.error("Failed to send alert email: %s", e)

def _send_webhook(prefix, level, message, tb_text, timestamp):
    if not cfg.ALERT_WEBHOOK_URL:
        log.warning("Webhook enabled but URL is empty."); return
    url = cfg.ALERT_WEBHOOK_URL
    if "hooks.slack.com" in url:
        text = f"*{prefix} — {level}*\n>{message}"
        if tb_text: text += f"\n\`\`\`{tb_text[-600:]}\`\`\`"
        payload = {"text": text + f"\n_{timestamp} | {HOSTNAME}_"}
    else:
        desc = message + (f"\n\`\`\`\n{tb_text[-900:]}\n\`\`\`" if tb_text else "")
        payload = {"embeds": [{"title": f"{prefix} — {level}", "description": desc[:2048],
                               "color": _LEVEL_COLORS.get(level, 15158332),
                               "footer": {"text": f"Host: {HOSTNAME} | {timestamp}"}}]}
    try:
        resp = requests.post(url, json=payload, timeout=10); resp.raise_for_status()
        log.info("Webhook alert sent (%s)", resp.status_code)
    except Exception as e:
        log.error("Failed to send webhook alert: %s", e)