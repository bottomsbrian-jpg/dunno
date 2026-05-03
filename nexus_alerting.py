import logging
log = logging.getLogger("nexus.alerting")

def send_alert(message: str, level: str = "INFO"):
    if level == "WARNING":
        log.warning("[ALERT] %s", message)
    elif level == "ERROR":
        log.error("[ALERT] %s", message)
    else:
        log.info("[ALERT] %s", message)
